#!/usr/bin/env python3
"""
Exp67 v2 (8-qubit redesign): Depolarizing noise dose-response for warm-start granular escalation.
Ember C3983 redesign — feasible in-session (n=8 vs n=20 original which was 23s/circuit).

REDESIGN RATIONALE:
  Exp67 original (C3982 pre-reg) used EDGES_20 (n=20), which required 23s/circuit under noisy
  simulation (~180h for full protocol). Redesign uses EDGES_8 (n=8, 12 edges, ring+cross):
  - Noiseless: 0.017s/circuit → MAXITER=20 per call → ~0.34s/COBYLA call
  - Noisy:     0.037s/circuit → ~0.74s/COBYLA call
  - Full 32-cell experiment (4 noise levels × 8 seeds): ~3 minutes
  - Level 0 (noiseless) run explicitly within this experiment (self-contained, same graph)

SCIENTIFIC QUESTION (unchanged from Exp67 original):
  Finding 42 (Exp66, C3981): noiseless capk=0.5236 < FakeMarrakesh capk=0.5625 (noise HELPS).
  Three explanations: (A) non-unital amplitude damping, (B) noise-assisted escape, (C) stat noise.

  H1: Does unital (depolarizing) noise also anti-contract (capk > noiseless)?
  If H1 VALIDATED: anti-contraction persists in unital case -> rules out (A), supports (B)/(C).
  If H1 INVALIDATED (depolarizing contracts): (A) non-unital mechanism is supported.

  NOTE: n=8 vs n=20 SCOPE BOUNDARY. Absolute capk values will differ from Exp64/66 (EDGES_20).
  The within-experiment comparison (noiseless vs depolarizing on SAME n=8 graph) is the valid test.
  We do NOT compare n=8 capk to n=20 Exp64/66 values; we only compare directions.

USAGE:
  python3 run_exp67_v2_8qubit.py --smoke    # 1 seed, 2 levels: ~20s feasibility check
  python3 run_exp67_v2_8qubit.py --run      # full 5 levels x 8 seeds = 40 cells: ~4 min
  python3 run_exp67_v2_8qubit.py --grade    # grade existing results only
  python3 run_exp67_v2_8qubit.py --level N  # single noise level (0=noiseless, 1-4=depolarizing)
"""
import sys, os, json, time, argparse
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import brute_force_max_cut
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from run_exp61_bestofk_anchor import build_for_p

# EDGES_8: 8-node ring+cross graph (from Exp39/Exp41). 12 edges, moderate density.
# Same graph used in Exp39 (budget sweep), Exp41 (16-node scaling comparison).
EDGES_8 = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,3),(1,5),(2,6),(4,7)]
N_QUBITS_8 = 8

# Seeds: 0-7 for N=8 independent replicates (different random initializations)
SEEDS = list(range(8))

K_MAX   = 3
SHOTS   = 256
MAXITER = 20
P_TARGET = 5   # warm-start target (same as Exp64/66)
P_ANCHOR = 3   # anchor p (same as Exp64/66)

# Noise levels: Level 0 = noiseless baseline (run in-experiment, self-contained)
# Levels 1-4 = parameterized depolarizing noise
# FakeMarrakesh-equiv reference: CZ gate error ~0.002; SX gate error ~0.0003.
NOISE_LEVELS = [
    ("noiseless", 0.0,    0.0  ),   # Level 0 — in-experiment baseline
    ("low",       0.0002, 0.002),   # Level 1 — ~1/5 FakeMarrakesh-equiv
    ("medium",    0.0005, 0.005),   # Level 2 — ~1/2 FakeMarrakesh-equiv
    ("high",      0.001,  0.010),   # Level 3 — ~FakeMarrakesh-equiv
    ("very-high", 0.003,  0.030),   # Level 4 — ~3x FakeMarrakesh-equiv
]

RESULTS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
CKPT_PATH    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                             "exp67_v2_8qubit_checkpoint.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp67_v2_8qubit_results.json")


