#!/usr/bin/env python3
"""
Exp 42: 12-Node QAOA Intermediate Scaling
Pre-registration: experiments/42-12node-scaling-preregistration.md
Ember C3598 | 2026-06-06

Research question: Is the x-basis QAOA sweet spot at 8-node a sharp boundary
or a gradual curve? Finding 17 showed non-monotone scaling:
  4-node gap=0.245, 8-node gap=0.013 (sweet spot), 16-node gap=0.096

12-node intermediate test distinguishes three hypotheses:
  H1: Gradual transition (0.013 < gap < 0.096)
  H2: Extended sweet spot (gap < 0.025)
  H3: Sharp transition (gap > 0.070 already at 12-node)

Three circuits compared (same as Exp40/41):
  1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
  2. X-basis QAOA:  XX cost (H-wrapped) + Rz mixer + X-measure
  3. Compiled QAOA: ZZ cost + Rz mixer + X-measure (H-gates only at init/measure)

Goals (pre-registered C3598):
  G1: 0.013 < gap(std-xbasis) < 0.096 at p=8 [intermediate = H1 confirmed]
  G2: x-basis p=8 ratio >= 0.75
  G3: x-basis monotone p=4→p=8 (barren plateau protection holds)
  G4: compiled p=8 < 0.65 (near-random, structural failure replicates)
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

# 8-node (Exp40 reference)
EDGES_8 = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,3),(1,5),(2,6),(4,7)]
N_QUBITS_8 = 8

# 12-node: ring + cross connections (18 edges, density 1.5 edges/node = same as 8/16-node)
EDGES_12 = [
    # Ring (12 edges)
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),(11,0),
    # Cross connections — varied distances for structural complexity (6 edges)
    (0,4),(1,7),(2,9),(3,6),(5,10),(8,11)
]
N_QUBITS_12 = 12

# 16-node (Exp41 reference)
EDGES_16 = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0),
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
    # X-basis measurement: H before measure
    for q in range(n_qubits):
        qc.h(q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_compiled_qaoa(p, gamma, beta, n_qubits, edges):
    """Compiled X-basis QAOA: ZZ cost + Rz mixer + X-measure (H-gates only at init/measure)."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
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
    """Entropy at uniform params — measures barren plateau onset."""
    gamma = [np.pi/4] * p
    beta = [np.pi/4] * p
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    counts = sim.run(qc, shots=shots).result().get_counts()
    total = sum(counts.values())
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


