#!/usr/bin/env python3
"""
Exp53: Depth vs Shots Tradeoff — p=5 COBYLA on EDGES_20
Elder C5852 | Pre-registered C5846 | Launched C5852

Pre-registration: /droid/repos/quantum/experiments/exp53-preregistration.md

HYPOTHESES:
  H1: p=5 COBYLA at 1024sh < 80% escape (depth penalty at high shots)
  H2: p=5 COBYLA at 256sh < 50% escape (double penalty at low shots)
  H3: gap_1024 = (p3_1024 - p5_1024) > gap_256 = (p3_256 - p5_256) (gap widens at high shots)

REUSED DATA FROM EXP51/52 (same seeds 42-51, same threshold, same noise model):
  p=3, COBYLA, 256sh:  6/10 = 0.60 (Exp51 Phase A)
  p=3, COBYLA, 1024sh: 9/10 = 0.90 (Exp51 Phase C)

NEW RUNS THIS EXPERIMENT (FakeMarrakesh simulation, no QPU quota needed):
  Arm C: p=5, COBYLA, 256sh,  seeds 42-51, max_iter=50
  Arm D: p=5, COBYLA, 1024sh, seeds 42-51, max_iter=50
  Total: 20 new runs
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
from run_exp51_spsa_vs_cobyla import optimize_cobyla
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))
OPT_LEVEL = 1
P_DEPTH = 5          # Key change: p=5 (vs p=3 in Exp51/52)
MAX_ITER = 50        # More iterations for larger parameter space (10 params vs 6)

# Reused data from Exp51/52 (same seeds, same threshold, same noise model)
EXP_REUSED = {
    "cobyla_p3_256sh":  {"escaped": 6, "rate": 0.60, "source": "Exp51 Phase A"},
    "cobyla_p3_1024sh": {"escaped": 9, "rate": 0.90, "source": "Exp51 Phase C"},
}

RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "results", "exp53_results.json")


def run_arm(arm_label, shots, seeds=SEEDS):
    """Run one experimental arm at p=5. Returns (escaped_count, results_list)."""
    print(f"\n{'='*60}")
    print(f"ARM: {arm_label} | p={P_DEPTH} | shots={shots} | seeds={seeds}")
    print(f"{'='*60}")
    t0 = time.time()

    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)

    edges = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)
    print(f"Graph: {n_qubits}n, {len(edges)}e | MaxCut={max_cut} | Threshold={ESCAPE_THRESHOLD * max_cut:.1f}")

    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(P_DEPTH, n_qubits, edges)
    transpiled_qc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    print(f"Circuit: {transpiled_qc.num_qubits}q, depth={transpiled_qc.depth()}, CX/CZ={transpiled_qc.count_ops().get('cx', 0) + transpiled_qc.count_ops().get('cz', 0)}")

    results = []
    escaped_count = 0

    for i, seed in enumerate(seeds, 1):
        np.random.seed(seed)
        seed_t0 = time.time()
        ratio = optimize_cobyla(
            transpiled_qc, gamma_params, beta_params, P_DEPTH,
            sim, edges, max_cut, n_qubits, shots=shots,
            max_iter=MAX_ITER
        )
        escaped = ratio >= ESCAPE_THRESHOLD
        if escaped:
            escaped_count += 1
        elapsed = time.time() - seed_t0
        print(f"  Seed {seed:2d} [{i:2d}/10]: ratio={ratio:.4f} {'[E]' if escaped else '[T]'} "
              f"time={elapsed:.0f}s")
        results.append({
            "seed": seed,
            "ratio": float(ratio),
            "escaped": bool(escaped),
            "elapsed_s": round(elapsed, 1)
        })

    total_elapsed = time.time() - t0
    rate = escaped_count / len(seeds)
    print(f"\n{arm_label} COMPLETE: {escaped_count}/{len(seeds)} escaped ({rate:.0%}) in {total_elapsed/60:.1f}min")
    return escaped_count, results


def evaluate_hypotheses(arm_c_rate, arm_d_rate):
    """Evaluate H1, H2, H3 against pre-registered success criteria."""
    p3_256 = EXP_REUSED["cobyla_p3_256sh"]["rate"]   # 0.60
    p3_1024 = EXP_REUSED["cobyla_p3_1024sh"]["rate"]  # 0.90
    p5_256 = arm_c_rate
    p5_1024 = arm_d_rate

    gap_256 = p3_256 - p5_256
    gap_1024 = p3_1024 - p5_1024

    h1 = {"hypothesis": "H1: p5_1024sh < 80% (depth penalty at high shots)",
          "verdict": "CONFIRMED" if p5_1024 < 0.80 else "REFUTED",
          "values": {"p5_1024sh": p5_1024, "threshold": 0.80}}
    h2 = {"hypothesis": "H2: p5_256sh < 50% (double penalty at low shots)",
          "verdict": "CONFIRMED" if p5_256 < 0.50 else "REFUTED",
          "values": {"p5_256sh": p5_256, "threshold": 0.50}}
    h3 = {"hypothesis": "H3: gap_1024 > gap_256 (gap widens with shots)",
          "verdict": "CONFIRMED" if gap_1024 > gap_256 else "REFUTED",
          "values": {"gap_1024": round(gap_1024, 3), "gap_256": round(gap_256, 3)}}

    return [h1, h2, h3]


def main():
    print("=" * 60)
    print("EXP53: Depth vs Shots Tradeoff (p=5 COBYLA, FakeMarrakesh)")
    print(f"Author: Elder C5852 | Pre-reg: C5846")
    print(f"P_DEPTH={P_DEPTH}, MAX_ITER={MAX_ITER}, SEEDS={SEEDS}")
    print("=" * 60)
    print(f"\nReused baselines (no rerun):")
    for k, v in EXP_REUSED.items():
        print(f"  {k}: {v['escaped']}/10 = {v['rate']:.0%} ({v['source']})")

    run_t0 = time.time()

    # Arm C: p=5, 256 shots
    c_escaped, c_results = run_arm("Arm-C (p=5, 256sh)", shots=256)
    arm_c_rate = c_escaped / len(SEEDS)

    # Arm D: p=5, 1024 shots
    d_escaped, d_results = run_arm("Arm-D (p=5, 1024sh)", shots=1024)
    arm_d_rate = d_escaped / len(SEEDS)

    total_time = time.time() - run_t0
    hypotheses = evaluate_hypotheses(arm_c_rate, arm_d_rate)

    print("\n" + "=" * 60)
    print("HYPOTHESIS EVALUATION")
    print("=" * 60)
    for h in hypotheses:
        print(f"\n[{h['verdict']}] {h['hypothesis']}")
        for k, v in h['values'].items():
            print(f"  {k}: {v}")

    results = {
        "experiment": "Exp53",
        "author": "Elder C5852",
        "pre_reg_cycle": "C5846",
        "launched_cycle": "C5852",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": {"p_depth": P_DEPTH, "max_iter": MAX_ITER, "seeds": SEEDS,
                   "escape_threshold": ESCAPE_THRESHOLD},
        "reused_baselines": EXP_REUSED,
        "arm_c": {"label": "p=5 COBYLA 256sh", "escaped": c_escaped, "rate": arm_c_rate, "results": c_results},
        "arm_d": {"label": "p=5 COBYLA 1024sh", "escaped": d_escaped, "rate": arm_d_rate, "results": d_results},
        "hypotheses": hypotheses,
        "total_wall_time_min": round(total_time / 60, 1)
    }

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {RESULTS_PATH}")
    print(f"Total wall time: {total_time/60:.1f} min")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"p=3, 256sh (Exp51):  6/10 = 60%  [baseline]")
    print(f"p=5, 256sh (Arm C):  {c_escaped}/10 = {arm_c_rate:.0%}  [new]")
    print(f"p=3, 1024sh (Exp51): 9/10 = 90%  [baseline]")
    print(f"p=5, 1024sh (Arm D): {d_escaped}/10 = {arm_d_rate:.0%}  [new]")
    confirmed = sum(1 for h in hypotheses if h['verdict'] == 'CONFIRMED')
    print(f"\nHypotheses: {confirmed}/3 CONFIRMED")


if __name__ == "__main__":
    main()
