#!/usr/bin/env python3
"""H10-C1 REGISTERED BARS v2 (Whisper C5017) — Amendment 3: the Hadamard-test meter.

WHAT CHANGED FROM v1 (h10_c1_prereg_bars_c5017.py) AND WHY, stated completely:
  v1 assumed C(g) = sum_S f(S)e^{igS} is measurable by the paper's 2-run insertion recipe.
  The KA fence refused the built circuits; root-caused to (a) a transcription INVERSION of
  the paper's footnote 18 in the scout note (left-side measurement gives the SIZE
  distribution, not the winding one), and (b) Eq. 107's 2-run identity resting on an
  EPR-only cancellation — at finite beta the expectation sandwich measures the CONJUGATED
  correlator, whose transform is NOT f(S) (it has negative-frequency support; characterized
  exactly).
  THE METER (Amendment 3): the single-coupling correlator C(g) = <Psi| B_R e^{igV} A_L |Psi>
  with A = Q(t) on L, B = Q(-t) on R (transpose = time reversal for our real-symmetric H —
  the wormhole's opposite-time convention emerging from the algebra), measured by an ancilla
  HADAMARD TEST: Re from the plain test, Im with an S^dag on the ancilla. No postselection,
  no assembly constants.
  CERTIFICATION: on the exact TFD (real-symmetric M) the identity
      C(g) == sum_S f(S) e^{igS}
  holds at machine precision (printed below as the certification leg). On the FLOWN state
  (complex up to a global phase e^{i phi}, phi ~ 1.518, genuine-complex residual ~0.067)
  the meter reads the phase-fixed winding; the registered numbers below are the FLIGHT
  ESTIMATOR'S noiseless values on the flown state — like-for-like at the state level.
  The alpha slope is invariant to the global-phase offset (constant phase absorbs into the
  fit intercept); ratios are magnitude-based.
"""
import json, math, os, sys
import importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
spec = importlib.util.spec_from_file_location("rt", os.path.join(HERE, "h10_c1_rhohalf_route_c5017.py"))
rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)

I2, X, Y, Z = rt.I2, rt.X, rt.Y, rt.Z
Ut = rt.trotter(2, 2)
A_L = Ut @ rt.Q @ Ut.conj().T           # Q(t)  on L
B_R = Ut.conj().T @ rt.Q @ Ut           # Q(-t) on R
w4 = np.kron(X, X) - np.kron(Y, Y) + np.kron(Z, Z)
ww, wv = np.linalg.eigh(w4)
G16 = [2 * np.pi * k / 16 for k in range(16)]

def apply_pair(psi, u4, i):
    t = psi.reshape([2] * 12)
    t = np.moveaxis(np.tensordot(u4.reshape(2, 2, 2, 2), t, axes=([2, 3], [i, 6 + i])),
                    [0, 1], [i, 6 + i])
    return t.reshape(-1)

def apply_side(psi, m, side):
    t = psi.reshape(64, 64)
    return (m @ t if side == 0 else t @ m.T).reshape(-1)

def eVg(psi, g):
    u4 = (wv * np.exp(-1j * g / 4 * ww)) @ wv.conj().T
    for i in range(6): psi = apply_pair(psi, u4, i)
    return psi * np.exp(1j * g * 4.5)

def C_meas(M):
    """The meter's noiseless reading: single-V correlator over the 16-point grid."""
    psi = M.reshape(-1).astype(complex)
    out = []
    for g in G16:
        v = apply_side(psi, A_L, 0)
        v = eVg(v, g)
        v = apply_side(v, B_R, 1)
        out.append(complex(np.vdot(psi, v)))
    return np.array(out)

def decode(Cvals, gstar):
    """Frozen SS3 arithmetic, unchanged in FORM from v1: 16-pt DFT, 4-pt frozen-set fit."""
    fh = {S: sum(Cvals[k] * np.exp(-1j * G16[k] * S) for k in range(16)) / 16 for S in range(7)}
    ph = np.unwrap([np.angle(fh[S]) for S in (1, 2, 3, 4)])
    Am = np.vstack([[1, 2, 3, 4], np.ones(4)]).T
    alpha = float(-(np.linalg.pinv(Am) @ ph)[0] / 2)
    C = lambda g: abs(sum(fh[S] * np.exp(1j * g * S) for S in fh))
    return {"alpha_4pt": alpha, "R_unwind": float(C(gstar) / C(0)), "R_wrong": float(C(-gstar) / C(0)),
            "C0": float(C(0)), "fhat": {str(S): [fh[S].real, fh[S].imag] for S in fh}}

