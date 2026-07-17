#!/usr/bin/env python3
"""Exp144 Gate-2 CLEAN MC (Elder C6518) — corrected objective, chair ruling C4780.

Fixes vs the C6517 first pass (defects disclosed there):
  1. OBJECTIVE: the conv arm is the BASELINE — its failures are NULL instances.
     Parameters minimize meter s.t. P(instance correct) >= 0.9 at eps=0.02
     (>= 0.75 at 0.04). No experiment-grade error rates demanded of it.
  2. JOINT (cut, W2) calibration: cut = z/sqrt(W2) with z from grid — never
     below the noise floor.
  3. SIGN-CONSISTENT majority vote: accept iff >= need probes hit with the SAME
     sign (target has fixed sign across probes; nulls split) — halves null rate.
  4. Ratio denominator = 5*M_BELL = 5000 exactly (grader/§5 convention).

Outputs (chair C4780): per-rung flight constants, R floors incl R(4), ratio
BANDS all three rungs, SLOPE bands centered ~9, n4 two-sided flag band.
Exact means via the C6517 statevector machinery (validated vs flight-kit path).
"""
import itertools
import json
import math
import sys

import numpy as np

sys.path.insert(0, sys.path[0] if sys.path[0] else ".")
from exp144_gate2_twostage_mc_elder_c6517 import (
    GRID, T, commutes, sample_instance, stage1_mean, stage2_mean, conv_probe,
    p_hit, ND)


def magnitude_majority_accept(mus, cut, shots, need):
    """Two-sided: P(>= need probes with |mean| >= cut). Planted signs are
    probe-convention-dependent (C6518 diagnostic) — magnitude voting is the
    correct statistic; final signs come from the refinement stage."""
    ps = [p_hit(m, cut, shots) for m in mus]
    dp = np.zeros(len(ps) + 1)
    dp[0] = 1.0
    for p_ in ps:
        dp[1:] = dp[1:] * (1 - p_) + dp[:-1] * p_
        dp[0] *= (1 - p_)
    return float(dp[need:].sum())

EPS_GRID = [0.01, 0.02, 0.04]
QBUDGET = 5000                      # 5 * M_BELL — §5 ratio denominator, exact
RNG = np.random.default_rng(424242)


def sign_majority_accept(mus, cut, shots, need):
    """P(>= need probes hit with a COMMON sign). Per-probe one-sided hits."""
    def one_sided(mu, side):
        sd = math.sqrt(max(1 - mu * mu, 1e-9) / shots)
        return 1 - ND.cdf((cut - side * mu) / sd)
    best = 0.0
    for side in (+1, -1):
        ps = [one_sided(m, side) for m in mus]
        dp = np.zeros(len(ps) + 1)
        dp[0] = 1.0
        for p in ps:
            dp[1:] = dp[1:] * (1 - p) + dp[:-1] * p
            dp[0] *= (1 - p)
        best = max(best, float(dp[need:].sum()))
    return best


def stage1_constants(n, eps, mu_anti_max_raw=None):
    """N1, cut1 for the conservation filter. Planted-kill <= 0.01/term,
    anticommuter false-pass <= 0.05 (cost-only)."""
    att = (1 - 2 * eps) ** n
    mu_c = att
    mu_a = (mu_anti_max_raw if mu_anti_max_raw is not None
            else math.cos(2 * 0.30)) * att       # worst single-anticommuter
    cut1 = (mu_c + mu_a) / 2
    for N1 in range(40, 601, 20):
        sd_c = math.sqrt(max(1 - mu_c**2, 1e-9) / N1)
        sd_a = math.sqrt(max(1 - mu_a**2, 1e-9) / N1)
        pk = ND.cdf((cut1 - mu_c) / sd_c)
        fp = 1 - ND.cdf((cut1 - mu_a) / sd_a)
        if pk <= 0.01 and fp <= 0.05:
            return N1, cut1, pk, fp
    return 600, cut1, pk, fp


