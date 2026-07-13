#!/usr/bin/env python3
"""exp126_magic_square_sim.py — THE KOBAYASHI MARU: Peres-Mermin magic-square
game, sim tier (Whisper C4666, Horizons-3 H5 — Creator directive: find a
MEASURABLE quantum advantage).

THE GAME (Mermin 1990; pseudo-telepathy form Brassard-Broadbent-Tapp 2005):
referee picks (row, col) uniformly from 9. Alice outputs 3 signs for her row
with product +1; Bob outputs 3 signs for his column with product = column
parity (+1, +1, -1). WIN iff they agree on the intersection cell. CLASSICAL
CEILING: 8/9 exactly — VERIFIED IN-CODE below by exhaustive enumeration over
all 4096 deterministic parity-respecting strategy pairs (shared randomness is
a convex combination, so deterministic suffices). QUANTUM VALUE: 1, via two
shared Bell pairs and per-context Pauli-group measurements.

THE SQUARE (operator identities verified in-code by explicit kron products):
        c1   c2   c3
   r1 [ XI   IX   XX ]   rows multiply to +I (all three)
   r2 [ IZ   ZI   ZZ ]   cols multiply to +I, +I, -I
   r3 [ XZ   ZX   YY ]
No classical assignment of +/-1 to the 9 cells satisfies all six parity
constraints (product over rows = +1, over cols = -1, same 9 numbers): that
contradiction IS the 8/9 ceiling.

APPARATUS: 4 qubits on a line B1-A1-A2-B2 (Alice middle: her entangled row-3
context CZ(A1,A2) is connectivity-free; Bob's col-3 Bell measurement pays the
routing — 3 of 9 contexts, audited). Prep: Bell(A1,B1) + Bell(A2,B2).
Derived third value per context: r3: YY = +(XZ)(ZX); c3: YY = -(XX)(ZZ)
(operator identities, checked in-code). Parity constraints are satisfied BY
CONSTRUCTION (third value computed as the signed product), so grading reduces
to intersection agreement.

Arms: main_rc (9, Bell-prepped), null_rc (9, |0000> — no entanglement; a
no-entanglement player cannot beat the classical ceiling), sentinels.
"""
import itertools
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000
SHOTS_NULL = 4000

I2 = np.eye(2, dtype=complex)
PX = np.array([[0, 1], [1, 0]], dtype=complex)
PY = np.array([[0, -1j], [1j, 0]], dtype=complex)
PZ = np.array([[1, 0], [0, -1]], dtype=complex)
P = {"I": I2, "X": PX, "Y": PY, "Z": PZ}

# square[r][c] as 2-char labels, slot1 = first qubit of the side, slot2 = second
SQUARE = [["XI", "IX", "XX"],
          ["IZ", "ZI", "ZZ"],
          ["XZ", "ZX", "YY"]]
ROW_PARITY = [+1, +1, +1]
COL_PARITY = [+1, +1, -1]


def kron2(lab):
    return np.kron(P[lab[0]], P[lab[1]])


def theorem_checks():
    """(1) row/col operator products; (2) in-context commutation;
    (3) derived-value identities; (4) EXHAUSTIVE classical bound = 8/9."""
    ok = True
    for r in range(3):
        prod = kron2(SQUARE[r][0]) @ kron2(SQUARE[r][1]) @ kron2(SQUARE[r][2])
        ok &= np.allclose(prod, ROW_PARITY[r] * np.eye(4))
    for c in range(3):
        prod = kron2(SQUARE[0][c]) @ kron2(SQUARE[1][c]) @ kron2(SQUARE[2][c])
        ok &= np.allclose(prod, COL_PARITY[c] * np.eye(4))
    for trip in ([SQUARE[r] for r in range(3)]
                 + [[SQUARE[r][c] for r in range(3)] for c in range(3)]):
        for a, b in itertools.combinations(trip, 2):
            ok &= np.allclose(kron2(a) @ kron2(b), kron2(b) @ kron2(a))
    # derived-value identities: r3: XZ.ZX = +YY ; c3: XX.ZZ = -YY
    ok &= np.allclose(kron2("XZ") @ kron2("ZX"), kron2("YY"))
    ok &= np.allclose(kron2("XX") @ kron2("ZZ"), -kron2("YY"))
    # exhaustive classical ceiling: strategies = parity-respecting sign rows
    def rows_with_parity(par):
        return [s for s in itertools.product([1, -1], repeat=3)
                if s[0] * s[1] * s[2] == par]
    a_strats = list(itertools.product(*[rows_with_parity(ROW_PARITY[r])
                                        for r in range(3)]))
    b_strats = list(itertools.product(*[rows_with_parity(COL_PARITY[c])
                                        for c in range(3)]))
    best = 0.0
    for A in a_strats:
        for B in b_strats:
            wins = sum(1 for r in range(3) for c in range(3)
                       if A[r][c] == B[c][r])
            best = max(best, wins / 9.0)
    classical_bound = best
    ok &= abs(classical_bound - 8.0 / 9.0) < 1e-12
    return ok, classical_bound, len(a_strats) * len(b_strats)


