#!/usr/bin/env python3
"""B1 promotion packet, G3 producer artifact — 512 re-solve WITH DUAL CAPTURE (Whisper C5073,
board #150, Elder gate spec docs/h14-b1-promotion-gate-SPEC-elder-c6618.md).

Same assembly as solve512 (imported from h14_b1_reduced_solve — one code path), same solver
settings; after solve, banks: primal WA, EVERY constraint's dual_value, primal/dual feasibility
residuals, and the solver's dual objective. The rigorous rounding of the approximate dual into
a certified upper bound U' happens in the analysis step (fresh block) — this job's product is
the raw certificate material Elder's G3 requires (an approx-feasible PRIMAL understates a max;
the DUAL is the certifying side).
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from h14_b1_reduced_solve import (G512_qstar, exchange512, comb512_A, comb512_B, D512,
                                  QSTAR_PRIMAL)
import cvxpy as cp
import scipy.sparse as sp

OUT_NPZ = os.path.join(HERE, "..", "results", "h14_b1_512_dual_certificate.npz")
OUT_JSON = os.path.join(HERE, "..", "results", "h14_b1_512_dual_certificate.json")


def main():
    t0 = time.time()
    gate = json.load(open(os.path.join(HERE, "..", "results", "h14_b1_stageV.json")))
    assert gate["gate"] == "PASS"
    G = G512_qstar()
    PI = exchange512()
    assert np.linalg.norm(PI @ G @ PI.T - G) < 1e-8
    WA = cp.Variable((512, 512), hermitian=True)
    cons = [WA >> 0]
    WB = cp.Constant(sp.csr_matrix(PI)) @ WA @ cp.Constant(sp.csr_matrix(PI))
    cons += [cp.real(cp.trace(WA + WB)) == 16, cp.imag(cp.trace(WA + WB)) == 0]
    cons += comb512_A(WA)
    cons += comb512_B(WB)
    prob = cp.Problem(cp.Maximize(cp.real(cp.trace(cp.Constant(sp.csr_matrix(G)) @ (WA + WB)))), cons)
    print(f"[{time.time()-t0:6.1f}s] assembled; solving (SCS, dual capture)...", flush=True)
    prob.solve(solver="SCS", eps=1e-7, max_iters=100000, verbose=False)
    print(f"[{time.time()-t0:6.1f}s] SOLVED: {prob.value:.8f} status {prob.status}", flush=True)

    duals = {}
    for i, c in enumerate(cons):
        dv = c.dual_value
        if dv is None: continue
        duals[f"dual_{i}"] = np.asarray(dv)
    # primal residuals
    Wv = WA.value
    eig_min = float(np.linalg.eigvalsh((Wv + Wv.conj().T) / 2).min())
    res = {f"violation_{i}": float(np.max(np.abs(np.asarray(c.violation())))) for i, c in enumerate(cons)}
    np.savez_compressed(OUT_NPZ, WA=Wv, G=G, **duals)
    summary = {"card": "h14_b1_512_dual_certificate", "cycle": "C5073",
               "primal_value": float(prob.value), "status": prob.status,
               "prev_run_value": 0.90667427,
               "min_eig_WA": eig_min, "constraint_violations": res,
               "n_dual_blocks": len(duals),
               "note": "raw certificate material; rigorous dual rounding -> certified U' happens in the analysis step (Elder G3)",
               "solver": "SCS eps 1e-7 max_iters 100000"}
    json.dump(summary, open(OUT_JSON, "w"), indent=1)
    print(f"[{time.time()-t0:6.1f}s] banked {len(duals)} dual blocks -> {OUT_NPZ}", flush=True)
    print(json.dumps(summary, indent=1)[:600], flush=True)


if __name__ == "__main__":
    main()
