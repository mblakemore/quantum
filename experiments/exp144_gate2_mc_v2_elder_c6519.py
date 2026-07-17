#!/usr/bin/env python3
"""Exp144 Gate-2 MC v2 (Elder C6519) — FINAL pre-freeze constants.

Chair rulings baked in (C4780 + C4781): 3 scored rungs; ratio bands + slope claim
(band from MC, 9 = noiseless asymptote); n4 two-sided flag; SPRT stage-1;
per-instance conv CEILING = 1M shots with unresolved = NULL and ratio = LOWER
BOUND >= ceiling/budget; magnitude majority (sign-persistence sub-claim killed
C6518); extended n4 grid; baseline objective (failures = NULL instances).

n=8 honesty: even the mitigated baseline (~2.3M/inst) exceeds the ceiling ->
n8 is a PREDICTED-CEILING rung: pre-registered claim = conv CANNOT finish within
1M (falsifiable: if it does, the cost model was wrong; report as-is). Ratio
>= 200 vs R(8)=10 = 20x lower-bound margin.
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

EPS_CENTRAL = 0.02
EPS_GRID = [0.01, 0.02, 0.04]
QBUDGET = 5000
CEILING = 1_000_000
SPRT_ALPHA = 0.05      # anticommuter falsely enters stage 2 (cost only)
SPRT_BETA = 0.01       # conserved (incl planted) falsely rejected (kill risk)
RNG = np.random.default_rng(77)


def sprt_stage1_EN(mu_true, att, cap=800):
    """E[shots] for SPRT: H_cons mean=att vs H_anti mean=att*cos(0.6)."""
    p1 = (1 + att) / 2                      # conserved
    p0 = (1 + att * math.cos(0.6)) / 2      # worst anticommuter
    A = math.log((1 - SPRT_BETA) / SPRT_ALPHA)
    B = math.log(SPRT_BETA / (1 - SPRT_ALPHA))
    pt = (1 + mu_true) / 2
    step = pt * math.log(p1 / p0) + (1 - pt) * math.log((1 - p1) / (1 - p0))
    if abs(step) < 1e-6:
        return cap
    bound = A if step > 0 else B
    return min(cap, max(8.0, bound / step))


def stage2_costs(mus, cut, W2, F):
    """Sequential probes, early stop when majority decided.
    Returns (accept_prob, E[probes])."""
    need = F // 2 + 1
    ps = [p_hit(m, cut, W2) for m in mus[:F]]
    # exact DP over probe sequence with early stopping
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def go(i, hits):
        if hits >= need:
            return (1.0, 0.0)
        if hits + (F - i) < need:
            return (0.0, 0.0)
        p = ps[i]
        a1, e1 = go(i + 1, hits + 1)
        a0, e0 = go(i + 1, hits)
        return (p * a1 + (1 - p) * a0, 1 + p * e1 + (1 - p) * e0)
    acc, eprobes = go(0, 0)
    return acc, eprobes


def rung_mc(n, eps, n_inst, cand_sample):
    att = (1 - 2 * eps) ** n
    results = []
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
        # stage-1 SPRT expected cost over the candidate space
        e_n1 = []
        for c in cands:
            mu = stage1_mean(c, terms, thetas) * att if c not in conserved else att
            e_n1.append(sprt_stage1_EN(mu, att))
        Mfull = 3 ** n
        s1_cost = float(np.mean(e_n1)) * Mfull
        n_cons_full = 3 + cons_frac * (Mfull - 3)
        n_s1_pass = n_cons_full + SPRT_ALPHA * (Mfull - n_cons_full)
        # stage-2 exact means; parameter grid (extended for n=4 per C4781 #4)
        grng = np.random.default_rng(13)
        mus = {c: [stage2_mean(c, conv_probe(c, w), terms, thetas, grng,
                               n_gauge=32) * att for w in range(1, 13)]
               for c in conserved}
        best = None
        for F in (8, 12):
            for W2 in (200, 300, 500):
                for z in (2.8, 3.2):
                    cut = z / math.sqrt(W2)
                    p_ok = (1 - SPRT_BETA) ** 3
                    e_probes_null, e_probes_planted = [], []
                    for c in conserved:
                        acc, ep = stage2_costs(mus[c], cut, W2, F)
                        if c in terms:
                            p_ok *= acc
                            e_probes_planted.append(ep)
                        else:
                            p_ok *= (1 - acc)
                            e_probes_null.append(ep)
                    en = float(np.mean(e_probes_null)) if e_probes_null else 0
                    epl = float(np.mean(e_probes_planted))
                    s2_cost = ((n_s1_pass - 3) * en + 3 * epl) * W2
                    meter = s1_cost + s2_cost + 3 * 70
                    if best is None or (p_ok, -meter) > (best[0], -best[1]):
                        best = (p_ok, meter, F, W2, round(cut, 4))
        p_ok, meter, F, W2, cut = best
        results.append({"p_ok": p_ok, "meter": meter, "F": F, "W2": W2,
                        "cut": cut, "ceiled": meter > CEILING})
    return results


def main():
    out = {"per_rung": {}, "ceiling": CEILING,
           "sprt": {"alpha": SPRT_ALPHA, "beta": SPRT_BETA}}
    ladder = {}
    for n in (4, 6, 8):
        rs = rung_mc(n, EPS_CENTRAL, n_inst=20 if n < 8 else 10,
                     cand_sample=72 if n < 8 else 48)
        p_ok = float(np.mean([r["p_ok"] for r in rs]))
        meters = [min(r["meter"], CEILING) for r in rs]
        ceiled = float(np.mean([r["ceiled"] for r in rs]))
        ratios = [m / QBUDGET for m in meters]
        ladder[n] = (ratios, ceiled)
        # modal parameters
        Fm = max(set(r["F"] for r in rs), key=[r["F"] for r in rs].count)
        Wm = max(set(r["W2"] for r in rs), key=[r["W2"] for r in rs].count)
        cm = max(set(r["cut"] for r in rs), key=[r["cut"] for r in rs].count)
        out["per_rung"][n] = {
            "P_instance_correct_mean": round(p_ok, 3),
            "meter_mean_unceiled": round(float(np.mean([r["meter"] for r in rs]))),
            "frac_ceiling": round(ceiled, 2), "F": Fm, "W2": Wm, "cut2": cm}
        print(f"n={n}: P(ok)={p_ok:.3f} meter_unceiled="
              f"{np.mean([r['meter'] for r in rs]):.0f} ceiling-hit={ceiled:.0%} "
              f"F={Fm} W2={Wm} cut={cm}")
    # bands (K=5 medians)
    bands, meds = {}, {}
    for n, (ratios, ceiled) in ladder.items():
        med5 = [float(np.median(RNG.choice(ratios, 5))) for _ in range(4000)]
        bands[n] = [round(float(np.percentile(med5, 5)), 1),
                    round(float(np.percentile(med5, 95)), 1)]
        meds[n] = round(float(np.median(ratios)), 1)
    s64 = [float(np.median(RNG.choice(ladder[6][0], 5)) /
                 np.median(RNG.choice(ladder[4][0], 5))) for _ in range(4000)]
    out.update({
        "ratio_bands": bands, "ladder_medians": meds,
        "slope_6over4_band": [round(float(np.percentile(s64, 5)), 1),
                              round(float(np.percentile(s64, 95)), 1)],
        "n8_semantics": ("PREDICTED-CEILING rung: conv expected NOT to resolve "
                         "within 1M -> ratio reported as LOWER BOUND >= "
                         f"{CEILING // QBUDGET}; falsifiable (resolution within "
                         "ceiling = cost model wrong, report as-is)"),
        "R_floors": {4: 2.0, 6: 1.5, 8: 10.0},
        "n4_flag_band_two_sided": bands.get(4)})
    print("\nBANDS:", bands, "| medians:", meds)
    print("SLOPE 6/4 band:", out["slope_6over4_band"], "(asymptote 9)")
    print("n8:", out["n8_semantics"])
    with open(sys.path[0] + "/exp144_mc_v2_results_c6519.json", "w") as f:
        json.dump(out, f, indent=2)
    print("-> exp144_mc_v2_results_c6519.json")


if __name__ == "__main__":
    main()
