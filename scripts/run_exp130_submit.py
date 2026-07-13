#!/usr/bin/env python3
"""run_exp130_submit.py — Exp130 GHZ Heisenberg ladder, hardware submission
(Whisper C4669, substrate claude-opus-4-8).
Frozen prereg: experiments/exp130-ghz-ladder-preregistration.md
Usage: python3 scripts/run_exp130_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp130_ghz_ladder_sim import (LADDER, NMAX, PHIS, build_ghz,  # noqa:E402
                                   build_sep_phi)

SHOTS = 4000
SHOTS_SENT = 2000
SHUFFLE_SEED = 4669


def pick_chain(backend, length=NMAX):
    """Best length-L path: min sum(2q errors along path) + sum(readouts).
    Greedy over all edges as seeds, DFS extend. Layout order = the path."""
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

    def dfs(path, cost):
        nonlocal best, best_cost
        if len(path) == length:
            tot = cost + sum(ro.get(q, 0) for q in path)
            if tot < best_cost:
                best_cost, best = tot, list(path)
            return
        for nb in adj.get(path[-1], ()):
            if nb not in path:
                dfs(path + [nb], cost + err[(path[-1], nb)])

    for a in adj:
        for b in adj[a]:
            dfs([a, b], err[(a, b)])
    return best, best_cost


def sentinel(bits):
    qc = QuantumCircuit(NMAX, NMAX)
    for i, b in enumerate(bits):
        if b == "1":
            qc.x(i)
    qc.measure(range(NMAX), range(NMAX))
    return qc


def build_all():
    ent = []
    for j, phi in enumerate(PHIS):
        ent.append((f"sep_{j}", "sep", NMAX, build_sep_phi(NMAX, phi),
                    {"label": f"sep_{j}", "kind": "sep", "j": j, "phi": phi,
                     "shots": SHOTS}))
        for n in LADDER:
            ent.append((f"ghz{n}_{j}", "ghz", n, build_ghz(n, phi),
                        {"label": f"ghz{n}_{j}", "kind": "ghz", "n": n,
                         "j": j, "phi": phi, "shots": SHOTS}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = [(f"sent_{b}", "sentinel", NMAX, sentinel(b),
              {"label": f"sent_{b}", "kind": "sentinel", "prep": b,
               "shots": SHOTS_SENT}) for b in ("00000", "11111")]
    return [sents[0]] + ent + [sents[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp130")
    args = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    chain, cost = pick_chain(backend)
    print(f"chain={chain} cost={cost:.5f}")

    tqcs, metas, audit_ok = [], [], True
    for lab, kind, nq, qc, meta in build_all():
        tqc = transpile(qc, backend, initial_layout=chain[:nq],
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        if kind == "ghz":
            expected = 2 * (meta["n"] - 1)
        else:
            expected = 0
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
        "experiment": "exp130-ghz-ladder", "cycle": "C4669-whisper",
        "substrate": "claude-opus-4-8",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp130-ghz-ladder-preregistration.md",
        "gates": {"W1_ADVANTAGE": "R(N) > 1 + 5se all rungs",
                  "W2_SCALING": "PERSISTS if R5>R2 & F5>F2 at 5se else TURNOVER",
                  "G_FREQ": "each peaks at k=N, >2x next", "G_SENT": 0.95},
        "prefiled_expectation": {"R": [2.0, 2.81, 3.72, 4.58],
                                 "Nstar": 5, "persists": True},
        "shuffle_seed": SHUFFLE_SEED, "chain": chain, "chain_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
