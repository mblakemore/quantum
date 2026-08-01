#!/usr/bin/env python3
"""H10-C1 REGISTERED BARS (Whisper C5017) — the prereg's numbers, computed from the frozen route.

Loads the committed route artifact (h10_c1_rhohalf_route_c5017.json: frozen ansatz params) and
computes every number the prereg registers, with the FLIGHT'S OWN ESTIMATORS (like-for-like, the
B4 lesson): the frozen 4-point decode's alpha differs from the instrument's threshold-set fit
(-0.1882 vs -0.1583 on the same state) because the fit sets differ — the registered bar is the
flight estimator's value on the as-flown state, nothing else.

Registered decode (frozen here):
  f_hat(S) = (1/16) sum_k C_hat(g_k) e^{-i g_k S},  g_k = 2 pi k/16   (complex C from Re+Im runs)
  alpha_hat = -slope/2 of unweighted lstsq on unwrapped angles arg f_hat(S), S in {1,2,3,4} FROZEN
  R_unwind = C_recon(g*)/C_recon(0), R_wrong = C_recon(-g*)/C_recon(0)  (lambda-robust ratios)
  lambda_hat = C_recon(0)/C0_asflown  (attenuation self-calibration, reported)
Coupling (conjugation-convention pinned by exact check): W_i = X_iX'_i - Y_iY'_i + Z_iZ'_i reads
+3 on untouched sites, -1 on any Pauli; V = (3N - sum_i W_i)/4 grades string size S exactly.
"""
import json, os, sys
import importlib.util
import numpy as np
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
spec = importlib.util.spec_from_file_location("rt", os.path.join(HERE, "h10_c1_rhohalf_route_c5017.py"))
rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)

art = json.load(open(os.path.join(RESULTS, "h10_c1_rhohalf_route_c5017.json")))
sel = art["routeB_variational"][art["Lstar"]]
M = rt.ansatz_state(np.array(sel["params"]), sel["L"], per_pair=sel["per_pair"])
Ut = rt.trotter(2, 2)
fS = rt.winding_M(M, Ut)
GSTAR = art["asflown_bars"]["gstar_asflown"]

def Cg(f, g): return abs(sum(f[S] * np.exp(1j * g * S) for S in f))

def alpha_4pt(f):
    ph = np.unwrap([np.angle(f[S]) for S in (1, 2, 3, 4)])
    A = np.vstack([[1, 2, 3, 4], np.ones(4)]).T
    return float(-(np.linalg.pinv(A) @ ph)[0] / 2)

out = {"source": "h10_c1_rhohalf_route_c5017.json Lstar=" + art["Lstar"],
       "decode": "16pt DFT; alpha = 4pt frozen-set {1,2,3,4} unweighted fit; ratios from reconstruction",
       "gstar": GSTAR}
out["alpha_4pt_registered"] = alpha_4pt(fS)
out["R_unwind_registered"] = float(Cg(fS, GSTAR) / Cg(fS, 0))
out["R_wrong_registered"] = float(Cg(fS, -GSTAR) / Cg(fS, 0))
out["C0_asflown"] = float(Cg(fS, 0))
out["scrambled_g_arm_prediction"] = 0.0   # = f(0), exactly zero by Z-parity of H (Q anticommutes)

# beta=0 arm: same circuit template, all prep params zero (Bell pairs), same Trotter evolution
fS0 = rt.winding_M(rt.bell_M(), Ut)
out["beta0_alpha_4pt"] = alpha_4pt(fS0)
out["beta0_max_phase"] = float(max(abs(np.angle(fS0[S])) for S in (1, 2, 3, 4)))

# books leg: energy shift of each side under e^{i g* V} on the as-flown state (reported row)
I2, X, Y, Z = rt.I2, rt.X, rt.Y, rt.Z
def two_side(P, i, sign=1.0):
    ops = [I2] * 12; ops[i] = P; ops[6 + i] = P
    return sign * rt.kron(*ops)
