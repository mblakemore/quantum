#!/usr/bin/env python3
"""run_exp131_submit.py — Exp131 optimal-cloning ceiling, hardware submission
(Whisper C4670, Horizons-3 H1, substrate claude-opus-4-8).
Frozen prereg: experiments/exp131-cloning-preregistration.md
Usage: python3 scripts/run_exp131_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp131_cloning_sim import AXIS, measure_circuit  # noqa: E402

PARAMS = [0.76101, 0.22136, 0.26021, 0.80229]
SHOTS = 8000
SHOTS_SENT = 2000
SHUFFLE_SEED = 4670


def pick_center_line(backend):
    """Best 3-line b-a-c (a=center=input). Minimize err(a,b)+err(a,c)+readouts.
    Returns layout [a, b, c] mapping virtual [q0=input, q1=copyB, q2=anc]."""
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    err, adj = {}, {}
    for (x, y), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        err[(x, y)] = err[(y, x)] = e
        adj.setdefault(x, set()).add(y)
        adj.setdefault(y, set()).add(x)
    ro = {q: (getattr(inst, 'error', 0.0) or 0.0)
          for (q,), inst in target['measure'].items()}
    best, best_cost = None, 1e9
    for a, nbrs in adj.items():
        ns = sorted(nbrs, key=lambda x: err[(a, x)] + ro.get(x, 0))
        if len(ns) < 2:
            continue
        b, c = ns[0], ns[1]
        cost = (err[(a, b)] + err[(a, c)]
                + ro.get(a, 0) + ro.get(b, 0) + ro.get(c, 0))
        if cost < best_cost:
            best_cost, best = cost, [a, b, c]
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
    for arm in ("optimal", "cheat"):
        for name in AXIS:
            qc, exp = measure_circuit(PARAMS, name, arm)
            lab = f"{arm}_{name}"
            ent.append((lab, arm, qc, {"label": lab, "kind": arm,
                                       "state": name, "expected": exp,
                                       "basis": AXIS[name][1], "shots": SHOTS}))
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
    ap.add_argument("--tag", default="exp131")
    args = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    line, cost = pick_center_line(backend)
    print(f"line(center,b,c)={line} cost={cost:.5f}")
    # virtual [q0=input,q1=copyB,q2=anc] -> physical [center, b, c]
    layout = [line[0], line[1], line[2]]

    tqcs, metas, cheat2q = [], [], []
    for lab, arm, qc, meta in build_all():
        lay = layout[:qc.num_qubits]
        tqc = transpile(qc, backend, initial_layout=lay,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        if arm == "cheat":
            cheat2q.append(n2)
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
    opt2q = sorted(set(m["twoq"] for m in metas if m["kind"] == "optimal"))
    audit_ok = all(c == 1 for c in cheat2q) and len(opt2q) <= 2
    print(f"optimal-arm 2q counts: {opt2q} | cheat 2q: {set(cheat2q)}")
    print(f"LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} ({len(tqcs)} pubs)")
    if not audit_ok:
        print("ABORT per prereg: cheat must be 1 CX; optimal 2q must be stable.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp131-cloning", "cycle": "C4670-whisper",
        "substrate": "claude-opus-4-8",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp131-cloning-preregistration.md",
        "ceiling": 5 / 6, "prep_angles": PARAMS,
        "gates": {"W1_UNIVERSAL": "opt spread<0.05 & max<=5/6+5se",
                  "W2_NO_UNIVERSAL_BEAT": "cheat min < 5/6 - 5se",
                  "W3_CHEAT_TELL": "cheat spread>0.30 & opt spread<0.05",
                  "W4_CEILING_PROXIMITY": "opt mean > 5/6 - 0.06",
                  "G_SENT": 0.95},
        "prefiled_expectation": {"opt_perbasis": {"Z": 0.8187, "X": 0.8172,
                                                  "Y": 0.8191},
                                 "cheat_perbasis": {"Z": 0.9901, "X": 0.5003,
                                                    "Y": 0.4996}},
        "shuffle_seed": SHUFFLE_SEED, "line": line, "line_cost": cost,
        "opt2q_counts": opt2q, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
