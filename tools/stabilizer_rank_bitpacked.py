#!/usr/bin/env python3
"""P-CCM v1.0 — BIT-PACKED F2 kernel. The measurement that settles the x1000 hardware factor.

WHY. The HSS campaign's classical band assumes a x1000 speedup over the paper's 2016 i5 MATLAB.
The reference kernel (stabilizer_rank_kernel.py) measured 2.36x SLOWER per O(n^3) unit than that
laptop — so nothing supported the x1000, and the only way to settle it is to write the
implementation the assumption was betting on and time it.

THE ALGORITHM'S NATURAL DATATYPE IS GF(2), AND THAT IS WHERE THE HEADROOM IS. MATLAB and numpy
both store a bit in a byte (or worse, a double). A uint64 holds 64. F2 inner products become
popcount(a & b) & 1, and row operations become word XORs — 64 bits per instruction rather than
one. This module packs G, Gbar and h into uint64 words and leaves the Z8 data (Q, D, J) as
integer arrays, because Z8 arithmetic is not F2 work and packing does not apply to it.

PROFILE THAT MOTIVATED IT (measured, after the sparse-update fix, n=100):
    shrink                  0.017 s tottime   <- top cost; its hot line is
                                                 [a for a in range(k) if (xi . G[a]) % 2]
                                                 i.e. k numpy calls inside a Python loop
    _update_addrow_sparse   0.011 s
    _update_basis           0.010 s
The S-computation in shrink is O(k) numpy calls; packed, it is ONE vectorised parity over words.

VERIFICATION IS TWO-LEVEL AND NON-NEGOTIABLE. The reference kernel is already gated 81/81 against
explicit 2^n statevector overlaps. This module must reproduce the REFERENCE exactly — same
inner-product triples on the same inputs — so a bug here cannot hide behind "the fast one is
probably right". A timing whose paired agreement check did not pass is not emitted.

Substrate: claude-fable-5, Whisper C5020. Creator directive: "build the bit-packed version".
"""
import numpy as np

EMPTY, SAME, SUCCESS = "EMPTY", "SAME", "SUCCESS"
WBITS = 64


# ─────────────────────────────────────────────────────────────────────────────
# packing helpers
# ─────────────────────────────────────────────────────────────────────────────
def nwords(n):
    return (n + WBITS - 1) // WBITS


def pack_rows(M):
    """(r, n) uint8 bit matrix -> (r, W) uint64 packed, LSB-first within each word."""
    M = np.ascontiguousarray(M.astype(np.uint8))
    r, n = M.shape
    W = nwords(n)
    out = np.zeros((r, W), dtype=np.uint64)
    for b in range(n):
        w, sh = divmod(b, WBITS)
        out[:, w] |= (M[:, b].astype(np.uint64) << np.uint64(sh))
    return out


def unpack_rows(P, n):
    """(r, W) uint64 -> (r, n) uint8."""
    r = P.shape[0]
    out = np.zeros((r, n), dtype=np.uint8)
    for b in range(n):
        w, sh = divmod(b, WBITS)
        out[:, b] = ((P[:, w] >> np.uint64(sh)) & np.uint64(1)).astype(np.uint8)
    return out


def f2_dot_row_many(v, P):
    """(ξ, g_a) for every row a of P, at once.  parity(popcount(v & P[a])).
    ONE vectorised call replacing the reference kernel's k separate numpy dots."""
    return (np.bitwise_count(P & v).sum(axis=1) & 1).astype(np.int64)


def f2_matmul(A, B):
    """A (ra,W) x B (rb,W) -> (ra,rb) over F2: C[i,j] = parity(popcount(A[i] & B[j]))."""
    return (np.bitwise_count(A[:, None, :] & B[None, :, :]).sum(axis=2) & 1).astype(np.int64)


# ─────────────────────────────────────────────────────────────────────────────
# State — F2 data packed, Z8 data plain
# ─────────────────────────────────────────────────────────────────────────────
class PackedState:
    __slots__ = ("n", "k", "W", "h", "G", "Gbar", "Q", "D", "J")

    def __init__(self, n, k, h_packed, G_packed, Gbar_packed, Q, D, J):
        self.n, self.k, self.W = n, k, nwords(n)
        self.h = h_packed.astype(np.uint64)
        self.G = G_packed.astype(np.uint64)
        self.Gbar = Gbar_packed.astype(np.uint64)
        self.Q = int(Q) % 8
        self.D = D.astype(np.int64) % 8
        self.J = J.astype(np.int64) % 8

    @classmethod
    def from_reference(cls, st):
        return cls(st.n, st.k, pack_rows(st.h[None, :])[0], pack_rows(st.G),
                   pack_rows(st.Gbar), st.Q, st.D.copy(), st.J.copy())

    def copy(self):
        return PackedState(self.n, self.k, self.h.copy(), self.G.copy(), self.Gbar.copy(),
                           self.Q, self.D.copy(), self.J.copy())


