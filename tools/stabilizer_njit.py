#!/usr/bin/env python3
"""P-CCM v1.0 — FULLY JIT-COMPILED InnerProduct. The end of the ladder.

WHY. Every acceleration this session hit the same wall: 31.6% of runtime was numpy/Python
DISPATCH on small arrays, which no accelerator touches.

    GF(2) bit-packing       5.7x on the routine    ->  1.28x end-to-end
    Z8 update on GPU        36-41x on the kernel   ->  2.10x end-to-end
    dimer partition on GPU  49.2x on the kernel    ->  2.2x  end-to-end
    numba on the Z8 kernel  20.6x                  ->  2.03x, or 5.65x IF dispatch goes to ~0

That last "IF" is what this file removes. Nothing here calls numpy at runtime: the whole of
InnerProduct — shrink, the F2 parity, the dimer partition, the exponential sum, the Z8 updates —
is one nopython compilation unit. No dispatch layer remains to measure.

CORRECTNESS: must reproduce the bit-packed kernel EXACTLY, which itself reproduces the
81/81-statevector-gated reference exactly. Three levels, and no timing is emitted without the
top two agreeing.

IMPLEMENTATION NOTES, all forced by nopython mode:
  * no list comprehensions, no np.nonzero, no np.ix_ — explicit loops and preallocated arrays
  * no np.bitwise_count — popcount via the Kernighan clear-lowest-set-bit loop
  * k cannot be mutated through a scalar argument, so routines return the updated k
  * SNAPSHOT-BEFORE-MUTATE is load-bearing: numpy's .copy() calls in the vectorised form are
    SEMANTICS, not optimisation. Reading them lazily gives fast wrong answers (caught by the
    gate earlier tonight, and preserved here deliberately).

Substrate: claude-fable-5, Whisper C5020. Creator directive: "JIT the whole inner_product".
"""
import numpy as np
from numba import njit

EMPTY, SAME, SUCCESS = 0, 1, 2


@njit(cache=True, inline="always")
def _popcount(x):
    c = 0
    while x:
        x &= x - np.uint64(1)
        c += 1
    return c


@njit(cache=True)
def _parity_and(a, b, W):
    acc = 0
    for w in range(W):
        acc ^= (_popcount(a[w] & b[w]) & 1)
    return acc


@njit(cache=True)
def _addrow(D, J, targets, nt, src, k):
    """Sparse Eq(49,50). SNAPSHOT FIRST — see module docstring."""
    if nt == 0:
        return
    jss = J[src, src]
    row_s = np.empty(k, dtype=np.int64)
    col_s = np.empty(k, dtype=np.int64)
    for c in range(k):
        row_s[c] = J[src, c]
        col_s[c] = J[c, src]
    for ti in range(nt):
        a = targets[ti]
        D[a] = (D[a] + D[src] + col_s[a]) % 8
    for ti in range(nt):
        a = targets[ti]
        for c in range(k):
            J[a, c] = (J[a, c] + row_s[c]) % 8
    for ti in range(nt):
        a = targets[ti]
        for c in range(k):
            J[c, a] = (J[c, a] + col_s[c]) % 8
    for ti in range(nt):
        a = targets[ti]
        for tj in range(nt):
            J[a, targets[tj]] = (J[a, targets[tj]] + jss) % 8


@njit(cache=True)
def _swap(D, J, i, j, k):
    if i == j:
        return
    t = D[i]; D[i] = D[j]; D[j] = t
    for c in range(k):
        t = J[i, c]; J[i, c] = J[j, c]; J[j, c] = t
    for c in range(k):
        t = J[c, i]; J[c, i] = J[c, j]; J[c, j] = t


@njit(cache=True)
def _shift(Q, D, J, ypos, k):
    """h <- h (+) g_ypos.  Eq(52,53) for a single-basis-vector shift."""
    Qn = (Q + D[ypos]) % 8
    for a in range(k):
        D[a] = (D[a] + J[a, ypos]) % 8
    return Qn


