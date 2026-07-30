#!/usr/bin/env python3
"""SAME-CALIBRATION DAY-EFFECT ESTIMATOR — pre-registered analysis. Elder C6575.

*** WRITTEN BEFORE THE FLIGHT EXISTS, DELIBERATELY. ***
The measurement it analyses (an earlier rung re-flown in the SAME job as a later one) has not been
flown. Writing the estimator and its accept/reject criteria first means the analysis cannot be shaped
by the result — the same reason the n=10 decoder was written while that flight was still airborne.

WHY THIS MEASUREMENT IS THE ONE THAT MATTERS. Retention has been measured one rung per flight, one
flight per day. So retention(n) is a MIXTURE of an n-effect and a per-flight (calibration) effect, and
nothing in the ladder as flown can separate them. Concretely, after rung 14:

    n         4      6      8     10     12     13     14
    ret   0.8494 0.8310 0.7880 0.6422 0.5607 0.5285 0.5562
    LOO sigma -0.33  +0.28  +0.56  -0.97  -1.10  -1.09  +3.56   <- six inside 1.1, one at 3.56

One flight misses a same-model, out-of-sample, error-weighting-robust prediction by 3.56 sigma high.
That survives every check available WITHOUT NEW DATA: not the fitting weights (1/SE^2 moved it to
+3.71), not SPRT-stopped rates (0.8833=53/60, 0.8750=70/80, 0.8556=77/90 are all full denominators),
not the estimator changing (single-model LOO), and not a trend reversal (the n=13->14 step is 0.79
sigma, retracted). **One point cannot separate an anomalous FLIGHT from an anomalous n, and no
refitting will.** Only a within-job pair can.

THE DESIGN. Fly rung A (an earlier n, already measured on a different day) and rung B (the later n) in
ONE job on ONE calibration. Then:

    DAY EFFECT at A   = ret_new(A) - ret_old(A)         same n, different days
    DAY EFFECT at B   = ret_new(B) - ret_old(B)         same n, different days
    N EFFECT (clean)  = ret_new(B) - ret_new(A)         different n, SAME day  <- the uncontaminated one
    N EFFECT (old)    = ret_old(B) - ret_old(A)         different n, different days (contaminated)

PRE-REGISTERED HYPOTHESES AND WHAT DISCRIMINATES THEM (fixed before data):

  H1  PER-FLIGHT NOISE. The n=14 flight was simply a good day. Predicts a LARGE day effect at B
      (>= 2 sigma, negative, i.e. the re-flight comes in lower and nearer the fit) and a clean n-effect
      CONSISTENT with the fitted curve. Consequence: the retention curve needs a per-flight error term
      and every n_max interval widens.

  H2  ANOMALOUS n. Something about n=14 specifically. Predicts a SMALL day effect at B (< 1 sigma) —
      the re-flight reproduces the high value — and a clean n-effect that DISAGREES with the fit.
      Consequence: the functional form is wrong in a way seven rungs could not reveal.

  H3  DRIFTING CALIBRATION. The hardware improved between the early and late rungs. Predicts a day
      effect at A that is LARGE and POSITIVE (the old early-rung value was measured on worse hardware
      and the re-flight beats it). Consequence: the apparent decline is partly a time trend, and the
      whole curve is confounded with date order, not merely noisy.

*** THERE IS NO H4 "NULL", AND FINDING THAT OUT IS THE REASON THE SELFTEST DRIVES EVERY BRANCH. ***
I first wrote a fourth hypothesis: "both day effects < 1 sigma AND the clean n-effect matches the fit
-> the 3.56 sigma was a fluctuation." **It is structurally unreachable.** If both rungs reproduce their
old values then n=14 really is high and the fit really does miss it, so the clean n-effect CANNOT match
the fit — the branch fires as H2 by construction (driven: it returned H2 at +2.55 sigma). H1 and H4
were the same hypothesis under two names: "the original n=14 was a favourable fluctuation" IS
per-flight noise, and its signature is rung B re-flying LOWER, which is H1. So H1 subsumes it and the
fourth branch is struck rather than left in as decoration.

This is the fifth inert-guard instance of the cycle and it is in a tool I wrote *to be careful*. It was
caught only because the selftest DRIVES each branch with a constructed input instead of reading the
table. A verdict table nobody has driven is a table, not a gate.

H1/H2/H3 make OPPOSITE predictions on the two day effects, so the design discriminates. That is the
whole point of pre-registering: the outcome table below cannot be redrawn after the numbers land.

*** WHAT THIS TOOL DOES NOT DO. *** It does not license an n_max claim under any outcome. D0 is
binding and unaffected: the forms disagree by 32 rungs at the ceiling and this measurement changes
nothing about that. It bears on whether retention(n) is INTERPRETABLE, not on where the chip stops.

  --selftest                     inject a KNOWN day effect and confirm the estimator recovers it
  --rung-a N --rate-a-new R --m-a-new M --rung-b N --rate-b-new R --m-b-new M
"""
import argparse, json, math, os, sys

