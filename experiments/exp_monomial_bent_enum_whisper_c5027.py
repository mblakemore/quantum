#!/usr/bin/env python3
"""Which bent family is the CHEAPEST to compile? — enumerate, don't recall.

THE QUESTION, as asked: "what's the next family to try?" The tempting move is to name families
from memory. The better move is that the question has a MEASURABLE form, because of an identity
that collapses two things I had been treating separately:

    for a MONOMIAL bent function f(x) = Tr(a x^d) on F_2^n,
        algebraic degree = HW(d)                     (Hamming weight of the exponent)
        circuit cost     = HW(d) - 1 multiplications (squarings are F2-LINEAR, hence FREE)
    SO CIRCUIT COST AND ALGEBRAIC DEGREE ARE THE SAME NUMBER.

Degree 2 is affine-equivalent to x.y — Maiorana-McFarland — which is exactly what leaked at
C4996 (F121 retired, 41 queries, ~7,000x). So the question is not which NAME to try next, it is:

    WHAT IS THE LOWEST HW(d) ABOVE 2 THAT ADMITS A BENT MONOMIAL?

That is enumerable. So it was enumerated rather than recalled.

WHAT THE ENUMERATION FOUND (all d in [1, 2^n-1], bentness by full Walsh spectrum):
    n=6: HW=2 (9 exponents) and HW=3 (6 exponents) — but the six are ONE cyclotomic coset,
         d=7 = 2^3-1 = 2^(n/2)-1, the DILLON exponent. Exactly one non-quadratic class.
    n=8: HW=2 (28) and HW=4 (24) — and the 24 are THREE distinct cosets:
         d=15 = 2^4-1  Dillon (= PS_ap, the family C5027 already priced and walled on qubits)
         d=39, whose coset contains 57 = 2^6-2^3+1 — the KASAMI exponent at i=3
         d=45, neither of the above

THE COST RESULT. Kasami i=3 gives d=57 = 111001, HW=4 -> 3 MULTIPLICATIONS AND NO INVERSION.
Against PS_ap's Itoh-Tsujii inversion (6 mults at k=20) plus one multiply = 7, that is 2.3x
cheaper, and gcd(3,40)=1 so i=3 is admissible at the target n=40. Verified bent at n=10
(682 of 1023 values of a) and n=16.

    d = 2^m - 1 is the exception to the HW cost rule: x^(2^m-1) = Frobenius^m(x)/x, one
    inversion and one multiply, NOT HW-1 multiplies. That shortcut is why Dillon/PS_ap costs
    what it costs — and it is also why PS_ap and "the Dillon monomial" are the same thing.

THE PART THAT MATTERS MOST, AND IT IS A CORRECTION OF THIS FILE'S OWN FIRST CONCLUSION.
The corrected rule from the PS_ap negative is that Roetteler runs f AND f~, so BOTH must be
cheap. The Kasami dual is NOT a monomial (searched exhaustively over every exponent and every
coefficient at n=10). I then measured its trace-term count — 21 at n=8, 40 at n=10, 467 at
n=14, a roughly constant ~40-62% of all available cyclotomic cosets — and read that density as
"no sparse compilation exists, the line is dead."

THAT INFERENCE IS FALSE, and the counterexample is in this same table: d=15 IS the Dillon/PS_ap
monomial whose dual C5027 verified is CHEAP (the same spread under sigma(a)=a^-1), and it scores
65% dense on the same metric. Falsified directly below: composing a monomial with a random
INVERTIBLE F2-LINEAR map — which costs ZERO T-gates, CNOTs only — moves its trace-term count
from 1 to 21-22, indistinguishable from the Kasami dual's 21. THE METRIC READS THE BASIS, NOT
THE COST.

So the Kasami line is NOT closed, and the honest state is:
    MEASURED   f is 2.3x cheaper than PS_ap and carries no inversion
    MEASURED   f stays bent at the sizes that matter, and i=3 is admissible at n=40
    MEASURED   the dual is not a monomial (exhaustive at n=10)
    OPEN       whether the dual is LINEARLY EQUIVALENT to something cheap — which is exactly
               what PS_ap's dual turned out to be, and what the trace-term count cannot see

Substrate: claude-opus-5, Whisper C5027.
"""
import sys

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from exp_bent_families_ps_whisper_c5027 import gf_mul, walsh  # noqa: E402


def tables(k):
    """log/antilog against a SEARCHED primitive element.

    An earlier version assumed g=2 was primitive and therefore labelled RED[8] — the AES
    polynomial, which is irreducible but under which x has order 51 — a 'bad modulus'. The
    field was fine; the test was wrong. Searching for g removes the assumption.
    """
    N = 2 ** k - 1
    for g in range(2, 2 ** k):
        anti = np.zeros(N, dtype=np.int64)
        log = np.full(2 ** k, -1, dtype=np.int64)
        z, ok = 1, True
        for e in range(N):
            if log[z] != -1:
                ok = False
                break
            anti[e], log[z] = z, e
            z = gf_mul(z, g, k)
        if ok and z == 1:
            return log, anti, N, g
    return None


