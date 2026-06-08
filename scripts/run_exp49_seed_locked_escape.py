#!/usr/bin/env python3
"""
Exp49: Seed-Locked Escape Characterization
Elder C5727 | 2026-06-08

CONTEXT: Exp48 found escape probability DEPTH-INVARIANT at ~40% (approx 2/5 runs
escape to ~0.67 cluster, 3/5 trapped at ~0.595). Two explanations:
  (a) Initialization-determined: certain SEEDS reliably escape regardless of depth
  (b) Stochastic: escape is random, 40% base rate independent of seed

Ember C3641 synthesis recommended this "B-type test" to distinguish:
  B-type = fix seeds across p-depths → if same seeds always escape, escape is
           initialization-specific. If different seeds escape at different depths,
           escape is stochastic landscape property.

METHOD:
  - Run 10 fixed seeds × {p=3, p=5} for xbasis (extremes from Exp47/48)
  - 10 seeds × 2 depths = 20 runs total
  - Test correlation: does seed X escaping at p=3 predict escaping at p=5?

HYPOTHESES:
  H1 (seed-locked): Seeds that escape at p=3 also escape at p=5.
     Metric: Pearson r(p3_ratios, p5_ratios) > 0.60
     Support for: deterministic landscape, escape basin determined by initial params

  H2 (stochastic): No correlation between p3 and p5 outcomes per seed.
     Metric: Pearson r < 0.25
     Support for: landscape changes with depth, COBYLA path-dependent

  H3 (partial): Some seeds show seed-dependent behavior, others don't.
     Metric: 0.25 <= r < 0.60
     Support for: mixed mechanism

SECONDARY ANALYSIS:
  - What distinguishes escaped vs trapped seeds? Compare initial gamma/beta values.
  - Escape threshold: ratio >= 0.640 (midpoint of 0.595 trapped / 0.680 escaped clusters)

SIGNIFICANCE: If H1, then future strategy = run calibration seeds once at low p,
              reuse best seeds at high p (massive efficiency gain).
              If H2, no shortcut — must run multiple seeds at target depth.
"""
import sys, os, json, time
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    optimize_with_cached_circuit,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 256
MAX_ITER = 30
OPT_LEVEL = 1
P_VALUES = [3, 5]       # Exp47/48 extremes — maximize discriminability
N_SEEDS = 10            # 10 fixed seeds per depth
ESCAPE_THRESHOLD = 0.640  # midpoint between 0.595 (trapped) and 0.680 (escaped)

# Fixed seeds for reproducibility
SEEDS = list(range(42, 42 + N_SEEDS))   # [42, 43, 44, ..., 51]


def run_single_xbasis(sim, max_cut, p, seed):
    """Run one xbasis QAOA trial with fixed seed for COBYLA x0 initialization.

    Seed is set immediately before optimize_with_cached_circuit so the
    np.random.uniform call inside it produces deterministic x0.
    Returns (ratio, initial_x0) for secondary analysis.
    """
    template, gpar, bpar = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    tqc = transpile(template, sim, optimization_level=OPT_LEVEL)

    # Seed controls the x0 = np.random.uniform(0, 2*pi, 2*p) inside optimize
    np.random.seed(seed)
    # Capture what x0 will be (same rng state as inside optimize)
    x0_preview = np.random.uniform(0, 2 * np.pi, 2 * p)

    # Reset seed so optimize uses the SAME x0
    np.random.seed(seed)
    ratio, _ = optimize_with_cached_circuit(
        tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
        N_QUBITS_20, SHOTS, n_restarts=1, max_iter=MAX_ITER,
    )
    return float(ratio), x0_preview.tolist()


