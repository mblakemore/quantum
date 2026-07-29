#!/usr/bin/env python3
"""Exp142 P1 n=10 HYBRID RUNG — Q-FEASIBILITY GATE (Whisper C5013).

Implements §4.2(b)+(c) of docs/exp142-p1-n10-hybrid-prereg-DRAFT-whisper-c5013.md.
Pre-flight, $0: decides FLY / NO-FLY / INCONCLUSIVE and, on FLY, derives the Bell-sample
budget. Runs the §4.2c SIM VALIDATION GATE first — its n=10 output is invalid unless the
model reproduces the executed n=6 and n=8 spectra.

THE TWO ARMS DO NOT SHARE A NOISE KNOB (Elder #2390 / Ember #2378):
  WINNER arm:   true-P rate = 0.5 + (alpha-ideal − 0.5) × retention(n)
                alpha-ideal = (1+α²)/2 = 0.95125 (two-copy Bell, design α=0.95)
                retention imported from exp142_p1_q_noise_retention_elder_c6575 (A3
                artifact: per-rung job IDs + revealed seals). n=10 value = extrapolate()[2]
                = 0.7573, the CENTRAL linear extrapolation, frozen per Elder #2380 (Ember
                review F1: say what the code does). The parametric sweep below covers the
                band down to retention 0.60, which is where the extrapolation risk lives.
  CONFUSER arm: ideal true rate is EXACTLY 0.5 for every wrong candidate (character-sum
                result, #2384/#2386, Ember-verified analytically + n=3 brute force). The
                observed runner-up elevation is EXTREME-VALUE: max over K=4^n−1 estimates
                of a fair coin at m samples. Exact null: P(max < t) = F_bin(m,0.5)(t)^K.
                On top of the null, the UNCHARACTERISED n=8 excess (+0.078 above null-max
                95th, Elder #2390) is carried as a WORST-CASE additive elevation of the
                best confuser's true rate. Failure direction: the excess makes the gate
                STRICTER (harder to fly), per the A3 safety-direction rule.

DECISION RULES (frozen in the prereg; A5 STRUCK per Elder #2416):
  NO-FLY:        best-confuser true rate ≥ true-P rate (a TRUE-rate ordering √m cannot fix).
                 Under the pinned draw-degenerate model this is a boolean, not a fraction —
                 the original A5 draw-fraction band was INERT (nofly_frac could only be 0.0
                 or 1.0 at any M) and an inert safeguard reads as protection. Struck.
  PARAMETRIC ROBUSTNESS (A5's replacement — the uncertainty here is parametric, not
                 draw-sampling): (1) report the verdict's distance to its boundary in both
                 parameters (excess needed to flip at pinned retention; retention collapse
                 needed at pinned excess); (2) sweep the plausible box
                 retention 0.60–0.80 × excess 0.056–0.160 — if ANY box point is NO-FLY,
                 verdict escalates to INCONCLUSIVE-PARAMETRIC (do not fly on estimates that
                 admit a NO-FLY corner); otherwise the FLIGHT budget freezes at the
                 CONSERVATIVE CORNER of the box, not the pinned point.
  FLY:           budget(m) = smallest m with
                 P(winner_hat − bestconfuser_hat ≥ 3·σ_bin(m)) ≥ 0.95,  σ_bin = √(0.25/m).
                 Ties in argmax count as failure (conservative). If the budget search
                 exhausts without meeting the bar, verdict = NO-DECISION, do not fly
                 (Ember review F2: a FLY-without-budget state must not exist).

EXCESS NOTE (Elder #2416(b), documented not hidden): the +0.078 excess is runner-up MINUS
null-MEDIAN, so it contains ~0.022 of ordinary null-max spread on top of the ~0.056 that
genuinely exceeds the null 95th. Carrying the full 0.078 as a TRUE-rate elevation
double-counts sampling spread once — in the STRICTER direction (bigger budget), so it is
kept; the parametric box (excess up to 0.160) covers both readings.

Usage:
  --validate            run the §4.2c validation gate only (n=6, n=8 known answers)
  --gate --commit <freeze-hash> [--M 200] [--n 10]    full gate (validation runs first)
"""
import argparse, hashlib, json, math, os, sys

import numpy as np
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exp142_p1_q_noise_retention_elder_c6575 import MEASURED, extrapolate, retention  # A3 artifact

ALPHA = 0.95
ALPHA_IDEAL = (1 + ALPHA ** 2) / 2                       # 0.95125 two-copy Bell

