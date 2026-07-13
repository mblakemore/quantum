#!/usr/bin/env python3
"""exp127_bgk_hlf_sim.py — THE SHALLOW-CIRCUIT COMPUTATIONAL BRIDGE: the 2D
Hidden Linear Function solver, sim tier (Whisper C4673; Creator: run the BGK
computational-bridge sim. Substrate claude-opus-4-8).

THE THEOREM (Bravyi-Gosset-Koenig, Science 2018, arXiv:1704.00690): the 2D-HLF
relation problem is solved WITH CERTAINTY by a CONSTANT-DEPTH quantum circuit
of 1- and 2-qubit gates local on a 2D grid, while any bounded-fan-in classical
circuit solving it with high probability needs depth Omega(log n). Unconditional
(no hardness conjectures) — the ONLY computational-advantage theorem that lives
at exactly our depth. BGKT 2020 (Nat. Phys.) proves the separation SURVIVES
noise, via a construction that plays the MAGIC-SQUARE game (F106's exact 8/9
game) between input pairs — so the classical hardness is inherited from the
contextuality F106 certified at 196 sigma.

HLF instance: symmetric adjacency A (grid edges, F_2), diagonal b in {0,1}^n.
q(x) = 2*sum_{i<j} A_ij x_i x_j + sum_i b_i x_i   (mod 4).
L_q = ker(A mod 2) = {x : A x = 0 mod 2}. Solution: z with
q(x) = 2*(z.x mod 2) mod 4  for ALL x in L_q.
Quantum solver U_q (CONSTANT depth): H^n | CZ per edge | S per b_i=1 | H^n |
measure -> z is a valid solution (P=1 noiseless).

HONESTY FENCE (frozen in groundwork C4666): a finite-instance run does NOT
prove QNC0 != NC0 — the separation is asymptotic (depth-SCALING). The sim-tier
deliverables are (a) constant-depth quantum CORRECTNESS (P(valid)=1), (b) the
valid-z set recomputed IN-ARTIFACT (the C4523/Exp126 enumerated-bound standard),
(c) the DEPTH LEDGER: quantum CZ-layer count constant across an n-ladder, (d)
NISQ noise survival, (e) the F106 through-line made explicit.
"""
import itertools
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile


def grid_edges(rows, cols):
    """2D grid graph on rows*cols qubits, index i = r*cols+c."""
    E = []
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            if c + 1 < cols:
                E.append((i, i + 1))
            if r + 1 < rows:
                E.append((i, i + cols))
    return E


def q_form(x, A, b):
    """q(x) mod 4 for bit-tuple x."""
    n = len(x)
    quad = sum(A[i][j] * x[i] * x[j] for i in range(n) for j in range(i + 1, n))
    lin = sum(b[i] * x[i] for i in range(n))
    return (2 * quad + lin) % 4


def kernel_Lq(A, b, n):
    """L_q = radical of the Z_4 XOR-polarization
    <x,y> = q(x^y) - q(x) - q(y) mod 4:  L_q = {x : <x,y> = 0 for all y}.
    (NOT the naive ker(A mod 2) — the quadratic term does not split under XOR;
    caught at sim tier C4673, statevector support did not match until fixed.)"""
    allx = list(itertools.product([0, 1], repeat=n))

    def pol(x, y):
        xy = tuple(x[i] ^ y[i] for i in range(n))
        return (q_form(xy, A, b) - q_form(x, A, b) - q_form(y, A, b)) % 4
    return [x for x in allx if all(pol(x, y) == 0 for y in allx)]


def valid_z_set(A, b, n):
    """z valid iff q(x) == 2*(z.x mod 2) mod 4 for all x in L_q. Enumerated
    IN-ARTIFACT — this IS the classical bound object (the solution affine
    subspace), recomputed not cited (C4523/Exp126 standard). Verified equal to
    the circuit's Gauss-sum support at sim tier."""
    L = kernel_Lq(A, b, n)
    valid = []
    for z in itertools.product([0, 1], repeat=n):
        if all(q_form(x, A, b) == (2 * (sum(z[i] * x[i] for i in range(n)) % 2))
               % 4 for x in L):
            valid.append(z)
    return valid, L