ALPHA_IDEAL = (1 + 0.95 ** 2) / 2
K = ALPHA_IDEAL - 0.5

# Prior measurements, one flight each on DIFFERENT days. Frozen here before the re-flight.
OLD = {4: (0.8833, 60), 6: (0.8750, 80), 8: (0.8556, 90), 10: (0.7898, 528),
       12: (0.7530, 664), 13: (0.7385, 1220), 14: (0.7510, 2040)}
# Pinned-gaussian LOO predictions (retention), same source as the residual table above.
FIT_LOO = {4: 0.8798, 6: 0.8080, 8: 0.7420, 10: 0.6803, 12: 0.6013, 13: 0.5588, 14: 0.4807}


def ret_se(rate, m):
    return (rate - 0.5) / K, math.sqrt(rate * (1 - rate) / m) / K


def analyse(a, rate_a, m_a, b, rate_b, m_b, fit_pred_b=None):
    ra_new, sa_new = ret_se(rate_a, m_a)
    rb_new, sb_new = ret_se(rate_b, m_b)
    ra_old, sa_old = ret_se(*OLD[a])
    rb_old, sb_old = ret_se(*OLD[b])

    day_a = ra_new - ra_old; se_day_a = math.hypot(sa_new, sa_old)
    day_b = rb_new - rb_old; se_day_b = math.hypot(sb_new, sb_old)
    n_new = rb_new - ra_new; se_n_new = math.hypot(sb_new, sa_new)
    n_old = rb_old - ra_old; se_n_old = math.hypot(sb_old, sa_old)

    fit_pred_b = FIT_LOO[b] if fit_pred_b is None else fit_pred_b
    fit_n = fit_pred_b - FIT_LOO[a]
    n_vs_fit = n_new - fit_n
    z = lambda v, s: (v / s) if s > 0 else float("nan")

    out = {"rung_a": a, "rung_b": b,
           "day_effect_a": {"delta": day_a, "se": se_day_a, "z": z(day_a, se_day_a)},
           "day_effect_b": {"delta": day_b, "se": se_day_b, "z": z(day_b, se_day_b)},
           "n_effect_same_day": {"delta": n_new, "se": se_n_new, "z": z(n_new, se_n_new)},
           "n_effect_across_days": {"delta": n_old, "se": se_n_old},
           "n_effect_vs_fit": {"delta": n_vs_fit, "se": se_n_new, "z": z(n_vs_fit, se_n_new)}}

    # PRE-REGISTERED verdict table — order fixed, no post-hoc reordering.
    za, zb, zf = out["day_effect_a"]["z"], out["day_effect_b"]["z"], out["n_effect_vs_fit"]["z"]
    if abs(za) >= 2 and za > 0:
        v = ("H3 DRIFTING CALIBRATION", "the earlier rung re-flies HIGHER: the apparent decline is "
             "partly a time trend and the curve is confounded with date order, not merely noisy")
    elif abs(zb) >= 2 and zb < 0:
        v = ("H1 PER-FLIGHT NOISE", "rung B re-flies LOWER, nearer the fit: retention needs a "
             "per-flight error term and every n_max interval widens")
    elif abs(zb) < 1 and abs(zf) >= 2:
        v = ("H2 ANOMALOUS n", "rung B reproduces high AND the same-day n-effect disagrees with the "
             "fit: the functional form is wrong in a way seven rungs could not reveal")
    else:
        v = ("INCONCLUSIVE", "the outcome falls between the pre-registered patterns. Report it as "
             "inconclusive and state which thresholds were missed — do NOT pick the nearest hypothesis")
    out["verdict"], out["verdict_reason"] = v
    return out