def check_goals(results_12):
    """Check Exp42 goals (G1-G4)."""
    d = results_12['data']
    goals = {}

    # G1: gap at p=8 is intermediate (0.013 < gap < 0.096) — H1 confirmed
    if 8 in d['standard'] and 8 in d['xbasis']:
        gap_8 = d['standard'][8]['approx_ratio'] - d['xbasis'][8]['approx_ratio']
        goals['gap_p8'] = gap_8
        goals['G1'] = 0.013 < gap_8 < 0.096

    # G2: x-basis p=8 ratio >= 0.75
    if 8 in d['xbasis']:
        goals['G2'] = d['xbasis'][8]['approx_ratio'] >= 0.75

    # G3: x-basis monotone p=4→p=8 (barren plateau protection)
    if 4 in d['xbasis'] and 8 in d['xbasis']:
        goals['G3'] = d['xbasis'][8]['approx_ratio'] > d['xbasis'][4]['approx_ratio']

    # G4: compiled near-random at p=8 (< 0.65)
    if 8 in d['compiled']:
        goals['G4'] = d['compiled'][8]['approx_ratio'] < 0.65

    return goals


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Exp 42: 12-Node QAOA Intermediate Scaling (Ember C3598)    ║")
    print("║  FakeMarrakesh Simulation — Finding 17 Sweet Spot Probe     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\nHypotheses:")
    print("  H1: Gradual transition (0.013 < gap < 0.096) — PRIMARY")
    print("  H2: Extended sweet spot (gap < 0.025)")
    print("  H3: Sharp transition (gap > 0.070 at 12-node)")
    print()

    # Setup FakeMarrakesh noise simulator
    fake = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake)
    sim = AerSimulator(noise_model=noise_model)

    # Compute exact MaxCut values
    print("Computing MaxCut values...")
    t_mc = time.time()
    MAX_CUT_12 = brute_force_max_cut(N_QUBITS_12, EDGES_12)
    print(f"  12-node MaxCut = {MAX_CUT_12} ({time.time()-t_mc:.3f}s)")
    print(f"  Graph: {N_QUBITS_12} nodes, {len(EDGES_12)} edges")

    # Reference values (from Exp40/41)
    print(f"\n  Reference: 8-node MaxCut = 10 (Exp40)")
    print(f"  Reference: 16-node MaxCut = 21 (Exp41)")

    P_VALUES = [4, 8]
    SHOTS = 512
    N_RESTARTS = 2
    MAX_ITER = 40

    print(f"\nParameters: p={P_VALUES}, shots={SHOTS}, restarts={N_RESTARTS}, max_iter={MAX_ITER}")
    print(f"Expected runtime: ~1-2 hours (12-qubit, less than 16-qubit Exp41)")

    start_total = time.time()

    print("\n" + "━"*65)
    print("12-NODE RANDOM MAXCUT")
    print("━"*65)
    results_12 = run_experiment(
        '12-node-random', N_QUBITS_12, EDGES_12, MAX_CUT_12,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table
    print("\n" + "═"*75)
    print("SUMMARY: Approximation Ratios (12-node random)")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}  {'Gap(S-X)':>10}")
    for p in P_VALUES:
        if all(p in results_12['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_12['data']['standard'][p]['approx_ratio']
            x = results_12['data']['xbasis'][p]['approx_ratio']
            c = results_12['data']['compiled'][p]['approx_ratio']
            gap = s - x
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}  {gap:>+10.4f}")

    # Full scaling table
    print("\nFull Scaling Comparison (p=8 Gap: Standard - X-basis):")
    print(f"  4-node  (Exp40): gap = 0.2456")
    print(f"  8-node  (Exp40): gap = 0.0126  ← sweet spot")
    if 8 in results_12['data']['standard'] and 8 in results_12['data']['xbasis']:
        gap = results_12['data']['standard'][8]['approx_ratio'] - results_12['data']['xbasis'][8]['approx_ratio']
        print(f"  12-node (Exp42): gap = {gap:.4f}  ← THIS EXPERIMENT")
    print(f"  16-node (Exp41): gap = 0.0964")

    # Entropy table
    print("\nEntropy (lower = less barren plateau):")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}")
    for p in P_VALUES:
        if all(p in results_12['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_12['data']['standard'][p]['entropy_uniform']
            x = results_12['data']['xbasis'][p]['entropy_uniform']
            c = results_12['data']['compiled'][p]['entropy_uniform']
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}")

    # Goal evaluation
    goals = check_goals(results_12)
    print("\n" + "═"*75)
    print("GOAL VERDICTS:")
    goal_descriptions = {
        'G1': f"gap intermediate 0.013 < gap < 0.096 [H1=gradual transition]",
        'G2': 'x-basis p=8 ratio >= 0.75 [competitive at 12-node]',
        'G3': 'x-basis monotone p=4→p=8 [barren plateau protection]',
        'G4': 'compiled p=8 < 0.65 [structural failure replicates]',
    }
    for goal, desc in goal_descriptions.items():
        if goal in goals:
            val = goals[goal]
            if isinstance(val, bool):
                print(f"  {goal}: {'PASS ✓' if val else 'FAIL ✗'}  [{desc}]")
    if 'gap_p8' in goals:
        gap = goals['gap_p8']
        print(f"\n  Actual gap at p=8: {gap:.4f}")
        if gap < 0.025:
            print(f"  → H2 CONFIRMED: Extended sweet spot (gap < 0.025)")
        elif gap < 0.096:
            print(f"  → H1 CONFIRMED: Gradual transition (0.013 < gap < 0.096)")
        else:
            print(f"  → H3 CONFIRMED: Sharp/over-transition (gap > 0.096, worse than 16-node)")

    pass_count = sum(1 for k, v in goals.items() if isinstance(v, bool) and v)
    total_goals = sum(1 for k, v in goals.items() if isinstance(v, bool))
    print(f"\n  {pass_count}/{total_goals} goals PASS")

    # Determine winning hypothesis
    if 'gap_p8' in goals:
        gap = goals['gap_p8']
        if gap < 0.025:
            verdict = "H2: Extended sweet spot"
        elif gap < 0.096:
            verdict = "H1: Gradual transition (sweet spot at 8-node)"
        else:
            verdict = "H3: Sharp transition / unexpected regression"
        print(f"\n  HYPOTHESIS VERDICT: {verdict}")

    # Save results
    output = {
        'experiment': 'Exp42',
        'cycle': 'C3598',
        'date': '2026-06-06',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'graph': {
            'n_qubits': N_QUBITS_12,
            'edges': EDGES_12,
            'max_cut': MAX_CUT_12
        },
        'results_12node': results_12,
        'goals': {k: v for k, v in goals.items()},
        'total_runtime_seconds': total_time,
        'scaling_reference': {
            '4node_p8_gap': 0.2456,
            '8node_p8_gap': 0.0126,
            '16node_p8_gap': 0.0964
        }
    }

    outfile = '/mnt/droid/repos/quantum/experiments/exp42_results.json'
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    print("\nQuantum repo: commit pending analysis")
