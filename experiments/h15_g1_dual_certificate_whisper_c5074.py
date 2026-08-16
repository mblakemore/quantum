#!/usr/bin/env python3
"""H15 G1 — producer-side PPT DUAL CERTIFICATE (B1 G3 pattern, Elder's spec
coordination#12398: extract the dual, verify feasibility OUTSIDE the solver via
eigenvalue residuals, round rigorously to U-prime; Elder re-derives
independently and we diff on the record).

Primal (per n):  max <Delta, E>  s.t.  E>=0, I-E>=0, PT(E)>=0, PT(I-E)>=0,
with Delta = M2 - I/4^n. Ceiling = 1/2 + primal/2.

Dual:  min Tr(Y)+Tr(V)  s.t.  Y>=0, V>=0, W>=0,  Y + PT(V) - PT(W) >= Delta.
Any FEASIBLE (Y,V,W) upper-bounds the primal. Certificate construction:
  1. take solver duals (Y,V,W);
  2. OUT-OF-SOLVER verification with numpy eigvalsh (independent of SCS):
     shift each matrix PSD by max(0,-lambda_min)*I;
  3. residual R = Y' + PT(V') - PT(W') - Delta; if lambda_min(R) < 0, add
     the deficit to Y' (costs D*deficit in the objective) -> R' >= 0 exactly
     up to eigensolver accuracy;
  4. U_prime = 1/2 + (Tr Y' + Tr V')/2, reported with every shift applied
     ON THE SAFE SIDE (inflating the bound, never deflating).
The dangerous direction is UNDERSTATING the ceiling; every rounding here
OVERSTATES it. Target to beat: the closed-form candidate 1/2+(2^n-1)/4^n.
$0. No submission path."""
import json
import sys

import numpy as np
import cvxpy as cp

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_g1_ceiling_atoms_whisper_c5074 import m2_brute

OUT = {"card": "h15_g1_dual_certificate", "cycle": "C5074",
       "spec": "Elder coordination#12398, B1 G3 pattern"}


def pt_np(X, d):
    return X.reshape(d, d, d, d).transpose(0, 3, 2, 1).reshape(d * d, d * d)


def certify(n, eps=1e-10):
    d = 2 ** n
    D = d * d
    acc, count = m2_brute(n)
    M2 = acc / (count * d ** 2)
    Delta = M2 - np.eye(D) / D

    E = cp.Variable((D, D), symmetric=True)

    def pt(X):
        return cp.reshape(cp.transpose(cp.reshape(X, (d, d, d, d), order="C"),
                                       (0, 3, 2, 1)), (D, D), order="C")

    c_S = E >> 0
    c_Y = np.eye(D) - E >> 0
    c_W = pt(E) >> 0
    c_V = pt(np.eye(D) - E) >> 0
    prob = cp.Problem(cp.Maximize(cp.trace(E @ Delta)),
                      [c_S, c_Y, c_W, c_V])
    prob.solve(solver=cp.SCS, eps=eps, max_iters=400000, verbose=False)
    primal = float(prob.value)

    def sym(M):
        M = np.asarray(M, dtype=float)
        return 0.5 * (M + M.T)

    Y, W, V = sym(c_Y.dual_value), sym(c_W.dual_value), sym(c_V.dual_value)

    # out-of-solver PSD repair (numpy eigvalsh, independent of SCS)
    shifts = {}
    mats = {}
    for name, M in (("Y", Y), ("V", V), ("W", W)):
        lam = float(np.linalg.eigvalsh(M)[0])
        s = max(0.0, -lam)
        shifts[name] = s
        mats[name] = M + s * np.eye(D)
    Yp, Vp, Wp = mats["Y"], mats["V"], mats["W"]

    # inequality residual: R = Y' + PT(V') - PT(W') - Delta  must be >= 0.
    # NOTE the safe direction on W: shifting W UP makes -PT(W) SMALLER, which
    # can only make R smaller -> repairing R afterwards keeps the bound valid.
    R = Yp + pt_np(Vp, d) - pt_np(Wp, d) - Delta
    lamR = float(np.linalg.eigvalsh(sym(R))[0])
    deficit = max(0.0, -lamR)
    Yp = Yp + deficit * np.eye(D)          # costs D*deficit, safe side

    # final re-verification from scratch
    R2 = Yp + pt_np(Vp, d) - pt_np(Wp, d) - Delta
    lamR2 = float(np.linalg.eigvalsh(sym(R2))[0])
    lamY = float(np.linalg.eigvalsh(Yp)[0])
    lamV = float(np.linalg.eigvalsh(Vp)[0])
    lamW = float(np.linalg.eigvalsh(Wp)[0])

    dual_obj = float(np.trace(Yp) + np.trace(Vp))
    safety = 1e-9 * max(1.0, abs(dual_obj))          # eigensolver headroom
    U_prime = 0.5 + (dual_obj + safety) / 2

    closed = 0.5 + (2 ** n - 1) / 4 ** n
    return {
        "n": n, "primal_ceiling": 0.5 + primal / 2,
        "solver_status": prob.status,
        "psd_shifts": shifts, "R_deficit_repaired": deficit,
        "final_min_eigs": {"Y": lamY, "V": lamV, "W": lamW, "R": lamR2},
        "dual_objective": dual_obj,
        "U_prime_ceiling_upper_bound": U_prime,
        "closed_form_candidate": closed,
        "gap_Uprime_minus_closed": U_prime - closed,
        "certificate_ok": bool(lamY >= -1e-12 and lamV >= -1e-12
                               and lamW >= -1e-12 and lamR2 >= -1e-12),
    }


if __name__ == "__main__":
    for n in (2, 3, 4):
        r = certify(n)
        OUT[f"n{n}"] = r
        print(f"n={n}: primal {r['primal_ceiling']:.10f}  "
              f"U' {r['U_prime_ceiling_upper_bound']:.10f}  "
              f"closed {r['closed_form_candidate']:.10f}  "
              f"gap {r['gap_Uprime_minus_closed']:.2e}  "
              f"cert_ok {r['certificate_ok']}", flush=True)
    with open("/droid/repos/quantum/results/h15_g1_dual_certificate_c5074.json",
              "w") as f:
        json.dump(OUT, f, indent=1)
    print("WROTE results/h15_g1_dual_certificate_c5074.json")