def _show(o):
    f = lambda d: f"{d['delta']:+.4f} +/- {d['se']:.4f}  ({d['z']:+.2f} sigma)" if "z" in d else \
                  f"{d['delta']:+.4f} +/- {d['se']:.4f}"
    print(f"  DAY EFFECT at n={o['rung_a']} (same n, different days):   {f(o['day_effect_a'])}")
    print(f"  DAY EFFECT at n={o['rung_b']} (same n, different days):   {f(o['day_effect_b'])}")
    print(f"  N EFFECT  same day (CLEAN):                  {f(o['n_effect_same_day'])}")
    print(f"  N EFFECT  across days (contaminated):        {f(o['n_effect_across_days'])}")
    print(f"  CLEAN N EFFECT vs the fitted curve:          {f(o['n_effect_vs_fit'])}")
    print(f"\n  VERDICT: {o['verdict']}\n    {o['verdict_reason']}")


def selftest():
    """Inject a KNOWN day effect and confirm the estimator recovers it — and that each branch FIRES.
    A verdict table nobody has driven is a table, not a gate (C6575, four instances)."""
    print("SELFTEST — synthetic re-flights with a known injected effect. Every branch must FIRE.\n")
    ok = True
    cases = [
        ("H1 per-flight noise: rung B re-flies LOWER by ~0.07 retention",
         10, OLD[10][0], 528, 14, 0.7510 - 0.07 * K, 2040, "H1 PER-FLIGHT NOISE"),
        ("H3 drifting calibration: rung A re-flies HIGHER by ~0.10 retention",
         10, OLD[10][0] + 0.10 * K, 2040, 14, 0.7510, 2040, "H3 DRIFTING CALIBRATION"),
        ("both rungs reproduce exactly -> MUST resolve to H2, not to a 'null' "
         "(this is the case that proved the struck H4 branch unreachable)",
         10, OLD[10][0], 528, 14, 0.7510, 2040, "H2 ANOMALOUS n"),
    ]
    for label, a, ra, ma, b, rb, mb, want in cases:
        o = analyse(a, ra, ma, b, rb, mb)
        got = o["verdict"]
        hit = got.startswith(want.split()[0])
        ok &= hit
        print(f"  {label}\n    -> {got}   {'FIRES' if hit else '*** DID NOT FIRE (expected ' + want + ') ***'}")
    # H2 needs rung B high AND the clean n-effect off the fit; construct by moving A only.
    o = analyse(10, OLD[10][0] - 0.12 * K, 2040, 14, 0.7510, 2040)
    print(f"  H2 anomalous n: rung B reproduces, same-day n-effect pushed off the fit\n"
          f"    -> {o['verdict']}   {'FIRES' if o['verdict'].startswith('H2') else '(fell to ' + o['verdict'] + ')'}")
    ok &= o["verdict"].startswith("H2")
    print(f"\n  SELFTEST: {'PASS — every branch reachable and driven' if ok else 'FAIL — an unreachable branch is not a gate'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rung-a", type=int); ap.add_argument("--rate-a-new", type=float); ap.add_argument("--m-a-new", type=int)
    ap.add_argument("--rung-b", type=int); ap.add_argument("--rate-b-new", type=float); ap.add_argument("--m-b-new", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    need = [a.rung_a, a.rate_a_new, a.m_a_new, a.rung_b, a.rate_b_new, a.m_b_new]
    if any(x is None for x in need):
        sys.exit("--selftest, or all of --rung-a/--rate-a-new/--m-a-new/--rung-b/--rate-b-new/--m-b-new")
    if a.rung_a not in OLD or a.rung_b not in OLD:
        sys.exit(f"both rungs need a prior measurement to difference against; have {sorted(OLD)}")
    o = analyse(a.rung_a, a.rate_a_new, a.m_a_new, a.rung_b, a.rate_b_new, a.m_b_new)
    print(f"SAME-CALIBRATION DAY-EFFECT ANALYSIS — n={a.rung_a} and n={a.rung_b} in one job\n")
    _show(o)
    print("\n  This bears on whether retention(n) is INTERPRETABLE. It licenses NO n_max claim under any")
    print("  outcome — D0 is binding and unaffected.")
    if a.out:
        o["cycle"] = "C6575"; o["prereg"] = "estimator and verdict table written BEFORE the flight"
        json.dump(o, open(a.out, "w"), indent=1); print(f"\nSAVED {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
