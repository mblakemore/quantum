#!/usr/bin/env python3
"""
Exp 45: 12-Node Budget Validation — p=[4,5,6,8] H-Gate Budget Sweet Spot Test
Pre-registration: experiments/45-12node-budget-validation-preregistration.md
Whisper C3968 | 2026-06-06

Research question: Does the H-gate budget sweet spot (~192) apply at 12-node scale?
Finding 18 used p=8 (288 H-gates — over-budget). Scaling rule (Finding 20) predicts
p_optimal = round(192/36) = 5 (180 H-gates) should give smaller gap.

Pearl do-operator: do(p=5) on 12-node random — holds topology+size fixed, varies budget.

Three circuits compared:
  1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
  2. X-basis QAOA:  XX cost (H-wrapped) + Rz mixer + X-measure
  3. Compiled QAOA: ZZ cost + Rz mixer + X-measure (reference)

Goals (pre-registered C3968):
  G1: Gap-vs-p curve non-monotone (budget nonlinearity exists at 12-node)
  G2: Gap minimum at p=5 or p=6 (budget sweet spot in range)
  G3: gap(p=5) < gap(p=8)=0.080 (budget rule reduces gap vs Finding 18)
  G4: Finding 18 replication: gap(p=8) within 15% of 0.080 (0.068–0.092)
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

# 12-node: ring + cross connections (18 edges, density 1.5 — same as Exp42/Finding 18)
EDGES_12 = [
    # Ring (12 edges)
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),(11,0),
    # Cross connections (6 edges)
    (0,4),(1,7),(2,9),(3,6),(5,10),(8,11)
]
N_QUBITS_12 = 12

# H-gate budget analysis (x-basis adds 2 H per edge per layer)
HGATES_PER_LAYER = 2 * len(EDGES_12)  # 36 for 18-edge 12-node graph
SWEET_SPOT_BUDGET = 192
P_OPTIMAL = round(SWEET_SPOT_BUDGET / HGATES_PER_LAYER)  # = 5

# Reference from Finding 18 (Exp42 p=8)
FINDING_18_REFERENCE = {
    'p8': {'std': 0.8357, 'xbasis': 0.7560, 'gap': 0.0797}
}
# Reference from Finding 20 (Exp44-C 16-node sweet spot at p=4)
FINDING_20_REFERENCE = {
    'p4_16node': {'std': 0.8131, 'xbasis': 0.7269, 'gap': 0.0861, 'hgates': 192}
}


def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def brute_force_max_cut(n_qubits, edges):
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
    # Init: |+> state
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
    # Measure in X basis: H before measure
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_compiled_qaoa(p, gamma, beta, n_qubits, edges):
    """Compiled: ZZ cost + Rz mixer + X-measure (H only at init + final measure)."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in edges:
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
        for q in range(n_qubits):
            qc.rz(2 * b, q)
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
                  shots=512, n_restarts=2, max_iter=40):
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
    for p in p_values:
        h_total = p * HGATES_PER_LAYER
        marker = " ← SWEET SPOT" if abs(h_total - SWEET_SPOT_BUDGET) <= HGATES_PER_LAYER else ""
        print(f"\n  p={p} ({h_total} H-gates{marker})")
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


