#!/usr/bin/env python3
"""Exp106 capacity activation — HARDWARE SUBMIT (Whisper C4529).
Pre-reg: experiments/exp106-capacity-activation-preregistration.md (FROZEN pre --submit).
Reuses the Exp105 submit discipline: calibration-gated pair, ONE SamplerV2 job,
pre-registered shuffle, F77 sentinel triplet START/MID/END, live re-audit.

Usage:  --scan (FREE: pair pick + live audit)  |  --submit (spends QPU)
        --backend ibm_marrakesh (default) --tag exp106
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from run_exp105_causal_game_submit import pick_pair
from exp105_causal_game_feasibility import build_game_circuit
from exp106_capacity_activation import all_entries, build_circuit, SHOTS_SENT

SHUFFLE_SEED = 4529  # pre-registered
EXPECTED_SWITCH_2Q = 4


def build_pubs():
    ent = all_entries()  # 64 (label, kind, a, b, bit, shots)
    rng = np.random.default_rng(SHUFFLE_SEED)
    order = rng.permutation(len(ent))
    shuffled = [ent[i] for i in order]
    entries = []
    for lab, kind, a, b, bit, shots in shuffled:
        qc = build_circuit(a, b, bit, definite=(kind == "null"))
        entries.append((lab, kind, qc, shots,
                        {"label": lab, "kind": kind, "pair": f"({a},{b})",
                         "input_bit": bit, "shots": shots}))
    # F77 sentinel triplet: START/MID/END (control-only readout, Exp105 template)
    sent = []
    for rep in ("start", "mid", "end"):
        for pname, pr, comm in (("(X,X)", ("X", "X"), True), ("(X,Z)", ("X", "Z"), False)):
            qc = build_game_circuit(pr[0], pr[1], definite=False)
            sent.append((f"sent_{rep}_{'commute' if comm else 'anticommute'}", "sentinel",
                         qc, SHOTS_SENT,
                         {"label": f"sent_{rep}_{'commute' if comm else 'anticommute'}",
                          "kind": "sentinel", "pair": pname, "commuting": comm,
                          "replicate": rep, "shots": SHOTS_SENT}))
    mid = len(entries) // 2
    final = sent[0:2] + entries[:mid] + sent[2:4] + entries[mid:] + sent[4:6]
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp106")
    args = ap.parse_args()

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

    pair, cost, twoq_name = pick_pair(backend)
    print(f"Calibration-gated pair {pair} (2q={twoq_name}, cost={cost:.5f})", flush=True)

    pubs_meta = build_pubs()
    total_shots = sum(p[3] for p in pubs_meta)
    print(f"PUBs: {len(pubs_meta)} (switch 32 / null 32 / sentinel 6), "
          f"total shots {total_shots}, shuffle seed {SHUFFLE_SEED}", flush=True)

    from qiskit import transpile
    print("Transpiling + LIVE re-audit...", flush=True)
    tqcs, metas, hist = [], [], {}
    audit_ok = True
    for lab, kind, qc, shots, meta in pubs_meta:
        tqc = transpile(qc, backend, initial_layout=list(pair),
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        meta = {**meta, "twoq": n2, "depth": tqc.depth()}
        if kind == "switch":
            hist[n2] = hist.get(n2, 0) + 1
            if n2 != EXPECTED_SWITCH_2Q:
                audit_ok = False
        tqcs.append(tqc)
        metas.append(meta)
    print(f"  switch-circuit 2q histogram on LIVE target: {hist}")
    print(f"  LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'}", flush=True)
    if not audit_ok:
        print("ABORT per pre-reg: switch skeleton drifted from {4:32}.")
        return 1
    if args.scan or not args.submit:
        print("\n--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp106-capacity-activation", "cycle": "C4529-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp106-capacity-activation-preregistration.md",
        "gates": {"sentinel_min_disc": 1.60, "null_D_band": 0.05, "win_floor": 0.10},
        "shuffle_seed": SHUFFLE_SEED, "pair": list(pair), "pair_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, 'w') as f:
        json.dump(manifest, f, indent=1)
    print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
    print(f"Manifest -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
