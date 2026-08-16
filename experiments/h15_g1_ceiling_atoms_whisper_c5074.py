#!/usr/bin/env python3
"""H15 G1 — ceiling atoms, per Elder's ruled route (coordination#12393).

Computes, at n=2,3,4 (n=4 is the flown-MICRO target):
  A1. Exact 2-copy moment operator M2 = E_A[psi_A psi_A^T (x) psi_A psi_A^T],
      TWO independent ways (brute average over ALL A; Gauss-sum quadruple
      condition) — byte-level agreement required (the ruling's brute-vs-closed
      pin, at the M2 level).
  A2. Exact single-copy mixture check: E_A[psi psi^T] == I/2^n (integer-exact).
  A3. Bell-basis diagonal of M2 -> the transversal-Bell 2-copy strategy's exact
      per-trial success (likelihood rule on Bell outcomes).
  A4. Global Helstrom on (M2, I/4^n): 1/2 + ||M2 - I/4^n||_1 / 4.
  A5. PPT-relaxed separable-measurement SDP ceiling (the ruled official ceiling,
      NUMERICAL PRIMAL ONLY here — the dual certificate is owed before freeze;
      B1 lesson: an approximate primal UNDERSTATES a max, and understating the
      classical ceiling is the dangerous direction for us).
  A6. The 4-copy symplectic-parity statistic (two Bell samples per decision):
      exact P(parity=0 | ALT) and P(parity=0 | NULL) — the A-independent
      statistic candidate for the in-circuit decision. Verified by enumeration
      at n=2,3 against the closed form.

Ensemble convention VERBATIM from exp_door_a_flight_kit_v2 (phase_state_vec):
A upper-triangular INCLUDING diagonal, n(n+1)/2 bits, exponent XOR of
A_ij x_i x_j over i<=j, qubit i = bit i of the index (little-endian).

$0. No submission path. No account import anywhere in this file.
"""
import itertools
import json
import numpy as np

RESULTS = {}


def phase_state_vec(n, A):
    v = np.empty(2 ** n)
    for k in range(2 ** n):
        x = [(k >> i) & 1 for i in range(n)]
        e = 0
        for i in range(n):
            for j in range(i, n):
                if A[i][j] and x[i] and x[j]:
                    e ^= 1
        v[k] = -1.0 if e else 1.0
    return v / np.sqrt(2 ** n)


def all_A(n):
    idx = [(i, j) for i in range(n) for j in range(i, n)]
    for bits in itertools.product([0, 1], repeat=len(idx)):
        A = [[0] * n for _ in range(n)]
        for (i, j), b in zip(idx, bits):
            A[i][j] = b
        yield A


def m2_brute(n):
    """Integer-exact accumulate: sum over all A of (psi psi^T)x(psi psi^T),
    entries are (+-1)/2^{2n} per A, so accumulate the +-1 integers."""
    d = 2 ** n
    acc = np.zeros((d * d, d * d), dtype=np.int64)
    count = 0
    for A in all_A(n):
        v = (phase_state_vec(n, A) * np.sqrt(d)).astype(np.int64)  # +-1 ints
        p1 = np.outer(v, v)
        acc += np.kron(p1, p1)
        count += 1
    return acc, count  # M2 = acc / (count * d**2)


def m2_gauss(n):
    """Quadruple condition: entry ((x,u),(y,v)) nonzero iff for all i<=j:
    x_i x_j + y_i y_j + u_i u_j + v_i v_j == 0 mod 2; then value 1/2^{2n}
    (times the fraction of A's, which is 1 when the condition holds — the
    E_A of a product of independent +-1's is the indicator). Integer form."""
    d = 2 ** n
    pairs = [(i, j) for i in range(n) for j in range(i, n)]
    bits = [[(k >> i) & 1 for i in range(n)] for k in range(d)]
    M = np.zeros((d * d, d * d), dtype=np.int64)
    for x in range(d):
        bx = bits[x]
        for y in range(d):
            by = bits[y]
            for u in range(d):
                bu = bits[u]
                for v in range(d):
                    bv = bits[v]
                    ok = True
                    for (i, j) in pairs:
                        s = (bx[i] & bx[j]) ^ (by[i] & by[j]) \
                            ^ (bu[i] & bu[j]) ^ (bv[i] & bv[j])
                        if s:
                            ok = False
                            break
                    if ok:
                        # row index = first-copy x tensor second-copy u
                        M[x * d + u, y * d + v] = 1
    return M  # M2 = M / d**2