def hlf_circuit(A, b, n, edges):
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.barrier()
    for (i, j) in edges:
        if A[i][j]:
            qc.cz(i, j)
    for i in range(n):
        if b[i]:
            qc.s(i)
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def edge_coloring_layers(edges, n):
    """Greedy edge coloring -> number of parallel CZ layers (= circuit CZ
    depth). For a 2D grid this is a CONSTANT (<=4) independent of n."""
    color = {}
    for e in edges:
        used = set()
        for f, c in color.items():
            if set(e) & set(f):
                used.add(c)
        k = 0
        while k in used:
            k += 1
        color[e] = k
    return (max(color.values()) + 1) if color else 0


def noiseless_verify(A, b, n, edges):
    from qiskit_aer import AerSimulator
    valid, L = valid_z_set(A, b, n)
    valid_set = set(valid)
    qc = hlf_circuit(A, b, n, edges)
    be = AerSimulator()
    cts = be.run(qc, shots=40000).result().get_counts()
    tot = sum(cts.values())
    good = 0
    support = set()
    for k, v in cts.items():
        z = tuple(int(c) for c in k[::-1])  # little-endian -> qubit order
        support.add(z)
        if z in valid_set:
            good += v
    p_valid = good / tot
    return p_valid, valid, L, support


def fake_preview(A, b, n, edges):
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    valid, _ = valid_z_set(A, b, n)
    valid_set = set(valid)
    be = AerSimulator.from_backend(FakeMarrakesh())
    qc = hlf_circuit(A, b, n, edges)
    tqc = transpile(qc, be, optimization_level=1, seed_transpiler=4673)
    n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
             and inst.operation.name != "barrier")
    cts = be.run(tqc, shots=40000).result().get_counts()
    tot = sum(cts.values())
    good = sum(v for k, v in cts.items()
               if tuple(int(c) for c in k[::-1]) in valid_set)
    return good / tot, n2, tqc.depth()


def main():
    out = {"instances": {}, "depth_ladder": {}}
    # --- primary instance: 2x2 grid (4-cycle), b=(1,0,0,1) ---
    rows, cols = 2, 2
    n = rows * cols
    edges = grid_edges(rows, cols)
    A = [[0] * n for _ in range(n)]
    for (i, j) in edges:
        A[i][j] = A[j][i] = 1
    b = [1, 0, 0, 1]
    p_valid, valid, L, support = noiseless_verify(A, b, n, edges)
    p_fake, n2_fake, d_fake = fake_preview(A, b, n, edges)
    cz_layers = edge_coloring_layers(edges, n)
    print(f"INSTANCE 2x2 grid n={n} edges={edges} b={b}")
    print(f"  |L_q|={len(L)}  |valid_z|={len(valid)}  (recomputed in-artifact)")
    print(f"  valid_z set = {valid}")
    print(f"  quantum support subset of valid_z: "
          f"{support.issubset(set(valid))}  (P_valid={p_valid:.4f})")
    print(f"  logical CZ-layers (edge-coloring) = {cz_layers}  [constant]")
    print(f"  FakeMarrakesh: P_valid={p_fake:.4f}  routed 2q={n2_fake} "
          f"depth={d_fake}")
    out["instances"]["2x2"] = {
        "n": n, "edges": edges, "b": b, "Lq_size": len(L),
        "valid_z": [list(z) for z in valid], "P_valid_noiseless": p_valid,
        "support_valid": support.issubset(set(valid)),
        "cz_layers_logical": cz_layers,
        "P_valid_fake": p_fake, "routed_2q_fake": n2_fake,
        "depth_fake": d_fake}

    # --- depth ladder: CZ-layers stays constant as the grid grows ---
    print("\nDEPTH LADDER (logical CZ-layers vs grid size):")
    for (r, c) in [(2, 2), (2, 3), (3, 3), (3, 4), (4, 4)]:
        e = grid_edges(r, c)
        L_layers = edge_coloring_layers(e, r * c)
        out["depth_ladder"][f"{r}x{c}"] = {"n": r * c, "edges": len(e),
                                           "cz_layers": L_layers}
        print(f"  {r}x{c}: n={r*c:2d} edges={len(e):2d} "
              f"CZ-layers={L_layers}  H-layers=2  -> total const depth")

    ok = (p_valid > 0.999 and support.issubset(set(valid))
          and all(v["cz_layers"] <= 4 for v in out["depth_ladder"].values()))
    out["design_valid"] = bool(ok)
    print(f"\nDESIGN CHECK (P_valid=1, support valid, depth const <=4): "
          f"{'PASS' if ok else 'FAIL'}")
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "..",
                                     "results", "exp127_feasibility.json"),
                        "w"), indent=1, default=float)
    print("wrote results/exp127_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
