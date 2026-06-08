#!/usr/bin/env python3
"""
Exp49 Continuation: Seeds 49, 50, 51 at p=5
Elder C5733 | 2026-06-08

The original run_exp49_seed_locked_escape.py timed out (14400s limit) after completing:
- All 10 p=3 seeds (100% escape, 683s/seed)
- p=5 seeds 42-48 (7/10, 1037-1040s/seed)

Results to date:
  p=3: 42=0.6846, 43=0.6538, 44=0.6755, 45=0.6507, 46=0.6839, 47=0.6830,
       48=0.6875, 49=0.6690, 50=0.6908, 51=0.6599 (all ESCAPED)
  p=5: 42=0.5980[T], 43=0.6391[T], 44=0.6442[E], 45=0.5928[T], 46=0.6376[T],
       47=0.6345[T], 48=0.6553[E], 49=?, 50=?, 51=?

Interim Pearson r (7 seeds): 0.374 (H3 territory, 0.25-0.60)

This script runs ONLY seeds 49, 50, 51 at p=5, then combines with prior results
to compute the final verdict.
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
ESCAPE_THRESHOLD = 0.640
P_DEPTH = 5  # only running p=5 for seeds 49-51
REMAINING_SEEDS = [49, 50, 51]

# All 10 p=3 results (known from prior run)
P3_RESULTS = {
    42: 0.6846, 43: 0.6538, 44: 0.6755, 45: 0.6507, 46: 0.6839,
    47: 0.6830, 48: 0.6875, 49: 0.6690, 50: 0.6908, 51: 0.6599
}

# p=5 results already computed (seeds 42-48)
P5_PRIOR = {
    42: 0.5980, 43: 0.6391, 44: 0.6442, 45: 0.5928, 46: 0.6376,
    47: 0.6345, 48: 0.6553
}


def run_single(sim, max_cut, p, seed):
    template, gpar, bpar = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
    np.random.seed(seed)
    x0_preview = np.random.uniform(0, 2 * np.pi, 2 * p)
    np.random.seed(seed)
    ratio, _ = optimize_with_cached_circuit(
        tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
        N_QUBITS_20, SHOTS, n_restarts=1, max_iter=MAX_ITER,
    )
    return float(ratio)


if __name__ == '__main__':
    print("Exp49 Continuation: Seeds 49, 50, 51 at p=5", flush=True)
    print(f"Prior results: 7/10 p=5 seeds complete (see script docstring)", flush=True)
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)

    t0 = time.time()
    new_results = {}

    for i, seed in enumerate(REMAINING_SEEDS):
        ratio = run_single(sim, max_cut, P_DEPTH, seed)
        new_results[seed] = ratio
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        elapsed = int(time.time() - t0)
        print(f"  [{i+1:02d}/{len(REMAINING_SEEDS):02d}] p=5 seed={seed} ... {ratio:.4f} [{status}]  elapsed={elapsed}s", flush=True)

    # Combine with prior results
    all_p5 = {**P5_PRIOR, **new_results}
    all_seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]

    p3_vals = [P3_RESULTS[s] for s in all_seeds]
    p5_vals = [all_p5[s] for s in all_seeds]

    n_esc_p3 = sum(1 for v in p3_vals if v >= ESCAPE_THRESHOLD)
    n_esc_p5 = sum(1 for v in p5_vals if v >= ESCAPE_THRESHOLD)

    r_pearson, p_value = stats.pearsonr(p3_vals, p5_vals)
    consistent = sum(1 for s in all_seeds if (P3_RESULTS[s] >= ESCAPE_THRESHOLD) == (all_p5[s] >= ESCAPE_THRESHOLD))

    print(f"\n{'='*60}", flush=True)
    print("EXP49 FINAL RESULTS", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"p=3 escape rate: {n_esc_p3}/10 = 100%", flush=True)
    print(f"p=5 escape rate: {n_esc_p5}/10 = {n_esc_p5*10}%", flush=True)
    print(f"Pearson r: {r_pearson:.4f} (p={p_value:.4f})", flush=True)
    print(f"Consistency: {consistent}/10 same outcome", flush=True)

    for s in all_seeds:
        s3 = "E" if P3_RESULTS[s] >= ESCAPE_THRESHOLD else "T"
        s5 = "E" if all_p5[s] >= ESCAPE_THRESHOLD else "T"
        consistent_s = "SAME" if (P3_RESULTS[s] >= ESCAPE_THRESHOLD) == (all_p5[s] >= ESCAPE_THRESHOLD) else "DIFF"
        print(f"  Seed {s}: p3={P3_RESULTS[s]:.4f}[{s3}] → p5={all_p5[s]:.4f}[{s5}] | {consistent_s}", flush=True)

    if r_pearson > 0.60:
        verdict = "H1 CONFIRMED (seed-locked)"
        interpretation = "Escape is INITIALIZATION-DETERMINED."
    elif r_pearson < 0.25:
        verdict = "H2 CONFIRMED (stochastic)"
        interpretation = "Escape is STOCHASTIC. No seed correlation across depths."
    else:
        verdict = "H3 SUPPORTED (partial)"
        interpretation = f"Mixed mechanism. r={r_pearson:.3f} in partial range."

    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"INTERPRETATION: {interpretation}", flush=True)

    # Save combined results
    output = {
        "experiment": "exp49_seed_locked_escape",
        "author": "Elder C5733 (continuation of C5727)",
        "date": "2026-06-08",
        "note": "Original run timed out at seed 49. This continuation adds seeds 49-51.",
        "settings": {
            "p_values": [3, 5], "seeds": all_seeds,
            "escape_threshold": ESCAPE_THRESHOLD, "shots": SHOTS,
            "max_iter": MAX_ITER, "n_qubits": N_QUBITS_20, "n_edges": len(EDGES_20),
        },
        "results": {
            "3": {str(s): P3_RESULTS[s] for s in all_seeds},
            "5": {str(s): all_p5[s] for s in all_seeds},
        },
        "analysis": {
            "pearson_r": float(r_pearson), "pearson_p": float(p_value),
            "consistency_rate": float(consistent / 10),
            "consistent_count": consistent, "n_seeds": 10,
        },
        "verdict": verdict,
        "interpretation": interpretation,
        "runtime_seconds_continuation": round(time.time() - t0, 1),
    }

    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'experiments', 'exp49_results.json')
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {outfile}", flush=True)
