#!/usr/bin/env python3
"""
Exp52 SPSA Final — Ember C3727
Completes SPSA_512sh and SPSA_1024sh (COBYLA arms already done).

COBYLA results already collected:
  128sh: 7/10 = 0.70  (Exp52)
  256sh: 6/10 = 0.60  (Exp51 reused)
  512sh: 8/10 = 0.80  (Exp52)
  1024sh: 9/10 = 0.90 (Exp51 reused)
  2048sh: 9/10 = 0.90 (Exp52 — seed51 trapped 0.5984, rest escaped)

H1 can be evaluated from COBYLA alone.
H2 requires SPSA_1024sh (this script).
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
from run_exp51_spsa_vs_cobyla import optimize_spsa
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))
OPT_LEVEL = 1
MAX_ITER_SPSA = 30
SPSA_PARAMS = {"a": 0.1, "A": 10, "alpha": 0.602, "c": 0.1, "gamma": 0.101}

# Already collected COBYLA curve
COBYLA_CURVE = {
    128:  0.70,
    256:  0.60,
    512:  0.80,
    1024: 0.90,
    2048: 0.90,
}

# SPSA from Exp51
SPSA_256SH_RATE = 0.30


def build_sim_and_circuit():
    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)
    p = 3
    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    transpiled_qc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    return sim, transpiled_qc, gamma_params, beta_params, max_cut


def run_spsa_arm(label, shots, seeds, sim, transpiled_qc, gamma_params, beta_params, max_cut):
    print(f"\n{'='*60}")
    print(f"ARM: {label} | optimizer=SPSA | shots={shots} | seeds={seeds}")
    print(f"{'='*60}")
    sys.stdout.flush()
    results = []
    n_escaped = 0
    for seed in seeds:
        np.random.seed(seed)
        t0 = time.time()
        ratio = optimize_spsa(
            transpiled_qc, gamma_params, beta_params, 3,
            sim, EDGES_20, max_cut, N_QUBITS_20, shots, MAX_ITER_SPSA,
            **SPSA_PARAMS
        )
        elapsed = time.time() - t0
        escaped = ratio > ESCAPE_THRESHOLD
        status = "✓ ESCAPED" if escaped else "✗ trapped"
        print(f"  [{label}] seed={seed}: ratio={ratio:.4f} {status} ({elapsed:.1f}s)")
        sys.stdout.flush()
        if escaped:
            n_escaped += 1
        results.append({"seed": seed, "ratio": float(ratio), "escaped": bool(escaped)})
    rate = n_escaped / len(seeds)
    print(f"\n  ARM RESULT: {n_escaped}/{len(seeds)} = {rate:.2f} escape rate")
    sys.stdout.flush()
    return results, n_escaped, rate


def main():
    print("=" * 70)
    print("EXP52 SPSA FINAL — Ember C3727")
    print("Running: SPSA_512sh + SPSA_1024sh")
    print(f"Bug fix: added MAX_ITER_SPSA={MAX_ITER_SPSA} as positional arg")
    print("=" * 70)
    sys.stdout.flush()

    sim, transpiled_qc, gamma_params, beta_params, max_cut = build_sim_and_circuit()

    spsa_512_results, spsa_512_escaped, spsa_512_rate = run_spsa_arm(
        "SPSA_512sh", 512, SEEDS, sim, transpiled_qc, gamma_params, beta_params, max_cut
    )

    spsa_1024_results, spsa_1024_escaped, spsa_1024_rate = run_spsa_arm(
        "SPSA_1024sh", 1024, SEEDS, sim, transpiled_qc, gamma_params, beta_params, max_cut
    )

    spsa_data = {
        256:  SPSA_256SH_RATE,
        512:  spsa_512_rate,
        1024: spsa_1024_rate,
    }

    # H1: COBYLA monotonicity (can evaluate from curve alone)
    shots_ordered = [128, 256, 512, 1024, 2048]
    rates_ordered = [COBYLA_CURVE[s] for s in shots_ordered]
    non_monotone = sum(1 for i in range(len(rates_ordered) - 1)
                       if rates_ordered[i + 1] < rates_ordered[i])
    h1 = non_monotone <= 1

    # H2: SPSA parity at 1024 shots
    h2 = spsa_data[1024] >= 0.70

    # H3: diminishing returns at 2048 (implicit — gain from 1024→2048)
    gain = COBYLA_CURVE[2048] - COBYLA_CURVE[1024]
    h3 = gain <= 0.05

    print("\n" + "=" * 70)
    print("H1 TEST: COBYLA Shot Curve Monotonicity")
    print("=" * 70)
    for s, r in zip(shots_ordered, rates_ordered):
        tag = "(Exp51 reused)" if s in [256, 1024] else "(Exp52)"
        print(f"  {s:5d}sh: {r:.2f} {tag}")
    print(f"  Non-monotone steps: {non_monotone}")
    print(f"  H1 {'CONFIRMED' if h1 else 'REFUTED'} (threshold: ≤1 non-monotone step)")
    sys.stdout.flush()

    print("\n" + "=" * 70)
    print("H2 TEST: SPSA Parity at 1024 shots")
    print("=" * 70)
    print(f"  SPSA_256sh  (Exp51 reused): {spsa_data[256]:.2f}")
    print(f"  SPSA_512sh  (Exp52 new):    {spsa_data[512]:.2f}")
    print(f"  SPSA_1024sh (Exp52 new):    {spsa_data[1024]:.2f}")
    print(f"  COBYLA_1024sh:              {COBYLA_CURVE[1024]:.2f}")
    print(f"  Gap (COBYLA - SPSA):        {COBYLA_CURVE[1024] - spsa_data[1024]:.2f}")
    print(f"  H2 {'CONFIRMED' if h2 else 'REFUTED'} (SPSA_1024 >= 0.70)")
    sys.stdout.flush()

    print("\n" + "=" * 70)
    print("H3 TEST: Diminishing Returns at 2048 shots")
    print("=" * 70)
    print(f"  COBYLA_1024sh → COBYLA_2048sh: {COBYLA_CURVE[1024]:.2f} → {COBYLA_CURVE[2048]:.2f} (gain={gain:.2f})")
    print(f"  H3 {'CONFIRMED' if h3 else 'REFUTED'} (gain ≤ 0.05)")
    sys.stdout.flush()

    print("\n" + "=" * 70)
    print("FULL RESULTS SUMMARY")
    print("=" * 70)
    print(f"  COBYLA curve: {', '.join(f'{s}sh:{COBYLA_CURVE[s]:.2f}' for s in shots_ordered)}")
    print(f"  SPSA curve:   {', '.join(f'{s}sh:{spsa_data[s]:.2f}' for s in [256, 512, 1024])}")
    print(f"  H1 (monotone): {'CONFIRMED' if h1 else 'REFUTED'}")
    print(f"  H2 (SPSA parity): {'CONFIRMED' if h2 else 'REFUTED'}")
    print(f"  H3 (diminishing returns): {'CONFIRMED' if h3 else 'REFUTED'}")
    sys.stdout.flush()

    # Save results
    output = {
        "experiment": "Exp52 SPSA Final — Ember C3727",
        "cobyla_curve": COBYLA_CURVE,
        "spsa_data": spsa_data,
        "spsa_512_results": spsa_512_results,
        "spsa_1024_results": spsa_1024_results,
        "hypotheses": {
            "H1_monotone": h1,
            "H2_spsa_parity": h2,
            "H3_diminishing_returns": h3,
            "non_monotone_steps": non_monotone,
        }
    }
    out_path = os.path.join(os.path.dirname(__file__), "../results/exp52_spsa_final.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to: {out_path}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