def main():
    out = {"amendment": 3, "meter": "Hadamard test, C(g) = <B_R e^{igV} A_L>, A=Q(t) L, B=Q(-t) R",
           "decode": "16pt DFT + 4pt frozen-set fit (FORM unchanged from v1)"}
    # certification leg: exact TFD identity
    Mex = rt.rho_half(rt.BETA)
    fex = rt.winding_M(Mex, Ut)
    Cex = C_meas(Mex)
    cert = max(abs(Cex[k] - sum(fex[S] * np.exp(1j * g * S) for S in fex)) for k, g in enumerate(G16))
    out["certification_exactTFD_identity_resid"] = float(cert)
    assert cert < 1e-9, "single-V identity broken on exact TFD"
    dec_ex = decode(Cex, -0.395)
    out["exactTFD_meter_reading"] = {k: v for k, v in dec_ex.items() if k != "fhat"}

    # flown-state registered numbers
    ROUTE = json.load(open(os.path.join(RESULTS, "h10_c1_rhohalf_route_c5017.json")))
    sel = ROUTE["routeB_variational"][ROUTE["Lstar"]]
    Man = rt.ansatz_state(np.array(sel["params"]), sel["L"], per_pair=sel["per_pair"])
    Cfl = C_meas(Man)
    # gstar: frozen from the flown meter reading's own curve (argmax over the instrument grid)
    fh0 = {S: sum(Cfl[k] * np.exp(-1j * G16[k] * S) for k in range(16)) / 16 for S in range(7)}
    gs_grid = np.linspace(-3.2, 3.2, 1281)
    Cfun = [abs(sum(fh0[S] * np.exp(1j * g * S) for S in fh0)) for g in gs_grid]
    gstar = float(gs_grid[int(np.argmax(Cfun))])
    dec = decode(Cfl, gstar)
    out["gstar_registered"] = gstar
    out["registered"] = dec
    out["Cmeas_flown_grid"] = [[c.real, c.imag] for c in Cfl]

    # beta0 arm (params=0): meter must read zero winding
    C0v = C_meas(rt.bell_M())
    dec0 = decode(C0v, gstar)
    out["beta0"] = {"alpha_4pt": dec0["alpha_4pt"], "max_phase": float(max(
        abs(np.angle(complex(a, b))) for S, (a, b) in dec0["fhat"].items() if S in "1234" and (a*a+b*b) > 1e-20))}

    # scrambled-g arm prediction = fhat[0] of the flown reading (Z-parity zero for exact; report flown value)
    out["scrambled_arm_prediction_f0"] = dec["fhat"]["0"]

    # MC error table: Hadamard-test SE model — Re,Im each from n-shot +/-1 ancilla readouts
    rng = np.random.default_rng(9)
    mc = []
    for lam in (1.0, 0.5, 0.35, 0.2, 0.1):
        for ng in (15000,):
            als, rus, rws = [], [], []
            for _ in range(20000):
                Cn = []
                for k in range(16):
                    c = lam * Cfl[k]
                    se_r = math.sqrt(max(0.0, 1 - c.real ** 2) / ng)
                    se_i = math.sqrt(max(0.0, 1 - c.imag ** 2) / ng)
                    Cn.append(complex(c.real + se_r * rng.normal(), c.imag + se_i * rng.normal()))
                d = decode(np.array(Cn), gstar)
                als.append(d["alpha_4pt"]); rus.append(d["R_unwind"]); rws.append(d["R_wrong"])
            mc.append({"lambda": lam, "n_per_part": ng,
                       "alpha_mean": float(np.mean(als)), "alpha_sigma": float(np.std(als)),
                       "alpha_sig_neg": float(-np.mean(als) / np.std(als)),
                       "unwind_sig_gt1": float((np.mean(rus) - 1) / np.std(rus)),
                       "wrong_sig_lt1": float((1 - np.mean(rws)) / np.std(rws))})
    out["mc_error_table"] = mc

    path = os.path.join(RESULTS, "h10_c1_prereg_bars_v2_c5017.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(f"certification (exact TFD identity): {cert:.2e}")
    print("exact-TFD meter reading:", {k: round(v, 4) for k, v in out["exactTFD_meter_reading"].items()})
    print("REGISTERED (flown state):", {k: round(v, 4) for k, v in dec.items() if k != "fhat"},
          "gstar:", gstar)
    print("beta0:", out["beta0"])
    for r in mc:
        print(f"lam={r['lambda']}: alpha {r['alpha_mean']:+.4f}+-{r['alpha_sigma']:.4f} "
              f"({r['alpha_sig_neg']:.1f}sig<0) unwind {r['unwind_sig_gt1']:.1f}sig wrong {r['wrong_sig_lt1']:.1f}sig")
    print("->", path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
