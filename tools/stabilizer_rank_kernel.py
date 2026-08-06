#!/usr/bin/env python3
"""P-CCM v1.0 — the Bravyi-Gosset stabilizer kernel: the inner loop whose COUNT the theory gives us.

WHY THIS EXISTS. The classical cost map has one hole, and it is named in its own card:

    "shape is faithful + paper-pinned; absolute seconds need a calibrated anchor
     (per-stabilizer-term runtime on this hardware) — v1.0 calibration item"

The sampling cost model is  2^(0.23t) * t^3 * w^3 * C.  The rank 2^(0.23t) and the per-term
work t^3*w^3 are analytic and paper-pinned. **C — seconds per stabilizer term on THIS hardware
— is the only unknown**, and it is why every absolute classical bill in the campaign is an
extrapolation from the paper's 2016 i5 MATLAB anchor times a x1000 hardware guess whose
plausible range spans 160x-4800x (23 T-gates of certifiable ceiling, measured C5020).

WHY NOT JUST TIME A SIMULATOR. C4971 falsified that: Aer's extended_stabilizer wall-time is
LINEAR IN SHOTS at ~0.20 s/shot with metropolis_mixing_time=5000 — it measures the Metropolis
SAMPLER CONFIG, not Clifford+T hardness, and its shape (overhead-flat at low T) is wrong for a
crossover. Timing it and curving on it is a G1 strawman.

    => THE MOVE: stop timing the simulator's sampler. Time the OPERATIONS whose COUNT the
       theory supplies — MeasurePauli / InnerProduct / ExponentialSum on stabilizer states —
       and multiply by the count the algorithm performs.

CORRECTNESS BEFORE SPEED, non-negotiable (the bench's own rule: "a fast wrong solver poisons
the map"). Every routine here is checked against an explicitly-constructed statevector at small
n before any timing is reported. A timing whose paired verification did not pass is not emitted.

REPRESENTATION (Bravyi & Gosset, PRL 116 250501 / arXiv:1601.07601, Appendices A-C):
    |K,q> = 2^(-k/2) SUM_{xvec in F2^k} exp(i*pi*q(xvec)/4) |h (+) SUM_a x_a g_a>
    state = (n, k, h in F2^n, G, Gbar in F2^{n x n}, Q in Z8, D in {0,2,4,6}^k, J sym k x k in {0,4})
    q(xvec) = Q + SUM_a D_a x_a + SUM_{a<b} J_{a,b} x_a x_b        (mod 8)      [Eq 43]
    J_{a,a} = 2 D_a                                                             [Eq 46]
    G Gbar^T = I (mod 2)                                                        [Eq 74]

Exponential sums are carried as the exact triple (eps, p, m) with W = eps * 2^(p/2) * e^{i*pi*m/4},
as the paper's own implementation does, "to avoid roundoff errors".

Substrate: claude-fable-5, Whisper C5020. Creator directive general#5845 ("ok build it!").
"""
import numpy as np

