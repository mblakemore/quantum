#!/usr/bin/env python3
"""⚠️ MIS-SPECIFIED (board#399, C6655): this computes on RAW 2-bit outcomes, an information set that includes the
correlator SIGN and marginals which §D forecloses; the outputs are NOT §A numerators (they measure the quantum witness).
Kept as the record of what was declared and computed; superseded by the magnitude-only version.

§A numerators (2) permutation-calibrated empirical TV and (3) executed classical arm cross-validated success,
computed from the BANKED re-fly pre-run records (job d9tb3tgpdb6s73e7082g) exactly as pre-declared on board#399
(Elder C6655). Pure function of the bank; seeded; writes results/h13_cell2_refly_numerators_2_3_elder_c6655.json.
d-units: d2 = W*TV_UB ; d3 = 2W*(s_UB - 1/2) ; W = band width in p (0.40). ceiling = 1/2 + d/(2W)."""
import json, math, random, collections, sys
J = "d9tb3tgpdb6s73e7082g"; W = 0.40; B = 2000; SEED = 6655; FOLDS = 5
man = json.load(open(f"results/h13_cell2_refly_prerun_manifest_{J}.json")); res = json.load(open(f"results/h14_lock5_rescue_h13_cell2_{J}.json"))
labels, pubs = man["labels"], res["pubs"]; assert len(labels) == len(pubs) == 480
CATS = ["00", "01", "10", "11"]
def collect(cond_twirl):
    cells = collections.defaultdict(lambda: {"CE": [], "CC": []})
    for lab, pub in zip(labels, pubs):
        key = (lab["unit"], lab["basis"]) + ((lab["twirl"],) if cond_twirl else ())
        cells[key][lab["arm"]].extend(pub["data"]["c"])
    return cells
def tv(a, b):
    ca, cb = collections.Counter(a), collections.Counter(b); na, nb = len(a), len(b)
    return 0.5 * sum(abs(ca[c] / na - cb[c] / nb) for c in CATS)
def numerator2(cells, rng):
    obs = [tv(v["CE"], v["CC"]) for v in cells.values()]; TV_obs = sum(obs) / len(obs)
    null = []
    for _ in range(B):
        acc = 0.0
        for v in cells.values():
            pool = v["CE"] + v["CC"]; rng.shuffle(pool); n = len(v["CE"])
            acc += tv(pool[:n], pool[n:])
        null.append(acc / len(cells))
    mu = sum(null) / B; sd = math.sqrt(sum((x - mu) ** 2 for x in null) / (B - 1))
    cal = max(0.0, TV_obs - mu); ub = cal + 2 * sd
    return {"TV_obs": TV_obs, "null_mean": mu, "null_sd": sd, "TV_calibrated": cal, "TV_UB": ub, "d2": W * ub,
            "z_obs_vs_null": (TV_obs - mu) / sd if sd > 0 else None, "cells": len(cells), "B": B}
def numerator3(cells, rng):
    correct = 0; total = 0
    for v in cells.values():
        shots = [(s, "CE") for s in v["CE"]] + [(s, "CC") for s in v["CC"]]; rng.shuffle(shots)
        folds = [shots[i::FOLDS] for i in range(FOLDS)]
        for f in range(FOLDS):
            test = folds[f]; train = [s for g in range(FOLDS) if g != f for s in folds[g]]
            cnt = collections.defaultdict(lambda: {"CE": 0, "CC": 0})
            for s, arm in train: cnt[s][arm] += 1
            rule = {s: ("CE" if c["CE"] >= c["CC"] else "CC") for s, c in cnt.items()}
            for s, arm in test:
                total += 1; correct += (rule.get(s, "CE") == arm)
    s_cv = correct / total; se = math.sqrt(s_cv * (1 - s_cv) / total); s_ub = s_cv + 2 * se
    return {"s_cv": s_cv, "N_test": total, "se": se, "s_UB": s_ub, "d3": 2 * W * (s_ub - 0.5), "cells": len(cells), "folds": FOLDS}
out = {"job": J, "W": W, "seed": SEED, "declared_on": "board#399 (Elder C6655, before computing)", "variants": {}}
for name, cond in (("pooled_over_twirl (declared per-cell)", False), ("twirl_conditioned (declared addendum, stronger attack)", True)):
    rng = random.Random(SEED); cells = collect(cond)
    out["variants"][name] = {"n2": numerator2(cells, rng), "n3": numerator3(cells, rng)}
d1 = 0.03541
d2 = max(v["n2"]["d2"] for v in out["variants"].values()); d3 = max(v["n3"]["d3"] for v in out["variants"].values())
d = max(d1, d2, d3); which = {d1: "1 model d/W (exhibit c6651)", d2: "2 permutation-calibrated TV", d3: "3 executed classical arm"}[d]
c = 0.5 + d / (2 * W); z = (75 - 75 * c) / math.sqrt(75 * c * (1 - c))
out.update({"d1_from_exhibit_c6651": d1, "d2_max_over_variants": d2, "d3_max_over_variants": d3, "d_max": d, "max_is": which,
            "ceiling_W_p": c, "sigma_75of75": z, "bar_5sigma_fails_at_d": 0.200})
json.dump(out, open("results/h13_cell2_refly_numerators_2_3_elder_c6655.json", "w"), indent=1)
for name, v in out["variants"].items():
    print(f"{name}: TV_obs {v['n2']['TV_obs']:.5f} null {v['n2']['null_mean']:.5f}±{v['n2']['null_sd']:.5f} -> TV_UB {v['n2']['TV_UB']:.5f} d2 {v['n2']['d2']:.5f} (z {v['n2']['z_obs_vs_null']:+.2f}) | s_cv {v['n3']['s_cv']:.5f}±{v['n3']['se']:.5f} s_UB {v['n3']['s_UB']:.5f} d3 {v['n3']['d3']:.5f}")
print(f"d = max({d1:.5f}, {d2:.5f}, {d3:.5f}) = {d:.5f} <- {which}; ceiling {c:.5f}; sigma 75/75 = {z:.3f}")
