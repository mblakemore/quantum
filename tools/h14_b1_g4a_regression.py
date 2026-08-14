#!/usr/bin/env python3
"""B1 promotion packet, G4a producer artifact (Whisper C5073, board #150, Elder gate c7d4b8f).

REGRESSION: the mixed-dim embed code path (ptrace_seq / embed_last / perm_matrix_mixed /
comb-at-mixed-dims — the machinery the 512 solve trusts) run at qubit dims [2,2,2,2,2] must
reproduce the certified dim-32 ceiling 0.8690277 (Stage V validated the OLD dim-32 comb path;
this closes the gap Elder named: the NEWER embed code was never regressed at 32).

Two pins:
  P1: exchange built via perm_matrix_mixed([2,2,2,2,2], [2,3,0,1,4]) must EQUAL the old
      exchange32() matrix exactly (new permutation machinery vs old hand-built).
  P2: solve value |dev| <= 1e-5 from QSTAR_PRIMAL (same bar as Stage V).
One code path: everything imported from h14_b1_reduced_solve.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from h14_b1_reduced_solve import (G_qstar, exchange32, clifford24, rep32, QSTAR_PRIMAL,
                                  ptrace_seq, embed_last, perm_matrix_mixed)
import cvxpy as cp

D32 = [2, 2, 2, 2, 2]


def comb_mixed_A(W, dims, odim):
    lhs1, d1 = ptrace_seq(W, dims, [4])
    red1, dr1 = ptrace_seq(W, dims, [4, 3])
    rhs1 = embed_last(red1 / odim, dr1, odim, 3)
    lhs2, d2 = ptrace_seq(W, dims, [4, 3, 2])
    red2, dr2 = ptrace_seq(W, dims, [4, 3, 2, 1])
    rhs2 = embed_last(red2 / odim, dr2, odim, 1)
    return [lhs1 == rhs1, lhs2 == rhs2]


def comb_mixed_B(W, dims, odim):
    lhs1, d1 = ptrace_seq(W, dims, [4])
    red1, dr1 = ptrace_seq(W, dims, [4, 1])
    rhs1 = embed_last(red1 / odim, dr1, odim, 1)
    lhs2, d2 = ptrace_seq(W, dims, [4, 1, 0])
    red2, dr2 = ptrace_seq(W, dims, [4, 1, 0, 3])
    rhs2 = embed_last(red2 / odim, dr2, odim, 1)
    return [lhs1 == rhs1, lhs2 == rhs2]


def main():
    t0 = time.time()
    G = G_qstar()
    # P1: new exchange machinery vs old hand-built
    PI_new = perm_matrix_mixed(D32, [2, 3, 0, 1, 4])
    PI_old = exchange32()
    dev_pi = np.max(np.abs(PI_new - PI_old))
    print(f"P1 exchange (perm_matrix_mixed vs exchange32): max dev {dev_pi:.2e} -> {'PASS' if dev_pi == 0 else 'FAIL'}")
    assert dev_pi == 0, "exchange builders disagree"
    reps = [rep32(V) for V in clifford24()]
    WA = cp.Variable((32, 32), hermitian=True)
    avg = sum(cp.Constant(R) @ WA @ cp.Constant(R.conj().T) for R in reps) / len(reps)
    WB = cp.Constant(PI_new) @ WA @ cp.Constant(PI_new)
    cons = [WA >> 0, WA == avg,
            cp.real(cp.trace(WA + WB)) == 4, cp.imag(cp.trace(WA + WB)) == 0]
    cons += comb_mixed_A(WA, D32, 2)
    cons += comb_mixed_B(WB, D32, 2)
    prob = cp.Problem(cp.Maximize(cp.real(cp.trace(cp.Constant(G) @ (WA + WB)))), cons)
    print(f"[{time.time()-t0:5.1f}s] assembled (comb via the MIXED-DIM machinery); solving...")
    try:
        prob.solve(solver="CLARABEL")
    except cp.error.SolverError:
        print("CLARABEL failed — SCS fallback")
        prob.solve(solver="SCS", eps=1e-9, max_iters=200000)
    val = float(prob.value); dev = abs(val - QSTAR_PRIMAL)
    gate = dev <= 1e-5 and prob.status in ("optimal", "optimal_inaccurate")
    print(f"[{time.time()-t0:5.1f}s] value {val:.10f} vs certified {QSTAR_PRIMAL:.10f} |dev| {dev:.2e} status {prob.status}")
    print(f"G4a REGRESSION: {'PASS' if gate else 'FAIL'}")
    json.dump({"card": "h14_b1_g4a_regression", "cycle": "C5073",
               "P1_exchange_max_dev": float(dev_pi),
               "value": val, "certified": QSTAR_PRIMAL, "abs_dev": float(dev),
               "status": prob.status, "gate": "PASS" if gate else "FAIL",
               "note": "mixed-dim embed machinery (ptrace_seq/embed_last/perm_matrix_mixed + comb at dims [2,2,2,2,2], odim 2) regressed against the certified dim-32 ceiling per Elder G4a"},
              open(os.path.join(HERE, "..", "results", "h14_b1_g4a_regression.json"), "w"), indent=1)
    print("-> results/h14_b1_g4a_regression.json")
    return 0 if gate else 2


if __name__ == "__main__":
    sys.exit(main())
