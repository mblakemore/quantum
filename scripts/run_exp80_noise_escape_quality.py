#!/usr/bin/env python3
"""
Exp80 (Elder C6271) — Does noise-assisted escape (F42/F43) help you SOLVE BETTER, or only lift
a policy-efficiency RATIO? Confirmation-with-power of the capk-vs-quality split.

CONTEXT: F42/F43 (Ember) claim moderate depolarizing noise RAISES capk (warm-start granular
capture-per-k) 0.543->0.615 ("Goldilocks noise-assisted escape"). My F44 (C6199) already showed
the LANDSCAPE gap contracts under depol -> the capk anti-contraction is an OPTIMIZATION-dynamics
effect, not landscape. OPEN: is that optimization effect a real RESOURCE (better solutions) or a
metric artifact?

CHEAP-FIRST RESULT (re-analysis of Ember's OWN N=8 checkpoint, C6271, advisor-prompted): the
metric that MATTERS — best warm-start SOLUTION QUALITY (best r_warm) — DECREASES MONOTONICALLY with
noise: noiseless 0.7265 -> medium 0.7042 -> high 0.6750 -> very-high 0.6392. Paired high-noiseless
= -0.051, noise hurt 0/8 seeds. So capk rises while solution quality falls (Exp79 pattern: the
ratio-metric improves while the thing you care about degrades).

THIS RUN confirms the quality degradation at larger N and records nfev (the eval-budget confound:
under noise COBYLA may burn MORE function evals, the Exp79 query-confound applied to capk).

PRIMARY METRIC (pre-registered): paired Delta(best r_warm) at "high" dose vs noiseless, N>=60, CI.
  CONFIRM noise-helps-solving iff mean Delta > 0 with CI excluding 0.
  KILL iff mean Delta <= 0 (noise does not help solution quality).
SECONDARY: paired Delta(nfev) (does noise spend more evals?) ; capk replication cited from Ember N=8.

FRAMING (honest): "capk replicates" and "noise is a resource for SOLVING" are DIFFERENT claims.
If capk rises but quality falls, the result is "the capk effect does not translate to better
solutions," NOT "F42/F43 is wrong." Builds on F44; extends Ember's thread.

USAGE: python3 run_exp80_noise_escape_quality.py [--seeds 80] [--levels noiseless,medium,high]
"""
import sys, os, json, time, argparse
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import brute_force_max_cut
from run_exp54_warmstart import evaluate_with_transpiled, pad_params
from run_exp61_bestofk_anchor import build_for_p
from run_exp67_v2_8qubit import EDGES_8, N_QUBITS_8, build_sim, NOISE_LEVELS, K_MAX, SHOTS, MAXITER, P_TARGET, P_ANCHOR

LEVELS = {name: (p1, p2) for name, p1, p2 in NOISE_LEVELS}


def opt_cobyla_nfev(x0, tqc, gp, bp, p, sim, edges, max_cut, nq):
    """COBYLA warm-start optimize; returns (best_ratio, best_x, nfev). Mirrors optimize_cobyla_ws
    (tracks best-seen) but surfaces scipy result.nfev (the eval-budget the noiseless version hides)."""
    best = {"r": 0.0, "x": np.array(x0, dtype=float)}
    def obj(x):
        r = evaluate_with_transpiled(x, tqc, gp, bp, p, sim, edges, max_cut, nq, SHOTS)
        if r > best["r"]:
            best["r"] = r; best["x"] = np.array(x, dtype=float)
        return -r
    res = minimize(obj, x0, method="COBYLA", options={"maxiter": MAXITER})
    return best["r"], best["x"], int(res.nfev)


