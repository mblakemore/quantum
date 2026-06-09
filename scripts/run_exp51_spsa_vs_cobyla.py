#!/usr/bin/env python3
"""
Exp51: SPSA vs COBYLA — Optimizer Noise Robustness Test
Ember C3691 | 2026-06-09

Pre-registration: /droid/repos/quantum/experiments/exp51-preregistration.md

HYPOTHESIS:
  H1: SPSA escape rate at p=3, shots=256 >= 80% (outperforms COBYLA 70% baseline)
  H2: SPSA run-to-run variance < COBYLA variance (Phase A/B of Exp50c as reference)
  H3 (optional Phase C): COBYLA shots=1024 escape rate >= 85% (shot-depression hypothesis)

DESIGN:
  Phase A: COBYLA, p=3, MAX_ITER=30, shots=256, seeds 42-51 (control — should reproduce ~70%)
  Phase B: SPSA, p=3, MAX_ITER=50, shots=256, seeds 42-51 (H1/H2 test)
  Phase C: COBYLA, p=3, MAX_ITER=30, shots=1024, seeds 42-51 (H3 test, optional)

ESCAPE_THRESHOLD = 0.640 (consistent with all Exp4x/Exp50x)
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

ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))
OPT_LEVEL = 1

# EXP49 p=3 reference for comparison (from Finding 25)
EXP49_P3_DATA = {
    42: 0.6846, 43: 0.6538, 44: 0.6755, 45: 0.6507,
    46: 0.6839,
    # seeds 47-51: not available for Exp49 p=3
}

# Exp50c Phase C reference (7/10=70%, Ember C3690)
EXP50C_PHASE_C = {
    42: 0.6880, 43: 0.6173, 44: 0.6170, 45: 0.6824,
    46: 0.6134, 47: 0.6833, 48: 0.6783, 49: 0.6854,
    50: 0.6786, 51: 0.6669,
}


# ============================================================
# COBYLA optimizer (V2 best-tracking — same as Exp50c)
# ============================================================
def optimize_cobyla(transpiled_qc, gamma_params, beta_params, p,
                    sim, edges, max_cut, n_qubits, shots, max_iter):
    """COBYLA with best-tracking V2."""
    best_ratio = 0.0
    x0 = np.random.uniform(0, 2 * np.pi, 2 * p)
    best_in_run = [0.0]

    def objective(x):
        r = evaluate_with_transpiled(
            x, transpiled_qc, gamma_params, beta_params,
            p, sim, edges, max_cut, n_qubits, shots)
        if r > best_in_run[0]:
            best_in_run[0] = r
        return -r

    minimize(objective, x0, method='COBYLA',
             options={'maxiter': max_iter, 'rhobeg': 0.5})
    return float(best_in_run[0])


# ============================================================
# SPSA optimizer (Spall 1998 — stochastic gradient approximation)
# ============================================================
def optimize_spsa(transpiled_qc, gamma_params, beta_params, p,
                  sim, edges, max_cut, n_qubits, shots, max_iter,
                  a=0.1, A=10, alpha=0.602, c=0.1, gamma=0.101):
    """
    SPSA with best-tracking.
    Each iteration uses 2 function evaluations (forward + backward perturbation).
    Schedule: a_k = a/(A+k)^alpha, c_k = c/k^gamma (Spall 1998 recommendations).
    Perturbation: Rademacher ±1 for all 2p parameters simultaneously.
    """
    dim = 2 * p
    theta = np.random.uniform(0, 2 * np.pi, dim)
    best_ratio = 0.0
    best_theta = theta.copy()

    for k in range(1, max_iter + 1):
        a_k = a / (A + k) ** alpha
        c_k = c / k ** gamma

        # Rademacher ±1 perturbation vector
        delta = np.random.choice([-1.0, 1.0], size=dim)

        theta_plus  = theta + c_k * delta
        theta_minus = theta - c_k * delta

        # Two stochastic function evaluations
        f_plus = evaluate_with_transpiled(
            theta_plus, transpiled_qc, gamma_params, beta_params,
            p, sim, edges, max_cut, n_qubits, shots)
        f_minus = evaluate_with_transpiled(
            theta_minus, transpiled_qc, gamma_params, beta_params,
            p, sim, edges, max_cut, n_qubits, shots)

        # Gradient estimate (ascending: maximize ratio)
        g_hat = (f_plus - f_minus) / (2 * c_k * delta)

        # Gradient ascent step
        theta = theta + a_k * g_hat

        # Best-tracking
        current = max(f_plus, f_minus)
        if current > best_ratio:
            best_ratio = current
            best_theta = (theta_plus if f_plus > f_minus else theta_minus).copy()

    return float(best_ratio)


# ============================================================
# Shared runner
# ============================================================
def run_cobyla(sim, max_cut, p, seed, max_iter, shots):
    template, gpar, bpar = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
    np.random.seed(seed)
    ratio = optimize_cobyla(
        tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
        N_QUBITS_20, shots, max_iter=max_iter,
    )
    return float(ratio)


def run_spsa(sim, max_cut, p, seed, max_iter, shots):
    template, gpar, bpar = build_parameterized_xbasis_qaoa(p, N_QUBITS_20, EDGES_20)
    tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
    np.random.seed(seed)
    ratio = optimize_spsa(
        tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
        N_QUBITS_20, shots, max_iter=max_iter,
    )
    return float(ratio)


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    # Phase selection via command-line arg (default: run all phases)
    run_phases = sys.argv[1:] if len(sys.argv) > 1 else ['A', 'B']
    if 'all' in run_phases:
        run_phases = ['A', 'B', 'C']

    print("=" * 65, flush=True)
    print("Exp51: SPSA vs COBYLA — Optimizer Noise Robustness Test", flush=True)
    print(f"Ember C3691 | {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}", flush=True)
    print(f"Phases: {run_phases}", flush=True)
    print("=" * 65, flush=True)
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)
    print()

    results = {}

    # ---- Phase A: COBYLA control (should reproduce Exp50c Phase C ~70%) ----
    if 'A' in run_phases:
        print("=== PHASE A: COBYLA p=3, MAX_ITER=30, shots=256 (control) ===", flush=True)
        phase_a = {}
        a_escaped = 0
        for i, seed in enumerate(SEEDS, 1):
            t0 = time.time()
            ratio = run_cobyla(sim, max_cut, p=3, seed=seed, max_iter=30, shots=256)
            elapsed = time.time() - t0
            escaped = ratio >= ESCAPE_THRESHOLD
            status = 'ESCAPED' if escaped else 'trapped'
            if escaped:
                a_escaped += 1
            ref = EXP50C_PHASE_C.get(seed, None)
            ref_str = f"Exp50c={ref:.4f}[{'E' if ref and ref >= ESCAPE_THRESHOLD else 'T'}]" if ref else "Exp50c=N/A"
            print(f"  [A {i:02d}/10] p=3 seed={seed} iter=30 shots=256 ... "
                  f"{ratio:.4f} [{status}]  {ref_str}  {elapsed:.0f}s", flush=True)
            phase_a[seed] = ratio

        print(f"\nPhase A escape rate: {a_escaped}/10 = {a_escaped*10}%  "
              f"(Exp50c Phase C baseline: 70%)", flush=True)
        results['phase_a'] = {'data': phase_a, 'escaped': a_escaped, 'rate': a_escaped / 10}
        print()

    # ---- Phase B: SPSA test (H1: SPSA >= 80%?) ----
    if 'B' in run_phases:
        print("=== PHASE B: SPSA p=3, MAX_ITER=50, shots=256 (H1 test) ===", flush=True)
        print("    (Each iteration = 2 function evals. Max evals = 100.)", flush=True)
        phase_b = {}
        b_escaped = 0
        for i, seed in enumerate(SEEDS, 1):
            t0 = time.time()
            ratio = run_spsa(sim, max_cut, p=3, seed=seed, max_iter=50, shots=256)
            elapsed = time.time() - t0
            escaped = ratio >= ESCAPE_THRESHOLD
            status = 'ESCAPED' if escaped else 'trapped'
            if escaped:
                b_escaped += 1
            ref_a = results.get('phase_a', {}).get('data', {}).get(seed, None)
            ref_str = f"PhaseA={ref_a:.4f}[{'E' if ref_a and ref_a >= ESCAPE_THRESHOLD else 'T'}]" if ref_a else "PhaseA=N/A"
            print(f"  [B {i:02d}/10] p=3 seed={seed} iter=50 shots=256 ... "
                  f"{ratio:.4f} [{status}]  {ref_str}  {elapsed:.0f}s", flush=True)
            phase_b[seed] = ratio

        print(f"\nPhase B (SPSA) escape rate: {b_escaped}/10 = {b_escaped*10}%  "
              f"(H1: >= 80% = CONFIRMED, 65-79% = PARTIAL, <= 64% = REFUTED)", flush=True)
        results['phase_b'] = {'data': phase_b, 'escaped': b_escaped, 'rate': b_escaped / 10}
        print()

    # ---- Phase C: COBYLA shots=1024 (H3 test — optional) ----
    if 'C' in run_phases:
        print("=== PHASE C: COBYLA p=3, MAX_ITER=30, shots=1024 (H3 test) ===", flush=True)
        print("    (4x shot count — each seed ~2700s estimate)", flush=True)
        phase_c = {}
        c_escaped = 0
        for i, seed in enumerate(SEEDS, 1):
            t0 = time.time()
            ratio = run_cobyla(sim, max_cut, p=3, seed=seed, max_iter=30, shots=1024)
            elapsed = time.time() - t0
            escaped = ratio >= ESCAPE_THRESHOLD
            status = 'ESCAPED' if escaped else 'trapped'
            if escaped:
                c_escaped += 1
            ref_a = results.get('phase_a', {}).get('data', {}).get(seed, None)
            ref_str = f"PhaseA={ref_a:.4f}[{'E' if ref_a and ref_a >= ESCAPE_THRESHOLD else 'T'}]" if ref_a else "PhaseA=N/A"
            print(f"  [C {i:02d}/10] p=3 seed={seed} iter=30 shots=1024 ... "
                  f"{ratio:.4f} [{status}]  {ref_str}  {elapsed:.0f}s", flush=True)
            phase_c[seed] = ratio

        print(f"\nPhase C (shots=1024) escape rate: {c_escaped}/10 = {c_escaped*10}%  "
              f"(H3: >= 85% = CONFIRMED strong, 75-84% = CONFIRMED weak, <= 74% = REFUTED)", flush=True)
        results['phase_c'] = {'data': phase_c, 'escaped': c_escaped, 'rate': c_escaped / 10}
        print()

    # ---- Summary ----
    print("=" * 65, flush=True)
    print("EXP51 SUMMARY", flush=True)
    print("=" * 65, flush=True)
    if 'phase_a' in results:
        pa = results['phase_a']
        print(f"Phase A (COBYLA, p=3, 30iter, shots=256):  {pa['escaped']}/10 = {pa['rate']*100:.0f}%  "
              f"(Exp50c baseline: 70%)", flush=True)
    if 'phase_b' in results:
        pb = results['phase_b']
        print(f"Phase B (SPSA, p=3, 50iter, shots=256):    {pb['escaped']}/10 = {pb['rate']*100:.0f}%  "
              f"(H1 threshold: >= 80%)", flush=True)
    if 'phase_c' in results:
        pc = results['phase_c']
        print(f"Phase C (COBYLA, p=3, 30iter, shots=1024): {pc['escaped']}/10 = {pc['rate']*100:.0f}%  "
              f"(H3 threshold: >= 85%)", flush=True)

    # H1 verdict
    if 'phase_b' in results:
        pb = results['phase_b']
        if pb['rate'] >= 0.80:
            verdict_h1 = "H1 CONFIRMED: SPSA outperforms COBYLA — algorithm design matters"
        elif pb['rate'] >= 0.65:
            verdict_h1 = "H1 PARTIAL: Marginal SPSA improvement — shot-noise dominant"
        else:
            verdict_h1 = "H1 REFUTED: SPSA no better than COBYLA — landscape-determined floor"
        print(f"\nVERDICT H1: {verdict_h1}", flush=True)

    # H3 verdict
    if 'phase_c' in results:
        pc = results['phase_c']
        if pc['rate'] >= 0.85:
            verdict_h3 = "H3 CONFIRMED (strong): More shots substantially raise rate — shot-depression real"
        elif pc['rate'] >= 0.75:
            verdict_h3 = "H3 CONFIRMED (weak): Modest improvement from more shots"
        else:
            verdict_h3 = "H3 REFUTED: More shots don't help — algorithm is bottleneck"
        print(f"VERDICT H3: {verdict_h3}", flush=True)

    # Save results JSON
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '..', 'results', 'exp51_results.json')
    with open(out_path, 'w') as f:
        json.dump({
            'experiment': 'Exp51',
            'source': 'Ember C3691',
            'date': time.strftime('%Y-%m-%d', time.gmtime()),
            'config': {'escape_threshold': ESCAPE_THRESHOLD, 'seeds': SEEDS},
            'results': results
        }, f, indent=2)
    print(f"\nResults saved to: {out_path}", flush=True)
    print("Exp51 COMPLETE.", flush=True)