Wsum = sum(two_side(X, i) - two_side(Y, i) + two_side(Z, i) for i in range(6))
V = (3 * 6 * np.eye(4096) - Wsum) / 4
wV, vV = np.linalg.eigh(V)
UV = (vV * np.exp(1j * GSTAR * wV)) @ vV.conj().T
# grading self-check: V must reproduce C(g) = sum f(S) e^{igS} on the op-state (identity gate)
psi = M.reshape(-1)
HL = np.kron(rt.H, np.eye(64)); HR = np.kron(np.eye(64), rt.H)
psi_g = UV @ psi
out["books_dE_R_at_gstar"] = float((np.vdot(psi_g, HR @ psi_g) - np.vdot(psi, HR @ psi)).real)
out["books_dE_L_at_gstar"] = float((np.vdot(psi_g, HL @ psi_g) - np.vdot(psi, HL @ psi)).real)
out["books_E_R_baseline"] = float(np.vdot(psi, HR @ psi).real)

# V-grading check: vec(chi) of a Pauli string chi is an eigenvector of V with eigenvalue S[chi].
# (op-state map: (O x I)|Phi> = vec(O) row-major — same L/R ordering as V's construction.)
# The Y-containing strings are the conjugation-sensitive cases the XX+YY+ZZ form MISgrades.
def pstr(spec_):
    ops = [I2] * 6
    for site, P in spec_: ops[site] = {"X": X, "Y": Y, "Z": Z}[P]
    return rt.kron(*ops)
gr = 0.0
for spec_, S in ([[], 0], [[(0, "X")], 1], [[(2, "Y"), (4, "Z")], 2],
                 [[(0, "X"), (1, "Y"), (2, "Z"), (3, "Y"), (4, "X"), (5, "Z")], 6]):
    v_ = pstr(spec_).reshape(-1)
    gr = max(gr, float(np.linalg.norm(V @ v_ - S * v_)))
out["V_grading_eigencheck_maxresid"] = gr
assert gr < 1e-9, "V does not grade string size — conjugation convention broken"
out["V_grading_gate_note"] = ("V eigencheck passed here; flight script MUST additionally verify the "
                              "circuit-level identity C(g)=sum f(S)e^{igS} at 1e-6 from the ACTUAL "
                              "pubs before submission (prereg SS6)")

# ---- MC error table with the registered estimators (seeded, 20k draws) ----
rng = np.random.default_rng(9)
mc = []
for lam in (1.0, 0.5, 0.3, 0.15):
    for ng in (15000,):
        Cgrid = [lam * Cg(fS, 2 * np.pi * k / 16) for k in range(16)]
        sef = float(np.mean([np.sqrt((1 - min(1.0, c) ** 2) / ng) for c in Cgrid]) / np.sqrt(16))
        al, ru, rw = [], [], []
        for _ in range(20000):
            fh = {S: lam * fS[S] + sef * (rng.normal() + 1j * rng.normal()) for S in fS}
            al.append(alpha_4pt(fh)); ru.append(Cg(fh, GSTAR) / Cg(fh, 0)); rw.append(Cg(fh, -GSTAR) / Cg(fh, 0))
        mc.append({"lambda": lam, "n_per_g_component": ng, "sigma_f": sef,
                   "alpha_mean": float(np.mean(al)), "alpha_sigma": float(np.std(al)),
                   "alpha_sig_neg": float(-np.mean(al) / np.std(al)),
                   "R_unwind_sigma": float(np.std(ru)), "unwind_sig_gt1": float((np.mean(ru) - 1) / np.std(ru)),
                   "R_wrong_sigma": float(np.std(rw)), "wrong_sig_lt1": float((1 - np.mean(rw)) / np.std(rw))})
out["mc_error_table_n15k"] = mc

path = os.path.join(RESULTS, "h10_c1_prereg_bars_c5017.json")
json.dump(out, open(path, "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}, indent=1, default=str))
for r in mc:
    print(f"lam={r['lambda']}: alpha {r['alpha_mean']:+.4f}+-{r['alpha_sigma']:.4f} ({r['alpha_sig_neg']:.1f}sig) "
          f"unwind {r['unwind_sig_gt1']:.1f}sig  wrong {r['wrong_sig_lt1']:.1f}sig")
print("->", path)
