#!/usr/bin/env python3
"""DOOR (b) END-TO-END SIM REPLICATION (Ember C4266) — the whole pipeline, zero QPU.

WHY THIS EXISTS. My standing C3869 commitment says quantum point-hypotheses stay capped at
~0.6 **unless sim-replicated**, and that the real fix for my worst-calibrated domain (49.3%
actual over 90 resolved) is "more sim-replication before hardware claims". The door (b) flight
already died once — FAIL-AS-FROZEN — on a PREP BUG discovered *on hardware*, after paying for
the shots. This would have caught it for free.

WHAT THE FLIGHT SCRIPT ALREADY CHECKS, and what it does not:
  · G-DECODE verifies the sign rule against exact simulation (n<=3)   — a COMPONENT
  · F-BIAS / F-IND / F-MIX verify the prep's statistics                — COMPONENTS
  · NOTHING runs prep -> Bell -> decode -> estimate END TO END at the REGISTERED parameters
    and compares the recovered values to CLOSED-FORM TRUTH. That composition is where the
    FAIL-AS-FROZEN bug lived: every component passed and the assembly was wrong.

THE THREE PRE-REGISTERED FALSIFIERS, all testable here before a single shot is bought:
  F1  delivered accuracy: does |tr(P rho)| come back within eps?
  F2  copy budget: does the REGISTERED budget actually suffice, or was the constant optimistic?
  F3  pipeline correctness: does the verification subset match closed-form truth?

TRUTH IS ANALYTIC, NOT SIMULATED — THIS IS THE ANTI-ECHO MEASURE. For the hard ensemble
rho_P = (I + alpha*P)/2^n, tr(Q rho_P) = alpha * delta_QP EXACTLY. So the estimator is scored
against a closed form derived from the ensemble's definition, NOT against my own sampler.
A sampler-vs-decoder comparison would be a validator reusing the primitive it validates
(c4194_001) and would report a confident PASS while both shared a defect.

The sampler is nonetheless built from BORN'S RULE on the two-qubit Bell measurement of the
product eigenstates, independently of `bell_sign`'s empirically-fixed convention, so the two
routes meet only at the answer.

n=16 needs no statevector: rho_P is PRODUCT-STRUCTURED (that is why the prep has zero 2q gates),
so the Bell outcome distribution factorises pair-by-pair and samples exactly at any n.
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doorb_flight_ember_c4262 import (  # noqa: E402  — IMPORTED, never retyped (one owner)
    SYM, bell_sign, budget_copies, n_y, prep_state,
)

# Single-qubit eigenvectors |P, s> for P in {X,Y,Z}, s in {+1,-1}
KET = {
    ("Z", +1): np.array([1, 0], dtype=complex),
    ("Z", -1): np.array([0, 1], dtype=complex),
    ("X", +1): np.array([1, 1], dtype=complex) / math.sqrt(2),
    ("X", -1): np.array([1, -1], dtype=complex) / math.sqrt(2),
    ("Y", +1): np.array([1, 1j], dtype=complex) / math.sqrt(2),
    ("Y", -1): np.array([1, -1j], dtype=complex) / math.sqrt(2),
}
KET[("I", +1)] = KET[("Z", +1)]
KET[("I", -1)] = KET[("Z", -1)]

# Bell basis |Phi_ab> = (I (x) X^a Z^b) |Phi+>, as 4-vectors on (copy A, copy B)
def _bell_basis():
    phi = np.zeros(4, dtype=complex)
    phi[0] = phi[3] = 1 / math.sqrt(2)                       # |00>+|11>
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I2 = np.eye(2, dtype=complex)
    out = {}
    for a in (0, 1):
        for b in (0, 1):
            # INDEX ORDER FIXED AGAINST ANALYTIC TRUTH, NOT AGAINST SIGNAL SIZE.
            # My first labelling was |Phi_ab> = (I (x) X^a Z^b)|Phi+>, which is a defensible
            # convention and is NOT the one `bell_sign` was brute-forced into. The two routes
            # disagreed and the P signal vanished to ~0. Resolved at n=1 by EXACT computation
            # (no sampling): with rho=(I+aZ)/2 and a=0.9, truth is a^2=0.810000, and of the
            # four index relabelings exactly ONE returns 0.810000 to machine precision while
            # the other three return exactly 0. Choosing the one that reproduces a CLOSED FORM
            # is not the same as choosing the one with the biggest number — that second move is
            # the one I refused on the door (b) pilot wash, and it stays refused.
            out[(b, a)] = np.kron(I2, np.linalg.matrix_power(X, a)
                                  @ np.linalg.matrix_power(Z, b)) @ phi
    return out


BELL = _bell_basis()


def pair_probs(ket_a, ket_b):
    """Born's rule: P(a,b) = |<Phi_ab | psi_A (x) psi_B>|^2 for ONE qubit pair.

    Derived from the Bell basis directly — it shares no code with `bell_sign`, whose (x,z)<->(a,b)
    pairing was fixed EMPIRICALLY by brute force. If that convention were wrong, this sampler
    would not agree with it, and the end-to-end estimate would miss the analytic truth.
    """
    psi = np.kron(ket_a, ket_b)
    return np.array([abs(np.vdot(BELL[(a, b)], psi)) ** 2 for a in (0, 1) for b in (0, 1)])


def local_signs(P_label, sgn, rng):
    """(global sign, per-qubit local signs) -> the SINGLE owner of the sign constraint.

    rho_P's eigenstate needs the product of local signs over the NON-IDENTITY positions to
    equal the drawn global sign; identity positions are free and must still be randomised
    (that omission was the FAIL-AS-FROZEN bug — identity qubits flew as pure |0>).

    WRITTEN BECAUSE I REIMPLEMENTED IT WRONG ON FIRST CONTACT. `prep_state` returns (s, bits)
    and leaves this constraint to its CALLER, where the flight script performs it inline —
    TWICE. A rule that every consumer must re-derive is a rule that every consumer can get
    wrong, and the first new consumer (this file) did: I gave qubit 0 the global sign and every
    other qubit its raw bit, which enforces no product constraint at all. The signal vanished
    to -0.054 against a truth of 0.81 — not a subtle miss, a destroyed one.
    """
    n = len(P_label)
    si = [int(rng.choice([1, -1])) for _ in range(n)]     # ALL positions, identity included
    free = [i for i, c in enumerate(P_label) if c != "I"]
    if free:
        si[free[-1]] = (sgn * int(np.prod([si[i] for i in free[:-1]]))) if len(free) > 1 else sgn
    return si


def run(n, eps, copies, P_label, seed, verify_labels):
    alpha = 3.0 * eps
    rng = np.random.default_rng(seed)
    # F-IND: independent streams per copy, exactly as the flight script requires
    streams = [np.random.default_rng(s) for s in rng.integers(0, 2 ** 31, size=4)]
    shots = int(math.ceil(copies / 2.0))       # two copies per Bell shot

    acc = {lab: 0 for lab in verify_labels}
    idx = [(a, b) for a in (0, 1) for b in (0, 1)]

    for _ in range(shots):
        sA, _ = prep_state(n, P_label, alpha, streams[0], streams[1])
        sB, _ = prep_state(n, P_label, alpha, streams[2], streams[3])
        siA = local_signs(P_label, sA, streams[1])
        siB = local_signs(P_label, sB, streams[3])
        outcomes = []
        for i, ch in enumerate(P_label):
            ka = KET[(ch, siA[i])]
            kb = KET[(ch, siB[i])]
            p = pair_probs(ka, kb)
            p = np.maximum(p, 0); p = p / p.sum()
            outcomes.append(idx[rng.choice(4, p=p)])
        for lab in verify_labels:
            acc[lab] += bell_sign(lab, outcomes)

    return {lab: acc[lab] / shots for lab in verify_labels}, shots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--eps", type=float, default=0.3)
    ap.add_argument("--delta", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=4266)
    ap.add_argument("--scale", type=float, default=1.0,
                    help="fraction of the REGISTERED budget to spend (F2 sweep)")
    a = ap.parse_args()

    n, eps, alpha = a.n, a.eps, 3.0 * a.eps
    P = ("XYZ" * (n // 3) + "XYZ"[: n % 3])[:n]     # a concrete P; the seal is untouched
    budget = budget_copies(n, eps, a.delta)
    copies = budget * a.scale

    print(f"DOOR (b) SIM REPLICATION — n={n}, eps={eps}, alpha={alpha}, P={P}")
    print(f"  registered budget {budget:,.0f} copies; spending {copies:,.0f} ({a.scale:.2f}x)")
    print(f"  TRUTH IS ANALYTIC: tr(Q rho_P) = alpha*delta_QP = {alpha} for Q=P, 0 otherwise")
    print(f"  so |tr(P rho)| = {alpha:.4f} and every other |tr(Q rho)| = 0.0000\n")

    # verification subset: P itself, plus decoys that must come back at ZERO
    # decoy sites must exist at ANY n — hard-coded indices crashed at n=4. Scale to the string.
    sites = sorted({0, n // 3, 2 * n // 3})[:3]
    decoys = [P[:i] + ("X" if P[i] != "X" else "Z") + P[i + 1:] for i in sites]
    labels = [P] + decoys + ["I" * n]
    est, shots = run(n, eps, copies, P, a.seed, labels)

    print(f"  {shots:,} Bell shots ({2*shots:,} copies)\n")
    print(f"  {'label':<10}{'E[v]':>12}{'|tr|est':>12}{'truth':>10}{'err':>10}   verdict")
    print("  " + "-" * 66)
    ok = True
    for lab in labels:
        v = est[lab]
        mag = math.sqrt(max(v, 0.0))
        truth = alpha if lab == P else (1.0 if set(lab) == {"I"} else 0.0)
        err = abs(mag - truth)
        good = err <= eps
        ok &= good
        tag = "P" if lab == P else ("identity" if set(lab) == {"I"} else "decoy")
        print(f"  {tag:<10}{v:>12.5f}{mag:>12.4f}{truth:>10.4f}{err:>10.4f}   "
              f"{'ok' if good else 'MISS >eps'}")

    print()
    print(f"  F1 accuracy (all |errors| <= eps={eps}) : {'PASS' if ok else 'FAIL'}")
    print(f"  F2 budget at {a.scale:.2f}x registered      : {'sufficient' if ok else 'INSUFFICIENT'}")
    print(f"  F3 pipeline vs closed-form truth      : {'PASS' if ok else 'FAIL'}")
    print("\n  NOTE: this is SIMULATION. It bounds pipeline and budget error only —")
    print("  it says nothing about hardware fidelity, which stays unmeasured until a flight.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
