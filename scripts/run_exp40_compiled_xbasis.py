#!/usr/bin/env python3
"""
Exp 40: Compiled X-Basis QAOA (H-Gate-Free Compilation)
Pre-registration: experiments/40-xbasis-compiled-preregistration.md
Whisper C3961 | 2026-06-06

Hypothesis: H-gate overhead was the confound in Exp38/39.
By absorbing H gates into frame (ZZ cost + Rz mixer in X-rotated frame),
the Rz commutation advantage dominates and compiled X-basis should outperform.

Three circuits compared:
  1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
  2. X-basis QAOA:  XX cost (H-wrapped) + Rz mixer + X-measure [Exp38/39]
  3. Compiled QAOA: ZZ cost + Rz mixer + X-measure [NEW, only 8 H gates total]

Key claim: Compiled (3) = X-basis but fewer H gates → less gate noise
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
# 4-node ring MaxCut (same as Exp38/39 for direct comparison)
EDGES_4 = [(0, 1), (1, 2), (2, 3), (0, 3)]
N_QUBITS_4 = 4
MAX_CUT_4 = 4

# 8-node random 3-regular-ish MaxCut (harder landscape, Exp40 extension)
EDGES_8 = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,3),(1,5),(2,6),(4,7)]
N_QUBITS_8 = 8
MAX_CUT_8_EXACT = 10  # brute-force confirmed below


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
    """X-basis QAOA (Exp38/39): XX cost via H-CX-Rz-CX-H + Rz mixer + X-measure.
    H gate count: 4 (init) + 4 edges × 4 H/edge × p layers + 4 (final) = 8 + 16p
    """
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
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_compiled_xbasis_qaoa(p, gamma, beta, n_qubits, edges):
    """Compiled X-basis QAOA (Exp40): ZZ cost + Rz mixer + X-measure.
    
    Key insight: H_all * (ZZ cost) * H_all = XX cost.
    By absorbing H gates into frame: 8 H gates total regardless of p,
    vs 8+16p for standard X-basis QAOA.
    
    Rz mixer commutes with Z-dephasing → mixer is noise-transparent.
    H-gate count: 4 (init) + 0 (per layer) + 4 (final) = 8 total.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))  # Put qubits in X eigenstates
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        # ZZ cost (standard CX-Rz-CX) — in X-rotated frame = effective XX interaction
        for i, j in edges:
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
        # Rz mixer: COMMUTES with Z-dephasing noise (key advantage over Rx mixer)
        for q in range(n_qubits):
            qc.rz(2 * b, q)
    # X-basis measurement (4 H gates at end — same cost regardless of p)
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def count_h_gates(circuit):
    """Count H gates in a transpiled/built circuit."""
    return sum(1 for inst in circuit.data if inst.operation.name == 'h')


# ─── Metrics ────────────────────────────────────────────────────────────────

def get_approximation_ratio(counts, edges, max_cut, n_qubits):
    total = sum(counts.values())
    expected_cut = sum(
        compute_cut_value(bs[::-1], edges) * cnt / total
        for bs, cnt in counts.items()
    )
    return expected_cut / max_cut


def get_output_entropy(counts, n_qubits):
    total = sum(counts.values())
    probs = np.array([counts.get(format(i, f'0{n_qubits}b'), 0) / total
                      for i in range(2**n_qubits)])
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs)) / n_qubits


# ─── Optimization ────────────────────────────────────────────────────────────

def optimize_qaoa(build_fn, p, sim, edges, max_cut, n_qubits,
                  shots=1024, n_restarts=3, max_iter=50):
    """COBYLA optimization with n_restarts random initializations."""
    best_ratio = 0.0
    best_params = None
    eval_counts = []

    for restart in range(n_restarts):
        params0 = np.random.uniform(0, 2*np.pi, 2*p)

        def neg_ratio(params):
            gamma = params[:p]
            beta = params[p:]
            qc = build_fn(p, gamma, beta, n_qubits, edges)
            result = sim.run(qc, shots=shots).result()
            counts = result.get_counts()
            return -get_approximation_ratio(counts, edges, max_cut, n_qubits)

        opt = minimize(neg_ratio, params0, method='COBYLA',
                       options={'maxiter': max_iter, 'rhobeg': 0.5, 'catol': 1e-4})
        ratio = -opt.fun
        eval_counts.append(opt.nfev)
        if ratio > best_ratio:
            best_ratio = ratio
            best_params = opt.x

    return best_ratio, best_params, eval_counts


def measure_entropy_at_uniform(build_fn, p, sim, edges, n_qubits, shots=4096):
    """Measure output entropy at uniform params (noise proxy)."""
    gamma = np.ones(p) * np.pi / 4
    beta = np.ones(p) * np.pi / 4
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    counts = sim.run(qc, shots=shots).result().get_counts()
    return get_output_entropy(counts, n_qubits)


