#!/usr/bin/env python3
"""
Exp101 — Window retention decomposition: is "calibration-window quality" a scalar?
Author: Ember (DC15E) | Cycle: C4099 | Date: 2026-07-04

ANALYSIS ONLY — no QPU, no new circuits. Reads Elder's committed result JSONs:
  results/exp95_qpu_results.json  (F78 "BAD" window,  job d93s1fkql68s73c8oong)
  results/exp98_qpu_results.json  (F81 "GOOD" window, job d93vso6vtlqs73ftmqhg)
Identical deep-QQQ circuits, identical qubits [54,53,55], 11.2h apart (per F81).

QUESTION (mechanism, not variance): F81 established the two windows differ 12x-vs-
CR-bound in blind MLE error. Exp99 (Ember C4098, sim) showed depolarizing noise turns
the ideal Grover curve sin^2((2k+1)theta) into a GEOMETRICALLY ATTENUATED oscillation
p(k) = 0.5 + R^k * (P_ideal(k) - 0.5). If window quality were a single depolarizing
scale, each window should fit that model with its own R, and per-k contrast retention
should be geometric in k and sign-symmetric (peaks and troughs attenuate alike).

MODELS (least squares over k=0..5, 4096 shots):
  M_shift : p = P_ideal(k) + c            (coherent/readout offset, no contrast decay)
  M_dep   : p = 0.5 + R^k*(P_id-0.5)      (pure depolarizing, Exp99 model)
  M_both  : p = 0.5 + d + R^k*(P_id-0.5)  (depolarizing + offset)
Compared by RSS + AIC vs the binomial shot-noise floor E[RSS] ~ sum p(1-p)/N.

SIDE OBSERVATIONS graded quantitatively:
  (a) odd/even retention asymmetry in the bad window (odd k = peaks p>0.5,
      even k = troughs p<0.5; pure depolarizing predicts NO asymmetry),
  (b) k0 (shallow, 7 2q gates) error ACROSS windows vs k5 (124 2q) retention
      across windows — if anti-ordered, window quality is not a scalar and a
      shallow same-window read does not certify the deep circuit (bears on
      README Rec#5 sentinel logic + Exp100 H-TSC gates).
"""
import json
import math
import os

import numpy as np
from scipy.optimize import minimize_scalar, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
SHOTS = 4096


def ideal_curve(a_true, ks):
    theta = math.asin(math.sqrt(a_true))
    return np.array([math.sin((2 * k + 1) * theta) ** 2 for k in ks])


def load_windows():
    with open(os.path.join(RESULTS, "exp95_qpu_results.json")) as f:
        e95 = json.load(f)
    with open(os.path.join(RESULTS, "exp98_qpu_results.json")) as f:
        e98 = json.load(f)
    a_true = e98["grade"]["QQQ"]["a_true"]
    ks = np.arange(6)
    # BAD window (Exp95): first k0 read (index 0..5); retest kept separately
    bad = np.array([p for _, p in e95["p_hw"][:6]])
    bad_k0_retest = e95["p_hw"][6][1]
    # GOOD window (Exp98): QQQ pubs i=0..5; retest pub i=12
    good = np.array([r["p"] for r in e98["per_pub"] if r["loader"] == "QQQ"][:6])
    good_k0_retest = [r["p"] for r in e98["per_pub"] if r["loader"] == "QQQ"][6]
    iwm = np.array([r["p"] for r in e98["per_pub"] if r["loader"] == "IWM"][:6])
    iwm_a = e98["grade"]["IWM"]["a_true"]
    return dict(a_true=a_true, ks=ks, bad=bad, bad_k0_retest=bad_k0_retest,
                good=good, good_k0_retest=good_k0_retest, iwm=iwm, iwm_a=iwm_a)


def rss(pred, obs):
    return float(np.sum((pred - obs) ** 2))


def aic(rss_val, n, kparams):
    return n * math.log(max(rss_val, 1e-12) / n) + 2 * kparams


def fit_models(p_ideal, obs, ks):
    n = len(obs)
    out = {}
    # M_shift: p = ideal + c
    c = float(np.mean(obs - p_ideal))
    r = rss(p_ideal + c, obs)
    out["M_shift"] = dict(params=dict(c=round(c, 5)), rss=r, aic=aic(r, n, 1))
    # M_dep: p = 0.5 + R^k (ideal-0.5)
    def f_dep(R):
        return rss(0.5 + (R ** ks) * (p_ideal - 0.5), obs)
    res = minimize_scalar(f_dep, bounds=(0.0, 1.5), method="bounded")
    out["M_dep"] = dict(params=dict(R=round(float(res.x), 4)), rss=float(res.fun),
                        aic=aic(float(res.fun), n, 1))
    # M_both: p = 0.5 + d + R^k (ideal-0.5)
    def f_both(x):
        R, d = x
        return rss(0.5 + d + (R ** ks) * (p_ideal - 0.5), obs)
    res2 = minimize(f_both, x0=[0.9, 0.0], bounds=[(0.0, 1.5), (-0.2, 0.2)])
    out["M_both"] = dict(params=dict(R=round(float(res2.x[0]), 4), d=round(float(res2.x[1]), 5)),
                         rss=float(res2.fun), aic=aic(float(res2.fun), n, 2))
    # binomial shot-noise floor for reference
    out["shot_floor_rss"] = float(np.sum(obs * (1 - obs) / SHOTS))
    return out


