#!/usr/bin/env python3
"""run_exp129_submit.py — Exp129 GHZ-vs-SQL metrology, hardware submission
(Whisper C4668). Frozen prereg: experiments/exp129-ghz-sql-preregistration.md
Usage: python3 scripts/run_exp129_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp129_ghz_sql_sim import PHIS, build_ghz, build_sep  # noqa: E402

SHOTS = 8000
SHOTS_SENT = 2000
SHUFFLE_SEED = 4668


def pick_star(backend):
    """Best star: center c with two neighbors a,b minimizing
    err(c,a)+err(c,b)+readouts(c,a,b). Layout order [c, a, b] = logical
    [q0=center, q1, q2]."""
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    err, adj = {}, {}
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        err[(a, b)] = err[(b, a)] = e
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    ro = {q: (getattr(inst, 'error', 0.0) or 0.0)
          for (q,), inst in target['measure'].items()}
    best, best_cost = None, 1e9
    for c, nbrs in adj.items():
        ns = sorted(nbrs, key=lambda x: err[(c, x)] + ro.get(x, 0))
        if len(ns) < 2:
            continue
        a, b = ns[0], ns[1]
        cost = (err[(c, a)] + err[(c, b)]
                + ro.get(c, 0) + ro.get(a, 0) + ro.get(b, 0))
        if cost < best_cost:
            best_cost, best = cost, [c, a, b]
    return best, best_cost


def sentinel(bits):
    qc = QuantumCircuit(3, 3)
    for i, b in enumerate(bits):
        if b == "1":
            qc.x(i)
    qc.measure(range(3), range(3))
    return qc


def build_all():
    ent = []
    for j, phi in enumerate(PHIS):
        ent.append((f"ghz_{j}", "ghz", build_ghz(phi),
                    {"label": f"ghz_{j}", "kind": "ghz", "j": j, "phi": phi,
                     "shots": SHOTS}))
        ent.append((f"sep_{j}", "sep", build_sep(phi),
                    {"label": f"sep_{j}", "kind": "sep", "j": j, "phi": phi,
                     "shots": SHOTS}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = [(f"sent_{b}", "sentinel", sentinel(b),
              {"label": f"sent_{b}", "kind": "sentinel", "prep": b,
               "shots": SHOTS_SENT}) for b in ("000", "111")]
    return [sents[0]] + ent + [sents[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp129")
    args = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    star, cost = pick_star(backend)
    print(f"star={star} cost={cost:.5f}")

    tqcs, metas, audit_ok = [], [], True
    for lab, kind, qc, meta in build_all():
        tqc = transpile(qc, backend, initial_layout=star,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        expected = 4 if kind == "ghz" else 0
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
        "experiment": "exp129-ghz-sql", "cycle": "C4668-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp129-ghz-sql-preregistration.md",
        "gates": {"W1_HEISENBERG": "R > 1 + 5se",
                  "W2_SQL_ABS": "9V3^2 > 3 + 5se",
                  "G_FREQ": "amp(k=3) > 2x max other", "G_SENT": 0.95},
        "prefiled_expectation": {"V3": [0.92, 0.96], "R": [2.5, 2.9]},
        "shuffle_seed": SHUFFLE_SEED, "star": star, "star_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