# logical wiring: q0=B1, q1=A1, q2=A2, q3=B2
def build(r, c, entangled):
    qc = QuantumCircuit(4, 4)
    if entangled:
        qc.h(1)
        qc.cx(1, 0)   # Bell(A1,B1)
        qc.h(2)
        qc.cx(2, 3)   # Bell(A2,B2)
    qc.barrier()
    # Alice row context on (q1=slot1, q2=slot2)
    if r == 0:
        qc.h(1)
        qc.h(2)
    elif r == 1:
        pass  # Z basis
    else:
        qc.cz(1, 2)
        qc.h(1)
        qc.h(2)
    # Bob column context on (q0=slot1, q3=slot2)
    if c == 0:
        qc.h(0)          # XI -> X on B1 ; IZ -> Z on B2
    elif c == 1:
        qc.h(3)          # IX -> X on B2 ; ZI -> Z on B1
    else:
        qc.cx(0, 3)      # Bell basis: bit(q0 after H) = XX, bit(q3) = ZZ
        qc.h(0)
    qc.barrier()
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def alice_values(r, b1, b2):
    """b1,b2 = eigenvalue signs from q1,q2. Returns her 3 row values."""
    if r == 0:
        return [b1, b2, b1 * b2]          # XI, IX, XX
    if r == 1:
        return [b2, b1, b1 * b2]          # IZ(=Z on A2=q2), ZI(q1), ZZ
    return [b1, b2, b1 * b2]              # XZ, ZX, YY = +prod


def bob_values(c, b1, b2):
    """b1,b2 = signs from q0,q3. Returns his 3 column values (rows 1..3)."""
    if c == 0:
        return [b1, b2, b1 * b2]          # XI(B1), IZ(B2), XZ
    if c == 1:
        return [b2, b1, b1 * b2]          # IX(B2), ZI(B1), ZX
    return [b1, b2, -b1 * b2]             # XX, ZZ, YY = -prod


def grade(counts, r, c):
    tot = win = 0
    for key, v in counts.items():
        k = key[::-1]  # little-endian -> clbit order q0..q3
        s = [1 if ch == "0" else -1 for ch in k]
        a = alice_values(r, s[1], s[2])
        b = bob_values(c, s[0], s[3])
        tot += v
        if a[c] == b[r]:
            win += v
    p = win / tot
    return p, float(np.sqrt(max(p * (1 - p), 1e-9) / tot))


def main():
    ok, bound, n_strats = theorem_checks()
    print(f"THEOREM CHECKS: {'PASS' if ok else 'FAIL'} | classical bound "
          f"= {bound:.12f} (8/9 = {8/9:.12f}) via {n_strats} strategy pairs")
    if not ok:
        return 1
    out = {"classical_bound": bound}
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        res = {}
        for arm, ent, shots in (("main", True, SHOTS), ("null", False,
                                                        SHOTS_NULL)):
            ps = []
            for r in range(3):
                for c in range(3):
                    qc = build(r, c, ent)
                    tqc = transpile(qc, backend, optimization_level=1,
                                    seed_transpiler=4666)
                    cts = backend.run(tqc, shots=shots).result().get_counts()
                    p, se = grade(cts, r, c)
                    res[f"{arm}_r{r+1}c{c+1}"] = [p, se]
                    ps.append(p)
            res[f"{arm}_pooled"] = float(np.mean(ps))
        out[label] = res
        print(f"[{label}] main pooled = {res['main_pooled']:.4f} | "
              f"null pooled = {res['null_pooled']:.4f}")
        print(f"  per-context main:",
              {k: round(v[0], 4) for k, v in res.items()
               if k.startswith('main_r')})
    ok2 = out["noiseless"]["main_pooled"] > 0.999
    print("NOISELESS QUANTUM VALUE = 1 CHECK:", "PASS" if ok2 else "FAIL")
    out["design_valid"] = bool(ok and ok2)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp126_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp126_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