@njit(cache=True)
def _shrink(k, n, W, h, G, Gbar, D, J, Q, xi, alpha, buf):
    """Returns (status, k, Q). Modifies h/G/Gbar/D/J in place."""
    nt = 0
    for a in range(k):
        if _parity_and(xi, G[a], W) == 1:
            buf[nt] = a
            nt += 1
    beta = (_parity_and(xi, h, W) ^ alpha) & 1
    if nt == 0:
        if beta == 1:
            return EMPTY, k, Q
        return SAME, k, Q

    i = buf[0]
    # targets = buf[1:nt]
    for ti in range(1, nt):
        a = buf[ti]
        for w in range(W):
            G[a, w] ^= G[i, w]
    _addrow(D, J, buf[1:], nt - 1, i, k)

    for ti in range(1, nt):
        a = buf[ti]
        for w in range(W):
            Gbar[i, w] ^= Gbar[a, w]

    last = k - 1
    if i != last:
        for w in range(W):
            t = G[i, w]; G[i, w] = G[last, w]; G[last, w] = t
            t = Gbar[i, w]; Gbar[i, w] = Gbar[last, w]; Gbar[last, w] = t
        _swap(D, J, i, last, k)

    if beta == 1:
        for w in range(W):
            h[w] ^= G[last, w]
        Q = _shift(Q, D, J, last, k)

    return SUCCESS, k - 1, Q


@njit(cache=True)
def _exponential_sum(Q, D, J, k, ebuf, tbuf):
    """Returns (eps, p, m). D/J are scratch copies owned by the caller."""
    s = -1
    ns = 0
    for a in range(k):
        if D[a] == 2 or D[a] == 6:
            if s < 0:
                s = a
            else:
                tbuf[ns] = a
                ns += 1
    if s >= 0 and ns > 0:
        _addrow(D, J, tbuf, ns, s, k)

    ne = 0
    for a in range(k):
        if a != s:
            ebuf[ne] = a
            ne += 1

    mono = np.zeros(k, dtype=np.int64)
    nmono = 0
    dim_a = np.empty(k, dtype=np.int64)
    dim_b = np.empty(k, dtype=np.int64)
    ndim = 0

    while ne > 0:
        a = ebuf[0]
        b = -1
        for ei in range(1, ne):
            if J[a, ebuf[ei]] == 4:
                b = ebuf[ei]
                break
        if b < 0:
            mono[nmono] = a
            nmono += 1
            for ei in range(1, ne):
                ebuf[ei - 1] = ebuf[ei]
            ne -= 1
        else:
            nt = 0
            for ei in range(ne):
                c = ebuf[ei]
                if c != a and c != b and J[a, c] == 4:
                    tbuf[nt] = c
                    nt += 1
            if nt > 0:
                _addrow(D, J, tbuf, nt, b, k)
            nt = 0
            for ei in range(ne):
                c = ebuf[ei]
                if c != a and c != b and J[b, c] == 4:
                    tbuf[nt] = c
                    nt += 1
            if nt > 0:
                _addrow(D, J, tbuf, nt, a, k)
            dim_a[ndim] = a
            dim_b[ndim] = b
            ndim += 1
            nn = 0
            for ei in range(ne):
                c = ebuf[ei]
                if c != a and c != b:
                    ebuf[nn] = c
                    nn += 1
            ne = nn

    W = 0.0 + 0.0j
    sig_hi = 1 if s >= 0 else 0
    for sigma in range(sig_hi + 1):
        ph = Q
        if s >= 0:
            ph += sigma * D[s]
        val = np.exp(1j * np.pi * (ph % 8) / 4.0)
        for mi in range(nmono):
            c = mono[mi]
            js = J[c, s] if s >= 0 else 0
            val *= 1.0 + np.exp(1j * np.pi * ((D[c] + sigma * js) % 8) / 4.0)
        for di in range(ndim):
            a = dim_a[di]; b = dim_b[di]
            jas = J[a, s] if s >= 0 else 0
            jbs = J[b, s] if s >= 0 else 0
            ea = np.exp(1j * np.pi * ((jas * sigma + D[a]) % 8) / 4.0)
            eb = np.exp(1j * np.pi * ((jbs * sigma + D[b]) % 8) / 4.0)
            eab = np.exp(1j * np.pi * ((jas * sigma + jbs * sigma + D[a] + D[b]) % 8) / 4.0)
            val *= 1.0 + ea + eb - eab
        W += val

    aw = abs(W)
    if aw < 1e-9:
        return 0, 0, 0
    p = int(round(np.log2(aw) * 2))
    m = int(round(np.angle(W) / (np.pi / 4.0))) % 8
    return 1, p, m


