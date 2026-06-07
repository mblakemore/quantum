#!/usr/bin/env python3
"""
Exp47: Crossover Replication — Is the Exp46 p=4/p=5 sign-flip REAL or single-restart noise?
Ember C3606 | 2026-06-07

CONTEXT: Exp46-Fast (n_restarts=1) found gap(std-xbasis) = {p3:-0.0275, p4:-0.0069,
p5:+0.0286, p6:+0.0082} — a zero-crossing between p=4 and p=5 (xbasis wins low-p,
standard wins high-p). But single COBYLA restart has ratio variance ~0.02-0.05, which
is the SAME magnitude as the gaps. The crossover may be an artifact.

METHOD: For the two CLEAN signals (p=3, p=5), run 3 INDEPENDENT single-restart
measurements each (different random COBYLA seeds). Report all 3 ratios + mean + std
for standard and xbasis. Decision rule:
  - REAL crossover: at p=3 xbasis>standard in all/most reps AND at p=5 standard>xbasis
    in all/most reps, with gap means separated by > 1 std.
  - NOISE: the rep distributions for standard and xbasis overlap heavily.

Reuses graph + circuit builders + evaluator from run_exp46_fast.py.
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20, HGATES_PER_LAYER, SWEET_SPOT_BUDGET,
    brute_force_max_cut, build_parameterized_standard_qaoa,
    build_parameterized_xbasis_qaoa, optimize_with_cached_circuit,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 256
N_REPS = 3          # independent single-restart measurements per (p, circuit)
MAX_ITER = 30
OPT_LEVEL = 1
P_VALUES = [3, 5]   # the two clean signals from Exp46

if __name__ == '__main__':
    print("Exp47: Crossover Replication (p=3,5 x 3 reps, noise assessment)", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges, "
          f"shots={SHOTS}, reps={N_REPS}, max_iter={MAX_ITER}", flush=True)

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    print("Backend ready. Computing MaxCut...", flush=True)
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)

    builders = [('standard', build_parameterized_standard_qaoa),
                ('xbasis',   build_parameterized_xbasis_qaoa)]

    data = {}      # data[p][circ] = list of N_REPS ratios
    start = time.time()
    for p in P_VALUES:
        data[p] = {}
        h = p * HGATES_PER_LAYER
        print(f"\n━━ p={p} ({h} H-gates, {100*h/SWEET_SPOT_BUDGET:.0f}% budget) ━━", flush=True)
        for circ_name, build_fn in builders:
            template, gpar, bpar = build_fn(p, N_QUBITS_20, EDGES_20)
            tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
            ratios = []
            for rep in range(N_REPS):
                t0 = time.time()
                # single restart, fresh random x0 each rep (np global RNG advances)
                ratio, _ = optimize_with_cached_circuit(
                    tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
                    N_QUBITS_20, SHOTS, n_restarts=1, max_iter=MAX_ITER)
                ratios.append(round(float(ratio), 4))
                print(f"    {circ_name:9s} rep{rep+1}: ratio={ratio:.4f} "
                      f"({time.time()-t0:.0f}s)", flush=True)
            data[p][circ_name] = ratios
            print(f"    {circ_name:9s} mean={np.mean(ratios):.4f} std={np.std(ratios):.4f}",
                  flush=True)

    print(f"\nTotal runtime: {(time.time()-start)/60:.1f} min", flush=True)

    # ─── Verdict ───
    print("\n" + "═"*72, flush=True)
    print("CROSSOVER VERDICT", flush=True)
    summary = {}
    for p in P_VALUES:
        s = np.array(data[p]['standard']); x = np.array(data[p]['xbasis'])
        gap_mean = float(s.mean() - x.mean())
        gap_std = float(np.sqrt(s.var()/len(s) + x.var()/len(x)))  # SE of difference
        winner = 'xbasis' if gap_mean < 0 else 'standard'
        separated = abs(gap_mean) > gap_std  # mean gap exceeds 1 SE
        summary[p] = {'std_ratios': data[p]['standard'], 'xbasis_ratios': data[p]['xbasis'],
                      'gap_mean': round(gap_mean, 4), 'gap_se': round(gap_std, 4),
                      'winner': winner, 'separated_1se': separated}
        print(f"  p={p}: gap(std-xb)={gap_mean:+.4f} ± {gap_std:.4f} SE → "
              f"winner={winner} {'(SEPARATED)' if separated else '(OVERLAP/noise)'}", flush=True)

    p3_xb = summary[3]['winner'] == 'xbasis' and summary[3]['separated_1se']
    p5_std = summary[5]['winner'] == 'standard' and summary[5]['separated_1se']
    crossover_real = p3_xb and p5_std
    print(f"\n  CROSSOVER REAL (p3 xbasis-sep AND p5 standard-sep): "
          f"{'YES ✓' if crossover_real else 'NO ✗ — likely single-restart noise'}", flush=True)

    out = {
        'experiment': 'Exp47-crossover-replication', 'cycle': 'C3606',
        'date': '2026-06-07', 'backend': 'FakeMarrakesh',
        'shots': SHOTS, 'n_reps': N_REPS, 'max_iter': MAX_ITER,
        'p_values': P_VALUES, 'max_cut': max_cut,
        'summary': summary, 'crossover_real': crossover_real,
        'exp46_reference_gaps': {3: -0.0275, 4: -0.0069, 5: 0.0286, 6: 0.0082},
    }
    outfile = '/mnt/droid/repos/quantum/experiments/exp47_results.json'
    with open(outfile, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved: {outfile}\nExp47 complete.", flush=True)
