#!/usr/bin/env python3
"""
Exp64-tau: tau-calibration of k-adaptive escalation via leave-one-out CV (N=17).
ZERO COMPUTE: pure replay over Exp61 + Exp62 results. Closes Finding 38's named tau-calibration arm.
Pre-reg: exp64tau-calibration-loocv-preregistration.md (committed 0fafe40 BEFORE this ran).

Policy (identical to Exp63): a0 = r_p3_single; if a0 >= tau -> single (k=1, lift=lift_single);
else -> full-k best (k=3, lift=lift_best). Capture = sum(adaptive_lift)/sum(lift_best) over fold.
LOO: tau_i = quantile(r_p3_single of the OTHER 16 cells); classify cell i with tau_i.
"""
import json, os, statistics, random

HERE = os.path.dirname(os.path.abspath(__file__))

def load(fn):
    with open(os.path.join(HERE, fn)) as f:
        return json.load(f)

exp61 = load("exp61_results.json")["data"]          # 8 EDGES_20 cells, seeds 42-49
exp62 = load("exp62_results.json")["data"]          # 12 cells across 4 instances

# Clean de-duped pool (same de-dup F38 used): Exp61 EDGES (8) + Exp62 FRESH only (exclude EDGES_20_ref dupes)
pool = []
for c in exp61:
    pool.append({"src": "exp61", "instance": "EDGES_20", "seed": c["seed"],
                 "a0": c["r_p3_single"], "lift_single": c["lift_single"], "lift_best": c["lift_best"]})
for c in exp62:
    if c.get("instance") == "EDGES_20_ref":
        continue   # dupe of exp61 seeds 42-44
    pool.append({"src": "exp62", "instance": c["instance"], "seed": c["seed"],
                 "a0": c["r_p3_single"], "lift_single": c["lift_single"], "lift_best": c["lift_best"]})

N = len(pool)
assert N == 17, f"expected N=17, got {N}"

def quantile(xs, q):
    """Inclusive linear-interpolation quantile (q in [0,1]); q=0.5 == median."""
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(pos); frac = pos - lo
    if lo + 1 >= len(s):
        return s[-1]
    return s[lo] + frac * (s[lo + 1] - s[lo])

def adaptive_lift(cell, tau):
    if cell["a0"] >= tau:
        return cell["lift_single"], 1
    return cell["lift_best"], 3

def loo_capture(rule_q):
    """Leave-one-out: tau_i fit on the other 16 at quantile rule_q, evaluate held-out cell."""
    sum_adapt, sum_best, k_list, escal = 0.0, 0.0, [], 0
    for i in range(N):
        others = [pool[j]["a0"] for j in range(N) if j != i]
        tau_i = quantile(others, rule_q)
        a_lift, k_used = adaptive_lift(pool[i], tau_i)
        sum_adapt += a_lift
        sum_best += pool[i]["lift_best"]
        k_list.append(k_used)
        if k_used == 3:
            escal += 1
    capture = sum_adapt / sum_best if sum_best != 0 else float("nan")
    return {"capture": capture, "mean_k_used": statistics.mean(k_list),
            "escalate_frac": escal / N, "sum_adapt": sum_adapt, "sum_best": sum_best}

# --- LOO-CV for the three PRE-SPECIFIED quantile rules ---
rules = {"q25": 0.25, "median": 0.50, "q75": 0.75}
loo = {name: loo_capture(q) for name, q in rules.items()}

med = loo["median"]
cap_range = max(loo[r]["capture"] for r in rules) - min(loo[r]["capture"] for r in rules)

# --- Bootstrap 95% CI on the median-rule pooled LOO capture (resample 17 cells) ---
# Recompute capture on each bootstrap resample using a FIXED tau (full-pool median) to isolate
# sampling noise in the capture ratio (the LOO tau barely moves; this CI is on the ratio's power).
random.seed(6128)
tau_full = quantile([c["a0"] for c in pool], 0.50)
def cap_at_tau(cells, tau):
    sa = sb = 0.0
    for c in cells:
        al, _ = adaptive_lift(c, tau)
        sa += al; sb += c["lift_best"]
    return sa / sb if sb != 0 else float("nan")
boot = []
for _ in range(2000):
    rs = [pool[random.randrange(N)] for _ in range(N)]
    v = cap_at_tau(rs, tau_full)
    if v == v:  # not NaN
        boot.append(v)
boot.sort()
ci = (boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot))])

# --- Descriptive frontier (HAIRCUT-FLAGGED, not graded) ---
a0s = sorted(set(c["a0"] for c in pool))
frontier = []
# sweep tau just-above each a0 boundary
for t in [-1e9] + [a + 1e-9 for a in a0s] + [1e9]:
    fr = cap_at_tau(pool, t)
    sa = sum(1 for c in pool if c["a0"] < t)  # escalated count
    frontier.append({"tau": (None if abs(t) > 1e8 else round(t, 6)), "capture": round(fr, 4),
                     "escalate_frac": round(sa / N, 4)})
pool_argmax = max(frontier, key=lambda r: r["capture"])

# --- VERDICTS (grade by the LETTER vs pre-reg) ---
P1 = med["capture"] >= 0.80
P2 = (1 < med["mean_k_used"] < 3)
P3 = med["capture"] > med["escalate_frac"]
P4 = cap_range <= 0.20

# Brier (outcome=1 if prediction held)
confs = {"P1": 0.60, "P2": 0.90, "P3": 0.70, "P4": 0.45}
held = {"P1": P1, "P2": P2, "P3": P3, "P4": P4}
brier = sum((confs[p] - (1 if held[p] else 0)) ** 2 for p in confs) / len(confs)

out = {
    "experiment": "Exp64-tau", "title": "tau-calibration of k-adaptive escalation via LOO-CV",
    "author": "Elder", "cycle": "C6128", "compute": "NONE (replay over Exp61+Exp62)",
    "pool_N": N, "tau_full_pool_median": round(tau_full, 6),
    "loo_cv": {r: {k: round(v, 6) for k, v in loo[r].items()} for r in loo},
    "median_rule_capture_ci95": [round(ci[0], 4), round(ci[1], 4)],
    "quantile_capture_range": round(cap_range, 4),
    "descriptive_frontier_HAIRCUT_FLAGGED": frontier,
    "pool_argmax_tau_NOT_THE_FINDING": pool_argmax,
    "verdicts": {"P1_capture>=0.80": P1, "P2_saves_compute": P2,
                 "P3_beats_cost_matched_random": P3, "P4_tau_robust_range<=0.20": P4},
    "brier_score": round(brier, 4),
}
with open(os.path.join(HERE, "exp64tau_results.json"), "w") as f:
    json.dump(out, f, indent=1)

print(f"N={N}  tau_full_median={tau_full:.4f}")
for r in rules:
    L = loo[r]
    print(f"  LOO[{r:>6}]: capture={L['capture']:+.4f}  mean_k={L['mean_k_used']:.3f}  escal_frac={L['escalate_frac']:.3f}")
print(f"median-rule capture 95%CI = [{ci[0]:+.4f}, {ci[1]:+.4f}]   quantile-range={cap_range:.4f}")
print(f"descriptive pool-argmax (NOT finding): tau={pool_argmax['tau']} capture={pool_argmax['capture']} escal={pool_argmax['escalate_frac']}")
print(f"VERDICTS  P1={P1} P2={P2} P3={P3} P4={P4}   Brier={brier:.4f}")