def build_sim(p1, p2):
    """Build AerSimulator (noiseless or depolarizing at given rates)."""
    from qiskit_aer import AerSimulator
    if p1 == 0.0 and p2 == 0.0:
        return AerSimulator(method="statevector")
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['h', 'rz', 'x', 'id', 'sx'])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cx', 'cz'])
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
    """Run one warm-start granular escalation cell."""
    np.random.seed(seed)
    t0 = time.time()

    # Build circuits using a noiseless AerSimulator for transpilation baseline
    from qiskit_aer import AerSimulator as _AS
    ref_sim = _AS()
    tqc_target, gp_target, bp_target = build_for_p(P_TARGET, ref_sim, n_qubits, edges)
    tqc_anchor, gp_anchor, bp_anchor = build_for_p(P_ANCHOR, ref_sim, n_qubits, edges)

    # Cold start (p=P_TARGET)
    x0_cold = np.random.uniform(0, 2 * np.pi, 2 * P_TARGET)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc_target, gp_target, bp_target,
                                   P_TARGET, sim, edges, max_cut, n_qubits, SHOTS, MAXITER)

    # K anchor runs (p=P_ANCHOR)
    anchors = []
    for j in range(K_MAX):
        x0_a = np.random.uniform(0, 2 * np.pi, 2 * P_ANCHOR)
        r_a, x_a = optimize_cobyla_ws(x0_a, tqc_anchor, gp_anchor, bp_anchor,
                                      P_ANCHOR, sim, edges, max_cut, n_qubits, SHOTS, MAXITER)
        anchors.append((float(r_a), np.asarray(x_a, dtype=float)))

    # Best-first ordering
    bestfirst_idx = []
    cur = 0
    for j in range(K_MAX):
        if anchors[j][0] > anchors[cur][0]:
            cur = j
        bestfirst_idx.append(cur)

    # Warm-start from each anchor
    warm_cache = {}
    r_warm_byk = []
    for j in range(K_MAX):
        idx = bestfirst_idx[j]
        if idx not in warm_cache:
            x0_w = pad_params(anchors[idx][1], P_ANCHOR, P_TARGET)
            rw, _ = optimize_cobyla_ws(x0_w, tqc_target, gp_target, bp_target,
                                       P_TARGET, sim, edges, max_cut, n_qubits, SHOTS, MAXITER)
            warm_cache[idx] = float(rw)
        r_warm_byk.append(warm_cache[idx])

    lift_byk = [rw - r_cold for rw in r_warm_byk]
    elapsed = time.time() - t0

    rec = {
        "seed": seed,
        "noise_label": noise_label,
        "k_max": K_MAX,
        "r_cold": float(r_cold),
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
          f"({elapsed:.1f}s)", flush=True)
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
    return (float(np.percentile(caps, 2.5)), float(np.percentile(caps, 97.5))) if caps else (None, None)


def summarize_level(recs, noise_label, p1, p2):
    cap_g, mk_g, _ = _pooled_loo(recs, granular=True)
    cap_b, mk_b, _ = _pooled_loo(recs, granular=False)
    ci_lo, ci_hi = _bootstrap_ci(recs, granular=True)
    eff_g = cap_g / mk_g if mk_g else float("nan")
    eff_b = cap_b / mk_b if mk_b else float("nan")
    return {
        "noise_label": noise_label,
        "p1_1qubit": p1,
        "p2_2qubit": p2,
        "n_cells": len(recs),
        "capk_granular": float(eff_g),
        "capk_binary": float(eff_b),
        "loo_capture_granular": float(cap_g),
        "mean_k_granular": float(mk_g),
        "bootstrap_ci_95": [ci_lo, ci_hi],
        "h3_granular_pareto_efficient": bool(eff_g > eff_b),
    }


