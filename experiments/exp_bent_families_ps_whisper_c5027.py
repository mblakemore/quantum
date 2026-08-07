#!/usr/bin/env python3
"""Bent families beyond Maiorana-McFarland — is the door my own red-team named actually open?

THE DOOR. C4996 retired the campaign's 476x runtime advantage by attacking the PROBLEM's algebra:
the MM property f(x,.) is a linear character in y with slope x, so a hidden shift's x-half leaks in
k oracle queries. That red-team's closing paragraph named the prerequisite for a real submission:

    "The property that made MM an ideal sealed, self-verifying race instance — a known closed-form
     dual — is the SAME property that makes it classically easy. Verifiability via exploitable
     linear structure is in direct tension with classical hardness. A genuine hidden-shift advantage
     needs A BENT FAMILY WITH NO SUCH STRUCTURE."

THE VULNERABILITY IS STRUCTURAL, NOT INCIDENTAL. f(x,y) = x.y XOR g(x) is LINEAR IN y for every
fixed x — that IS Maiorana-McFarland's defining property. No choice of g repairs it.

CANDIDATE: Dillon's PARTIAL SPREAD (PS-). The support is a union of 2^(k-1) pairwise-disjoint
k-dimensional subspaces of F2^(2k) meeting only at 0. There is no coordinate split into halves with
one half linear, so the MM attack has nothing to grip.

PRE-REGISTERED BEFORE ANY CODE RAN (scratchpad/prereg.txt, and restated here so it travels with the
artifact):

  P1  a correct PS- is bent: Walsh spectrum flat at +-2^k. CONSTRUCTION CHECK — failure means my
      implementation is wrong, not the theory.
  P2  the MM linear-structure attack FAILS on PS-. Expected, and PRE-STATED AS NEAR-TAUTOLOGICAL
      AND THEREFORE WEAK: the attack is DEFINED in terms of MM's linear half, so its failure on a
      family without one shows almost nothing. Run as a sanity check, NOT as a result.
  P3  THE REAL QUESTION, answer unknown: does PS- have its OWN exploitable structure? A union of
      subspaces is highly structured. Specific worry: support membership may reveal the subspaces,
      and a shift mapping the union to a translate may be recoverable from few support samples.
  P4  THE TENSION MAY NOT BE ESCAPABLE. If a family is easy to verify it may be easy to attack, and
      "the genre admits no sealed self-verifying hard instance" is a real negative result.

FALSIFIER for the whole line: ANY o(2^k) attack on PS- hidden shift shuts the door again.

Scope: k=3..5 (n=6..10), classical simulation only, no QPU. Problem design, not a flight.
Substrate: claude-fable-5, Whisper C5027.
"""
import itertools
import sys

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# F2 linear algebra on integer bit-vectors
# ─────────────────────────────────────────────────────────────────────────────
def bits(v, n):
    return [(v >> i) & 1 for i in range(n)]


def span(basis):
    """All 2^len(basis) elements of the subspace spanned by `basis` (ints, XOR)."""
    out = {0}
    for b in basis:
        out |= {x ^ b for x in out}
    return out


