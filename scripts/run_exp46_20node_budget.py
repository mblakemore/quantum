#!/usr/bin/env python3
"""
Exp 46: 20-Node Random Budget Validation — p=[3,4,5,6] H-Gate Budget Sweet Spot Test
Pre-registration: experiments/46-20node-budget-validation-preregistration.md
Whisper C3969 | 2026-06-07

Research question: Does the corrected H-gate budget formula ceil(192/(2n_e)) hold at
20-node scale with a PURE RANDOM topology (no ring+cross structure)?

Finding 21 correction: p_optimal = ceil(192/(2n_e)), not round(). Validated at 8/12/16-node.
This experiment tests whether the correction holds for random (not ring+cross) topology.

Pearl do-operator: do(p=4) on 20-node random — holds topology+size fixed, varies budget.

Graph: 20-node random, numpy seed=46, 30 edges, density=1.5
H-gates per layer: 60
p_optimal = ceil(192/60) = ceil(3.2) = 4 → 240 H-gates

H-gate budget by p:
  p=3: 180H (−6.25% below 192 threshold — expressibility deficit expected)
  p=4: 240H (+25% above 192 — p_optimal per ceil() formula)
  p=5: 300H (+56% — over-budget, gradual decoherence)
  p=6: 360H (+88% — heavily over-budget)
"""
import json
import sys
import time
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

# ─── Graph definitions ──────────────────────────────────────────────────────

# 20-node random graph: numpy seed=46, 30 edges, density=1.5
# Generated: all_pairs = [(i,j) for i<j in range(20)], rng.permutation, take 30
EDGES_20 = [
    (0, 13), (0, 14), (0, 16), (1, 4), (1, 7), (2, 4), (2, 8), (2, 18),
    (3, 4), (3, 6), (3, 13), (3, 15), (3, 16), (4, 7), (4, 14), (5, 15),
    (6, 8), (6, 11), (7, 8), (7, 15), (7, 17), (9, 10), (10, 18), (11, 13),
    (11, 15), (11, 18), (11, 19), (15, 17), (15, 18), (17, 19)
]
N_QUBITS_20 = 20

# H-gate budget analysis
HGATES_PER_LAYER = 2 * len(EDGES_20)   # 60 for 30-edge 20-node graph
SWEET_SPOT_BUDGET = 192
import math
P_OPTIMAL = math.ceil(SWEET_SPOT_BUDGET / HGATES_PER_LAYER)  # ceil(3.2) = 4

# References for comparison
FINDING_20_REFERENCES = {
    'p8_8node':  {'gap': 0.013, 'h_gates': 192, 'nodes': 8},
    'p4_16node': {'gap': 0.086, 'h_gates': 192, 'nodes': 16},
    'p6_12node': {'gap': 0.035, 'h_gates': 216, 'nodes': 12},  # Finding 21 (ring+cross)
}


def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def brute_force_max_cut(n_qubits, edges):
    """Brute force for small graphs. For n=20 this is 2^20 = 1M iterations — takes ~2-5sec."""
    best = 0
    for mask in range(1 << n_qubits):
        bs = format(mask, f'0{n_qubits}b')
        cut = compute_cut_value(bs, edges)
        best = max(best, cut)
    return best


# ─── Circuit builders ────────────────────────────────────────────────────────

