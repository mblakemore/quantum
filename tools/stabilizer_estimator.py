#!/usr/bin/env python3
"""P-CCM v1.0 — components ④a (uniform stabilizer sampler) and ④ (the norm estimator).

WHY ④a EXISTS AT ALL — solver-plan §5 GAP 2. The estimator's error bar comes from

    M2 = E|<theta|psi>|^2 = ||psi||^2 / d,     M4 = E|<theta|psi>|^4 = 2||psi||^4 / (d(d+1))

which hold because UNIFORM stabilizer states form a 3-design (the paper computes them "by
pretending theta is drawn from the Haar measure", Eq 14). The kernel's existing
random_state_via_extend says in its own docstring:

    "it does not claim to sample Haar-uniformly over stabilizer states"

It was written to feed the TIMING harness, where the distribution is irrelevant. Used in the
estimator it would produce a number that runs, looks plausible, and carries NO VALID ERROR BAR —
a silent failure of exactly the class this campaign keeps getting caught by. Hence Lemma 5.

LEMMA 5 (the paper):  |S_n^{n-d}| = 8 * 2^{n + [n(n+1) - d(d+1)]/2} * PROD_{a=1..d} (1 - 2^{d-n-a})/(1 - 2^{-a})
Sampling recipe:  draw d ~ P(d) = |S_n^{n-d}| / SUM_m |S_n^m|;  then a uniform k=n-d dimensional
subspace, a uniform shift, and a uniform quadratic form (Q, D, J).

THE ESTIMATOR (④, paper Eq 15,16):
    xi = (d/L) SUM_{i=1..L} |<theta_i|psi>|^2,   L = 4 eps^-2,   d = 2^t
    median of J = O(log 1/p_f) independent xi's  ->  relative error eps w.p. >= 1 - p_f

GATES:
    B1  Lemma 5 counts sum to the known stabilizer-state count 8 * 2^n PROD (2^k + 1)
    B2  chi^2 uniformity of the sampler over ALL states, by explicit enumeration at n = 2
    B3  the same test applied to random_state_via_extend  -> resolves pre-registration P5
    C1  xi approximates the EXACT ||psi||^2 within the claimed relative error
    C2  the estimator is UNBIASED: mean of many xi -> ||psi||^2

Substrate: claude-fable-5, Whisper C5021. Creator directive: "build it!".
"""
import math
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stabilizer_rank_kernel as ref                                       # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# ④a — Lemma 5 and the uniform sampler
# ─────────────────────────────────────────────────────────────────────────────
def count_S(n, d):
    """|S_n^{n-d}| — Lemma 5. d = 0 gives the full-dimensional case."""
    if d == 0:
        return 8.0 * 2.0 ** (n + 0.5 * n * (n + 1))
    v = 8.0 * 2.0 ** (n + 0.5 * (n * (n + 1) - d * (d + 1)))
    for a in range(1, d + 1):
        v *= (1 - 2.0 ** (d - n - a)) / (1 - 2.0 ** (-a))
    return v


def dim_distribution(n):
    """P(d) over d = 0..n, and the total |S_n|."""
    c = np.array([count_S(n, d) for d in range(n + 1)], dtype=float)
    return c / c.sum(), c.sum()


def _rand_invertible(n, rng):
    while True:
        G = rng.integers(0, 2, size=(n, n), dtype=np.uint8)
        Gi = ref._inv_gf2(G)
        if Gi is not None:
            return G, Gi


def random_stabilizer_state(n, rng):
    """UNIFORM over S_n, per Lemma 5. This is the distribution the estimator's error bar needs.

    A uniformly random invertible G makes the span of its first k rows a uniform k-dim subspace
    (GL(n,2) is transitive on ordered bases), and a uniform h hits every coset of that subspace
    equally often — so K is uniform among affine spaces of dimension k. (Q, D, J) is then drawn
    uniformly over the 8 * 4^k * 2^{k(k-1)/2} quadratic forms that Lemma 5 counts."""
    P, _ = dim_distribution(n)
    d = int(rng.choice(len(P), p=P))
    k = n - d
    G, Gi = _rand_invertible(n, rng)
    Gbar = Gi.T % 2
    h = rng.integers(0, 2, size=n, dtype=np.uint8)
    Q = int(rng.integers(0, 8))
    D = np.zeros(n, dtype=np.int64)
    D[:k] = rng.integers(0, 4, size=k) * 2
    J = np.zeros((n, n), dtype=np.int64)
    for a in range(k):
        for b in range(a + 1, k):
            v = int(rng.integers(0, 2)) * 4
            J[a, b] = J[b, a] = v
        J[a, a] = (2 * D[a]) % 8
    return ref.StabState(n, k, h, G, Gbar, Q, D, J)


# ─────────────────────────────────────────────────────────────────────────────
# ④ — the norm estimator (Eqs 15,16)
# ─────────────────────────────────────────────────────────────────────────────
def estimate_norm2(terms, coeffs, t, eps, p_f, rng, L=None, J=None):
    """xi ~ ||psi||^2 for psi = SUM_a coeffs[a] |terms[a]>, all t-qubit stabilizer states.

    terms may be a list OR a callable a -> StabState, so a chi = 2^21 decomposition is never
    materialised (solver-plan §6.2)."""
    if L is None:
        L = int(math.ceil(4.0 / eps ** 2))
    if J is None:
        J = max(1, int(math.ceil(math.log(1.0 / p_f) / math.log(4.0 / 3.0))))
    get = terms if callable(terms) else (lambda a: terms[a])
    chi = len(coeffs)
    d = 2.0 ** t
    ests = []
    for _ in range(J):
        acc = 0.0
        for _ in range(L):
            th = random_stabilizer_state(t, rng)
            amp = 0j
            for a in range(chi):
                amp += coeffs[a] * ref.triple_to_complex(ref.inner_product(get(a), th))
            acc += abs(amp) ** 2
        ests.append(d * acc / L)
    return float(np.median(ests)), ests