# ---- executed-rung known answers (§4.2c targets; sources = flown jobs via A3 artifact +
# ---- confusion-spectrum cards elder_c6575 / whisper_c5008) ----
KNOWN = {
    6: {"m_samples": 80, "measured_winner": 0.8750, "measured_runner": 0.700},
    8: {"m_samples": 90, "measured_winner": 0.8556, "measured_runner": 0.800},
}
# m_samples cross-check (Elder #2390 quantile table): n=6 null-max 5/50/95 = 0.6750/0.7000/
# 0.7375 = 54/56/59 out of 80; n=8 = 0.7000/0.7222/0.7444 = 63/65/67 out of 90. The
# validation gate recomputes these exactly, so a wrong m fails loudly (it did — first run
# of this file used m=85 for n=6 and failed its own gate).
# frozen tolerances (§4.2c: "tolerances frozen with the sim code pin")
TOL_WINNER = 0.005          # winner-rate model vs measured (retention calibration identity)
TOL_NULL_MEDIAN = 0.03      # null-max median vs measured runner-up, WHERE null explains it
N8_EXCESS = 0.078           # the sole real excess: n=8 runner-up MINUS NULL-MAX MEDIAN
                            # (0.800 − 0.7222; it also exceeds the null 95th = "real")

SEP_SD = 3.0
SEP_CONF = 0.95
# parametric robustness box (A5 replacement, Elder #2416): retention x excess
BOX_RETENTION = (0.60, 0.80)
BOX_EXCESS = (0.056, 0.160)
BOX_GRID = 5                # 5x5 grid incl. corners
BUDGET_M_MAX = 20000


def winner_rate(n):
    r = retention(n) if n in MEASURED else extrapolate(n)[2]
    return 0.5 + (ALPHA_IDEAL - 0.5) * r, r


def null_max_quantile(q, m, K):
    """Exact quantile of max over K iid Bin(m, 0.5)/m rates: smallest t=w/m with
    F_bin(w)^K >= q."""
    w = np.arange(m + 1)
    cdf_max = binom.cdf(w, m, 0.5) ** K
    return w[np.searchsorted(cdf_max, q)] / m


def p_argmax_correct(m, p_w, K, confuser_true=0.5):
    """P(winner strictly beats the max of K confusers at m samples). Ties = failure.
    Confusers at confuser_true (0.5 null, or 0.5+excess worst case): the max of K−1 nulls
    and 1 elevated confuser; F_max = F_null^(K−1) · F_conf."""
    w = np.arange(m + 1)
    pmf_w = binom.pmf(w, m, p_w)
    F_null = binom.cdf(w - 1, m, 0.5)                    # strictly below w
    F_conf = binom.cdf(w - 1, m, confuser_true)
    return float(np.sum(pmf_w * (F_null ** (K - 1)) * F_conf))


def p_separation(m, p_w, K, sd, confuser_true):
    """P(winner_hat − max_confuser_hat ≥ sd·σ_bin(m)), exact over the joint support."""
    gap = sd * math.sqrt(0.25 / m)
    w = np.arange(m + 1)
    pmf_w = binom.pmf(w, m, p_w)
    # ceil(x)-1 == floor(x) EXCEPT at integral x (m = 4k^2 for sd=3), where it is
    # floor(x)-1 — off by one in the STRICTER direction (Elder #2416(a)). Intentional:
    # at the exact boundary the separation criterion is read STRICTLY (> gap, not >=).
    # Do not "fix" to floor(): that would weaken the bar precisely at those m.
    thresh = np.ceil((w / m - gap) * m) - 1              # max confuser count strictly below the bar
    thresh = np.clip(thresh, -1, m).astype(int)
    F_null = np.where(thresh >= 0, binom.cdf(thresh, m, 0.5), 0.0)
    F_conf = np.where(thresh >= 0, binom.cdf(thresh, m, confuser_true), 0.0)
    return float(np.sum(pmf_w * (F_null ** (K - 1)) * F_conf))


# ------------------------------------------------------------------ §4.2c validation
def validate():
    print("=== §4.2c SIM VALIDATION GATE — executed-rung known answers ===")
    ok = True
    for n, k in KNOWN.items():
        K = 4 ** n - 1
        model_w, r = winner_rate(n)
        null_med = null_max_quantile(0.50, k["m_samples"], K)
        null_95 = null_max_quantile(0.95, k["m_samples"], K)
        d_w = abs(model_w - k["measured_winner"])
        excess = k["measured_runner"] - null_med
        # winner check: model must hit measured (retention-calibrated — an identity check
        # that the import chain is unbroken, not new information)
        w_ok = d_w <= TOL_WINNER
        # confuser check: n=6 the null must EXPLAIN the runner-up (within tolerance of the
        # median); n=8 the runner-up must EXCEED the null 95th by ≈ the frozen excess
        if n == 6:
            c_ok = abs(excess) <= TOL_NULL_MEDIAN
            c_note = f"runner-up − null-median = {excess:+.4f} (null EXPLAINS it: |Δ| ≤ {TOL_NULL_MEDIAN})"
        else:
            c_ok = (k["measured_runner"] > null_95) and abs(excess - N8_EXCESS) <= 0.01
            c_note = (f"runner-up − null-median = {excess:+.4f} (REAL: exceeds null-95th "
                      f"{null_95:.4f}; frozen excess {N8_EXCESS})")
        ok &= w_ok and c_ok
        print(f"  n={n}: winner model {model_w:.4f} vs measured {k['measured_winner']:.4f} "
              f"(Δ={d_w:.4f}, retention={r:.3f}) {'OK' if w_ok else 'FAIL'}")
        print(f"        null-max median {null_med:.4f} / 95th {null_95:.4f}; {c_note} "
              f"{'OK' if c_ok else 'FAIL'}")
    print(f"\nVALIDATION GATE: {'PASS' if ok else 'FAIL'}")
    return ok


