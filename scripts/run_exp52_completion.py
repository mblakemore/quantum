#!/usr/bin/env python3
"""
Exp52 Completion Script — Ember C3725
Picks up where server restart killed the run.

What's missing:
  1. COBYLA_2048sh seed=51 (seeds 42-50 completed: 9/9 escaped)
  2. SPSA_512sh (10 seeds: 42-51) — never ran
  3. SPSA_1024sh (10 seeds: 42-51) — never ran

Completed data from exp52_output.txt:
  COBYLA_128sh:  7/10 = 0.70
  COBYLA_512sh:  8/10 = 0.80
  COBYLA_2048sh: 9/9 escaped so far (seed 51 missing)
  Reused Exp51: cobyla_256sh=0.60, cobyla_1024sh=0.90, spsa_256sh=0.30
"""
import sys, os, json, time
import numpy as np

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
MAX_ITER_COBYLA = 30
MAX_ITER_SPSA = 30
SPSA_PARAMS = {"a": 0.1, "A": 10, "alpha": 0.602, "c": 0.1, "gamma": 0.101}

# Data already collected (from exp52_output.txt)
COBYLA_2048SH_COMPLETED = {
    42: (0.6834, True),
    43: (0.6867, True),
    44: (0.6884, True),
    45: (0.6867, True),
    46: (0.6829, True),
    47: (0.6719, True),
    48: (0.6803, True),
    49: (0.6837, True),
    50: (0.6843, True),
    # seed 51: MISSING — will run now
}

# Reused from Exp51
EXP51_REUSED = {
    "cobyla_256sh": 0.60,
    "cobyla_1024sh": 0.90,
    "spsa_256sh": 0.30,
}

# Previously completed Exp52 arms (from exp52_output.txt)
COBYLA_128SH_RATE = 0.70   # 7/10
COBYLA_512SH_RATE = 0.80   # 8/10


def build_sim_and_circuit():
    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)
    p = 3
    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    transpiled_qc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    return sim, transpiled_qc, gamma_params, beta_params, max_cut


def run_single_seed(label, optimizer, shots, seed, sim, transpiled_qc,
                    gamma_params, beta_params, max_cut):
    np.random.seed(seed)
    t0 = time.time()
    if optimizer == "COBYLA":
        ratio = optimize_cobyla(
            transpiled_qc, gamma_params, beta_params, 3,
            sim, EDGES_20, max_cut, N_QUBITS_20, shots, MAX_ITER_COBYLA
        )
    else:
        ratio = optimize_spsa(
            transpiled_qc, gamma_params, beta_params, 3,
            sim, EDGES_20, max_cut, N_QUBITS_20, shots,
            **SPSA_PARAMS
        )
    elapsed = time.time() - t0
    escaped = ratio > ESCAPE_THRESHOLD
    status = "✓ ESCAPED" if escaped else "✗ trapped"
    print(f"  [{label}] seed={seed}: ratio={ratio:.4f} {status} ({elapsed:.1f}s)")
    return ratio, escaped


def run_arm(label, optimizer, shots, seeds, sim, transpiled_qc,
            gamma_params, beta_params, max_cut):
    print(f"\n{'='*60}")
    print(f"ARM: {label} | optimizer={optimizer} | shots={shots} | seeds={seeds}")
    print(f"{'='*60}")
    results = []
    n_escaped = 0
    for seed in seeds:
        ratio, escaped = run_single_seed(
            label, optimizer, shots, seed,
            sim, transpiled_qc, gamma_params, beta_params, max_cut
        )
        if escaped:
            n_escaped += 1
        results.append({"seed": seed, "ratio": float(ratio), "escaped": bool(escaped)})
    rate = n_escaped / len(seeds)
    print(f"\n  ARM RESULT: {n_escaped}/{len(seeds)} = {rate:.2f} escape rate")
    return results, n_escaped, rate


