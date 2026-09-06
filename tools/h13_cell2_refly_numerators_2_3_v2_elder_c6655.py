#!/usr/bin/env python3
"""§A numerators (2') and (3') on the MAGNITUDE-ONLY, PER-DRAW information set — computed exactly as ruled by the
register seat on board#399 (Whisper C5097, quantum@e35b3ac) after my mis-specified first run (b13045f).
Bank: re-fly pre-run job d9tb3tgpdb6s73e7082g. Pure function; seeded; twirl POOLED per (unit, arm); null = within-unit
arm-label swap. Writes results/h13_cell2_refly_numerators_2_3_v2_elder_c6655.json."""
import json, math, random, collections
import numpy as np
J = "d9tb3tgpdb6s73e7082g"; W = 0.40; B = 2000; SEED = 6655; D1 = 0.03541
man = json.load(open(f"results/h13_cell2_refly_prerun_manifest_{J}.json")); res = json.load(open(f"results/h14_lock5_rescue_h13_cell2_{J}.json"))
labels, pubs = man["labels"], res["pubs"]; assert len(labels) == len(pubs) == 480
acc = collections.defaultdict(lambda: [0, 0])
for lab, pub in zip(labels, pubs):
    s = acc[(lab["unit"], lab["arm"], lab["basis"])]
    for bs in pub["data"]["c"]:
        s[0] += (1 - 2 * int(bs[0])) * (1 - 2 * int(bs[1])); s[1] += 1
C = {k: v[0] / v[1] for k, v in acc.items()}
units = sorted({k[0] for k in C}); bases = ["X", "Y", "Z"]; U = len(units)
feat = {(u, a): np.array([abs(C[(u, a, b)]) for b in bases]) for u in units for a in ("CE", "CC")}
m = {k: float(v.mean()) for k, v in feat.items()}                       # per-draw pooled magnitude
ce = np.array([m[(u, "CE")] for u in units]); cc = np.array([m[(u, "CC")] for u in units])
# ── (2') distances between the two 20-sample distributions ─────────────────────────────────────
def ks(a, b):
    xs = np.sort(np.concatenate([a, b])); Fa = np.searchsorted(np.sort(a), xs, side="right") / len(a); Fb = np.searchsorted(np.sort(b), xs, side="right") / len(b)
    return float(np.max(np.abs(Fa - Fb)))
def tv_binned(a, b, k):
    pooled = np.concatenate([a, b]); edges = np.quantile(pooled, np.linspace(0, 1, k + 1)[1:-1])
    ha = np.bincount(np.searchsorted(edges, a, side="right"), minlength=k) / len(a); hb = np.bincount(np.searchsorted(edges, b, side="right"), minlength=k) / len(b)
    return 0.5 * float(np.abs(ha - hb).sum())
stats = {"D": ks, "TV4": lambda a, b: tv_binned(a, b, 4), "TV8": lambda a, b: tv_binned(a, b, 8)}
rng = random.Random(SEED); out2 = {}
nulls = {k: [] for k in stats}
for _ in range(B):
    swap = [rng.random() < 0.5 for _ in units]
    a = np.array([cc[i] if swap[i] else ce[i] for i in range(U)]); b = np.array([ce[i] if swap[i] else cc[i] for i in range(U)])
    for k, f in stats.items(): nulls[k].append(f(a, b))
for k, f in stats.items():
    obs = f(ce, cc); mu = float(np.mean(nulls[k])); sd = float(np.std(nulls[k], ddof=1)); cal = max(0.0, obs - mu); ub = cal + 2 * sd
    out2[k] = {"obs": obs, "null_mean": mu, "null_sd": sd, "calibrated": cal, "UB": ub, "z": (obs - mu) / sd if sd > 0 else None}
win2 = max(out2, key=lambda k: out2[k]["UB"]); d2 = W * out2[win2]["UB"]
# ── (3') executed classical arm, leave-one-unit-out over 40 (unit, arm) records ────────────────
def louo(predict):
    correct = 0
    for u in units:
        tr = [(feat[(v, a)], a) for v in units if v != u for a in ("CE", "CC")]
        for a in ("CE", "CC"): correct += (predict(tr, feat[(u, a)]) == a)
    return correct / (2 * U)
