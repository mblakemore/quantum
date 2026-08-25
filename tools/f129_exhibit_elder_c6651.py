#!/usr/bin/env python3
"""F129 EXHIBIT (Elder C6651, court seat) — temporal-steering witness W_TS recomputed from the banked RAW COUNTS of the
Cell 3 flight (job d9rufentfhrs73ds52cg) under the re-analysis protocol
(docs/h13-temporal-steering-reanalysis-protocol-whisper-c5057.md), and diffed against
results/h13_temporal_steering_reanalysis_c5057.json.

Protocol, verbatim in symbols:  W_TS = Σ_{i∈{X,Y,Z}} Σ_{a∈{0,1}} P(a | i,i) · ⟨B_i⟩²_{a}
  — the three DIAGONAL settings (t1 measure Pauli i with outcome a, t2 measure Pauli i with outcome b), per-outcome
  conditional expectation ⟨B_i⟩_a = E[(-1)^b | a], hidden-state bound W_TS ≤ 1 (Jensen), no readout/QND corrections,
  bootstrap SE with B=4000 resamples seed 20260811, CERTIFIED if W_TS > 1 at ≥5σ.

CONVENTIONS TO PIN (the reanalysis records an `alt_convention`, so two were computed): which classical bit is t1's
outcome a and which is t2's b (Qiskit little-endian: rightmost = creg bit 0), and whether prep 0 and prep 1 circuits
are POOLED or treated separately. Both are enumerated and the one reproducing the recorded per-setting terms
(XX 0.9455, YY 0.9579, ZZ 0.9267) is reported as the primary — a construction RECOVERED against the protocol's
formula, not a statistic matched by search. The spatial arm (pair 137/147) is recomputed the same way as a control.
"""
import json, os, sys, math, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RES = os.path.join(ROOT, "results")
JOB = "d9rufentfhrs73ds52cg"
bank = json.load(open(os.path.join(RES, f"h13_cell3_counts_{JOB}_elder_c6651.json")))
man = json.load(open(os.path.join(RES, f"h13_cell3_manifest_{JOB}.json")))
ref = json.load(open(os.path.join(RES, "h13_temporal_steering_reanalysis_c5057.json")))
labels = man["labels"]; pubs = bank["pubs"]
assert len(labels) == len(pubs), (len(labels), len(pubs))

def shots_of(counts, a_idx, b_idx):
    """expand counts -> list of (a, b) with bit positions read from the RIGHT (Qiskit little-endian)."""
    out = []
    for bits, n in counts.items():
        s = bits.replace(" ", "")
        a = int(s[-1 - a_idx]); b = int(s[-1 - b_idx])
        out.extend([(a, b)] * n)
    return out

def W_from_settings(sets):
    """sets: dict i -> list of (a,b) pooled over whatever circuits feed setting (i,i). Returns (W, per_i)."""
    per = {}
    for i, ab in sets.items():
        N = len(ab); term = 0.0
        for a in (0, 1):
            sub = [b for (aa, b) in ab if aa == a]
            if not sub: continue
            Pa = len(sub) / N; Bi = sum(1 - 2 * b for b in sub) / len(sub)
            term += Pa * Bi * Bi
        per[i] = term
    return sum(per.values()), per

def build(arm, a_idx, b_idx, prep_filter):
    sets = {}
    for lab, pub in zip(labels, pubs):
        if lab["arm"] != arm or lab["i"] != lab["j"]: continue
        if prep_filter is not None and lab.get("prep") != prep_filter: continue
        sets.setdefault(lab["i"], []).extend(shots_of(pub["counts"], a_idx, b_idx))
    return sets

def bootstrap_se(sets, B, seed):
    rng = random.Random(seed); Ws = []
    keys = sorted(sets); data = {k: sets[k] for k in keys}
    for _ in range(B):
        res = {k: [data[k][rng.randrange(len(data[k]))] for _ in range(len(data[k]))] for k in keys}
        Ws.append(W_from_settings(res)[0])
    m = sum(Ws) / B; return math.sqrt(sum((w - m) ** 2 for w in Ws) / (B - 1))