# ─── Main experiment ─────────────────────────────────────────────────────────

def run_experiment(problem_label, n_qubits, edges, max_cut, p_values, sim,
                   shots=1024, n_restarts=3, max_iter=50):
    results = {
        'problem': problem_label,
        'n_qubits': n_qubits,
        'max_cut': max_cut,
        'p_values': p_values,
        'shots': shots,
        'n_restarts': n_restarts,
        'max_iter': max_iter,
        'circuits': ['standard', 'xbasis', 'compiled'],
        'data': {}
    }

    build_fns = {
        'standard': build_standard_qaoa,
        'xbasis':   build_xbasis_qaoa,
        'compiled': build_compiled_xbasis_qaoa,
    }

    # Gate count validation (at p=4 for 4-node ring)
    print(f"\n{'─'*60}")
    print(f"Gate count analysis (p=4, {problem_label})")
    p_test = 4
    gamma_t = np.ones(p_test) * np.pi/4
    beta_t  = np.ones(p_test) * np.pi/4
    for name, fn in build_fns.items():
        qc = fn(p_test, gamma_t, beta_t, n_qubits, edges)
        h_count = count_h_gates(qc)
        gate_counts = {g: sum(1 for i in qc.data if i.operation.name==g)
                       for g in ['h','cx','rz','rx']}
        print(f"  {name:12s}: H={gate_counts['h']:3d} CX={gate_counts['cx']:3d} "
              f"Rz={gate_counts['rz']:3d} Rx={gate_counts['rx']:3d}")

    # Main optimization sweep
    for name, build_fn in build_fns.items():
        results['data'][name] = {}
        for p in p_values:
            t0 = time.time()
            print(f"\n[{problem_label}] {name} p={p} ...", flush=True)
            
            # Optimization
            ratio, params, eval_counts = optimize_qaoa(
                build_fn, p, sim, edges, max_cut, n_qubits,
                shots=shots, n_restarts=n_restarts, max_iter=max_iter
            )
            
            # Entropy at uniform params (noise proxy)
            entropy = measure_entropy_at_uniform(build_fn, p, sim, edges, n_qubits)
            
            elapsed = time.time() - t0
            results['data'][name][p] = {
                'approx_ratio': float(ratio),
                'entropy_uniform': float(entropy),
                'eval_counts': eval_counts,
                'elapsed_sec': float(elapsed)
            }
            print(f"  → ratio={ratio:.4f}  entropy={entropy:.4f}  "
                  f"evals={eval_counts}  t={elapsed:.1f}s")

    return results


