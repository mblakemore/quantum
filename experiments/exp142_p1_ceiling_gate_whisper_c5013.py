#!/usr/bin/env python3
"""CEILING HUNT — per-rung feasibility gate (Whisper C5013). FROZEN prereg @ 2adf197f.

Implements the prereg's per-rung GATE step ($0):
  - retention predictions from ALL THREE candidate forms in Elder's PINNED artifact
    (results/exp142_p1_retention_form_elder_c6575.json — params imported, never re-fit here;
    mid-arc updates are Elder's mechanical re-run of the pinned fitter, D3);
  - feasibility per form: NO-FLY iff worst-case confuser true rate >= that form's winner rate
    (a TRUE-rate ordering no budget fixes);
  - D4-MANDATORY trigger (corrected, feasibility-within-rung-cap): do the forms DISAGREE on
    whether ANY budget <= the rung cap can fly this rung? (Disclosed dormant for 12-18.)
  - SIZING (double margin, frozen D3): winner rate from the LOW-END form across all three
    (the retention axis of the old box, now data-driven), excess at the BOX MAXIMUM 0.160
    (the conservative corner of the excess axis — this is what produced the n=10 corner
    budget 528, and carrying only the pinned 0.078 here would silently under-size), budget =
    smallest m with P(separation >= 3 sd) >= 0.95 — the EXACT frozen criterion via the
    reviewed n=10 p_separation machinery, imported not reimplemented. The NO-FLY true-rate
    ordering test keeps the pinned excess 0.078 (the frozen verdict rule), sizing keeps 0.160.

Usage: python3 exp142_p1_ceiling_gate_whisper_c5013.py --n 12 [--rung-cap-s 40]
"""
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exp142_p1_n10_qgate_whisper_c5013 import (ALPHA_IDEAL, N8_EXCESS,      # frozen court code
                                               SEP_CONF, SEP_SD, p_separation)

FREEZE = "2adf197ff7e472683e7aefd60ea46b307fa1a4e4"
ARTIFACT = os.path.join(HERE, "..", "results", "exp142_p1_retention_form_elder_c6575.json")
SECONDS_PER_1000_SAMPLES = 7.6   # measured: n=10 flight, 528 samples = 4 QPU-s
EXCESS_SIZING = 0.160            # box maximum — the conservative corner of the excess axis


def form_retention(fit, n):
    p = fit["params"]
    if "linear" in fit["form"]:
        return p["a"] + p["b"] * n
    if "per-qubit" in fit["form"]:
        return p["A"] * p["c"] ** n
    return p["A"] * math.exp(-p["b"] * n * n)


def min_budget(p_w, K, conf_true, m_cap):
    for m in range(20, m_cap + 1):
        if p_separation(m, p_w, K, SEP_SD, conf_true) >= SEP_CONF:
            return m
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--rung-cap-s", type=float, default=40.0)
    a = ap.parse_args()
    n, K = a.n, 4 ** a.n - 1
    art = json.load(open(ARTIFACT))
    m_cap = int(a.rung_cap_s / SECONDS_PER_1000_SAMPLES * 1000)
    conf_true = 0.5 + N8_EXCESS          # frozen VERDICT rule (true-rate ordering)
    conf_size = 0.5 + EXCESS_SIZING      # box-corner excess for SIZING only

    per_form = {}
    for name, fit in art["fits"].items():
        r = form_retention(fit, n)
        p_w = 0.5 + (ALPHA_IDEAL - 0.5) * r
        nofly = conf_true >= p_w
        b = None if nofly else min_budget(p_w, K, conf_size, m_cap)
        per_form[name] = {"retention": round(r, 4), "winner_rate": round(p_w, 4),
                          "NO_FLY_true_rate_ordering": nofly,
                          "feasible_within_rung_cap": b is not None, "budget_at_own_r": b}

    feas = [v["feasible_within_rung_cap"] for v in per_form.values()]
    d4_mandatory = len(set(feas)) > 1                       # forms DISAGREE on feasibility-within-cap
    low_form = min(per_form, key=lambda k: per_form[k]["retention"])
    r_low = per_form[low_form]["retention"]
    p_w_low = 0.5 + (ALPHA_IDEAL - 0.5) * r_low
    if conf_true >= p_w_low and all(v["NO_FLY_true_rate_ordering"] for v in per_form.values()):
        verdict, budget = "NO-FLY (unanimous true-rate ordering) — D4 test-once applies", None
    elif not any(feas):
        verdict, budget = "NO-FLY (no form feasible within rung cap) — D4 test-once applies", None
    else:
        budget = min_budget(p_w_low, K, conf_size, m_cap)
        if budget is None:
            verdict = ("INCONCLUSIVE-SIZING: low-end form infeasible within rung cap but others "
                       "feasible — D4-MANDATORY (forms disagree)")
        else:
            verdict = "FLY"

    out = {"card": "exp142_p1_ceiling_gate", "rung_n": n, "freeze_commit": FREEZE,
           "retention_artifact": "exp142_p1_retention_form_elder_c6575.json (pinned)",
           "per_form": per_form, "low_end_form": low_form,
           "sizing": {"r_low": round(r_low, 4), "winner_rate_low": round(p_w_low, 4),
                      "excess_verdict": N8_EXCESS, "excess_sizing_box_corner": EXCESS_SIZING, "criterion": f"P(sep>={SEP_SD}sd)>={SEP_CONF}"},
           "D4_mandatory_trigger_fired": d4_mandatory,
           "VERDICT": verdict, "FLIGHT_BUDGET_bell_samples": budget,
           "est_qpu_seconds": None if budget is None else round(budget / 1000 * SECONDS_PER_1000_SAMPLES, 1),
           "rung_cap_seconds": a.rung_cap_s, "m_cap_samples": m_cap}
    path = os.path.join(HERE, "..", "results", f"exp142_p1_ceiling_gate_n{n}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
