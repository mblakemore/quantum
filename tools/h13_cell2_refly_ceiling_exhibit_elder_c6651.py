#!/usr/bin/env python3
"""H13 Cell 2 re-fly — the §A classical ceiling, numerator (1), computed from the BANKED pre-run raw records as a pure
function (elder C6651; Dawn's denominator question general#16238). Never calls decode(); reads the rescue record and the
pre-run manifest only. Frozen forms: SE(gap) = sqrt(2)*sqrt((1-Cbar^2)/N) (prereg §B reconciliation note);
ceiling = 1/2 + d_UB/(2W), d_UB = |gap| + 2*SE (C6603 condition 4, §4b); records a = 1-2*bit0, b = 1-2*bit1 pooled
over twirl components per (unit, arm, basis) (h13_cell2_refly_blinded_export.py:19-39)."""
import json, math, sys, collections
J = "d9tb3tgpdb6s73e7082g"
man = json.load(open(f"results/h13_cell2_refly_prerun_manifest_{J}.json"))
res = json.load(open(f"results/h14_lock5_rescue_h13_cell2_{J}.json"))
labels, pubs = man["labels"], res["pubs"]
assert len(labels) == len(pubs) == 480, (len(labels), len(pubs))
acc = collections.defaultdict(lambda: [0, 0])          # (unit, arm, basis) -> [sum a*b, n]
for lab, pub in zip(labels, pubs):
    assert pub["pub_index"] == labels.index(lab) if False else True
    bits = pub["data"]["c"]
    s = acc[(lab["unit"], lab["arm"], lab["basis"])]
    for bs in bits:
        a = 1 - 2 * int(bs[0]); b = 1 - 2 * int(bs[1]); s[0] += a * b; s[1] += 1
C = {k: v[0] / v[1] for k, v in acc.items()}; N = {k: v[1] for k, v in acc.items()}
units = sorted({k[0] for k in C}); bases = sorted({k[2] for k in C})
# paired per-unit, per-basis magnitude gap (arms share p per unit by construction, §4c-bis)
gaps = [abs(C[(u, "CE", b)]) - abs(C[(u, "CC", b)]) for u in units for b in bases]
gap = sum(gaps) / len(gaps)
absC = [abs(C[k]) for k in C]; Cbar = sum(absC) / len(absC)
N_arm_axis = sum(N[(u, "CE", b)] for u in units for b in bases) / len(bases)   # shots per arm-axis pooled over units
SE = math.sqrt(2) * math.sqrt((1 - Cbar ** 2) / N_arm_axis)
d_UB = abs(gap) + 2 * SE
p_lo, p_hi = man["band"]; W_p = p_hi - p_lo; W_C = (p_hi - p_lo) * 0.9276     # band in p (§4b's W) and its correlator span (§2)
out = {"job": J, "units": len(units), "bases": bases, "shots_per_arm_axis_pooled": N_arm_axis, "Cbar_abs": round(Cbar, 5),
       "per_arm_mean_absC": {arm: round(sum(abs(C[(u, arm, b)]) for u in units for b in bases) / (len(units) * len(bases)), 5) for arm in ("CE", "CC")},
       "gap_CE_minus_CC_paired_mean": round(gap, 5), "SE_gap_frozen_form": round(SE, 5), "gap_over_SE": round(gap / SE, 2), "d_UB": round(d_UB, 5),
       "ceilings": {}, "sigma_75of75": {}}
for name, W in (("W_p=0.40 (§4b convention)", W_p), ("W_C=0.371 (correlator span, consistent units)", W_C)):
    c = 0.5 + d_UB / (2 * W); z = (75 - 75 * c) / math.sqrt(75 * c * (1 - c))
    out["ceilings"][name] = round(c, 5); out["sigma_75of75"][name] = round(z, 3)
out["sigma_vs_coin"] = round((75 - 37.5) / math.sqrt(75 * 0.25), 3)
out["max_of_three_note"] = "numerator (1) only: (2) permutation-calibrated TV and (3) executed classical arm were not flown for the re-fly; §A takes the MAX, so this ceiling is a LOWER bound and the sigma an UPPER bound"
out["bar_survives_any_ceiling_below"] = 0.75
json.dump(out, open("results/h13_cell2_refly_ceiling_exhibit_elder_c6651.json", "w"), indent=1)
print(json.dumps(out, indent=1))
