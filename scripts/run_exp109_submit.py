#!/usr/bin/env python3
"""run_exp109_submit.py — Exp109 superdense coding, hardware submission (Whisper C4590).

Frozen prereg: experiments/exp109-superdense-coding-preregistration.md
Usage: python3 scripts/run_exp109_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
--scan (default): transpile audit only, FREE. --submit: spend QPU.
"""
import argparse
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
ENC = {"00": [], "01": ["x"], "10": ["z"], "11": ["z", "x"]}
SHOTS_PAYLOAD = 4000
SHOTS_SENT = 2000
SHUFFLE_SEED = 4590


def pick_pair(backend):
    """Calibration-gated: min (2q error + both readouts) over coupled edges (exp91 logic)."""
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else (
        'ecr' if 'ecr' in target.operation_names else None)
    best, best_cost = None, 1e9
    for (a, b), inst in (target[twoq] if twoq else {}).items():
        err2 = getattr(inst, 'error', None)
        if err2 is None:
            continue
        try:
            roa = target['measure'][(a,)].error
            rob = target['measure'][(b,)].error
        except Exception:
            roa = rob = 0.0
        cost = err2 + (roa or 0) + (rob or 0)
        if cost < best_cost:
            best_cost, best = cost, (a, b)
    return best, best_cost, twoq


def payload(m, entangled):
    qc = QuantumCircuit(2, 2)
    if entangled:
        qc.h(0)
        qc.cx(0, 1)
    qc.barrier()          # fence: keep the encoding slot un-optimizable
    for g in ENC[m]:
        getattr(qc, g)(0)
    qc.barrier()          # (Exp105 lesson: transpiler cancels CX.I.CX)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def sentinel(bits):
    qc = QuantumCircuit(2, 2)
    for i, b in enumerate(bits):
        if b == "1":
            qc.x(i)
    qc.measure([0, 1], [0, 1])
    return qc


def build_all():
    ent = []
    for arm, e in (("main", True), ("null", False)):
        for m in ENC:
            ent.append((f"{arm}_{m}", arm, payload(m, e), SHOTS_PAYLOAD,
                        {"label": f"{arm}_{m}", "kind": arm, "message": m,
                         "shots": SHOTS_PAYLOAD}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = [(f"sent_{b}", "sentinel", sentinel(b), SHOTS_SENT,
              {"label": f"sent_{b}", "kind": "sentinel", "prep": b,
               "shots": SHOTS_SENT}) for b in ("00", "11")]
    return [sents[0]] + ent + [sents[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp109")
    args = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    pair, cost, twoq = pick_pair(backend)
    print(f"pair={pair} cost={cost:.5f} 2q={twoq}")

    tqcs, metas, audit_ok = [], [], True
    for lab, kind, qc, shots, meta in build_all():
        tqc = transpile(qc, backend, initial_layout=list(pair),
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        expected = 2 if kind == "main" else (1 if kind == "null" else 0)
        if n2 != expected:
            audit_ok = False
            print(f"  AUDIT MISMATCH {lab}: 2q={n2} expected {expected}")
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
    print(f"LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} ({len(tqcs)} pubs)")
    if not audit_ok:
        print("ABORT per prereg: 2q skeleton drifted.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp109-superdense-coding", "cycle": "C4590-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp109-superdense-coding-preregistration.md",
        "gates": {"G1_win_floor": 0.55, "G2_null_band": 0.03,
                  "G3_sentinel_floor": 0.95},
        "prefiled_expectation": [0.93, 0.97],
        "shuffle_seed": SHUFFLE_SEED, "pair": list(pair), "pair_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
