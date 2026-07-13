#!/usr/bin/env python3
"""run_exp134_submit.py — Exp134: the HLF solver NISQ-BOUNDARY LADDER
(Whisper C4675, substrate claude-opus-4-8). Extends F-earning Exp127-HW: the
2D-HLF solver has O(1) LOGICAL depth, but a 2D grid does not embed in heavy-hex,
so ROUTED depth grows with n. This ladder (n=4,6,9) maps where the constant-
depth advantage survives real routing vs where it inverts — the computational
edition of the F85/F130 scaling question. Both outcomes are findings.

Per grid: build the HLF instance, recompute valid_z IN-ARTIFACT (Gauss-sum
support standard), verify noiseless P=1, transpile (auto-layout, honest routing),
report routed CZ + depth, fly. Grade P_valid(n) vs the per-instance uniform floor.

Usage: python3 scripts/run_exp134_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp127_bgk_hlf_sim import (grid_edges, hlf_circuit,  # noqa: E402
                                valid_z_set)

GRIDS = [(2, 2), (2, 3), (3, 3)]     # n = 4, 6, 9
SHOTS = 40000
SHOTS_SENT = 4000
SEED = 4675


# Non-degenerate b per grid (chosen C4675 by min-floor search over all b:
# an alternating/naive b collapses L_q -> floor=1, a useless instance. These
# give floors 0.25/0.25/0.125 so "beats chance" is a meaningful gate.)
B_BY_GRID = {
    (2, 2): [0, 0, 0, 0],
    (2, 3): [1, 0, 1, 1, 0, 1],
    (3, 3): [0] * 9,
}


def make_instance(rows, cols):
    n = rows * cols
    edges = grid_edges(rows, cols)
    A = [[0] * n for _ in range(n)]
    for (i, j) in edges:
        A[i][j] = A[j][i] = 1
    b = B_BY_GRID[(rows, cols)]
    return n, edges, A, b


def noiseless_pvalid(A, b, n, edges):
    from qiskit_aer import AerSimulator
    valid, L = valid_z_set(A, b, n)
    vs = set(valid)
    cts = AerSimulator().run(hlf_circuit(A, b, n, edges),
                             shots=20000).result().get_counts()
    tot = sum(cts.values())
    good = sum(v for k, v in cts.items()
               if tuple(int(c) for c in k[::-1]) in vs)
    return good / tot, valid, L


def sentinel(n, ones):
    qc = QuantumCircuit(n, n)
    if ones:
        for i in range(n):
            qc.x(i)
    qc.measure(range(n), range(n))
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp134")
    args = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")

    pubs, metas = [], []
    audit_ok = True
    for (r, c) in GRIDS:
        n, edges, A, b = make_instance(r, c)
        p0, valid, L = noiseless_pvalid(A, b, n, edges)
        floor = len(valid) / 2 ** n
        qc = hlf_circuit(A, b, n, edges)
        tqc = transpile(qc, backend, optimization_level=1,
                        seed_transpiler=SEED)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        cz_layers_logical = 4 if n >= 9 else (3 if n == 6 else 2)
        ok = abs(p0 - 1.0) < 0.02
        audit_ok &= ok
        print(f"grid {r}x{c} n={n}: noiseless P={p0:.4f} "
              f"|valid_z|={len(valid)} floor={floor:.4f} | "
              f"logical CZ-layers={cz_layers_logical} routed 2q={n2} "
              f"depth={tqc.depth()}  {'OK' if ok else 'FAIL-NOISELESS'}")
        pubs.append((tqc, None, SHOTS))
        metas.append({"grid": f"{r}x{c}", "n": n, "edges": edges, "b": b,
                      "valid_z": [list(z) for z in valid], "floor": floor,
                      "noiseless_P": p0, "routed_2q": n2,
                      "cz_layers_logical": cz_layers_logical,
                      "hw_depth": tqc.depth(), "shots": SHOTS})
    # one sentinel pair on the largest register (n=9)
    nmax = GRIDS[-1][0] * GRIDS[-1][1]
    for ones in (False, True):
        ts = transpile(sentinel(nmax, ones), backend, optimization_level=1,
                       seed_transpiler=SEED)
        pubs.append((ts, None, SHOTS_SENT))
        metas.append({"kind": "sentinel", "ones": ones, "n": nmax,
                      "shots": SHOTS_SENT})
    print(f"LIVE AUDIT (noiseless P=1 all grids): "
          f"{'PASS' if audit_ok else 'FAIL'} ({len(pubs)} pubs)")
    if not audit_ok:
        print("ABORT: a grid failed noiseless verification.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(pubs)
    jid = job.job_id()
    manifest = {
        "experiment": "exp134-hlf-nisq-boundary", "cycle": "C4675-whisper",
        "substrate": "claude-opus-4-8", "backend": args.backend,
        "tag": args.tag, "grids": [f"{r}x{c}" for r, c in GRIDS],
        "gates": {"per_grid_W1": "P_valid > floor + 5se",
                  "W_BOUNDARY": "both-outcomes: locate n* where P_valid<0.5",
                  "G_SENT": 0.95},
        "prefiled_expectation": {"n4": 0.90, "n6": "0.6-0.8", "n9": "boundary"},
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
