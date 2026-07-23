#!/usr/bin/env python3
"""Attenuation Map v1.1 — the full-arc dataset compiler. Whisper C4982, substrate claude-fable-5.

v1.0 (results/attenuation_map.json): per-device lambda_eff from d2q=4 two-qubit witnesses —
depth-only, modal-observable, single-width. The decoder-race arc (C4973–C4981, F120/F121)
measured everything v1.0 could not see. v1.1 adds, WITHOUT discarding v1.0's seed points:

  L1  PER-BIT INFORMATION LAW: mean per-bit bias b(d2q) per (die, width, t, register-class)
      series, fitted lambda_bit where >=3 points exist (C4974 regression rule enforced:
      fit() REFUSES <3 points — the C4973 single-point-min-norm bug class, structurally).
  L2  OBSERVABLE GAP: lambda_modal >> lambda_bit (the F120 30x) — modal rows kept for contrast.
  L3  MAGIC TAX rho_t rows (clean vs confounded, labeled per Elder #630/#652).
  L4  ROUTING VARIANCE + EXCLUSION FOOTPRINT rows (d2q is a random variable, not a constant).
  L5  DEFECT REGISTRY per die (dated; calibration-dependent): tilted / stuck-at-readout /
      circuit-level-bad — the race-4/5 taxonomy.

Also computes the arc's one outstanding number: rho_t(167) on kingston — the SECOND clean
matched-depth point (race-6 card rule 4; Elder #630 clean-curve requirement).
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
NPHYS = 156


def J(name):
    return json.load(open(os.path.join(RES, name)))


def s_of(d, block):
    e = d.get(block, d.get("seals", {}).get(block, {}))
    return e["s_str"] if "s_str" in e else d["seals"][block]["s_str"]


def bias_from_row(row, s_str):
    """mean per-bit bias toward s from a stored bit_frac (marginal order) row."""
    frac = row["bit_frac_marginal_order"]
    n = len(frac)
    vals = []
    for p in range(n):                       # display pos p <-> marginal index n-1-p
        f = frac[n - 1 - p]
        want = int(s_str[p])
        vals.append((f - 0.5 if want == 1 else 0.5 - f) * 2)
    return float(np.mean(vals))


def hd(a, b):
    return sum(x != y for x, y in zip(a, b))


def fit_lambda(points, label):
    """ln(bias) ~ -lambda*d2q + c. REFUSES <3 points (C4974 regression rule)."""
    pts = [(d, b) for d, b in points if b > 0]
    if len(pts) < 3:
        return {"label": label, "n_points": len(pts),
                "lambda_bit": None, "note": "REFUSED: <3 points post-filter (C4974 rule) — points reported, no law claimed"}
    d = np.array([p[0] for p in pts], float)
    lb = np.log([p[1] for p in pts])
    A = np.vstack([d, np.ones_like(d)]).T
    coef, *_ = np.linalg.lstsq(A, lb, rcond=None)
    return {"label": label, "n_points": len(pts), "lambda_bit": round(float(-coef[0]), 5),
            "intercept_bias": round(float(math.exp(coef[1])), 4),
            "points": [(int(x), round(float(y), 4)) for x, y in pts]}


rows = []          # master dataset
def add(die, day, width, t, d2q, reg, bias, dec_hd, src, note=""):
    rows.append({"die": die, "date": day, "width": width, "t": t, "d2q": int(d2q),
                 "register_class": reg, "mean_perbit_bias": (round(bias, 4) if bias is not None else None),
                 "decode_HD": dec_hd, "source": src, "note": note})


# ---- C4973 ladder (via C4974 re-analysis) — marrakesh w40 t0, pre-hygiene era ----
c4974 = J("exp_hss_infodecode_exploratory.json")
for r in c4974["rungs"]:
    add("marrakesh", "2026-07-22", 40, 0, r["tag"].split("d2q")[1], "pre-hygiene",
        2 * r["mean_perbit_agreement_with_s"] - 1, r["HD_majority_s"],
        "C4973 banked ladder (C4974)", "blind majority HD; chase fixed 185")

# ---- race-1 (C4976) — HD-only rows (no bit_frac stored) ----
for d2q, h in ((28, 0), (84, 0), (140, 1), (196, 3)):
    add("marrakesh", "2026-07-23a", 40, 0, d2q, "pre-hygiene", None, h,
        "race-1 rung0 (reveal #564)", "bias not stored; HD under pinned convention")

# ---- race-2 (C4977) — HD-only rows ----
for d2q, h, note in ((36, 0, ""), (108, 0, ""), (190, 0, "shot-matched 100k"),
                     (245, 1, "shots-limited: subs 3/3/3/1")):
    add("marrakesh", "2026-07-23b", 40, 0, d2q, "pre-hygiene", None, h,
        "race-2 (reveal #578)", note)

# ---- races 3-6: bias from stored bit_frac + reveals ----
def harvest(gate_json, race_json, rev_r0, rev_race, die, day, reg, r0key="rung0_n40"):
    g, rc = J(gate_json), J(race_json)
    s0 = s_of(J(rev_r0), r0key)
    sr = s_of(J(rev_race), "race_n40")
    out = {}
    for r in g["rows"]:
        blk = r["block"]
        key = "s_hat_GRADED_calibrated_majority" if "s_hat_GRADED_calibrated_majority" in r else "s_hat"
        if r.get("npubs") not in (None, 16):
            continue
        if blk.startswith("ladder") or blk.startswith("twin40") or blk.startswith("rung0"):
            b = bias_from_row(r, s0) if "bit_frac_marginal_order" in r else None
            add(die, day, 40, 0, r["d2q"], reg, b, hd(r[key], s0), gate_json)
            out[(blk, r["d2q"])] = b
    for r in rc["rows"] if "rows" in rc else []:
        if r.get("npubs") == max(x.get("npubs", 0) for x in rc["rows"]):
            key = "s_hat_GRADED_calibrated_majority" if "s_hat_GRADED_calibrated_majority" in r else "s_hat"
            b = bias_from_row(r, sr) if "bit_frac_marginal_order" in r else None
            add(die, day, 40, 80, r["d2q"], reg, b, hd(r[key], sr), race_json)
            out[("race", r["d2q"])] = b
    return out

# race-4 (clean, marrakesh)
r4 = harvest("exp_hss_race4_gate_shat.json", "exp_hss_race4_race_shat.json",
             "exp_hss_race4_reveal_rung0_ember.json", "exp_hss_race4_reveal_race_ember.json",
             "marrakesh", "2026-07-23d", "clean(exclusion)")
# race-5 (dirty, marrakesh)
r5 = harvest("exp_hss_race5_gate_shat.json", "exp_hss_race5_race_shat.json",
             "exp_hss_race5_reveal_rung0_ember.json", "exp_hss_race5_reveal_race_ember.json",
             "marrakesh", "2026-07-23e", "dirty(no-exclusion)")
# race-6 (clean-class, kingston)
r6 = harvest("exp_hss_race6_gate_shat.json", "exp_hss_race6_race_shat.json",
             "exp_hss_race6_reveal_rung0_ember.json", "exp_hss_race6_reveal_race_ember.json",
             "kingston", "2026-07-23f", "clean-class(pre-gate certified)")

# race-3 (dirty, marrakesh) — different row schema (s_hat only + bit_frac)
g3, rc3 = J("exp_hss_race3_gate_shat.json"), J("exp_hss_race3_race_shat.json")
s0_3 = s_of(J("exp_hss_race3_reveal_rung0_ember.json"), "rung0_n40")
s32_3 = s_of(J("exp_hss_race3_reveal_rung0_ember.json"), "rung0_n32")
sr3 = s_of(J("exp_hss_race3_reveal_race_ember.json"), "race_n40")
sr32 = s_of(J("exp_hss_race3_reveal_race_ember.json"), "race_n32")
for r in g3["rows"]:
    if r.get("npubs") not in (None, 16):
        continue
    if r["block"].startswith("ladder") or r["block"] == "twin40":
        b = bias_from_row(r, s0_3) if "bit_frac_marginal_order" in r else None
        add("marrakesh", "2026-07-23c", 40, 0, r["d2q"], "dirty(11/16 systematic)",
            b, hd(r["s_hat"], s0_3), "race-3 gate")
    if r["block"] == "twin32":
        b = bias_from_row(r, s32_3) if "bit_frac_marginal_order" in r else None
        add("marrakesh", "2026-07-23c", 32, 0, r["d2q"], "dirty", b, hd(r["s_hat"], s32_3), "race-3 twin32")
for blk, n, st in (("race_n40", 40, sr3), ("race_n32", 32, sr32)):
    rws = [r for r in rc3["race"][blk]] if "race" in rc3 else []
    if rws:
        r = rws[-1]
        b = bias_from_row(r, st) if "bit_frac_marginal_order" in r else None
        add("marrakesh", "2026-07-23c", n, 80, r.get("d2q", 0) or (125 if n == 40 else 182),
            "dirty", b, hd(r["s_hat"], st), "race-3 race")

# ---- fits (per series, C4974 rule enforced) ----
def series(die, reg, t=0, width=40):
    return [(r["d2q"], r["mean_perbit_bias"]) for r in rows
            if r["die"] == die and r["register_class"] == reg and r["t"] == t
            and r["width"] == width and r["mean_perbit_bias"] is not None]

fits = [
    fit_lambda(series("marrakesh", "pre-hygiene"), "marrakesh w40 t0 pre-hygiene (C4973 ladder)"),
    fit_lambda(series("marrakesh", "clean(exclusion)"), "marrakesh w40 t0 CLEAN register (race-4)"),
    fit_lambda(series("marrakesh", "dirty(no-exclusion)"), "marrakesh w40 t0 dirty (race-5)"),
    fit_lambda(series("kingston", "clean-class(pre-gate certified)"), "kingston w40 t0 clean-class (race-6)"),
]

# ---- rho_t(167) — the SECOND clean point (race-6, kingston), per-pub bootstrap ----
MAN6 = J("exp_hss_race6_flight_manifest.json")
rev6r = J("exp_hss_race6_reveal_race_ember.json")
rev6l = J("exp_hss_race6_reveal_rung0_ember.json")
from qiskit_ibm_runtime import QiskitRuntimeService
res6 = QiskitRuntimeService().job(MAN6["job_id"]).result()
def perpub_bias6(block, laykey, s_str):
    lay = MAN6["layouts"][laykey]["final"]
    idx = [NPHYS - 1 - p for p in lay]
    sbits = np.array([int(b) for b in s_str])
    out = []
    for i, m in enumerate(MAN6["pubs_meta"]):
        if m["block"] != block:
            continue
        c = res6[i].data[list(res6[i].data.keys())[0]].get_counts()
        ones = np.zeros(40); tot = 0
        for st, cnt in c.items():
            marg = "".join(st[j] for j in idx)[::-1]
            ones += cnt * (np.frombuffer(marg.encode(), np.uint8).astype(np.int64) - 48)
            tot += cnt
        frac = ones / tot
        out.append(float((np.where(sbits == 1, frac - 0.5, 0.5 - frac) * 2).mean()))
    return np.array(out)
b0 = perpub_bias6("twin40", "twin40_src", s_of(rev6l, "rung0_n40"))
b8 = perpub_bias6("race_n40", "race_n40", s_of(rev6r, "race_n40"))
rng = np.random.default_rng(20260723)
boots = [rng.choice(b8, len(b8)).mean() / rng.choice(b0, len(b0)).mean() for _ in range(1000)]
lo, hi = np.percentile(boots, [2.5, 97.5])
rho167 = {"matched_d2q": 167, "die": "kingston", "clean": True,
          "bias_t0": round(float(b0.mean()), 4), "bias_t80": round(float(b8.mean()), 4),
          "rho_t": round(float(b8.mean() / b0.mean()), 4),
          "ci95": [round(float(lo), 4), round(float(hi), 4)], "pubs": [len(b0), len(b8)]}

rho_rows = [
    {**rho167, "status": "CLEAN point #2 (race-6)"},
    {"matched_d2q": 217, "die": "marrakesh", "clean": True, "rho_t": 0.7427,
     "ci95": [0.7307, 0.7542], "status": "CLEAN point #1 (race-4)"},
    {"matched_d2q": 125, "die": "marrakesh", "clean": False, "rho_t": 0.797,
     "status": "CONFOUNDED (race-3 dirty register) — not a curve point"},
    {"matched_d2q": 190, "die": "marrakesh", "clean": False, "rho_t": 0.796,
     "status": "CONFOUNDED (race-5 dirty) — not a curve point"},
    {"matched_d2q": 195, "die": "marrakesh", "clean": False, "rho_t": 0.531,
     "status": "CONFOUNDED (race-3, n32 + dirty) — not a curve point"},
]

out = {
    "card": "attenuation_map_v1_1", "cycle": "C4982", "substrate": "claude-fable-5",
    "supersedes": "attenuation_map.json v1.0 seed points RETAINED below; the modal-observable "
                  "lambda_global(w40)=0.091 'law' from C4973 stage-1 is RETRACTED as a law "
                  "(single-point min-norm fit, C4974 correction) — kept only as the modal-vs-bit "
                  "observable-gap illustration",
    "v1_0_seed_points": J("attenuation_map.json")["seed_points"],
    "model_v1_1": "per-bit: bias(d2q) ~ b0*exp(-lambda_bit*d2q) per (die, width, t, register-class); "
                  "decoder success predicted by bias*sqrt(N_shots) per bit vs threshold; "
                  "modal observable decays ~width*faster (F120: lambda_modal ~ gates_per_slot*lambda_2q, "
                  "lambda_bit ~ gates_per_slot*lambda_2q/width)",
    "regression_rule": "fit() refuses <3 points post-filter (C4973 single-point-fit bug class)",
    "dataset_rows": rows,
    "lambda_bit_fits": fits,
    "rho_t_rows": rho_rows,
    "routing_variance_row": {
        "note": "d2q is a RANDOM VARIABLE of the transpile, not a device constant",
        "marrakesh_w40_best_of_20_same_week": [146, 194, 205],
        "marrakesh_w40_best_of_100": 125,
        "marrakesh_w40_best_of_100_clean8_excluded": "INFEASIBLE (0/100) — device-limitation, race-6 abort",
        "marrakesh_w40_best_of_100_clean6_excluded": 217,
        "kingston_w40_best_of_100": 167,
        "exclusion_footprint_marrakesh": "+92 slots (125->217) for 6 excluded qubits; infeasible for 8"},
    "defect_registry": {
        "taxonomy": ["tilted (threshold-correctable, cal-visible)",
                     "stuck-at-readout (cal-visible, threshold-uncorrectable)",
                     "circuit-level-bad (cal-INVISIBLE, only a dynamic pre-gate catches it)"],
        "marrakesh_2026-07-23": {"near_stuck": [113], "circuit_bad": [114, 115],
                                 "measured_bad": [67, 119, 133, 134, 135],
                                 "tilted_correctable": [4, 33, 65, 68, 69, 73, 78]},
        "kingston_2026-07-23": {"stuck_98pct_with_leakage": [16],
                                "tilted_correctable": [92, 101],
                                "note": "flown register clean-class (pre-gate exact x2, zero flips)"},
        "warning": "calibration-dependent; re-screen per window; the clean-ladder pre-gate is the "
                   "only guard for class-3 defects"},
    "standing_usage": "pre-flight: predict decoder success from the matching series' lambda_bit + "
                      "planned shots; place gates INSIDE measured capability (C4977 lesson); treat "
                      "routing depth as a lottery — pre-register caps and best-of-N; guard grades "
                      "with the free t=0 pre-gate (C4980/81 lesson)",
}
path = os.path.join(RES, "attenuation_map_v1_1.json")
json.dump(out, open(path, "w"), indent=1)
print("rows:", len(rows))
for f in fits:
    print(f)
print("rho_t(167) kingston CLEAN #2:", rho167)
print("wrote", os.path.normpath(path))
