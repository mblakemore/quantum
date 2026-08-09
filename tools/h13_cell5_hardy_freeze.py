#!/usr/bin/env python3
"""H13 Cell 5 (Hardy) — design numeric to FREEZE angles, predictions, and bands. $0, sim only.

Optimizes the Hardy state + local Ry measurement angles for max Hardy probability q subject
to the three zero constraints, then prices the four probabilities under the campaign noise
model (readout 1.5%/bit, CX depol 0.8%) to set prereg bands.

Conventions: measurement setting = Ry(-theta) before Z measurement (outcome 1 = |1>).
Hardy logic (CH difference form, LHV bound 0):
  W = P(11|A1B1) - P(11|A2B1) - P(11|A1B2) - P(00|A2B2) <= 0 for all LHV.
Whisper C5048. Docs tier.
"""
import json
import numpy as np
from scipy.optimize import minimize

def ry(t):
    return np.array([[np.cos(t / 2), -np.sin(t / 2)], [np.sin(t / 2), np.cos(t / 2)]])

def probs(state, ta, tb):
    """P(a,b) for measuring in Ry-rotated bases; returns 2x2 array P[a,b]."""
    U = np.kron(ry(-ta), ry(-tb))
    v = U @ state
    p = np.abs(v) ** 2
    return p.reshape(2, 2)

def hardy_quantities(x):
    # state: real, 3 params (no |11> needed a priori but allow full real 4-vector, normalized)
    s = x[:4] / np.linalg.norm(x[:4])
    a1, a2, b1, b2 = x[4:8]
    P_11_A1B1 = probs(s, a1, b1)[1, 1]
    P_11_A2B1 = probs(s, a2, b1)[1, 1]
    P_11_A1B2 = probs(s, a1, b2)[1, 1]
    P_00_A2B2 = probs(s, a2, b2)[0, 0]
    return s, P_11_A1B1, P_11_A2B1, P_11_A1B2, P_00_A2B2

def neg_obj(x, mu=200.0):
    _, q, z1, z2, z3 = hardy_quantities(x)
    return -(q) + mu * (z1 ** 2 + z2 ** 2 + z3 ** 2)

def neg_obj_hard(x):
    """Stage-2 objective: brutal penalty pins the true Hardy point (zeros ~ 0)."""
    _, q, z1, z2, z3 = hardy_quantities(x)
    return -(q) + 2.0e6 * (z1 ** 2 + z2 ** 2 + z3 ** 2)

def apply_readout(P, eps=0.015):
    """Symmetric readout flips on both bits of a 2x2 joint distribution."""
    F = np.array([[1 - eps, eps], [eps, 1 - eps]])
    return F @ P @ F.T

def noisy_quantities(s, angles, p_cx=0.008, eps=0.015):
    rho = np.outer(s, s)
    rho = (1 - p_cx) * rho + p_cx * np.eye(4) / 4
    a1, a2, b1, b2 = angles
    out = {}
    for name, (ta, tb, idx) in {
        "q_11_A1B1": (a1, b1, (1, 1)), "z1_11_A2B1": (a2, b1, (1, 1)),
        "z2_11_A1B2": (a1, b2, (1, 1)), "z3_00_A2B2": (a2, b2, (0, 0)),
    }.items():
        U = np.kron(ry(-ta), ry(-tb))
        r = U @ rho @ U.conj().T
        P = np.real(np.diag(r)).reshape(2, 2)
        P = apply_readout(P, eps)
        out[name] = float(P[idx])
    out["W"] = out["q_11_A1B1"] - out["z1_11_A2B1"] - out["z2_11_A1B2"] - out["z3_00_A2B2"]
    return out

def main():
    rng = np.random.default_rng(5048)
    best = None
    for _ in range(60):
        x0 = np.concatenate([rng.normal(size=4), rng.uniform(-np.pi, np.pi, 4)])
        res = minimize(neg_obj, x0, method="Nelder-Mead",
                       options={"maxiter": 20000, "xatol": 1e-10, "fatol": 1e-12})
        res = minimize(neg_obj_hard, res.x, method="Nelder-Mead",
                       options={"maxiter": 40000, "xatol": 1e-12, "fatol": 1e-14})
        if best is None or res.fun < best.fun:
            best = res
    s, q, z1, z2, z3 = hardy_quantities(best.x)
    angles = [float(a % (2 * np.pi)) for a in best.x[4:8]]
    ideal = {"state": [round(float(v), 6) for v in s],
             "angles_A1_A2_B1_B2": [round(a, 6) for a in angles],
             "q": round(float(q), 6), "zeros": [round(float(z), 8) for z in (z1, z2, z3)],
             "q_max_theory": round((5 * np.sqrt(5) - 11) / 2, 6)}
    noisy = noisy_quantities(s, best.x[4:8])
    rep = {"ideal": ideal, "noisy_prediction": {k: round(v, 5) for k, v in noisy.items()}}
    # shot budget at 8000/setting
    ses = {k: float(np.sqrt(v * (1 - v) / 8000)) for k, v in noisy.items() if k != "W"}
    seW = float(np.sqrt(sum(s ** 2 for s in ses.values())))
    rep["se_at_8000"] = {k: round(v, 5) for k, v in ses.items()}
    rep["W_se_at_8000"] = round(seW, 5)
    rep["W_sigmas"] = round(noisy["W"] / seW, 1)
    print(json.dumps(rep, indent=2))
    with open("/droid/repos/quantum/results/h13_cell5_hardy_freeze_c5048.json", "w") as f:
        json.dump(rep, f, indent=2)

if __name__ == "__main__":
    main()