def build_standard_qaoa(p, gamma, beta, n_qubits, edges):
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in edges:
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
        for q in range(n_qubits):
            qc.rx(2 * b, q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_xbasis_qaoa(p, gamma, beta, n_qubits, edges):
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        # XX cost operator: H-CX-Rz-CX-H per edge
        for i, j in edges:
            qc.h(i); qc.h(j)
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
            qc.h(i); qc.h(j)
        # Rz mixer
        for q in range(n_qubits):
            qc.rz(2 * b, q)
    # Measure in X basis
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


# ─── Simulation ─────────────────────────────────────────────────────────────

def simulate_circuit(qc, sim, shots=512):
    from qiskit import transpile
    tqc = transpile(qc, sim)
    job = sim.run(tqc, shots=shots)
    return job.result().get_counts()


def evaluate_qaoa(params, build_fn, p, sim, edges, max_cut, n_qubits, shots=512):
    gamma = params[:p]
    beta = params[p:]
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    counts = simulate_circuit(qc, sim, shots=shots)
    total = sum(counts.values())
    expected_cut = sum(
        (count / total) * compute_cut_value(bs, edges)
        for bs, count in counts.items()
    )
    return expected_cut / max_cut


def optimize_qaoa(build_fn, p, sim, edges, max_cut, n_qubits,
                  shots=512, n_restarts=2, max_iter=50):
    best_ratio, best_params = 0, None
    for _ in range(n_restarts):
        x0 = np.random.uniform(0, 2 * np.pi, 2 * p)
        res = minimize(
            lambda x: -evaluate_qaoa(x, build_fn, p, sim, edges, max_cut, n_qubits, shots),
            x0, method='COBYLA',
            options={'maxiter': max_iter, 'rhobeg': 0.5}
        )
        ratio = -res.fun
        if ratio > best_ratio:
            best_ratio, best_params = ratio, res.x
    return best_ratio, best_params


# ─── Main experiment loop ─────────────────────────────────────────────────────

def run_experiment(problem_label, n_qubits, edges, max_cut, p_values, sim,
                   shots=512, n_restarts=2, max_iter=50):
    results = {
        'problem': problem_label,
        'n_qubits': n_qubits,
        'n_edges': len(edges),
        'max_cut': max_cut,
        'p_values': p_values,
        'data': {c: {} for c in ['standard', 'xbasis']}
    }
    circuit_types = [
        ('standard', build_standard_qaoa),
        ('xbasis', build_xbasis_qaoa),
    ]
    for p in p_values:
        h_total = p * HGATES_PER_LAYER
        pct = 100 * h_total / SWEET_SPOT_BUDGET
        marker = " ← SWEET (ceil)" if p == P_OPTIMAL else (
            " ← BELOW THRESHOLD" if h_total < SWEET_SPOT_BUDGET else "")
        print(f"\n  p={p} ({h_total} H-gates, {pct:.0f}% of budget{marker})")
        for circ_name, build_fn in circuit_types:
            t0 = time.time()
            ratio, params = optimize_qaoa(
                build_fn, p, sim, edges, max_cut, n_qubits,
                shots=shots, n_restarts=n_restarts, max_iter=max_iter
            )
            elapsed = time.time() - t0
            results['data'][circ_name][p] = {
                'approx_ratio': round(float(ratio), 4),
                'params': params.tolist() if params is not None else None,
                'time_s': round(elapsed, 1)
            }
            print(f"    {circ_name:10s}: {ratio:.4f}  ({elapsed:.1f}s)")
    return results


def check_goals(results, p_values):
    p_sorted = sorted(p_values)
    std_vals = {p: results['data']['standard'][p]['approx_ratio'] for p in p_sorted if p in results['data']['standard']}
    xbasis_vals = {p: results['data']['xbasis'][p]['approx_ratio'] for p in p_sorted if p in results['data']['xbasis']}
    gaps = {p: std_vals[p] - xbasis_vals[p] for p in p_sorted if p in std_vals and p in xbasis_vals}
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

    # G2: Gap minimum at p=4 (ceil() prediction)
    min_gap_p = min((p for p in p_sorted if p in gaps), key=lambda p: gaps[p])
    goals['G2_min_at_p4'] = min_gap_p == P_OPTIMAL
    goals['G2_min_p'] = min_gap_p
    goals['G2_min_gap'] = round(gaps[min_gap_p], 4)
    goals['G2_p_optimal'] = P_OPTIMAL

    # G3: Asymmetric penalty — gap(p=3) > gap(p=5) by factor > 2
    if 3 in gaps and 5 in gaps:
        ratio_asym = gaps[3] / gaps[5] if gaps[5] > 0 else float('inf')
        goals['G3_asymmetric_penalty'] = gaps[3] > gaps[5] and ratio_asym > 1.5
        goals['G3_gap_p3'] = round(gaps[3], 4)
        goals['G3_gap_p5'] = round(gaps[5], 4)
        goals['G3_asymmetry_ratio'] = round(ratio_asym, 2)

    # G4: gap(p=4) within expected range (0.05-0.12)
    if P_OPTIMAL in gaps:
        goals['G4_gap_in_range'] = 0.05 <= gaps[P_OPTIMAL] <= 0.12
        goals['G4_gap_p_optimal'] = round(gaps[P_OPTIMAL], 4)

    return goals


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Setting up FakeMarrakesh noise model...")
    backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(backend)
    sim = AerSimulator(noise_model=noise_model)

    SHOTS = 512
    N_RESTARTS = 2
    MAX_ITER = 50
    P_VALUES = [3, 4, 5, 6]

    print(f"\nExp46: 20-Node Random Budget Validation (ceil() Formula Test)")
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges, density {len(EDGES_20)/N_QUBITS_20:.1f}")
    print(f"Topology: PURE RANDOM (numpy seed=46) — no ring+cross structure")
    print(f"H-gates per layer: {HGATES_PER_LAYER}")
    print(f"Sweet spot budget: {SWEET_SPOT_BUDGET} H-gates")
    print(f"p_optimal = ceil({SWEET_SPOT_BUDGET}/{HGATES_PER_LAYER}) = {P_OPTIMAL}")
    print(f"H-gate totals: {', '.join(f'p={p}:{p*HGATES_PER_LAYER}H' for p in P_VALUES)}")
    print(f"Parameters: p={P_VALUES}, shots={SHOTS}, restarts={N_RESTARTS}, max_iter={MAX_ITER}")

    print("\nComputing MaxCut (brute force 2^20 = 1M iterations)...")
    t0 = time.time()
    MAX_CUT_20 = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {MAX_CUT_20}  ({time.time()-t0:.1f}s)")

    start_total = time.time()

    print("\n" + "━"*60)
    print("20-NODE RANDOM MAXCUT — p=[3,4,5,6] BUDGET SWEEP")
    print("━"*60)
    results = run_experiment(
        '20-node-random-budget-sweep', N_QUBITS_20, EDGES_20, MAX_CUT_20,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table
    print("\n" + "═"*90)
    print("SUMMARY: Approximation Ratios vs H-Gate Budget (20-node random)")
    print(f"{'p':>4}  {'H-gates':>8}  {'Budget%':>8}  {'Standard':>10}  {'X-basis':>10}  {'Gap':>10}  {'Notes'}")
    for p in P_VALUES:
        if p in results['data']['standard'] and p in results['data']['xbasis']:
            s = results['data']['standard'][p]['approx_ratio']
            x = results['data']['xbasis'][p]['approx_ratio']
            gap = s - x
            h = HGATES_PER_LAYER * p
            pct = 100 * h / SWEET_SPOT_BUDGET
            note = "← CEIL() OPTIMAL" if p == P_OPTIMAL else ("← BELOW THRESHOLD" if h < SWEET_SPOT_BUDGET else "")
            print(f"{p:>4}  {h:>8}  {pct:>7.0f}%  {s:>10.4f}  {x:>10.4f}  {gap:>10.4f}  {note}")

    # References
    print("\nReferences (for cross-size comparison):")
    for label, ref in FINDING_20_REFERENCES.items():
        print(f"  {label}: gap={ref['gap']:.3f} ({ref['h_gates']}H, {ref['nodes']}-node)")

    # Goal evaluation
    print("\n" + "═"*90)
    print("GOAL VERDICTS (Exp46 ceil() formula validation at 20-node):")
    goals = check_goals(results, P_VALUES)

    goal_descriptions = {
        'G1_non_monotone':       'Gap-vs-p non-monotone (budget nonlinearity exists at 20-node)',
        'G2_min_at_p4':          'Gap minimum at p=4 (ceil() formula prediction)',
        'G3_asymmetric_penalty': 'Asymmetric penalty: gap(p=3) > gap(p=5) by >1.5x',
        'G4_gap_in_range':       'gap(p=4) in expected range 0.05–0.12',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals:
            val = goals[goal]
            if isinstance(val, bool):
                print(f"  {goal}: {'PASS ✓' if val else 'FAIL ✗'}  [{desc}]")

    if 'gaps_by_p' in goals:
        print(f"\n  Gap trajectory: {goals['gaps_by_p']}")
    if 'G2_min_p' in goals:
        print(f"  Minimum gap: p={goals['G2_min_p']} gap={goals['G2_min_gap']:.4f} (predicted p={goals['G2_p_optimal']})")
    if 'G3_asymmetry_ratio' in goals:
        print(f"  Asymmetry ratio gap(p=3)/gap(p=5) = {goals['G3_asymmetry_ratio']}x")

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS")

    # Save results
    output = {
        'experiment': 'Exp46',
        'cycle': 'C3969',
        'date': '2026-06-07',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
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
            'density': len(EDGES_20) / N_QUBITS_20
        },
        'results': results,
        'goals': {k: v for k, v in goals.items() if isinstance(v, (bool, float, int, dict, str))},
        'total_runtime_seconds': total_time,
        'references': FINDING_20_REFERENCES,
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp46_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    print("\nExp46 complete.")