if __name__ == '__main__':
    print("Exp49: Seed-Locked Escape Characterization", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges", flush=True)
    print(f"Depths: {P_VALUES} | Seeds: {SEEDS}", flush=True)
    print(f"Escape threshold: {ESCAPE_THRESHOLD}", flush=True)
    print(f"Hypotheses:", flush=True)
    print("  H1 (seed-locked): r(p3, p5) > 0.60 — same seeds escape at both depths", flush=True)
    print("  H2 (stochastic):  r(p3, p5) < 0.25 — no seed correlation", flush=True)
    print("  H3 (partial):     0.25 <= r < 0.60", flush=True)
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)

    results = {}   # results[p][seed] = ratio
    init_params = {}  # init_params[p][seed] = initial_gamma_beta array

    total_runs = len(P_VALUES) * N_SEEDS
    run_num = 0
    t0 = time.time()

    for p in P_VALUES:
        results[p] = {}
        init_params[p] = {}
        for seed in SEEDS:
            run_num += 1
            print(f"  [{run_num:02d}/{total_runs}] p={p} seed={seed} ...", end=" ", flush=True)
            ratio, params = run_single_xbasis(sim, max_cut, p, seed)
            results[p][seed] = float(ratio)
            init_params[p][seed] = params
            escaped = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
            print(f"{ratio:.4f} [{escaped}]  elapsed={time.time()-t0:.0f}s", flush=True)

    print()
    print("=" * 60, flush=True)
    print("RESULTS MATRIX", flush=True)
    print("=" * 60, flush=True)
    print(f"{'Seed':>6} | {'p=3':>8} | {'p=5':>8} | {'p3 escaped':>12} | {'p5 escaped':>12} | {'Consistent':>10}", flush=True)
    print("-" * 70, flush=True)

    p3_ratios = []
    p5_ratios = []
    consistent_count = 0

    for seed in SEEDS:
        r3 = results[3][seed]
        r5 = results[5][seed]
        e3 = r3 >= ESCAPE_THRESHOLD
        e5 = r5 >= ESCAPE_THRESHOLD
        consistent = (e3 == e5)
        if consistent:
            consistent_count += 1
        p3_ratios.append(r3)
        p5_ratios.append(r5)
        print(f"  {seed:>4} | {r3:>8.4f} | {r5:>8.4f} | {'✓' if e3 else '✗':>12} | {'✓' if e5 else '✗':>12} | {'SAME' if consistent else 'DIFF':>10}", flush=True)

    print("-" * 70, flush=True)
    print()

    # Pearson correlation
    r_pearson, p_value = stats.pearsonr(p3_ratios, p5_ratios)
    # Escape consistency
    consistency_rate = consistent_count / N_SEEDS

    print("ANALYSIS", flush=True)
    print(f"  Pearson r(p3, p5):     {r_pearson:.4f}  (p={p_value:.4f})", flush=True)
    print(f"  Consistency rate:      {consistency_rate:.1%}  ({consistent_count}/{N_SEEDS} seeds same escape/trap)", flush=True)
    print()
    print(f"  p=3 escape count: {sum(1 for r in p3_ratios if r >= ESCAPE_THRESHOLD)}/{N_SEEDS}", flush=True)
    print(f"  p=5 escape count: {sum(1 for r in p5_ratios if r >= ESCAPE_THRESHOLD)}/{N_SEEDS}", flush=True)
    print()

    # Hypothesis verdict
    if r_pearson > 0.60:
        verdict = "H1 CONFIRMED (seed-locked)"
        interpretation = "Escape is INITIALIZATION-DETERMINED. Same seeds escape across depths."
    elif r_pearson < 0.25:
        verdict = "H2 CONFIRMED (stochastic)"
        interpretation = "Escape is STOCHASTIC. No seed correlation across depths."
    else:
        verdict = "H3 SUPPORTED (partial)"
        interpretation = f"Mixed mechanism. r={r_pearson:.3f} in partial range."

    print(f"HYPOTHESIS VERDICT: {verdict}", flush=True)
    print(f"INTERPRETATION: {interpretation}", flush=True)
    print()

    # Secondary: initial param analysis for escapers vs trappers at p=3
    escaper_seeds_p3 = [s for s in SEEDS if results[3][s] >= ESCAPE_THRESHOLD]
    trapper_seeds_p3 = [s for s in SEEDS if results[3][s] < ESCAPE_THRESHOLD]

    if escaper_seeds_p3 and trapper_seeds_p3:
        print("SECONDARY ANALYSIS: Initial params (p=3)", flush=True)
        for label, seed_group in [("Escapers", escaper_seeds_p3), ("Trappers", trapper_seeds_p3)]:
            params_group = [init_params[3][s] for s in seed_group]
            gamma_means = [np.mean(p[:3]) for p in params_group]
            beta_means = [np.mean(p[3:]) for p in params_group]
            print(f"  {label} (n={len(seed_group)}): seeds={seed_group}", flush=True)
            print(f"    mean initial gamma: {np.mean(gamma_means):.4f} ± {np.std(gamma_means):.4f}", flush=True)
            print(f"    mean initial beta:  {np.mean(beta_means):.4f} ± {np.std(beta_means):.4f}", flush=True)

    # Save results
    output = {
        "experiment": "exp49_seed_locked_escape",
        "author": "Elder C5727",
        "date": "2026-06-08",
        "settings": {
            "p_values": P_VALUES,
            "seeds": SEEDS,
            "escape_threshold": ESCAPE_THRESHOLD,
            "shots": SHOTS,
            "max_iter": MAX_ITER,
            "n_qubits": N_QUBITS_20,
            "n_edges": len(EDGES_20),
        },
        "results": {str(p): results[p] for p in P_VALUES},
        "analysis": {
            "pearson_r": float(r_pearson),
            "pearson_p": float(p_value),
            "consistency_rate": float(consistency_rate),
            "consistent_count": consistent_count,
            "n_seeds": N_SEEDS,
        },
        "verdict": verdict,
        "interpretation": interpretation,
        "runtime_seconds": round(time.time() - t0, 1),
    }

    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'experiments', 'exp49_results.json')
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {outfile}", flush=True)
    print(f"Total runtime: {output['runtime_seconds']}s", flush=True)
