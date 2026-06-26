#!/usr/bin/env python3
"""
Exp67: Depolarizing noise dose-response for warm-start granular escalation.
Ember C3982 (pre-reg: experiments/exp67-depolarizing-dose-response-preregistration.md).

PURPOSE: Isolate the mechanism behind Finding 42's anti-contraction result.
  Finding 42 (Exp66): noiseless capk=0.5236 < FakeMarrakesh capk=0.5625 (noise HELPS).
  Three explanations: (A) non-unital amplitude damping, (B) noise-assisted escape, (C) stat noise.

  This experiment uses PURE DEPOLARIZING (unital) noise at 4 levels.
  Contractivity theorem (nc-ch8-9) predicts unital noise CONTRACTS capk.
  H1: depolarizing at FakeMarrakesh-equiv rates DOES contract (capk < noiseless) → supports (A).
  H1 FAIL: anti-contraction persists in unital case → rules out (A), supports (B) or (C).

USAGE:
  python3 run_exp67_depolarizing_dose_response.py --smoke    # 2 cells level 1 fast check
  python3 run_exp67_depolarizing_dose_response.py --run      # full 32 cells (4 levels × 8 seeds)
  python3 run_exp67_depolarizing_dose_response.py --level 2  # single noise level only (8 cells)
"""
import sys, os, json, time, argparse
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from run_exp61_bestofk_anchor import build_for_p
from run_exp57_instance_generalization import gen_instance

# Noiseless baseline from Exp66 (EDGES_20 seeds 42-49, 8 cells)
# These will be loaded at runtime if results file exists, otherwise use fixed reference
EXP66_NOISELESS_CAPK  = 0.5236   # from Finding 42
EXP64_FAKEMARRAKESH_CAPK = 0.5625  # from Finding 41

# EDGES_20 seeds 42-49 (same pool as Exp64/Exp66)
EDGES_SEEDS = [42, 43, 44, 45, 46, 47, 48, 49]

K_MAX  = 3
SHOTS  = 256
MAXITER = 20

# Noise levels: (label, p1_1qubit, p2_2qubit)
NOISE_LEVELS = [
    ("low",       0.0002, 0.002),
    ("medium",    0.0005, 0.005),
    ("high",      0.001,  0.010),
    ("very-high", 0.003,  0.030),
]

RESULTS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
CKPT_PATH    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "exp67_checkpoint.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp67_results.json")


def build_depolarizing_sim(p1, p2):
    """Build AerSimulator with depolarizing noise at given per-gate error rates."""
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    if p1 == 0 and p2 == 0:
        return AerSimulator(method="statevector")  # noiseless, explicit statevector

    nm = NoiseModel()
    err1q = depolarizing_error(p1, 1)
    err2q = depolarizing_error(p2, 2)
    # Apply to all instances of these gate types
    nm.add_all_qubit_quantum_error(err1q, ['h', 'rz', 'x', 'id', 'sx'])
    nm.add_all_qubit_quantum_error(err2q, ['cx', 'cz'])
    # statevector method = shot-based Monte Carlo noise (like FakeMarrakesh); avoids density matrix
    return AerSimulator(method="statevector", noise_model=nm)


def _load_ckpt():
    if os.path.exists(CKPT_PATH):
        try:
            return json.load(open(CKPT_PATH))
        except Exception:
            return {}
    return {}


def _save_ckpt(c):
    os.makedirs(os.path.dirname(CKPT_PATH), exist_ok=True)
    tmp = CKPT_PATH + ".tmp"
    json.dump(c, open(tmp, "w"), indent=2)
    os.replace(tmp, CKPT_PATH)


