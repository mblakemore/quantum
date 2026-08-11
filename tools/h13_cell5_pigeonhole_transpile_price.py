#!/usr/bin/env python3
"""
H13 Cell 5 pigeonhole — TRANSPILE PRICE for the weak-value circuit.

THE DEFECT THIS PAYS (C5060). Cell 6 was retired because its premise gate was priced from a
TEXTBOOK decomposition (3/6 gates modelled against 21 flown), and then its replacement cleared
the gate by 0.0007 at the BEST transpile while failing at the worst — a gate that passes or
fails on a transpiler seed is not a gate. So Cell 5 gets priced from the COMPILED circuit on
real heavy-hex connectivity, SWEPT ACROSS SEEDS, before any tank request. A single transpile is
a sample, not a cost.

THE CIRCUIT (working point handed over by the resolution pre-check, not guessed):
  3 system qubits (the "pigeons"), 1 ancilla pointer.
  prepare |+++> and ancilla |0>
  weak coupling  exp(-i eps Pi_same(0,1) (x) Y_anc),  Pi_same = (I + Z0 Z1)/2
  post-select the system on |+i,+i,+i>   (S-dagger then H on each, then measure 0)
  read the ancilla in the X basis        (H then measure) — the FIRST-ORDER axis; reading Z
                                          returns zeros at every coupling (C5060 pointer-axis bug)

The post-selection keep fraction is 12.50% and the classical floor is 1/3 per pair, both
established by tools/h13_cell5_pigeonhole_resolution_precheck.py.
"""
import argparse
import math

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp

EPS_CZ_MEDIAN = 0.0072      # device median 2q error (Cell 6 lineage)
P1_BAR = 0.95               # the same premise-gate bar Cell 6 was held to