def grade_all(level_summaries):
    """Grade H1-H4 using within-experiment noiseless vs depolarizing comparison."""
    print("\n" + "=" * 70)
    print("GRADING — Exp67 v2 (n=8 redesign, Ember C3983)")
    print("=" * 70)
    print("\nH1 tests: does DEPOLARIZING (unital) noise DECREASE capk vs noiseless?")
    print("H1 VALIDATE: unital noise contracts (supports non-unital origin of Finding 42)")
    print("H1 INVALIDATE: unital noise also anti-contracts (explains away non-unital as cause)")

    # Noiseless is Level 0 in this experiment
    noiseless = next((s for s in level_summaries if s["noise_label"] == "noiseless"), None)
    noiseless_capk = noiseless["capk_granular"] if noiseless else None
    print(f"\nLevel 0 noiseless: capk_granular = {noiseless_capk:.4f}" if noiseless_capk else "\nLevel 0 (noiseless): not available")

    for s in level_summaries:
        if s["noise_label"] == "noiseless":
            continue
        delta = s["capk_granular"] - noiseless_capk if noiseless_capk else None
        delta_str = f"  Δ={delta:+.4f} vs noiseless" if delta is not None else ""
        print(f"  {s['noise_label']:12s} p1={s['p1_1qubit']:.4f} p2={s['p2_2qubit']:.3f}: "
              f"capk_granular={s['capk_granular']:.4f} | binary={s['capk_binary']:.4f} | "
              f"H3={'PASS' if s['h3_granular_pareto_efficient'] else 'FAIL'}{delta_str}")

    # H1: "high" depolarizing capk < noiseless (contraction)
    high = next((s for s in level_summaries if s["noise_label"] == "high"), None)
    if high and noiseless_capk is not None:
        h1 = bool(high["capk_granular"] < noiseless_capk)
        print(f"\nH1 (depolarizing-high < noiseless): {'VALIDATE' if h1 else 'INVALIDATE'} "
              f"({high['capk_granular']:.4f} {'<' if h1 else '>='} {noiseless_capk:.4f})")
    else:
        h1 = None
        print("\nH1: Not gradeable")

    # H2: Spearman rho(noise_level_index, capk) < -0.5 (monotone decrease with noise)
    noisy_levels = [s for s in level_summaries if s["noise_label"] != "noiseless"]
    if len(noisy_levels) >= 3:
        capks_noisy = [s["capk_granular"] for s in noisy_levels]
        level_idx = list(range(1, len(noisy_levels) + 1))
        rho, pval = spearmanr(level_idx, capks_noisy)
        h2 = bool(rho < -0.5)
        print(f"\nH2 (Spearman rho(noise_level, capk) < -0.5): {'VALIDATE' if h2 else 'INVALIDATE'} "
              f"(rho={rho:.3f}, p={pval:.3f})")
    else:
        h2, rho = None, None
        print("\nH2: Not gradeable")

    # H3: granular > binary at ALL levels
    h3_all = all(s["h3_granular_pareto_efficient"] for s in level_summaries)
    print(f"\nH3 (Pareto-efficiency at ALL noise levels): {'VALIDATE' if h3_all else 'INVALIDATE'}")

    # H4: range of capk > 0.05 across all levels
    all_capks = [s["capk_granular"] for s in level_summaries]
    capk_range = max(all_capks) - min(all_capks) if all_capks else 0.0
    h4 = bool(capk_range > 0.05)
    print(f"\nH4 (capk range > 0.05 across all levels): {'VALIDATE' if h4 else 'INVALIDATE'} "
          f"(range={capk_range:.4f})")
    print("\n" + "=" * 70)

    return {
        "h1": h1, "h2": h2, "h3_all": h3_all, "h4": h4,
        "spearman_rho": float(rho) if rho is not None else None,
        "noiseless_capk": float(noiseless_capk) if noiseless_capk is not None else None,
    }