# ─────────────────────────────────────────────────────────────────────────────
# Z8 updates — identical maths to the reference, kept side by side deliberately
# ─────────────────────────────────────────────────────────────────────────────
def _update_addrow_sparse(D, J, targets, src, k):
    if len(targets) == 0:
        return
    T = np.asarray(targets, dtype=np.intp)
    Jk = J[:k, :k]
    jss = int(Jk[src, src])
    row_s = Jk[src, :k].copy()
    col_s = Jk[:k, src].copy()
    D[T] = (D[T] + D[src] + Jk[T, src]) % 8
    Jk[T, :] = (Jk[T, :] + row_s) % 8
    Jk[:, T] = (Jk[:, T] + col_s[:, None]) % 8
    Jk[np.ix_(T, T)] = (Jk[np.ix_(T, T)] + jss) % 8


def _swap_basis_sparse(D, J, i, j, k):
    if i == j:
        return
    D[[i, j]] = D[[j, i]]
    Jk = J[:k, :k]
    Jk[[i, j], :] = Jk[[j, i], :]
    Jk[:, [i, j]] = Jk[:, [j, i]]


def _update_basis(D, J, R, k):
    Ru = R.astype(np.int64) % 2
    Dn = (Ru @ D[:R.shape[1]]) % 8
    Ju = J[:R.shape[1], :R.shape[1]]
    Dn = (Dn + np.einsum("ab,bc,ac->a", Ru, np.triu(Ju, 1), Ru)) % 8
    return Dn, (Ru @ Ju @ Ru.T) % 8


def _update_shift(Q, D, J, y, k):
    yv = y[:k].astype(np.int64) % 2
    Qn = (Q + int(D[:k] @ yv) + int(yv @ np.triu(J[:k, :k], 1) @ yv)) % 8
    return Qn, (D[:k] + (J[:k, :k] @ yv)) % 8


# ─────────────────────────────────────────────────────────────────────────────
# SHRINK — packed
# ─────────────────────────────────────────────────────────────────────────────
def shrink(st, xi_packed, alpha):
    k = st.k
    # THE LINE THIS MODULE EXISTS FOR: one vectorised parity over packed words,
    # replacing k separate numpy dot calls in a Python loop.
    par = f2_dot_row_many(xi_packed, st.G[:k]) if k else np.zeros(0, dtype=np.int64)
    S = np.nonzero(par)[0]
    beta = int(np.bitwise_count(xi_packed & st.h).sum() & 1) ^ int(alpha) & 1
    if S.size == 0:
        return EMPTY if beta == 1 else SAME

    i = int(S[0])
    rest = S[1:]

    st.G[rest] ^= st.G[i]                       # word XOR: 64 bits per operation
    _update_addrow_sparse(st.D, st.J, rest, i, k)

    if rest.size:
        acc = np.bitwise_xor.reduce(st.Gbar[rest], axis=0)
        st.Gbar[i] ^= acc

    last = k - 1
    if i != last:
        st.G[[i, last]] = st.G[[last, i]]
        st.Gbar[[i, last]] = st.Gbar[[last, i]]
        _swap_basis_sparse(st.D, st.J, i, last, k)

    if beta:
        st.h ^= st.G[last]
        y = np.zeros(k, dtype=np.int64)
        y[last] = 1
        st.Q, Dn = _update_shift(st.Q, st.D, st.J, y, k)
        st.D[:k] = Dn

    st.k = k - 1
    return SUCCESS


# ─────────────────────────────────────────────────────────────────────────────
# EXPONENTIAL SUM — Z8 only, no F2 work; shares the reference's logic
# ─────────────────────────────────────────────────────────────────────────────
def _w_triple(z, tol=1e-9):
    if abs(z) < tol:
        return (0, 0, 0)
    return (1, int(round(np.log2(abs(z)) * 2)), int(round(np.angle(z) / (np.pi / 4))) % 8)


