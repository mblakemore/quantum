#!/usr/bin/env python3
"""
h14_b1_reduced_solve.py — the symmetry-reduced causal-game SDP (H14 B1 follow-on, Whisper C5069).

STAGE V (this file's --validate): rebuild the dim-32 ceiling with the SYMMETRIC variable —
  W_A parametrized on the C1-diag commutant basis, W_B = Π W_A Π (party exchange folded) —
  through the EXISTING comb-constraint code (causal_game_sdp.comb_constraints_A/B, one code
  path with the certified artifact). GATE: must reproduce the frozen primal-at-q* value
  0.8690277186779367 (results/causal_game_sdp_qij.json V6) to <= 1e-5 before any 512 work
  is trusted. The B1 study (results/h14_b1_symmetry_study.json) proved q* is exactly
  orbit-invariant and the rep commutes with G(q*) at 1.9e-15 — so restricting W to the
  commutant loses nothing (a group-average of any optimal W is optimal and symmetric).

STAGE 512 (--solve512): the same machinery at the symmetric-access dims — deferred until
  stage V passes; the number, when it lands, carries both pre-committed readings from the
  H14 charter and does NOT by itself promote or demote any claim.

    python3 tools/h14_b1_reduced_solve.py --validate
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import causal_game_sdp as cg          # the certified bound factory — constraints reused verbatim
import cvxpy as cp

R2 = np.sqrt(2.0)
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
NAMES = ['1', 'X', 'Y', 'Z', '(X+Y)/r2', '(X-Y)/r2', '(X+Z)/r2', '(X-Z)/r2', '(Y+Z)/r2', '(Y-Z)/r2']
GENS = [I2, X, Y, Z, (X+Y)/R2, (X-Y)/R2, (X+Z)/R2, (X-Z)/R2, (Y+Z)/R2, (Y-Z)/R2]
PLUS = np.array([1, 1], complex) / R2
MINUS = np.array([1, -1], complex) / R2
QSTAR_PRIMAL = 0.8690277186779367     # frozen V6 value; the validation gate's target


def load_qstar():
    qj = json.load(open(os.path.join(HERE, "..", "results", "causal_game_sdp_qij.json")))
    def split_pair(k):
        s, d = k[1:-1], 0
        for p, ch in enumerate(s):
            if ch == '(': d += 1
            elif ch == ')': d -= 1
            elif ch == ',' and d == 0: return s[:p], s[p+1:]
    qmap = {}
    for cl, dd in (('c', qj['q_star_commuting']), ('a', qj['q_star_anticommuting'])):
        for k, v in dd.items():
            a, b = split_pair(k)
            qmap[(NAMES.index(a), NAMES.index(b))] = (cl, float(v))
    return qmap


def G_qstar():
    """G(q*) through the bound factory's own game_op — one code path."""
    G = np.zeros((32, 32), complex)
    for (i, j), (cl, w) in load_qstar().items():
        if w == 0:
            continue
        G += w * cg.game_op(GENS[i], GENS[j], PLUS if cl == 'c' else MINUS)
    return G


def clifford24():
    Hm, Sm = (X + Z) / R2, np.diag([1, 1j]).astype(complex)
    def peq(A, B): return abs(abs(np.trace(A.conj().T @ B)) / 2 - 1) < 1e-9
    grp, frontier = [I2], [I2]
    while frontier:
        newf = []
        for M in frontier:
            for g in (Hm, Sm):
                Nn = g @ M
                if not any(peq(Nn, E) for E in grp):
                    grp.append(Nn); newf.append(Nn)
        frontier = newf
    assert len(grp) == 24, len(grp)
    return grp


def rep32(V):
    """Pinned convention from the B1 study: bar on the OUT factors only (err 1.9e-15)."""
    return np.kron(np.kron(np.kron(np.kron(V, V.conj()), V), V.conj()), I2)


def exchange32():
    P4 = np.zeros((16, 16))
    for a in range(4):
        for b in range(4):
            P4[b*4 + a, a*4 + b] = 1
    return np.kron(P4, I2)


