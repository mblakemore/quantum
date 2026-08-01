#!/usr/bin/env python3
"""H10-C1 rho^{1/2}-INSERTION ROUTE (Whisper C5017) — the last prereg-time item (scout SS9/SS10).

THE QUESTION: the winding meter's finite-beta object is O = Q(t) rho^{1/2}; on hardware the
insertion is realized by PREPARING the thermofield double |TFD> = vec(rho^{1/2}) on 2N qubits
(two-sided correlators on |TFD> ARE rho^{1/2}-inserted traces: <TFD|A_L B_R^T|TFD> =
Tr[rho^{1/2} A rho^{1/2} B]). The engineering choice: HOW to prepare |TFD_beta> at beta=0.6.

Routes assessed:
  A. LCU-compiled truncated expansion of e^{-beta H/2} on Bell pairs (non-unitary -> ancillas,
     select oracles, postselection) — quantified, then accepted/rejected on numbers.
  B. Variational thermal purification: alternating (inter-side pair coupling, two-side H
     evolution) layers from Bell pairs — the literature route (Wu-Hsieh class), exactly
     optimizable at N=6 (12 qubits = 4096-dim, classical).

METHOD DISCIPLINE (Item-2 lesson, applied at design time): every reconstructed frozen input is
GATED against the committed artifacts (the ephemeral-code gap this script also repairs — the
seeded H and the Trotter convention now live in committed code, pinned to the frozen numbers);
the new fast winding path is validated against the IMPORTED instrument (frozen arithmetic) on
full objects, then used. AS-FLOWN bars are computed like-for-like (B4 lesson): the prereg's
predictions come from the REALIZED prep (ansatz state) + REALIZED evolution (frozen Trotter),
with ideal-vs-realized deltas REPORTED, not wished away.

KA GATES (all must pass or the campaign output is not read):
  KA-H:  reconstructed H reproduces G_beta(0.5) and the OP row (alpha, rms, gstar, Gb) exactly
  KA-W:  fast einsum winding == imported winding() per-S at machine precision (M = rho^{1/2})
  KA-T:  reconstructed Trotter reproduces all four frozen rows (2-norm err, alpha, Cmax)
  KA-F:  TFD-frame identity: winding of M=rho_h equals the O=Q(t)rho^{1/2} instrument's output
"""
import itertools, json, math, os, sys
import importlib.util
import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
spec = importlib.util.spec_from_file_location("wsim", os.path.join(HERE, "h10_c1_winding_sim_c5016.py"))
wsim = importlib.util.module_from_spec(spec); spec.loader.exec_module(wsim)
kron, I2, X, Y, Z = wsim.kron, wsim.I2, wsim.X, wsim.Y, wsim.Z

N = 6; BETA, T = 0.6, 0.3            # frozen operating point (SS9)
PAIRS = list(itertools.combinations(range(N), 2))
GS = np.linspace(-3.2, 3.2, 1281)     # frozen unwinding grid (instrument convention)

# ---------- frozen constructor (pinned this session against the committed artifacts) ----------
def build_H():
    """all-to-all random Heisenberg + random Z fields, seed 42, N=6 — the constructive recipe:
    rng=default_rng(42); J = rng.normal(15)/sqrt(6) over pairs in combinations order (drawn
    FIRST); h = rng.normal(6); site 0 = leftmost kron factor; Q = X on site 0."""
    rng = np.random.default_rng(42)
    Js = rng.normal(size=15) / np.sqrt(6); hs = rng.normal(size=6)
    pterms = [Js[k] * sum(kron(*[P if q in (i, j) else I2 for q in range(N)]) for P in (X, Y, Z))
              for k, (i, j) in enumerate(PAIRS)]
    zterms = [hs[i] * kron(*[Z if q == i else I2 for q in range(N)]) for i in range(N)]
    return sum(pterms) + sum(zterms), pterms, zterms

H, PTERMS, ZTERMS = build_H()
Q = kron(*[X if k == 0 else I2 for k in range(N)])
EVw, EVv = np.linalg.eigh(H)

def rho_half(beta):
    r = (EVv * np.exp(-beta * EVw / 2)) @ EVv.conj().T
    return r / np.sqrt(np.trace(r @ r).real)      # Tr[rho]=1  =>  |vec| = 1

