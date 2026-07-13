#!/usr/bin/env python3
"""run_exp126_submit.py — Exp126 magic-square game, hardware submission
(Whisper C4666, Horizons-3 H5).

Frozen prereg: experiments/exp126-magic-square-preregistration.md
Usage: python3 scripts/run_exp126_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
--scan (default): transpile audit only, FREE. --submit: spend QPU.
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp126_magic_square_sim import build, theorem_checks  # noqa: E402

SHOTS_MAIN = 20000
SHOTS_NULL = 4000
SHOTS_SENT = 2000
SHUFFLE_SEED = 4666


def pick_line(backend):
    """Calibration-gated best 4-qubit LINE: min sum(2q errors) + sum(readouts).
    Logical wiring maps l0=B1, l1=A1, l2=A2, l3=B2 (Alice middle)."""
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    err = {}
    adj = {}
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        err[(a, b)] = err[(b, a)] = e
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    ro = {}
    for (q,), inst in target['measure'].items():
        ro[q] = getattr(inst, 'error', 0.0) or 0.0
    best, best_cost = None, 1e9
    for a in adj:
        for b in adj[a]:
            for c in adj[b] - {a}:
                for d in adj[c] - {a, b}:
                    line = (a, b, c, d)
                    cost = (err[(a, b)] + err[(b, c)] + err[(c, d)]
                            + sum(ro.get(q, 0) for q in line))
                    if cost < best_cost:
                        best_cost, best = cost, line
    return best, best_cost, twoq


def sentinel(bits):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(4, 4)
    for i, b in enumerate(bits):
        if b == "1":
            qc.x(i)
    qc.measure(range(4), range(4))
    return qc


def build_all():
    ent = []
    for arm, e, shots in (("main", True, SHOTS_MAIN),
                          ("null", False, SHOTS_NULL)):
        for r in range(3):
            for c in range(3):
                lab = f"{arm}_r{r+1}c{c+1}"
                ent.append((lab, arm, build(r, c, e), shots,
                            {"label": lab, "kind": arm, "r": r, "c": c,
                             "shots": shots}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = [(f"sent_{b}", "sentinel", sentinel(b), SHOTS_SENT,
              {"label": f"sent_{b}", "kind": "sentinel", "prep": b,
               "shots": SHOTS_SENT}) for b in ("0000", "1111")]
    return [sents[0]] + ent + [sents[1]]


def expected_2q(kind, r, c):
    """Exact expectation for swap-free pubs (c != 2 index); c3 pubs routed."""
    if kind == "sentinel":
        return 0
    n = 0
    if kind == "main":
        n += 2                      # two Bell preps, both adjacent
    if r == 2:
        n += 1                      # CZ(A1,A2) adjacent (Alice middle)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp126")
    args = ap.parse_args()

    ok, bound, n = theorem_checks()
    print(f"theorem checks: {'PASS' if ok else 'FAIL'} bound={bound:.10f}")
    if not ok:
        return 1

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    line, cost, twoq = pick_line(backend)
    print(f"line={line} cost={cost:.5f} 2q={twoq}")
    # logical (q0=B1,q1=A1,q2=A2,q3=B2) -> physical line l0-l1-l2-l3
    layout = list(line)

    tqcs, metas, audit_ok = [], [], True
    for lab, kind, qc, shots, meta in build_all():
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        r, c = meta.get("r"), meta.get("c")
        if kind == "sentinel" or (c is not None and c != 2):
            exp = expected_2q(kind, r, c)
            if n2 != exp:
                audit_ok = False
                print(f"  AUDIT MISMATCH {lab}: 2q={n2} expected {exp}")
        else:  # c3 pubs pay routing for CX(B1,B2) across the line
            if n2 > 12:
                audit_ok = False
                print(f"  AUDIT MISMATCH {lab}: routed 2q={n2} > ceiling 12")
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
    print("2q table:", {m["label"]: m["twoq"] for m in metas})
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
        "experiment": "exp126-magic-square", "cycle": "C4666-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp126-magic-square-preregistration.md",
        "classical_bound": bound,
        "gates": {"W1_GAME": "pooled > 8/9 + 5se",
                  "W2_MIN": "min context > 8/9 + 5se",
                  "G_NULL": "null pooled < 8/9", "G_SENT": 0.95},
        "prefiled_expectation": {"pooled": 0.9779, "min": 0.9689,
                                 "null": 0.663},
        "shuffle_seed": SHUFFLE_SEED, "line": layout, "line_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