def main():
    target = ref["temporal"]["per"]; rows = []
    for arm in ("temporal", "spatial"):
        for (a_idx, b_idx, bits_name) in ((0, 1, "a=bit0,b=bit1"), (1, 0, "a=bit1,b=bit0")):
            for prep in (None, 0, 1):
                sets = build(arm, a_idx, b_idx, prep)
                if not sets: continue
                W, per = W_from_settings(sets)
                rows.append({"arm": arm, "bits": bits_name, "prep": "pooled" if prep is None else prep, "W": W, "per": per,
                             "n_shots_per_setting": {k: len(v) for k, v in sets.items()}})
    # pin the primary: temporal, closest per-setting match to the recorded terms
    temporal = [r for r in rows if r["arm"] == "temporal"]
    def dist(r): return max(abs(r["per"].get(k, 9) - target[k]) for k in ("XX", "YY", "ZZ")) if all(k in r["per"] for k in ("XX", "YY", "ZZ")) else 9
    # protocol per-keys are 'XX','YY','ZZ'; my per keys are 'X','Y','Z' — map
    for r in rows: r["per"] = {k + k: v for k, v in r["per"].items()}
    primary = min(temporal, key=dist)
    sets = build("temporal", 0 if primary["bits"].startswith("a=bit0") else 1, 1 if primary["bits"].startswith("a=bit0") else 0, None if primary["prep"] == "pooled" else primary["prep"])
    se = bootstrap_se(sets, ref["bootstrap"]["B"], ref["bootstrap"]["seed"])
    W = primary["W"]; sigma = (W - 1.0) / se
    exhibit = {"cycle": "C6651", "grader": "elder", "finding": "F129 · H13 temporal steering (post-hoc re-analysis of Cell 3)", "job": JOB,
               "source": {"counts": f"results/h13_cell3_counts_{JOB}_elder_c6651.json (banked C6651 from the job)", "manifest": f"results/h13_cell3_manifest_{JOB}.json",
                          "protocol": ref["protocol"], "compared_to": "results/h13_temporal_steering_reanalysis_c5057.json"},
               "conventions_enumerated": rows,
               "primary_convention": {"bits": primary["bits"], "prep": primary["prep"], "how_pinned": "the enumeration whose per-setting terms are closest to the recorded XX/YY/ZZ; the protocol fixes the formula, this pins only bit order and prep pooling"},
               "recomputed": {"W_TS": W, "per": primary["per"], "se_bootstrap": se, "sigma_over_bound_1": sigma, "B": ref["bootstrap"]["B"], "seed": ref["bootstrap"]["seed"]},
               "recorded": {"W_TS": ref["temporal"]["W"], "per": target, "se": ref["temporal"]["se"], "sigma": ref["temporal"]["sigma"], "alt_convention": ref["temporal"].get("alt_convention")},
               "deltas": {"W": W - ref["temporal"]["W"], "se": se - ref["temporal"]["se"], "sigma": sigma - ref["temporal"]["sigma"],
                          "per": {k: primary["per"][k] - target[k] for k in target}},
               "spatial_control": [r for r in rows if r["arm"] == "spatial"][:2],
               "hs_bound_check_recorded": ref.get("hs_bound_check")}
    exhibit["verdict"] = ("EXHIBIT COMPLETE — W_TS reproduces from raw counts" if abs(exhibit["deltas"]["W"]) < 1e-3 and abs(exhibit["deltas"]["se"]) < 2e-3
                          else "EXHIBIT INCOMPLETE — recomputation does not reproduce the recorded statistic; see deltas") + ". EXHIBIT, not a ratification."
    out = os.path.join(RES, "f129_exhibit_elder_c6651.json"); json.dump(exhibit, open(out, "w"), indent=1)
    print(f"primary convention: {primary['bits']}, prep {primary['prep']}")
    print(f"W_TS recomputed {W:.6f} (recorded {ref['temporal']['W']:.6f}, Δ {W-ref['temporal']['W']:+.2e}); per {{XX {primary['per']['XX']:.4f} YY {primary['per']['YY']:.4f} ZZ {primary['per']['ZZ']:.4f}}} (recorded {target})")
    print(f"SE bootstrap {se:.6f} (recorded {ref['temporal']['se']:.6f}); sigma {sigma:.2f} (recorded {ref['temporal']['sigma']:.2f})")
    for r in rows:
        print(f"  {r['arm']:8s} {r['bits']:16s} prep {str(r['prep']):6s} W {r['W']:.5f}  per {{" + ", ".join(f"{k} {v:.4f}" for k, v in r['per'].items()) + "}")
    print(exhibit["verdict"], "->", os.path.relpath(out, ROOT))

if __name__ == "__main__":
    main()