def single_copy_check(n):
    d = 2 ** n
    acc = np.zeros((d, d), dtype=np.int64)
    count = 0
    for A in all_A(n):
        v = (phase_state_vec(n, A) * np.sqrt(d)).astype(np.int64)
        acc += np.outer(v, v)
        count += 1
    expect = np.eye(d, dtype=np.int64) * count
    return bool(np.array_equal(acc, expect)), count


def bell_basis(n):
    """Transversal Bell basis vectors on d*d, labels (a,b) in F2^n x F2^n.
    |B_ab> = (I (x) X^a Z^b) |Phi+>^{(x)n} with qubit-i pairs (i, i+n) mapped
    into the (copy1 (x) copy2) index convention row = x*d+u."""
    d = 2 ** n
    vecs = {}
    for a in range(d):
        for b in range(d):
            v = np.zeros(d * d)
            for x in range(d):
                u = x ^ a
                # phase from Z^b acting on |u>: (-1)^{b.u}
                ph = -1.0 if bin(b & u).count("1") % 2 else 1.0
                v[x * d + u] = ph
            vecs[(a, b)] = v / np.sqrt(d)
    return vecs


def bell_strategy(n, M2):
    """Exact per-trial success of the transversal-Bell measurement with
    optimal (likelihood) classical post-processing, priors 1/2."""
    d = 2 ** n
    bv = bell_basis(n)
    p_alt = {}
    for key, v in bv.items():
        p_alt[key] = float(v @ M2 @ v)
    p_null = 1.0 / (d * d)
    tv = 0.5 * sum(abs(p - p_null) for p in p_alt.values())
    return 0.5 + 0.5 * tv, p_alt


def helstrom(n, M2):
    d2 = 4 ** n
    delta = M2 - np.eye(d2) / d2
    w = np.linalg.eigvalsh(delta)
    return 0.5 + 0.25 * float(np.abs(w).sum())


def ppt_ceiling(n, M2, eps=1e-9):
    """Ruled official ceiling (PPT relaxation of separable measurements).
    max 1/2 + 1/2 Tr[E (M2 - I/d2)] s.t. 0<=E<=I, E^Tb>=0, (I-E)^Tb>=0.
    Real symmetric WLOG (both hypothesis states real, constraint set
    conjugation-invariant). PRIMAL NUMERICAL VALUE ONLY — dual owed at freeze."""
    import cvxpy as cp
    d = 2 ** n
    d2 = d * d
    delta = M2 - np.eye(d2) / d2
    E = cp.Variable((d2, d2), symmetric=True)

    def pt(X):  # partial transpose on copy 2
        return cp.reshape(
            cp.transpose(cp.reshape(X, (d, d, d, d), order="C"),
                         (0, 3, 2, 1)),
            (d2, d2), order="C")

    cons = [E >> 0, np.eye(d2) - E >> 0, pt(E) >> 0,
            pt(np.eye(d2) - E) >> 0]
    prob = cp.Problem(cp.Maximize(cp.trace(E @ delta)), cons)
    prob.solve(solver=cp.SCS, eps=eps, max_iters=200000, verbose=False)
    return 0.5 + 0.5 * float(prob.value), prob.status


