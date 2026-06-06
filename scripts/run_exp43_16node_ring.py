#!/usr/bin/env python3
"""
Exp 43: 16-Node RING Topology — Pearl Causal Topology Test
Pre-registration: experiments/43-16node-ring-topology-preregistration.md
Whisper C3967 | 2026-06-06

Research question: Does 16-node RING topology restore x-basis competitive advantage?
Finding 18 (Elder C5685): gap tracks inverse of standard QAOA plateau severity.
Whisper C3966 Pearl prediction: crossover is topology+depth-driven, NOT purely size-driven.
do(topology=ring) test: P(gap | do(topology=ring), size=16)

Three circuits compared (same as Exp41/42):
  1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
  2. X-basis QAOA:  XX cost (H-wrapped) + Rz mixer + X-measure
  3. Compiled QAOA: ZZ cost + Rz mixer + X-measure (H gates only at init/measure)

Goals (pre-registered C3967):
  G1: Ring gap at p=8 < 0.096 (topology effect confirmed vs random-16)
  G2: Standard QAOA plateaus on ring at p=8 (p=8 ratio < p=4 ratio)
  G3: Ring gap at p=8 < 0.05 (H1: strong topology effect, sweet spot restored)
  G4: X-basis anti-plateau protection holds on ring (xbasis p=8 > p=4)
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

# 16-node RING (Exp43 — topology test): degree=2, density=1.0 edges/node
EDGES_16_RING = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0)
]
N_QUBITS_16_RING = 16
# MaxCut = 8 (alternating partition: even vs odd nodes)

# Reference: 16-node random (Exp41, for gap comparison)
# Results: std p=8=0.836, xbasis p=8=0.740, gap=0.096
RANDOM_16_REFERENCE = {'std_p8': 0.8357, 'xbasis_p8': 0.7560, 'gap_p8': 0.0797}
# Note: Using Exp42-validated data (Elder C5685 confirmed 0.096 for Exp41)

# 4-node ring reference (Exp40, for structural analogy)
# Results: std p=8=0.824, xbasis p=8=0.811, gap=0.013...
# Wait, Exp40 4-node ring: std=0.9395, xbasis=0.7836 at p=4; std=0.8235, xbasis=0.8109 at p=8
# Gap = 0.0126 at p=8, 0.1559 at p=4
RING_4_REFERENCE = {
    'std_p4': 0.9395, 'xbasis_p4': 0.7836, 'gap_p4': 0.1559,
    'std_p8': 0.8235, 'xbasis_p8': 0.8109, 'gap_p8': 0.0126
}


def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def brute_force_max_cut(n_qubits, edges):
    """Exact MaxCut via brute force. For ring: MaxCut = n/2."""
    best = 0
    for mask in range(1 << n_qubits):
        bs = format(mask, f'0{n_qubits}b')
        cut = compute_cut_value(bs, edges)
        best = max(best, cut)
    return best


# ─── Circuit builders ────────────────────────────────────────────────────────

def build_standard_qaoa(p, gamma, beta, n_qubits, edges):
    """Standard QAOA: ZZ cost (CX-Rz-CX) + Rx mixer + Z-basis measurement."""
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
    """X-basis QAOA: XX cost via H-CX-Rz-CX-H + Rz mixer + X-measure."""
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
    """Compiled X-basis QAOA: ZZ cost + Rz mixer + X-measure (minimal H gates)."""
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

def optimize_qaoa(build_fn, p, sim, edges, max_cut, n_qubits,
                  shots=512, n_restarts=2, max_iter=40):
    """COBYLA optimization with n_restarts random initializations."""
    best_ratio = 0.0
    best_params = None

    for restart in range(n_restarts):
        params0 = np.random.uniform(0, np.pi, 2 * p)

        def neg_ratio(params):
            gamma = params[:p]
            beta = params[p:]
            qc = build_fn(p, gamma, beta, n_qubits, edges)
            counts = sim.run(qc, shots=shots).result().get_counts()
            total = sum(counts.values())
            expected_cut = sum(
                compute_cut_value(bs[::-1], edges) * cnt / total
                for bs, cnt in counts.items()
            )
            return -expected_cut / max_cut

        result = minimize(neg_ratio, params0, method='COBYLA',
                         options={'maxiter': max_iter, 'rhobeg': 0.5, 'catol': 1e-4})
        ratio = -result.fun
        if ratio > best_ratio:
            best_ratio = ratio
            best_params = result.x

    return best_ratio, best_params


def measure_entropy_at_uniform(build_fn, p, sim, edges, n_qubits, shots=4096):
    """Entropy at uniform params — measures barren plateau onset."""
    gamma = [np.pi/4] * p
    beta = [np.pi/4] * p
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    counts = sim.run(qc, shots=shots).result().get_counts()
    total = sum(counts.values())
    entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    return entropy / n_qubits


def run_experiment(problem_label, n_qubits, edges, max_cut, p_values, sim,
                   shots=512, n_restarts=2, max_iter=40):
    """Run full experiment: all three circuit types at all depths."""
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
            print(f"    p={p}: ratio={ratio:.4f}, entropy={entropy:.4f}, time={elapsed:.1f}s")

    return results


def check_goals(results_ring, ring_4_ref, random_16_ref):
    """Check Exp43 goals (G1-G4)."""
    d = results_ring['data']
    goals = {}

    # G1: Ring gap at p=8 < 0.096 (topology effect vs random-16)
    if 8 in d['standard'] and 8 in d['xbasis']:
        ring_gap_p8 = d['standard'][8]['approx_ratio'] - d['xbasis'][8]['approx_ratio']
        goals['ring_gap_p8'] = ring_gap_p8
        goals['G1'] = ring_gap_p8 < random_16_ref['gap_p8']  # < 0.096

    # G2: Standard QAOA plateaus on ring (std p=8 < std p=4)
    if 4 in d['standard'] and 8 in d['standard']:
        std_p4 = d['standard'][4]['approx_ratio']
        std_p8 = d['standard'][8]['approx_ratio']
        goals['std_plateau_delta'] = std_p8 - std_p4  # Negative = plateau
        goals['G2'] = std_p8 < std_p4  # Plateau confirmed

    # G3: Ring gap at p=8 < 0.05 (H1: strong topology effect)
    if 'ring_gap_p8' in goals:
        goals['G3'] = goals['ring_gap_p8'] < 0.05

    # G4: X-basis anti-plateau protection (xbasis p=8 > p=4)
    if 4 in d['xbasis'] and 8 in d['xbasis']:
        goals['G4'] = d['xbasis'][8]['approx_ratio'] > d['xbasis'][4]['approx_ratio']

    return goals


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  Exp 43: 16-Node RING — Pearl Topology Causal Test             ║")
    print("║  FakeMarrakesh Simulation — Finding 18 Extension               ║")
    print("║  Whisper C3967 | do(topology=ring) | size=16 fixed             ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    # Setup FakeMarrakesh noise simulator
    fake = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake)
    sim = AerSimulator(noise_model=noise_model)

    # Compute exact MaxCut for 16-node ring (should be 8)
    print(f"\nComputing MaxCut for 16-node ring...")
    t_mc = time.time()
    MAX_CUT_16_RING = brute_force_max_cut(N_QUBITS_16_RING, EDGES_16_RING)
    print(f"  16-node ring MaxCut = {MAX_CUT_16_RING} ({time.time()-t_mc:.2f}s)")
    print(f"  Graph: {N_QUBITS_16_RING} nodes, {len(EDGES_16_RING)} edges (degree=2, density=1.0)")
    print(f"  Note: Optimal = {MAX_CUT_16_RING} (all edges cut by alternating partition)")

    P_VALUES = [4, 8]
    SHOTS = 512
    N_RESTARTS = 2
    MAX_ITER = 40

    print(f"\nParameters: p={P_VALUES}, shots={SHOTS}, restarts={N_RESTARTS}, max_iter={MAX_ITER}")
    print(f"Pearl causal test: do(topology=ring), fix size=16")
    print(f"Prediction (H1, P=0.50): ring gap at p=8 < 0.05 (sweet spot restored)")
    print(f"Rival (H3, P=0.25): ring gap ≈ 0.096 (size dominates, topology irrelevant)")
    print("Expected runtime: 1-2 hours")

    start_total = time.time()

    print("\n" + "━"*65)
    print("16-NODE RING MaxCut (Topology Causal Test)")
    print("━"*65)
    results_ring = run_experiment(
        '16-node-ring', N_QUBITS_16_RING, EDGES_16_RING, MAX_CUT_16_RING,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table
    print("\n" + "═"*70)
    print("SUMMARY: Approximation Ratios (16-node RING)")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}  {'Gap(S-X)':>10}")
    for p in P_VALUES:
        if all(p in results_ring['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_ring['data']['standard'][p]['approx_ratio']
            x = results_ring['data']['xbasis'][p]['approx_ratio']
            c = results_ring['data']['compiled'][p]['approx_ratio']
            gap = s - x
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}  {gap:>+10.4f}")

    # Reference comparison
    print("\nReference comparison:")
    print(f"  4-node ring (Exp40):  p=8 gap = +{RING_4_REFERENCE['gap_p8']:.4f}")
    print(f"  8-node random (Exp40): p=8 gap = +0.0126 ← sweet spot")
    print(f"  12-node random (Exp42): p=8 gap = +0.0797")
    print(f"  16-node random (Exp41): p=8 gap = +{RANDOM_16_REFERENCE['gap_p8']:.4f}")
    print(f"  16-node RING (Exp43):  p=8 gap = ???  ← this experiment")

    # Goal evaluation
    goals = check_goals(results_ring, RING_4_REFERENCE, RANDOM_16_REFERENCE)
    print("\n" + "═"*70)
    print("GOAL VERDICTS:")
    goal_descriptions = {
        'G1': f"Ring gap at p=8 < {RANDOM_16_REFERENCE['gap_p8']:.4f} (topology effect confirmed)",
        'G2': 'Standard QAOA plateaus on ring (p=8 ratio < p=4 ratio)',
        'G3': 'Ring gap at p=8 < 0.05 (H1: sweet spot restored)',
        'G4': 'X-basis anti-plateau protection holds (xbasis p=8 > p=4)',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals:
            val = goals[goal]
            if isinstance(val, bool):
                print(f"  {goal}: {'PASS ✓' if val else 'FAIL ✗'}  [{desc}]")
    if 'ring_gap_p8' in goals:
        print(f"  Actual ring gap at p=8: {goals['ring_gap_p8']:.4f}")
    if 'std_plateau_delta' in goals:
        print(f"  Standard plateau delta (p=8 - p=4): {goals['std_plateau_delta']:+.4f}")

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS")

    # Causal interpretation
    print("\n" + "═"*70)
    print("PEARL CAUSAL INTERPRETATION:")
    if 'ring_gap_p8' in goals:
        gap = goals['ring_gap_p8']
        if gap < 0.05:
            print(f"  H1 CONFIRMED: Topology restores x-basis advantage (gap={gap:.4f})")
            print(f"  Pearl DAG validated: Graph_Topology → Standard_Plateau_Risk")
            print(f"  Practical: X-basis competitive on low-connectivity regular graphs at 16 nodes")
        elif gap < 0.08:
            print(f"  H2 CONFIRMED: Partial topology effect (gap={gap:.4f})")
            print(f"  Pearl DAG: Topology contributes but density also matters")
        else:
            print(f"  H3 CONFIRMED: Size/H-gate budget dominates (gap={gap:.4f})")
            print(f"  Pearl DAG revision needed: Topology is downstream of connectivity density")

    # Save results
    output = {
        'experiment': 'Exp43',
        'cycle': 'C3967',
        'date': '2026-06-06',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'graph': {
            'n_qubits': N_QUBITS_16_RING,
            'edges': EDGES_16_RING,
            'max_cut': MAX_CUT_16_RING,
            'topology': 'ring',
            'degree': 2,
            'density': 1.0
        },
        'results_16ring': results_ring,
        'goals': {k: v for k, v in goals.items()},
        'total_runtime_seconds': total_time,
        'references': {
            '4ring_p8_gap': RING_4_REFERENCE['gap_p8'],
            '8random_p8_gap': 0.0126,
            '12random_p8_gap': 0.0797,
            '16random_p8_gap': RANDOM_16_REFERENCE['gap_p8'],
        },
        'pearl_causal_test': {
            'intervention': 'do(topology=ring)',
            'fixed_variable': 'size=16',
            'prediction': 'gap < 0.05 (H1, P=0.50)',
            'rival': 'gap >= 0.08 (H3, P=0.25)'
        }
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp43_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    print("\nQuantum repo: commit pending analysis (Whisper C3967)")
