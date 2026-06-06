#!/usr/bin/env python3
"""
Exp 41: 16-Node QAOA Scaling Extension
Pre-registration: experiments/41-16node-scaling-preregistration.md
Whisper C3965 | 2026-06-06

Research question: Does H-gate landscape advantage in x-basis QAOA scale to 16 nodes?
Finding 16: 4-node gap=0.245, 8-node gap=0.013 (18× reduction).
Does 16-node gap shrink further?

Three circuits compared (same as Exp40):
  1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
  2. X-basis QAOA:  XX cost (H-wrapped) + Rz mixer + X-measure
  3. Compiled QAOA: ZZ cost + Rz mixer + X-measure (8 H gates only)

Goals (pre-registered C3965):
  G5: 16-node p=8 x-basis ratio >= 0.80
  G6: 16-node p=8 gap (std - xbasis) < 0.013
  G7: x-basis avoids barren plateau (monotone p=4→p=8)
  G8: compiled near-random (< 0.65)
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

# 8-node (from Exp40, for direct reference)
EDGES_8 = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,3),(1,5),(2,6),(4,7)]
N_QUBITS_8 = 8

# 16-node: ring + cross connections (24 edges, same density ratio as 8-node)
EDGES_16 = [
    # Ring (16 edges)
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0),
    # Cross connections — varied distances for structural complexity (8 edges)
    (0,5),(1,9),(2,11),(3,13),(4,8),(6,12),(7,14),(10,15)
]
N_QUBITS_16 = 16


def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def brute_force_max_cut(n_qubits, edges):
    """Exact MaxCut via brute force. Feasible for n<=20."""
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
    """X-basis QAOA (Exp38/39 design): XX cost via H-CX-Rz-CX-H + Rz mixer + X-measure."""
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
    # X-basis measurement: H before measure
    for q in range(n_qubits):
        qc.h(q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_compiled_qaoa(p, gamma, beta, n_qubits, edges):
    """Compiled X-basis QAOA: ZZ cost + Rz mixer + X-measure (8 H gates only).
    H gates appear only at init and final measurement — never repeated per layer.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))  # State prep in X-basis (4/8/16 H gates once)
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in edges:
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
        for q in range(n_qubits):
            qc.rz(2 * b, q)
    # X-basis measurement
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
    """Entropy at uniform params (pi/4, pi/4) — measures barren plateau onset."""
    gamma = [np.pi/4] * p
    beta = [np.pi/4] * p
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    counts = sim.run(qc, shots=shots).result().get_counts()
    total = sum(counts.values())
    # Shannon entropy of output distribution
    entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    return entropy / n_qubits  # Normalized


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