def symplectic_parity(n):
    """A6: two Bell samples (v1, v2), v=(a,b) in F2^{2n}.
    parity = omega(v1,v2) = a1.b2 (+) a2.b1.
    ALT: both v in the Lagrangian L_A = {(a, M_A a)}, M_A symmetric
         -> omega = a1^T M a2 + a2^T M a1 = 0 ALWAYS (exact).
    NULL: v1, v2 uniform independent on F2^{2n}:
         P(omega=0) = (4^n + (4^n - 1) * 4^n / 2) / 4^{2n}
                    = 1/2 + 1/(2*4^n)  ... verify by enumeration for n<=3."""
    D = 4 ** n
    closed = 0.5 + 0.5 / D
    enum = None
    if n <= 3:
        zeros = 0
        for a1 in range(2 ** n):
            for b1 in range(2 ** n):
                for a2 in range(2 ** n):
                    for b2 in range(2 ** n):
                        w = (bin(a1 & b2).count("1")
                             + bin(a2 & b1).count("1")) % 2
                        if w == 0:
                            zeros += 1
        enum = zeros / (D * D)
    # ALT exactness spot-verified over ALL A at n=2,3 via Bell supports
    alt_ok = None
    if n <= 3:
        d = 2 ** n
        bv = bell_basis(n)
        alt_ok = True
        for A in all_A(n):
            psi = phase_state_vec(n, A)
            two = np.kron(np.outer(psi, psi), np.outer(psi, psi))
            support = [k for k, v in bv.items() if float(v @ two @ v) > 1e-12]
            for (a1, b1) in support:
                for (a2, b2) in support:
                    w = (bin(a1 & b2).count("1")
                         + bin(a2 & b1).count("1")) % 2
                    if w != 0:
                        alt_ok = False
    # decision rule "respond ALT iff parity==0", priors 1/2, noiseless:
    #   P(correct) = 1/2 * 1 + 1/2 * (1 - P(0|NULL))
    succ_1parity = 0.5 * 1.0 + 0.5 * (1.0 - closed)
    return {"p_parity0_null_closed": closed,
            "p_parity0_null_enum": enum,
            "alt_parity_always0_all_A": alt_ok,
            "success_1_parity_bit_noiseless": succ_1parity}


def run(n, do_sdp=True):
    d = 2 ** n
    out = {"n": n}
    acc, count = m2_brute(n)
    M2 = acc / (count * d ** 2)
    G = m2_gauss(n)
    M2g = G / d ** 2
    out["m2_brute_equals_gauss_exact"] = bool(
        np.array_equal(acc * 1, G * count))  # acc/(count*d^2) == G/d^2
    out["n_A"] = count
    ok, _ = single_copy_check(n)
    out["single_copy_mixture_exact"] = ok
    bell_p, p_alt = bell_strategy(n, M2)
    out["bell_2copy_success_exact"] = bell_p
    conc = {f"{a},{b}": p for (a, b), p in p_alt.items() if p > 1e-12}
    out["bell_alt_support_size"] = len(conc)
    out["bell_alt_p00"] = p_alt[(0, 0)]
    out["helstrom_global_2copy"] = helstrom(n, M2)
    if do_sdp:
        val, status = ppt_ceiling(n, M2)
        out["ppt_ceiling_2copy_primal"] = val
        out["ppt_status"] = status
        out["ppt_note"] = ("PRIMAL NUMERICAL ONLY - dual certificate owed at "
                           "freeze (understating a max ceiling is the "
                           "dangerous direction)")
    out["symplectic_parity_4copy"] = symplectic_parity(n)
    return out


if __name__ == "__main__":
    for n in (2, 3, 4):
        print(f"=== n={n} ===", flush=True)
        RESULTS[f"n{n}"] = run(n, do_sdp=True)
        print(json.dumps(RESULTS[f"n{n}"], indent=1, default=str), flush=True)
    RESULTS["card"] = "h15_g1_ceiling_atoms"
    RESULTS["cycle"] = "C5074"
    RESULTS["route"] = "Elder ruling coordination#12393"
    with open("/droid/repos/quantum/results/h15_g1_ceiling_atoms_c5074.json",
              "w") as f:
        json.dump(RESULTS, f, indent=1, default=str)
    print("WROTE results/h15_g1_ceiling_atoms_c5074.json")
