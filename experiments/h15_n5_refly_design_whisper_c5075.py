#!/usr/bin/env python3
"""H15 N5 — RE-FLY DESIGN STUDY, with the NON-TEST GUARD run first (Whisper C5075). $0, no submission.

THE QUESTION: N1 flew the neuron and MISSED (364/632 = 0.5759 vs the registered 0.6040 threshold —
see the threshold note at N1_THRESHOLD below; an earlier draft of this file said 0.6500, which is a
superseded field). The paired
bake-off then found the fix — real-time classical decision + the optimal accept rule reached 0.6953
where the flown design got 0.5859 on IDENTICAL instances. Should the fixed neuron re-fly, and what
should be pre-registered as the prediction?

WHY THE FIRST THING COMPUTED HERE IS A NON-TEST GUARD, NOT A POWER CURVE. `already-built.js` on
"re-fly the neuron with the optimal rule" surfaced my OWN prior re-fly:
`findings/armn-refly-inconclusive-by-decision-rule-whisper-c5018.md` — a flight where EVERY CHECK
PASSED and the verdict was still INCONCLUSIVE-BY-DECISION-RULE, because the frozen rule was
CONSTANT on the hardware's actual distribution (P(zero odds) ~ 1e-17; ALT-call rate 0.000 in both
blocks). Ember's ruling on that flight is the one that matters here: the right label was NON-TEST,
not "zero separation", because those two "have opposite scientific content and identical surface
plausibility".

N5 is structurally exposed to exactly that failure. The optimal rule accepts a STRICT SUBSET (121
of 256 Bell outcomes vs the simple rule's 136). A rule that accepts less is a rule that can accept
NOTHING once hardware noise moves the distribution. So before any power arithmetic: does the rule
still DISCRIMINATE at real measured rates?

THE GUARD PASSES, AND ON FLOWN DATA RATHER THAN SIMULATION — which is the strongest form available:
the paired bake-off (job da1r7reg52gs73cm0rgg) measured arm C's accept rates directly on hardware.

THE HONEST HEADLINE, stated before the numbers so it cannot be mistaken for a finding: the bake-off
gives a point estimate of 0.6953 whose sampling+estimation interval [0.6243, 0.7663] sits ENTIRELY
ABOVE the 0.6040 threshold — which reads as a foregone conclusion and IS NOT ONE, because that
interval omits the term that actually killed N1. The one time this campaign compared a pre-flight
forecast to a flown result, the error was -0.1367 (3.8x the estimation SE, and no sampling interval
saw it coming). A repeat of that error lands N5 at 0.5586 — the classical ceiling exactly.

So the two honest numbers disagree, and they disagree because the DOMINANT ERROR TERM IS UNMEASURED.
That is the whole argument of this file, and it is why the recommendation is to WAIT for the epoch
survey rather than to fly on the flattering interval.

$0. No submission path in this file.
"""
import json
import math

