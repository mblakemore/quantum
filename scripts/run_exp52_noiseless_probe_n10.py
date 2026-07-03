#!/usr/bin/env python3
"""
Exp52 NOISELESS PROBE — FULL N=10 rerun | Ember C4079 | resolves pred_c3963_001
Extends run_exp52_noiseless_probe.py (N=5, seeds 42-46) to the FULL 10 seeds 42-51.

pred_c3963_001 (conf 0.57): Exp52 noiseless bias-floor result is NOT a COBYLA/N=5
artifact — a fuller noiseless rerun (full 10 seeds 42-51) at >=1024sh reaches escape
rate >=0.90 (near-unity), staying clearly ABOVE the noisy 90% plateau at the SAME
shot budget; bias-variance crossover holds (noiseless ~= noisy at 256sh).
  Branch A (CONFIRMED): noiseless 1024sh+ >= 0.90 AND 256sh ~= noisy 0.60
  Branch B (WEAKENED):  noiseless 1024sh drops toward noisy 0.90 at N=10
                        (the N=5 100% was small-sample luck)

Identical harness to the N=5 probe except SEEDS = 42..51 and a distinct output file
(results/exp52_noiseless_probe_n10.json) so the N=5 history is preserved.
NO QPU — local noiseless AerSimulator statevector sampling.
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize  # noqa: F401 (parity with reused modules)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,  # noqa: F401
)
from run_exp51_spsa_vs_cobyla import optimize_cobyla
from qiskit import transpile
from qiskit_aer import AerSimulator

ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))  # FULL 42-51 (N=10) — the pred_c3963_001 test condition
OPT_LEVEL = 1
SHOT_LEVELS = [256, 1024, 2048]
MAX_ITER = 30

# Noisy reference (same seed family, Exp51/Exp52) for direct comparison
NOISY_REF = {256: 0.60, 1024: 0.90, 2048: 0.90}


def run_noiseless_arm(shots, seeds):
    print(f"\n{'='*60}\nNOISELESS COBYLA N=10 | shots={shots} | seeds={seeds}\n{'='*60}")
    sim = AerSimulator()  # NO noise_model = the whole point
    p = 3
    edges = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)
    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    transpiled_qc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)

    results, escaped_count = [], 0
    for seed in seeds:
        np.random.seed(seed)
        t0 = time.time()
        ratio = optimize_cobyla(
            transpiled_qc, gamma_params, beta_params, p,
            sim, edges, max_cut, n_qubits, shots, MAX_ITER
        )
        escaped = ratio > ESCAPE_THRESHOLD
        escaped_count += int(escaped)
        elapsed = time.time() - t0
        print(f"  seed={seed}: ratio={ratio:.4f} {'OK ESCAPED' if escaped else 'xx trapped'} ({elapsed:.1f}s)")
        results.append({"seed": seed, "ratio": float(ratio), "escaped": bool(escaped), "elapsed_s": float(elapsed)})
    rate = escaped_count / len(seeds)
    print(f"\n  NOISELESS {shots}sh: {escaped_count}/{len(seeds)} = {rate:.2f}  (noisy ref {NOISY_REF.get(shots,'?')})")
    return results, escaped_count, rate


def main():
    print("=" * 70)
    print("Exp52 NOISELESS PROBE FULL N=10 | Ember C4079 | resolves pred_c3963_001")
    print(f"Seeds {SEEDS} | shots {SHOT_LEVELS} | NO noise model | local AerSimulator")
    print("=" * 70)
    out = {"experiment": "exp52_noiseless_probe_n10", "cycle": 4079, "seeds": SEEDS,
           "shot_levels": SHOT_LEVELS, "escape_threshold": ESCAPE_THRESHOLD,
           "noisy_reference": NOISY_REF, "n5_reference": {256: 0.60, 1024: 1.00, 2048: 1.00},
           "arms": {}}
    for shots in SHOT_LEVELS:
        res, esc, rate = run_noiseless_arm(shots, SEEDS)
        out["arms"][str(shots)] = {"results": res, "escaped": esc, "rate": rate,
                                   "noisy_ref_rate": NOISY_REF.get(shots)}
    r256, r1024, r2048 = (out["arms"][str(s)]["rate"] for s in SHOT_LEVELS)
    out["verdict"] = {
        "noiseless_curve": {256: r256, 1024: r1024, 2048: r2048},
        "ceiling_2048": r2048,
        "beats_noisy_plateau": r2048 > NOISY_REF[2048],
        "n10_1024_ge_090": r1024 >= 0.90,
        "crossover_256_matches_noisy": abs(r256 - NOISY_REF[256]) <= 0.20,
        "branch": "A_CONFIRMED" if (r1024 >= 0.90 and abs(r256 - NOISY_REF[256]) <= 0.20)
                  else "B_WEAKENED",
    }
    print("\n" + "=" * 70)
    print(f"VERDICT: noiseless N=10 curve 256={r256:.2f} 1024={r1024:.2f} 2048={r2048:.2f}")
    print(f"  1024sh >= 0.90 (pred A core):   {out['verdict']['n10_1024_ge_090']}")
    print(f"  256sh ~= noisy 0.60 crossover:  {out['verdict']['crossover_256_matches_noisy']}")
    print(f"  BRANCH: {out['verdict']['branch']}")
    print("=" * 70)
    os.makedirs("results", exist_ok=True)
    with open("results/exp52_noiseless_probe_n10.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Saved -> results/exp52_noiseless_probe_n10.json")


if __name__ == "__main__":
    main()
