#!/usr/bin/env python3
"""B1 packet G3 — INDEPENDENT dual rounding to a certified upper bound U' (Whisper C5073, #150).

Independence discipline (commit-reveal vs Elder's hash-committed U'): the partial-trace maps and
their adjoints are implemented HERE from scratch (numpy reshape), the comb maps are checked
against the solver's own comb512_* on random inputs, conventions are pinned EMPIRICALLY, and the
final bound is self-certified by the weak-duality identity Tr[C WA] = U - Tr[S WA]. Every step is
a hard assert; a failure STOPS with the piece named rather than emitting a number.

Bound logic: primal is max Tr[C WA] over {WA>=0, Tr WA = 8 (from Re Tr(WA+WB)=16, WB=PI WA PI),
comb_A(WA)=0, comb_B(WB)=0}, with C = 2*G_herm (objective 2 Re Tr[G WA], verified identity).
Weak duality: for ANY multipliers, S := t*I + adj_combA(Y3,Y4) + adj_combB_in_WAspace(Y5,Y6) - C.
If S >= 0 then for any feasible WA>=0: Tr[C WA] = 8*t - Tr[S WA] <= 8*t (comb terms vanish on
feasible WA; Tr[S WA]>=0). So U = 8*t with S>=0 certifies. We take (t, Y*) from the banked dual,
pin signs empirically, repair S to PSD, and report the repaired certified U'.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from h14_b1_reduced_solve import (G512_qstar, exchange512, comb512_A, comb512_B, D512)
import cvxpy as cp

RNG = np.random.default_rng(5073)
DIMS = D512  # [4,4,4,4,2]


def rand_herm(n):
    X = RNG.normal(size=(n, n)) + 1j * RNG.normal(size=(n, n))
    return (X + X.conj().T) / 2


# ---- reshape-based partial trace and its adjoint (implemented + verified here) ----
def ptrace(M, dims, axes):
    """Trace out `axes` (indices into dims) of operator M on ⊗dims. Returns (out, out_dims)."""
    n = len(dims)
    T = M.reshape(dims + dims)                 # row indices 0..n-1, col indices n..2n-1
    keep = [i for i in range(n) if i not in axes]
    for ax in sorted(axes, reverse=True):
        T = np.trace(T, axis1=ax, axis2=ax + (T.ndim // 2))
    out_dims = [dims[i] for i in keep]
    d = int(np.prod(out_dims))
    return T.reshape(d, d), out_dims


def ptrace_adj(Y, dims, axes):
    """Adjoint of ptrace(·,dims,axes): insert identity legs at `axes`. Y lives on the kept dims."""
    n = len(dims)
    keep = [i for i in range(n) if i not in axes]
    yd = [dims[i] for i in keep]
    Yt = Y.reshape(yd + yd)
    # build full tensor by tensoring identities on traced axes, then move legs to place
    for ax in sorted(axes):
        Yt = np.expand_dims(Yt, 0)             # placeholder; we reconstruct by explicit kron below
    # explicit construction: iterate factor by factor is fussy — use einsum-free kron placement.
    # Simpler correct route: build via basis — but that's O(d^2). Instead use the identity that
    # ptrace_adj = insert I on each traced axis in row/col. Do it by reconstructing the 2n tensor.
    full_r = list(range(n)); full_c = list(range(n, 2 * n))
    # start from Y as 2*|keep| tensor
    Yt = Y.reshape(yd + yd)
    # current axis order: keep-rows then keep-cols
    cur_axes = list(keep) + [a + n for a in keep]
    for ax in sorted(axes):
        I = np.eye(dims[ax])
        Yt = np.tensordot(Yt, I, axes=0)       # append two new legs (row,col) for this axis
        cur_axes = cur_axes + [ax, ax + n]
    # now permute cur_axes -> sorted (0..n-1, n..2n-1)
    target = list(range(n)) + list(range(n, 2 * n))
    perm = [cur_axes.index(t) for t in target]
    Yt = np.transpose(Yt, perm)
    d = int(np.prod(dims))
    return Yt.reshape(d, d)


def check_ptrace_adjoint():
    axes_sets = [[4], [4, 3], [4, 3, 2], [4, 3, 2, 1], [4, 1], [4, 1, 0], [4, 1, 0, 3]]
    worst = 0.0
    D = int(np.prod(DIMS))
    for axes in axes_sets:
        X = rand_herm(D)
        pt, od = ptrace(X, DIMS, axes)
        Y = rand_herm(int(np.prod(od)))
        lhs = np.vdot(pt, Y)                    # <ptrace(X), Y>
        rhs = np.vdot(X, ptrace_adj(Y, DIMS, axes))  # <X, ptrace_adj(Y)>
        worst = max(worst, abs(lhs - rhs))
    return worst


from h14_b1_reduced_solve import perm_matrix_mixed


def embed_last_np(x, small_dims, insert_dim, position):
    P = perm_matrix_mixed(small_dims + [insert_dim], list(range(len(small_dims)))[:position]
                          + [len(small_dims)] + list(range(len(small_dims)))[position:])
    big = np.kron(x, np.eye(insert_dim))
    return P @ big @ P.T


def embed_last_adj(Y, small_dims, insert_dim, position):
    P = perm_matrix_mixed(small_dims + [insert_dim], list(range(len(small_dims)))[:position]
                          + [len(small_dims)] + list(range(len(small_dims)))[position:])
    Z = P.T @ Y @ P                             # inserted axis now LAST
    out, _ = ptrace(Z, small_dims + [insert_dim], [len(small_dims)])
    return out


# comb_A maps (numpy), mirroring comb512_A exactly
def combA1(W):
    lhs, _ = ptrace(W, DIMS, [4])
    red, dr = ptrace(W, DIMS, [4, 3])
    return lhs - embed_last_np(red / 4, dr, 4, 3)          # on [4,4,4,4]=256


def combA1_adj(Y):
    return ptrace_adj(Y, DIMS, [4]) - (1 / 4) * ptrace_adj(embed_last_adj(Y, [4, 4, 4], 4, 3), DIMS, [4, 3])


def combA2(W):
    lhs, _ = ptrace(W, DIMS, [4, 3, 2])
    red, dr = ptrace(W, DIMS, [4, 3, 2, 1])
    return lhs - embed_last_np(red / 4, dr, 4, 1)          # on [4,4]=16


def combA2_adj(Y):
    return ptrace_adj(Y, DIMS, [4, 3, 2]) - (1 / 4) * ptrace_adj(embed_last_adj(Y, [4], 4, 1), DIMS, [4, 3, 2, 1])


def combB1(W):
    lhs, _ = ptrace(W, DIMS, [4])
    red, dr = ptrace(W, DIMS, [4, 1])
    return lhs - embed_last_np(red / 4, dr, 4, 1)


def combB1_adj(Y):
    return ptrace_adj(Y, DIMS, [4]) - (1 / 4) * ptrace_adj(embed_last_adj(Y, [4, 4, 4], 4, 1), DIMS, [4, 1])


def combB2(W):
    lhs, _ = ptrace(W, DIMS, [4, 1, 0])
    red, dr = ptrace(W, DIMS, [4, 1, 0, 3])
    return lhs - embed_last_np(red / 4, dr, 4, 1)


def combB2_adj(Y):
    return ptrace_adj(Y, DIMS, [4, 1, 0]) - (1 / 4) * ptrace_adj(embed_last_adj(Y, [4], 4, 1), DIMS, [4, 1, 0, 3])


def cvxpy_comb_value(comb_fn, W):
    """Numeric [lhs-rhs] of each constraint of the solver's comb function at constant W."""
    Wc = cp.Constant(W)
    return [np.asarray(c.args[0].value) - np.asarray(c.args[1].value) for c in comb_fn(Wc)]


