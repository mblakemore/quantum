#!/usr/bin/env python3
"""P1 margin ERROR BARS — permutation bootstrap of the Q SPRT stop time. Elder C6575.

WHY. The curve reports point margins (6.6x / 22.9x / 218.3x). Both meters are SINGLE DRAWS of a
random variable and I should say how wide that is rather than publish three bare numbers:

  - the Q meter is a SEQUENTIAL stop time. It bills however many Bell samples the SPRT needed in
    the ORDER the samples happened to arrive. That order is arbitrary — a favourable early run
    stops sooner. At n=6 the SPRT stopped at 30 samples although the rate (0.875) implies ~41 on
    average, i.e. this particular ordering was lucky and the Q arm was billed LESS than typical.
    A Q meter billed too low INFLATES the margin, so this is the direction that matters.
  - the C1 meter has the analogous dependence on where P sits in the committed walk (handled
    separately in the curve's walk-position decomposition).

Bootstrapping the sample ORDER (not resampling the data) isolates exactly the stop-time variance
while holding the measured constraint rate fixed. Reports the margin as a median + 90% interval.

HONEST SCOPE: this is the variance of the METER given this flight's data. It does NOT capture
shot noise in the underlying rate, nor the single-draw-of-P variance. It makes the published
ratios honest about one specific source of spread, not all of them.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import numpy as np
import exp142_robust_decoder_sim as G2
import exp142_decode_meter as M
from exp142_p1_c1_decoder_elder_c5003 import two_copy_Q, wald_AB
from run_exp66_qpu_partb import _get_ibm_service

RES = os.path.join(HERE, "..", "results")
R_BELL = {4: 0.933, 6: 0.882, 8: 0.846}
P_HAT = {4: "XZIY", 6: "IYXZXY", 8: "IZYXZXZZ"}          # all three now revealed-correct
Q_JOB = {4: "d9hr6n50k0jc738ild80", 6: "d9hrarshonhs73adh7og"}
C1 = {4: "exp142_p1_c1_curve_n4_elder_c6575.json",
      6: "exp142_p1_c1_curve_n6_elder_c6575.json",
      8: "exp142_p1_c1_n8_decode_elder_c6575.json"}
NBOOT = 20000


def main():
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    svc, rows = None, []
    rng = np.random.default_rng(6575)
    for n in (4, 6, 8):
        if n == 8:
            bits = json.load(open(os.path.join(RES, "exp142_p1_n8_qarm_fetch_elder_c6568.json")))["raw_bitstrings"]
        else:
            svc = svc or _get_ibm_service()
            bits = list(M.fetch_pub_bits(svc.job(Q_JOB[n]), 0))
        P = P_HAT[n]; Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
        stream = np.array([int(G2.sp_inner(G2.outcome_to_bits(s, n, mapping), Pb, n)) == want
                           for s in bits])
        rate = stream.mean()
        rb = R_BELL[n]; A, _ = wald_AB(n)
        s_pass, s_fail = math.log(rb / 0.5), math.log((1 - rb) / 0.5)
        as_flown = two_copy_Q(list(stream), n, rb)

        stops = np.empty(NBOOT, dtype=int)
        for b in range(NBOOT):
            perm = rng.permutation(stream)
            llr = np.cumsum(np.where(perm, s_pass, s_fail))
            hit = np.argmax(llr >= A)
            stops[b] = (hit + 1) if llr[hit] >= A else len(perm)     # censored at budget
        cens = float(np.mean(np.cumsum(np.where(stream, s_pass, s_fail))[-1] < A))

        c1 = json.load(open(os.path.join(RES, C1[n])))["result"]["C1_distinct_copies"]
        mar = c1 / (2 * stops)
        lo, med, hi = np.percentile(mar, [5, 50, 95])
        rows.append((n, rate, as_flown, int(np.median(stops)), int(np.percentile(stops, 5)),
                     int(np.percentile(stops, 95)), c1, c1 / (2 * as_flown), med, lo, hi))
        print(f"n={n}: rate {rate:.4f}  as-flown stop {as_flown:>3} samples | "
              f"bootstrap median {int(np.median(stops)):>3} [{int(np.percentile(stops,5))}-"
              f"{int(np.percentile(stops,95))}]  censored {100*cens:.0f}%", flush=True)

    print("\n" + "=" * 92)
    print("MARGIN WITH METER ERROR BARS (Q stop-time permutation bootstrap, n=20000)")
    print("=" * 92)
    print(f"{'n':>2} | {'as-flown':>9} | {'bootstrap median':>17} | {'90% interval':>18} | as-flown vs median")
    print("-" * 92)
    for (n, rate, af, sm, s5, s95, c1, m_af, med, lo, hi) in rows:
        flag = "FLATTERED" if m_af > med * 1.05 else ("conservative" if m_af < med * 0.95 else "typical")
        print(f"{n:>2} | {m_af:>8.1f}x | {med:>16.1f}x | {lo:>7.1f}x - {hi:<8.1f}x | {flag}")
    print("-" * 92)
    print("as-flown > median  =>  this flight's sample ORDER stopped the Q SPRT early,")
    print("                       billing the quantum arm too little and INFLATING the ratio.")

    out = os.path.join(RES, "exp142_p1_margin_bootstrap_elder_c6575.json")
    json.dump({"n_bootstrap": NBOOT, "method": "permutation of Bell-sample ORDER, rate held fixed",
               "per_rung": [{"n": n, "constraint_rate": rate, "stop_as_flown": af,
                             "stop_median": sm, "stop_p5": s5, "stop_p95": s95,
                             "C1_copies": c1, "margin_as_flown": m_af, "margin_median": med,
                             "margin_p5": lo, "margin_p95": hi} for
                            (n, rate, af, sm, s5, s95, c1, m_af, med, lo, hi) in rows],
               "scope": "variance of the Q METER given this flight's data only; does NOT include "
                        "shot noise in the rate, nor single-draw-of-P variance (see the curve's "
                        "walk-position decomposition for the C1 side)"},
              open(out, "w"), indent=1)
    print(f"\nSAVED {out}")


if __name__ == "__main__":
    main()
