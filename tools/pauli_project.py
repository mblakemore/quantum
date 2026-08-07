#!/usr/bin/env python3
"""P-CCM v1.0 — component ③: GENERAL-PAULI PROJECTION of a stabilizer state. The last blocker.

WHAT WAS MISSING. The kernel's `shrink` projects onto {x : (xi,x) = alpha} — a Z-TYPE Pauli only —
and `apply_H` is a stub that raises. But component ② hands back stabilizer groups G, H in P_t whose
generators are arbitrary Paulis, so evaluating <psi|Pi_G|psi> on the standard form needs

    (I + P)/2 |K,q>        for  P = i^kappa X^alpha Z^beta,   kappa = alpha.beta (mod 2)

Without it the solver only runs where an explicit 2^t statevector would have done — the regime where
verification is easy and value is zero.

THE DERIVATION, because the case analysis is the whole content.

Write |K,q> = 2^{-k/2} SUM_{x in K} w^{q(x)}|x>,  w = e^{i pi/4},  K = h (+) span(g_1..g_k).
Then P|K,q> = 2^{-k/2} SUM_{x in K} w^{qt(x)} |x (+) alpha>, where the DIAGONAL part contributes

    qt = q + [2 kappa + 4(beta.h)] + SUM_a 4(beta.g_a) x_a                          (affine, cheap)

because 4*XOR is linear mod 8. The X part is then JUST a shift of the affine space: h <- h (+) alpha,
with q UNCHANGED in coordinates. Two cases follow, split by whether alpha lies in the linear part:

CASE B — alpha NOT in L(K).  K and K (+) alpha are disjoint, so the sum spans a space of dimension
  k+1 with new basis vector alpha, and

      q''(xvec, x_{k+1}) = q(xvec) + x_{k+1} * r(xvec),    r = qt - q

  which is already a valid quadratic form: D_{k+1} = 2 kappa + 4(beta.h) in {0,2,4,6} and
  J_{a,k+1} = 4(beta.g_a) in {0,4}. Dimension GROWS. Factor 2^{-1/2}.

CASE A — alpha IN L(K).  Both states live on the same K, so re-express P|K,q> with shift h and
  compare. The difference r = q' - q is AFFINE (J is untouched by both steps), r = r0 + SUM r_a x_a.
  The amplitude factor is 1 + w^r, and:

      r = 0 -> 2      r = 4 -> 0      r = 2 -> sqrt2 w^1      r = 6 -> sqrt2 w^7

  For the result to be a stabilizer state the MODULUS must be constant on the support, so r mod 4
  must be constant, forcing every r_a in {0,4}. Two sub-cases:

    A-i   r0 = 0 mod 4 : r takes values {0,4}. Support = {xvec : (+)_{a in S} x_a = r0/4}, an affine
          hyperplane — i.e. EXACTLY a shrink, on xi = (+)_{a in S} gbar_a. Dimension SHRINKS by 1
          (or the state is returned unchanged / killed when S is empty). Factor 2^{-1/2} (or 1).
    A-ii  r0 = 2 mod 4 : r takes values {2,6}, support is ALL of K, dimension UNCHANGED and only
          phases move: 1 + w^r = 2 cos(pi r/8) w^{r/2}, whose sign flip at r=6 is the (+4) that
          makes g(x) = 1 - 2m(x) with m an F2-linear function. Expanding 2*XOR mod 8 gives the
          quadratic correction, so g is a quadratic form:

              Q += 1 - 2 l0 ;   D_a += 4 l0 - 2  (a in S) ;   J_ab += 4  (a<b in S)

          Factor 2^{-1/2}.

  A constant r in {2,6} would mean <phi|P|phi> = +-i, impossible for Hermitian P — asserted, not
  assumed.

CASE A-i REUSES THE EXISTING GATED SHRINK rather than reimplementing it. That is deliberate: shrink
is inside the 81/81 reference gate, and the cheapest correct code here is code I do not write.

GATE: (I + P.matrix())/2 @ statevector  ==  factor * result.statevector(), on random stabilizer
states and random Hermitian Paulis. Amplitudes, not probabilities — a global phase error is
invisible in <.> and fatal in a SUM of terms, which is the only way these states are ever used.

Substrate: claude-fable-5, Whisper C5023. Creator directive: "@whisper build component 3".
"""
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stabilizer_rank_kernel as ref                                        # noqa: E402