def commutant_basis(reps, dim, tol=1e-9):
    """Orthonormal Hermitian basis of the commutant of the group rep, by averaging + Gram-Schmidt."""
    basis = []
    def avg(M):
        return sum(R @ M @ R.conj().T for R in reps) / len(reps)
    # Hermitian seed basis: E_ii, (E_ij+E_ji)/√2, (iE_ij - iE_ji)/√2
    seeds = []
    for i in range(dim):
        E = np.zeros((dim, dim), complex); E[i, i] = 1; seeds.append(E)
    for i in range(dim):
        for j in range(i+1, dim):
            E = np.zeros((dim, dim), complex); E[i, j] = E[j, i] = 1/np.sqrt(2); seeds.append(E)
            E = np.zeros((dim, dim), complex); E[i, j] = 1j/np.sqrt(2); E[j, i] = -1j/np.sqrt(2); seeds.append(E)
    for Ssd in seeds:
        A = avg(Ssd)
        for B in basis:
            A = A - np.trace(B.conj().T @ A) * B
        nrm = np.sqrt(abs(np.trace(A.conj().T @ A)))
        if nrm > tol:
            basis.append(A / nrm)
    return basis


def validate():
    t0 = time.time()
    G = G_qstar()
    CLIF = clifford24()
    reps = [rep32(V) for V in CLIF]
    # sanity: the rep really commutes with G (the study's pin, re-asserted here)
    maxerr = max(np.linalg.norm(R @ G @ R.conj().T - G) for R in reps)
    assert maxerr < 1e-8, maxerr
    print(f"[{time.time()-t0:5.1f}s] rep commutes with G(q*): max err {maxerr:.2e}")
    basis = commutant_basis(reps, 32)
    print(f"[{time.time()-t0:5.1f}s] C1-diag commutant basis at 32: {len(basis)} Hermitian elements "
          f"(vs 1024 unreduced) — recorded; stage V imposes the same restriction as linear "
          f"invariance constraints on the standard variable (solver-friendlier form)")
    PI = exchange32()
    WA = cp.Variable((32, 32), hermitian=True)
    avg = sum(cp.Constant(R) @ WA @ cp.Constant(R.conj().T) for R in reps) / len(reps)
    WB = cp.Constant(PI) @ WA @ cp.Constant(PI)
    cons = [WA >> 0, WA == avg, cp.real(cp.trace(WA + WB)) == 4,
            cp.imag(cp.trace(WA + WB)) == 0]
    cons += cg.comb_constraints_A(WA)
    cons += cg.comb_constraints_B(WB)
    prob = cp.Problem(cp.Maximize(cp.real(cp.trace(cp.Constant(G) @ (WA + WB)))), cons)
    try:
        prob.solve(solver="CLARABEL")
    except cp.error.SolverError:
        print("CLARABEL failed on the restricted form — falling back to SCS (high accuracy)")
        prob.solve(solver="SCS", eps=1e-9, max_iters=200000)
    val = prob.value
    dev = abs(val - QSTAR_PRIMAL)
    print(f"[{time.time()-t0:5.1f}s] reduced primal at q*: {val:.10f}  status={prob.status}")
    print(f"          frozen target:      {QSTAR_PRIMAL:.10f}  |dev| = {dev:.2e}")
    gate = dev <= 1e-5 and prob.status in ("optimal", "optimal_inaccurate")
    print(f"VALIDATION GATE: {'PASS' if gate else 'FAIL'} "
          f"({len(basis)}-parameter symmetric variable reproduces the certified ceiling)"
          if gate else "VALIDATION GATE: FAIL — 512 work is NOT unlocked")
    out = {"card": "h14_b1_reduced_solve_stageV", "cycle": "C5069", "substrate": "claude-fable-5",
           "commutant_basis_dim": len(basis), "reduced_value": float(val), "status": prob.status,
           "frozen_target": QSTAR_PRIMAL, "abs_dev": float(dev), "gate": "PASS" if gate else "FAIL"}
    json.dump(out, open(os.path.join(HERE, "..", "results", "h14_b1_stageV.json"), "w"), indent=1)
    print("-> results/h14_b1_stageV.json")
    return 0 if gate else 2



