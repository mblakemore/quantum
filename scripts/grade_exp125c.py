#!/usr/bin/env python3
"""grade_exp125c.py — grade Exp125c reset-thermalize thermometry under the FROZEN prereg.
ΔP = P(1|t_max)-P(1|t_min) = conservative lower bound on d*p_eq; certifies (or bounds) the F105 frontier.
Writes results/exp125c_grade.json."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

LN2 = math.log(2)


def floor_of(p):
    if p <= 0:
        return 0.0
    if p >= 0.5:
        return float("inf")
    return LN2 / math.log((1 - p) / p)


def p1(counts):
    n1 = sum(c for b, c in counts.items() if b.strip()[-1] == "1")
    tot = sum(counts.values())
    return n1 / tot, tot


def main():
    man = json.load(open(os.path.join(HERE, "..", "results", "exp125c_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    P = {}
    for i, m in enumerate(metas):
        d = res[i].data
        counts = list(d.__dict__.values())[0].get_counts() if not hasattr(d, "c") \
            else d.c.get_counts()
        pv, N = p1(counts)
        P[m["label"]] = (pv, N, m["delay_us"])

    T1 = man["T1_s"]
    delays = sorted(man["delays_us"])
    t_min, t_max = delays[0], delays[-1]
    p_min, N_min, _ = P[f"therm_{t_min}us"]
    p_max, N_max, _ = P[f"therm_{t_max}us"]
    se_min = math.sqrt(p_min * (1 - p_min) / N_min)
    se_max = math.sqrt(p_max * (1 - p_max) / N_max)
    dP = p_max - p_min
    se_dP = math.sqrt(se_min ** 2 + se_max ** 2)

    # exp fit P(t)=P0+A(1-exp(-t/tau)) to confirm thermalization (tau ~ T1)
    ts = np.array([P[f"therm_{u}us"][2] for u in delays]) * 1e-6
    ps = np.array([P[f"therm_{u}us"][0] for u in delays])
    tau_fit = None
    try:
        from scipy.optimize import curve_fit
        def f(t, P0, A, tau):
            return P0 + A * (1 - np.exp(-t / tau))
        popt, _ = curve_fit(f, ts, ps, p0=[p_min, max(dP, 1e-4), T1],
                            bounds=([0, -1, 1e-6], [1, 1, 1e-3]), maxfev=20000)
        tau_fit = float(popt[2])
    except Exception as e:
        tau_fit = f"fit-failed:{type(e).__name__}"

    rise = 1 - math.exp(-t_max * 1e-6 / T1)      # 0.993 at 5*T1
    p_eq_lower = max(0.0, dP) / rise
    floor_lower = floor_of(p_eq_lower)
    se_p = se_dP / rise
    se_floor = (LN2 / (math.log((1 - p_eq_lower) / p_eq_lower) ** 2 * p_eq_lower * (1 - p_eq_lower))
                * se_p) if 0 < p_eq_lower < 0.5 else float("inf")

    b_hat = 1 - P["ref1"][0]
    a_hat = p_min

    g_therm = "PASS" if (dP - 5 * se_dP) > 0 else "FAIL"

    out = {
        "experiment": "exp125c-reset-thermalize-thermometry", "cycle": "C4665-whisper",
        "job_id": man["job_id"], "qubit": man["qubit"], "T1_us": round(T1 * 1e6, 1),
        "P1_by_delay": {f"{u}us": round(P[f"therm_{u}us"][0], 5) for u in delays},
        "a_hat(readout+reset@t0)": round(a_hat, 5), "b_hat(readout_1to0)": round(b_hat, 5),
        "deltaP": round(dP, 5), "SE_deltaP": round(se_dP, 5),
        "deltaP_over_5SE_sigma": round(dP / se_dP, 2) if se_dP > 0 else None,
        "tau_fit_us": round(tau_fit * 1e6, 1) if isinstance(tau_fit, float) else tau_fit,
        "G_therm(dP-5SE>0)": g_therm,
        "p_eq_lower": round(p_eq_lower, 5),
        "floor_lower_E": round(floor_lower, 4), "SE_floor": round(se_floor, 4),
    }

    if g_therm == "PASS":
        S = 0.855 - 5 * 0.020        # conservative |S(B|A)|
        bonus = S * floor_lower
        se_b = S * se_floor
        tc, tk = man["tax_coherent"], man["tax_classical"]
        out["frontier"] = {
            "bonus_lower_E": round(bonus, 4), "SE_bonus": round(se_b, 4),
            "vs_coherent_0.028": "ACCESSIBLE-CERTIFIED" if (bonus - tc - 5 * se_b) > 0
                else ("INACCESSIBLE" if (tc - bonus - 5 * se_b) > 0 else "STRADDLE"),
            "vs_classical_0.092": "ACCESSIBLE-CERTIFIED" if (bonus - tk - 5 * se_b) > 0
                else ("INACCESSIBLE" if (tk - bonus - 5 * se_b) > 0 else "STRADDLE"),
            "tax_note": "F97 tax is a QET-feedforward decoherence proxy for cashing cost, NOT measured erasure work",
        }
    else:
        out["meta_finding"] = ("THIRD-AXIS NULL: q4 thermal population not resolved above 0 at 5sigma. "
                               "F104 (credit-SE), F105 (tomographic-SPAM), F125c (equilibration thermometry) "
                               "converge: the erasure effect lies below NISQ's certification floor. "
                               "Per frozen ceiling: STOP, no Exp125d.")

    outp = os.path.join(HERE, "..", "results", "exp125c_grade.json")
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