def main():
    ap = argparse.ArgumentParser(description="Exp67 v2 — 8-qubit depolarizing dose-response")
    ap.add_argument("--smoke", action="store_true", help="1 seed x 2 noise levels (~30s check)")
    ap.add_argument("--run",   action="store_true", help="full run: 5 levels x 8 seeds (~4 min)")
    ap.add_argument("--grade", action="store_true", help="grade existing results only")
    ap.add_argument("--level", type=int, default=None,
                    help="run single level (0=noiseless, 1=low, 2=med, 3=high, 4=very-high)")
    args = ap.parse_args()

    if args.grade:
        if not os.path.exists(RESULTS_PATH):
            print("No results file. Run experiment first.")
            sys.exit(1)
        data = json.load(open(RESULTS_PATH))
        grade_all(data.get("level_summaries", []))
        return

    if not (args.smoke or args.run or args.level is not None):
        print(__doc__)
        sys.exit(0)

    max_cut = brute_force_max_cut(N_QUBITS_8, EDGES_8)
    print(f"Graph: EDGES_8, {N_QUBITS_8} qubits, {len(EDGES_8)} edges, max_cut={max_cut}")

    if args.smoke:
        seeds_to_run = [SEEDS[0]]
        levels_to_run = [NOISE_LEVELS[0], NOISE_LEVELS[3]]  # noiseless + high
    elif args.level is not None:
        if 0 <= args.level < len(NOISE_LEVELS):
            levels_to_run = [NOISE_LEVELS[args.level]]
        else:
            print(f"Level must be 0-{len(NOISE_LEVELS)-1}")
            sys.exit(1)
        seeds_to_run = SEEDS
    else:
        seeds_to_run = SEEDS
        levels_to_run = NOISE_LEVELS

    ckpt = _load_ckpt()
    all_cells = ckpt.get("cells", [])
    done_keys = {(c["seed"], c["noise_label"]) for c in all_cells}

    t_total = time.time()
    for label, p1, p2 in levels_to_run:
        print(f"\n=== Level: {label} (p1={p1:.4f}, p2={p2:.3f}) ===")
        sim = build_sim(p1, p2)
        for seed in seeds_to_run:
            if (seed, label) in done_keys:
                print(f"  [{label}] seed={seed} CACHED")
                continue
            try:
                rec = run_cell(seed, label, sim, EDGES_8, max_cut, N_QUBITS_8)
                all_cells.append(rec)
                done_keys.add((seed, label))
                _save_ckpt({"cells": all_cells})
            except Exception as e:
                print(f"  [{label}] seed={seed} ERROR: {e}", file=sys.stderr)

    elapsed_total = time.time() - t_total
    print(f"\nTotal wall-time: {elapsed_total:.0f}s")

    level_summaries = []
    for label, p1, p2 in NOISE_LEVELS:
        recs = [c for c in all_cells if c["noise_label"] == label]
        if recs:
            level_summaries.append(summarize_level(recs, label, p1, p2))

    verdicts = grade_all(level_summaries)

    output = {
        "experiment": "Exp67_v2_8qubit",
        "title": "Depolarizing dose-response on EDGES_8 (n=8, redesign from n=20 original)",
        "author": "Ember C3983",
        "redesign_note": "Original Exp67 (C3982 pre-reg) used n=20 EDGES_20 (23s/circuit infeasible). "
                         "v2 uses n=8 EDGES_8 (0.037s/circuit, full run ~4min). "
                         "Scientific question unchanged. Scope boundary: n=8 absolute capk != n=20.",
        "graph": {"n_qubits": N_QUBITS_8, "edges": EDGES_8, "max_cut": brute_force_max_cut(N_QUBITS_8, EDGES_8)},
        "level_summaries": level_summaries,
        "verdicts": verdicts,
        "n_seeds": len(seeds_to_run),
        "n_levels": len(level_summaries),
        "total_cells": len(all_cells),
        "total_wall_time_s": elapsed_total,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = RESULTS_PATH + ".tmp"
    json.dump(output, open(tmp, "w"), indent=2)
    os.replace(tmp, RESULTS_PATH)
    print(f"\nResults: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