# ====================== STAGE 512 (appended C5069, after stage V PASS) ======================
D512 = [4, 4, 4, 4, 2]   # [A_I(ctl,sys), A_O(ctl,sys), B_I, B_O, C_I]
I4 = np.eye(4, dtype=complex)


def cU(U):
    """controlled-U on ctl (x) sys, control ordering [ctl, sys] (matches rep512's 1(x)V)."""
    P0 = np.diag([1, 0]).astype(complex); P1 = np.diag([0, 1]).astype(complex)
    return np.kron(P0, I2) + np.kron(P1, U)


def cj_vec4(U4):
    Iv = np.eye(4).reshape(-1)
    return np.kron(I4, U4.conj()) @ Iv


def G512_qstar():
    G = np.zeros((512, 512), complex)
    for (i, j), (cl, w) in load_qstar().items():
        if w == 0:
            continue
        a = cj_vec4(cU(GENS[i])); b = cj_vec4(cU(GENS[j]))
        ck = PLUS if cl == 'c' else MINUS
        G += w * np.kron(np.kron(np.outer(a, a.conj()), np.outer(b, b.conj())),
                         np.outer(ck, ck.conj()))
    return G


def rep512(V):
    f_in = np.kron(I2, V); f_out = np.kron(I2, V.conj())
    return np.kron(np.kron(np.kron(np.kron(f_in, f_out), f_in), f_out), I2)


def exchange512():
    P16 = np.zeros((256, 256))
    for a in range(16):
        for b in range(16):
            P16[b*16 + a, a*16 + b] = 1
    return np.kron(P16, I2)


def perm_matrix_mixed(dims, order):
    """Permutation matrix sending axis layout `dims` to layout dims[order]."""
    n = int(np.prod(dims))
    P = np.zeros((n, n))
    strides = np.cumprod([1] + [dims[k] for k in range(len(dims)-1, 0, -1)])[::-1]
    def idx(multi, ds):
        v = 0
        for x, dd in zip(multi, ds):
            v = v * dd + x
        return v
    import itertools as it
    for multi in it.product(*[range(dd) for dd in dims]):
        src = idx(multi, dims)
        dst = idx([multi[k] for k in order], [dims[k] for k in order])
        P[dst, src] = 1
    return P


def ptrace_seq(expr, dims, axes):
    """Sequential cvxpy partial trace over `axes` (indices into `dims`)."""
    cur_dims = list(dims)
    cur = expr
    for ax in sorted(axes, reverse=True):
        cur = cp.partial_trace(cur, cur_dims, axis=ax)
        cur_dims.pop(ax)
    return cur, cur_dims


def embed_last(expr_small, small_dims, insert_dim, position):
    """(expr (x) 1_insert) then permute the appended axis into `position`."""
    big = cp.kron(expr_small, cp.Constant(np.eye(insert_dim)))
    dims_now = small_dims + [insert_dim]
    order = list(range(len(small_dims)))
    order.insert(position, len(small_dims))
    P = cp.Constant(perm_matrix_mixed(dims_now, order))
    return P @ big @ P.T


def comb512_A(W):
    """A<B<C comb at mixed dims: (1) Tr_C W = Tr_{C,B_O}W/4 (x) 1_{B_O};
    (2) Tr_{C,B_O,B_I} W = Tr_{C,B_O,B_I,A_O}W/4 (x) 1_{A_O}."""
    lhs1, d1 = ptrace_seq(W, D512, [4])                    # dims [4,4,4,4]
    red1, dr1 = ptrace_seq(W, D512, [4, 3])                # dims [4,4,4]
    rhs1 = embed_last(red1 / 4, dr1, 4, 3)
    lhs2, d2 = ptrace_seq(W, D512, [4, 3, 2])              # dims [4,4]
    red2, dr2 = ptrace_seq(W, D512, [4, 3, 2, 1])          # dims [4]
    rhs2 = embed_last(red2 / 4, dr2, 4, 1)
    return [lhs1 == rhs1, lhs2 == rhs2]