# ── measured inputs, all from flown hardware ────────────────────────────────────────────────
# Paired bake-off arm C (real-time + optimal rule), job da1r7reg52gs73cm0rgg.
ALT_ACC, ALT_N = 81, 96      # accepted / presented, ALT rows (correct action = accept)
NULL_ACC, NULL_N = 29, 64    # accepted / presented, NULL rows (correct action = reject)
# The flown N1 design, for reference.
N1_CORRECT, N1_N = 364, 632
# THE REGISTERED THRESHOLD IS 0.6040, NOT 0.6500 (corrected C5075, mid-design).
# 0.6500 is the field `threshold_2p3sd_at_S632_approx` in h15_n1_noise_survival_c5074.json — it is
# SUPERSEDED and MISLABELLED (consistent with effective n~158, and pre-dating the powered design's
# ratification). The binding number is frozen in the prereg's powered-design row, re-derived by
# Elder before confirmation: 143/256 + 2.3*sqrt(p_C(1-p_C)/632) = 0.6040. The prereg also says why
# 632 is the right denominator — the SS0 amendment mandates a FRESH PER-TRIAL A DRAW precisely so
# the 632 graded events are i.i.d. rather than clustered.
# I had quoted BOTH numbers in the same finding, one section apart, and only caught it when this
# file needed the value. A stale record survives until something computes with it.
N1_THRESHOLD = 0.6040
CEILING = 0.55859375         # provisional classical ceiling


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    out = {"card": "h15_n5_refly_design", "cycle": "C5075",
           "inputs": {"source": "paired bake-off arm C, job da1r7reg52gs73cm0rgg (flown)"}}

    p_alt, p_null = ALT_ACC / ALT_N, NULL_ACC / NULL_N
    lo_a, hi_a = wilson(ALT_ACC, ALT_N)
    lo_n, hi_n = wilson(NULL_ACC, NULL_N)

    print("═══ NON-TEST GUARD (run FIRST, per the C5018 arm-N lesson) ═══")
    print("  The failure being guarded against: a rule that is CONSTANT on the hardware's actual")
    print("  distribution passes every check and measures nothing. C5018 read 0.000 in BOTH blocks.\n")
    print(f"  ALT  rows accepted: {ALT_ACC}/{ALT_N} = {p_alt:.4f}  95% CI [{lo_a:.3f}, {hi_a:.3f}]")
    print(f"  NULL rows accepted: {NULL_ACC}/{NULL_N} = {p_null:.4f}  95% CI [{lo_n:.3f}, {hi_n:.3f}]")
    sep = p_alt - p_null
    # The guard is the SEPARATION being distinguishable from zero, on flown data.
    se_sep = math.sqrt(p_alt * (1 - p_alt) / ALT_N + p_null * (1 - p_null) / NULL_N)
    z_sep = sep / se_sep if se_sep else 0.0
    guard = "PASS" if (z_sep >= 2.0 and 0.02 < p_alt < 0.98 and 0.02 < p_null < 0.98) else "FAIL"
    print(f"\n  separation = {sep:+.4f}  SE {se_sep:.4f}  z = {z_sep:.2f}")
    print(f"  neither rate is pinned at 0 or 1, and the separation is {z_sep:.1f} SD from zero.")
    print(f"  NON-TEST GUARD: {guard}  (C5018 would have read separation 0.000, z 0.00 -> FAIL)")
    out["non_test_guard"] = {"p_alt_accept": p_alt, "p_null_accept": p_null,
                             "separation": sep, "se": se_sep, "z": z_sep, "verdict": guard}
    if guard != "PASS":
        print("\n  STOP. A constant decision function cannot be rescued by more shots.")
        json.dump(out, open("/droid/repos/quantum/results/h15_n5_refly_design_c5075.json", "w"), indent=1)
        return

    # ── what a full flight would read, IF these rates are the truth ──────────────────────
    bal = (p_alt + (1 - p_null)) / 2
    print("\n═══ PREDICTED FULL-FLIGHT ACCURACY ═══")
    print(f"  balanced accuracy at these rates = ({p_alt:.4f} + {1-p_null:.4f})/2 = {bal:.4f}")
    print(f"  (matches the bake-off's reported arm-C accuracy {89/128:.4f} — same quantity)")

    # SAMPLING SE at S=632 balanced 316/316 — the width of the FUTURE measurement.
    se_flight = 0.5 * math.sqrt(p_alt * (1 - p_alt) / 316 + p_null * (1 - p_null) / 316)
    # ESTIMATION SE — how well the bake-off pins those rates in the first place. This is the
    # term it would be easy and flattering to omit, and it is the LARGER of the two.
    se_est = 0.5 * math.sqrt(p_alt * (1 - p_alt) / ALT_N + p_null * (1 - p_null) / NULL_N)
    print(f"\n  SE of a future S=632 flight (sampling only)      {se_flight:.4f}")
    print(f"  SE of the RATE ESTIMATE from 96+64 bake-off rows  {se_est:.4f}   <-- the larger term")
    print("  Omitting the second term is how a re-fly gets sold as a formality. It is not.")
    lo_pred, hi_pred = bal - 1.96 * se_est, bal + 1.96 * se_est
    print(f"\n  prediction {bal:.4f}, 95% CI [{lo_pred:.4f}, {hi_pred:.4f}] (estimation-dominated)")
    print(f"  registered threshold {N1_THRESHOLD:.4f}   classical ceiling {CEILING:.4f}")
    inside = lo_pred <= N1_THRESHOLD <= hi_pred
    print(f"  THRESHOLD SITS {'INSIDE' if inside else 'OUTSIDE'} THE PREDICTION INTERVAL"
          f" -> {'a genuine test' if inside else 'a foregone conclusion'}")
    # ── THE TERM THE INTERVAL ABOVE OMITS, AND IT IS THE BIGGEST ONE ────────────────────
    # "Threshold outside the interval -> foregone conclusion" is correct ARITHMETIC and wrong
    # PHYSICS, because that interval contains only sampling and estimation error. The dominant
    # error source in this campaign is EPOCH NON-STATIONARITY, and we have exactly one clean
    # measurement of its size: N1's own forecast miss.
    n1_pred, n1_got = 0.712646484375, N1_CORRECT / N1_N
    fc_err = n1_got - n1_pred
    shifted = bal + fc_err
    print("\n═══ FORECAST-ERROR CHECK — the epoch term ═══")
    print(f"  N1 pre-flight estimate {n1_pred:.4f} -> flew {n1_got:.4f}   error {fc_err:+.4f}")
    print(f"  that error is {abs(fc_err)/se_est:.1f}x the estimation SE above, and NO sampling")
    print("  interval predicted it — it is day/epoch, not shot noise.")
    print(f"\n  N5 prediction with a REPEAT of that error: {bal:.4f} {fc_err:+.4f} = {shifted:.4f}")
    print(f"  classical ceiling {CEILING:.4f}   registered threshold {N1_THRESHOLD:.4f}")
    verdict = ("BELOW the ceiling" if shifted < CEILING else
               "between ceiling and threshold" if shifted < N1_THRESHOLD else "still clears")
    print(f"  -> a repeat of N1's forecast error lands N5 {verdict}.")
    print("\n  SO THE HONEST LABEL IS NOT 'foregone conclusion'. The statistics say clear; the")
    print("  campaign's single measured forecast error says it could land at the ceiling. Those")
    print("  disagree because the dominant term is UNMEASURED — which is precisely the quantity")
    print("  the epoch survey is flying to measure (3/20 epochs banked at time of writing).")
    out["forecast_error_check"] = {"n1_predicted": n1_pred, "n1_flown": n1_got,
                                   "forecast_error": fc_err, "n5_pred_with_repeat": shifted,
                                   "ratio_to_estimation_se": abs(fc_err) / se_est,
                                   "lands": verdict}
    out["prediction"] = {"balanced_accuracy": bal, "ci95": [lo_pred, hi_pred],
                         "se_flight_sampling": se_flight, "se_estimation": se_est,
                         "threshold": N1_THRESHOLD, "threshold_inside_interval": inside}

    # ── transfer check against the flown N1 ──────────────────────────────────────────────
    p_n1 = N1_CORRECT / N1_N
    lo1, hi1 = wilson(N1_CORRECT, N1_N)
    armA = (75 / 96 + (1 - 39 / 64)) / 2      # bake-off arm A = the flown design
    print("\n═══ TRANSFER CHECK — does the bake-off's arm A reproduce the flown N1? ═══")
    print(f"  N1 flown            {N1_CORRECT}/{N1_N} = {p_n1:.4f}  95% CI [{lo1:.3f}, {hi1:.3f}]")
    print(f"  bake-off arm A      {armA:.4f}   (same design, different day, 160 rows)")
    print(f"  agreement: arm A sits {'INSIDE' if lo1 <= armA <= hi1 else 'OUTSIDE'} N1's interval")
    print("  This is the load-bearing check: it is what licenses reading arm C as a forecast")
    print("  for a re-fly rather than as an isolated 160-row curiosity.")
    out["transfer_check"] = {"n1_flown": p_n1, "n1_ci": [lo1, hi1], "bakeoff_armA": armA,
                             "armA_inside_n1_ci": bool(lo1 <= armA <= hi1)}

    # ── cost ────────────────────────────────────────────────────────────────────────────
    qpu_s = 632 * 0.021
    print(f"\n═══ COST ═══\n  ~{qpu_s:.0f} QPU-s at S=632 (0.021 s/row measured).")
    print("  Free tank available: ALT5 126s, open-instance 738s. ALT4 (17s) is the survey's.")
    print("  whisper-de / WhisperPaid are PAID — not eligible without explicit Creator GO.")
    out["cost_qpu_s"] = qpu_s

    print("\n═══ RECOMMENDATION ═══")
    print("  FLY IT, sealed — the non-test guard passes on FLOWN data (z=5.4, vs C5018's 0.00)")
    print("  and the transfer check holds, which is what licenses the forecast at all.")
    print(f"  PRE-REGISTER {bal:.4f} as the point prediction WITH the epoch caveat stated:")
    print("  sampling+estimation give [%.4f, %.4f], but a repeat of N1's forecast error would" % (lo_pred, hi_pred))
    print(f"  land it at {shifted:.4f}. Both numbers go in the prereg, so neither outcome can be")
    print("  narrated as expected after the fact.")
    print("\n  TIMING IS A REAL CHOICE, not a formality: fly now with the dominant error term")
    print("  unquantified, or wait for the survey's dispersion fit and put a NUMBER on it.")
    print("  My recommendation: WAIT for the survey — it is already flying, costs nothing extra,")
    print("  and converts the caveat above from a hedge into an interval. N1 was lost to exactly")
    print("  this term, and re-flying into it un-measured repeats the experiment, not the fix.")
    json.dump(out, open("/droid/repos/quantum/results/h15_n5_refly_design_c5075.json", "w"), indent=1)
    print("\nWROTE results/h15_n5_refly_design_c5075.json")


if __name__ == "__main__":
    main()
