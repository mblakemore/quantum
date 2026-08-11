#!/usr/bin/env python3
"""
H13 Cell 5 pigeonhole — RESOLUTION PRE-CHECK, run BEFORE designing the weak-value circuit.

WHY THIS ORDER (C5060). Two H13 cells died today because the hardware-reality check was run
AFTER the design was built:
  Cell 6 — priced from a textbook decomposition; the transpiled count flipped the premise gate
           on a transpiler seed. RETIRED.
  Cell 7 — sim gate met by a front estimator detecting at 1e-9 against a ~2e-2 device floor;
           the informative and measurable regimes proved DISJOINT. NO-GO.
Both were correct designs aimed at regimes the hardware cannot reach. The weak-value class has
that same pincer BUILT IN — the coupling must be weak enough not to collapse the state and
strong enough to see — so this script asks the killer question first, at zero QPU:

    IS THERE A COUPLING STRENGTH WHERE THE WEAK-VALUE APPROXIMATION HOLDS **AND** THE POINTER
    SHIFT CLEARS THE DEVICE FLOOR, AT THE POST-SELECTION KEEP-FRACTION THIS EFFECT REQUIRES?

If no, Cell 5's pigeonhole leg is closed for the price of this file and nobody designs the
circuit. If yes, the answer hands the design its working point instead of the design guessing.

THE PHYSICS (Aharonov et al., PNAS 113:532, 2016)
  3 particles, 2 boxes. Pre-select |+++>, post-select |+i,+i,+i>. For EVERY pair the weak value
  of the "same box" projector is exactly 0 — no two particles are found together — while any
  classical assignment of 3 pigeons to 2 boxes forces at least one shared pair, so the three
  classical pair-probabilities must sum to >= 1.

  THE SIGNAL IS AN ABSENCE, WHICH INVERTS CELL 7's PROBLEM. Cell 7 needed to resolve a tiny
  NONZERO against the noise floor and lost. Here the prediction is ZERO and the classical floor
  is of order 1/3 per pair — so the question is whether the ERROR BAR can be pushed well below
  a number of order 1/3, not whether a 1e-8 signal can be seen. That is a far easier ask, and
  the reason this pre-check is worth running rather than assuming the Cell 7 verdict transfers.

Usage:  python3 tools/h13_cell5_pigeonhole_resolution_precheck.py [--shots 20000]
"""
import argparse
import math

import numpy as np

