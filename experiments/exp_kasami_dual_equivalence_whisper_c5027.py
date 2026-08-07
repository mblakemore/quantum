#!/usr/bin/env python3
"""Is the Kasami dual affine-equivalent to a cheap monomial?  (Creator: "test the linear
equivalence of the Kasami dual!", ship-computer general#6153)

WHY THIS IS THE QUESTION. Roetteler's hidden-shift algorithm applies BOTH the oracle O_f and the
dual oracle O_f~, so a family is only useful if f AND f~ are both cheap. Kasami i=3 gives
d = 2^6-2^3+1 = 57, HW=4 -> three multiplications and NO inversion, 2.3x cheaper than PS_ap's
Itoh-Tsujii inversion + multiply. Its dual is not a monomial (exhaustive at n=10). The open
question was whether it is a monomial UP TO FREE OPERATIONS.

THE RIGHT RELATION IS AFFINE, NOT LINEAR. In this cost model three things are free:
    F2-linear maps   CNOTs only, zero T   (established in exp_ps_ap_transpile)
    translations     X gates
    constant offset  global phase
so the honest relation is f~(x) = g(Lx + c) XOR eps. Anything affine-equivalent to a monomial
costs exactly what the monomial costs.

METHOD, invariant first because the constructive search is exponential.
  GAMMA-RANK: the F2-rank of M[x][y] = f(x XOR y). Under x -> Lx + c the matrix undergoes a
  simultaneous row/column permutation, which cannot change rank; the constant offset eps flips
  M -> M XOR J, handled by taking the min over both. So Gamma-rank is an AFFINE INVARIANT, and a
  mismatch is a DECISIVE negative — no search required.
  Degree is also affine-invariant, and the dual has degree 4, so only HW(e)=4 monomials qualify.
  Coefficients reduce too: scaling x -> cx is linear and free, so b matters only modulo
  b ~ b*c^e, leaving gcd(e, 2^n-1) classes per exponent rather than 2^n-1.
  Where the invariant MATCHES, a depth-first search constructs L explicitly: choosing L(e_k)
  determines L on 2^(k+1) points, every one of which must already agree, which prunes hard.

RESULT — AND THE TWO SIZES DISAGREE, WHICH IS THE WHOLE POINT.

    n=8   Gamma-rank(f) = 42 = Gamma-rank(dual).  Equivalence possible, and CONSTRUCTIVELY
          CONFIRMED: an invertible L exists (rank 8/8) with dual(x) = Tr(2 (Lx)^57) at ALL 256
          points. L has no c*x^(2^j) closed form — it is a generic linear map, which is still
          free. At n=8 the Kasami dual costs exactly what f costs.

    n=10  Gamma-rank(f) = 62, Gamma-rank(dual) = 64. DIFFERENT -> not equivalent, decisively.
          Sweeping ALL 22 HW=4 cyclotomic cosets against all gcd(e,N) coefficient classes:
          ZERO bent degree-4 monomials at n=10 have Gamma-rank 64.

SO THE n=8 EQUIVALENCE IS A SMALL-SIZE COINCIDENCE. n=10 is the informative size, because the
target is n=40 and a property that dies between 8 and 10 is not a family property.

THIRD AND FOURTH SIZES (Creator: "check n=12 or n=14 to see if it's really structural").
Two points cannot tell which size is the outlier, so both were run. n=14 keeps i=3 and therefore
the SAME family member (gcd(3,14)=1); n=12 forces a different i (gcd(3,12)=3), which independently
tests whether n=10 was an i=3 quirk.

     n   i      d  HW  Gamma-rank f  Gamma-rank dual   gap  verdict
     8   3     57   4            42               42     0  EQUIVALENT (L constructed)
    10   3     57   4            62               64     2  not equivalent
    12   5    993   6           302              314    12  not equivalent
    14   3     57   4            86              448   362  not equivalent

THREE INDEPENDENT SIZES SAY NO, ONE SAYS YES, AND THE GAP WIDENS MONOTONICALLY: 0, 2, 12, 362.
n=8 is the outlier. The behaviour is STRUCTURAL.

    Counting honestly: n=12 also ran i=7, giving d=3972 and IDENTICAL ranks 302/314. That is not
    corroboration — 3972 = 993*4, the same cyclotomic coset, so it is the same function up to
    Frobenius (free). One data point, not two. The identical ranks are the tell.

AND THE ONE OTHER "EQUIVALENT" IN THE WHOLE SWEEP IS THE SHARPEST RESULT HERE. At n=12, i=11
collapses mod 4095 to d=3072, HW=2 — DEGREE TWO, i.e. Maiorana-McFarland — and there the dual IS
free (ranks 14 = 14). MM is precisely the family my own C4996 red-team RETIRED for leaking the
hidden shift in 41 classical queries (F121, ~7,000x, 3/3 court seats). So in this data the dual
comes free exactly where the function is quadratic, and quadratic is exactly what is classically
broken. That is C4996's closing paragraph — "verifiability via exploitable linear structure is in
direct tension with classical hardness" — as a measured instance rather than an argument.

    The rule is not clean, and saying so is the point: n=8 is non-quadratic (HW=4) and its dual is
    still free. It is an unexplained exception, not evidence for the rule. Four sizes is a trend,
    not a theorem, and no obstruction is proven here.

CONTROL, because a sweep that finds nothing is indistinguishable from a sweep that is broken:
f itself is a bent degree-4 monomial with b inside the tested coefficient classes, so it is IN
the candidate set at both sizes. It matches its dual at n=8 and does not at n=10. An invariant
that simply never matched would have failed the n=8 case too, where the equivalence is
independently known to hold.

SCOPE — stated because the failure one step earlier in this same investigation was exactly an
over-read negative. "NOT AFFINE-EQUIVALENT TO A MONOMIAL" IS NOT "EXPENSIVE". The dual could
still be cheap some other way — a sum of two monomials, or structure outside the monomial class
entirely. What is established at n=10 is precisely: it is not a monomial up to free operations.
That closes the cheapest hypothesis, not the question.

Substrate: claude-opus-5, Whisper C5027.
"""
import sys
from math import gcd

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
import exp_bent_families_ps_whisper_c5027 as _B  # noqa: E402