def exponential_sum(Q, D, J, k):
    D = D[:k].copy() % 8
    J = J[:k, :k].copy() % 8
    Q = int(Q) % 8
    S = [a for a in range(k) if D[a] in (2, 6)]
    if S:
        s = S[0]
        others = S[1:]
        if others:
            _update_addrow_sparse(D, J, others, s, k)
        S = [s]
    s = S[0] if S else None

    E = [a for a in range(k) if a != s]
    M, dimers = [], []
    while E:
        a = E[0]
        Ka = [b for b in E[1:] if J[a, b] == 4]
        if not Ka:
            M.append(a)
            E.remove(a)
        else:
            b = Ka[0]
            rest = [c for c in E if c not in (a, b)]
            if rest:
                # SPARSE dimer update (Eq 73). The paper: "the R matrices corresponding to the
                # basis change Eq.(73) are sparse since any row of R contains at most three
                # non-zero elements." R = I + E_b + E_a with E_b = SUM_{c in Tb} e_c e_b^T and
                # E_a = SUM_{c in Ta} e_c e_a^T.  These compose SEQUENTIALLY without error
                # because E_a E_b = 0: it would need a in Tb, and Tb excludes a by construction.
                # I fixed this in shrink and left the dense form here — it then became the top
                # cost once the F2 layer was packed.
                Tb = [c for c in rest if J[a, c] == 4]
                Ta = [c for c in rest if J[b, c] == 4]
                _update_addrow_sparse(D, J, Tb, b, k)
                _update_addrow_sparse(D, J, Ta, a, k)
            dimers.append((a, b))
            E = [c for c in E if c not in (a, b)]

    def W_sigma(sigma):
        val = np.exp(1j * np.pi * ((Q + (sigma * D[s] if s is not None else 0)) % 8) / 4)
        for c in M:
            js = int(J[c, s]) if s is not None else 0
            val *= 1 + np.exp(1j * np.pi * ((D[c] + sigma * js) % 8) / 4)
        for (a, b) in dimers:
            jas = int(J[a, s]) if s is not None else 0
            jbs = int(J[b, s]) if s is not None else 0
            ea = np.exp(1j * np.pi * ((jas * sigma + D[a]) % 8) / 4)
            eb = np.exp(1j * np.pi * ((jbs * sigma + D[b]) % 8) / 4)
            eab = np.exp(1j * np.pi * ((jas * sigma + jbs * sigma + D[a] + D[b]) % 8) / 4)
            val *= 1 + ea + eb - eab
        return val

    W = W_sigma(0) if s is None else W_sigma(0) + W_sigma(1)
    return _w_triple(W)


# ─────────────────────────────────────────────────────────────────────────────
# INNER PRODUCT — packed
# ─────────────────────────────────────────────────────────────────────────────
def inner_product(s1, s2):
    st = s1.copy()
    k1, k2, n = s1.k, s2.k, s1.n

    for b in range(k2, n):
        xi = s2.Gbar[b]
        alpha = int(np.bitwise_count(xi & s2.h).sum() & 1)
        if shrink(st, xi, alpha) == EMPTY:
            return (0, 0, 0)

    k = st.k
    hx = st.h ^ s2.h
    y = f2_dot_row_many(hx, s2.Gbar[:k2]) if k2 else np.zeros(0, dtype=np.int64)
    R = f2_matmul(st.G[:k], s2.Gbar[:k2]) if (k and k2) else np.zeros((k, k2), dtype=np.int64)

    Q2, D2 = _update_shift(s2.Q, s2.D, s2.J, y, k2) if k2 else (s2.Q, s2.D[:0])
    D2full = s2.D.copy()
    if k2:
        D2full[:k2] = D2
    D2n, J2n = _update_basis(D2full, s2.J, R, k) if k else (np.zeros(0, dtype=np.int64),
                                                            np.zeros((0, 0), dtype=np.int64))
    Q = (st.Q - Q2) % 8
    D = (st.D[:k] - D2n) % 8
    J = (st.J[:k, :k] - J2n) % 8
    eps, p, m = exponential_sum(Q, D, J, k)
    if eps == 0:
        return (0, 0, 0)
    return (eps, p - (k1 + k2), m)


# ─────────────────────────────────────────────────────────────────────────────
# TWO-LEVEL VERIFICATION: packed must reproduce the already-gated reference
# ─────────────────────────────────────────────────────────────────────────────
def cross_check(trials=40, verbose=True):
    import stabilizer_rank_kernel as ref
    rng = np.random.default_rng(20260807)
    npass = nfail = 0
    fails = []
    for _ in range(trials):
        n = int(rng.integers(2, 9))
        k1 = int(rng.integers(0, n + 1))
        k2 = int(rng.integers(0, n + 1))
        r1 = ref.random_state_via_extend(n, k1, rng)
        r2 = ref.random_state_via_extend(n, k2, rng)
        want = ref.inner_product(r1, r2)
        got = inner_product(PackedState.from_reference(r1), PackedState.from_reference(r2))
        if want == got:
            npass += 1
        else:
            nfail += 1
            fails.append(f"n={n} k1={k1} k2={k2}: ref {want} vs packed {got}")
    if verbose:
        print(f"    {npass} agree, {nfail} disagree (vs the 81/81-gated reference kernel)")
        for f in fails[:6]:
            print(f"      {f}")
    return npass, nfail, fails


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    print("BIT-PACKED F2 KERNEL — TWO-LEVEL VERIFICATION\n")
    print("  packed vs reference (reference itself gated 81/81 vs explicit statevectors):")
    p, f, _ = cross_check()
    print(f"\n  {'✅ AGREEMENT — eligible for timing.' if f == 0 else '⛔ DISAGREEMENT — no timing may be reported.'}")
    sys.exit(0 if f == 0 else 2)