def check_goals(results_16):
    """Check Exp41 goals (G5-G8)."""
    d = results_16['data']
    goals = {}

    # G5: 16-node p=8 x-basis ratio >= 0.80
    if 8 in d['xbasis']:
        goals['G5'] = d['xbasis'][8]['approx_ratio'] >= 0.80

    # G6: 16-node p=8 gap (standard - xbasis) < 0.013 (Finding 16 trend continues)
    if 8 in d['standard'] and 8 in d['xbasis']:
        gap_8 = d['standard'][8]['approx_ratio'] - d['xbasis'][8]['approx_ratio']
        goals['G6'] = gap_8 < 0.013
        goals['gap_p8'] = gap_8  # Store for reporting

    # G7: x-basis avoids barren plateau (monotone p=4→p=8)
    if 4 in d['xbasis'] and 8 in d['xbasis']:
        goals['G7'] = d['xbasis'][8]['approx_ratio'] > d['xbasis'][4]['approx_ratio']

    # G8: compiled near-random (< 0.65)
    if 8 in d['compiled']:
        goals['G8'] = d['compiled'][8]['approx_ratio'] < 0.65

    return goals


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Exp 41: 16-Node QAOA Scaling Extension (Whisper C3965) ║")
    print("║  FakeMarrakesh Simulation — Finding 16 Extrapolation     ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Setup FakeMarrakesh noise simulator
    fake = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake)
    sim = AerSimulator(noise_model=noise_model)

    # Compute exact MaxCut
    print(f"\nComputing MaxCut for 16-node graph...")
    t_mc = time.time()
    MAX_CUT_16 = brute_force_max_cut(N_QUBITS_16, EDGES_16)
    print(f"  16-node MaxCut = {MAX_CUT_16} ({time.time()-t_mc:.2f}s)")
    print(f"  Graph: {N_QUBITS_16} nodes, {len(EDGES_16)} edges")

    # Reference 8-node (quick sanity check)
    MAX_CUT_8 = brute_force_max_cut(N_QUBITS_8, EDGES_8)
    print(f"  8-node MaxCut = {MAX_CUT_8} (Exp40 reference)")

    P_VALUES = [4, 8]  # Key comparison range from Finding 16
    SHOTS = 512        # Reduced from 1024 for 16-qubit feasibility
    N_RESTARTS = 2     # Reduced from 3
    MAX_ITER = 40      # Reduced from 50

    print(f"\nParameters: p={P_VALUES}, shots={SHOTS}, restarts={N_RESTARTS}, max_iter={MAX_ITER}")
    print("Expected runtime: 2-4 hours for 16-qubit simulation")

    start_total = time.time()

    print("\n" + "━"*60)
    print("16-NODE RANDOM MAXCUT")
    print("━"*60)
    results_16 = run_experiment(
        '16-node-random', N_QUBITS_16, EDGES_16, MAX_CUT_16,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table
    print("\n" + "═"*70)
    print("SUMMARY: Approximation Ratios (16-node random)")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}  {'Gap(S-X)':>10}")
    for p in P_VALUES:
        if all(p in results_16['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_16['data']['standard'][p]['approx_ratio']
            x = results_16['data']['xbasis'][p]['approx_ratio']
            c = results_16['data']['compiled'][p]['approx_ratio']
            gap = s - x
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}  {gap:>+10.4f}")

    # Reference: Exp40 8-node results
    print("\nReference: Exp40 8-node results")
    print(f"  p=4: std=0.9395, xbasis=0.7836, gap=+0.1559")
    print(f"  p=8: std=0.8235, xbasis=0.8109, gap=+0.0130  ← Finding 16")

    # Entropy table
    print("\nEntropy (lower = less barren plateau)")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}")
    for p in P_VALUES:
        if all(p in results_16['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_16['data']['standard'][p]['entropy_uniform']
            x = results_16['data']['xbasis'][p]['entropy_uniform']
            c = results_16['data']['compiled'][p]['entropy_uniform']
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}")

    # Goal evaluation
    goals = check_goals(results_16)
    print("\n" + "═"*70)
    print("GOAL VERDICTS:")
    goal_descriptions = {
        'G5': 'p=8 x-basis ratio >= 0.80',
        'G6': f"p=8 gap < 0.013 (Finding 16 trend)",
        'G7': 'x-basis monotone p=4→p=8 (no barren plateau)',
        'G8': 'compiled < 0.65 (near-random)',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals:
            val = goals[goal]
            if isinstance(val, bool):
                print(f"  {goal}: {'PASS ✓' if val else 'FAIL ✗'}  [{desc}]")
    if 'gap_p8' in goals:
        print(f"  Actual gap at p=8: {goals['gap_p8']:.4f}")

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS")

    # Save results
    output = {
        'experiment': 'Exp41',
        'cycle': 'C3965',
        'date': '2026-06-06',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'graph': {
            'n_qubits': N_QUBITS_16,
            'edges': EDGES_16,
            'max_cut': MAX_CUT_16
        },
        'results_16node': results_16,
        'goals': {k: v for k, v in goals.items()},
        'total_runtime_seconds': total_time,
        'finding16_reference': {
            '8node_p8_std': 0.8235,
            '8node_p8_xbasis': 0.8109,
            '8node_p8_gap': 0.013
        }
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp41_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    print("\nQuantum repo: commit pending analysis")