EMPTY, SAME, SUCCESS = ref.EMPTY, ref.SAME, ref.SUCCESS


def _parity(u, v):
    return int(np.dot(u.astype(int), v.astype(int))) & 1


def pauli_project(st, kappa, alpha, beta):
    """(I + P)/2 |st>  for  P = i^kappa X^alpha Z^beta,  Hermitian (kappa = alpha.beta mod 2).

    Modifies st IN PLACE. Returns (status, p) where the projected state is  2^{-p/2} * |st>:
        EMPTY   -> the projection annihilates the state (p meaningless)
        SAME    -> P|st> = |st>, result is |st> exactly, p = 0
        SUCCESS -> result is 2^{-1/2}|st> with st updated, p = 1
    """
    n, k = st.n, st.k
    alpha = np.asarray(alpha, dtype=np.uint8) & 1
    beta = np.asarray(beta, dtype=np.uint8) & 1
    assert (int(np.dot(alpha.astype(int), beta.astype(int))) - int(kappa)) % 2 == 0, \
        "P is not Hermitian: kappa must equal alpha.beta mod 2"

    # coordinates of alpha in the FULL basis via the dual; alpha in L(K) iff c_a = 0 for a >= k
    c = np.array([_parity(alpha, st.Gbar[a]) for a in range(n)], dtype=np.uint8)

    # the diagonal (Z^beta and phase) contribution, r = qt - q, affine and cheap
    r_const = (2 * int(kappa) + 4 * _parity(beta, st.h)) % 8
    r_lin = np.array([(4 * _parity(beta, st.G[a])) % 8 for a in range(k)], dtype=np.int64)

    # ── CASE B: alpha not in L(K) — the space GROWS ──────────────────────────
    if c[k:].any():
        p = k + int(np.argmax(c[k:] == 1))
        # make g_p = alpha by a basis change, keeping G Gbar^T = I
        for a in range(n):
            if a != p and c[a]:
                st.Gbar[a] = (st.Gbar[a] ^ st.Gbar[p]) % 2
        st.G[p] = alpha.copy()
        if p != k:
            st.G[[p, k]] = st.G[[k, p]]
            st.Gbar[[p, k]] = st.Gbar[[k, p]]
        st.D[k] = r_const
        st.J[:k, k] = r_lin
        st.J[k, :k] = r_lin
        st.J[k, k] = (2 * r_const) % 8
        st.k = k + 1
        return SUCCESS, 1

    # ── CASE A: alpha in L(K) — same affine space; compute r = q' - q ────────
    # q~ from the diagonal part, then shift back by c so both use the shift h
    Qt = (st.Q + r_const) % 8
    Dt = st.D[:k].copy()
    Dt = (Dt + r_lin) % 8                      # 2*Dt unchanged mod 8, so J_aa stays valid
    Jt = st.J[:k, :k].copy()
    for a in range(k):
        if c[a]:
            y = np.zeros(k, dtype=np.int64)
            y[a] = 1
            Qt, Dt = ref._update_shift(Qt, Dt, Jt, y, k)

    r0 = int(Qt - st.Q) % 8
    ra = (Dt - st.D[:k]) % 8
    assert all(int(v) in (0, 4) for v in ra), \
        f"r has a coefficient outside {{0,4}} ({ra.tolist()}) — input was not a Hermitian Pauli"
    S = [a for a in range(k) if int(ra[a]) == 4]

    if r0 % 4 == 0:
        # ── A-i: r in {0,4}. Either constant, or an affine hyperplane = a shrink ──
        if not S:
            return (SAME, 0) if r0 == 0 else (EMPTY, 0)
        xi = np.zeros(n, dtype=np.uint8)
        for a in S:
            xi ^= st.Gbar[a]
        target = ((r0 // 4) ^ _parity(xi, st.h)) & 1
        status = ref.shrink(st, xi, target)
        assert status == SUCCESS, "A-i must reduce the dimension by exactly one"
        return SUCCESS, 1

    # ── A-ii: r in {2,6}. Support is all of K; only the phases move ──────────
    assert S, "a constant r in {2,6} would give <phi|P|phi> = +-i, impossible for Hermitian P"
    l0 = ((r0 - 2) // 4) & 1
    st.Q = (st.Q + 1 - 2 * l0) % 8
    for a in S:
        st.D[a] = (st.D[a] + 4 * l0 - 2) % 8
    for ii in range(len(S)):
        for jj in range(ii + 1, len(S)):
            a, b = S[ii], S[jj]
            st.J[a, b] = (st.J[a, b] + 4) % 8
            st.J[b, a] = st.J[a, b]
    for a in S:
        st.J[a, a] = (2 * st.D[a]) % 8
    return SUCCESS, 1


def project_group(st, generators):
    """Pi_G |st> for G = <generators>, each (kappa, alpha, beta). Returns (state|None, p)
    with the result equal to 2^{-p/2}|st>. This is the object component ② hands over."""
    total = 0
    for (kappa, alpha, beta) in generators:
        status, p = pauli_project(st, kappa, alpha, beta)
        if status == EMPTY:
            return None, 0
        total += p
    return st, total


# ─────────────────────────────────────────────────────────────────────────────
# GATES
# ─────────────────────────────────────────────────────────────────────────────
def _pauli_matrix(kappa, alpha, beta):
    I2 = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    M = np.array([[1.0 + 0j]])
    for j in range(len(alpha)):
        f = (X @ Z if beta[j] else X) if alpha[j] else (Z if beta[j] else I2)
        M = np.kron(M, f)
    return (1j ** (int(kappa) % 4)) * M


def _random_hermitian_pauli(n, rng):
    alpha = rng.integers(0, 2, size=n).astype(np.uint8)
    beta = rng.integers(0, 2, size=n).astype(np.uint8)
    kappa = (int(np.dot(alpha.astype(int), beta.astype(int))) % 2 + 2 * int(rng.integers(2))) % 4
    return kappa, alpha, beta


def self_test(verbose=True):
    rng = np.random.default_rng(20260807)
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<46} {detail}")

    print("  H1 — (I+P)/2 on AMPLITUDES vs explicit matrices (not probabilities: a global")
    print("       phase error is invisible in <.> and fatal inside a sum of terms)")
    counts = {"EMPTY": 0, "SAME": 0, "GROW": 0, "SHRINK": 0, "PHASE": 0}
    worst = 0.0
    ncase = 0
    for n in (1, 2, 3, 4):
        for _ in range(140):
            k = int(rng.integers(0, n + 1))
            st = ref.random_state_via_extend(n, k, rng)
            if st.check_invariants() is not None:
                continue
            v0 = st.statevector()
            kappa, alpha, beta = _random_hermitian_pauli(n, rng)
            want = (np.eye(2 ** n) + _pauli_matrix(kappa, alpha, beta)) @ v0 / 2
            k_before = st.k
            status, p = pauli_project(st, kappa, alpha, beta)
            ncase += 1
            if status == EMPTY:
                counts["EMPTY"] += 1
                worst = max(worst, float(np.max(np.abs(want))))
                continue
            got = 2.0 ** (-p / 2) * st.statevector()
            if status == SAME:
                counts["SAME"] += 1
            elif st.k > k_before:
                counts["GROW"] += 1
            elif st.k < k_before:
                counts["SHRINK"] += 1
            else:
                counts["PHASE"] += 1
            worst = max(worst, float(np.max(np.abs(want - got))))
            inv = st.check_invariants()
            if inv is not None:
                rec(f"H1 invariants broken: {inv}", False)
                return npass, nfail
    rec("H1 amplitudes match (I+P)/2 exactly", worst < 1e-10,
        f"{ncase} cases, max |err| = {worst:.2e}")
    print(f"       branch coverage:  " +
          "  ".join(f"{k}={v}" for k, v in counts.items()))
    allhit = all(v > 0 for v in counts.values())
    rec("H1b every branch of the case analysis exercised", allhit,
        "EMPTY / SAME / grow(B) / shrink(A-i) / phase(A-ii)")

    print("\n  H2 — projector idempotence: applying P twice equals applying it once")
    worst2 = 0.0
    for n in (2, 3):
        for _ in range(120):
            st = ref.random_state_via_extend(n, int(rng.integers(0, n + 1)), rng)
            if st.check_invariants() is not None:
                continue
            kappa, alpha, beta = _random_hermitian_pauli(n, rng)
            s1 = st.copy()
            st1, p1 = pauli_project(s1, kappa, alpha, beta)
            if st1 == EMPTY:
                continue
            v1 = 2.0 ** (-p1 / 2) * s1.statevector()
            s2 = s1.copy()
            st2, p2 = pauli_project(s2, kappa, alpha, beta)
            v2 = (0 if st2 == EMPTY else 1) and 2.0 ** (-(p1 + p2) / 2) * s2.statevector()
            if st2 == EMPTY:
                worst2 = max(worst2, float(np.max(np.abs(v1))))
            else:
                worst2 = max(worst2, float(np.max(np.abs(v1 - v2))))
    rec("H2 Pi^2 = Pi", worst2 < 1e-10, f"max |err| = {worst2:.2e}")

    print("\n  H3 — group projection Pi_G against an explicit product of projectors")
    worst3 = 0.0
    ngrp = 0
    for n in (2, 3):
        for _ in range(60):
            st = ref.random_state_via_extend(n, int(rng.integers(0, n + 1)), rng)
            if st.check_invariants() is not None:
                continue
            gens = []
            for _ in range(int(rng.integers(1, 3))):
                gens.append(_random_hermitian_pauli(n, rng))
            # only commuting generators form a group projector
            ok = True
            for (k1, a1, b1), (k2, a2, b2) in itertools.combinations(gens, 2):
                if (_parity(a1, b2) ^ _parity(a2, b1)) == 1:
                    ok = False
            if not ok:
                continue
            M = np.eye(2 ** n, dtype=complex)
            for (kk, aa, bb) in gens:
                M = ((np.eye(2 ** n) + _pauli_matrix(kk, aa, bb)) / 2) @ M
            want = M @ st.statevector()
            s = st.copy()
            res, p = project_group(s, gens)
            got = np.zeros(2 ** n, dtype=complex) if res is None else \
                2.0 ** (-p / 2) * s.statevector()
            ngrp += 1
            worst3 = max(worst3, float(np.max(np.abs(want - got))))
    rec("H3 Pi_G matches the product of projectors", worst3 < 1e-10,
        f"{ngrp} commuting groups, max |err| = {worst3:.2e}")

    return npass, nfail


if __name__ == "__main__":
    print("GENERAL-PAULI PROJECTION — component ③ correctness gates\n")
    print("  (I + i^kappa X^alpha Z^beta)/2 acting on the standard form (n,k,h,G,Gbar,Q,D,J)")
    print("  CASE B  alpha not in L(K): dimension GROWS by 1, new basis vector alpha")
    print("  CASE A-i  r in {0,4}: an affine hyperplane — reuses the gated shrink")
    print("  CASE A-ii r in {2,6}: dimension unchanged, phases only\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ GATES PASSED — <psi|Pi_G|psi> can now be evaluated on the standard form.")
    else:
        print("  ⛔ GATES NOT PASSED.")
        sys.exit(2)