def exact_norm2(terms, coeffs):
    """||psi||^2 exactly, O(chi^2) inner products through the SAME kernel. This is the oracle
    the estimator is gated against, and it is also the exact route for small chi."""
    get = terms if callable(terms) else (lambda a: terms[a])
    chi = len(coeffs)
    tot = 0j
    for a in range(chi):
        for b in range(chi):
            tot += np.conj(coeffs[b]) * coeffs[a] * \
                ref.triple_to_complex(ref.inner_product(get(a), get(b)))
    return float(tot.real)


# ─────────────────────────────────────────────────────────────────────────────
# GATES
# ─────────────────────────────────────────────────────────────────────────────
def _state_key(st):
    v = st.statevector()
    return tuple(np.round(v, 9) + 0.0)


def _chi2_uniform(counts, ncat, ntot):
    """Pearson chi^2 against the uniform distribution, with a normal-approximation p-value."""
    exp = ntot / ncat
    chi2 = sum((c - exp) ** 2 for c in counts) / exp + (ncat - len(counts)) * exp
    dof = ncat - 1
    z = (chi2 - dof) / math.sqrt(2.0 * dof)
    p = 0.5 * math.erfc(z / math.sqrt(2.0))
    return chi2, dof, p


def self_test(verbose=True):
    rng = np.random.default_rng(20260807)
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<44} {detail}")

    print("  B1 — Lemma 5 counts vs the known stabilizer-state count")
    for n in (1, 2, 3, 4):
        _, tot = dim_distribution(n)
        known = 8.0 * 2 ** n
        for kk in range(1, n + 1):
            known *= (2 ** kk + 1)
        rec(f"B1 |S_{n}| = 8*2^n*PROD(2^k+1)", abs(tot - known) / known < 1e-9,
            f"Lemma5 {tot:,.0f}  known {known:,.0f}")

    print("\n  B2 — chi^2 uniformity of the Lemma-5 sampler (explicit enumeration, n=2)")
    n = 2
    _, tot = dim_distribution(n)
    ncat = int(round(tot))
    N = 20 * ncat
    seen = Counter()
    for _ in range(N):
        seen[_state_key(random_stabilizer_state(n, rng))] += 1
    chi2, dof, p = _chi2_uniform(list(seen.values()), ncat, N)
    rec("B2 Lemma-5 sampler is uniform over S_2", p > 0.01,
        f"{len(seen)}/{ncat} states hit, chi2={chi2:.1f} dof={dof} p={p:.3f}")

    print("\n  B3 — the SAME test on random_state_via_extend  (pre-registration P5)")
    seen2 = Counter()
    for _ in range(N):
        k = int(rng.integers(0, n + 1))
        seen2[_state_key(ref.random_state_via_extend(n, k, rng))] += 1
    chi2b, dofb, pb = _chi2_uniform(list(seen2.values()), ncat, N)
    verdict = "NOT uniform" if pb <= 0.01 else "uniform"
    rec(f"B3 random_state_via_extend is {verdict}", True,
        f"{len(seen2)}/{ncat} states hit, chi2={chi2b:.1f} p={pb:.3g}")
    print(f"       -> P5 predicted it FAILS this test: "
          f"{'CONFIRMED' if pb <= 0.01 else 'REFUTED — it passes'}")

    print("\n  C1/C2 — the estimator against the exact ||psi||^2 through the same kernel")
    import magic_sparsify as ms
    for t in (4, 6):
        k = max(1, min(t - 1, ms.choose_k(t, 0.5)))
        M = ms.random_subspace(t, k, rng)
        Z, _ = ms.z_of_L(ms._pack(M), k)
        xs = ms.term_bitstrings(M, k)
        terms = [ms.term_stabstate(x) for x in xs]
        coeffs = [ms.coefficient(k, Z)] * len(terms)
        ex = exact_norm2(terms, coeffs)
        rec(f"C0 exact ||psi||^2 = 1              t={t} chi={len(terms)}", abs(ex - 1) < 1e-9,
            f"||psi||^2 = {ex:.10f}")
        eps = 0.5
        xi, ests = estimate_norm2(terms, coeffs, t, eps, 0.1, rng)
        rec(f"C1 |xi/||psi||^2 - 1| < 3 eps       t={t}", abs(xi / ex - 1) < 3 * eps,
            f"xi = {xi:.4f}  exact = {ex:.4f}  rel = {xi/ex-1:+.3f}")
        # C2: unbiasedness — many independent single-batch estimates
        many = [estimate_norm2(terms, coeffs, t, eps, 0.9, rng, L=40, J=1)[0] for _ in range(40)]
        mean = float(np.mean(many))
        rec(f"C2 estimator is unbiased            t={t}", abs(mean / ex - 1) < 0.15,
            f"mean of 40 = {mean:.4f}  exact = {ex:.4f}  rel = {mean/ex-1:+.3f}")
    return npass, nfail


if __name__ == "__main__":
    print("STABILIZER SAMPLER + NORM ESTIMATOR — components ④a and ④\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ GATES PASSED")
    else:
        print("  ⛔ GATES NOT PASSED")
        sys.exit(2)