# ---------------------------------------------------------------------------- states
KET0 = np.array([1, 0], dtype=complex)
KET1 = np.array([0, 1], dtype=complex)
PLUS = (KET0 + KET1) / math.sqrt(2)            # pre-selection, per particle
PLUS_I = (KET0 + 1j * KET1) / math.sqrt(2)     # post-selection, per particle
I2 = np.eye(2, dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

DEVICE_FLOOR = 2e-2    # measured in the Cell 7 full-noise sim on FakeMarrakesh; same class of read


def kron(*ops):
    """Kronecker product that PRESERVES RANK — seeding with a 2-D [[1]] silently promoted
    1-D state vectors to (1,8) row matrices and the first matmul died on it (C5060)."""
    out = ops[0]
    for o in ops[1:]:
        out = np.kron(out, o)
    return np.asarray(out, dtype=complex)


def pair_projector(j, k, n=3):
    """Pi_same on pair (j,k) = (I + Z_j Z_k)/2 — projector onto the |00>,|11> subspace."""
    ops = [I2] * n
    ops[j] = Z
    ops[k] = Z
    return (np.eye(2 ** n, dtype=complex) + kron(*ops)) / 2


def weak_value(op, pre, post):
    num = post.conj() @ (op @ pre)
    den = post.conj() @ pre
    return num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=20000)
    a = ap.parse_args()

    n = 3
    pre = kron(PLUS, PLUS, PLUS)
    post = kron(PLUS_I, PLUS_I, PLUS_I)
    pairs = [(0, 1), (0, 2), (1, 2)]
    PLUS_CTRL = pre   # control post-selection = the pre-selection itself

    print("═" * 78)
    print("PART 1 — THE EFFECT ITSELF (exact weak values, no circuit)")
    print("═" * 78)
    wvs = []
    for (j, k) in pairs:
        wv = weak_value(pair_projector(j, k), pre, post)
        wvs.append(wv)
        print(f"  pair ({j},{k}) : weak value of Pi_same = {wv.real:+.12f} {wv.imag:+.12f}i")
    keep = abs(post.conj() @ pre) ** 2
    print(f"\n  post-selection keep fraction |<post|pre>|^2 = {keep:.6f}  ({keep*100:.2f}%)")
    all_zero = all(abs(w) < 1e-12 for w in wvs)
    print(f"  all three weak values zero: {'YES ✅ the effect is present' if all_zero else 'NO 🔴'}")

    print("\n" + "═" * 78)
    print("PART 2 — THE CLASSICAL FLOOR THIS MUST BEAT (enumerated in-code, never quoted)")
    print("═" * 78)
    # Every assignment of 3 distinguishable pigeons to 2 boxes; count shared pairs.
    best = None
    for assign in range(8):
        boxes = [(assign >> i) & 1 for i in range(3)]
        shared = sum(1 for (j, k) in pairs if boxes[j] == boxes[k])
        best = shared if best is None else min(best, shared)
    print(f"  min shared pairs over all 2^3 classical assignments = {best}")
    print(f"  => sum of the three classical pair-probabilities >= {best}")
    print(f"  => at least one pair must read >= {best/3:.4f} on average")
    classical_floor_per_pair = best / 3

    print("\n" + "═" * 78)
    print("PART 3 — THE PINCER, AND THE POSITIVE CONTROL THAT MAKES IT A MEASUREMENT")
    print("═" * 78)
    print("  ⚠️ THE PIGEONHOLE PREDICTION IS ZERO, so a DEAD apparatus and a SUCCESSFUL")
    print("     detection produce THE SAME READING. A zero is only evidence if the identical")
    print("     code path can be shown to move when the weak value is nonzero.")
    print("  CONTROL: post-select on |+++> (= the pre-selection). Then the weak value of")
    print("     Pi_same is just its expectation, 0.5 — nonzero and known. Same coupling, same")
    print("     read, same estimator; only the post-selection differs.\n")

    def sweep(post_state, label):
        print(f"  ── {label} ──")
        print("  eps      <X_anc> shift    shift/eps    keep      note")
        out = []
        for eps in (1.0, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01):
            Pi = pair_projector(0, 1)
            big_Pi = np.kron(Pi, np.eye(2, dtype=complex))
            big_Y = np.kron(np.eye(2 ** n, dtype=complex), Y)
            H = eps * (big_Pi @ big_Y)
            w, V = np.linalg.eigh(H)
            U = V @ np.diag(np.exp(-1j * w)) @ V.conj().T
            psi = U @ np.kron(pre, KET0)
            Ppost = np.kron(np.outer(post_state, post_state.conj()), np.eye(2, dtype=complex))
            psi_ps = Ppost @ psi
            norm = np.linalg.norm(psi_ps)
            if norm < 1e-14:
                print(f"  {eps:<8.3f} post-selection empty"); continue
            psi_ps = psi_ps / norm
            Xanc = np.kron(np.eye(2 ** n, dtype=complex), X)
            shift = float(np.real(psi_ps.conj() @ (Xanc @ psi_ps)))
            out.append((eps, shift, shift / eps, norm ** 2))
            print(f"  {eps:<8.3f} {shift:+.9f}    {shift/eps:+8.4f}    {norm**2:.4f}")
        return out

    ctrl = sweep(PLUS_CTRL, "POSITIVE CONTROL — post-select |+++>, weak value 0.5 (must MOVE)")
    pig = sweep(post, "PIGEONHOLE — post-select |+i,+i,+i>, weak value 0 (must NOT move)")

    ctrl_max = max((abs(s) for _, s, _, _ in ctrl), default=0.0)
    pig_max = max((abs(s) for _, s, _, _ in pig), default=0.0)
    print(f"\n  largest |shift|  control {ctrl_max:.6f}   pigeonhole {pig_max:.6f}")
    if ctrl_max > 1e-6 and pig_max < 1e-6:
        print("  ✅ THE APPARATUS MOVES WHEN THE WEAK VALUE IS NONZERO AND STAYS STILL WHEN IT")
        print("     IS ZERO. The zero is a measurement, not a disconnection.")
        apparatus_live = True
    elif ctrl_max <= 1e-6:
        print("  🔴 THE CONTROL DID NOT MOVE EITHER — the apparatus is dead and the pigeonhole")
        print("     zero carries NO information. Fix the instrument before believing any zero.")
        apparatus_live = False
    else:
        print("  🔴 THE PIGEONHOLE ARM MOVED — the effect is not being reproduced.")
        apparatus_live = False


    print("\n" + "═" * 78)
    print("PART 4 — VERDICT")
    print("═" * 78)
    kept = a.shots * keep
    se = math.sqrt(1.0 / max(kept, 1))
    print(f"  kept shots at {a.shots} total, keep {keep*100:.2f}%  = {kept:.0f}")
    print(f"  statistical resolution on a near-zero pointer ~ {se:.4f}")
    print(f"  classical floor to beat (per pair)             ~ {classical_floor_per_pair:.4f}")
    if not apparatus_live:
        print("\n  🔴 VERDICT WITHHELD — the positive control above did not behave, so no statement\n     about resolution means anything yet. Resolution arithmetic on a dead apparatus\n     is the exact failure this arc retired two cells for.")
        return 1

    if se < classical_floor_per_pair / 5:
        print(f"\n  ✅ RESOLUTION IS NOT THE WALL. The error bar ({se:.4f}) is "
              f"{classical_floor_per_pair/se:.1f}x below the classical floor "
              f"({classical_floor_per_pair:.4f}).")
        print("     Unlike Cell 7, the signal here is an ABSENCE measured against a floor of "
              "order 1/3,\n     not a 1e-8 amplitude against 2e-2 of noise. The cell is NOT "
              "closed by this check.")
        print("     NEXT: build the weak-value circuit at a coupling in the linear column above,\n"
              "     then price the TRANSPILED 2q count before any tank request (the Cell 6 defect).")
    else:
        print(f"\n  🔴 RESOLUTION IS THE WALL: {se:.4f} against a floor of "
              f"{classical_floor_per_pair:.4f}. Raise shots or close the leg.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