def retention(p_ideal, obs):
    return (obs - 0.5) / (p_ideal - 0.5)


def main():
    d = load_windows()
    ks, a = d["ks"], d["a_true"]
    p_id = ideal_curve(a, ks)

    print("=" * 78)
    print("Exp101 — window retention decomposition (Ember C4099, analysis-only)")
    print(f"a_true={a:.6f}  theta={math.degrees(math.asin(math.sqrt(a))):.2f} deg")
    print("=" * 78)

    report = {"experiment": "exp101_window_retention_decomposition", "cycle": 4099,
              "author": "ember", "inputs": ["exp95_qpu_results.json", "exp98_qpu_results.json"],
              "a_true": a, "ideal": [round(x, 5) for x in p_id]}

    for name, obs in [("BAD (Exp95/F78)", d["bad"]), ("GOOD (Exp98/F81)", d["good"])]:
        ret = retention(p_id, obs)
        dev = obs - p_id
        print(f"\n--- {name} window, deep QQQ loader, qubits [54,53,55] ---")
        print("k   p_hw     ideal    dev       retention")
        for k in ks:
            print(f"{k}   {obs[k]:.4f}   {p_id[k]:.4f}   {dev[k]:+.4f}   {ret[k]:.3f}")
        fits = fit_models(p_id, obs, ks)
        print(f"fits: shift c={fits['M_shift']['params']['c']} RSS={fits['M_shift']['rss']:.5f} AIC={fits['M_shift']['aic']:.1f}")
        print(f"      dep   R={fits['M_dep']['params']['R']} RSS={fits['M_dep']['rss']:.5f} AIC={fits['M_dep']['aic']:.1f}")
        print(f"      both  R={fits['M_both']['params']['R']} d={fits['M_both']['params']['d']} RSS={fits['M_both']['rss']:.5f} AIC={fits['M_both']['aic']:.1f}")
        print(f"      shot-noise RSS floor ~ {fits['shot_floor_rss']:.5f}")
        # odd/even asymmetry (k>=1): peaks (odd) vs troughs (even)
        odd = float(np.mean(ret[1::2]))
        even = float(np.mean(ret[2::2]))
        print(f"      retention odd-k (peaks) {odd:.3f} vs even-k (troughs) {even:.3f}"
              f"  -> asymmetry {odd - even:+.3f} (pure depolarizing predicts ~0)")
        key = "bad" if name.startswith("BAD") else "good"
        report[key] = dict(p_hw=[round(x, 5) for x in obs], retention=[round(x, 3) for x in ret],
                           fits=fits, odd_even_asym=round(odd - even, 3))

    # IWM shallow control (good window only)
    p_id_iwm = ideal_curve(d["iwm_a"], ks)
    ret_iwm = retention(p_id_iwm, d["iwm"])
    print("\n--- IWM shallow control (0 2q gates), GOOD window ---")
    print("k   p_hw     ideal    retention")
    for k in ks:
        print(f"{k}   {d['iwm'][k]:.4f}   {p_id_iwm[k]:.4f}   {ret_iwm[k]:.3f}")
    fits_iwm = fit_models(p_id_iwm, d["iwm"], ks)
    print(f"fits: dep R={fits_iwm['M_dep']['params']['R']} RSS={fits_iwm['M_dep']['rss']:.5f} | shot floor {fits_iwm['shot_floor_rss']:.5f}")
    report["iwm_control"] = dict(p_hw=[round(float(x), 5) for x in d["iwm"]],
                                 retention=[round(float(x), 3) for x in ret_iwm], fits=fits_iwm)

    # k0 vs k5 cross-window ordering
    k0_bad = (d["bad"][0] + d["bad_k0_retest"]) / 2
    k0_good = (d["good"][0] + d["good_k0_retest"]) / 2
    err_k0_bad, err_k0_good = abs(k0_bad - a), abs(k0_good - a)
    r5_bad = float(retention(p_id, d["bad"])[5])
    r5_good = float(retention(p_id, d["good"])[5])
    print("\n--- shallow-vs-deep quality across windows (n=2, sign only) ---")
    print(f"k0 plain-read |err| (7 2q gates):   BAD {err_k0_bad:.4f}   GOOD {err_k0_good:.4f}")
    print(f"k5 contrast retention (124 2q):     BAD {r5_bad:.3f}    GOOD {r5_good:.3f}")
    anti = (err_k0_good > err_k0_bad) and (r5_good > r5_bad)
    print(f"ANTI-ORDERED (better deep window has worse shallow read): {anti}")
    report["k0_vs_k5"] = dict(err_k0_bad=round(err_k0_bad, 4), err_k0_good=round(err_k0_good, 4),
                              r5_bad=round(r5_bad, 3), r5_good=round(r5_good, 3), anti_ordered=bool(anti))

    out_path = os.path.join(RESULTS, "exp101_window_retention_decomposition_c4099.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=1)
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