def check_forward_maps():
    D = int(np.prod(DIMS)); W = rand_herm(D)
    a = cvxpy_comb_value(comb512_A, W); b = cvxpy_comb_value(comb512_B, W)
    devs = [np.max(np.abs(combA1(W) - a[0])), np.max(np.abs(combA2(W) - a[1])),
            np.max(np.abs(combB1(W) - b[0])), np.max(np.abs(combB2(W) - b[1]))]
    return max(devs)


def check_comb_adjoints():
    D = int(np.prod(DIMS)); worst = 0.0
    for fwd, adj, od in [(combA1, combA1_adj, 256), (combA2, combA2_adj, 16),
                         (combB1, combB1_adj, 256), (combB2, combB2_adj, 16)]:
        X = rand_herm(D); Y = rand_herm(od)
        worst = max(worst, abs(np.vdot(fwd(X), Y) - np.vdot(X, adj(Y))))
    return worst


if __name__ == "__main__":
    w1 = check_ptrace_adjoint()
    print(f"GATE 1 — ptrace/adjoint identity, worst |dev|: {w1:.2e}")
    assert w1 < 1e-9, "GATE 1 FAIL"
    print("GATE 1 PASS")

    w2 = check_forward_maps()
    print(f"GATE 2 — my comb maps vs solver comb512_*, worst |dev|: {w2:.2e}")
    assert w2 < 1e-9, "GATE 2 FAIL — forward maps disagree with the solver"
    print("GATE 2 PASS")

    w3 = check_comb_adjoints()
    print(f"GATE 3 — comb adjoint inner-product identity, worst |dev|: {w3:.2e}")
    assert w3 < 1e-9, "GATE 3 FAIL"
    print("GATE 3 PASS — primitives certified; ready to assemble S")

    # ---- load banked material + assemble S, pinning convention EMPIRICALLY ----
    dat = np.load(os.path.join(HERE, "..", "results", "h14_b1_512_dual_certificate.npz"))
    WA, G = dat["WA"], dat["G"]
    PI = exchange512()
    Gh = (G + G.conj().T) / 2
    C = 2 * Gh
    y1 = float(dat["dual_1"]); y2 = float(dat["dual_2"])
    Y3, Y4, Y5, Y6 = dat["dual_3"], dat["dual_4"], dat["dual_5"], dat["dual_6"]
    print(f"\nbanked: dual_1(Re-tr)={y1:.8f}  dual_2(Im-tr)={y2:.2e}  16*dual_1={16*y1:.8f}")
    obj = float(np.real(np.trace(C @ WA)))
    print(f"primal Tr[C WA] = {obj:.10f} (== reported 0.9066742739690719)")

    def combB_adj_WA(adjf, Y):   # constraint acts on WB = PI WA PI
        return PI @ adjf(Y) @ PI

    comb_part = (combA1_adj(Y3) + combA2_adj(Y4)
                 + combB_adj_WA(combB1_adj, Y5) + combB_adj_WA(combB2_adj, Y6))

    # Empirical pin: U = 16*y1 (Re-trace b=16, others b=0). The dual slack must satisfy the
    # identity Tr[C WA] = U - Tr[S WA]. Try {sign of comb block} x {trace coeff 2*y1 or y1}.
    best = None
    for sgn in (+1, -1):
        for tcoef, tag in ((2 * y1, "2*y1*I"), (y1, "y1*I")):
            S = tcoef * np.eye(512) + sgn * comb_part - C
            resid = abs(obj - (16 * y1 - float(np.real(np.trace(S @ WA)))))
            if best is None or resid < best[0]:
                best = (resid, sgn, tcoef, tag, S)
    resid, sgn, tcoef, tag, S = best
    print(f"\nGATE 4 — empirical convention pin: sign {sgn:+d}, trace term {tag}, "
          f"identity residual |Tr[C WA] - (16y1 - Tr[S WA])| = {resid:.2e}")
    assert resid < 1e-6, "GATE 4 FAIL — no assembly satisfies weak-duality identity; convention unresolved"
    print("GATE 4 PASS — S assembled, convention pinned by the data")

    S = (S + S.conj().T) / 2
    lmin = float(np.linalg.eigvalsh(S)[0])
    delta = max(0.0, -lmin)
    U = 16 * y1
    Uprime = U + 8 * delta        # certified: Tr[C X] <= U + 8*max(0,-lmin(S)) for feasible X (Tr X=8)
    print(f"\nS min eigenvalue: {lmin:.3e}  ->  repair delta {delta:.3e}")
    print(f"dual objective U = 16*y1 = {U:.10f}")
    print(f"CERTIFIED U' = U + 8*delta = {Uprime:.10f}")
    print(f"vs primal {obj:.10f}  ->  gap U'-primal = {Uprime-obj:+.3e} "
          f"({'TIGHTER than primal' if Uprime < obj else 'above primal'})")

    # independence: hash my result for the reveal-diff with Elder's committed hash
    import hashlib
    result = {"card": "h14_b1_g3_certified_bound", "cycle": "C5073", "seat": "whisper",
              "U_dual_obj": U, "S_min_eig": lmin, "repair_delta": delta,
              "U_prime_certified": Uprime, "primal": obj,
              "gap_Uprime_minus_primal": Uprime - obj,
              "convention": {"comb_sign": sgn, "trace_term": tag, "identity_residual": resid},
              "gates": {"ptrace_adj": w1, "comb_maps_vs_solver": w2, "comb_adj": w3, "identity": resid},
              "note": "independent numpy-reshape adjoints, comb maps match solver exactly (0), convention pinned empirically; U' = 16*dual_1 + 8*max(0,-lmin(S))"}
    outp = os.path.join(HERE, "..", "results", "h14_b1_g3_certified_bound_c5073.json")
    js = json.dumps(result, indent=1, sort_keys=True)
    open(outp, "w").write(js)
    print(f"\nsha256(result) = {hashlib.sha256(js.encode()).hexdigest()}")
    print(f"-> {outp}")
