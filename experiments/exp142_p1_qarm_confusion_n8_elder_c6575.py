#!/usr/bin/env python3
"""P1 Q-arm n=8 CONFUSION SPECTRUM — how lucky was the 1.4-SE call, and what does n=10 need?

Elder C6575, after the reveal. Turning a hedge into a measured quantity.

THE QUESTION. At n=8 the Q arm won its argmax by 0.056 over the runner-up — about 1.4 SE at 90
Bell samples. It was CORRECT (seal revealed IZYXZXZZ). But a naive multiple-comparisons argument
says an argmax over 4^8-1 = 65535 candidates needs the winner to clear the NULL MAXIMUM, and for
65535 independent Gaussians that is ~4.4 SE. We won at 1.4. Two possible reasons:

  (a) genuine luck  -> the n=8 verdict was fragile and n=10 is reckless at any similar budget; or
  (b) the nulls are NOT independent -> candidates sharing structure with the true P are correlated,
      the effective number of independent comparisons is far below 4^n-1, and the real bar is the
      observed null MAX, not the Gaussian-independent one.

These have OPPOSITE implications for n=10 sizing, so guessing is not acceptable. The n=8 data
already on disk answers it directly: compute the constraint rate for ALL 65535 candidates and look
at the actual null distribution. No extrapolation, no new QPU.

WHAT IT REPORTS
  - full rate spectrum: true-P rate, runner-up, null mean/sd, observed null MAX
  - the winner's margin over the null BULK and over the null MAX, both in null-sd units
  - the EMPIRICAL upper tail (a Gaussian null model is fitted and REJECTED — it implies more
    effective comparisons than candidates exist, so the tail is reported by direct count instead)
  - a shot budget for n=10 derived from the MEASURED null width, not a Gaussian assumption

ANSWER (n=8): (a). The winner cleared the null BULK by 6.75 sd — the signal is unambiguous — but
cleared the observed null MAX by only 1.06 sd. The bar it had to beat was not a noise draw: the
runner-up at 0.800 sits 5.7 sd above the 0.500 bulk and carries genuine partial structure. So the
identification was correct AND thin, and n=10 must not be sized off the n=8 budget.

HONEST SCOPE: one flight, one sealed P. The null spectrum is measured; the n=10 separation must
still be EXTRAPOLATED from three rungs (0.233/0.175/0.056), which is the weak link and is labelled
as such. This sizes a budget; it does not promise an outcome.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import numpy as np
import exp142_robust_decoder_sim as G2
from exp142_p1_c1_decoder_elder_c5003 import candidates

RES = os.path.join(HERE, "..", "results")
TRUE_P = "IZYXZXZZ"          # revealed 2026-07-29 (quantum@b171df7) — used ONLY for post-hoc labelling


def main():
    bits = json.load(open(os.path.join(RES, "exp142_p1_n8_qarm_fetch_elder_c6568.json")))["raw_bitstrings"]
    m, n = len(bits), 8
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    Q = np.array([G2.outcome_to_bits(s, n, mapping) for s in bits])      # (m, 2n)

    print(f"n={n}, {m} Bell samples, walking all {4**n - 1} candidates...", flush=True)
    rates = {}
    for P in candidates(n):
        Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
        sp = (Q[:, :n] @ Pb[n:] + Q[:, n:] @ Pb[:n]) % 2                 # symplectic inner product
        rates[P] = float(np.mean(sp == want))

    order = sorted(rates.items(), key=lambda kv: -kv[1])
    true_rate = rates[TRUE_P]
    true_rank = next(i for i, (P, _) in enumerate(order) if P == TRUE_P) + 1
    nulls = np.array([r for P, r in rates.items() if P != TRUE_P])
    nmu, nsd, nmax = float(nulls.mean()), float(nulls.std(ddof=1)), float(nulls.max())
    runner = order[1]

    print(f"\n  true P {TRUE_P}: rate {true_rate:.4f}   RANK {true_rank} of {len(rates)}")
    print(f"  runner-up {runner[0]}: {runner[1]:.4f}   margin {true_rate - runner[1]:.4f}")
    print(f"  null bulk: mean {nmu:.4f}  sd {nsd:.4f}   observed null MAX {nmax:.4f}")

    z_bulk = (true_rate - nmu) / nsd
    z_max = (true_rate - nmax) / nsd
    binom_se = math.sqrt(true_rate * (1 - true_rate) / m)
    print(f"\n  winner over null BULK : {z_bulk:.2f} null-sd   <- the real signal")
    print(f"  winner over null MAX  : {z_max:.2f} null-sd   <- the margin that actually had to hold")
    print(f"  binomial SE per rate  : {binom_se:.4f}  (margin over runner-up = "
          f"{(true_rate - runner[1]) / binom_se:.2f} binomial SE — the '1.4 SE' figure)")

    # UPPER-TAIL STRUCTURE. A Gaussian-null model is the WRONG frame here and saying so is the
    # point: under it, the observed null max (z=+5.69 over the bulk) would imply ~1.6e8 effective
    # independent comparisons — MORE than the 65535 candidates that exist, which is impossible.
    # The resolution is that the top of the spectrum is not drawn from the null at all: candidates
    # sharing symplectic structure with the true P carry GENUINE partial signal (the runner-up sits
    # at 0.80, nowhere near the 0.50 null bulk). So characterise the tail empirically instead of
    # inferring an effective-N from a distribution that does not apply.
    z_nullmax = (nmax - nmu) / nsd
    print(f"\n  upper tail is NOT null-Gaussian (a Gaussian fit implies more effective comparisons "
          f"than candidates exist -> model rejected). Empirical tail:")
    for thr in (0.60, 0.65, 0.70, 0.75, 0.80):
        c = int((nulls >= thr).sum())
        print(f"    non-true candidates with rate >= {thr:.2f}: {c:6,}  ({100*c/len(nulls):.3f}%)")
    print(f"    -> the runner-up at {runner[1]:.3f} carries REAL partial signal (null bulk "
          f"{nmu:.3f}), so the bar the winner had to clear is a STRUCTURED competitor, "
          f"not a noise draw.")
    tail_counts = {f"{thr:.2f}": int((nulls >= thr).sum()) for thr in (0.60, 0.65, 0.70, 0.75, 0.80)}

    verdict = ("NOT luck — the winner cleared the OBSERVED null max, and the nulls are heavily "
               "correlated so the effective comparison count is far below 4^n-1"
               if z_max > 2 else
               "GENUINELY THIN — the winner did not clear the observed null max by a comfortable "
               "margin; the n=8 call was fragile and n=10 must not be sized like it")
    print(f"\n  VERDICT: {verdict}")

    # ---- n=10 sizing off the MEASURED null width ----
    seps = [0.233, 0.175, 0.056]                                   # observed n=4/6/8 separations
    d1 = [seps[i+1] - seps[i] for i in range(len(seps) - 1)]        # -0.058, -0.119
    sep10_lin = max(seps[-1] + d1[-1], 0.005)                       # linear extrapolation, floored
    sep10_geo = max(seps[-1] * (seps[-1] / seps[-2]), 0.005)        # geometric decay
    print(f"\n  --- n=10 SIZING (separation EXTRAPOLATED — the weak link) ---")
    print(f"  observed separations n=4/6/8: {seps}")
    for label, s10 in (("linear-decay", sep10_lin), ("geometric-decay", sep10_geo)):
        for zreq in (3.0, max(z_max, 2.0)):
            need = (0.85 * 0.15) * (zreq / s10) ** 2                # m = p(1-p)(z/sep)^2
            print(f"   {label:16s} sep~{s10:.4f} @ {zreq:.1f} sd -> need ~{need:,.0f} Bell samples "
                  f"({2*need:,.0f} copies) vs BQ[10]=110 frozen  [{need/110:,.0f}x]")

    out = os.path.join(RES, "exp142_p1_qarm_confusion_n8_elder_c6575.json")
    json.dump({"n": n, "bell_samples": m, "true_P": TRUE_P, "true_rate": true_rate,
               "true_rank": true_rank, "runner_up": runner[0], "runner_rate": runner[1],
               "margin_over_runner": true_rate - runner[1],
               "null_mean": nmu, "null_sd": nsd, "null_max": nmax,
               "z_over_null_bulk": z_bulk, "z_over_null_max": z_max,
               "binomial_se": binom_se,
               "margin_in_binomial_se": (true_rate - runner[1]) / binom_se,
               "null_max_z": z_nullmax, "upper_tail_counts": tail_counts,
               "gaussian_null_model": "REJECTED — implies more effective comparisons than candidates exist; upper tail carries genuine partial signal from structurally-related candidates",
               "nominal_candidates": 4**n - 1, "verdict": verdict,
               "n10_sizing": {"observed_separations_4_6_8": seps,
                              "sep10_linear": sep10_lin, "sep10_geometric": sep10_geo,
                              "caveat": "separation at n=10 is EXTRAPOLATED from 3 rungs; the null "
                                        "width is MEASURED. Sizes a budget, does not promise an outcome."},
               "top20": [{"P": P, "rate": r} for P, r in order[:20]]},
              open(out, "w"), indent=1)
    print(f"\nSAVED {out}")


if __name__ == "__main__":
    main()