def thresh_rule(tr, x):
    ce_m = np.mean([f.mean() for f, a in tr if a == "CE"]); cc_m = np.mean([f.mean() for f, a in tr if a == "CC"])
    med = float(np.median([f.mean() for f, a in tr])); direction = 1 if ce_m >= cc_m else -1     # learned on the training folds
    return "CE" if direction * (x.mean() - med) >= 0 else "CC"
def lda_rule(tr, x):
    X1 = np.array([f for f, a in tr if a == "CE"]); X0 = np.array([f for f, a in tr if a == "CC"])
    mu1, mu0 = X1.mean(0), X0.mean(0); S = (np.cov(X1.T, ddof=1) + np.cov(X0.T, ddof=1)) / 2 + 1e-9 * np.eye(3)
    w = np.linalg.solve(S, mu1 - mu0); c = w @ (mu1 + mu0) / 2
    return "CE" if w @ x - c >= 0 else "CC"
s_thr = louo(thresh_rule); s_lda = louo(lda_rule); s = max(s_thr, s_lda); win3 = "median-threshold(direction learned)" if s_thr >= s_lda else "LDA(3 magnitudes)"
Nrec = 2 * U; se = math.sqrt(s * (1 - s) / Nrec); s_ub = s + 2 * se; d3 = 2 * W * (s_ub - 0.5)
d = max(D1, d2, d3); which = {D1: "1 model d/W (c6651 exhibit)", d2: f"2' distance ({win2})", d3: f"3' classical arm ({win3})"}[d]
c = 0.5 + d / (2 * W); z = (75 - 75 * c) / math.sqrt(75 * c * (1 - c))
out = {"job": J, "W": W, "seed": SEED, "B": B, "units": U, "information_set": "magnitude-only per draw, twirl pooled per (unit, arm); null = within-unit arm swap (board#399 ruling e35b3ac)",
       "per_draw_pooled_magnitude": {"CE_mean": float(ce.mean()), "CC_mean": float(cc.mean()), "gap_CE_minus_CC": float(ce.mean() - cc.mean())},
       "n2_prime": {"stats": out2, "winner": win2, "d2": d2}, "n3_prime": {"s_threshold_LOUO": s_thr, "s_LDA_LOUO": s_lda, "s": s, "winner": win3, "N_records": Nrec, "se": se, "s_UB": s_ub, "d3": d3},
       "d1": D1, "d_max": d, "max_is": which, "ceiling_W_p": c, "sigma_75of75": z, "graded_finding_registered": {"ceiling": 0.54426, "sigma": 7.925},
       "delta_vs_registered": {"ceiling": c - 0.54426, "sigma": z - 7.925}, "bar_5sigma_fails_at_d": 0.200}
json.dump(out, open("results/h13_cell2_refly_numerators_2_3_v2_elder_c6655.json", "w"), indent=1)
print(f"per-draw pooled |C|: CE {ce.mean():.5f} CC {cc.mean():.5f} gap {ce.mean()-cc.mean():+.5f}")
for k, v in out2.items(): print(f"  (2') {k}: obs {v['obs']:.4f} null {v['null_mean']:.4f}±{v['null_sd']:.4f} -> calibrated {v['calibrated']:.4f} UB {v['UB']:.4f} (z {v['z']:+.2f})")
print(f"  (2') winner {win2}: d2' = {d2:.5f}")
print(f"  (3') LOUO accuracy: threshold(direction learned) {s_thr:.4f}, LDA {s_lda:.4f} -> s {s:.4f} ± {se:.4f}, s_UB {s_ub:.4f}, d3' = {d3:.5f}")
print(f"d = max({D1:.5f}, {d2:.5f}, {d3:.5f}) = {d:.5f} <- {which}; ceiling {c:.5f}; 75/75 = {z:.3f}σ (registered 0.54426 / 7.925σ; Δσ {z-7.925:+.3f})")