def check_goals(results_4, results_8):
    """Evaluate pre-registered goals G1-G4."""
    print("\n" + "═"*60)
    print("GOAL EVALUATION (Pre-registered criteria)")
    print("═"*60)

    data4 = results_4['data']
    data8 = results_8['data']
    p_vals = results_4['p_values']

    # G1: Compiled X-basis achieves r ≥ r_standard + 0.05 on 4-node ring at some p
    g1_pass = any(
        data4['compiled'][p]['approx_ratio'] >= data4['standard'][p]['approx_ratio'] + 0.05
        for p in p_vals if p in data4['compiled'] and p in data4['standard']
    )
    best_p_g1 = max(p_vals,
                    key=lambda p: data4['compiled'][p]['approx_ratio'] - data4['standard'][p]['approx_ratio']
                    if p in data4['compiled'] and p in data4['standard'] else -999)
    g1_delta = (data4['compiled'][best_p_g1]['approx_ratio'] -
                data4['standard'][best_p_g1]['approx_ratio']
                if best_p_g1 in data4['compiled'] and best_p_g1 in data4['standard'] else None)
    print(f"\nG1 [Compiled ≥ Standard + 0.05, 4-node, some p]: "
          f"{'PASS ✓' if g1_pass else 'FAIL ✗'}")
    print(f"   Best delta: {g1_delta:.4f} at p={best_p_g1}")

    # G2: Compiled entropy < Standard entropy at p≥4
    g2_checks = [(p, data4['compiled'][p]['entropy_uniform'],
                   data4['standard'][p]['entropy_uniform'])
                 for p in p_vals if p >= 4 and p in data4['compiled'] and p in data4['standard']]
    g2_pass = all(c < s for p, c, s in g2_checks)
    print(f"\nG2 [Compiled entropy < Standard entropy at p≥4]: "
          f"{'PASS ✓' if g2_pass else 'FAIL ✗'}")
    for p, c, s in g2_checks:
        print(f"   p={p}: compiled={c:.4f}  standard={s:.4f}  "
              f"{'✓' if c < s else '✗'}")

    # G3: Compiled ratio ≥ X-basis ratio at all p
    g3_checks = [(p, data4['compiled'][p]['approx_ratio'],
                   data4['xbasis'][p]['approx_ratio'])
                 for p in p_vals if p in data4['compiled'] and p in data4['xbasis']]
    g3_pass = all(c >= x for p, c, x in g3_checks)
    print(f"\nG3 [Compiled ratio ≥ X-basis ratio at all p]: "
          f"{'PASS ✓' if g3_pass else 'FAIL ✗'}")
    for p, c, x in g3_checks:
        print(f"   p={p}: compiled={c:.4f}  xbasis={x:.4f}  "
              f"{'✓' if c >= x else '✗'}  delta={c-x:+.4f}")

    # G4: On 8-node MaxCut, compiled advantage increases relative to 4-node
    delta4 = [data4['compiled'][p]['approx_ratio'] - data4['standard'][p]['approx_ratio']
              for p in p_vals if p in data4['compiled'] and p in data4['standard']]
    delta8 = [data8['compiled'][p]['approx_ratio'] - data8['standard'][p]['approx_ratio']
              for p in p_vals if p in data8['compiled'] and p in data8['standard']]
    g4_pass = np.mean(delta8) > np.mean(delta4) if delta8 and delta4 else False
    print(f"\nG4 [8-node advantage > 4-node advantage]: "
          f"{'PASS ✓' if g4_pass else 'FAIL ✗'}")
    if delta4 and delta8:
        print(f"   4-node mean delta: {np.mean(delta4):+.4f}")
        print(f"   8-node mean delta: {np.mean(delta8):+.4f}")

    return {'G1': g1_pass, 'G2': g2_pass, 'G3': g3_pass, 'G4': g4_pass}


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    np.random.seed(42)

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Exp 40: Compiled X-Basis QAOA (Whisper C3961)          ║")
    print("║  FakeMarrakesh Simulation — No QPU quota used            ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Setup FakeMarrakesh noise simulator
    fake = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake)
    sim = AerSimulator(noise_model=noise_model)

    # Verify max-cut values
    mc4 = brute_force_max_cut(N_QUBITS_4, EDGES_4)
    mc8 = brute_force_max_cut(N_QUBITS_8, EDGES_8)
    print(f"\nMax-cut verified: 4-node={mc4}, 8-node={mc8}")
    MAX_CUT_4 = mc4
    MAX_CUT_8_EXACT = mc8

    P_VALUES = [1, 4, 8, 16]
    SHOTS = 1024
    N_RESTARTS = 3
    MAX_ITER = 50

    start_total = time.time()

    print("\n" + "━"*60)
    print("4-NODE RING MAXCUT")
    print("━"*60)
    results_4 = run_experiment(
        '4-node-ring', N_QUBITS_4, EDGES_4, MAX_CUT_4,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    print("\n" + "━"*60)
    print("8-NODE MAXCUT")
    print("━"*60)
    results_8 = run_experiment(
        '8-node-random', N_QUBITS_8, EDGES_8, MAX_CUT_8_EXACT,
        P_VALUES, sim, shots=SHOTS, n_restarts=N_RESTARTS, max_iter=MAX_ITER
    )

    # Goal evaluation
    goals = check_goals(results_4, results_8)

    total_time = time.time() - start_total
    print(f"\nTotal runtime: {total_time/60:.1f} minutes")

    # Summary table
    print("\n" + "═"*70)
    print("SUMMARY: Approximation Ratios (4-node ring)")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}  {'Comp-Std':>10}")
    for p in P_VALUES:
        if all(p in results_4['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_4['data']['standard'][p]['approx_ratio']
            x = results_4['data']['xbasis'][p]['approx_ratio']
            c = results_4['data']['compiled'][p]['approx_ratio']
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}  {c-s:>+10.4f}")

    print("\nEntropy (4-node ring, lower = better circuit fidelity)")
    print(f"{'p':>4}  {'Standard':>10}  {'X-basis':>10}  {'Compiled':>10}")
    for p in P_VALUES:
        if all(p in results_4['data'][c] for c in ['standard','xbasis','compiled']):
            s = results_4['data']['standard'][p]['entropy_uniform']
            x = results_4['data']['xbasis'][p]['entropy_uniform']
            c = results_4['data']['compiled'][p]['entropy_uniform']
            print(f"{p:>4}  {s:>10.4f}  {x:>10.4f}  {c:>10.4f}")

    # Goal summary
    print("\n" + "═"*70)
    print("FINAL VERDICT:")
    for goal, passed in goals.items():
        print(f"  {goal}: {'PASS ✓' if passed else 'FAIL ✗'}")

    pass_count = sum(1 for v in goals.values() if v)
    print(f"\n  {pass_count}/4 goals PASS")

    # Save results
    output = {
        'experiment': 'Exp40',
        'cycle': 'C3961',
        'date': '2026-06-06',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_restarts': N_RESTARTS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'results_4node': results_4,
        'results_8node': results_8,
        'goals': goals,
        'total_runtime_seconds': total_time
    }

    outpath = '/droid/repos/quantum/experiments/exp40_results.json'
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outpath}")
