#!/usr/bin/env python3
"""Q-ARM HARDWARE NOISE RETENTION, calibrated on the executed rungs — Elder C6575.

Produces the VALUE AND SOURCE that prereg amendment A3 (general#2376) requires the n=10 hybrid
freeze to cite, so the gate's noise handling is mechanical from the frozen doc rather than a
number asserted in chat.

WHY IT EXISTS. Ember's A2 correctly pins the gate's noise model to the hardware-calibrated alpha.
That is necessary and NOT sufficient, because there are TWO degradations and alpha covers one:

  (i)  alpha = 0.95 BY DESIGN -> ideal two-copy Bell constraint rate (1+alpha^2)/2 = 0.9512.
  (ii) HARDWARE NOISE on top  -> measured true-P rate 0.8556 at n=8.

(ii) is a further multiplicative retention on the deviation-from-chance, and it is not implied by
pinning alpha. Winner and confuser deviations both scale by it, so the winner-vs-confuser GAP —
the quantity the NO-FLY gate tests — scales by it too.

DIRECTION, which is the whole point: an alpha-pinned but noise-free gate sees a LARGER gap than
the flight will deliver, so it says FLY when reality may be NO-FLY. That is the wrong failure
direction for a safety gate. Note this is OPPOSITE to the C1 side, where noiseless-ideal makes the
classical arm cheaper and is therefore correctly conservative. The asymmetry is real and each arm
needs its own treatment.

USE: retention(10) is the factor to apply to alpha-ideal rates before evaluating the gate. Use the
LOW end of the extrapolation.
"""
import json, os

ALPHA = 0.95
IDEAL = (1 + ALPHA ** 2) / 2            # frozen c5003 two-copy Bell rate = 0.9512
# measured true-P constraint rates on the EXECUTED rungs (all three seals revealed & correct)
MEASURED = {4: 0.8833, 6: 0.8750, 8: 0.8556}
SOURCES = {
    4: "exp142_p1_c1_curve_n4 / Q job d9hr6n50k0jc738ild80 (revealed XZIY)",
    6: "Whisper C5008 confusion spectrum + Elder recompute / job d9hrarshonhs73adh7og (revealed IYXZXY)",
    8: "exp142_p1_qarm_confusion_n8_elder_c6575 / job d9hroc3sbqfc73eqi98g (revealed IZYXZXZZ)"}


def retention(n, table=None):
    """Fraction of the alpha-ideal deviation-from-chance that survives hardware, at rung n."""
    t = table or MEASURED
    return (t[n] - 0.5) / (IDEAL - 0.5)


def extrapolate(n_target=10):
    r = {n: retention(n) for n in sorted(MEASURED)}
    ns = sorted(r)
    slope = (r[ns[-1]] - r[ns[0]]) / (ns[-1] - ns[0])        # linear in n
    return r, slope, r[ns[-1]] + slope * (n_target - ns[-1])


def main():
    r, slope, r10 = extrapolate(10)
    print(f"alpha = {ALPHA}   alpha-ideal two-copy Bell rate = {IDEAL:.4f}\n")
    print(f"{'n':>2} {'measured':>9} {'retention':>10}   source")
    for n in sorted(r):
        print(f"{n:>2} {MEASURED[n]:>9.4f} {r[n]:>10.3f}   {SOURCES[n]}")
    print(f"\nretention slope {slope:+.4f}/qubit  ->  n=10 retention {r10:.3f}")
    print(f"gap inflation if the gate omits it: {1/r10:.2f}x  (gate too permissive by that factor)")

    tp, ru = 0.8556, 0.8000                                  # measured n=8 winner / best confuser
    itp, iru = 0.5 + (tp - .5) / r[8], 0.5 + (ru - .5) / r[8]
    print(f"\nsanity check on the real n=8 pair:")
    print(f"  measured   winner {tp:.4f}  confuser {ru:.4f}  gap {tp-ru:.4f}")
    print(f"  alpha-ideal winner {itp:.4f}  confuser {iru:.4f}  gap {itp-iru:.4f}"
          f"  = {(itp-iru)/(tp-ru):.2f}x larger than the flight delivered")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "exp142_p1_q_noise_retention_elder_c6575.json")
    json.dump({"alpha": ALPHA, "alpha_ideal_bell_rate": IDEAL,
               "measured_true_P_rates": MEASURED, "sources": SOURCES,
               "retention_per_rung": r, "slope_per_qubit": slope,
               "retention_n10_extrapolated": r10,
               "gap_inflation_if_omitted": 1 / r10,
               "PREREG_USE": "Amendment A3 (general#2376): multiply alpha-ideal rates by this "
                             "retention BEFORE evaluating the n=10 NO-FLY gate. Use the LOW end.",
               "direction": "omitting it makes the gate ANTI-CONSERVATIVE (sees a larger gap than "
                            "the flight delivers -> says FLY when reality may be NO-FLY). Opposite "
                            "to the C1 side, where noiseless-ideal is correctly conservative.",
               "caveat": "3-point linear extrapolation in n — the same weak-link class the gate "
                         "itself was introduced to replace. It is a CORRECTION to a conservative "
                         "direction, not a headline number; if the sim can model the device noise "
                         "directly, prefer that over this extrapolation."},
              open(out, "w"), indent=1)
    print(f"\nSAVED {out}")


if __name__ == "__main__":
    main()