def U_exact(t): return (EVv * np.exp(-1j * EVw * t)) @ EVv.conj().T

def trotter(r, order, t=T):
    """Frozen convention (pinned to all four artifact rows INCLUDING the o1 alphas — the 2-norm
    alone cannot see term-order reversal for real-symmetric terms): term list = 15 pair-Heisenberg
    exponentials in combinations order then Z-fields, each applied by LEFT-multiplication (first
    listed term acts first); o2 = forward halves then reversed halves (palindrome)."""
    terms = PTERMS + ZTERMS; dt = t / r
    if order == 1:
        S = np.eye(64, dtype=complex)
        for Tm in terms: S = expm(-1j * Tm * dt) @ S
    else:
        A = np.eye(64, dtype=complex)
        for Tm in terms: A = expm(-1j * Tm * dt / 2) @ A
        B = np.eye(64, dtype=complex)
        for Tm in reversed(terms): B = expm(-1j * Tm * dt / 2) @ B
        S = B @ A
    U = np.eye(64, dtype=complex)
    for _ in range(r): U = U @ S
    return U

# ---------- fast winding of an arbitrary insertion M under an arbitrary U ----------
P4 = np.stack([I2, X, Y, Z])                       # p in IXYZ order; weight = (p != 0)
def winding_M(M, U):
    """f(S), Ssum for O = U Q U^dag M. Fast per-site Pauli contraction; validated (KA-W)
    against the imported instrument before use."""
    O = (U @ Q @ U.conj().T @ M).reshape([2] * 12)
    C = np.einsum('abcdefghijkl,Aga,Bhb,Cic,Djd,Eke,Flf->ABCDEF',
                  O, P4, P4, P4, P4, P4, P4, optimize=True) / np.sqrt(2 ** N)
    c = C.reshape(-1)
    digs = np.array([[(idx // 4 ** (5 - s)) % 4 for s in range(6)] for idx in range(4096)])
    Sw = (digs != 0).sum(axis=1)
    fS = {int(S): complex((c[Sw == S] ** 2).sum()) for S in range(7)}
    return fS

def Cg(fS, g): return abs(sum(fS[S] * np.exp(1j * g * S) for S in fS))
def curve(fS):
    vals = [Cg(fS, g) for g in GS]
    k = int(np.argmax(vals))
    return float(GS[k]), float(vals[k]), float(Cg(fS, 0.0))

def analyze(M, U):
    fS = winding_M(M, U)
    alpha, rms, Ss = wsim.fit_alpha(fS)            # frozen fit, imported
    gstar, Cmax, C0 = curve(fS)
    return {"alpha": alpha, "rms": rms, "gstar": gstar, "Cmax": Cmax, "C0": C0, "fS": fS}

# ---------- KA gates ----------
def gates():
    out = {}
    art_op = json.load(open(os.path.join(RESULTS, "h10_c1_operating_point_c5017.json")))["operating_point"]
    art_fs = json.load(open(os.path.join(RESULTS, "h10_c1_winding_fastscrambler_c5017.json")))["rows"]
    art_tr = json.load(open(os.path.join(RESULTS, "h10_c1_trotter_error_c5017.json")))
    rh = rho_half(0.5)
    out["KA_H_Gb05"] = abs(np.trace(rh @ Q @ rh @ Q).real - art_fs[0]["Gb"])
    ex = analyze(rho_half(BETA), U_exact(T))
    out["KA_H_alpha"] = abs(ex["alpha"] - art_op["alpha"]); out["KA_H_rms"] = abs(ex["rms"] - art_op["rms"])
    out["KA_H_gstar"] = abs(ex["gstar"] - art_op["gstar"]); out["KA_H_C0"] = abs(ex["C0"] - art_op["Gb"])
    # KA-W: fast path vs imported instrument, per-S
    fS_ref, _, Gb_ref = wsim.winding(H, BETA, T, N, Q)
    fS_fast = winding_M(rho_half(BETA), U_exact(T))
    out["KA_W_maxdiff"] = max(abs(fS_ref[S] - fS_fast[S]) for S in fS_ref)
    out["KA_F_sumf_vs_Gb"] = abs(sum(fS_fast.values()) - Gb_ref)
    # KA-T: all four frozen Trotter rows. 2-norm + alpha at 1e-9; Cmax separately at 1e-5 —
    # Cmax is a GRID-ARGMAX value (0.005 spacing): near-tied neighboring points make it
    # float-path sensitive at ~(dg)^2*curvature ~ 1e-6 (observed only on r=2 rows, one extra
    # matmul). Alphas at 1e-16 pin the convention; the argmax tolerance is stated, not hidden.
    Ue = U_exact(T); mx = 0.0; mxg = 0.0
    for r in (1, 2):
        for o in (1, 2):
            Ut = trotter(r, o); row = art_tr[f"trotter_r{r}_o{o}"]
            a = analyze(rho_half(BETA), Ut)
            mx = max(mx, abs(np.linalg.norm(Ut - Ue, 2) - row["unitary_2norm_err"]),
                     abs(a["alpha"] - row["alpha"]))
            mxg = max(mxg, abs(a["Cmax"] - row["Cmax"]))
    out["KA_T_maxdiff"] = mx; out["KA_T_Cmax_gridargmax"] = mxg
    ok = all(v < 1e-9 for k, v in out.items() if k != "KA_T_Cmax_gridargmax") and mxg < 1e-5
    return ok, out, ex

# ---------- TFD frame + routes ----------
def bell_M(): return np.eye(64, dtype=complex) / 8.0

def fidelity(Ma, Mb): return abs(np.vdot(Ma.reshape(-1), Mb.reshape(-1))) ** 2

def requirement_curve(Mt, Ut, n_seeds=12, epss=(0.05, 0.1, 0.2)):
    """bias-vs-infidelity: |TFD> + eps|r>, normalized. Reports (1-F, |dalpha|, |dCmax|, |dC0|)."""
    base = analyze(Mt, Ut); rows = []
    v0 = Mt.reshape(-1)
    for eps in epss:
        for sd in range(n_seeds):
            rng = np.random.default_rng(3000 + sd)
            r = rng.normal(size=4096) + 1j * rng.normal(size=4096); r /= np.linalg.norm(r)
            v = v0 + eps * r; v /= np.linalg.norm(v)
            a = analyze(v.reshape(64, 64), Ut)
            rows.append({"eps": eps, "seed": sd, "one_minus_F": 1 - abs(np.vdot(v0, v)) ** 2,
                         "dalpha": abs(a["alpha"] - base["alpha"]),
                         "dCmax": abs(a["Cmax"] - base["Cmax"]), "dC0": abs(a["C0"] - base["C0"])})
    return rows

# cached 4x4 eigendecompositions of the 15 pair terms (for fast compiled sweeps)
_P4TERMS = []
rng_cache = np.random.default_rng(42)
_Jc = rng_cache.normal(size=15) / np.sqrt(6); _hc = rng_cache.normal(size=6)
for _k in range(15):
    _T4 = _Jc[_k] * (np.kron(X, X) + np.kron(Y, Y) + np.kron(Z, Z))
    _w4, _v4 = np.linalg.eigh(_T4); _P4TERMS.append((_w4, _v4.real))

def _apply4(Mt, u4, ax1, ax2):
    return np.moveaxis(np.tensordot(u4.reshape(2, 2, 2, 2), Mt, axes=([2, 3], [ax1, ax2])),
                       [0, 1], [ax1, ax2])

def _sweep_o1(Mt, g, side):
    """One first-order sweep of exp(-i g H) on one side (0=L axes 0-5, 1=R axes 6-11), applied
    term-by-term in the frozen order (pairs in combinations order, then Z-fields) — this IS the
    hardware circuit for the prep's two-side evolution; no compilation gap exists by construction."""
    off = 0 if side == 0 else 6
    for k, (i, j) in enumerate(PAIRS):
        w4, v4 = _P4TERMS[k]
        u4 = (v4 * np.exp(-1j * g * w4)) @ v4.T
        Mt = _apply4(Mt, u4, off + i, off + j)
    ph = [np.exp(-1j * g * _hc[i] * np.array([1, -1])) for i in range(6)]
    for i in range(6):
        sh = [1] * 12; sh[off + i] = 2
        Mt = Mt * ph[i].reshape(sh)
    return Mt

def ansatz_state(params, L, per_pair=False, compiled=True):
    """From Bell pairs: per layer, (a) inter-side pair coupling exp(-i (aX X_iX'_i + aY Y_iY'_i
    + aZ Z_iZ'_i)) per Bell pair [shared or per-pair params], (b) two-side evolution by angle g —
    compiled=True uses the o1 sweep (the ACTUAL circuit; variational params absorb Trotter error),
    compiled=False uses exact e^{-igH} (kept only for comparison)."""
    Mt = bell_M().reshape([2] * 12); k = 0
    for _ in range(L):
        if per_pair:
            axs = params[k:k + 18].reshape(6, 3); k += 18
        else:
            axs = np.tile(params[k:k + 3], (6, 1)); k += 3
        g = params[k]; k += 1
        for i in range(6):
            aX, aY, aZ = axs[i]
            u4 = expm(-1j * (aX * np.kron(X, X) + aY * np.kron(Y, Y) + aZ * np.kron(Z, Z)))
            Mt = _apply4(Mt, u4, i, 6 + i)
        if compiled:
            Mt = _sweep_o1(Mt, g, 0); Mt = _sweep_o1(Mt, g, 1)
        else:
            Ug = (EVv * np.exp(-1j * g * EVw)) @ EVv.T
            Mt = (Ug @ Mt.reshape(64, 64) @ Ug).reshape([2] * 12)
    return Mt.reshape(64, 64)

def optimize_ansatz(L, per_pair=False, restarts=6, compiled=True):
    Mt = rho_half(BETA); npar = (18 if per_pair else 3) * L + L
    tvec = Mt.reshape(-1)
    def cost(p): return 1 - abs(np.vdot(tvec, ansatz_state(p, L, per_pair, compiled).reshape(-1))) ** 2
    best = None
    for rs in range(restarts):
        x0 = np.zeros(npar) if rs == 0 else np.random.default_rng(1000 + rs).uniform(-0.3, 0.3, npar)
        r = minimize(cost, x0, method="L-BFGS-B", options={"maxiter": 800, "ftol": 1e-14})
        if best is None or r.fun < best.fun: best = r
    return best.x, 1 - best.fun

def route_A(Mt, F_target):
    """k-term Taylor of e^{-beta H/2} on Bell pairs: fidelity(k), then the LCU bill for k_min."""
    # Pauli 1-norm of H: sum over terms |coeff| (3 per pair + 6 fields)
    rng = np.random.default_rng(42)
    Js = rng.normal(size=15) / np.sqrt(6); hs = rng.normal(size=6)
    lamH = float(3 * np.abs(Js).sum() + np.abs(hs).sum())
    out = {"lambda_H_pauli1norm": lamH, "orders": []}
    tgt = Mt.reshape(-1); k_min = None
    for k in range(1, 9):
        Mk = np.zeros((64, 64), complex); term = np.eye(64, dtype=complex)
        for j in range(k + 1):
            Mk += term / 8.0
            term = term @ (-BETA / 2 * H) / (j + 1)
        v = Mk.reshape(-1) / np.linalg.norm(Mk)
        Fk = abs(np.vdot(tgt, v)) ** 2
        lam_lcu = float(sum((BETA / 2) ** j * lamH ** j / math.factorial(j) for j in range(k + 1)))
        succ = float((np.linalg.norm((expm(-BETA / 2 * H) @ bell_M().reshape(64, 64)).reshape(-1)) /
                      (lam_lcu * np.linalg.norm(bell_M().reshape(-1)))) ** 2)
        out["orders"].append({"k": k, "F": Fk, "lambda_LCU": lam_lcu, "postselect_prob": succ})
        if k_min is None and Fk >= F_target: k_min = k
    out["k_min_for_F_target"] = k_min
    return out

def run():
    ok, ka, exact_op = gates()
    print("KA GATES:", "PASS" if ok else "FAIL", {k: f"{v:.2e}" for k, v in ka.items()})
    if not ok:
        print("DO NOT READ THE CAMPAIGN"); return 1
    out = {"H": "all-to-all random Heisenberg + random Z fields, seed 42, N=6 (constructor now committed)",
           "constructor": "default_rng(42): J=normal(15)/sqrt(6) pairs-first combinations order; h=normal(6); Q=X site0",
           "trotter_convention": "15 pair-terms (combinations order) then Z-fields; o2 = fwd-half + reversed-half; U=S(t/r)^r",
           "KA": {k: float(v) for k, v in ka.items()}, "operating_point": {"beta": BETA, "t": T}}
    Mt = rho_half(BETA); Ut = trotter(2, 2)
    tr_ref = analyze(Mt, Ut)                       # frozen-Trotter, exact insertion (SS10 baseline)
    out["trotter_exactM"] = {k: v for k, v in tr_ref.items() if k != "fS"}

    F0 = fidelity(Mt, bell_M())
    out["bell_baseline_F0"] = float(F0)
    print(f"Bell-pair raw fidelity vs TFD(beta=0.6): {F0:.6f}")

    out["requirement_curve"] = requirement_curve(Mt, Ut)
    # linear summary: dalpha ~ kappa * (1-F)
    xs = np.array([r["one_minus_F"] for r in out["requirement_curve"]])
    ys = np.array([r["dalpha"] for r in out["requirement_curve"]])
    kappa = float((xs @ ys) / (xs @ xs))
    out["dalpha_per_infidelity"] = kappa
    print(f"requirement: |dalpha| ~= {kappa:.3f} * (1-F)  =>  (1-F) <= {0.010/kappa:.4f} for Trotter-parity bias")

    # ---- route B: COMPILED ansatz (the ansatz IS the hardware circuit; variational params
    # absorb the sweep's Trotter error — no prep compilation gap exists by construction) ----
    CAND = [("L1", 1, False, 6), ("L2", 2, False, 6), ("L2pp", 2, True, 8), ("L3", 3, False, 6)]
    routeB = {}
    for key, L, pp, rs in CAND:
        params, F = optimize_ansatz(L, per_pair=pp, restarts=rs)
        a = analyze(ansatz_state(params, L, per_pair=pp), Ut)
        routeB[key] = {"L": L, "per_pair": pp, "F": float(F), "params": [float(p) for p in params],
                       "n_cx_prep_prerouting": int(L * (2 * 45 + 6 * 3)),
                       "asflown": {k: float(v) for k, v in a.items() if k != "fS"},
                       "dalpha_prep": float(abs(a["alpha"] - tr_ref["alpha"]))}
        print(f"{key}: F={F:.6f}  alpha={a['alpha']:+.4f} (d_prep={routeB[key]['dalpha_prep']:.4f}) "
              f"prep_CX~{routeB[key]['n_cx_prep_prerouting']}")
    # selection: CX-ascending, first with prep-added alpha bias <= Trotter-parity 0.010
    Lstar = None
    for key, L, pp, _ in CAND:
        if routeB[key]["dalpha_prep"] <= 0.010:
            Lstar = key; break
    if Lstar is None:
        params, F = optimize_ansatz(3, per_pair=True, restarts=8)
        a = analyze(ansatz_state(params, 3, per_pair=True), Ut)
        routeB["L3pp"] = {"L": 3, "per_pair": True, "F": float(F),
                          "params": [float(p) for p in params], "n_cx_prep_prerouting": 324,
                          "asflown": {k: float(v) for k, v in a.items() if k != "fS"},
                          "dalpha_prep": float(abs(a["alpha"] - tr_ref["alpha"]))}
        if routeB["L3pp"]["dalpha_prep"] <= 0.010: Lstar = "L3pp"
    out["routeB_variational"] = routeB; out["Lstar"] = Lstar

    F_star = routeB[Lstar]["F"] if Lstar else max(r["F"] for r in routeB.values())
    out["routeA_lcu"] = route_A(Mt, F_star)
    ra = out["routeA_lcu"]
    print(f"route A: k_min={ra['k_min_for_F_target']} for F>={F_star:.4f}; "
          f"postselect at k_min ~ {ra['orders'][(ra['k_min_for_F_target'] or 8)-1]['postselect_prob']:.3f}")

    # ---- as-flown bars at the chosen route (the prereg's SS3 numbers) ----
    if Lstar is not None:
        sel = routeB[Lstar]
        params = np.array(sel["params"])
        Mstar = ansatz_state(params, sel["L"], per_pair=sel["per_pair"])
        asf = analyze(Mstar, Ut); fS = asf.pop("fS")
        # arm bars, all from the as-flown f(S)
        gstar = asf["gstar"]
        # scrambled-phase arm: |f(S)| kept, phases randomized (all S), C evaluated at gstar;
        # frozen seed 0, 200 trials (definition restated here; deterministic bars are the KA)
        rng = np.random.default_rng(0)
        scr = np.array([abs(sum(abs(fS[S]) * np.exp(1j * ph[S]) * np.exp(1j * gstar * S) for S in fS))
                        for ph in rng.uniform(0, 2 * np.pi, size=(200, 7))])
        bars = {"mechanism_C_at_gstar": asf["Cmax"], "no_coupling_C0": asf["C0"],
                "wrong_sign_C": float(Cg(fS, -gstar)),
                "scrambled_phase_mean_C": float(scr.mean()), "scrambled_phase_p95": float(np.percentile(scr, 95)),
                "alpha_asflown": asf["alpha"], "rms_asflown": asf["rms"], "gstar_asflown": gstar,
                "gstar_vs_2alpha_asflown": [gstar, float(2 * asf["alpha"])]}
        # separations at planned shots — binomial SE on a +/-1 observable: sqrt((1-C^2)/n)
        n = 12000
        se = lambda C: np.sqrt((1 - C ** 2) / n)
        bars["planned_shots_per_arm_component"] = n
        bars["sep_mech_vs_floor_sigma"] = float((asf["Cmax"] - asf["C0"]) /
                                                np.hypot(se(asf["Cmax"]), se(asf["C0"])))
        bars["sep_floor_vs_wrongsign_sigma"] = float((asf["C0"] - bars["wrong_sign_C"]) /
                                                     np.hypot(se(asf["C0"]), se(bars["wrong_sign_C"])))
        out["asflown_bars"] = bars
        out["asflown_vs_exact_deltas"] = {k: float(bars[k] - exact_op[m]) for k, m in
                                          [("mechanism_C_at_gstar", "Cmax"), ("no_coupling_C0", "C0"),
                                           ("alpha_asflown", "alpha")]}
        out["fS_asflown"] = {str(S): [float(fS[S].real), float(fS[S].imag)] for S in sorted(fS)}
        # ---- alpha shot budget: f(S) from a 16-point g-grid DFT; sigma_f = mean_g SE(C)/sqrt(16);
        # DECODE RULE (to freeze in prereg): fit over S with |f_hat| >= 3 sigma_f, >=3 points or
        # alpha is declared unmeasurable (loud fail). KEY METER PROPERTY: global depolarizing
        # attenuation scales all C(g) by lambda -> |f| shrinks, arg f UNCHANGED -> alpha is
        # lambda-invariant; attenuation only raises shot cost (sigma_f/lambda in f-units).
        gsgrid = np.array([2 * np.pi * k / 16 for k in range(16)])
        Cgrid = np.array([Cg(fS, g) for g in gsgrid])
        budget = []
        for lam in (1.0, 0.3, 0.1):
            for ng in (5000, 20000, 50000):
                sef = float(np.mean(np.sqrt((1 - np.minimum(1, lam * Cgrid) ** 2) / ng)) / np.sqrt(16) / lam)
                fit_set = [S for S in sorted(fS) if S > 0 and abs(fS[S]) >= 3 * sef]
                if len(fit_set) >= 3:
                    A = np.vstack([fit_set, np.ones(len(fit_set))]).T
                    piv = np.linalg.pinv(A)[0]
                    sig_a = float(np.sqrt(sum(p ** 2 * (sef / abs(fS[S])) ** 2 for p, S in
                                              zip(piv, fit_set))) / 2)
                else:
                    sig_a = None
                budget.append({"lambda": lam, "n_per_g_component": ng, "sigma_f": sef,
                               "fit_set_S": fit_set, "sigma_alpha": sig_a})
        out["alpha_shot_budget_16pt_grid"] = budget
        for b in budget:
            if b["lambda"] in (1.0, 0.3) and b["n_per_g_component"] == 20000:
                print(f"alpha budget: lambda={b['lambda']} n_g=20k -> fit set {b['fit_set_S']} "
                      f"sigma_alpha={b['sigma_alpha'] if b['sigma_alpha'] is None else round(b['sigma_alpha'], 4)}")
        print("AS-FLOWN BARS:", json.dumps({k: (round(v, 4) if isinstance(v, float) else v)
                                            for k, v in bars.items()}))
    path = os.path.join(RESULTS, "h10_c1_rhohalf_route_c5017.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print("->", path)
    return 0

if __name__ == "__main__":
    sys.exit(run())
