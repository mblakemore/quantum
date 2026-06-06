#!/usr/bin/env python3
"""
Exp 44-C: H-Gate Budget Isolation Test — 16-Node Random, Extended p Range
Pre-registration: experiments/44c-hgate-budget-isolation-preregistration.md
Elder C5686 | 2026-06-06

H3 Contingency from Ember C3599 adaptive design (Exp43 gap=0.143 ≥ 0.08 → H3 → Exp44-C).

Research question: Is there a gap minimum near p=4 on 16-node random?
H-gate budget hypothesis: 16-node p=4 ≈ 192 H-gates = 8-node p=8 sweet spot budget.

Three circuits compared:
  1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
  2. X-basis QAOA:  XX cost (H-wrapped) + Rz mixer + X-measure
  3. Compiled QAOA: ZZ cost + Rz mixer + X-measure (H gates only at init/measure)

Goals (pre-registered C5686):
  G1: 16-node p=4 gap differs from p=8 gap by ≥15% relative
  G2: Gap-vs-p curve is non-monotone for 16-node random
  G3: Gap minimum (if any) occurs at p ≤ 4 (budget crossover hypothesis)
  G4: X-basis shows anti-plateau behavior (monotone improvement) across p range
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

# 16-node random (same as Exp41 — for direct comparability with Finding 17 data)
EDGES_16 = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0),
    (0,5),(1,9),(2,11),(3,13),(4,8),(6,12),(7,14),(10,15)
]
N_QUBITS_16 = 16

# H-gate budget analysis (x-basis adds 2 H per edge per layer)
HGATES_PER_LAYER = 2 * len(EDGES_16)  # 48 for 24-edge 16-node graph

# Reference results from prior experiments
EXP41_REFERENCE = {
    'p4': {'std': 0.8087, 'xbasis': 0.7338, 'gap': 0.0749},
    'p8': {'std': 0.8405, 'xbasis': 0.7441, 'gap': 0.0964},
}
EXP40_8NODE_SWEET_SPOT = {
    'p8': {'std': 0.8235, 'xbasis': 0.8109, 'gap': 0.0126},
    'hgates_total': 192,  # 24 H/layer × 8 layers
}


def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def brute_force_max_cut(n_qubits, edges):
    """Exact MaxCut via brute force."""
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
        for i, j in edges:
            qc.h(i); qc.h(j)
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
            qc.h(i); qc.h(j)
        for q in range(n_qubits):
            qc.rz(2 * b, q)
    for q in range(n_qubits):
        qc.h(q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_compiled_qaoa(p, gamma, beta, n_qubits, edges):
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in edges:
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
        for q in range(n_qubits):
            qc.rz(2 * b, q)
    for q in range(n_qubits):
        qc.h(q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


# ─── Optimization ────────────────────────────────────────────────────────────

def evaluate_circuit(params, build_fn, p, sim, edges, max_cut, n_qubits, shots):
    gamma = params[:p]
    beta = params[p:]
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    total = sum(counts.values())
    cut_sum = sum(compute_cut_value(bs[::-1], edges) * cnt for bs, cnt in counts.items())
    return -(cut_sum / total) / max_cut


def optimize_qaoa(build_fn, p, sim, edges, max_cut, n_qubits, shots, n_restarts, max_iter):
    best_ratio, best_params = -1, None
    for _ in range(n_restarts):
        x0 = np.random.uniform(0, 2 * np.pi, 2 * p)
        res = minimize(
            evaluate_circuit, x0,
            args=(build_fn, p, sim, edges, max_cut, n_qubits, shots),
            method='COBYLA',
            options={'maxiter': max_iter, 'rhobeg': 0.5}
        )
        ratio = -res.fun
        if ratio > best_ratio:
            best_ratio = ratio
            best_params = res.x
    return best_ratio, best_params


def measure_entropy_at_uniform(build_fn, p, sim, edges, n_qubits, shots=256):
    gamma = np.full(p, np.pi / 4)
    beta = np.full(p, np.pi / 8)
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    total = sum(counts.values())
    probs = np.array([v / total for v in counts.values()])
    return -np.sum(probs * np.log2(probs + 1e-12)) / n_qubits


# ─── Experiment runner ───────────────────────────────────────────────────────

def run_experiment(problem_label, n_qubits, edges, max_cut, p_values, sim,
                   shots=512, n_restarts=2, max_iter=40):
    results = {
        'problem': problem_label,
        'n_qubits': n_qubits,
        'n_edges': len(edges),
        'max_cut': max_cut,
        'p_values': p_values,
        'data': {c: {} for c in ['standard', 'xbasis', 'compiled']}
    }
    circuit_types = [
        ('standard', build_standard_qaoa),
        ('xbasis', build_xbasis_qaoa),
        ('compiled', build_compiled_qaoa),
    ]
    for circuit_name, build_fn in circuit_types:
        print(f"\n  [{circuit_name}]")
        for p in p_values:
            t0 = time.time()
            ratio, params = optimize_qaoa(
                build_fn, p, sim, edges, max_cut, n_qubits,
                shots=shots, n_restarts=n_restarts, max_iter=max_iter
            )
            entropy = measure_entropy_at_uniform(build_fn, p, sim, edges, n_qubits)
            elapsed = time.time() - t0
            results['data'][circuit_name][p] = {
                'approx_ratio': ratio,
                'entropy_uniform': entropy,
                'runtime_s': elapsed
            }
            print(f"    p={p}: ratio={ratio:.4f}, entropy={entropy:.4f}, time={elapsed:.1f}s, H-gates={HGATES_PER_LAYER*p}")
    return results


def check_goals(results):
    d = results['data']
    goals = {}

    # Compute gaps for all p values
    gaps = {}
    for p in results['p_values']:
        if str(p) in d['standard'] or p in d['standard']:
            p_key = p if p in d['standard'] else str(p)
            s = d['standard'][p_key]['approx_ratio']
            x = d['xbasis'][p_key]['approx_ratio']
            gaps[p] = s - x

    goals['gaps_by_p'] = gaps

    # G1: p=4 gap differs from p=8 gap by ≥15% relative
    if 4 in gaps and 8 in gaps:
        relative_diff = abs(gaps[4] - gaps[8]) / gaps[8]
        goals['G1'] = relative_diff >= 0.15
        goals['G1_relative_diff'] = relative_diff
        print(f"  G1: |gap(p=4)-gap(p=8)|/gap(p=8) = {relative_diff:.3f} ({'≥' if relative_diff >= 0.15 else '<'}0.15)")

    # G2: non-monotone gap curve
    if len(gaps) >= 3:
        p_sorted = sorted(gaps.keys())
        gap_vals = [gaps[p] for p in p_sorted]
        increasing = all(gap_vals[i] <= gap_vals[i+1] for i in range(len(gap_vals)-1))
        decreasing = all(gap_vals[i] >= gap_vals[i+1] for i in range(len(gap_vals)-1))
        goals['G2'] = not (increasing or decreasing)
        goals['G2_monotone_type'] = 'monotone_increasing' if increasing else ('monotone_decreasing' if decreasing else 'non_monotone')

    # G3: gap minimum at p ≤ 4 (only if G2 PASS)
    if goals.get('G2', False) and len(gaps) >= 3:
        min_p = min(gaps, key=lambda p: gaps[p])
        goals['G3'] = min_p <= 4
        goals['G3_min_p'] = min_p
        goals['G3_min_gap'] = gaps[min_p]

    # G4: x-basis anti-plateau (monotone improvement across p)
    xbasis_vals = {}
    for p in results['p_values']:
        p_key = p if p in d['xbasis'] else str(p)
        xbasis_vals[p] = d['xbasis'][p_key]['approx_ratio']
    p_sorted = sorted(xbasis_vals.keys())
    goals['G4'] = all(xbasis_vals[p_sorted[i]] <= xbasis_vals[p_sorted[i+1]]
                      for i in range(len(p_sorted)-1))
    goals['G4_xbasis_trajectory'] = {p: xbasis_vals[p] for p in p_sorted}

    return goals


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Exp 44-C: H-Gate Budget Isolation (Elder C5686)            ║")
    print("║  16-Node Random — Extended p Range [1,2,4,8]                ║")
    print("║  H3 Contingency from Ember C3599 Adaptive Design            ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print(f"\nH-gate budget per layer (x-basis): {HGATES_PER_LAYER} H-gates")
    print("Sweet-spot budget: 8-node p=8 = 192 H-gates total")
    print("16-node budget by p:")
    for p in [1, 2, 4, 8]:
        budget = HGATES_PER_LAYER * p
        marker = " ← SWEET SPOT BUDGET" if budget == 192 else ""
        print(f"  p={p}: {budget} H-gates{marker}")

    fake = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake)
    sim = AerSimulator(noise_model=noise_model)

    print(f"\nComputing MaxCut for 16-node random graph...")
    t_mc = time.time()
    MAX_CUT_16 = brute_force_max_cut(N_QUBITS_16, EDGES_16)
    print(f"  MaxCut = {MAX_CUT_16} ({time.time()-t_mc:.2f}s)")

    P_VALUES = [1, 2, 4, 8]
    SHOTS = 512
    N_RESTARTS = 2
    MAX_ITER = 40

    print(f"\nParameters: p={P_VALUES}, shots={SHOTS}, restarts={N_RESTARTS}, max_iter={MAX_ITER}")
    print("Expected runtime: ~15-20 minutes")

    start_total = time.time()

    print("\n" + "━"*60)
    print("16-NODE RANDOM MAXCUT — EXTENDED p SWEEP")
    print("━"*60)
    results = run_experiment(
        '16-node-random-p-sweep', N_QUBITS_16, EDGES_16, MAX_CUT_16,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table with H-gate counts
    print("\n" + "═"*80)
    print("SUMMARY: Approximation Ratios vs H-Gate Budget")
    print(f"{'p':>4}  {'H-gates':>8}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}  {'Gap(S-X)':>10}")
    for p in P_VALUES:
        p_key = p if p in results['data']['standard'] else str(p)
        if p_key in results['data']['standard']:
            s = results['data']['standard'][p_key]['approx_ratio']
            x = results['data']['xbasis'][p_key]['approx_ratio']
            c_val = results['data']['compiled'][p_key]['approx_ratio']
            gap = s - x
            h = HGATES_PER_LAYER * p
            marker = " ←SWEET" if h == 192 else ""
            print(f"{p:>4}  {h:>8}  {s:>10.4f}  {x:>10.4f}  {c_val:>10.4f}  {gap:>+10.4f}{marker}")

    print("\nReference: Exp41 16-node random")
    print(f"  p=4: std={EXP41_REFERENCE['p4']['std']:.4f}, xbasis={EXP41_REFERENCE['p4']['xbasis']:.4f}, gap={EXP41_REFERENCE['p4']['gap']:.4f}")
    print(f"  p=8: std={EXP41_REFERENCE['p8']['std']:.4f}, xbasis={EXP41_REFERENCE['p8']['xbasis']:.4f}, gap={EXP41_REFERENCE['p8']['gap']:.4f}")
    print(f"\nReference: 8-node sweet spot (Exp40)")
    print(f"  p=8: gap=0.0126, H-gate budget=192")

    # Goal evaluation
    print("\n" + "═"*80)
    print("GOAL VERDICTS (Exp44-C H-gate budget hypothesis):")
    goals = check_goals(results)

    goal_descriptions = {
        'G1': 'p=4 gap differs from p=8 gap by ≥15% (depth matters)',
        'G2': 'Gap-vs-p non-monotone (budget nonlinearity exists)',
        'G3': 'Gap minimum at p≤4 (H44-C-A: budget crossover hypothesis)',
        'G4': 'X-basis monotone improvement (barren plateau avoidance robust)',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals:
            val = goals[goal]
            if isinstance(val, bool):
                print(f"  {goal}: {'PASS ✓' if val else 'FAIL ✗'}  [{desc}]")
    if 'gaps_by_p' in goals:
        print(f"\n  Gap trajectory: {goals['gaps_by_p']}")
    if 'G1_relative_diff' in goals:
        print(f"  G1 relative diff: {goals['G1_relative_diff']:.3f}")
    if 'G2_monotone_type' in goals:
        print(f"  G2 curve type: {goals['G2_monotone_type']}")
    if 'G3_min_p' in goals:
        print(f"  G3 minimum at p={goals['G3_min_p']}, gap={goals['G3_min_gap']:.4f}")
    if 'G4_xbasis_trajectory' in goals:
        print(f"  G4 x-basis trajectory: {goals['G4_xbasis_trajectory']}")

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS")

    # Save results
    output = {
        'experiment': 'Exp44C',
        'cycle': 'C5686',
        'date': '2026-06-06',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'hgates_per_layer': HGATES_PER_LAYER,
        'sweet_spot_budget': 192,
        'graph': {
            'n_qubits': N_QUBITS_16,
            'edges': EDGES_16,
            'max_cut': MAX_CUT_16,
            'topology': 'random',
            'density': len(EDGES_16) / N_QUBITS_16
        },
        'results': results,
        'goals': {k: v for k, v in goals.items() if isinstance(v, (bool, float, int, dict, str))},
        'total_runtime_seconds': total_time,
        'references': {
            'exp41_p4_gap': EXP41_REFERENCE['p4']['gap'],
            'exp41_p8_gap': EXP41_REFERENCE['p8']['gap'],
            'sweet_spot_gap': EXP40_8NODE_SWEET_SPOT['p8']['gap'],
        }
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp44c_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    print("\nH3 contingency complete. Exp44-C grading pending results.")
