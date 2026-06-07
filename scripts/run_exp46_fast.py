#!/usr/bin/env python3
"""
Exp46-Fast: 20-Node Random Budget Validation — Optimized Version
Ember C3604 | 2026-06-07

PROBLEM DIAGNOSED IN ORIGINAL Exp46 (run_exp46_20node_budget.py):
  simulate_circuit() calls transpile() inside every COBYLA evaluation.
  For 20 qubits on FakeMarrakesh, SWAP routing is NP-hard → transpile takes
  minutes per call. With n_restarts=2, max_iter=50, 8 combinations:
  up to 800 transpile calls → potential 400+ hour runtime.

FIX: Qiskit ParameterVector pattern (transpile-once):
  1. Build parameterized circuit templates with ParameterVector
  2. Transpile ONCE per (p, circuit_type) combination
  3. Use assign_parameters() in COBYLA loop — no retranspile

Reduced parameters vs original (for practical runtime):
  shots: 512 → 256 (statistical noise acceptable for gap-shape analysis)
  n_restarts: 2 → 1 (single restart sufficient for ratio estimation)
  max_iter: 50 → 30 (converges well before 30 for smooth QAOA landscape)
  optimization_level: default(3) → 1 (moderate routing, not exhaustive)

Expected runtime: ~1-3 hours (vs 400+ hours for original)

Pre-registration: experiments/46-20node-budget-validation-preregistration.md
Science question: Does ceil(192/(2*n_edges)) hold at 20-node pure random topology?
"""
import json
import sys
import time
import math
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

# ─── Graph definitions ───────────────────────────────────────────────────────

# 20-node random graph: numpy seed=46, 30 edges
EDGES_20 = [
    (0, 13), (0, 14), (0, 16), (1, 4), (1, 7), (2, 4), (2, 8), (2, 18),
    (3, 4), (3, 6), (3, 13), (3, 15), (3, 16), (4, 7), (4, 14), (5, 15),
    (6, 8), (6, 11), (7, 8), (7, 15), (7, 17), (9, 10), (10, 18), (11, 13),
    (11, 15), (11, 18), (11, 19), (15, 17), (15, 18), (17, 19)
]
N_QUBITS_20 = 20

HGATES_PER_LAYER = 2 * len(EDGES_20)   # 60 for 30-edge graph
SWEET_SPOT_BUDGET = 192
P_OPTIMAL = math.ceil(SWEET_SPOT_BUDGET / HGATES_PER_LAYER)  # ceil(3.2) = 4

FINDING_20_REFERENCES = {
    'p8_8node':  {'gap': 0.013, 'h_gates': 192, 'nodes': 8},
    'p4_16node': {'gap': 0.086, 'h_gates': 192, 'nodes': 16},
    'p6_12node': {'gap': 0.035, 'h_gates': 216, 'nodes': 12},
}


# ─── Utility ─────────────────────────────────────────────────────────────────

def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def brute_force_max_cut(n_qubits, edges):
    """Brute force for small graphs. For n=20: 2^20=1M iterations, ~2-5sec."""
    best = 0
    for mask in range(1 << n_qubits):
        bs = format(mask, f'0{n_qubits}b')
        cut = compute_cut_value(bs, edges)
        best = max(best, cut)
    return best


# ─── Parameterized circuit builders ─────────────────────────────────────────