def build(eps, n_sys=3):
    """Weak-value pigeonhole circuit, qubit 3 = ancilla pointer."""
    # Pi_same (x) Y  =  (I + Z0 Z1)/2 (x) Y  =  0.5 * (I I I Y) + 0.5 * (Z Z I Y)
    # Qiskit Pauli strings are little-endian: rightmost char = qubit 0.
    op = SparsePauliOp.from_list([("YIII", 0.5), ("YIZZ", 0.5)])
    qc = QuantumCircuit(4, 4)
    qc.h([0, 1, 2])                                   # |+++>
    qc.append(PauliEvolutionGate(op, time=eps), [0, 1, 2, 3])
    for q in (0, 1, 2):                               # post-select basis |+i> -> computational
        qc.sdg(q)
        qc.h(q)
    qc.h(3)                                           # ancilla X-basis read
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eps", type=float, default=0.1)
    a = ap.parse_args()
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    print("═" * 78)
    print(f"TRANSPILE PRICE — pigeonhole weak-value circuit, eps = {a.eps}")
    print("  swept across 3 optimisation levels x 5 seeds, because ONE transpile is a SAMPLE")
    print("═" * 78)

    qc = build(a.eps)
    # NB: the evolution is ONE 4-qubit instruction pre-synthesis, so a "count 2q gates as
    # written" line would read 0 and mean nothing. Report the DECOMPOSED count instead —
    # a baseline that says 0 is worse than no baseline (C5060).
    textbook = sum(1 for inst in qc.decompose(reps=3).data if inst.operation.num_qubits == 2)
    counts = []
    for lvl in (1, 2, 3):
        for seed in (11, 23, 37, 51, 79):
            t = transpile(qc, backend, optimization_level=lvl, seed_transpiler=seed)
            counts.append(sum(v for k, v in t.count_ops().items()
                              if k in ("cz", "cx", "ecr", "rzz")))
    lo, hi, med = min(counts), max(counts), int(np.median(counts))
    p1_lo = (1 - EPS_CZ_MEDIAN) ** hi        # worst case = most gates
    p1_hi = (1 - EPS_CZ_MEDIAN) ** lo

    print(f"  decomposed 2q (pre-routing)    : {textbook}")
    print(f"  TRANSPILED 2q  min/med/max     : {lo} / {med} / {hi}   observed {sorted(set(counts))}")
    print(f"  seed spread                    : {hi - lo} gates")
    print(f"  P1 = (1-{EPS_CZ_MEDIAN})^n     : {p1_hi:.4f} (best) .. {p1_lo:.4f} (worst)")
    print()

    # THE CELL 6 TEST, APPLIED TO OURSELVES: does the verdict flip across the sweep?
    if p1_lo >= P1_BAR:
        print(f"  ✅ CLEARS {P1_BAR} AT EVERY TRANSPILE IN THE SWEEP (worst case {p1_lo:.4f}).")
        print("     Not a seed-dependent pass — the property Cell 6 could not achieve.")
        verdict = 0
    elif p1_hi >= P1_BAR > p1_lo:
        print(f"  🔴 SEED-DEPENDENT: passes at {lo} gates ({p1_hi:.4f}), FAILS at {hi} ({p1_lo:.4f}).")
        print("     THIS IS EXACTLY WHY CELL 6 WAS RETIRED. Do not fly on the best transpile.")
        verdict = 1
    else:
        print(f"  🔴 FAILS AT EVERY TRANSPILE (best case {p1_hi:.4f} < {P1_BAR}).")
        verdict = 1

    print("\n  NOTE ON WHAT P1 MEANS HERE, because Cell 6's bar does not transfer unexamined:")
    print("  Cell 6's 0.95 gated a PREMISE (the bomb must be a faithful detector). This cell's")
    print("  headline is a NULL measured against a classical floor of 1/3, so circuit fidelity")
    print("  enters as a BIAS on the pointer, not as a premise that is either true or false.")
    print("  The number to beat is the 0.0200 error bar from the resolution pre-check, and a")
    print("  fidelity-induced pointer bias must sit well under it. THAT is the real gate, and")
    print("  it needs a full-noise sim — priced from THESE counts, not from the circuit as written.")

    # ── THE REAL GATE: does noise-induced pointer bias stay under the 0.0200 error bar? ──
    from qiskit_aer import AerSimulator
    sim = AerSimulator.from_backend(backend)
    print("\n" + "═" * 78)
    print("FULL-NOISE SIM — the gate that actually decides this cell")
    print("  pigeonhole arm must read ~0; the question is how far NOISE pushes it")
    print("═" * 78)
    RESOLUTION = 0.0200        # from the resolution pre-check, 20k shots at 12.50% keep
    shots = 200000
    tq = transpile(qc, sim, optimization_level=1, seed_transpiler=11)
    res = sim.run(tq, shots=shots, seed_simulator=7).result().get_counts()
    k0 = sum(v for b, v in res.items() if b.replace(" ", "")[-3:] == "000" and b.replace(" ", "")[-4] == "0")
    k1 = sum(v for b, v in res.items() if b.replace(" ", "")[-3:] == "000" and b.replace(" ", "")[-4] == "1")
    keep = (k0 + k1) / shots
    x = (k0 - k1) / (k0 + k1) if (k0 + k1) else float("nan")
    se = math.sqrt(max(1e-12, 1 - x * x) / max(k0 + k1, 1))
    print(f"  kept {k0+k1} of {shots}  (keep {keep*100:.2f}%, ideal 12.50%)")
    print(f"  <X_anc> under device noise = {x:+.5f} +- {se:.5f}   (ideal exactly 0)")
    print(f"  noise-induced bias |{x:+.5f}| vs the {RESOLUTION} resolution bar")
    if abs(x) < RESOLUTION:
        print(f"  ✅ BIAS IS UNDER THE BAR. The null survives device noise with room: "
              f"{RESOLUTION/max(abs(x),1e-9):.1f}x margin, and it is {1/3/max(abs(x),1e-9):.0f}x "
              f"below the 1/3 classical floor.")
    else:
        print(f"  🔴 BIAS EXCEEDS THE BAR — device noise alone moves the pointer further than the "
              f"measurement can resolve. The null is not readable as designed.")
        verdict = 1
    return verdict


if __name__ == "__main__":
    raise SystemExit(main())