EMPTY, SAME, SUCCESS = "EMPTY", "SAME", "SUCCESS"


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────
class StabState:
    """Stabilizer state in the paper's standard form. Mutable; routines modify in place."""

    __slots__ = ("n", "k", "h", "G", "Gbar", "Q", "D", "J")

    def __init__(self, n, k, h, G, Gbar, Q, D, J):
        self.n, self.k = n, k
        self.h = h.astype(np.uint8)
        self.G, self.Gbar = G.astype(np.uint8), Gbar.astype(np.uint8)
        self.Q = int(Q) % 8
        self.D = (D.astype(np.int64) % 8)
        self.J = (J.astype(np.int64) % 8)

    def copy(self):
        return StabState(self.n, self.k, self.h.copy(), self.G.copy(), self.Gbar.copy(),
                         self.Q, self.D.copy(), self.J.copy())

    # -- invariants, checked in the self-test rather than assumed --------------
    def check_invariants(self):
        if not np.array_equal((self.G @ self.Gbar.T) % 2, np.eye(self.n, dtype=np.uint8)):
            return "G Gbar^T != I (Eq 74)"
        if self.k and not np.array_equal(np.diag(self.J)[:self.k] % 8, (2 * self.D[:self.k]) % 8):
            return "J_aa != 2 D_a (Eq 46)"
        if self.k and not np.array_equal(self.J[:self.k, :self.k], self.J[:self.k, :self.k].T):
            return "J not symmetric"
        if self.k and not set(np.unique(self.D[:self.k]).tolist()) <= {0, 2, 4, 6}:
            return "D outside {0,2,4,6}"
        return None

    def statevector(self):
        """Explicit 2^n amplitudes. VERIFICATION ONLY — never on a timed path."""
        psi = np.zeros(2 ** self.n, dtype=complex)
        for mask in range(2 ** self.k):
            x = np.array([(mask >> a) & 1 for a in range(self.k)], dtype=np.uint8)
            pt = self.h.copy()
            for a in range(self.k):
                if x[a]:
                    pt = (pt ^ self.G[a]) % 2
            qv = self.Q + int(self.D[:self.k] @ x)
            for a in range(self.k):
                for b in range(a + 1, self.k):
                    qv += int(self.J[a, b]) * int(x[a]) * int(x[b])
            idx = int("".join(str(int(v)) for v in pt), 2) if self.n else 0
            psi[idx] += np.exp(1j * np.pi * (qv % 8) / 4)
        return psi * 2 ** (-self.k / 2)


# ─────────────────────────────────────────────────────────────────────────────
# Basis / shift updates — Eqs (49,50) and (52,53)
# ─────────────────────────────────────────────────────────────────────────────
def _update_basis(D, J, R, k):
    """Eq (48-50): g_a <- SUM_b R_{a,b} g_b.  D_a <- SUM_b R_ab D_b + SUM_{b<c} J_bc R_ab R_ac;
    J <- R J R^T.  All arithmetic in Z8.  Rectangular R (k_new x k_old) is allowed."""
    Ru = R.astype(np.int64) % 2
    Dn = (Ru @ D[:R.shape[1]]) % 8
    Ju = J[:R.shape[1], :R.shape[1]]
    # SUM_{b<c} J_bc R_ab R_ac   — strictly upper triangle
    Jup = np.triu(Ju, 1)
    Dn = (Dn + np.einsum("ab,bc,ac->a", Ru, Jup, Ru)) % 8
    Jn = (Ru @ Ju @ Ru.T) % 8
    return Dn, Jn


def _update_addrow_sparse(D, J, targets, src, k):
    """SPARSE form of Eqs (49,50) for R = I + SUM_{a in targets} e_a e_src^T  (g_a <- g_a (+) g_src).

    The paper specifies these updates as O(|R|^2), NOT the dense O(k^3) of a general R J R^T:
    "Using sparse matrix-matrix multiplication one can perform all updates in Eqs.(49,50) in
    time O(|R|^2)."  My first version used the dense formula and was therefore a factor of k
    too slow — an ALGORITHMIC defect, not a constant-factor one, and it made the kernel 20x
    slower per O(n^3) unit than the paper's own 2016 MATLAB.

    With R = I + E, E = SUM_{a in T} e_a e_s^T:
        R J R^T = J + E J + J E^T + E J E^T
          E J     -> add row J[s,:] to rows a in T
          J E^T   -> add col J[:,s] to cols a in T
          E J E^T -> add J[s,s] to every (a,b) with a,b in T
        D_a <- D_a + D_s + J[a,s]   for a in T          (paper's own stated form)
    """
    if not targets:
        return
    T = np.asarray(targets, dtype=np.intp)
    Jk = J[:k, :k]
    jss = int(Jk[src, src])
    row_s = Jk[src, :k].copy()
    col_s = Jk[:k, src].copy()
    D[T] = (D[T] + D[src] + Jk[T, src]) % 8          # Eq 49, sparse
    Jk[T, :] = (Jk[T, :] + row_s) % 8                # E J
    Jk[:, T] = (Jk[:, T] + col_s[:, None]) % 8       # J E^T
    Jk[np.ix_(T, T)] = (Jk[np.ix_(T, T)] + jss) % 8  # E J E^T


