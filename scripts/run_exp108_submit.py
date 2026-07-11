#!/usr/bin/env python3
"""Exp108 ICO refrigeration resource — HARDWARE SUBMIT (Whisper C4558).
Pre-reg: experiments/exp108-ico-refrigeration-preregistration.md (FROZEN pre --submit).
Exp105/106 submit discipline: calibration-gated 4-CHAIN (first 4q payload in this line),
layout chosen by free transpile-permutation scan, ONE SamplerV2 job, pre-registered
shuffle, same-skeleton sentinels START/MID/END, live 2q-class re-audit.

Usage:  --scan (FREE: chain pick + layout scan + live audit)  |  --submit (spends QPU)
        --backend ibm_marrakesh (default) --tag exp108
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from exp108_ico_refrigeration import (build_circuit, SHOTS_GAME, SHOTS_SENT,
                                      self_validate)

SHUFFLE_SEED = 4558          # pre-registered
MAX_SWITCH_2Q = 40           # frozen class bound (FakeMarrakesh preview: 21)


def pick_chain4(backend):
    """Calibration-gated best 4-qubit PATH: min sum(3 edge 2q errors) + sum(4 readouts)."""
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    edges, err = {}, {}
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        edges.setdefault(a, set()).add(b)
        edges.setdefault(b, set()).add(a)
        err[(a, b)] = err[(b, a)] = e
    ro = {}
    for q in edges:
        try:
            ro[q] = target['measure'][(q,)].error or 0.0
        except Exception:
            ro[q] = 0.0
    best, best_cost = None, 1e9
    for a in edges:
        for b in edges[a]:
            for c in edges[b] - {a}:
                for d in edges[c] - {a, b}:
                    cost = err[(a, b)] + err[(b, c)] + err[(c, d)] + \
                        sum(ro.get(q, 0.0) for q in (a, b, c, d))
                    if cost < best_cost:
                        best_cost, best = cost, (a, b, c, d)
    return best, best_cost, twoq


def scan_layout(backend, chain):
    """FREE: transpile the retention-sentinel skeleton under all 24 logical->physical
    permutations of the chain; return the layout with min routed 2q count."""
    from qiskit import transpile
    qc = build_circuit(0, 0, 0, arm="switch")   # same skeleton as payload
    best, best_n = None, 1e9
    for perm in itertools.permutations(chain):
        tqc = transpile(qc, backend, initial_layout=list(perm),
                        seed_transpiler=SHUFFLE_SEED, optimization_level=3)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        if n2 < best_n:
            best_n, best = n2, list(perm)
    return best, best_n


def build_pubs():
    labels = list(itertools.product([0, 1], repeat=3))
    ent = []
    for arm in ("switch", "null_fwd", "null_rev"):
        for lab in labels:
            ent.append((f"{arm}_{lab[0]}{lab[1]}{lab[2]}", arm, lab, SHOTS_GAME))
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffled = [ent[i] for i in rng.permutation(len(ent))]
    entries = [(name, arm, build_circuit(*lab, arm=arm), shots,
                {"label": name, "kind": arm, "prep": list(lab), "shots": shots})
               for name, arm, lab, shots in shuffled]
    sent = []
    for rep in ("start", "mid", "end"):
        sent.append((f"sent_{rep}_retention", "sentinel",
                     build_circuit(0, 0, 0, arm="switch"), SHOTS_SENT,
                     {"label": f"sent_{rep}_retention", "kind": "sentinel",
                      "replicate": rep, "shots": SHOTS_SENT}))
    deco = [("sent_mid_deconull", "sentinel", build_circuit(1, 0, 0, arm="switch"),
             SHOTS_SENT, {"label": "sent_mid_deconull", "kind": "sentinel",
                          "replicate": "mid", "shots": SHOTS_SENT})]
    mid = len(entries) // 2
    return [sent[0]] + entries[:mid] + [sent[1]] + deco + entries[mid:] + [sent[2]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp108")
    args = ap.parse_args()

    assert self_validate()
    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} pending={st.pending_jobs}",
          flush=True)
    try:
        u = svc.usage()
        print(f"QPU budget: {u.get('usage_remaining_seconds')}s remaining "
              f"/ limit {u.get('usage_limit_seconds')}s", flush=True)
    except Exception as e:
        print("usage probe:", e)

    chain, cost, twoq_name = pick_chain4(backend)
    print(f"Calibration-gated 4-chain {chain} (2q={twoq_name}, cost={cost:.5f})", flush=True)
    layout, n2_best = scan_layout(backend, chain)
    print(f"Layout scan (24 perms): best {layout} -> {n2_best} 2q gates", flush=True)

    pubs_meta = build_pubs()
    total_shots = sum(p[3] for p in pubs_meta)
    print(f"PUBs: {len(pubs_meta)} (8 switch / 8 null_fwd / 8 null_rev / 4 sentinel), "
          f"total shots {total_shots}, shuffle seed {SHUFFLE_SEED}", flush=True)

    from qiskit import transpile
    print("Transpiling + LIVE re-audit...", flush=True)
    tqcs, metas, hist = [], [], {}
    audit_ok = True
    for lab, kind, qc, shots, meta in pubs_meta:
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=3)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        meta = {**meta, "twoq": n2, "depth": tqc.depth()}
        if kind in ("switch", "sentinel"):
            hist[n2] = hist.get(n2, 0) + 1
            if n2 > MAX_SWITCH_2Q:
                audit_ok = False
        tqcs.append(tqc)
        metas.append(meta)
    print(f"  switch+sentinel 2q histogram on LIVE target: {hist}")
    print(f"  LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} (class bound <= {MAX_SWITCH_2Q})",
          flush=True)
    if not audit_ok:
        print("ABORT per pre-reg: payload exceeded the audited 2q class.")
        return 1
    if args.scan or not args.submit:
        print("\n--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp108-ico-refrigeration", "cycle": "C4558-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp108-ico-refrigeration-preregistration.md",
        "gates": {"retention_min": 0.85, "therm_band": 0.05, "win_floor": 0.08},
        "shuffle_seed": SHUFFLE_SEED, "chain": list(chain), "chain_cost": cost,
        "layout": layout, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, 'w') as f:
        json.dump(manifest, f, indent=1)
    print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
    print(f"Manifest -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
