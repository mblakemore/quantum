#!/usr/bin/env python3
"""run_exp128_submit.py — Exp128 2->1 QRAC, hardware submission
(Whisper C4667). Frozen prereg: experiments/exp128-qrac-preregistration.md
Usage: python3 scripts/run_exp128_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp128_qrac_sim import (THETA, build, build_classical,  # noqa: E402
                             classical_bound)

SHOTS = 20000
SHUFFLE_SEED = 4667


def pick_qubit(backend):
    """Best single qubit: min (readout error + sx error)."""
    target = backend.target
    best, best_cost = None, 1e9
    for (q,), inst in target['measure'].items():
        ro = getattr(inst, 'error', None)
        if ro is None:
            continue
        try:
            sx = target['sx'][(q,)].error or 0.0
        except Exception:
            sx = 0.0
        cost = ro + sx
        if cost < best_cost:
            best_cost, best = cost, q
    return best, best_cost


def build_all():
    ent = []
    for (x0, x1) in THETA:
        for q in (0, 1):
            lab = f"main_{x0}{x1}_q{q}"
            ent.append((lab, build(x0, x1, q),
                        {"label": lab, "kind": "main", "x0": x0, "x1": x1,
                         "q": q, "shots": SHOTS}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    cls = [(f"class_{x0}_q0", build_classical(x0),
            {"label": f"class_{x0}_q0", "kind": "class", "x0": x0,
             "shots": SHOTS}) for x0 in (0, 1)]
    return [cls[0]] + ent + [cls[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp128")
    args = ap.parse_args()

    bound, n = classical_bound()
    print(f"enumerated classical bound: {bound} ({n} pairs) "
          f"{'PASS' if abs(bound - 0.75) < 1e-12 else 'FAIL'}")
    if abs(bound - 0.75) > 1e-12:
        return 1

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    q, cost = pick_qubit(backend)
    print(f"qubit={q} cost={cost:.5f}")

    tqcs, metas, audit_ok = [], [], True
    for lab, qc, meta in build_all():
        tqc = transpile(qc, backend, initial_layout=[q],
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        if n2 != 0:
            audit_ok = False
            print(f"  AUDIT MISMATCH {lab}: 2q={n2} expected 0")
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
    print(f"LIVE AUDIT (zero-2q): {'PASS' if audit_ok else 'FAIL'} "
          f"({len(tqcs)} pubs)")
    if not audit_ok:
        print("ABORT per prereg.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp128-qrac", "cycle": "C4667-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp128-qrac-preregistration.md",
        "classical_bound": 0.75,
        "quantum_optimum": float(np.cos(np.pi / 8) ** 2),
        "gates": {"W1_QRAC": "pooled > 0.75 + 5se",
                  "W2_MIN": "min case > 0.75 + 5se",
                  "G_QBAND": "pooled <= 0.8536 + 5se",
                  "G_CLASS": "class pooled <= 0.75", "G_SENT": 0.95},
        "prefiled_expectation": {"pooled": 0.8453, "min": 0.8410,
                                 "class": 0.7447},
        "shuffle_seed": SHUFFLE_SEED, "qubit": q, "qubit_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