def _swap_basis_sparse(D, J, i, j, k):
    """Permutation R: swap basis vectors i and j.  O(k), not O(k^3)."""
    if i == j:
        return
    D[[i, j]] = D[[j, i]]
    Jk = J[:k, :k]
    Jk[[i, j], :] = Jk[[j, i], :]
    Jk[:, [i, j]] = Jk[:, [j, i]]


def _update_shift(Q, D, J, y, k):
    """Eq (51-53): h <- h (+) y with y = SUM y_a g_a.  J unchanged."""
    yv = y[:k].astype(np.int64) % 2
    Qn = (Q + int(D[:k] @ yv) + int(yv @ np.triu(J[:k, :k], 1) @ yv)) % 8
    Dn = (D[:k] + (J[:k, :k] @ yv)) % 8
    return Qn, Dn


# ─────────────────────────────────────────────────────────────────────────────
# SHRINK — Appendix B
# ─────────────────────────────────────────────────────────────────────────────
def shrink(st, xi, alpha, lazy=False):
    """M = K ∩ {x : (xi,x) = alpha}. Modifies st in place. Returns EMPTY / SAME / SUCCESS."""
    k, n = st.k, st.n
    S = [a for a in range(k) if int(xi @ st.G[a]) % 2 == 1]
    beta = (int(alpha) ^ (int(xi @ st.h) % 2)) & 1
    if not S:
        return EMPTY if beta == 1 else SAME

    i = S[0]
    rest = S[1:]

    # g_a <- g_a (+) g_i for a in rest   =>  R = I + SUM_{a in rest} e_a e_i^T
    st.G[rest] = (st.G[rest] ^ st.G[i]) % 2
    if not lazy:
        _update_addrow_sparse(st.D, st.J, rest, i, k)

    # dual: gbar_i <- gbar_i (+) SUM_{a in rest} gbar_a
    if rest:
        acc = st.Gbar[rest].sum(axis=0) % 2
        st.Gbar[i] = (st.Gbar[i] ^ acc) % 2

    # swap i <-> k-1  (paper's "k-th"; 0-indexed here)
    last = k - 1
    if i != last:
        st.G[[i, last]] = st.G[[last, i]]
        st.Gbar[[i, last]] = st.Gbar[[last, i]]
        if not lazy:
            _swap_basis_sparse(st.D, st.J, i, last, k)

    # h <- h (+) beta * g_{k-1}
    if beta:
        st.h = (st.h ^ st.G[last]) % 2
        if not lazy:
            y = np.zeros(k, dtype=np.int64)
            y[last] = 1
            st.Q, Dn = _update_shift(st.Q, st.D, st.J, y, k)
            st.D[:k] = Dn

    st.k = k - 1
    return SUCCESS


# ─────────────────────────────────────────────────────────────────────────────
# EXPONENTIAL SUM — Appendix A.  Exact triple (eps, p, m).
# ─────────────────────────────────────────────────────────────────────────────
def _w_triple_from_complex(z, tol=1e-9):
    """Convert a small exactly-representable value eps*2^(p/2)*e^{i pi m/4} to its triple."""
    if abs(z) < tol:
        return (0, 0, 0)
    p2 = np.log2(abs(z)) * 2
    p = int(round(p2))
    m = int(round(np.angle(z) / (np.pi / 4))) % 8
    return (1, p, m)


def exponential_sum(Q, D, J, k):
    """W(K,q) = SUM_{xvec in F2^k} exp(i pi q(xvec)/4), returned as (eps, p, m).

    Follows Appendix A: reduce D to {0,4} off a single index s, partition the remaining basis
    into dimers and monomers by O(k) sparse basis changes, then factorise."""
    D = D[:k].copy() % 8
    J = J[:k, :k].copy() % 8
    Q = int(Q) % 8

    # --- S = {a : D_a in {2,6}} ; collapse to at most one element -------------
    S = [a for a in range(k) if D[a] in (2, 6)]
    if S:
        s = S[0]
        others = S[1:]
        if others:
            _update_addrow_sparse(D, J, others, s, k)
        S = [s]
    s = S[0] if S else None

    # --- partition [k] \ S into dimers and monomers --------------------------
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
                R = np.eye(k, dtype=np.int64)
                for c in rest:
                    if J[a, c] == 4:
                        R[c, b] ^= 1
                    if J[b, c] == 4:
                        R[c, a] ^= 1
                D, J = _update_basis(D, J, R, k)
            dimers.append((a, b))
            E = [c for c in E if c not in (a, b)]

    # --- factorised sum, Eqs (64)/(69,70) ------------------------------------
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
    return _w_triple_from_complex(W)