def run_cell(seed, p1, p2, edges, max_cut, nq):
    np.random.seed(seed)
    sim = build_sim(p1, p2)
    from qiskit_aer import AerSimulator as _AS
    ref = _AS()
    tqc_t, gpt, bpt = build_for_p(P_TARGET, ref, nq, edges)
    tqc_a, gpa, bpa = build_for_p(P_ANCHOR, ref, nq, edges)
    nfev = 0
    # cold
    x0c = np.random.uniform(0, 2 * np.pi, 2 * P_TARGET)
    r_cold, _, fc = opt_cobyla_nfev(x0c, tqc_t, gpt, bpt, P_TARGET, sim, edges, max_cut, nq); nfev += fc
    # K anchors
    anchors = []
    for _ in range(K_MAX):
        x0a = np.random.uniform(0, 2 * np.pi, 2 * P_ANCHOR)
        ra, xa, fa = opt_cobyla_nfev(x0a, tqc_a, gpa, bpa, P_ANCHOR, sim, edges, max_cut, nq); nfev += fa
        anchors.append((ra, xa))
    # best-first warm-starts
    r_warm = []
    cur = 0
    cache = {}
    for j in range(K_MAX):
        if anchors[j][0] > anchors[cur][0]:
            cur = j
        if cur not in cache:
            x0w = pad_params(anchors[cur][1], P_ANCHOR, P_TARGET)
            rw, _, fw = opt_cobyla_nfev(x0w, tqc_t, gpt, bpt, P_TARGET, sim, edges, max_cut, nq); nfev += fw
            cache[cur] = rw
        r_warm.append(cache[cur])
    return {"seed": seed, "r_cold": float(r_cold), "r_anchors": [float(a[0]) for a in anchors],
            "r_warm_byk": [float(x) for x in r_warm], "best_warm": float(max(r_warm)),
            "nfev": int(nfev)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=80)
    ap.add_argument("--levels", default="noiseless,medium,high")
    args = ap.parse_args()
    levels = args.levels.split(",")
    max_cut = brute_force_max_cut(N_QUBITS_8, EDGES_8)
    print(f"Exp80 | EDGES_8 n={N_QUBITS_8} max_cut={max_cut} | seeds={args.seeds} | levels={levels}", flush=True)

    data = {lvl: [] for lvl in levels}
    for lvl in levels:
        p1, p2 = LEVELS[lvl]
        t0 = time.time()
        for s in range(args.seeds):
            data[lvl].append(run_cell(s, p1, p2, EDGES_8, max_cut, N_QUBITS_8))
        bw = np.array([c["best_warm"] for c in data[lvl]])
        nf = np.array([c["nfev"] for c in data[lvl]])
        print(f"  {lvl:<10} best_warm mean={bw.mean():.4f} sd={bw.std():.4f} | nfev mean={nf.mean():.0f} | {time.time()-t0:.0f}s", flush=True)

    # paired analysis vs noiseless
    out = {"experiment": "exp80_noise_escape_quality", "cycle": 6271, "author": "elder",
           "seeds": args.seeds, "levels": levels, "max_cut": max_cut, "data": data, "paired": {}}
    base = {c["seed"]: c for c in data.get("noiseless", [])}
    print("\n=== PAIRED vs noiseless (primary = best_warm solution quality) ===", flush=True)
    for lvl in levels:
        if lvl == "noiseless" or not base:
            continue
        cur = {c["seed"]: c for c in data[lvl]}
        common = sorted(set(base) & set(cur))
        dq = np.array([cur[s]["best_warm"] - base[s]["best_warm"] for s in common])
        dnf = np.array([cur[s]["nfev"] - base[s]["nfev"] for s in common])
        se = dq.std(ddof=1) / np.sqrt(len(dq))
        ci = (dq.mean() - 1.96 * se, dq.mean() + 1.96 * se)
        out["paired"][lvl] = {"n": len(common), "dquality_mean": float(dq.mean()),
                              "dquality_ci95": [float(ci[0]), float(ci[1])],
                              "noise_better_frac": float((dq > 0).mean()),
                              "dnfev_mean": float(dnf.mean())}
        verdict = "CONFIRM (noise helps quality)" if ci[0] > 0 else "KILL (noise does NOT help quality)"
        print(f"  {lvl:<10} Dquality={dq.mean():+.4f} CI95=[{ci[0]:+.4f},{ci[1]:+.4f}] "
              f"noise-better={ (dq>0).mean()*100:.0f}% | Dnfev={dnf.mean():+.0f} -> {verdict}", flush=True)

    any_confirm = any(v["dquality_ci95"][0] > 0 for v in out["paired"].values())
    out["overall_verdict"] = ("CONFIRM: noise improves solution quality at matched protocol"
                              if any_confirm else
                              "KILL: noise does NOT improve solution quality (capk rise does not translate to better solutions)")
    print(f"\n  OVERALL: {out['overall_verdict']}", flush=True)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "exp80_noise_escape_quality.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)


if __name__ == "__main__":
    main()