@njit(cache=True)
def inner_product_njit(n, W_, k1, h1, G1, Gb1, Q1, D1, J1,
                       k2, h2, G2, Gb2, Q2, D2, J2):
    """<phi2|phi1> as (eps, p, m). Fully compiled: no numpy dispatch on this path."""
    # working copy of state 1
    hh = h1.copy(); GG = G1.copy(); GB = Gb1.copy()
    DD = D1.copy(); JJ = J1.copy(); QQ = Q1
    k = k1
    buf = np.empty(n + 1, dtype=np.int64)

    for b in range(k2, n):
        alpha = _parity_and(Gb2[b], h2, W_)
        st, k, QQ = _shrink(k, n, W_, hh, GG, GB, DD, JJ, QQ, Gb2[b], alpha, buf)
        if st == EMPTY:
            return 0, 0, 0

    # y = coords of h (+) h2 in K2's dual basis;  R[a,b] = (g_a, gbar2_b)
    hx = np.empty(W_, dtype=np.uint64)
    for w in range(W_):
        hx[w] = hh[w] ^ h2[w]

    D2w = D2.copy(); J2w = J2.copy(); Q2w = Q2
    for a in range(k2):
        if _parity_and(hx, Gb2[a], W_) == 1:
            Q2w = (Q2w + D2w[a]) % 8
            for c in range(k2):
                D2w[c] = (D2w[c] + J2w[c, a]) % 8

    # apply R (rectangular k x k2) to (D2w, J2w) -> Eq(49,50)
    Rm = np.zeros((k, k2), dtype=np.int64)
    for a in range(k):
        for b in range(k2):
            Rm[a, b] = _parity_and(GG[a], Gb2[b], W_)

    Dn = np.zeros(k, dtype=np.int64)
    for a in range(k):
        acc = 0
        for b in range(k2):
            if Rm[a, b]:
                acc += D2w[b]
        for b in range(k2):
            if Rm[a, b]:
                for c in range(b + 1, k2):
                    if Rm[a, c]:
                        acc += J2w[b, c]
        Dn[a] = acc % 8
    # Jn = Rm J2w Rm^T.  Written as ONE matrix product at a time: the direct four-loop form
    # is O(k^2 k2^2) = O(t^4), which is a factor of t above the O(t^3) the paper specifies and
    # was measured as t^3.72 scaling at C5021 (3.59 -> 5.92 ns/t^3-unit from t=40 to t=80).
    # Same defect class as the dense-vs-sparse add-row found at C5020: an ALGORITHMIC error
    # that compilation, vectorisation and parallelism all faithfully preserve.
    Tm = np.zeros((k2, k), dtype=np.int64)                 # Tm = J2w Rm^T   (k2 x k)
    for a in range(k):
        for v in range(k2):
            if Rm[a, v]:
                for u in range(k2):
                    Tm[u, a] += J2w[u, v]
    Jn = np.zeros((k, k), dtype=np.int64)                  # Jn = Rm Tm      (k x k)
    for a in range(k):
        for u in range(k2):
            if Rm[a, u]:
                for b in range(k):
                    Jn[a, b] += Tm[u, b]
    for a in range(k):
        for b in range(k):
            Jn[a, b] = Jn[a, b] % 8

    Qd = (QQ - Q2w) % 8
    Dd = np.empty(k, dtype=np.int64)
    for a in range(k):
        Dd[a] = (DD[a] - Dn[a]) % 8
    Jd = np.empty((k, k), dtype=np.int64)
    for a in range(k):
        for b in range(k):
            Jd[a, b] = (JJ[a, b] - Jn[a, b]) % 8

    ebuf = np.empty(k + 1, dtype=np.int64)
    tbuf = np.empty(k + 1, dtype=np.int64)
    eps, p, m = _exponential_sum(Qd, Dd, Jd, k, ebuf, tbuf)
    if eps == 0:
        return 0, 0, 0
    return eps, p - (k1 + k2), m
