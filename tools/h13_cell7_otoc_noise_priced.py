#!/usr/bin/env python3
"""
H13 Cell 7 — OTOC light-cone instrument: noiseless reference + FULL-NOISE, TRANSPILE-PRICED sim.

WHY THIS FILE EXISTS AT ALL (C5060, and it is the second reason it is being written):
  1. Board #79's outstanding gate: the sim gate was met on a NOISELESS statevector. The OTOC
     needs U-dagger and roughly doubles depth, so hardware feasibility was explicitly NOT
     established. Pricing from a TEXTBOOK decomposition instead of the TRANSPILED circuit is the
     exact defect that produced the Cell 6 NO-TEST (3/6 modelled against 21 flown) and later
     retired Cell 6 entirely. Cell 7 had not paid it.
  2. THE SCRIPT THAT MET THE SIM GATE WAS NEVER COMMITTED. It ran in a scratchpad, produced the
     monotone front, v=1.000, and the whole control table now quoted in
     docs/h13-cell7-otoc-redesign-whisper-c5060.md — and then it was gone. A GATE RECORDED AS MET
     WITH UNREPRODUCIBLE EVIDENCE IS A CLAIM, NOT A GATE. Everything the doc asserts is
     recomputed here from source so the row's verdict rests on something a reader can run.

INSTRUMENT
  C(r,d) = 1 - Re<psi0| V0^dag W_r(d)^dag V0 W_r(d) |psi0>,  W_r(d) = U(d)^dag X_r U(d), V0 = Z_0
  on an N-site Ry(theta) + CZ brickwork. The light cone is where the commutator becomes NONZERO
  AT ALL, not where it is large — so the front estimator is nonzero-DETECTION, never a fixed
  amplitude threshold (a fixed threshold must eventually fall below a geometrically decaying
  leading edge, which is what made attempt 2's front non-monotone).

USAGE
  python3 tools/h13_cell7_otoc_noise_priced.py            # full run (noiseless + control + noise)
  python3 tools/h13_cell7_otoc_noise_priced.py --quick    # smaller depths, for a smoke test
"""
import argparse
import json
import math
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

# Frozen instrument constants ------------------------------------------------------------------
N_SITES = 9            # chain length for the noiseless reference
SOURCE = 0             # V0 acts here
BOUND_SITES_PER_LAYER = 2.0     # circuit causal bound for this brickwork
NONZERO_EPS = 1e-9     # "nonzero at all" — detection, not amplitude
EPS_CZ_MEDIAN = 0.0072  # device median 2q error used for the P1-style price (Cell 6 lineage)


def brickwork(n, depth, theta):
    """Ry(theta) on every site each layer, then CZ on alternating bonds. Causal structure
    advances exactly one site per layer, which is WHY the control below is mandatory."""
    qc = QuantumCircuit(n)
    for d in range(depth):
        for q in range(n):
            qc.ry(theta, q)
        for q in range(d % 2, n - 1, 2):
            qc.cz(q, q + 1)
    return qc


def otoc_column(n, depth, theta, site_r):
    """1 - Re<psi0| V0^dag W_r^dag V0 W_r |psi0> by direct statevector algebra (noiseless)."""
    U = brickwork(n, depth, theta)
    Ud = U.inverse()

    psi0 = Statevector.from_label("0" * n)

    # W_r = U^dag X_r U  applied to |psi0>, then V0, then W_r again, then V0 — assembled as the
    # standard OTOC overlap <psi0| V0 W_r V0 W_r |psi0> with Hermitian V0, W_r.
    def apply_W(state):
        qc = QuantumCircuit(n)
        qc.compose(U, inplace=True)
        qc.x(site_r)
        qc.compose(Ud, inplace=True)
        return state.evolve(qc)

    def apply_V(state):
        qc = QuantumCircuit(n)
        qc.z(SOURCE)
        return state.evolve(qc)

    lhs = apply_W(apply_V(apply_W(psi0)))     # W V W |psi0>
    val = np.vdot(apply_V(psi0).data, lhs.data)   # <psi0| V W V W |psi0>
    return 1.0 - float(np.real(val))


def front_at_depth(n, depth, theta):
    """Largest site whose commutator is nonzero at all. Detection, not amplitude."""
    front = 0
    for r in range(n):
        if abs(otoc_column(n, depth, theta, r)) > NONZERO_EPS:
            front = max(front, r)
    return front


def velocity(fronts, depths):
    """Least-squares slope through the origin-anchored front/depth points, with a CI."""
    d = np.array(depths, dtype=float)
    f = np.array(fronts, dtype=float)
    slope = float(np.sum(d * f) / np.sum(d * d))
    resid = f - slope * d
    dof = max(1, len(d) - 1)
    se = float(math.sqrt(np.sum(resid ** 2) / dof / np.sum(d * d)))
    return slope, (slope - 1.96 * se, slope + 1.96 * se)