def trace_tab(k):
    t = np.zeros(2 ** k, dtype=np.int8)
    for z in range(2 ** k):
        s, u = 0, z
        for _ in range(k):
            s ^= u
            u = gf_mul(u, u, k)
        t[z] = s & 1
    return t


def monomial(a, d, log, anti, N, T, n):
    """Truth table of Tr(a x^d), via logs. x=0 -> Tr(0)=0."""
    f = np.zeros(2 ** n, dtype=np.int8)
    nz = np.arange(1, 2 ** n)
    f[nz] = T[anti[(log[a] + d * log[nz]) % N]]
    return f


def n_trace_terms(f, log, anti, N):
    """Cyclotomic cosets carrying a nonzero univariate coefficient.

    NOT A COST METRIC — see the falsification in main(). Kept because it is the quantity that
    LOOKED like a cost metric, and the record of why it is not is the point of this file.
    """
    S = np.nonzero(f[1:])[0] + 1
    L = log[S]
    seen, count = set(), 0
    for lo in range(1, N, 64):
        jj = np.arange(lo, min(lo + 64, N))
        acc = np.bitwise_xor.reduce(anti[(-jj[:, None] * L[None, :]) % N], axis=1)
        for j, v in zip(jj.tolist(), acc.tolist()):
            if not v:
                continue
            c, y = set(), int(j)
            while y not in c:
                c.add(y)
                y = (y * 2) % N
            fs = frozenset(c)
            if fs not in seen:
                seen.add(fs)
                count += 1
    return count


def random_invertible(n, rng):
    while True:
        M = rng.integers(0, 2, size=(n, n), dtype=np.uint8)
        A, r = M.copy(), 0
        for c in range(n):
            p = next((i for i in range(r, n) if A[i, c]), None)
            if p is None:
                continue
            A[[r, p]] = A[[p, r]]
            for i in range(n):
                if i != r and A[i, c]:
                    A[i] ^= A[r]
            r += 1
        if r == n:
            return M


def apply_linear(f, M, n):
    """f o L, for L the F2-linear map with matrix M. Costs ZERO T-gates on hardware."""
    perm = np.zeros(2 ** n, dtype=np.int64)
    for x in range(2 ** n):
        v = 0
        for j in range(n):
            if (x >> j) & 1:
                col = 0
                for i in range(n):
                    col |= int(M[i, j]) << i
                v ^= col
        perm[x] = v
    return f[perm]


def main():
    print("MONOMIAL BENT FUNCTIONS — cost = algebraic degree, so ENUMERATE the cheap ones\n")
    n = 8
    log, anti, N, g = tables(n)
    T = trace_tab(n)

    print(f"  n={n}, primitive g={g}. The three non-quadratic bent monomial classes:\n")
    print(f"    {'d':>4} {'binary':>8} {'HW':>3} {'mults':>8} {'family':>10} "
          f"{'dual terms':>11}")
    fam = {15: "Dillon", 39: "Kasami", 45: "(third)"}
    for d in (15, 39, 45):
        found = None
        for a in range(1, 2 ** n):
            f = monomial(a, d, log, anti, N, T, n)
            W = walsh(f, n)
            if np.all(np.abs(W) == 2 ** (n // 2)):
                found = (f, W)
                break
        f, W = found
        dual = ((1 - np.sign(W)) // 2).astype(np.int8)
        mults = "1 inv+1" if d == 15 else str(bin(d).count("1") - 1)
        print(f"    {d:>4} {bin(d)[2:]:>8} {bin(d).count('1'):>3} {mults:>8} "
              f"{fam[d]:>10} {n_trace_terms(dual, log, anti, N):>11}")

    print("\n  Kasami i=3 -> d=57, HW=4, THREE multiplications and NO inversion, against")
    print("  PS_ap's inversion+multiply = 7 at k=20. 2.3x cheaper. gcd(3,40)=1, so admissible")
    print("  at the target n=40.\n")

    # ── the falsification ────────────────────────────────────────────────────
    print("  FALSIFYING THE 'DENSE DUAL = EXPENSIVE' INFERENCE THIS FILE FIRST DREW:\n")
    f = monomial(1, 57, log, anti, N, T, n)
    base = n_trace_terms(f, log, anti, N)
    rng = np.random.default_rng(5027)
    hits = [n_trace_terms(apply_linear(f, random_invertible(n, rng), n), log, anti, N)
            for _ in range(6)]
    print(f"    Tr(x^57), a monomial                      : {base:>3} trace term(s)")
    print(f"    the SAME function through 6 random linear L: {hits}")
    print("\n    An F2-linear map is CNOTs only — zero T. Those circuits cost the same.")
    print("    The Kasami dual's 21 sits inside that range. The metric reads the BASIS,")
    print("    not the cost, so it cannot close the line and this file does not claim to.")
    print("\n    OPEN: is the Kasami dual linearly equivalent to something cheap? That is what")
    print("    PS_ap's dual turned out to be, and it is the question worth spending on next.")


if __name__ == "__main__":
    main()