def comb512_B(W):
    """B<A<C comb: mirror with (A_I,A_O)<->(B_I,B_O)."""
    lhs1, d1 = ptrace_seq(W, D512, [4])
    red1, dr1 = ptrace_seq(W, D512, [4, 1])                # trace C, A_O -> dims [4,4,4] = [A_I,B_I,B_O]
    rhs1 = embed_last(red1 / 4, dr1, 4, 1)                 # reinsert A_O at position 1
    lhs2, d2 = ptrace_seq(W, D512, [4, 1, 0])              # dims [4,4] = [B_I,B_O]
    red2, dr2 = ptrace_seq(W, D512, [4, 1, 0, 3])          # trace also B_O -> [B_I]
    rhs2 = embed_last(red2 / 4, dr2, 4, 1)
    return [lhs1 == rhs1, lhs2 == rhs2]


def solve512():
    t0 = time.time()
    gate = json.load(open(os.path.join(HERE, "..", "results", "h14_b1_stageV.json")))
    assert gate["gate"] == "PASS", "stage V gate not passed — 512 not unlocked"
    G = G512_qstar()
    print(f"[{time.time()-t0:6.1f}s] G512 built (trace {np.trace(G).real:.4f})")
    Hm, Sm = (X + Z) / R2, np.diag([1, 1j]).astype(complex)
    for nm, V in (("H", Hm), ("S", Sm)):
        R = rep512(V)
        err = np.linalg.norm(R @ G @ R.conj().T - G)
        print(f"[{time.time()-t0:6.1f}s] invariance check rep512({nm}): err {err:.2e}")
        assert err < 1e-8, f"rep512({nm}) does not commute with G512 — convention break"
    PI = exchange512()
    err = np.linalg.norm(PI @ G @ PI.T - G)
    print(f"[{time.time()-t0:6.1f}s] exchange invariance: err {err:.2e}")
    assert err < 1e-8
    import scipy.sparse as sp
    WA = cp.Variable((512, 512), hermitian=True)
    cons = [WA >> 0]
    for V in (Hm, Sm):
        R = sp.csr_matrix(rep512(V))
        cons.append(WA == cp.Constant(R) @ WA @ cp.Constant(R.conj().T))
    WB = cp.Constant(sp.csr_matrix(PI)) @ WA @ cp.Constant(sp.csr_matrix(PI))
    cons += [cp.real(cp.trace(WA + WB)) == 16, cp.imag(cp.trace(WA + WB)) == 0]
    cons += comb512_A(WA)
    cons += comb512_B(WB)
    prob = cp.Problem(cp.Maximize(cp.real(cp.trace(cp.Constant(sp.csr_matrix(G)) @ (WA + WB)))), cons)
    print(f"[{time.time()-t0:6.1f}s] problem assembled; solving (SCS)...")
    prob.solve(solver="SCS", eps=1e-7, max_iters=100000, verbose=False)
    print(f"[{time.time()-t0:6.1f}s] SOLVED: value = {prob.value:.8f}  status = {prob.status}")
    out = {"card": "h14_b1_symmetric_access_ceiling", "cycle": "C5069", "substrate": "claude-fable-5",
           "value": float(prob.value), "status": prob.status,
           "stageV_gate": "PASS (cited)", "solver": "SCS eps 1e-7",
           "readings": "charter pre-committed: >0.988 fence stands; <0.988 promotion is its own gated process",
           "comparison": {"dim32_ceiling": QSTAR_PRIMAL, "F82_hardware": 0.9769, "charter_fork": 0.988}}
    json.dump(out, open(os.path.join(HERE, "..", "results", "h14_b1_symmetric_access.json"), "w"), indent=1)
    print("-> results/h14_b1_symmetric_access.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--solve512", action="store_true")
    a = ap.parse_args()
    if a.validate:
        sys.exit(validate())
    elif a.solve512:
        solve512()
    else:
        print(__doc__)
