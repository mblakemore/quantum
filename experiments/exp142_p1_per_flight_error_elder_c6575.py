#!/usr/bin/env python3
"""PER-FLIGHT ERROR TERM, derived mechanically from repeated same-n flights. Elder C6575.

*** WRITTEN BEFORE THE THIRD PAIR LANDS, DELIBERATELY *** — same reason as the day-effect estimator:
an analysis written after the data can be shaped by it.

WHY IT EXISTS. Chair grade on the pair experiment (Whisper): rung-15 sizing must carry a per-flight
error term REGARDLESS of the third pair's verdict, because "the curve is never again treated as tight
when we hold direct evidence it is not." The pairs showed the same-day n-effect CENTRE reproduces
(-0.0820 vs -0.0860 historical) while the VARIANCE ACROSS CALIBRATIONS is large — a term that was never
in the model. This derives it.

THE DECOMPOSITION. Repeated measurements of the same rung on different calibrations vary for two
reasons, and only one of them is in the current error bars:
    observed variance  =  binomial (shot noise, already modelled)  +  per-flight (NOT modelled)
so
    sigma_per_flight = sqrt( max(0, var_observed - var_binomial_expected) )

*** THREE HONESTY CONSTRAINTS, because k IS TINY AND A VARIANCE FROM k=3 IS A TERRIBLE ESTIMATE. ***

(1) **A VARIANCE ESTIMATE FROM k FLIGHTS CARRIES ENORMOUS UNCERTAINTY AT SMALL k.** The sampling
    distribution of s^2 is chi-square with k-1 dof: at k=3 the 90% CI on sigma spans roughly 0.52x to
    3.7x the point estimate. So this tool reports sigma_per_flight as a **BAND, never a point**, and
    the band is wide enough at k=3 that quoting the centre alone would be its own flattering-number
    error. It refuses to emit a term at all for k < 2.

(2) **HETEROGENEOUS m MAKES THE COMPARISON UNEQUAL.** The historical n=10 arm has m=528 against the
    pairs' m=2040, so its binomial SE is ~2x larger and it dominates the expected variance. The tool
    therefore computes the binomial expectation as the MEAN OF THE PER-MEASUREMENT VARIANCES (not from
    a single pooled m) and flags any n whose m values differ by more than 2x, because there the excess
    is a difference of two poorly-matched quantities.

(3) **NEGATIVE EXCESS IS REPORTED, NOT HIDDEN.** If observed variance falls below binomial expectation
    the raw (negative) value is printed alongside the clamped zero. A clamp that silently swallows a
    negative is how "no excess detected" becomes indistinguishable from "the estimator is noisy" —
    and at k=3 a negative excess is entirely expected some of the time even when a real term exists.

DIRECTION OF THE CONSEQUENCE, stated so nobody has to work it out: a per-flight term WIDENS the
uncertainty on each rung, which pushes the sizing low-end DOWN, which demands MORE samples. So this
uncertainty bites in the SAFE direction — unlike most of what we found today, adding it cannot make a
rung look cheaper than it is.

  --report                       derive the term from the measurements below
  --json                         machine-readable
  --add "n,rate,m,label"         add a measurement (repeatable) — e.g. a third pair on landing
"""
import argparse, json, math, sys

ALPHA_IDEAL = (1 + 0.95 ** 2) / 2
K = ALPHA_IDEAL - 0.5

# Every same-n measurement we hold. Historical + the two pairs.
MEAS = [
    (10, 0.7898, 528,  "historical (job d9l38b8ii2cc73egv1i0)"),
    (10, 0.7951, 2040, "pair 1 (d9lndjrhdfks73cl8020)"),
    (10, 0.8064, 2040, "pair 2 (d9lndkjhdfks73cl803g)"),
    (14, 0.7510, 2040, "historical (job d9li42jhdfks73cl16j0)"),
    (14, 0.7755, 2040, "pair 1 (d9lndjrhdfks73cl8020)"),
    (14, 0.7520, 2040, "pair 2 (d9lndkjhdfks73cl803g)"),
]

# chi-square quantiles for the sigma band, dof = k-1. {dof: (chi2_0.05, chi2_0.95)}
CHI2 = {1: (0.00393, 3.841), 2: (0.1026, 5.991), 3: (0.3518, 7.815), 4: (0.7107, 9.488),
        5: (1.1455, 11.070), 6: (1.6354, 12.592)}


def ret(rate):
    return (rate - 0.5) / K