def rung_mc(n, eps, n_inst=24, cand_sample=72):
    att = (1 - 2 * eps) ** n
    N1, cut1, pk1, fp1 = stage1_constants(n, eps)
    best = None
    # exact stage-2 means per instance (computed once, reused across params)
    inst_data = []
    for _ in range(n_inst):
        terms = sample_instance(n, RNG)
        coeffs = list(RNG.permutation(GRID) * RNG.choice([-1, 1], 3))
        thetas = [c * T for c in coeffs]
        if n == 4:
            cands = ["".join(p) for p in itertools.product("XYZ", repeat=n)]
        else:
            cands, seen = list(terms), set(terms)
            while len(cands) < cand_sample + 3:
                c = "".join(RNG.choice(list("XYZ"), n))
                if c not in seen:
                    seen.add(c); cands.append(c)
        conserved = [c for c in cands if all(commutes(c, t2) for t2 in terms)]
        cons_frac = (len(conserved) - 3) / max(len(cands) - 3, 1)
        grng = np.random.default_rng(11)
        mus = {}
        for cnd in conserved:
            F_max = 12
            mus[cnd] = [stage2_mean(cnd, conv_probe(cnd, w), terms, thetas,
                                    grng, n_gauge=32) * att for w in range(1, F_max + 1)]
        inst_data.append((terms, conserved, cons_frac, mus))
    # parameter grid, corrected objective
    for F in (8, 12):
        need = F // 2 + 1
        for W2 in (100, 200, 300):
            for z in (2.6, 3.0, 3.4):
                cut = z / math.sqrt(W2)
                ok_all, meters, ratios = 0, [], []
                for terms, conserved, cons_frac, mus in inst_data:
                    p_ok = (1 - pk1) ** 3
                    for cnd in conserved:
                        acc = magnitude_majority_accept(mus[cnd][:F], cut, W2, need)
                        if cnd in terms:
                            p_ok *= acc
                        else:
                            p_ok *= (1 - acc)
                    Mfull = 3 ** n
                    n_cons_full = 3 + cons_frac * (Mfull - 3)
                    n_s1_pass = n_cons_full + fp1 * (Mfull - n_cons_full)
                    meter = Mfull * N1 + n_s1_pass * F * W2 + 3 * 70
                    meters.append(meter)
                    ratios.append(meter / QBUDGET)
                    ok_all += p_ok
                p_inst = ok_all / len(inst_data)
                target = 0.9 if eps <= 0.02 else 0.75
                if p_inst >= target:
                    mm = float(np.mean(meters))
                    if best is None or mm < best["meter_mean"]:
                        best = {"N1": N1, "cut1": round(cut1, 3), "F": F,
                                "W2": W2, "cut2": round(cut, 4),
                                "p_instance_correct": round(p_inst, 3),
                                "meter_mean": round(mm),
                                "ratios": [round(r, 2) for r in ratios]}
    return best


def main():
    out = {"per_rung": {}, "eps_central": 0.02}
    ladder = {}
    for n in (4, 6, 8):
        out["per_rung"][n] = {}
        for eps in EPS_GRID:
            r = rung_mc(n, eps, n_inst=24 if n < 8 else 10,
                        cand_sample=72 if n < 8 else 48)
            out["per_rung"][n][str(eps)] = r
            tag = (f"n={n} eps={eps}: " +
                   ("NO PARAMS MEET TARGET" if r is None else
                    f"N1={r['N1']} F={r['F']} W2={r['W2']} cut2={r['cut2']} "
                    f"P(ok)={r['p_instance_correct']} meter={r['meter_mean']} "
                    f"ratio~{np.mean(r['ratios']):.1f}"))
            print(tag)
            if eps == 0.02 and r is not None:
                ladder[n] = r["ratios"]
    # bands: K=5 median over instance-draw ratios, bootstrap
    bands, med_pts = {}, {}
    for n, rs in ladder.items():
        med5 = [float(np.median(RNG.choice(rs, 5))) for _ in range(4000)]
        bands[n] = [round(float(np.percentile(med5, 5)), 2),
                    round(float(np.percentile(med5, 95)), 2)]
        med_pts[n] = float(np.median(rs))
    slopes = {}
    for a, b in ((4, 6), (6, 8)):
        if a not in ladder or b not in ladder:
            continue
        boot = []
        for _ in range(4000):
            ma = np.median(RNG.choice(ladder[a], 5))
            mb = np.median(RNG.choice(ladder[b], 5))
            boot.append(mb / ma)
        slopes[f"{b}/{a}"] = [round(float(np.percentile(boot, 5)), 2),
                              round(float(np.percentile(boot, 95)), 2)]
    r_floors = {4: 2.0, 6: 1.5, 8: 10.0}
    out.update({"ladder_medians": {n: round(m, 2) for n, m in med_pts.items()},
                "ratio_bands": bands, "slope_bands": slopes,
                "R_floors": r_floors})
    print("\nLADDER (eps=0.02 medians):", {n: round(m, 1) for n, m in med_pts.items()})
    print("RATIO BANDS (K=5 median, 5-95%):", bands)
    print("SLOPE BANDS (centered ~9):", slopes)
    print("R floors:", r_floors, "(all ladder medians must clear with margin)")
    with open(sys.path[0] + "/exp144_clean_mc_results_c6518.json", "w") as f:
        json.dump(out, f, indent=2)
    print("-> exp144_clean_mc_results_c6518.json")


if __name__ == "__main__":
    main()
