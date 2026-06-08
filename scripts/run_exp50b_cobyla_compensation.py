#!/usr/bin/env python3
"""
Exp50b (Exp50-revised Phase 2+3): COBYLA Compensation Threshold
Elder C5733 | 2026-06-08

CONTEXT: Exp49 found ~17-28% escape rate at p=5 with MAX_ITER=30 (stochastic/partial,
final verdict pending). Pearson r was in H3 territory (0.374 at 7/10 seeds).

WHY: p=3 used MAX_ITER=30 with 6 params = 5 iter/param → 100% escape
     p=5 uses MAX_ITER=30 with 10 params = 3 iter/param → ~20-30% escape
     COBYLA Compensation Threshold (Whisper C4002): iter/param = the causal variable.

Pearl causal model (Whisper C4002):
  P(escape | do(budget_per_dim=5)) vs P(escape | do(budget_per_dim=3))
  Causal variable: ITERATIONS-PER-DIMENSION
  Depth is a CONFOUNDER (depth × MAX_ITER → budget_per_dim)
  Seeds are INITIAL CONDITIONS (Pearl Rung 1), not causal nodes

DESIGN:
  Phase 1 (Baseline): p=5, MAX_ITER=30 → 3 iter/param → ALREADY DONE in Exp49
    (re-use exp49_results.json Phase 1 data)
  Phase 2 (Main test): p=5, MAX_ITER=50 → 5 iter/param
    Prediction: escape rate INCREASES toward p=3 rate (~80-100%)
  Phase 3 (Control): p=3, MAX_ITER=18 → 3 iter/param
    Prediction: escape rate DECREASES from 100% (shows iter/param, not depth, matters)

HYPOTHESES:
  H_B (Budget): P(escape|iter/param=5) > P(escape|iter/param=3)
    Decision: Phase 2 escape rate > Phase 1 escape rate (50% increase minimum)
    AND Phase 3 escape rate < Phase 1 p=3 rate (100% drops to <85%)
  H_DEPTH: Depth is the actual causal variable
    Decision: Phase 2 escape rate ≈ Phase 1 rate (MAX_ITER doesn't matter)
  H_SEED: Seed-specific effects dominate
    Decision: Same seeds always escape regardless of iter/param

PRE-CONDITION: Exp49 H1 NOT confirmed (r < 0.60). Current r=0.374 → TRIGGER MET.
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
OPT_LEVEL = 1
ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))   # same 10 seeds as Exp49

# Phase 2: equalized budget (main test)
PHASE2_P = 5
PHASE2_ITER = 50   # 5 iter/param (vs Exp49's 3 iter/param)

# Phase 3: reduced budget control
PHASE3_P = 3
PHASE3_ITER = 18   # 3 iter/param (vs Exp49's 5 iter/param)


def run_single(sim, max_cut, p, seed, max_iter):
    template, gpar, bpar = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
    np.random.seed(seed)
    x0_preview = np.random.uniform(0, 2 * np.pi, 2 * p)
    np.random.seed(seed)
    ratio, _ = optimize_with_cached_circuit(
        tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
        N_QUBITS_20, SHOTS, n_restarts=1, max_iter=max_iter,
    )
    return float(ratio), x0_preview.tolist()


if __name__ == '__main__':
    print("Exp50b: COBYLA Compensation Threshold Test", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges", flush=True)
    print(f"Seeds: {SEEDS}", flush=True)
    print(f"Escape threshold: {ESCAPE_THRESHOLD}", flush=True)
    print(f"Phase 2: p={PHASE2_P}, MAX_ITER={PHASE2_ITER} ({PHASE2_ITER//(2*PHASE2_P)} iter/param)", flush=True)
    print(f"Phase 3: p={PHASE3_P}, MAX_ITER={PHASE3_ITER} ({PHASE3_ITER//(2*PHASE3_P)} iter/param)", flush=True)
    print(f"Hypothesis: iter/param=5 → ~100% escape; iter/param=3 → ~40% escape", flush=True)
    print()

    # Load Phase 1 data from Exp49 results (if available)
    exp49_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '..', 'experiments', 'exp49_results.json')
    phase1_data = None
    if os.path.exists(exp49_file):
        with open(exp49_file) as f:
            exp49 = json.load(f)
        phase1_data = exp49['results']['5']  # p=5, MAX_ITER=30
        esc_p1 = sum(1 for v in phase1_data.values() if v >= ESCAPE_THRESHOLD)
        print(f"Phase 1 (Exp49, p=5/MAX_ITER=30): {esc_p1}/10 = {esc_p1*10}% escape", flush=True)
        data_str = ', '.join(f's{s}={phase1_data[str(s)]:.4f}[{"E" if phase1_data[str(s)]>=ESCAPE_THRESHOLD else "T"}]' for s in SEEDS)
        print(f"  Data: {data_str}", flush=True)
    else:
        print("Phase 1 data not yet available (Exp49 still running) — skip", flush=True)
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)

    t0 = time.time()
    results_phase2 = {}
    results_phase3 = {}

    # Phase 2: p=5, MAX_ITER=50
    print(f"\n=== PHASE 2: p={PHASE2_P}, MAX_ITER={PHASE2_ITER} ===", flush=True)
    for i, seed in enumerate(SEEDS):
        run_num = i + 1
        ratio, x0 = run_single(sim, max_cut, PHASE2_P, seed, PHASE2_ITER)
        results_phase2[seed] = ratio
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        elapsed = int(time.time() - t0)
        print(f"  [P2 {run_num:02d}/{len(SEEDS):02d}] p=5 seed={seed} MAX_ITER={PHASE2_ITER} ... {ratio:.4f} [{status}]  elapsed={elapsed}s", flush=True)

    esc_p2 = sum(1 for v in results_phase2.values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase 2 escape rate: {esc_p2}/10 = {esc_p2*10}%", flush=True)

    # Phase 3: p=3, MAX_ITER=18
    print(f"\n=== PHASE 3: p={PHASE3_P}, MAX_ITER={PHASE3_ITER} ===", flush=True)
    for i, seed in enumerate(SEEDS):
        run_num = i + 1
        ratio, x0 = run_single(sim, max_cut, PHASE3_P, seed, PHASE3_ITER)
        results_phase3[seed] = ratio
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        elapsed = int(time.time() - t0)
        print(f"  [P3 {run_num:02d}/{len(SEEDS):02d}] p=3 seed={seed} MAX_ITER={PHASE3_ITER} ... {ratio:.4f} [{status}]  elapsed={elapsed}s", flush=True)

    esc_p3 = sum(1 for v in results_phase3.values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase 3 escape rate: {esc_p3}/10 = {esc_p3*10}%", flush=True)

    # Analysis
    print("\n" + "="*70, flush=True)
    print("EXP50b FORMAL RESULTS: COBYLA Compensation Threshold", flush=True)
    print("="*70, flush=True)

    p1_esc = sum(1 for v in phase1_data.values() if v >= ESCAPE_THRESHOLD) if phase1_data else None
    print(f"\nEscape rates (COBYLA iterations per parameter):", flush=True)
    print(f"  Phase 1: p=5, MAX_ITER=30 (3.0 iter/param): {p1_esc}/10 = {p1_esc*10 if p1_esc else '?'}%", flush=True)
    print(f"  Phase 2: p=5, MAX_ITER=50 (5.0 iter/param): {esc_p2}/10 = {esc_p2*10}%", flush=True)
    print(f"  Phase 3: p=3, MAX_ITER=18 (3.0 iter/param): {esc_p3}/10 = {esc_p3*10}%", flush=True)
    print(f"  Reference (Exp49 p=3, MAX_ITER=30, 5.0 iter/param): 10/10 = 100%", flush=True)

    # Verdict
    if phase1_data:
        phase2_increase = esc_p2 - p1_esc
        phase3_decrease = 10 - esc_p3  # how much it decreased from 100%
        h_b = esc_p2 >= p1_esc + 3 and esc_p3 <= 8
        h_depth = abs(esc_p2 - p1_esc) <= 2
        print(f"\nPhase 2 escape change from Phase 1: {'+' if phase2_increase>=0 else ''}{phase2_increase} seeds", flush=True)
        print(f"Phase 3 decrease from reference (p=3/30): {phase3_decrease}/10", flush=True)

        if h_b:
            verdict = "H_B CONFIRMED: Iterations-per-dimension is the causal variable"
            interpretation = f"MAX_ITER=50 restored escape rate ({esc_p2}/10 vs {p1_esc}/10). Depth confounded by budget."
        elif h_depth:
            verdict = "H_DEPTH SUPPORTED: Depth is causal (MAX_ITER change has no effect)"
            interpretation = f"Escape rate unchanged: {esc_p2}/10 at MAX_ITER=50 vs {p1_esc}/10 at MAX_ITER=30"
        else:
            verdict = f"AMBIGUOUS: P2={esc_p2}/10, P3={esc_p3}/10 (partial H_B support)"
            interpretation = "Partial budget effect — may need more extreme MAX_ITER range to confirm"
    else:
        verdict = "PRELIMINARY (no Phase 1 reference)"
        interpretation = f"Phase 2={esc_p2}/10, Phase 3={esc_p3}/10"

    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"INTERPRETATION: {interpretation}", flush=True)

    # Save results
    output = {
        "experiment": "exp50b_cobyla_compensation",
        "author": "Elder C5733",
        "date": "2026-06-08",
        "trigger_condition": "Exp49 H1 NOT confirmed (r<0.60)",
        "settings": {
            "seeds": SEEDS,
            "escape_threshold": ESCAPE_THRESHOLD,
            "shots": SHOTS,
            "phase2": {"p": PHASE2_P, "max_iter": PHASE2_ITER, "iter_per_param": PHASE2_ITER//(2*PHASE2_P)},
            "phase3": {"p": PHASE3_P, "max_iter": PHASE3_ITER, "iter_per_param": PHASE3_ITER//(2*PHASE3_P)},
        },
        "results": {
            "phase1_reuse_exp49": {str(s): phase1_data[str(s)] for s in SEEDS} if phase1_data else None,
            "phase2_p5_iter50": {str(s): results_phase2[s] for s in SEEDS},
            "phase3_p3_iter18": {str(s): results_phase3[s] for s in SEEDS},
        },
        "escape_rates": {
            "phase1_p5_iter30": p1_esc / len(SEEDS) if phase1_data else None,
            "phase2_p5_iter50": esc_p2 / len(SEEDS),
            "phase3_p3_iter18": esc_p3 / len(SEEDS),
            "reference_p3_iter30": 1.0,
        },
        "verdict": verdict,
        "interpretation": interpretation,
        "runtime_seconds": round(time.time() - t0, 1),
    }

    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'experiments', 'exp50b_results.json')
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {outfile}", flush=True)
    print(f"Total runtime: {output['runtime_seconds']}s", flush=True)