def se_ret(rate, m):
    return math.sqrt(rate * (1 - rate) / m) / K


def derive(meas):
    out = {}
    for n in sorted({r[0] for r in meas}):
        rows = [r for r in meas if r[0] == n]
        k = len(rows)
        rets = [ret(r[1]) for r in rows]
        ses = [se_ret(r[1], r[2]) for r in rows]
        ms = [r[2] for r in rows]
        entry = {"n": n, "k": k, "retentions": [round(x, 4) for x in rets],
                 "m_values": ms, "sources": [r[3] for r in rows]}
        if k < 2:
            entry["status"] = "INSUFFICIENT — need >=2 flights at this n"
            out[n] = entry; continue
        mean = sum(rets) / k
        var_obs = sum((x - mean) ** 2 for x in rets) / (k - 1)
        var_bin = sum(s * s for s in ses) / k          # mean per-measurement variance, NOT pooled-m
        excess_raw = var_obs - var_bin
        sigma_pf = math.sqrt(max(0.0, excess_raw))
        dof = k - 1
        lo_q, hi_q = CHI2.get(dof, (0.3518, 7.815))
        # chi-square band on the OBSERVED sd, then re-subtract the binomial floor
        band = None
        if dof in CHI2:
            v_lo = var_obs * dof / hi_q
            v_hi = var_obs * dof / lo_q
            band = (math.sqrt(max(0.0, v_lo - var_bin)), math.sqrt(max(0.0, v_hi - var_bin)))
        entry.update({
            "mean_retention": round(mean, 4),
            "sd_observed": round(math.sqrt(var_obs), 4),
            "sd_binomial_expected": round(math.sqrt(var_bin), 4),
            "excess_variance_RAW": round(excess_raw, 8),
            "sigma_per_flight_point": round(sigma_pf, 4),
            "sigma_per_flight_90pct_band": [round(band[0], 4), round(band[1], 4)] if band else None,
            "m_heterogeneous": max(ms) / min(ms) > 2.0,
            "status": ("NEGATIVE EXCESS — observed below binomial expectation; consistent with no "
                       "per-flight term AND with a real term masked by tiny k"
                       if excess_raw < 0 else "excess present"),
        })
        out[n] = entry
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--add", action="append", default=[])
    a = ap.parse_args()

    meas = list(MEAS)
    for s in a.add:
        p = [x.strip() for x in s.split(",")]
        if len(p) < 3:
            sys.exit(f"--add wants 'n,rate,m[,label]' — got {s!r}")
        meas.append((int(p[0]), float(p[1]), int(p[2]), p[3] if len(p) > 3 else "added"))

    res = derive(meas)
    if a.json:
        print(json.dumps(res, indent=1)); return 0

    print("PER-FLIGHT ERROR TERM — derived from repeated same-n flights\n")
    for n, e in res.items():
        print(f"  n={n}  k={e['k']} flights   retentions {e['retentions']}   m {e['m_values']}")
        if e["k"] < 2:
            print(f"     {e['status']}\n"); continue
        print(f"     sd observed {e['sd_observed']}   sd binomial-expected {e['sd_binomial_expected']}"
              f"   excess variance {e['excess_variance_RAW']:+.8f}")
        b = e["sigma_per_flight_90pct_band"]
        print(f"     **sigma_per_flight = {e['sigma_per_flight_point']}**   90% band [{b[0]}, {b[1]}]"
              if b else f"     sigma_per_flight = {e['sigma_per_flight_point']}")
        if e["m_heterogeneous"]:
            print("     ⚠️  m values differ by >2x — the excess here is a difference of poorly-matched "
                  "quantities; treat as the weaker estimate")
        if e["excess_variance_RAW"] < 0:
            print(f"     ⚠️  {e['status']}")
        print()
    ks = sorted({e["k"] for e in res.values()})
    print("  READING THIS HONESTLY:")
    print(f"   • k is TINY (k={','.join(str(x) for x in ks)}). A variance estimate has a chi-square")
    print("     sampling distribution on k-1 dof — at k=3 the 90% band spans ~0.5x-3.7x the point —")
    print("     so the BAND is the result and the point estimate alone would be a flattering number.")
    print("   • A negative excess is reported, not clamped away — at small k it is expected some of")
    print("     the time even when a real term exists, so it is NOT evidence of absence.")
    print("   • DIRECTION: a per-flight term widens each rung's uncertainty, pushing the sizing")
    print("     low-end DOWN and demanding MORE samples. This uncertainty bites the SAFE way.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
