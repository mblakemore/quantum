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
                artifact: per-rung job IDs + revealed seals; n=10 by low-end extrapolation).
  CONFUSER arm: ideal true rate is EXACTLY 0.5 for every wrong candidate (character-sum
                result, #2384/#2386, Ember-verified analytically + n=3 brute force). The
                observed runner-up elevation is EXTREME-VALUE: max over K=4^n−1 estimates
                of a fair coin at m samples. Exact null: P(max < t) = F_bin(m,0.5)(t)^K.
                On top of the null, the UNCHARACTERISED n=8 excess (+0.078 above null-max
                95th, Elder #2390) is carried as a WORST-CASE additive elevation of the
                best confuser's true rate. Failure direction: the excess makes the gate
                STRICTER (harder to fly), per the A3 safety-direction rule.

DECISION RULES (frozen in the prereg):
  NO-FLY:        best-confuser true rate ≥ true-P rate in > 5% of draws
                 (√m cannot fix a wrong ordering of TRUE rates).
  INCONCLUSIVE:  observed NO-FLY fraction in 3–8% → raise M to ≥1000, re-run (A5).
  FLY:           otherwise; budget = smallest m with
                 P(winner_hat − bestconfuser_hat ≥ 3·σ_bin(m)) ≥ 0.95,  σ_bin = √(0.25/m),
                 computed with the worst-case excess carried. Ties in argmax count as
                 failure (conservative).

Under the pinned model the per-draw rates are draw-independent (uniform-P symmetry of the
null; retention is per-rung not per-P), so the M-draw loop is degenerate here by
construction — kept explicit so any future per-P model (e.g. weight-dependent retention)
drops in without changing the decision plumbing. Draw-degeneracy is REPORTED, not hidden.

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

NOFLY_FRAC = 0.05
INCONCLUSIVE_BAND = (0.03, 0.08)
SEP_SD = 3.0
SEP_CONF = 0.95


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
    thresh = np.ceil((w / m - gap) * m) - 1              # max count c with c/m <= w/m - gap ... strict
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
def gate(commit_hash, M, n):
    if not validate():
        sys.exit("§4.2c VALIDATION FAILED — the n=10 gate output is not valid. Stop.")
    master = hashlib.sha256(commit_hash.encode()).hexdigest()     # §4.1 seed rule (parity
    # with the C1 sim; the pinned model is draw-degenerate, see docstring — seeded anyway)

    K = 4 ** n - 1
    p_w, r_used = winner_rate(n)
    conf_true_worst = 0.5 + N8_EXCESS                    # worst-case excess carried forward

    # NO-FLY test over M draws (draw-degenerate under pinned model — reported as such)
    nofly_frac = float(np.mean([conf_true_worst >= p_w for _ in range(M)]))
    if nofly_frac > NOFLY_FRAC:
        verdict = "NO-FLY"
    elif INCONCLUSIVE_BAND[0] <= nofly_frac <= INCONCLUSIVE_BAND[1]:
        verdict = "INCONCLUSIVE — raise M to ≥1000 and re-run (A5)"
    else:
        verdict = "FLY"

    # budget derivation (FLY only): smallest m meeting the separation bar, worst case
    budget = None
    frozen_ref = {}
    if verdict == "FLY":
        for m in range(20, 20001):
            if p_separation(m, p_w, K, SEP_SD, conf_true_worst) >= SEP_CONF:
                budget = m
                break
        frozen_ref = {"m": 110, "p_argmax_correct_null": p_argmax_correct(110, p_w, K, 0.5),
                      "p_argmax_correct_worstcase": p_argmax_correct(110, p_w, K, conf_true_worst)}

    out = {"card": "exp142_p1_n10_q_feasibility_gate", "cycle": "C5013",
           "seed_source_commit": commit_hash, "n": n, "M": M,
           "draw_degenerate_under_pinned_model": True,
           "winner_true_rate": round(p_w, 4), "retention_used": round(r_used, 4),
           "retention_source": "exp142_p1_q_noise_retention_elder_c6575 (A3 artifact)",
           "confuser_model": f"extreme-value null (K={K}) + worst-case n=8 excess {N8_EXCESS}",
           "nofly_fraction": nofly_frac, "VERDICT": verdict,
           "derived_bell_sample_budget": budget,
           "frozen_budget_reference": frozen_ref,
           "budget_rule": f"smallest m with P(sep >= {SEP_SD} sd) >= {SEP_CONF}, worst-case excess carried"}
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