# ---------------------------------------------------------------------------- noiseless + control
def run_noiseless(depths, theta, n=N_SITES, label=""):
    fronts = [front_at_depth(n, d, theta) for d in depths]
    v, ci = velocity(fronts, depths)
    monotone = all(b >= a for a, b in zip(fronts, fronts[1:]))
    inside = v <= BOUND_SITES_PER_LAYER + 1e-12
    print(f"  {label:14} fronts={fronts}  v={v:.3f}  CI=[{ci[0]:.3f},{ci[1]:.3f}]"
          f"  monotone={'Y' if monotone else 'N'}  inside_bound={'Y' if inside else 'N'}")
    return {"label": label, "theta": theta, "fronts": fronts, "v": v, "ci": list(ci),
            "monotone": monotone, "inside_bound": inside}


# ------------------------------------------------------------------- the flight circuit (C5060)
def flight_circuit(n, depth, theta, site_r, with_measure=True):
    """THE OTOC REDUCES TO ONE Z-BASIS MEASUREMENT. |psi0> = |0..0> is a +1 eigenstate of
    V0 = Z_0, so V0|psi0> = |psi0> and

        F = <psi0| V W V W |psi0> = <psi0| W V W |psi0> = <chi| Z_0 |chi>,   |chi> = W|psi0>

    with W = U^dag X_r U. So the whole instrument is: apply U, X_r, U^dag, read Z on qubit 0.
    NO ancilla, NO interferometer, NO Hadamard test. Verified exact to 1e-9 against the direct
    statevector algebra across (d,r) in {2,3,4}x{2,3,4,5}.

    This matters for the flight, not just for elegance: the design doc assumed the OTOC needed
    an interferometric read on top of the doubled depth. It does not. My first attempt at a
    noisy read DID build an interferometer, and it was wrong — see run_noisy's docstring."""
    U = brickwork(n, depth, theta)
    qc = QuantumCircuit(n, 1) if with_measure else QuantumCircuit(n)
    qc.compose(U, inplace=True)
    qc.x(site_r)
    qc.compose(U.inverse(), inplace=True)
    if with_measure:
        qc.measure(SOURCE, 0)
    return qc


def transpile_price(n, depth, theta, site_r, seeds=(11, 23, 37, 51, 79), opt_levels=(1, 2, 3)):
    """Price the FLIGHT circuit from the COMPILED gate count on real heavy-hex connectivity,
    swept across transpiler seeds — because Cell 6 died on a premise gate that flipped between 7
    and 9 gates depending on the seed. A single transpile is a sample, not a cost.

    ⚠️ READ transpiled_2q == 0 AS PHYSICS, NOT AS A BROKEN TRANSPILE (C5060). Outside the light
    cone U^dag X_r U = X_r EXACTLY, so every CZ legitimately cancels and the compiler returns a
    circuit with no two-qubit gates at all. Measured here: r=4 gives 0 / 0 / 0 / 28 / 38 / 54 / 66
    two-qubit gates at depths 1..7 — zero precisely while the site is outside the cone, and
    nonzero from d=4, which is exactly where the front reaches r=4. THE COMPILED GATE COUNT IS
    ITSELF A LIGHT-CONE DETECTOR. It also means a noisy 'measurement' at d<4 is a measurement of
    an EMPTY CIRCUIT, which is how this script's first draft reported z=403 'readable' from
    nothing."""
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    qc = flight_circuit(n, depth, theta, site_r)
    counts = []
    for lvl in opt_levels:
        for s in seeds:
            t = transpile(qc, backend, optimization_level=lvl, seed_transpiler=s)
            ops = t.count_ops()
            counts.append(sum(v for k, v in ops.items() if k in ("cz", "cx", "ecr", "rzz")))
    textbook = 2 * sum(1 for d in range(depth) for _ in range(d % 2, n - 1, 2))
    return {"depth": depth, "site_r": site_r,
            "transpiled_2q": {"min": min(counts), "median": int(np.median(counts)),
                              "max": max(counts), "all": sorted(set(counts))},
            "textbook_2q": textbook,
            "seed_spread": max(counts) - min(counts),
            "P1_at_min": (1 - EPS_CZ_MEDIAN) ** min(counts),
            "P1_at_max": (1 - EPS_CZ_MEDIAN) ** max(counts),
            "P1_textbook": (1 - EPS_CZ_MEDIAN) ** textbook}


