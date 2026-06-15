#!/usr/bin/env python3
"""
Exp50c Phase B+C Continuation — Ember C3686
Resumes from where PID 830493 was killed by Creator (Whisper preserved partial output aecf045).

KNOWN COMPLETED:
  Phase A: ALL 10 seeds done (4/10 = 40% escape)
  Phase B: seeds 42-46 done (2/5 = 40% escape at halfway)

THIS SCRIPT RUNS:
  Phase B: seeds 47-51 (5 remaining seeds)
  Phase C: ALL 10 seeds (p=3, MAX_ITER=30)

PHASE A results (hard-coded from exp50c_output_partial_C4047.txt):
  s42=0.6492[E], s43=0.5928[T], s44=0.6785[E], s45=0.6079[T]
  s46=0.6300[T], s47=0.6206[T], s48=0.5882[T], s49=0.6902[E]
  s50=0.6840[E], s51=0.6531[E]  → 4/10 = 40% escape

PHASE B partial (seeds 42-46, hard-coded):
  s42=0.5930[T], s43=0.6824[E], s44=0.5972[T], s45=0.6074[T], s46=0.6702[E]
  → 2/5 = 40% at halfway

H1_budget: Phase B (iter=50) > Phase A (iter=30) escape rate?
H2_budget: escape rates similar (landscape dominates)?
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
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 256
OPT_LEVEL = 1
ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))

# Hard-coded from partial output (Phase A complete, Phase B seeds 42-46)
PHASE_A_RESULTS = {
    42: 0.6492, 43: 0.5928, 44: 0.6785, 45: 0.6079, 46: 0.6300,
    47: 0.6206, 48: 0.5882, 49: 0.6902, 50: 0.6840, 51: 0.6531,
}

PHASE_B_PARTIAL = {
    42: 0.5930, 43: 0.6824, 44: 0.5972, 45: 0.6074, 46: 0.6702,
}  # seeds 42-46 already done

# Phase B remaining seeds
PHASE_B_REMAINING = [s for s in SEEDS if s not in PHASE_B_PARTIAL]  # [47, 48, 49, 50, 51]

EXP49_P5_DATA = {
    42: 0.5980, 43: 0.6391, 44: 0.6442, 45: 0.5928,
    46: 0.6376, 47: 0.6345, 48: 0.6553, 49: 0.5867,
    50: 0.6877, 51: 0.5974,
}


def optimize_with_cached_circuit_v2(transpiled_qc, gamma_params, beta_params, p,
                                     sim, edges, max_cut, n_qubits, shots, n_restarts, max_iter):
    """COBYLA best-tracking fix — same as run_exp50c_best_tracking.py."""
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
    print("Exp50c Phase B+C Continuation — Ember C3686", flush=True)
    print("Resuming from PID 830493 kill (Whisper C4047 preservation)", flush=True)
    print(f"Phase A: DONE 4/10 = 40% escape (hard-coded)", flush=True)
    print(f"Phase B: seeds 42-46 DONE 2/5 partial, running seeds {PHASE_B_REMAINING}", flush=True)
    print(f"Phase C: ALL 10 seeds pending (p=3, MAX_ITER=30)", flush=True)
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))

    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)
    print()

    # === Phase B continuation (seeds 47-51) ===
    phase_b_results = dict(PHASE_B_PARTIAL)  # start with known results

    esc_b_partial = sum(1 for v in PHASE_B_PARTIAL.values() if v >= ESCAPE_THRESHOLD)
    print(f"=== PHASE B CONTINUATION: seeds 47-51 (p=5, MAX_ITER=50) ===", flush=True)
    print(f"  (Seeds 42-46 hard-coded: {esc_b_partial}/5 escaped)", flush=True)

    for seed in PHASE_B_REMAINING:
        i = SEEDS.index(seed)
        t0 = time.time()
        ratio = run_single(sim, max_cut, p=5, seed=seed, max_iter=50)
        elapsed = round(time.time() - t0)
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        phase_a_val = PHASE_A_RESULTS[seed]
        a_status = "E" if phase_a_val >= ESCAPE_THRESHOLD else "T"
        delta = ratio - phase_a_val
        delta_str = f"+{delta:.4f}" if delta >= 0 else f"{delta:.4f}"
        print(f"  [B {i+1:02d}/10] p=5 seed={seed} iter=50 ... {ratio:.4f} [{status}]"
              f"  PhaseA={phase_a_val:.4f}[{a_status}] delta={delta_str}  {elapsed}s", flush=True)
        phase_b_results[seed] = ratio

    esc_b = sum(1 for v in phase_b_results.values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase B escape rate: {esc_b}/10 = {esc_b*10}%  (Phase A: 40%, H1_budget: should exceed)", flush=True)
    print(f"  [2/5 from partial + {esc_b - esc_b_partial}/5 from continuation = {esc_b}/10]", flush=True)
    print()

    # === Phase C (p=3, MAX_ITER=30) — all 10 seeds ===
    phase_c_results = {}
    print(f"=== PHASE C: p=3, MAX_ITER=30 (Exp49 replication — expected ~100% escape) ===", flush=True)
    t_start = time.time()
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        ratio = run_single(sim, max_cut, p=3, seed=seed, max_iter=30)
        elapsed = round(time.time() - t0)
        status = "ESCAPED" if ratio >= ESCAPE_THRESHOLD else "trapped"
        print(f"  [C {i+1:02d}/10] p=3 seed={seed} iter=30 ... {ratio:.4f} [{status}]  {elapsed}s", flush=True)
        phase_c_results[seed] = ratio

    esc_c = sum(1 for v in phase_c_results.values() if v >= ESCAPE_THRESHOLD)
    print(f"\nPhase C escape rate: {esc_c}/10 = {esc_c*10}%  (Exp49 p=3 baseline: 100%)", flush=True)
    print(f"Phase C total time: {round(time.time()-t_start)}s", flush=True)
    print()

    # === COMBINED SUMMARY ===
    esc_a = sum(1 for v in PHASE_A_RESULTS.values() if v >= ESCAPE_THRESHOLD)  # 4
    print("=" * 65, flush=True)
    print("EXP50C COMPLETE — RESULTS SUMMARY", flush=True)
    print("=" * 65, flush=True)
    print(f"Phase A (p=5, iter=30, best-tracking):  {esc_a}/10 = {esc_a*10}%", flush=True)
    print(f"Phase B (p=5, iter=50, best-tracking):  {esc_b}/10 = {esc_b*10}%", flush=True)
    print(f"Phase C (p=3, iter=30, best-tracking):  {esc_c}/10 = {esc_c*10}%", flush=True)
    print(f"Exp49   (p=5, iter=30, NO best-track):  3/10 = 30% [reference]", flush=True)
    print(flush=True)

    fix_delta = esc_a - 3
    fix_str = f"+{fix_delta}0%" if fix_delta >= 0 else f"{fix_delta}0%"
    print(f"FIX EFFECT (Phase A vs Exp49):           {fix_str} (best-tracking alone)", flush=True)
    print(flush=True)

    if esc_b > esc_a:
        print(f"VERDICT: H1_budget SUPPORTED — iter=50 better ({esc_b*10}% vs {esc_a*10}%)", flush=True)
        print(f"  More COBYLA budget DOES increase escape rate at p=5 on this landscape", flush=True)
    elif esc_b == esc_a:
        print(f"VERDICT: H2_budget (landscape dominates) — iter doesn't change escape rate", flush=True)
        print(f"  Budget is NOT the limiting factor; landscape structure is", flush=True)
    else:
        print(f"VERDICT: ANOMALY — Phase B < Phase A despite best-tracking monotonicity", flush=True)
        print(f"  Investigate: initialization variance or theta_init reproducibility issue?", flush=True)

    print(flush=True)

    # Save complete results
    out_path = os.path.join(os.path.dirname(__file__), '..', 'findings', 'exp50c_results.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out_data = {
        'experiment': 'exp50c_continuation',
        'description': 'COBYLA best-tracking fix — clean H1_budget test (C3673 design, C3686 continuation)',
        'ember_cycle_design': 3673,
        'ember_cycle_continuation': 3686,
        'whisper_preservation_cycle': 4047,
        'escape_threshold': ESCAPE_THRESHOLD,
        'phase_a_note': 'Complete from original run (PID 830493), hard-coded',
        'phase_b_note': 'Seeds 42-46 from partial output, seeds 47-51 from this run',
        'results': {
            'A_p5_iter30': {str(s): v for s, v in PHASE_A_RESULTS.items()},
            'B_p5_iter50': {str(s): v for s, v in sorted(phase_b_results.items())},
            'C_p3_iter30': {str(s): v for s, v in phase_c_results.items()},
        },
        'escape_rates': {
            'phase_a_p5_iter30': esc_a,
            'phase_b_p5_iter50': esc_b,
            'phase_c_p3_iter30': esc_c,
            'exp49_p5_iter30_no_fix': 3,
        },
        'fix_effect_phase_a_vs_exp49': esc_a - 3,
        'h1_budget_verdict': 'SUPPORTED' if esc_b > esc_a else ('INCONCLUSIVE' if esc_b == esc_a else 'ANOMALY'),
    }
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=2)
    print(f"Results saved to: {out_path}", flush=True)
    print("Exp50c COMPLETE.", flush=True)
