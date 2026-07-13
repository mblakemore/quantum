#!/usr/bin/env python3
"""run_exp127hw_submit.py — Exp127-HW: the 2D-HLF constant-depth solver ON
SILICON (Whisper C4674, substrate claude-opus-4-8). The frozen n=4 instance
from the C4673 sim flies — earning the campaign's first computational-genre
on-silicon F-number (Ember C4154 determination).

Frozen instance (from exp127_bgk_hlf_sim.py, sim-verified P_valid=1 noiseless):
  2x2 grid, edges [(0,1),(0,2),(1,3),(2,3)], b=[1,0,0,1].
  valid_z = {(0,0,0,1),(0,1,1,0),(1,0,0,0),(1,1,1,1)}  (recomputed in-artifact).
Circuit: H^4 | CZ per edge | S on q0,q3 | H^4 | measure.

HONESTY FENCE (frozen): a finite instance does NOT prove QNC0 != NC0. The
on-silicon claim is bounded: the constant-depth solver produces valid HLF
solutions FAR above the uniform floor (4/16 = 0.25) AND covers the whole
solution coset — the theorem carries the asymptotic separation.

Usage: python3 scripts/run_exp127hw_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp127_bgk_hlf_sim import (grid_edges, hlf_circuit,  # noqa: E402
                                valid_z_set)
from qiskit import QuantumCircuit  # noqa: E402

SHOTS = 40000
SHOTS_SENT = 4000
SEED = 4674
N = 4
EDGES = grid_edges(2, 2)
A = [[0] * N for _ in range(N)]
for (i, j) in EDGES:
    A[i][j] = A[j][i] = 1
B = [1, 0, 0, 1]


def pick_chain(backend, length=4):
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
    ro = {q: (getattr(i, 'error', 0.0) or 0.0)
          for (q,), i in target['measure'].items()}
    best, bc = None, 1e9

    def dfs(path, cost):
        nonlocal best, bc
        if len(path) == length:
            tot = cost + sum(ro.get(q, 0) for q in path)
            if tot < bc:
                bc, best = tot, list(path)
            return
        for nb in adj.get(path[-1], ()):
            if nb not in path:
                dfs(path + [nb], cost + err[(path[-1], nb)])
    for a in adj:
        for b in adj[a]:
            dfs([a, b], err[(a, b)])
    return best, bc


def sentinel(bits):
    qc = QuantumCircuit(N, N)
    for i, ch in enumerate(bits):
        if ch == "1":
            qc.x(i)
    qc.measure(range(N), range(N))
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp127hw")
    args = ap.parse_args()

    valid, L = valid_z_set(A, B, N)
    print(f"frozen valid_z ({len(valid)}): {valid}  |L_q|={len(L)}")

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    chain, cost = pick_chain(backend)
    print(f"chain={chain} cost={cost:.5f}")

    qc = hlf_circuit(A, B, N, EDGES)
    tqc = transpile(qc, backend, initial_layout=chain,
                    seed_transpiler=SEED, optimization_level=1)
    n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
             and inst.operation.name != "barrier")
    print(f"HLF solver: routed 2q={n2} depth={tqc.depth()} "
          f"(logical: 4 CZ + 2 H-layers)")
    tsents = []
    for bits in ("0000", "1111"):
        ts = transpile(sentinel(bits), backend, initial_layout=chain,
                       seed_transpiler=SEED, optimization_level=1)
        tsents.append((bits, ts))
    audit_ok = (n2 <= 14)  # sim fake gave 10; ceiling for routing drift
    print(f"LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} (routed 2q<=14)")
    if not audit_ok:
        print("ABORT: routing drift beyond ceiling.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    pubs = [(tqc, None, SHOTS)] + [(ts, None, SHOTS_SENT)
                                   for _, ts in tsents]
    job = SamplerV2(mode=backend).run(pubs)
    jid = job.job_id()
    manifest = {
        "experiment": "exp127hw-bgk-hlf-solver", "cycle": "C4674-whisper",
        "substrate": "claude-opus-4-8", "backend": args.backend,
        "tag": args.tag,
        "finding": "experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md",
        "instance": {"grid": "2x2", "edges": EDGES, "b": B},
        "valid_z": [list(z) for z in valid],
        "uniform_floor": len(valid) / 2 ** N,
        "gates": {"W1_SOLVER": "P_valid > 0.25 + 5se",
                  "W2_MAJORITY": "P_valid > 0.5 + 5se",
                  "W3_COVERAGE": "all 4 valid_z prob > 0.08",
                  "G_SENT": 0.95},
        "prefiled_expectation": {"P_valid_fake": 0.963, "P_valid_hw": [0.82, 0.93]},
        "chain": chain, "routed_2q": n2, "hw_depth": tqc.depth(),
        "sentinel_order": ["0000", "1111"],
        "job_id": jid,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