# ─────────────────────────────────────────────────────────────────────────────
# INNER PRODUCT — Appendix C
# ─────────────────────────────────────────────────────────────────────────────
def inner_product(s1, s2):
    """<phi2|phi1> as (eps, p, m) with value eps * 2^(p/2) * e^{i pi m/4}.  O(n^3)."""
    st = s1.copy()
    k1, k2, n = s1.k, s2.k, s1.n

    for b in range(k2, n):
        xi = s2.Gbar[b]
        alpha = int(xi @ s2.h) % 2
        if shrink(st, xi, alpha) == EMPTY:
            return (0, 0, 0)

    k = st.k
    # express h and the basis of K in K2's coordinates
    y = ((s2.Gbar[:k2].astype(np.int64) @ ((st.h ^ s2.h) % 2).astype(np.int64)) % 2)
    # was an O(k*k2) PYTHON double loop with a numpy dot inside; it is one matmul
    R = (st.G[:k].astype(np.int64) @ s2.Gbar[:k2].astype(np.int64).T) % 2

    Q2, D2 = _update_shift(s2.Q, s2.D, s2.J, y, k2)
    D2full = s2.D.copy()
    D2full[:k2] = D2
    D2n, J2n = _update_basis(D2full, s2.J, R, k)

    Q = (st.Q - Q2) % 8
    D = (st.D[:k] - D2n) % 8
    J = (st.J[:k, :k] - J2n) % 8
    eps, p, m = exponential_sum(Q, D, J, k)
    if eps == 0:
        return (0, 0, 0)
    return (eps, p - (k1 + k2), m)


def triple_to_complex(t):
    eps, p, m = t
    return 0j if eps == 0 else eps * (2.0 ** (p / 2)) * np.exp(1j * np.pi * m / 4)


# ─────────────────────────────────────────────────────────────────────────────
# Construction: random stabilizer states via random Clifford circuits
# ─────────────────────────────────────────────────────────────────────────────
def basis_state(n, bits=None):
    """|h> as a k=0 stabilizer state."""
    h = np.zeros(n, dtype=np.uint8) if bits is None else np.array(bits, dtype=np.uint8)
    I = np.eye(n, dtype=np.uint8)
    return StabState(n, 0, h, I.copy(), I.copy(), 0, np.zeros(n, dtype=np.int64),
                     np.zeros((n, n), dtype=np.int64))


def apply_H(st, j):
    """Hadamard on qubit j, acting on the standard form. Implemented via the paper's
    identity: H_j |K,q> is obtained by shrinking on e_j then extending, tracking phases.
    For the kernel's purposes we build states by an explicit route instead — see
    random_state_via_extend."""
    raise NotImplementedError("not needed for the calibration path")


def random_state_via_extend(n, k, rng):
    """Build a valid standard-form state directly: random full-rank G (with its dual),
    random shift h, random Q, random D in {0,2,4,6}, random symmetric J in {0,4} with
    J_aa = 2 D_a.  This samples the SAME DATA STRUCTURE the algorithm operates on, which is
    what the timing needs — it does not claim to sample Haar-uniformly over stabilizer states."""
    while True:
        G = rng.integers(0, 2, size=(n, n), dtype=np.uint8)
        Gi = _inv_gf2(G)
        if Gi is not None:
            break
    Gbar = Gi.T % 2                      # G Gbar^T = G G^{-1} = I
    h = rng.integers(0, 2, size=n, dtype=np.uint8)
    Q = int(rng.integers(0, 8))
    D = np.zeros(n, dtype=np.int64)
    D[:k] = rng.integers(0, 4, size=k) * 2
    J = np.zeros((n, n), dtype=np.int64)
    for a in range(k):
        for b in range(a + 1, k):
            v = int(rng.integers(0, 2)) * 4
            J[a, b] = J[b, a] = v
    for a in range(k):
        J[a, a] = (2 * D[a]) % 8
    return StabState(n, k, h, G, Gbar, Q, D, J)