def check_goals(results):
    p_sorted = sorted(results['p_values'])
    std_vals = {p: results['data']['standard'][p]['approx_ratio'] for p in p_sorted}
    xbasis_vals = {p: results['data']['xbasis'][p]['approx_ratio'] for p in p_sorted}
    gaps = {p: std_vals[p] - xbasis_vals[p] for p in p_sorted}
    gap_list = [gaps[p] for p in p_sorted]

    goals = {}
    goals['gaps_by_p'] = {p: round(gaps[p], 4) for p in p_sorted}

    # G1: Non-monotone gap curve
    goals['G1_non_monotone'] = not all(
        gap_list[i] <= gap_list[i+1] for i in range(len(gap_list)-1)
    ) and not all(
        gap_list[i] >= gap_list[i+1] for i in range(len(gap_list)-1)
    )

    # G2: Gap minimum at p=5 or p=6
    min_gap_p = min(p_sorted, key=lambda p: gaps[p])
    goals['G2_min_at_budget_p'] = min_gap_p in [5, 6]
    goals['G2_min_p'] = min_gap_p
    goals['G2_min_gap'] = round(gaps[min_gap_p], 4)

    # G3: gap(p=5) < gap(p=8) = 0.080
    if 5 in gaps and 8 in gaps:
        goals['G3_budget_beats_p8'] = gaps[5] < gaps[8]
        goals['G3_gap_p5'] = round(gaps[5], 4)
        goals['G3_gap_p8'] = round(gaps[8], 4)
    elif 5 in gaps:
        goals['G3_budget_beats_p8'] = gaps[5] < 0.080
        goals['G3_gap_p5'] = round(gaps[5], 4)

    # G4: Finding 18 replication — gap(p=8) within 15% of 0.080
    if 8 in gaps:
        ref_gap = FINDING_18_REFERENCE['p8']['gap']
        goals['G4_finding18_replicated'] = abs(gaps[8] - ref_gap) / ref_gap <= 0.15
        goals['G4_gap_p8'] = round(gaps[8], 4)
        goals['G4_finding18_ref'] = ref_gap

    # X-basis trajectory
    goals['G4_xbasis_trajectory'] = {p: round(xbasis_vals[p], 4) for p in p_sorted}

    return goals


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Setting up FakeMarrakesh noise model...")
    backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(backend)
    sim = AerSimulator(noise_model=noise_model)

    SHOTS = 512
    N_RESTARTS = 2
    MAX_ITER = 40
    P_VALUES = [4, 5, 6, 8]

    print(f"\nExp45: 12-Node Budget Validation")
    print(f"Graph: {N_QUBITS_12} qubits, {len(EDGES_12)} edges, density {len(EDGES_12)/N_QUBITS_12:.1f}")
    print(f"H-gates per layer: {HGATES_PER_LAYER}")
    print(f"Sweet spot budget: {SWEET_SPOT_BUDGET} H-gates → p_optimal = {P_OPTIMAL}")
    print(f"H-gate totals by p: { {p: p*HGATES_PER_LAYER for p in P_VALUES} }")
    print(f"Reference (Finding 18): 12-node p=8 gap={FINDING_18_REFERENCE['p8']['gap']}")
    print(f"Parameters: p={P_VALUES}, shots={SHOTS}, restarts={N_RESTARTS}, max_iter={MAX_ITER}")

    print("\nComputing MaxCut (brute force)...")
    MAX_CUT_12 = brute_force_max_cut(N_QUBITS_12, EDGES_12)
    print(f"MaxCut = {MAX_CUT_12}")

    start_total = time.time()

    print("\n" + "━"*60)
    print("12-NODE RANDOM MAXCUT — p=[4,5,6,8] BUDGET SWEEP")
    print("━"*60)
    results = run_experiment(
        '12-node-budget-sweep', N_QUBITS_12, EDGES_12, MAX_CUT_12,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table
    print("\n" + "═"*85)
    print("SUMMARY: Approximation Ratios vs H-Gate Budget")
    print(f"{'p':>4}  {'H-gates':>8}  {'Budget%':>8}  {'Standard':>10}  {'X-basis':>10}  {'Gap(S-X)':>10}")
    for p in P_VALUES:
        if p in results['data']['standard']:
            s = results['data']['standard'][p]['approx_ratio']
            x = results['data']['xbasis'][p]['approx_ratio']
            gap = s - x
            h = HGATES_PER_LAYER * p
            pct = 100 * h / SWEET_SPOT_BUDGET
            marker = " ← SWEET" if p == P_OPTIMAL else ""
            print(f"{p:>4}  {h:>8}  {pct:>7.0f}%  {s:>10.4f}  {x:>10.4f}  {gap:>+10.4f}{marker}")

    print(f"\nReference (Finding 18): 12-node p=8: std={FINDING_18_REFERENCE['p8']['std']:.4f}, "
          f"xbasis={FINDING_18_REFERENCE['p8']['xbasis']:.4f}, gap={FINDING_18_REFERENCE['p8']['gap']:.4f}")
    print(f"Reference (Finding 20): 16-node p=4 (192 H): gap={FINDING_20_REFERENCE['p4_16node']['gap']:.4f}")

    # Goal evaluation
    print("\n" + "═"*85)
    print("GOAL VERDICTS (Exp45 H-gate budget validation):")
    goals = check_goals(results)

    goal_descriptions = {
        'G1_non_monotone': 'Gap-vs-p non-monotone (budget nonlinearity exists at 12-node)',
        'G2_min_at_budget_p': 'Gap minimum at p=5 or p=6 (budget sweet spot in range)',
        'G3_budget_beats_p8': 'gap(p=5) < gap(p=8)=0.080 (budget rule reduces gap vs Finding 18)',
        'G4_finding18_replicated': 'gap(p=8) within 15% of Finding 18 result (0.080)',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals:
            val = goals[goal]
            if isinstance(val, bool):
                print(f"  {goal}: {'PASS ✓' if val else 'FAIL ✗'}  [{desc}]")

    if 'gaps_by_p' in goals:
        print(f"\n  Gap trajectory: {goals['gaps_by_p']}")
    if 'G2_min_p' in goals:
        print(f"  Minimum gap at p={goals['G2_min_p']}: {goals['G2_min_gap']:.4f}")
    if 'G4_xbasis_trajectory' in goals:
        print(f"  X-basis trajectory: {goals['G4_xbasis_trajectory']}")

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS")

    # Save results
    output = {
        'experiment': 'Exp45',
        'cycle': 'C3968',
        'date': '2026-06-06',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'hgates_per_layer': HGATES_PER_LAYER,
        'sweet_spot_budget': SWEET_SPOT_BUDGET,
        'p_optimal_predicted': P_OPTIMAL,
        'graph': {
            'n_qubits': N_QUBITS_12,
            'edges': EDGES_12,
            'max_cut': MAX_CUT_12,
            'topology': 'ring_plus_cross',
            'density': len(EDGES_12) / N_QUBITS_12
        },
        'results': results,
        'goals': {k: v for k, v in goals.items() if isinstance(v, (bool, float, int, dict, str))},
        'total_runtime_seconds': total_time,
        'references': {
            'finding18_p8_gap': FINDING_18_REFERENCE['p8']['gap'],
            'finding20_16node_p4_gap': FINDING_20_REFERENCE['p4_16node']['gap'],
        }
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp45_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    print("\nExp45 complete. Budget rule validation pending analysis.")
