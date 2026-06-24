#!/usr/bin/env python3
"""
Exp52 NOISELESS PROBE — Ember C3963 | tests pred_c3961
Pre-registration context: findings/27-exp52-cobyla-shot-budget-curve.md

pred_c3961 (conf 0.53): the noisy-Exp52 escape-rate PLATEAU (1024sh 9/10=90%,
2048sh saturated, H3) is a DECOHERENCE BIAS FLOOR — the ~10% non-escapers are
stuck at the FakeMarrakesh T2-channel fixed point (irreducible bias, c3740_002
contractivity). Remove the noise and only REDUCIBLE sampling variance Delta(H)/sqrt(N)
remains, so escape rate should CLIMB past the noisy 90% ceiling toward ~100% and
the 1024->2048 plateau should weaken/vanish.

DECISIVE READ (bounded, 5 seeds for in-cycle early-read):
  NOISELESS COBYLA at shots {256, 1024, 2048}, seeds 42-46 (subset of the noisy 42-51).
  Compare vs noisy reference (same seeds family): 256=60%, 1024=90%, 2048~90% (plateau).
  - If noiseless 1024/2048 -> 5/5 (100%) and >256 noiseless: bias-floor confirmed (pred A).
  - If noiseless still ceilings <100% at 2048: bias floor is NOT the whole story (pred B/C).

Mirrors run_exp52_shot_budget_curve.run_arm EXACTLY except sim has NO noise_model.
NO QPU — local AerSimulator statevector-sampling. Cluster-isolated from Elder Exp61-63.
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
SEEDS = list(range(42, 47))  # 42-46, subset of noisy 42-51
OPT_LEVEL = 1
SHOT_LEVELS = [256, 1024, 2048]
MAX_ITER = 30

# Noisy reference (same seed family, Exp52/Exp51) for direct comparison
NOISY_REF = {256: 0.60, 1024: 0.90, 2048: 0.90}


def run_noiseless_arm(shots, seeds):
    print(f"\n{'='*60}\nNOISELESS COBYLA | shots={shots} | seeds={seeds}\n{'='*60}")
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
        print(f"  seed={seed}: ratio={ratio:.4f} {'✓ ESCAPED' if escaped else '✗ trapped'} ({elapsed:.1f}s)")
        results.append({"seed": seed, "ratio": float(ratio), "escaped": bool(escaped), "elapsed_s": float(elapsed)})
    rate = escaped_count / len(seeds)
    print(f"\n  NOISELESS {shots}sh: {escaped_count}/{len(seeds)} = {rate:.2f}  (noisy ref {NOISY_REF.get(shots,'?')})")
    return results, escaped_count, rate


def main():
    print("=" * 70)
    print("Exp52 NOISELESS PROBE | Ember C3963 | pred_c3961 mechanism test")
    print(f"Seeds {SEEDS} | shots {SHOT_LEVELS} | NO noise model | local AerSimulator")
    print("=" * 70)
    out = {"experiment": "exp52_noiseless_probe", "cycle": 3963, "seeds": SEEDS,
           "shot_levels": SHOT_LEVELS, "escape_threshold": ESCAPE_THRESHOLD,
           "noisy_reference": NOISY_REF, "arms": {}}
    for shots in SHOT_LEVELS:
        res, esc, rate = run_noiseless_arm(shots, SEEDS)
        out["arms"][str(shots)] = {"results": res, "escaped": esc, "rate": rate,
                                   "noisy_ref_rate": NOISY_REF.get(shots)}
    # Verdict
    r256, r1024, r2048 = (out["arms"][str(s)]["rate"] for s in SHOT_LEVELS)
    out["verdict"] = {
        "noiseless_curve": {256: r256, 1024: r1024, 2048: r2048},
        "ceiling_2048": r2048,
        "beats_noisy_plateau": r2048 > NOISY_REF[2048],
        "reaches_unity": r2048 >= 1.0,
        "monotone_up_to_1024": r1024 >= r256,
    }
    print("\n" + "=" * 70)
    print(f"VERDICT: noiseless curve 256={r256:.2f} 1024={r1024:.2f} 2048={r2048:.2f}")
    print(f"  beats noisy 90% plateau @2048: {out['verdict']['beats_noisy_plateau']}")
    print(f"  reaches 100% ceiling @2048:    {out['verdict']['reaches_unity']}")
    print("=" * 70)
    os.makedirs("results", exist_ok=True)
    with open("results/exp52_noiseless_probe.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Saved -> results/exp52_noiseless_probe.json")


if __name__ == "__main__":
    main()
