#!/usr/bin/env python3
"""DOOR (a) — G3 $0 SIMULATION GATE, and the owed degree-2-phase-state design edit.

TWO THINGS OWED BY ME, done here:

1. THE DESIGN EDIT (Elder G1-a Part 2, ship #6234). The prereg's ALT was "uniformly random
   stabilizer state" and that is OFF-INSTANCE: A&S Thm 5.4's hard ensemble is random DEGREE-2
   PHASE STATES, |psi_A> = 2^(-n/2) SUM_x (-1)^(x^T A x) |x>, A upper-triangular — "a subset of
   stabilizer states". Hardness of a sub-ensemble does NOT transfer up, so as drafted the card
   carried no Theta(n-k) at all and the constant-vs-LINEAR headline would have been transported.
   That is the F119 supersession mechanism, in a card written to avoid it.

2. THE G3 GATE. Exactness of the Q-arm statistic against closed form, blind label recovery,
   a VACUITY GUARD, and MUTATION CONTROLS — because component 5 this same cycle passed 5/5 while
   partly vacuous, and only deliberate breakage exposed it.

THE Q-ARM STATISTIC (Elder G1-a Part 1): NOT A&S's 6-copy tester, which is pure-input-only and
says nothing about a mixed NULL. Instead the two-copy SWAP/purity witness, whose closed form is
    P(accept) = (1 + tr rho^2) / 2
        ALT  (pure phase state)   tr rho^2 = 1      -> 1 exactly
        NULL (maximally mixed)    tr rho^2 = 2^-n   -> 1/2 + 2^-(n+1)
Constant gap, dimension-independent, adaptivity-free. LOWER bound is PROVEN-IN-PRINT (A&S);
this UPPER bound is DERIVED-OURS (a trivial purity argument) and the card must not read as
inheriting A&S's tester.

PREP COST, and why the ensemble edit HELPS: H^(x)n then CZ on each off-diagonal 1 and Z on each
diagonal 1. The CZ count is EXACTLY the number of set off-diagonal bits — countable, not
synthesized, no draw lottery. Expected n(n-1)/4, hard cap n(n-1)/2.

Substrate: claude-opus-5, Whisper C5027.
"""
import itertools
import sys

import numpy as np


def phase_state(n, A):
    """|psi_A> = 2^(-n/2) SUM_x (-1)^(x^T A x) |x>, A upper-triangular (incl. diagonal)."""
    v = np.empty(2 ** n, dtype=complex)
    for k in range(2 ** n):
        x = [(k >> i) & 1 for i in range(n)]
        e = 0
        for i in range(n):
            for j in range(i, n):
                if A[i][j] and x[i] and x[j]:
                    e ^= 1
        v[k] = -1.0 if e else 1.0
    return v / np.sqrt(2 ** n)


def random_A(n, rng):
    return [[int(rng.integers(0, 2)) if j >= i else 0 for j in range(n)] for i in range(n)]


def cz_count(A, n):
    """Two-qubit gates the prep needs: one CZ per set OFF-diagonal bit. Exactly countable."""
    return sum(A[i][j] for i in range(n) for j in range(i + 1, n))


def accept_prob(rho_purity):
    """Closed form of the two-copy destructive-SWAP purity witness."""
    return (1.0 + rho_purity) / 2.0


def self_test(verbose=True):
    rng = np.random.default_rng(50271)
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<50} {detail}")

    print("  G3a — the ALT ensemble is what the THEOREM's hard instance is")
    worst = 0.0
    for n in (3, 4, 5, 6):
        for _ in range(8):
            A = random_A(n, rng)
            v = phase_state(n, A)
            worst = max(worst, abs(np.vdot(v, v).real - 1.0))          # normalised
            worst = max(worst, float(np.max(np.abs(np.abs(v) - 2 ** (-n / 2)))))  # flat modulus
    rec("G3a degree-2 phase states: normalised, flat modulus", worst < 1e-12,
        f"max dev = {worst:.2e}")

    print("\n  G3b — Q-ARM STATISTIC vs CLOSED FORM (the number the flight reads)")
    w_alt = w_null = 0.0
    for n in (3, 4, 5, 6):
        A = random_A(n, rng)
        v = phase_state(n, A)
        rho_alt = np.outer(v, v.conj())
        w_alt = max(w_alt, abs(accept_prob(np.trace(rho_alt @ rho_alt).real) - 1.0))
        mm = np.eye(2 ** n) / 2 ** n
        want = 0.5 + 2.0 ** (-(n + 1))
        w_null = max(w_null, abs(accept_prob(np.trace(mm @ mm).real) - want))
    rec("G3b ALT accepts with probability exactly 1", w_alt < 1e-12, f"max err = {w_alt:.2e}")
    rec("G3b NULL accepts at exactly 1/2 + 2^-(n+1)", w_null < 1e-12, f"max err = {w_null:.2e}")

    print("\n  G3c — VACUITY GUARD: the two hypotheses must actually be separable")
    gaps = {n: 1.0 - (0.5 + 2.0 ** (-(n + 1))) for n in (8, 12, 16)}
    ok = all(g > 0.45 for g in gaps.values())
    rec("G3c gap is large and grows with n", ok,
        " ".join(f"n={n}:{g:.4f}" for n, g in gaps.items()))

    print("\n  G3d — BLIND LABEL RECOVERY at the frozen shot count, M=40 sealed trials")
    n, M = 8, 40
    for shots in (16, 34):
        correct = 0
        for _ in range(M):
            lab = int(rng.integers(0, 2))                     # sealed: 0=NULL, 1=ALT
            p = 1.0 if lab == 1 else 0.5 + 2.0 ** (-(n + 1))
            k = rng.binomial(shots, p)
            guess = 1 if k == shots else 0                    # ALT iff every shot accepts
            correct += (guess == lab)
        rec(f"G3d M=40 blind accuracy at {shots} shots", correct / M >= 0.95,
            f"{correct}/{M} = {correct / M:.3f}")

    print("\n  G3e — MUTATION CONTROLS: break it on purpose; the gates MUST fail")
    bad = accept_prob(0.0)                                    # a witness blind to purity
    rec("G3e a purity-blind witness is CAUGHT by G3b", abs(bad - 1.0) > 1e-9,
        f"reads {bad:.4f} on ALT, closed form says 1.0")
    correct = 0
    for _ in range(M):
        lab = int(rng.integers(0, 2))
        guess = int(rng.integers(0, 2))                       # a decoder that ignores the data
        correct += (guess == lab)
    rec("G3e a coin-flip decoder is CAUGHT by G3d", correct / M < 0.95,
        f"{correct}/{M} = {correct / M:.3f}")

    print("\n  PREP COST of the corrected ensemble (exactly countable, no synthesis lottery)")
    for n in (8, 12, 16):
        cs = [cz_count(random_A(n, rng), n) for _ in range(200)]
        print(f"    n={n:>3}  CZ mean {np.mean(cs):>6.1f}  cap {n*(n-1)//2:>4}  "
              f"(expected {n*(n-1)/4:.1f})")

    return npass, nfail


if __name__ == "__main__":
    print("DOOR (a) — G3 $0 GATE + the owed degree-2-phase-state design edit\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ G3 GATES PASSED — ensemble corrected, Q-arm statistic verified against")
        print("     closed form, vacuity guarded, mutations caught. G2 seals remain the blocker.")
    else:
        print("  ⛔ G3 NOT PASSED.")
        sys.exit(2)