def run_cell(seed, noise_label, sim, edges, max_cut, n_qubits):
    """Run one granular escalation cell (same protocol as Exp64/Exp66)."""
    np.random.seed(seed)
    t0 = time.time()

    # Build circuits (transpiled for noiseless AerSimulator basis)
    # Build fresh for each noise level (same circuit, different sim)
    from qiskit_aer import AerSimulator as _AerSim
    ref_sim = _AerSim()  # use noiseless for circuit building
    tqc5, gp5, bp5 = build_for_p(5, ref_sim, n_qubits, edges)
    tqc3, gp3, bp3 = build_for_p(3, ref_sim, n_qubits, edges)

    # Cold start (p=5)
    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, SHOTS, MAXITER)

    # K=3 p=3 anchor runs
    anchors = []
    for j in range(K_MAX):
        x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
        r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                    n_qubits, SHOTS, MAXITER)
        anchors.append((float(r3), np.asarray(x3, dtype=float)))

    # Best-first ordering
    bestfirst_idx = []
    cur = 0
    for j in range(K_MAX):
        if anchors[j][0] > anchors[cur][0]:
            cur = j
        bestfirst_idx.append(cur)

    # Warm-start (p=5) from each anchor (cache duplicates)
    warm_cache = {}
    r_warm_byk = []
    for j in range(K_MAX):
        idx = bestfirst_idx[j]
        if idx not in warm_cache:
            x0w = pad_params(anchors[idx][1], 3, 5)
            rw, _ = optimize_cobyla_ws(x0w, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                       n_qubits, SHOTS, MAXITER)
            warm_cache[idx] = float(rw)
        r_warm_byk.append(warm_cache[idx])

    lift_byk = [rw - r_cold for rw in r_warm_byk]
    elapsed = time.time() - t0

    rec = {
        "seed": seed,
        "noise_label": noise_label,
        "k_max": K_MAX,
        "r_cold_p5": float(r_cold),
        "r_p3_anchors": [a[0] for a in anchors],
        "bestfirst_idx": bestfirst_idx,
        "r_warm_byk": r_warm_byk,
        "lift_byk": lift_byk,
        "n_warm_opts": len(warm_cache),
        "elapsed_s": elapsed,
    }

    print(f"  [{noise_label}] seed={seed} cold={r_cold:.4f} "
          f"anchors=[{','.join(f'{a[0]:.3f}' for a in anchors)}] "
          f"warm=[{','.join(f'{w:.3f}' for w in r_warm_byk)}] "
          f"lift=[{','.join(f'{l:+.3f}' for l in lift_byk)}] "
          f"({elapsed:.0f}s)", flush=True)
    return rec


def _policy_lift(rec, tau, granular):
    r3 = rec["r_p3_anchors"]
    lift = rec["lift_byk"]
    k_max = len(r3)
    if granular:
        a = -1e18
        for j in range(k_max):
            a = max(a, r3[j])
            if a >= tau:
                return j + 1, lift[j]
        return k_max, lift[k_max - 1]
    else:
        if r3[0] >= tau:
            return 1, lift[0]
        return k_max, lift[k_max - 1]


def _pooled_loo(recs, granular):
    r0 = [r["r_p3_anchors"][0] for r in recs]
    num = den = 0.0
    ks = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        k_used, lift = _policy_lift(rec, tau_i, granular)
        fixed = rec["lift_byk"][-1]
        num += lift
        den += fixed
        ks.append(k_used)
    capture = num / den if den != 0 else float("nan")
    return capture, float(np.mean(ks)), ks


def _bootstrap_ci(recs, granular, draws=2000, seed=67):
    r0 = [r["r_p3_anchors"][0] for r in recs]
    pairs = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        _, lift = _policy_lift(rec, tau_i, granular)
        pairs.append((lift, rec["lift_byk"][-1]))
    n = len(pairs)
    rng = np.random.RandomState(seed)
    caps = []
    for _ in range(draws):
        idx = rng.randint(0, n, n)
        num = sum(pairs[k][0] for k in idx)
        den = sum(pairs[k][1] for k in idx)
        if den != 0:
            caps.append(num / den)
    if not caps:
        return None, None
    return float(np.percentile(caps, 2.5)), float(np.percentile(caps, 97.5))