# ------------------------------------------------------------------ §4.2b gate
def _min_budget(p_w, K, conf_true):
    """Smallest m meeting the separation bar; None if the search exhausts."""
    for m in range(20, BUDGET_M_MAX + 1):
        if p_separation(m, p_w, K, SEP_SD, conf_true) >= SEP_CONF:
            return m
    return None


def gate(commit_hash, M, n):
    if not validate():
        sys.exit("§4.2c VALIDATION FAILED — the n=10 gate output is not valid. Stop.")

    K = 4 ** n - 1
    p_w, r_used = winner_rate(n)
    conf_true_worst = 0.5 + N8_EXCESS

    # -- verdict at the pinned point (boolean: TRUE-rate ordering, draw-degenerate) --
    pinned_nofly = conf_true_worst >= p_w

    # -- parametric robustness (A5 replacement, Elder #2416) --
    excess_to_flip = (ALPHA_IDEAL - 0.5) * r_used            # excess at which NO-FLY at pinned retention
    retention_to_flip = N8_EXCESS / (ALPHA_IDEAL - 0.5)      # retention collapse for NO-FLY at pinned excess
    sweep, box_nofly, budgets = [], False, []
    for rr in np.linspace(*BOX_RETENTION, BOX_GRID):
        p_w_r = 0.5 + (ALPHA_IDEAL - 0.5) * rr
        for ex in np.linspace(*BOX_EXCESS, BOX_GRID):
            ct = 0.5 + ex
            if ct >= p_w_r:
                box_nofly = True
                sweep.append({"retention": round(rr, 3), "excess": round(ex, 3), "NO-FLY": True})
                continue
            b = _min_budget(p_w_r, K, ct)
            budgets.append(b)
            sweep.append({"retention": round(rr, 3), "excess": round(ex, 3), "budget": b})

    if pinned_nofly:
        verdict = "NO-FLY"
        flight_budget = None
    elif box_nofly:
        verdict = "INCONCLUSIVE-PARAMETRIC — box contains a NO-FLY corner; tighten estimates, do not fly"
        flight_budget = None
    elif any(b is None for b in budgets):
        verdict = "NO-DECISION — budget search exhausted inside the box; do not fly (F2)"
        flight_budget = None
    else:
        verdict = "FLY"
        flight_budget = max(budgets)                          # CONSERVATIVE CORNER, frozen

    pinned_budget = _min_budget(p_w, K, conf_true_worst)
    frozen_ref = {"m": 110, "p_argmax_correct_null": p_argmax_correct(110, p_w, K, 0.5),
                  "p_argmax_correct_worstcase": p_argmax_correct(110, p_w, K, conf_true_worst)}

    out = {"card": "exp142_p1_n10_q_feasibility_gate", "cycle": "C5013",
           "seed_source_commit": commit_hash, "n": n,
           "model": "draw-degenerate (uniform-P symmetry; retention per-rung) — uncertainty is parametric",
           "winner_true_rate": round(p_w, 4), "retention_used": round(r_used, 4),
           "retention_note": "central linear extrapolation, frozen per Elder #2380 (F1)",
           "retention_source": "exp142_p1_q_noise_retention_elder_c6575 (A3 artifact)",
           "confuser_model": f"extreme-value null (K={K}) + worst-case n=8 excess {N8_EXCESS} "
                             "(contains ~0.022 null spread — double-counted, stricter direction, #2416(b))",
           "VERDICT": verdict,
           "verdict_robustness": {
               "excess_needed_to_flip": round(excess_to_flip, 4),
               "excess_carried": N8_EXCESS,
               "excess_margin_x": round(excess_to_flip / N8_EXCESS, 2),
               "retention_needed_to_flip": round(retention_to_flip, 4),
               "retention_used": round(r_used, 4),
               "retention_margin_x": round(r_used / retention_to_flip, 2)},
           "FLIGHT_BUDGET_bell_samples": flight_budget,
           "flight_budget_rule": "CONSERVATIVE CORNER of the parametric box (Elder #2416), "
                                 f"P(sep >= {SEP_SD} sd) >= {SEP_CONF}",
           "pinned_point_budget": pinned_budget,
           "parametric_box": {"retention": BOX_RETENTION, "excess": BOX_EXCESS,
                              "grid": f"{BOX_GRID}x{BOX_GRID}", "sweep": sweep},
           "frozen_budget_reference": frozen_ref}
    path = os.path.join(HERE, "..", "results", f"exp142_p1_n{n}_qgate_whisper_c5013.json")
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--commit", help="freeze commit hash — §4.1 seed source")
    ap.add_argument("--M", type=int, default=200)
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    if a.validate:
        sys.exit(0 if validate() else 1)
    if a.gate:
        if not a.commit:
            sys.exit("--gate requires --commit (seed rule: sha256 of freeze commit)")
        gate(a.commit, a.M, a.n)