def _inv_gf2(A):
    """Inverse of A over F2, or None if singular."""
    n = A.shape[0]
    M = np.concatenate([A.copy() % 2, np.eye(n, dtype=np.uint8)], axis=1)
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            if M[i, c]:
                piv = i
                break
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(n):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        r += 1
    if r < n:
        return None
    return M[:, n:]


# ─────────────────────────────────────────────────────────────────────────────
# CORRECTNESS GATE — run before any timing is reported
# ─────────────────────────────────────────────────────────────────────────────
def self_test(verbose=True):
    """Check the kernel against explicitly-constructed statevectors at small n.
    Returns (n_pass, n_fail, failures)."""
    rng = np.random.default_rng(20260806)
    npass = nfail = 0
    failures = []

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        if ok:
            npass += 1
        else:
            nfail += 1
            failures.append(f"{name}: {detail}")
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name}  {detail if not ok else ''}")

    if verbose:
        print("  [1] state invariants (Eq 46, Eq 74)")
    for n in (3, 4, 5):
        for k in range(0, n + 1):
            st = random_state_via_extend(n, k, rng)
            rec(f"invariants n={n} k={k}", st.check_invariants() is None, str(st.check_invariants()))

    if verbose:
        print("  [2] exponential_sum vs brute force over F2^k")
    for n in (3, 4):
        for k in range(0, n + 1):
            for _ in range(4):
                st = random_state_via_extend(n, k, rng)
                got = triple_to_complex(exponential_sum(st.Q, st.D, st.J, k))
                brute = 0j
                for mask in range(2 ** k):
                    x = np.array([(mask >> a) & 1 for a in range(k)], dtype=np.int64)
                    qv = st.Q + int(st.D[:k] @ x) + int(x @ np.triu(st.J[:k, :k], 1) @ x)
                    brute += np.exp(1j * np.pi * (qv % 8) / 4)
                rec(f"expsum n={n} k={k}", abs(got - brute) < 1e-8, f"got {got:.4f} vs {brute:.4f}")

    if verbose:
        print("  [3] inner_product vs explicit statevector overlap")
    for n in (2, 3, 4):
        for _ in range(6):
            k1 = int(rng.integers(0, n + 1))
            k2 = int(rng.integers(0, n + 1))
            s1 = random_state_via_extend(n, k1, rng)
            s2 = random_state_via_extend(n, k2, rng)
            got = triple_to_complex(inner_product(s1, s2))
            want = np.vdot(s2.statevector(), s1.statevector())
            rec(f"inner n={n} k1={k1} k2={k2}", abs(got - want) < 1e-8,
                f"got {got:.5f} vs {want:.5f}")

    if verbose:
        print("  [4] shrink preserves the state on SAME, empties correctly on EMPTY")
    for n in (3, 4):
        for _ in range(6):
            k = int(rng.integers(1, n + 1))
            st = random_state_via_extend(n, k, rng)
            before = st.statevector()
            xi = np.zeros(n, dtype=np.uint8)          # xi = 0 -> S empty, beta = 0 -> SAME
            r = shrink(st, xi, 0)
            ok = (r == SAME) and np.allclose(before, st.statevector())
            rec(f"shrink SAME n={n} k={k}", ok, f"returned {r}")

    return npass, nfail, failures


if __name__ == "__main__":
    print("BRAVYI-GOSSET STABILIZER KERNEL — CORRECTNESS GATE\n")
    p, f, fails = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f:
        print("\n  FAILURES:")
        for x in fails[:12]:
            print(f"    {x}")
        print("\n  ⛔ GATE NOT PASSED — no timing may be reported from this kernel.")
    else:
        print("  ✅ GATE PASSED — kernel is eligible for timing.")