# n=14 is not in the shared RED table and is needed for the same-i third size. x^14+x^5+x^3+x+1.
# NOT asserted irreducible — VERIFIED as a side effect: tables() only returns when it finds an
# element of full order 2^14-1, which cannot exist if the modulus factors. A reducible modulus
# makes tables() return None and the size is skipped rather than silently reported wrong.
_B.RED.setdefault(14, 0b100000000101011)

from exp_bent_families_ps_whisper_c5027 import gf_mul, walsh  # noqa: E402,E401

sys.setrecursionlimit(100000)


def tables(k):
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


def mono(b, e, log, anti, N, T, n):
    f = np.zeros(2 ** n, dtype=np.int8)
    nz = np.arange(1, 2 ** n)
    f[nz] = T[anti[(log[b] + e * log[nz]) % N]]
    return f


def gamma_rank(f, n):
    """F2-rank of M[x][y] = f(x XOR y) — an AFFINE-EQUIVALENCE INVARIANT."""
    def rk(g):
        idx = np.arange(2 ** n)
        rows = [int.from_bytes(np.packbits(g[x ^ idx]).tobytes(), "big")
                for x in range(2 ** n)]
        r = 0
        for b in range(2 ** n):
            bit = 2 ** n - 1 - b
            p = next((i for i in range(r, len(rows)) if (rows[i] >> bit) & 1), None)
            if p is None:
                continue
            rows[r], rows[p] = rows[p], rows[r]
            pr = rows[r]
            for i in range(len(rows)):
                if i != r and (rows[i] >> bit) & 1:
                    rows[i] ^= pr
            r += 1
        return r
    return min(rk(f.astype(np.uint8)), rk((1 - f).astype(np.uint8)))