def build_parameterized_standard_qaoa(p, n_qubits, edges):
    """Build standard QAOA with ParameterVector — transpile-once compatible."""
    gamma = ParameterVector('γ', p)
    beta = ParameterVector('β', p)
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        for i, j in edges:
            qc.cx(i, j); qc.rz(2 * gamma[layer], j); qc.cx(i, j)
        for q in range(n_qubits):
            qc.rx(2 * beta[layer], q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc, gamma, beta


def build_parameterized_xbasis_qaoa(p, n_qubits, edges):
    """Build x-basis QAOA with ParameterVector — transpile-once compatible."""
    gamma = ParameterVector('γ', p)
    beta = ParameterVector('β', p)
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        for i, j in edges:
            qc.h(i); qc.h(j)
            qc.cx(i, j); qc.rz(2 * gamma[layer], j); qc.cx(i, j)
            qc.h(i); qc.h(j)
        for q in range(n_qubits):
            qc.rz(2 * beta[layer], q)
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc, gamma, beta


# ─── Transpile-once optimization core ───────────────────────────────────────

def evaluate_with_transpiled(params, transpiled_qc, gamma_params, beta_params,
                              p, sim, edges, max_cut, n_qubits, shots):
    """Evaluate QAOA without re-transpiling — just bind parameters and run."""
    gamma_vals = params[:p]
    beta_vals = params[p:]
    assignments = {}
    for i in range(p):
        assignments[gamma_params[i]] = gamma_vals[i]
        assignments[beta_params[i]] = beta_vals[i]
    bound = transpiled_qc.assign_parameters(assignments)
    job = sim.run(bound, shots=shots)
    counts = job.result().get_counts()
    total = sum(counts.values())
    expected_cut = sum(
        (count / total) * compute_cut_value(bs, edges)
        for bs, count in counts.items()
    )
    return expected_cut / max_cut


def optimize_with_cached_circuit(transpiled_qc, gamma_params, beta_params, p,
                                  sim, edges, max_cut, n_qubits, shots, n_restarts, max_iter):
    """COBYLA optimization using pre-transpiled circuit (no re-transpile per eval)."""
    best_ratio, best_params = 0, None
    for restart in range(n_restarts):
        x0 = np.random.uniform(0, 2 * np.pi, 2 * p)
        res = minimize(
            lambda x: -evaluate_with_transpiled(
                x, transpiled_qc, gamma_params, beta_params,
                p, sim, edges, max_cut, n_qubits, shots),
            x0, method='COBYLA',
            options={'maxiter': max_iter, 'rhobeg': 0.5}
        )
        ratio = -res.fun
        if ratio > best_ratio:
            best_ratio, best_params = ratio, res.x
    return best_ratio, best_params


# ─── Main experiment ─────────────────────────────────────────────────────────

def run_experiment_fast(problem_label, n_qubits, edges, max_cut, p_values, sim,
                        shots, n_restarts, max_iter, opt_level):
    results = {
        'problem': problem_label,
        'n_qubits': n_qubits,
        'n_edges': len(edges),
        'max_cut': max_cut,
        'p_values': p_values,
        'data': {'standard': {}, 'xbasis': {}}
    }

    circuit_specs = [
        ('standard', build_parameterized_standard_qaoa),
        ('xbasis',   build_parameterized_xbasis_qaoa),
    ]

    for p in p_values:
        h_total = p * HGATES_PER_LAYER
        pct = 100 * h_total / SWEET_SPOT_BUDGET
        marker = " ← CEIL() SWEET SPOT" if p == P_OPTIMAL else (
            " ← BELOW THRESHOLD" if h_total < SWEET_SPOT_BUDGET else "")
        print(f"\n  p={p} ({h_total} H-gates, {pct:.0f}% of budget{marker})", flush=True)

        for circ_name, build_fn in circuit_specs:
            # TRANSPILE ONCE
            t_trans = time.time()
            template_qc, gamma_params, beta_params = build_fn(p, n_qubits, edges)
            transpiled_qc = transpile(template_qc, sim, optimization_level=opt_level)
            trans_time = time.time() - t_trans
            print(f"    {circ_name:10s}: transpiled in {trans_time:.1f}s "
                  f"(depth={transpiled_qc.depth()})", flush=True)

            # OPTIMIZE (no re-transpile)
            t_opt = time.time()
            ratio, params = optimize_with_cached_circuit(
                transpiled_qc, gamma_params, beta_params, p,
                sim, edges, max_cut, n_qubits, shots, n_restarts, max_iter)
            opt_time = time.time() - t_opt

            results['data'][circ_name][p] = {
                'approx_ratio': round(float(ratio), 4),
                'params': params.tolist() if params is not None else None,
                'transpile_time_s': round(trans_time, 1),
                'optimize_time_s': round(opt_time, 1),
            }
            print(f"    {circ_name:10s}: ratio={ratio:.4f}  "
                  f"(transpile={trans_time:.0f}s, optimize={opt_time:.0f}s)", flush=True)

    return results


def check_goals(results, p_values):
    p_sorted = sorted(p_values)
    std_vals = {p: results['data']['standard'][p]['approx_ratio']
                for p in p_sorted if p in results['data']['standard']}
    xbasis_vals = {p: results['data']['xbasis'][p]['approx_ratio']
                   for p in p_sorted if p in results['data']['xbasis']}
    gaps = {p: std_vals[p] - xbasis_vals[p]
            for p in p_sorted if p in std_vals and p in xbasis_vals}
    gap_list = [gaps[p] for p in p_sorted if p in gaps]

    goals = {}
    goals['gaps_by_p'] = {p: round(gaps[p], 4) for p in p_sorted if p in gaps}
    goals['hgates_by_p'] = {p: p * HGATES_PER_LAYER for p in p_sorted}

    # G1: Non-monotone gap curve
    goals['G1_non_monotone'] = not all(
        gap_list[i] <= gap_list[i+1] for i in range(len(gap_list)-1)
    ) and not all(
        gap_list[i] >= gap_list[i+1] for i in range(len(gap_list)-1)
    )

    # G2: Gap minimum at P_OPTIMAL (ceil formula)
    min_gap_p = min((p for p in p_sorted if p in gaps), key=lambda p: gaps[p])
    goals['G2_min_at_p4'] = min_gap_p == P_OPTIMAL
    goals['G2_min_p'] = min_gap_p
    goals['G2_min_gap'] = round(gaps[min_gap_p], 4)
    goals['G2_p_optimal'] = P_OPTIMAL

    # G3: Asymmetric penalty — gap(p=3) > gap(p=5) by > 1.5x
    if 3 in gaps and 5 in gaps:
        ratio_asym = gaps[3] / gaps[5] if gaps[5] > 0 else float('inf')
        goals['G3_asymmetric_penalty'] = gaps[3] > gaps[5] and ratio_asym > 1.5
        goals['G3_gap_p3'] = round(gaps[3], 4)
        goals['G3_gap_p5'] = round(gaps[5], 4)
        goals['G3_asymmetry_ratio'] = round(ratio_asym, 2)

    # G4: gap(p=4) within expected range
    if P_OPTIMAL in gaps:
        goals['G4_gap_in_range'] = 0.05 <= gaps[P_OPTIMAL] <= 0.12
        goals['G4_gap_p_optimal'] = round(gaps[P_OPTIMAL], 4)

    return goals


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    SHOTS = 256
    N_RESTARTS = 1
    MAX_ITER = 30
    OPT_LEVEL = 1   # moderate transpile (faster than default=3)
    P_VALUES = [3, 4, 5, 6]

    print("Exp46-Fast: 20-Node Random Budget Validation (transpile-once optimization)", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges", flush=True)
    print(f"H-gates/layer: {HGATES_PER_LAYER}, sweet-spot: {SWEET_SPOT_BUDGET}H, "
          f"p_optimal=ceil({SWEET_SPOT_BUDGET}/{HGATES_PER_LAYER})={P_OPTIMAL}", flush=True)
    print(f"Parameters: shots={SHOTS}, restarts={N_RESTARTS}, "
          f"max_iter={MAX_ITER}, opt_level={OPT_LEVEL}", flush=True)
    print(f"FIX: ParameterVector transpile-once pattern (vs 800+ transpiles in original)", flush=True)

    print("\nSetting up FakeMarrakesh noise model...", flush=True)
    backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(backend)
    sim = AerSimulator(noise_model=noise_model)
    print("Backend ready.", flush=True)

    print(f"\nComputing MaxCut (brute force 2^20 = 1M iterations)...", flush=True)
    t0 = time.time()
    MAX_CUT_20 = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {MAX_CUT_20}  ({time.time()-t0:.1f}s)", flush=True)

    start_total = time.time()
    print("\n" + "━"*70, flush=True)
    print("20-NODE RANDOM — p=[3,4,5,6] BUDGET SWEEP (transpile-once)", flush=True)
    print("━"*70, flush=True)

    results = run_experiment_fast(
        '20-node-random-budget-sweep', N_QUBITS_20, EDGES_20, MAX_CUT_20,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS,
        max_iter=MAX_ITER, opt_level=OPT_LEVEL)

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes", flush=True)

    print("\n" + "═"*90, flush=True)
    print("SUMMARY: Approximation Ratios vs H-Gate Budget (20-node random, fast version)", flush=True)
    print(f"{'p':>4}  {'H-gates':>8}  {'Budget%':>8}  {'Standard':>10}  "
          f"{'X-basis':>10}  {'Gap':>10}  {'Notes'}", flush=True)
    for p in P_VALUES:
        if p in results['data']['standard'] and p in results['data']['xbasis']:
            s = results['data']['standard'][p]['approx_ratio']
            x = results['data']['xbasis'][p]['approx_ratio']
            gap = s - x
            h = HGATES_PER_LAYER * p
            pct = 100 * h / SWEET_SPOT_BUDGET
            note = "← CEIL() OPTIMAL" if p == P_OPTIMAL else (
                "← BELOW THRESHOLD" if h < SWEET_SPOT_BUDGET else "")
            print(f"{p:>4}  {h:>8}  {pct:>7.0f}%  {s:>10.4f}  {x:>10.4f}  {gap:>10.4f}  {note}",
                  flush=True)

    print("\nReferences:", flush=True)
    for label, ref in FINDING_20_REFERENCES.items():
        print(f"  {label}: gap={ref['gap']:.3f} ({ref['h_gates']}H, {ref['nodes']}-node)", flush=True)

    goals = check_goals(results, P_VALUES)
    print("\n" + "═"*90, flush=True)
    print("GOAL VERDICTS:", flush=True)
    goal_descriptions = {
        'G1_non_monotone':       'Non-monotone gap curve (budget nonlinearity at 20-node)',
        'G2_min_at_p4':          'Gap minimum at p=4 (ceil() formula prediction)',
        'G3_asymmetric_penalty': 'Asymmetric penalty: gap(p=3) > gap(p=5) by >1.5x',
        'G4_gap_in_range':       'gap(p=4) in expected range 0.05–0.12',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals and isinstance(goals[goal], bool):
            print(f"  {goal}: {'PASS ✓' if goals[goal] else 'FAIL ✗'}  [{desc}]", flush=True)

    if 'gaps_by_p' in goals:
        print(f"\n  Gap trajectory: {goals['gaps_by_p']}", flush=True)
    if 'G2_min_p' in goals:
        print(f"  Min gap: p={goals['G2_min_p']} gap={goals['G2_min_gap']:.4f} "
              f"(predicted p={goals['G2_p_optimal']})", flush=True)
    if 'G3_asymmetry_ratio' in goals:
        print(f"  Asymmetry ratio: {goals['G3_asymmetry_ratio']}x", flush=True)

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS", flush=True)

    output = {
        'experiment': 'Exp46-Fast',
        'cycle': 'C3604',
        'date': '2026-06-07',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'opt_level': OPT_LEVEL,
        'optimization': 'ParameterVector transpile-once (Ember C3604)',
        'p_values': P_VALUES,
        'hgates_per_layer': HGATES_PER_LAYER,
        'sweet_spot_budget': SWEET_SPOT_BUDGET,
        'p_optimal_predicted': P_OPTIMAL,
        'graph': {
            'n_qubits': N_QUBITS_20,
            'edges': EDGES_20,
            'max_cut': MAX_CUT_20,
            'topology': 'random',
            'seed': 46,
            'density': len(EDGES_20) / N_QUBITS_20,
        },
        'results': results,
        'goals': {k: v for k, v in goals.items() if isinstance(v, (bool, float, int, dict, str))},
        'total_runtime_seconds': total_time,
        'references': FINDING_20_REFERENCES,
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp46_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}", flush=True)
    print("\nExp46-Fast complete.", flush=True)
