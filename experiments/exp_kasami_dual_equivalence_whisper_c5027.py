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

Substrate: claude-fable-5, Whisper C5027.
"""
import sys
from math import gcd

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from exp_bent_families_ps_whisper_c5027 import gf_mul, walsh  # noqa: E402

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

    print("\n  n=8 says YES, n=10 says NO. The target is n=40, so n=10 is the informative one:")
    print("  the n=8 equivalence is a SMALL-SIZE COINCIDENCE, not a family property.")
    print("\n  SCOPE: 'not affine-equivalent to a monomial' is NOT 'expensive'. It closes the")
    print("  cheapest hypothesis for the dual, not the question.")


if __name__ == "__main__":
    main()