def rank_f2(vecs, n):
    rows, r = list(vecs), 0
    piv = []
    for bit in range(n):
        p = next((i for i in range(r, len(rows)) if (rows[i] >> bit) & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and (rows[i] >> bit) & 1:
                rows[i] ^= rows[r]
        piv.append(bit)
        r += 1
    return r


# ─────────────────────────────────────────────────────────────────────────────
# The DESARGUESIAN SPREAD of F2^(2k), via the field F_{2^k}
# Every element of F_{2^k}^2 \ {0} lies in exactly one of the 2^k + 1 lines
#   L_a = {(x, a*x) : x in F_{2^k}}   for a in F_{2^k},   plus  L_inf = {(0, y)}
# Those lines are k-dimensional F2-subspaces meeting pairwise only at 0 — a spread.
# PS- takes the union of 2^(k-1) of them (excluding 0) as the support.
# ─────────────────────────────────────────────────────────────────────────────
# Conway polynomials for F_{2^k}: x^k + ... (as bitmask of the reduction polynomial)
RED = {2: 0b111, 3: 0b1011, 4: 0b10011, 5: 0b100101, 6: 0b1000011, 7: 0b10000011,
       8: 0b100011011, 10: 0b10000001001, 12: 0b1000001010011,
       16: 0b10001000000001011, 20: 0b100000000000000001001}


def gf_mul(a, b, k):
    """Multiply in F_{2^k}."""
    red, p = RED[k], 0
    while b:
        if b & 1:
            p ^= a
        b >>= 1
        a <<= 1
        if a >> k & 1:
            a ^= red
    return p


def desarguesian_spread(k):
    """The 2^k + 1 lines of the Desarguesian spread of F2^(2k), each as a set of ints.
    An element (x,y) is encoded as x | (y << k)."""
    lines = []
    for a in range(2 ** k):                       # L_a = {(x, a x)}
        lines.append({x | (gf_mul(a, x, k) << k) for x in range(2 ** k)})
    lines.append({(y << k) for y in range(2 ** k)})   # L_inf = {(0,y)}
    return lines


def ps_minus(k, chosen, n=None):
    """PS- truth table on F2^(2k): f(v) = 1 iff v is in the union of `chosen` lines, v != 0.
    Dillon: |chosen| = 2^(k-1) gives a BENT function."""
    n = n or 2 * k
    supp = set()
    for i in chosen:
        supp |= LINES_CACHE[k][i]
    supp.discard(0)
    return np.array([1 if v in supp else 0 for v in range(2 ** n)], dtype=np.int8)


LINES_CACHE = {}


# ─────────────────────────────────────────────────────────────────────────────
# Bentness
# ─────────────────────────────────────────────────────────────────────────────
def walsh(f, n):
    """Walsh-Hadamard transform of (-1)^f. Bent iff all |W| == 2^(n/2)."""
    F = (1 - 2 * f.astype(np.int64))
    h = 1
    while h < 2 ** n:
        F = F.reshape(-1, 2 * h)
        a, b = F[:, :h].copy(), F[:, h:].copy()
        F[:, :h], F[:, h:] = a + b, a - b
        F = F.reshape(-1)
        h *= 2
    return F


def is_bent(f, n):
    W = walsh(f, n)
    return bool(np.all(np.abs(W) == 2 ** (n // 2))), W


# ─────────────────────────────────────────────────────────────────────────────
# The MM attack, as it was actually fired at F121 — run here as a SANITY CHECK
# ─────────────────────────────────────────────────────────────────────────────
def mm_slope_leak(f_shifted, k):
    """MM attack: read the slope of f(0,.) in y. On MM this returns s_x directly.
    On a family with no linear half it returns garbage — which is the point, and is WEAK
    evidence by construction (P2)."""
    n = 2 * k
    base = f_shifted[0]
    slope = 0
    for i in range(k):
        e = 1 << (k + i)                    # e_i in the y-half
        if f_shifted[e] != base:
            slope |= (1 << i)
    return slope


def main():
    print(__doc__.split("Scope:")[0].strip()[:0] or "", end="")
    print("BENT FAMILIES BEYOND MAIORANA-MCFARLAND — PS- construction and sanity check\n")

    for k in (3, 4, 5):
        n = 2 * k
        LINES_CACHE[k] = desarguesian_spread(k)
        lines = LINES_CACHE[k]

        # the spread must actually BE a spread before anything built on it means anything
        pairwise_ok = all(len(lines[i] & lines[j]) == 1
                          for i, j in itertools.combinations(range(len(lines)), 2))
        covers = set().union(*lines)
        dims_ok = all(rank_f2([v for v in L if v], n) == k for L in lines)
        print(f"  k={k}  spread: {len(lines)} lines (expect {2**k + 1}), "
              f"pairwise∩={{0}}: {pairwise_ok}, each k-dim: {dims_ok}, "
              f"covers F2^{n}: {len(covers) == 2**n}")

        # P1 — PS- with 2^(k-1) lines is bent
        rng = np.random.default_rng(4242 + k)
        chosen = sorted(rng.choice(len(lines), size=2 ** (k - 1), replace=False).tolist())
        f = ps_minus(k, chosen)
        bent, W = is_bent(f, n)
        print(f"        PS- on {2**(k-1)} of {len(lines)} lines: BENT={bent}  "
              f"|W| unique={sorted(set(np.abs(W).tolist()))[:3]}  (expect [{2**(n//2)}])")

        # P2 — the MM attack, as a sanity check only
        s = int(rng.integers(1, 2 ** n))
        fs = np.array([f[v ^ s] for v in range(2 ** n)], dtype=np.int8)
        got = mm_slope_leak(fs, k)
        true_sx = s & ((1 << k) - 1)
        print(f"        MM slope-leak vs true s_x: got {got:0{k}b}, true {true_sx:0{k}b}  "
              f"-> {'LEAKS' if got == true_sx else 'fails (expected, and weak evidence)'}\n")


if __name__ == "__main__":
    main()
