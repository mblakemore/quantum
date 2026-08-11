#!/usr/bin/env python3
"""G-ABSTAIN — arm-equal abstention gate (Ember's free-discriminator fence, promoted to a gate).

An abstention rate that CORRELATES WITH THE ARM is a free discriminator requiring no physics:
a grader could classify sets by whether they abstain. That is a NO-TEST regardless of what the
science block says. Two-proportion test across arms; alpha frozen at 0.01.

SHIPS WITH A DEMONSTRATED FIRE (Ember #9288): replayed against the FLOWN Cell 2 data that
motivated it (CE 7/40 abstain vs CC 26/40). A gate whose pass has never been contrasted with a
fire does not carry the information its pass implies.
"""
import math, sys

# ALPHA CHOSEN ON COST ASYMMETRY, NOT CONVENTION (C5058, from this gate's own fire-proof).
# At 0.01 the gate refused the gross flown case (7/40 vs 26/40, z=-4.32) but PASSED a 2/40-vs-9/40
# asymmetry (z=-2.27) that would still hand a grader real signal with no physics. For a FENCE the
# two errors are not symmetric: a false REFUSE costs a re-fly; a false PASS ships a contaminated
# claim. So the gate is set to err toward refusing. 0.05 two-sided.
ALPHA_Z = 1.96

def g_abstain(a_abst, a_n, b_abst, b_n):
    p1, p2 = a_abst / a_n, b_abst / b_n
    p = (a_abst + b_abst) / (a_n + b_n)
    se = math.sqrt(max(p * (1 - p) * (1 / a_n + 1 / b_n), 1e-12))
    z = (p1 - p2) / se if se > 0 else 0.0
    return {"rate_A": round(p1, 4), "rate_B": round(p2, 4), "z": round(z, 2),
            "verdict": "REFUSE (arm-correlated abstention — free discriminator)" if abs(z) > ALPHA_Z else "PASS (arms statistically equal)"}

# THE GATE'S OWN DETECTION FLOOR, PRINTED WITH EVERY VERDICT (Ember #9298, verified independently).
# MDE at 80% power, n=40/arm, base rate 5%: alpha 0.01 -> 0.300 | 0.05 -> 0.229 | 0.10 -> 0.194.
# ALPHA IS NEARLY EXHAUSTED AS A LEVER — the floor is set by n=40, not by alpha: reaching a 0.14
# gap needs n=80/arm, 0.09 needs n=160. So a PASS from this gate excludes GROSS arm-correlation
# (>~23%) and says NOTHING about a 10% one. The fixture at 2/40-vs-9/40 (gap 0.175) sits BELOW
# this floor: it refuses because that draw landed favourably, not because the gate reliably
# detects gaps of that size — A SINGLE FIXTURE PASSING JUST OVER THE BAR DEMONSTRATES WIRING,
# NOT COVERAGE.
MDE_80 = 0.229

if __name__ == "__main__":
    print("G-ABSTAIN can-it-fire proof — BOTH directions, one run:\n")
    cases = [
        ("FLOWN Cell 2 (the run that motivated the gate)", 7, 40, 26, 40, "REFUSE"),
        ("healthy: equal abstention, both arms 0/40",       0, 40,  0, 40, "PASS"),
        ("healthy: equal abstention, both arms 5/40",       5, 40,  5, 40, "PASS"),
        ("subtle: 2/40 vs 9/40",                            2, 40,  9, 40, "REFUSE"),
    ]
    for label, aa, an, ba, bn, want in cases:
        r = g_abstain(aa, an, ba, bn)
        got = "REFUSE" if r["verdict"].startswith("REFUSE") else "PASS"
        mark = "✅" if got == want else "🔴"
        print(f"  {mark} {label:<46} A={aa}/{an} B={ba}/{bn}  z={r['z']:+6.2f}  -> {got:<7} (want {want})")
    print(f"\n  ⚖️  LABEL THAT TRAVELS WITH EVERY PASS: canary for arm-correlation above ~{MDE_80:.2f}")
    print( "      (80% power, n=40/arm, base 5%). A pass EXCLUDES GROSS arm-correlation and says")
    print( "      NOTHING about a ~10% one. n is the lever, not alpha: 0.14 needs n=80, 0.09 needs n=160.")
    print("\n  NOTE: at the selected band [0.30,0.70] the PREDICTED abstention is 0/40 in both arms.")
    print("  That prediction is now stated in the prereg, so an observed 0-vs-0 is a CONFIRMED")
    print("  prediction rather than an absence nobody expected either way (Ember #9288).")