def main():
    print("=" * 70)
    print("EXP52 COMPLETION — Ember C3725")
    print("Running: COBYLA_2048sh seed=51 + SPSA_512sh + SPSA_1024sh")
    print("=" * 70)

    sim, transpiled_qc, gamma_params, beta_params, max_cut = build_sim_and_circuit()

    # ── Step 1: COBYLA_2048sh seed 51 ──────────────────────────────
    print("\n" + "=" * 60)
    print("COMPLETING ARM: COBYLA_2048sh (seed=51 only)")
    print("=" * 60)
    ratio_51, escaped_51 = run_single_seed(
        "COBYLA_2048sh", "COBYLA", 2048, 51,
        sim, transpiled_qc, gamma_params, beta_params, max_cut
    )

    # Combine with already-completed seeds
    cobyla_2048sh_escaped = sum(1 for r, e in COBYLA_2048SH_COMPLETED.values() if e)
    if escaped_51:
        cobyla_2048sh_escaped += 1
    cobyla_2048sh_rate = cobyla_2048sh_escaped / 10
    print(f"\n  COBYLA_2048sh FINAL: {cobyla_2048sh_escaped}/10 = {cobyla_2048sh_rate:.2f} escape rate")

    # ── Step 2: SPSA_512sh ─────────────────────────────────────────
    spsa_512_results, spsa_512_escaped, spsa_512_rate = run_arm(
        "SPSA_512sh", "SPSA", 512, SEEDS,
        sim, transpiled_qc, gamma_params, beta_params, max_cut
    )

    # ── Step 3: SPSA_1024sh ────────────────────────────────────────
    spsa_1024_results, spsa_1024_escaped, spsa_1024_rate = run_arm(
        "SPSA_1024sh", "SPSA", 1024, SEEDS,
        sim, transpiled_qc, gamma_params, beta_params, max_cut
    )

    # ── Hypothesis Tests ───────────────────────────────────────────
    cobyla_curve = {
        128:  COBYLA_128SH_RATE,
        256:  EXP51_REUSED["cobyla_256sh"],
        512:  COBYLA_512SH_RATE,
        1024: EXP51_REUSED["cobyla_1024sh"],
        2048: cobyla_2048sh_rate,
    }
    spsa_data = {
        256:  EXP51_REUSED["spsa_256sh"],
        512:  spsa_512_rate,
        1024: spsa_1024_rate,
    }

    shots_ordered = [128, 256, 512, 1024, 2048]
    rates_ordered = [cobyla_curve[s] for s in shots_ordered]
    non_monotone = sum(1 for i in range(len(rates_ordered) - 1)
                       if rates_ordered[i + 1] < rates_ordered[i])
    h1 = non_monotone <= 1

    gap = cobyla_curve[1024] - spsa_data[1024]
    h2 = spsa_data[1024] >= 0.70

    gain = cobyla_curve[2048] - cobyla_curve[1024]
    h3 = gain <= 0.05

    print("\n" + "=" * 70)
    print("H1 TEST: COBYLA Shot Curve Monotonicity")
    print("=" * 70)
    for s, r in zip(shots_ordered, rates_ordered):
        tag = "(Exp51 reused)" if s in [256, 1024] else "(Exp52)"
        print(f"  {s:5d}sh: {r:.2f} {tag}")
    print(f"  Non-monotone steps: {non_monotone}")
    print(f"  H1 {'CONFIRMED' if h1 else 'REFUTED'}")

    print("\n" + "=" * 70)
    print("H2 TEST: SPSA Parity at 1024 shots")
    print("=" * 70)
    print(f"  SPSA_256sh  (Exp51 reused): {spsa_data[256]:.2f}")
    print(f"  SPSA_512sh  (Exp52 new):    {spsa_data[512]:.2f}")
    print(f"  SPSA_1024sh (Exp52 new):    {spsa_data[1024]:.2f}")
    print(f"  COBYLA_1024sh:              {cobyla_curve[1024]:.2f}")
    print(f"  Gap (COBYLA - SPSA):        {gap:.2f}")
    print(f"  H2 {'CONFIRMED' if h2 else 'REFUTED'} (SPSA_1024 >= 0.70)")

    print("\n" + "=" * 70)
    print("H3 TEST: Saturation above 1024 shots")
    print("=" * 70)
    print(f"  COBYLA_1024sh: {cobyla_curve[1024]:.2f}")
    print(f"  COBYLA_2048sh: {cobyla_curve[2048]:.2f}")
    print(f"  Gain:          {gain:+.2f}")
    print(f"  H3 {'CONFIRMED' if h3 else 'REFUTED'} (gain <= 0.05)")

    # ── Save results ───────────────────────────────────────────────
    output = {
        "experiment": "Exp52",
        "completion_cycle": "C3725",
        "original_cycle": "C3708",
        "completion_reason": "Server restart killed COBYLA_2048sh seed=51 and SPSA arm had not yet run",
        "cobyla_curve": cobyla_curve,
        "spsa_data": spsa_data,
        "new_arms": {
            "COBYLA_2048sh_seed51": {
                "seed": 51, "ratio": float(ratio_51), "escaped": bool(escaped_51)
            },
            "COBYLA_2048sh_final": {
                "escaped": cobyla_2048sh_escaped, "total": 10, "rate": cobyla_2048sh_rate
            },
            "SPSA_512sh": {"escaped": spsa_512_escaped, "total": 10, "rate": spsa_512_rate,
                           "seeds": spsa_512_results},
            "SPSA_1024sh": {"escaped": spsa_1024_escaped, "total": 10, "rate": spsa_1024_rate,
                            "seeds": spsa_1024_results},
        },
        "hypothesis_tests": {
            "H1": {"description": "COBYLA curve monotone (<=1 non-monotone step)",
                   "non_monotone_steps": non_monotone, "confirmed": h1},
            "H2": {"description": "SPSA_1024 >= 0.70 (within 20pp of COBYLA_1024=0.90)",
                   "spsa_1024_rate": spsa_1024_rate, "cobyla_1024_rate": cobyla_curve[1024],
                   "gap": float(gap), "confirmed": h2},
            "H3": {"description": "COBYLA_2048 <= COBYLA_1024 + 0.05 (saturation)",
                   "gain_2048_vs_1024": float(gain), "confirmed": h3},
        },
    }

    outpath = "/droid/repos/quantum/results/exp52_completion_results.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outpath}")

    print("\n" + "=" * 70)
    print("EXP52 COMPLETE")
    print(f"  H1 (monotone curve): {'CONFIRMED' if h1 else 'REFUTED'}")
    print(f"  H2 (SPSA parity):    {'CONFIRMED' if h2 else 'REFUTED'}")
    print(f"  H3 (saturation):     {'CONFIRMED' if h3 else 'REFUTED'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
