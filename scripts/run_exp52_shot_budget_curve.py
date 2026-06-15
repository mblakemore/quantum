#!/usr/bin/env python3
"""
Exp52: Shot Budget Curve + SPSA Parity Test
Ember C3707 | Pre-registered 2026-06-14
Launched: C3708

Pre-registration: /droid/repos/quantum/experiments/exp52-preregistration.md

HYPOTHESES:
  H1: COBYLA escape rate monotone across shots={128,256,512,1024,2048} (>=4/5 monotone)
  H2: SPSA escape rate at >=1024sh within 20pp of COBYLA (SPSA_1024 >= 70%)
  H3: COBYLA_2048 <= COBYLA_1024 + 5pp (saturation above 1024)

REUSED FROM EXP51 (seeds 42-51, same threshold 0.64, same FakeMarrakesh):
  256sh COBYLA: 6/10 = 0.60 (Phase A)
  256sh SPSA:   3/10 = 0.30 (Phase B, context only)
  1024sh COBYLA: 9/10 = 0.90 (Phase C)

NEW RUNS THIS EXPERIMENT:
  128sh COBYLA  x10 seeds (Arm1-128)
  512sh COBYLA  x10 seeds (Arm1-512)
  2048sh COBYLA x10 seeds (Arm1-2048)
  512sh SPSA    x10 seeds (Arm2-512)
  1024sh SPSA   x10 seeds (Arm2-1024)
  Total: 50 new runs
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,
)
from run_exp51_spsa_vs_cobyla import optimize_cobyla, optimize_spsa
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))
OPT_LEVEL = 1

# ============================================================
# REUSED DATA FROM EXP51 (same seeds, same threshold, same noise model)
# ============================================================
EXP51_REUSED = {
    "cobyla_256sh": {"escaped": 6, "rate": 0.60, "source": "Exp51 Phase A"},
    "spsa_256sh":   {"escaped": 3, "rate": 0.30, "source": "Exp51 Phase B"},
    "cobyla_1024sh": {"escaped": 9, "rate": 0.90, "source": "Exp51 Phase C"},
}


def run_arm(arm_label, optimizer, shots, seeds, max_iter_cobyla=30, spsa_params=None):
    """Run one experimental arm. Returns list of (seed, ratio, escaped) tuples."""
    print(f"\n{'='*60}")
    print(f"ARM: {arm_label} | optimizer={optimizer} | shots={shots} | seeds={seeds}")
    print(f"{'='*60}")

    # Build noise model + simulator (same as Exp51)
    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)

    # Build circuit (standard QAOA, p=3, not x-basis)
    p = 3
    edges = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)

    # Build and transpile circuit once (same approach as Exp51)
    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    transpiled_qc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)

    results = []
    escaped_count = 0

    for seed in seeds:
        np.random.seed(seed)
        t0 = time.time()

        if optimizer == "COBYLA":
            ratio = optimize_cobyla(
                transpiled_qc, gamma_params, beta_params, p,
                sim, edges, max_cut, n_qubits, shots, max_iter_cobyla
            )
        elif optimizer == "SPSA":
            if spsa_params is None:
                spsa_params = {"a": 0.1, "A": 10, "alpha": 0.602, "c": 0.1, "gamma": 0.101}
            ratio = optimize_spsa(
                transpiled_qc, gamma_params, beta_params, p,
                sim, edges, max_cut, n_qubits, shots,
                a=spsa_params["a"], A=spsa_params["A"],
                alpha=spsa_params["alpha"], c=spsa_params["c"],
                gamma=spsa_params["gamma"]
            )
        else:
            raise ValueError(f"Unknown optimizer: {optimizer}")

        escaped = ratio > ESCAPE_THRESHOLD
        if escaped:
            escaped_count += 1

        elapsed = time.time() - t0
        status = "✓ ESCAPED" if escaped else "✗ trapped"
        print(f"  seed={seed}: ratio={ratio:.4f} {status} ({elapsed:.1f}s)")

        results.append({
            "seed": seed,
            "ratio": float(ratio),
            "escaped": bool(escaped),
            "elapsed_s": float(elapsed)
        })

    rate = escaped_count / len(seeds)
    print(f"\n  ARM RESULT: {escaped_count}/{len(seeds)} = {rate:.2f} escape rate")
    return results, escaped_count, rate


def main():
    print("=" * 70)
    print("EXP52: Shot Budget Curve + SPSA Parity Test")
    print(f"Ember C3708 | FakeMarrakesh (AerSimulator) | Seeds: {SEEDS}")
    print(f"Escape threshold: {ESCAPE_THRESHOLD}")
    print("=" * 70)
    print()
    print("REUSED FROM EXP51:")
    for k, v in EXP51_REUSED.items():
        print(f"  {k}: {v['escaped']}/10 = {v['rate']:.2f} ({v['source']})")
    print()

    arms_to_run = [
        # (label, optimizer, shots)
        ("COBYLA_128sh",  "COBYLA", 128),
        ("COBYLA_512sh",  "COBYLA", 512),
        ("COBYLA_2048sh", "COBYLA", 2048),
        ("SPSA_512sh",    "SPSA",   512),
        ("SPSA_1024sh",   "SPSA",   1024),
    ]

    all_results = {}

    for label, opt, shots in arms_to_run:
        data, escaped, rate = run_arm(label, opt, shots, SEEDS)
        all_results[label] = {
            "optimizer": opt,
            "shots": shots,
            "escaped": escaped,
            "rate": rate,
            "data": data,
        }

    # ============================================================
    # COMPILE FULL RESULTS (new + reused)
    # ============================================================
    full_cobyla_curve = {
        128:  all_results["COBYLA_128sh"]["rate"],
        256:  EXP51_REUSED["cobyla_256sh"]["rate"],    # reused
        512:  all_results["COBYLA_512sh"]["rate"],
        1024: EXP51_REUSED["cobyla_1024sh"]["rate"],   # reused
        2048: all_results["COBYLA_2048sh"]["rate"],
    }

    full_spsa_data = {
        256:  EXP51_REUSED["spsa_256sh"]["rate"],      # context from Exp51
        512:  all_results["SPSA_512sh"]["rate"],
        1024: all_results["SPSA_1024sh"]["rate"],
    }

    # ============================================================
    # H1 TEST: COBYLA curve monotone?
    # ============================================================
    shot_counts_ordered = [128, 256, 512, 1024, 2048]
    cobyla_rates_ordered = [full_cobyla_curve[s] for s in shot_counts_ordered]

    non_monotone_steps = 0
    for i in range(len(cobyla_rates_ordered) - 1):
        if cobyla_rates_ordered[i+1] < cobyla_rates_ordered[i]:
            non_monotone_steps += 1

    h1_confirmed = non_monotone_steps <= 1  # allows 1 non-monotone step

    print("\n" + "=" * 70)
    print("H1 TEST: COBYLA Shot Curve Monotonicity")
    print("=" * 70)
    for s, r in zip(shot_counts_ordered, cobyla_rates_ordered):
        source = "(Exp51)" if s in [256, 1024] else "(new)"
        print(f"  {s:5d}sh: {r:.2f} {source}")
    print(f"  Non-monotone steps: {non_monotone_steps}")
    print(f"  H1 CONFIRMED: {h1_confirmed}")

    # ============================================================
    # H2 TEST: SPSA parity at 1024sh
    # ============================================================
    spsa_1024_rate = full_spsa_data[1024]
    cobyla_1024_rate = full_cobyla_curve[1024]
    gap = cobyla_1024_rate - spsa_1024_rate
    h2_confirmed = spsa_1024_rate >= 0.70

    print("\n" + "=" * 70)
    print("H2 TEST: SPSA Parity at 1024 shots")
    print("=" * 70)
    print(f"  SPSA_256sh  (Exp51): {full_spsa_data[256]:.2f}")
    print(f"  SPSA_512sh  (new):   {full_spsa_data[512]:.2f}")
    print(f"  SPSA_1024sh (new):   {full_spsa_data[1024]:.2f}")
    print(f"  COBYLA_1024sh:       {cobyla_1024_rate:.2f}")
    print(f"  Gap (COBYLA - SPSA): {gap:.2f}")
    print(f"  H2 CONFIRMED (SPSA_1024 >= 0.70): {h2_confirmed}")

    # ============================================================
    # H3 TEST: Saturation above 1024
    # ============================================================
    gain_2048 = full_cobyla_curve[2048] - full_cobyla_curve[1024]
    h3_confirmed = gain_2048 <= 0.05

    print("\n" + "=" * 70)
    print("H3 TEST: Saturation above 1024 shots")
    print("=" * 70)
    print(f"  COBYLA_1024sh: {full_cobyla_curve[1024]:.2f}")
    print(f"  COBYLA_2048sh: {full_cobyla_curve[2048]:.2f}")
    print(f"  Gain (2048-1024): {gain_2048:+.2f}")
    print(f"  H3 CONFIRMED (gain <= 0.05): {h3_confirmed}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    output = {
        "experiment": "Exp52",
        "source": "Ember C3708 | FakeMarrakesh AerSimulator",
        "date": time.strftime("%Y-%m-%d"),
        "config": {
            "escape_threshold": ESCAPE_THRESHOLD,
            "seeds": SEEDS,
            "problem": "EDGES_20, 20 qubits, 30 edges, MaxCut=26",
            "ansatz": "p=3 QAOA (standard, not x-basis)"
        },
        "reused_from_exp51": EXP51_REUSED,
        "new_arms": all_results,
        "compiled_results": {
            "cobyla_curve": full_cobyla_curve,
            "spsa_data": full_spsa_data,
        },
        "hypothesis_tests": {
            "H1": {
                "description": "COBYLA curve monotone (<=1 non-monotone step)",
                "non_monotone_steps": non_monotone_steps,
                "confirmed": h1_confirmed,
            },
            "H2": {
                "description": "SPSA_1024 >= 0.70 (within 20pp of COBYLA_1024=0.90)",
                "spsa_1024_rate": spsa_1024_rate,
                "cobyla_1024_rate": cobyla_1024_rate,
                "gap": gap,
                "confirmed": h2_confirmed,
            },
            "H3": {
                "description": "COBYLA_2048 <= COBYLA_1024 + 0.05 (saturation)",
                "gain_2048_vs_1024": gain_2048,
                "confirmed": h3_confirmed,
            },
        },
    }

    outpath = "/droid/repos/quantum/results/exp52_results.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {outpath}")

    print("\n" + "=" * 70)
    print("EXP52 COMPLETE")
    print(f"  H1 (monotone curve): {'CONFIRMED' if h1_confirmed else 'REFUTED'}")
    print(f"  H2 (SPSA parity):    {'CONFIRMED' if h2_confirmed else 'REFUTED'}")
    print(f"  H3 (saturation):     {'CONFIRMED' if h3_confirmed else 'REFUTED'}")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