# ---------------------------------------------------------------------------- full-noise sim
def run_noisy(n, depths, theta, site_r, shots=8000, ideal=None):
    """Full device noise model from FakeMarrakesh, sampled, on the FLIGHT circuit.

    WHAT THE FIRST DRAFT OF THIS FUNCTION DID WRONG, kept because the failure is the lesson: it
    wrapped the sequence in H...H on the source qubit as an 'interferometric read' — which is not
    an OTOC interferometer (that needs an ancilla controlling the operator order) — and then
    reported p1=0.9881 at depths 1, 2 AND 3, identical to four decimals, with z=403 'readable'.
    Three different depths cannot give one answer. They compiled to the SAME EMPTY CIRCUIT,
    because at those depths the probed site is outside the cone. A STRONG READABLE SIGNAL WAS
    REPORTED FROM A CIRCUIT CONTAINING NOTHING.

    Reports the noisy estimate NEXT TO the noiseless value, because a noisy number alone cannot
    say whether it is measuring the physics or the noise floor."""
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    sim = AerSimulator.from_backend(FakeMarrakesh())

    out = []
    for depth in depths:
        qc = flight_circuit(n, depth, theta, site_r)
        t = transpile(qc, sim, optimization_level=1, seed_transpiler=11)
        two_q = sum(v for k, v in t.count_ops().items() if k in ("cz", "cx", "ecr", "rzz"))
        res = sim.run(t, shots=shots, seed_simulator=7).result().get_counts()
        p1 = res.get("1", 0) / shots
        z0 = 1 - 2 * p1                      # <Z_0> from the measured bit
        c_noisy = 1.0 - z0
        se = 2 * math.sqrt(max(p1 * (1 - p1), 1e-12) / shots)
        c_ideal = ideal[depth] if ideal and depth in ideal else float("nan")
        out.append({"depth": depth, "two_q_compiled": two_q, "C_noisy": c_noisy, "se": se,
                    "C_ideal": c_ideal, "bias": c_noisy - c_ideal,
                    "empty_circuit": two_q == 0})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    depths = [1, 2, 3, 4] if a.quick else [1, 2, 3, 4, 5, 6, 7]
    report = {"depths": depths, "n_sites": N_SITES}

    print("═" * 78)
    print("PART 1 — NOISELESS REFERENCE (recomputing what the committed doc asserts)")
    print("═" * 78)
    report["noiseless"] = run_noiseless(depths, math.pi / 4, label="theta=pi/4")

    print("\n" + "═" * 78)
    print("PART 2 — THE CONTROL: vary coupling at FIXED connectivity")
    print("        (a front that reads the wiring diagram cannot move here)")
    print("═" * 78)
    control = []
    for name, th in (("pi/4", math.pi / 4), ("pi/8", math.pi / 8), ("pi/32", math.pi / 32),
                     ("pi/256", math.pi / 256), ("identity", 0.0)):
        control.append(run_noiseless(depths[:6], th, label=name))
    report["control"] = control

    print("\n" + "═" * 78)
    print("PART 3 — THE TRANSPILE PRICE (the gate Cell 7 had not paid)")
    print("         Priced PER DEPTH, because a zero count is the cone, not a cheap circuit.")
    print("═" * 78)
    SITE_R, TH_FLY = 4, math.pi / 32
    prices = []
    print("  depth | textbook | transpiled 2q (min/med/max) | seed spread | P1@max | note")
    for d in depths:
        p = transpile_price(N_SITES, d, TH_FLY, site_r=SITE_R)
        prices.append(p)
        tp = p["transpiled_2q"]
        note = "OUTSIDE CONE — empty circuit" if tp["max"] == 0 else ""
        print(f"   {d:2d}   |   {p['textbook_2q']:3d}    |    {tp['min']:3d} / {tp['median']:3d}"
              f" / {tp['max']:3d}            |     {p['seed_spread']:2d}      |"
              f" {p['P1_at_max']:.4f} | {note}")
    report["price_by_depth"] = prices

    print("\n" + "═" * 78)
    print("PART 4 — FULL-NOISE SIM at theta=pi/32 on the FLIGHT circuit")
    print("         (one Z-basis read; noisy value shown BESIDE the noiseless truth)")
    print("═" * 78)
    ideal = {d: otoc_column(N_SITES, d, TH_FLY, SITE_R) for d in depths}
    noisy = run_noisy(N_SITES, depths, TH_FLY, site_r=SITE_R, ideal=ideal)
    report["noisy"] = noisy
    print("  depth | 2q | C_ideal    | C_noisy    | bias      | verdict")
    for row in noisy:
        if row["empty_circuit"]:
            verdict = "EMPTY CIRCUIT — measures nothing"
        elif abs(row["bias"]) > 3 * row["se"] and abs(row["bias"]) > 0.5 * max(abs(row["C_ideal"]), 1e-9):
            verdict = "NOISE DOMINATES"
        else:
            verdict = "signal survives"
        print(f"   {row['depth']:2d}   | {row['two_q_compiled']:2d} | {row['C_ideal']:+.6f}  |"
              f" {row['C_noisy']:+.6f}  | {row['bias']:+.5f}  | {verdict}")

    with open("results/h13_cell7_noise_priced_c5060.json", "w") as fh:
        json.dump(report, fh, indent=1)
    print("\nwrote results/h13_cell7_noise_priced_c5060.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
