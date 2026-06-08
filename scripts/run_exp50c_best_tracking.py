#!/usr/bin/env python3
"""
Exp50c: COBYLA Best-Tracking Fix — Clean H1_budget Test
Ember C3673 | 2026-06-08

ROOT CAUSE (Ember C3672 code analysis, confirmed):
  optimize_with_cached_circuit tracks best ACROSS restarts only.
  With n_restarts=1, returns res.fun (FINAL COBYLA position).
  COBYLA is non-monotonic: can wander PAST the escape basin.
  Seed 44 proof: MAX_ITER=30 → escaped (0.6442), MAX_ITER=50 → trapped (0.5921).

FIX (optimize_with_cached_circuit_v2):
  Track best-ever WITHIN a COBYLA run via objective wrapper.
  Monotonicity guarantee: more_iters >= fewer_iters always.
  No extra circuit evaluations (tracked inside same objective calls).

DESIGN:
  Same seeds [42-51], same graph (20 qubits, 30 edges)
  Phase A: p=5, MAX_ITER=30 (baseline — same as Exp49, should replicate 30% escape)
  Phase B: p=5, MAX_ITER=50 (clean H1_budget test — COBYLA has 5 iter/param)
  Phase C: p=3, MAX_ITER=30 (replication — should be ~100% escape as per Exp49)

HYPOTHESES:
  H1_budget (iter/param causal): Phase B escape rate > Phase A escape rate
  H2_budget (landscape dominates): Phase B ≈ Phase A escape rate
  Fix validation: Phase A should reproduce Exp49 results (~30% escape, same seeds)

COMPARISON SOURCES:
  Exp49 p=5 results: s42=0.5980[T], s43=0.6391[T], s44=0.6442[E], s45=0.5928[T],
                     s46=0.6376[T], s47=0.6345[T], s48=0.6553[E], s49=0.5867[T],
                     s50=0.6877[E], s51=0.5974[T] → 3/10 = 30% escape
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 256
OPT_LEVEL = 1
ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))

EXP49_P5_DATA = {
    42: 0.5980, 43: 0.6391, 44: 0.6442, 45: 0.5928,
    46: 0.6376, 47: 0.6345, 48: 0.6553, 49: 0.5867,
    50: 0.6877, 51: 0.5974,
}


def optimize_with_cached_circuit_v2(transpiled_qc, gamma_params, beta_params, p,
                                     sim, edges, max_cut, n_qubits, shots, n_restarts, max_iter):
    """COBYLA best-tracking fix (Ember C3673 / Exp50c).

    Wraps the objective function to capture the best-ever ratio seen during
    each COBYLA run. Guarantees monotonicity: more iterations >= fewer iterations.
    No extra circuit evaluations — best tracked inside the same objective calls.
    """
    best_ratio, best_params = 0, None
    for restart in range(n_restarts):
        x0 = np.random.uniform(0, 2 * np.pi, 2 * p)
        best_in_run = [0.0]
        best_x_in_run = [x0.copy()]

        def objective(x):
            r = evaluate_with_transpiled(
                x, transpiled_qc, gamma_params, beta_params,
                p, sim, edges, max_cut, n_qubits, shots)
            if r > best_in_run[0]:
                best_in_run[0] = r
                best_x_in_run[0] = x.copy()
            return -r

        minimize(objective, x0, method='COBYLA',
                 options={'maxiter': max_iter, 'rhobeg': 0.5})

        if best_in_run[0] > best_ratio:
            best_ratio = best_in_run[0]
            best_params = best_x_in_run[0]
    return best_ratio, best_params


def run_single(sim, max_cut, p, seed, max_iter):
    template, gpar, bpar = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
    np.random.seed(seed)
    ratio, _ = optimize_with_cached_circuit_v2(
        tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
        N_QUBITS_20, SHOTS, n_restarts=1, max_iter=max_iter,
    )
    return float(ratio)


if __name__ == '__main__':
    print("Exp50c: COBYLA Best-Tracking Fix — Clean H1_budget Test", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges", flush=True)
    print(f"Seeds: {SEEDS}", flush=True)
    print(f"Escape threshold: {ESCAPE_THRESHOLD}", flush=True)
    print(f"Fix: optimize_with_cached_circuit_v2 (best-ever, not final position)", flush=True)
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))

    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)
    print()

    results = {}

    # Phase A: p=5, MAX_ITER=30 (replication of Exp49 — should match ~30% escape)
    phase_a_label = "A_p5_iter30"
    print(f"=== PHASE A: p=5, MAX_ITER=30 (Exp49 replication with best-tracking) ===", flush=True)
    results[phase_a_label] = {}
    t_start = time.time()
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        ratio = run_single(sim, max_cut, p=5, seed=seed, max_iter=30)
        elapsed = round(time.time() - t0)
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        exp49_val = EXP49_P5_DATA[seed]
        exp49_status = "E" if exp49_val >= ESCAPE_THRESHOLD else "T"
        delta = ratio - exp49_val
        delta_str = f"+{delta:.4f}" if delta >= 0 else f"{delta:.4f}"
        print(f"  [A {i+1:02d}/{len(SEEDS):02d}] p=5 seed={seed} iter=30 ... {ratio:.4f} [{status}]"
              f"  Exp49={exp49_val:.4f}[{exp49_status}] delta={delta_str}  {elapsed}s", flush=True)
        results[phase_a_label][seed] = ratio
    esc_a = sum(1 for v in results[phase_a_label].values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase A escape rate: {esc_a}/10 = {esc_a*10}%  (Exp49 baseline: 30%)", flush=True)
    print(f"Phase A total time: {round(time.time()-t_start)}s", flush=True)
    print()

    # Phase B: p=5, MAX_ITER=50 (H1_budget test — clean with best-tracking)
    phase_b_label = "B_p5_iter50"
    print(f"=== PHASE B: p=5, MAX_ITER=50 (clean H1_budget test) ===", flush=True)
    results[phase_b_label] = {}
    t_start = time.time()
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        ratio = run_single(sim, max_cut, p=5, seed=seed, max_iter=50)
        elapsed = round(time.time() - t0)
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        phase_a_val = results[phase_a_label][seed]
        a_status = "E" if phase_a_val >= ESCAPE_THRESHOLD else "T"
        delta = ratio - phase_a_val
        delta_str = f"+{delta:.4f}" if delta >= 0 else f"{delta:.4f}"
        print(f"  [B {i+1:02d}/{len(SEEDS):02d}] p=5 seed={seed} iter=50 ... {ratio:.4f} [{status}]"
              f"  PhaseA={phase_a_val:.4f}[{a_status}] delta={delta_str}  {elapsed}s", flush=True)
        results[phase_b_label][seed] = ratio
    esc_b = sum(1 for v in results[phase_b_label].values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase B escape rate: {esc_b}/10 = {esc_b*10}%  (H1_budget: should be > Phase A)", flush=True)
    print(f"Phase B total time: {round(time.time()-t_start)}s", flush=True)
    print()

    # Phase C: p=3, MAX_ITER=30 (Exp49 replication — should be ~100% escape)
    phase_c_label = "C_p3_iter30"
    print(f"=== PHASE C: p=3, MAX_ITER=30 (Exp49 p=3 replication, iter/param=5) ===", flush=True)
    results[phase_c_label] = {}
    t_start = time.time()
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        ratio = run_single(sim, max_cut, p=3, seed=seed, max_iter=30)
        elapsed = round(time.time() - t0)
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        print(f"  [C {i+1:02d}/{len(SEEDS):02d}] p=3 seed={seed} iter=30 ... {ratio:.4f} [{status}]"
              f"  {elapsed}s", flush=True)
        results[phase_c_label][seed] = ratio
    esc_c = sum(1 for v in results[phase_c_label].values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase C escape rate: {esc_c}/10 = {esc_c*10}%  (Exp49 p=3 baseline: 100%)", flush=True)
    print(f"Phase C total time: {round(time.time()-t_start)}s", flush=True)
    print()

    # Summary and hypothesis verdict
    print("=" * 65, flush=True)
    print("RESULTS SUMMARY", flush=True)
    print("=" * 65, flush=True)
    print(f"Phase A (p=5, iter=30, best-tracking):  {esc_a}/10 = {esc_a*10}%", flush=True)
    print(f"Phase B (p=5, iter=50, best-tracking):  {esc_b}/10 = {esc_b*10}%", flush=True)
    print(f"Phase C (p=3, iter=30, best-tracking):  {esc_c}/10 = {esc_c*10}%", flush=True)
    print(f"Exp49   (p=5, iter=30, NO best-track):  3/10 = 30% [reference]", flush=True)
    print(flush=True)

    fix_delta_a = esc_a*10 - 30
    fix_str = f"+{fix_delta_a}%" if fix_delta_a >= 0 else f"{fix_delta_a}%"
    print(f"FIX EFFECT (Phase A vs Exp49):           {fix_str} (best-tracking impact)", flush=True)
    print(flush=True)

    if esc_b > esc_a:
        print(f"VERDICT: H1_budget SUPPORTED — iter=50 better than iter=30 ({esc_b*10}% vs {esc_a*10}%)", flush=True)
    elif esc_b == esc_a:
        print(f"VERDICT: H2_budget (landscape) — iter doesn't change escape rate at p=5", flush=True)
    else:
        print(f"VERDICT: ANOMALY — best-tracking still non-monotonic (unexpected)", flush=True)

    # Save results
    out_path = os.path.join(os.path.dirname(__file__), '..', 'findings', 'exp50c_results.json')
    out_data = {
        'experiment': 'exp50c',
        'description': 'COBYLA best-tracking fix — clean H1_budget test',
        'ember_cycle': 3673,
        'escape_threshold': ESCAPE_THRESHOLD,
        'results': {k: {str(s): v for s, v in d.items()} for k, d in results.items()},
        'escape_rates': {
            'phase_a_p5_iter30': esc_a,
            'phase_b_p5_iter50': esc_b,
            'phase_c_p3_iter30': esc_c,
            'exp49_p5_iter30_no_fix': 3,
        },
        'fix_effect_phase_a_vs_exp49': esc_a - 3,
    }
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=2)
    print(f"\nResults saved to: {out_path}", flush=True)
