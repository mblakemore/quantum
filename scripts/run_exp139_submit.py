#!/usr/bin/env python3
"""Exp139 coherent entropy concentration seeded at F118 — HARDWARE SUBMIT (Whisper C4720).
Pre-reg: experiments/exp139-concentration-preregistration.md (FROZEN). ENGINEERING artifact,
honestly scoped (classical compression, NOT new ICO physics). 4-qubit chain (q0,q1,q2 inputs,
q3 dest); 8 basis-prep concentration circuits (pool to cold 0.21 AND bath 0.25) + 2 single-input
references; ONE SamplerV2 job, live 2q re-audit, frozen seed.

Usage: --scan (FREE) | --submit (spends QPU) --backend ibm_marrakesh
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
from exp139_concentration import conc_circuit, single_circuit, SHOTS, P_COLD, P_BATH

SHUFFLE_SEED = 4720
MAX_2Q = 40
# module-level integrity-gate constants (overridable by the exp139b re-fly wrapper; recorded in manifest)
S000_MAX = 0.05
S111_MIN = 0.95


def pick_chain4(backend):
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
    from qiskit import transpile
    qc = conc_circuit((1, 1, 1))   # same Toffoli skeleton regardless of prep
    best, best_n = None, 1e9
    for perm in itertools.permutations(chain):
        tqc = transpile(qc, backend, initial_layout=list(perm),
                        seed_transpiler=SHUFFLE_SEED, optimization_level=3)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2 and i.operation.name != "barrier")
        if n2 < best_n:
            best_n, best = n2, list(perm)
    return best, best_n


def build_pubs():
    ent = []
    for b in itertools.product([0, 1], repeat=3):
        ent.append((f"conc_{b[0]}{b[1]}{b[2]}", "conc", conc_circuit(b), SHOTS,
                    {"label": f"conc_{b[0]}{b[1]}{b[2]}", "kind": "conc", "prep": list(b), "shots": SHOTS}))
    for b0 in (0, 1):
        ent.append((f"single_{b0}", "single", single_circuit(b0), SHOTS,
                    {"label": f"single_{b0}", "kind": "single", "prep": [b0], "shots": SHOTS}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    return [ent[i] for i in rng.permutation(len(ent))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp139")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} pending={st.pending_jobs}", flush=True)
    try:
        u = svc.usage()
        print(f"QPU budget: {u.get('usage_remaining_seconds')}s / {u.get('usage_limit_seconds')}s", flush=True)
    except Exception as e:
        print("usage probe:", e)

    chain, cost, twoq_name = pick_chain4(backend)
    print(f"Calibration-gated 4-chain {chain} (2q={twoq_name}, cost={cost:.5f})", flush=True)
    layout, n2 = scan_layout(backend, chain)
    print(f"Layout scan: best {layout} -> {n2} 2q gates", flush=True)

    pubs = build_pubs()
    from qiskit import transpile
    print("Transpiling + LIVE re-audit...", flush=True)
    tqcs, metas, hist = [], [], {}
    audit_ok = True
    for lab, kind, qc, shots, meta in pubs:
        il = layout if qc.num_qubits == len(layout) else layout[:qc.num_qubits]
        tqc = transpile(qc, backend, initial_layout=il,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=3)
        nn = sum(1 for i in tqc.data if i.operation.num_qubits == 2 and i.operation.name != "barrier")
        meta = {**meta, "twoq": nn, "depth": tqc.depth()}
        if kind == "conc":
            hist[nn] = hist.get(nn, 0) + 1
            if nn > MAX_2Q:
                audit_ok = False
        tqcs.append(tqc)
        metas.append(meta)
    print(f"  conc 2q histogram on LIVE target: {hist}")
    print(f"  LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} (bound <= {MAX_2Q})", flush=True)
    if not audit_ok:
        print("ABORT per pre-reg.")
        return 1
    if args.scan or not args.submit:
        print("\n--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {"experiment": "exp139-concentration", "cycle": "C4720-whisper",
                "backend": args.backend, "tag": args.tag,
                "prereg": "experiments/exp139-concentration-preregistration.md",
                "p_cold": P_COLD, "p_bath": P_BATH,
                "gates": {"s000_max": S000_MAX, "s111_min": S111_MIN},
                "shuffle_seed": SHUFFLE_SEED, "chain": list(chain), "layout": layout,
                "job_id": jid, "metas": metas}
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    json.dump(manifest, open(outp, 'w'), indent=1)
    print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
    print(f"Manifest -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
