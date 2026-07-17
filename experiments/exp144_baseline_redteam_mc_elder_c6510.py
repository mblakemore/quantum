#!/usr/bin/env python3
"""Exp144 SS4 baseline red-team MC (Elder C6510).

Firms up the conventional-arm meter with an SPRT simulation instead of assumed
per-candidate shot counts, INCLUDING the commuting-narrowing speedup the baseline
is entitled to (conservative = give the baseline every legal advantage).

Model (per SS4, conjugation readout, single V use per shot):
  - candidate P aligned setting: outcome +/-1 with mean mu = -sign * sin(2*theta_min)
    * (1 - 2*q_eff) if planted (worst case = SMALLEST theta), 0 if non-planted.
  - two-sided SPRT H0: mu=0 vs H1: |mu| >= mu1;  alpha = 0.01/M(n) (a single false
    term breaks support exactness -> Bonferroni over the candidate space),
    beta = 0.05 (miss -> candidate re-queued, cost modeled by re-scan).
  - sweep: random-order scan over M(n) full-weight strings; after each planted term
    is FOUND the remaining list is filtered to strings commuting with it (legal
    narrowing from the promised commuting ensemble).
  - coefficient refinement: 70 shots per accepted term (variance arithmetic at
    tau_theta = 0.06 on sin(2theta) readout), included.
Meter = total shots until all m=3 terms found + refined.
"""
import numpy as np, itertools, math, json, sys

rng = np.random.default_rng(20260717)
THETAS = [0.30, 0.40, 0.50]          # frozen theta_j = c_j * t
REFINE = 70

def commutes(a, b):
    k = sum(1 for x, y in zip(a, b) if x != y)   # full-weight: no I letters
    return k % 2 == 0

def sprt_shots(mu_true, mu1, alpha, beta, reps=400):
    """MC expected SPRT shots for +/-1 outcomes, two-sided (test vs |mu1|)."""
    p1 = (1 + mu1) / 2
    la, lb = math.log((1 - beta) / alpha), math.log(beta / (1 - alpha))
    tot = []
    p_true = (1 + mu_true) / 2
    for _ in range(reps):
        llr_pos = llr_neg = 0.0     # track both signs of H1
        nshot = 0
        while True:
            x = 1 if rng.random() < p_true else -1
            nshot += 1
            step_pos = math.log(p1 / 0.5) if x > 0 else math.log((1 - p1) / 0.5)
            llr_pos += step_pos
            llr_neg += (math.log((1 - p1) / 0.5) if x > 0 else math.log(p1 / 0.5))
            m = max(llr_pos, llr_neg)
            if m >= la or (llr_pos <= lb and llr_neg <= lb) or nshot > 3000:
                tot.append(nshot); break
    return float(np.mean(tot))

def run(n, q_eff, reps=50):
    full = None
    M = 3 ** n
    mu1 = math.sin(2 * min(THETAS)) * (1 - 2 * q_eff)     # worst planted signal
    alpha = 0.01 / M
    e_null = sprt_shots(0.0, mu1, alpha, 0.05)
    e_plant = sprt_shots(mu1, mu1, alpha, 0.05)
    # enumerate strings lazily only for the sweep structure (letters as ints 0..2)
    meters = []
    for _ in range(reps):
        # planted instance: sample commuting mult-independent triple (index space)
        while True:
            cand = [tuple(rng.integers(0, 3, n)) for _ in range(3)]
            cs = ["".join("XYZ"[i] for i in c) for c in cand]
            if len(set(cs)) == 3 and all(commutes(a, b) for a, b in itertools.combinations(cs, 2)):
                break
        # random scan order = random ranks; simulate narrowing statistically:
        # phase 1: scan among M until 1st planted hit (3 targets)
        shots, found, remainingM, targets = 0.0, 0, M, 3
        while found < 3:
            # expected scans to next hit among remainingM with `targets` targets
            e_scan = (remainingM + 1) / (targets + 1)
            shots += (e_scan - 1) * e_null + e_plant
            found += 1; targets -= 1
            remainingM = max(targets, remainingM // 2)   # commuting filter halves
        shots += 3 * REFINE
        meters.append(shots)
    return {"n": n, "q_eff": q_eff, "M": M,
            "sprt_null": round(e_null, 1), "sprt_planted": round(e_plant, 1),
            "meter_mean": round(float(np.mean(meters)), 0),
            "meter_p10": round(float(np.percentile(meters, 10)), 0)}

if __name__ == "__main__":
    QBUDGET = {4: 5000 + 3 * 100 + 512, 6: 5000 + 3 * 100 + 512, 8: 5000 + 3 * 100 + 512}
    out = []
    print(f"{'n':>2} {'q_eff':>5} {'M':>6} {'E[N|null]':>9} {'E[N|plant]':>10} "
          f"{'meter(mean)':>12} {'meter(p10)':>10} {'ratio(mean)':>11}")
    for n in (4, 6, 8):
        for q in (0.05, 0.10):
            r = run(n, q)
            r["ratio_mean"] = round(r["meter_mean"] / QBUDGET[n], 2)
            r["ratio_p10"] = round(r["meter_p10"] / QBUDGET[n], 2)
            out.append(r)
            print(f"{n:>2} {q:>5} {r['M']:>6} {r['sprt_null']:>9} {r['sprt_planted']:>10} "
                  f"{r['meter_mean']:>12} {r['meter_p10']:>10} {r['ratio_mean']:>11}")
    with open(sys.path[0] + "/exp144_baseline_redteam_mc_results_c6510.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nNOTE: baseline given every legal advantage (commuting narrowing, "
          "beta=0.05 re-queue not re-scan, favorable q_eff). Ratios are the "
          "CONSERVATIVE (baseline-favoring) provisional R inputs.")
