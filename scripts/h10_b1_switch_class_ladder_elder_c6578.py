#!/usr/bin/env python3
"""
h10_b1_switch_class_ladder_elder_c6578.py — Elder's pre-seal co-check of the B1 switch exhibit row.

CONFIRMS Whisper's 15/21 = 0.714286 by an independent route (SDP/Helstrom POVM over explicitly
constructed switch output states, vs their analytic construction).

AND PRODUCES THE THING THAT MATTERS MORE — the STRATEGY-CLASS LADDER. My first attempt read
11/21 because I had restricted the class without noticing; widening it twice climbed to their
number. That progression is not my bookkeeping, it is a diagnostic table:

    11/21 = 0.5238   control-only readout, target traced      (readout collapsed)
    14/21 = 0.6667   joint (control,target) POVM, PRODUCT in  (half-Bell prep failed)
    15/21 = 0.7143   half-Bell target + 3-qubit Helstrom      (correct, as specified)

Each rung is a REALISTIC single-fault version of the flown circuit. So the ladder says what a
mis-compiled switch arm would actually MEASURE — and that is exactly what an apparatus-health
gate has to be able to separate.

THE FINDING: G4b's registered band [0.63, 0.78] contains BOTH 0.7143 (correct) and 0.6667
(half-Bell prep failed). A single failed entangling gate on the target preparation lands inside
the band and PASSES. G3 (parallel > switch) also still passes, because a degraded switch is
even further below parallel. So that fault would be recorded as a healthy switch arm and the
registered exhibit row would be wrong by 1/21 with no gate firing.

At ~500 shots/pair the 1/21 gap is ~11 sigma — the band is loose by choice, not by necessity.
"""
import sys
import numpy as np
import cvxpy as cp

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from h10_b1_ceiling_sdp_elder_c6578 import full_pairs

I2 = np.eye(2)


def switch_out(U, V, psi, anc):
    """(control x target [x ref]) state after the switch on a target that may be entangled."""
    d = 2 if not anc else 4
    A = np.kron(V @ U, I2) if anc else V @ U
    B = np.kron(U @ V, I2) if anc else U @ V
    v = (np.kron(np.array([1, 0]), A @ psi) + np.kron(np.array([0, 1]), B @ psi)) / np.sqrt(2)
    return np.outer(v, v.conj()), 2 * d


def helstrom(pairs, psi, anc):
    rho = [(switch_out(U, V, psi, anc)[0], l) for _, U, V, l in pairs]
    dim = switch_out(*pairs[0][1:3], psi, anc)[1]
    E = cp.Variable((dim, dim), hermitian=True)
    obj = sum(cp.real(cp.trace((E if l == "M+" else np.eye(dim) - E) @ r)) for r, l in rho)
    pr = cp.Problem(cp.Maximize(obj / len(rho)), [E >> 0, np.eye(dim) - E >> 0])
    pr.solve(solver="SCS", verbose=False)
    return pr.value


def main():
    pairs, mism, nonu = full_pairs()
    assert not mism and not nonu, "pair inputs did not verify"
    rng = np.random.default_rng(11)

    prod = [np.array([1, 0], complex), np.array([1, 1], complex) / np.sqrt(2)]
    prod += [(lambda v: v / np.linalg.norm(v))(rng.normal(size=2) + 1j * rng.normal(size=2))
             for _ in range(60)]
    ent = [np.array([1, 0, 0, 1], complex) / np.sqrt(2), np.array([1, 0, 0, 0], complex)]
    ent += [(lambda v: v / np.linalg.norm(v))(rng.normal(size=4) + 1j * rng.normal(size=4))
            for _ in range(50)]

    v_prod = max(helstrom(pairs, p, False) for p in prod)
    v_ent = max(helstrom(pairs, p, True) for p in ent)

    print("STRATEGY-CLASS LADDER for the switch arm")
    print(f"  joint (C,T) POVM, product target : {v_prod:.6f} = {v_prod*21:.3f}/21")
    print(f"  half-Bell target + 3q Helstrom   : {v_ent:.6f} = {v_ent*21:.3f}/21"
          f"   {'CONFIRMS registered 15/21' if abs(v_ent - 15/21) < 1e-4 else '*** MISMATCH ***'}")

    lo, hi = 0.63, 0.78
    print(f"\nG4b band [{lo}, {hi}] against realistic single faults:")
    for v, lbl in ((15/21, "correct (half-Bell + 3q Helstrom)"),
                   (v_prod, "half-Bell prep FAILED -> product target"),
                   (11/21, "readout collapsed to control-only"),
                   (0.62, "dead apparatus")):
        print(f"  {v:.4f}  {lbl:42s} -> {'PASS' if lo <= v <= hi else 'FAIL'}")
    print("\n  => the half-Bell-prep fault PASSES G4b, and passes G3 too (a degraded switch is")
    print("     further below parallel). It would be recorded as a healthy switch arm.")
    n = 21 * 500
    sd = np.sqrt((15/21) * (1 - 15/21) / n)
    print(f"  => the 1/21 gap is {(15/21 - v_prod)/sd:.1f} sigma at ~500 shots/pair: separable by choice.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