def summarize_level(recs, noise_label, p1, p2):
    """Compute summary metrics for one noise level."""
    cap_g, mk_g, ks_g = _pooled_loo(recs, granular=True)
    cap_b, mk_b, ks_b = _pooled_loo(recs, granular=False)
    ci_g_lo, ci_g_hi = _bootstrap_ci(recs, granular=True)
    eff_g = cap_g / mk_g if mk_g else float("nan")
    eff_b = cap_b / mk_b if mk_b else float("nan")
    h3_pass = bool(eff_g > eff_b)
    return {
        "noise_label": noise_label,
        "p1_1qubit": p1,
        "p2_2qubit": p2,
        "n_cells": len(recs),
        "capk_granular": float(eff_g),
        "capk_binary": float(eff_b),
        "loo_capture_granular": float(cap_g),
        "mean_k_granular": float(mk_g),
        "bootstrap_ci_95": [ci_g_lo, ci_g_hi],
        "h3_granular_pareto_efficient": h3_pass,
    }


def grade_all(level_summaries):
    """Grade H1-H4 across all levels (including noiseless from Exp66)."""
    print("\n" + "=" * 70)
    print("GRADING (Exp67 pre-registered hypotheses)")
    print("=" * 70)

    # Extract capk_granular by noise level index
    # Level 0 = noiseless (Exp66 reference), Levels 1-4 = this experiment
    print(f"\nNoiseless (Exp66 ref): capk_granular = {EXP66_NOISELESS_CAPK:.4f}")
    for s in level_summaries:
        print(f"{s['noise_label']:12s} (p1={s['p1_1qubit']:.4f}, p2={s['p2_2qubit']:.3f}): "
              f"capk_granular = {s['capk_granular']:.4f} | "
              f"capk_binary = {s['capk_binary']:.4f} | "
              f"H3: {'PASS' if s['h3_granular_pareto_efficient'] else 'FAIL'}")

    # H1: Level 3 ("high") depolarizing capk < noiseless (0.5236)
    high = next((s for s in level_summaries if s['noise_label'] == 'high'), None)
    if high:
        h1 = bool(high['capk_granular'] < EXP66_NOISELESS_CAPK)
        print(f"\nH1 (depolarizing-high < noiseless {EXP66_NOISELESS_CAPK:.4f}): "
              f"{'VALIDATE' if h1 else 'INVALIDATE'} "
              f"(depolarizing-high capk = {high['capk_granular']:.4f})")
    else:
        h1 = None
        print("\nH1: Not gradeable (level 3 'high' not found)")

    # H2: Spearman correlation between noise level index and capk < -0.5
    labels = [s['noise_label'] for s in level_summaries]
    capks = [s['capk_granular'] for s in level_summaries]
    level_idx = list(range(1, len(level_summaries) + 1))
    if len(level_idx) >= 3:
        rho, pval = spearmanr(level_idx, capks)
        h2 = bool(rho < -0.5)
        print(f"\nH2 (Spearman rho(noise_level, capk) < -0.5): "
              f"{'VALIDATE' if h2 else 'INVALIDATE'} (rho={rho:.3f}, p={pval:.3f})")
    else:
        h2 = None
        rho = None
        print("\nH2: Not gradeable (< 3 levels)")

    # H3: granular > binary at all levels
    h3_all = all(s['h3_granular_pareto_efficient'] for s in level_summaries)
    print(f"\nH3 (Pareto-efficiency at ALL noise levels): "
          f"{'VALIDATE' if h3_all else 'INVALIDATE'}")

    # H4: range of capk > 0.05
    if capks:
        capk_range = max(capks) - min(capks)
        # Also include noiseless in range
        all_capks = [EXP66_NOISELESS_CAPK] + capks
        total_range = max(all_capks) - min(all_capks)
        h4 = bool(total_range > 0.05)
        print(f"\nH4 (range of capk > 0.05 across all levels): "
              f"{'VALIDATE' if h4 else 'INVALIDATE'} (range={total_range:.4f})")
    else:
        h4 = None
        total_range = None

    print("\n" + "=" * 70)
    return {"h1": h1, "h2": h2, "h3_all": h3_all, "h4": h4,
            "spearman_rho": float(rho) if rho is not None else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="2-cell fast check")
    ap.add_argument("--run",   action="store_true", help="full experiment")
    ap.add_argument("--level", type=int, default=None, help="run single noise level (1-4)")
    ap.add_argument("--grade", action="store_true", help="grade existing results only")
    args = ap.parse_args()

    if args.grade:
        if not os.path.exists(RESULTS_PATH):
            print("No results file found. Run experiment first.")
            sys.exit(1)
        data = json.load(open(RESULTS_PATH))
        level_summaries = data.get("level_summaries", [])
        grade_all(level_summaries)
        return

    if not (args.smoke or args.run or args.level is not None):
        print("Usage: --smoke | --run | --level N | --grade")
        sys.exit(1)

    edges = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)
    print(f"Graph: EDGES_20, {n_qubits} qubits, max_cut={max_cut}")

    seeds = [EDGES_SEEDS[0], EDGES_SEEDS[1]] if args.smoke else EDGES_SEEDS
    levels_to_run = NOISE_LEVELS
    if args.level is not None:
        idx = args.level - 1
        if 0 <= idx < len(NOISE_LEVELS):
            levels_to_run = [NOISE_LEVELS[idx]]
        else:
            print(f"Level must be 1-{len(NOISE_LEVELS)}")
            sys.exit(1)

    ckpt = _load_ckpt()
    all_cells = ckpt.get("cells", [])
    completed_keys = {(c["seed"], c["noise_label"]) for c in all_cells}

    t_total = time.time()
    for label, p1, p2 in levels_to_run:
        print(f"\n=== Noise Level: {label} (p1={p1:.4f}, p2={p2:.3f}) ===")
        sim = build_depolarizing_sim(p1, p2)

        for seed in seeds:
            key = (seed, label)
            if key in completed_keys:
                print(f"  [{label}] seed={seed} SKIPPED (cached)")
                continue

            try:
                rec = run_cell(seed, label, sim, edges, max_cut, n_qubits)
                all_cells.append(rec)
                completed_keys.add(key)
                _save_ckpt({"cells": all_cells})
            except Exception as e:
                print(f"  [{label}] seed={seed} ERROR: {e}", file=sys.stderr)

    print(f"\nTotal wall-time: {time.time() - t_total:.0f}s")

    # Summarize by noise level
    level_summaries = []
    for label, p1, p2 in NOISE_LEVELS:
        recs = [c for c in all_cells if c["noise_label"] == label]
        if recs:
            s = summarize_level(recs, label, p1, p2)
            level_summaries.append(s)

    verdicts = grade_all(level_summaries)

    output = {
        "experiment": "Exp67",
        "title": "Depolarizing noise dose-response for warm-start granular escalation",
        "author": "Ember C3982",
        "preregistration": "experiments/exp67-depolarizing-dose-response-preregistration.md",
        "noiseless_reference": {
            "source": "Exp66 Part A (C3981)",
            "capk_granular": EXP66_NOISELESS_CAPK,
            "capk_binary": None,   # Exp66 binary reference not loaded here
        },
        "fakemarrakesh_reference": {
            "source": "Exp64 (Finding 41)",
            "capk_granular": EXP64_FAKEMARRAKESH_CAPK,
        },
        "level_summaries": level_summaries,
        "verdicts": verdicts,
        "n_seeds": len(seeds),
        "n_levels": len(level_summaries),
        "total_cells": len(all_cells),
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = RESULTS_PATH + ".tmp"
    json.dump(output, open(tmp, "w"), indent=2)
    os.replace(tmp, RESULTS_PATH)
    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