def gamma_rank_fast(f, n):
    """Same invariant, packed into uint64 words so n=12 and n=14 are reachable — the pure-python
    bigint version is O(2^3n) in bit-ops and does not get past n=10. Forward elimination only,
    since rank does not need full reduction. CONTROLLED against gamma_rank() at n=8 and n=10
    before being trusted at any size where the slow version cannot be run."""
    N = 2 ** n
    idx = np.arange(N)

    def rk(g):
        M = np.empty((N, N // 64), dtype=np.uint64)
        for x in range(N):
            M[x] = np.packbits(g[x ^ idx].astype(np.uint8), bitorder="little").view(np.uint64)
        r = 0
        for y in range(N):
            w, b = y >> 6, np.uint64(y & 63)
            mask = np.uint64(1) << b
            nz = np.flatnonzero((M[r:, w] & mask) != 0)
            if nz.size == 0:
                continue
            p = r + int(nz[0])
            if p != r:
                tmp = M[r].copy()
                M[r] = M[p]
                M[p] = tmp
            hit = np.zeros(N, bool)
            hit[r + 1:] = (M[r + 1:, w] & mask) != 0
            if hit.any():
                M[hit] ^= M[r]
            r += 1
            if r == N:
                break
        return r
    return min(rk(f.astype(np.uint8)), rk((1 - f).astype(np.uint8)))


def sweep_size(n, i, log=None):
    """Gamma-ranks of the Kasami function and its dual at one size, for one i."""
    tb = tables(n)
    if tb is None:
        return None
    log, anti, N, g0 = tb
    T = trace_tab(n)
    d = (2 ** (2 * i) - 2 ** i + 1) % N
    if np.gcd(i, n) != 1:
        return ("inadmissible", d, None, None)
    for a in range(1, 2 ** n):
        f = mono(a, d, log, anti, N, T, n)
        W = walsh(f, n)
        if np.all(np.abs(W) == 2 ** (n // 2)):
            dual = ((1 - np.sign(W)) // 2).astype(np.int8)
            return (a, d, gamma_rank_fast(f, n), gamma_rank_fast(dual, n))
    return ("not bent", d, None, None)


def find_L(target, g, n):
    """Invertible L with target(x) = g(Lx), by DFS over basis images with full-span pruning."""
    M = 2 ** n
    if target[0] != g[0]:
        return None
    Limg = [0] * M
    span, basis = {0}, []

    def dfs(k):
        if k == n:
            return True
        for v in range(1, M):
            if v in span:
                continue
            lo, hi, ok = 1 << k, 1 << (k + 1), True
            for x in range(lo, hi):
                lx = Limg[x - lo] ^ v
                if target[x] != g[lx]:
                    ok = False
                    break
                Limg[x] = lx
            if not ok:
                continue
            add = {s ^ v for s in span}
            span.update(add)
            basis.append(v)
            if dfs(k + 1):
                return True
            span.difference_update(add)
            basis.pop()
        return False
    return basis if dfs(0) else None


def rank_f2(vs, n):
    rows, r = list(vs), 0
    for b in range(n):
        p = next((i for i in range(r, len(rows)) if (rows[i] >> b) & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and (rows[i] >> b) & 1:
                rows[i] ^= rows[r]
        r += 1
    return r


def main():
    print("IS THE KASAMI DUAL AFFINE-EQUIVALENT TO A CHEAP MONOMIAL?\n")
    for n in (8, 10):
        log, anti, N, g0 = tables(n)
        T = trace_tab(n)
        for a in range(1, 2 ** n):
            f = mono(a, 57, log, anti, N, T, n)
            W = walsh(f, n)
            if np.all(np.abs(W) == 2 ** (n // 2)):
                break
        dual = ((1 - np.sign(W)) // 2).astype(np.int8)
        rf, rd = gamma_rank(f, n), gamma_rank(dual, n)
        print(f"  n={n:>2} (primitive g={g0}, bent a={a}): "
              f"Gamma-rank f={rf}, dual={rd}  -> "
              f"{'MATCH, search for L' if rf == rd else 'DIFFERENT: NOT equivalent, decisive'}")

        if rf == rd:
            basis = find_L(list(map(int, dual)), list(map(int, f)), n)
            if basis:
                L = np.zeros(2 ** n, dtype=np.int64)
                for x in range(2 ** n):
                    v = 0
                    for j in range(n):
                        if (x >> j) & 1:
                            v ^= basis[j]
                    L[x] = v
                print(f"       CONSTRUCTED L: rank {rank_f2(basis, n)}/{n}, "
                      f"dual(x)==f(Lx) at ALL {2**n} x: {bool(np.all(dual == f[L]))}")
            else:
                print("       no L found despite matching invariant")
        else:
            # decisive already, but sweep every candidate so the negative is not one-shot
            seen, reps = set(), []
            for e in range(1, N):
                if bin(e).count("1") != 4:
                    continue
                c, y = set(), e
                while y not in c:
                    c.add(y)
                    y = (y * 2) % N
                fr = frozenset(c)
                if fr not in seen:
                    seen.add(fr)
                    reps.append(min(c))
            hits = 0
            for e in reps:
                for bi in range(gcd(e, N)):
                    g = mono(int(anti[bi]), e, log, anti, N, T, n)
                    if not np.all(np.abs(walsh(g, n)) == 2 ** (n // 2)):
                        continue
                    if gamma_rank(g, n) == rd:
                        hits += 1
            print(f"       swept {len(reps)} HW=4 cosets x gcd(e,N) coefficient classes: "
                  f"{hits} monomial(s) with the dual's Gamma-rank")

    # ── third and fourth sizes: is it structural? ────────────────────────────
    print("\n  IS IT STRUCTURAL? third and fourth sizes (n=14 keeps i=3, n=12 must change i):\n")
    print(f"    {'n':>3} {'i':>3} {'d':>6} {'HW':>3} {'rank f':>7} {'rank dual':>10} "
          f"{'gap':>5} {'verdict':>16}")
    for n, i in ((12, 5), (12, 11), (14, 3)):
        a, d, rf, rd = sweep_size(n, i)
        if rf is None:
            print(f"    {n:>3} {i:>3} {d:>6} {'':>3} {str(a):>7}")
            continue
        note = "EQUIVALENT" if rf == rd else "not equivalent"
        if bin(d).count("1") == 2:
            note += " *"
        print(f"    {n:>3} {i:>3} {d:>6} {bin(d).count('1'):>3} {rf:>7} {rd:>10} "
              f"{rd - rf:>5} {note:>16}")
    print("\n    * d=3072 has HW=2 — DEGREE TWO, i.e. Maiorana-McFarland. The dual is free there,")
    print("      and MM is exactly the family C4996 RETIRED for leaking the shift in 41 classical")
    print("      queries. The dual comes free where the function is quadratic, and quadratic is")
    print("      what is classically broken. n=8 stays an unexplained exception to that.")

    print("\n  n=8 says YES; n=10, n=12 and n=14 all say NO, with the gap widening 0, 2, 12, 362.")
    print("  n=8 is the OUTLIER and the behaviour is STRUCTURAL — though four sizes are a trend,")
    print("  not a theorem, and nothing here proves an obstruction.")
    print("\n  SCOPE: 'not affine-equivalent to a monomial' is NOT 'expensive'. It closes the")
    print("  cheapest hypothesis for the dual, not the question.")


if __name__ == "__main__":
    main()
