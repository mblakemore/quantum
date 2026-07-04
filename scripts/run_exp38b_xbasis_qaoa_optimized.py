#!/usr/bin/env python3
"""
Exp 38b: X-Basis QAOA vs Standard QAOA — PROPERLY OPTIMIZED re-run (Elder C6347).

WHY THIS EXISTS (integrity correction):
  The original Exp38 (scripts/run_exp38_xbasis_qaoa.py, results
  experiments/38-xbasis-qaoa-results.json) was labeled at C5656 as
  "COBYLA-optimized (3 restarts)" and its interpretation narrated
  "the classical optimizer compensates for mixer-layer noise." VERIFIED
  FALSE at C6347: that script calls run_with_analytic_params() ONLY — fixed
  heuristic angles gamma=beta=pi/(4p), a SINGLE seed (np.random.seed(38)),
  N=1. `minimize` is imported but never called. No COBYLA ran. The
  git commit 9249150 ("Exp38 COBYLA results flip verdict to 1/4 PASS") is
  byte-identical to the analytic script. So the G1/G4 "standard wins with
  optimization" conclusion described an optimizer that never executed, and
  the entropy (measured at pi/4) and approximation ratio (measured at
  pi/(4p)) were taken at DIFFERENT parameter regimes.

WHAT THIS DOES (the fair test the pre-reg intended):
  For each method (standard ZZ-cost/Rx-mixer, xbasis XX-cost/Rz-mixer),
  each p, and each noise condition (NOISELESS vs FakeMarrakesh-NOISY):
    - COBYLA optimization from R independent random restarts
    - report the DISTRIBUTION of best approximation ratios across restarts
      (this distribution IS the optimizer-variance Ember C4079 flagged)
    - decompose via the noiseless-vs-noisy split: if standard beats xbasis
      even NOISELESSLY -> optimizer/landscape effect, NOT decoherence;
      if they tie noiselessly and diverge only under noise -> decoherence
      (and X-basis "immunity" would show as xbasis degrading LESS).

  Physics sanity check (built in): noiselessly, X-basis QAOA is the
  Hadamard-conjugate of standard QAOA at the same angles, so their
  NOISELESS optimized ratios should coincide (a control). If they don't,
  the comparison itself is mis-specified.

Zero QPU (FakeMarrakesh noise model + Aer, 4 qubits).
"""
import argparse
import json
import time
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

EDGES = [(0, 1), (1, 2), (2, 3), (0, 3)]
N_QUBITS = 4
MAX_CUT = 4


def compute_cut_value(bitstring, edges):
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def build_standard_qaoa(p, gamma, beta):
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    qc.h(range(N_QUBITS))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in EDGES:
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
        for q in range(N_QUBITS):
            qc.rx(2 * b, q)
    qc.measure(range(N_QUBITS), range(N_QUBITS))
    return qc


def build_xbasis_qaoa(p, gamma, beta):
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    qc.h(range(N_QUBITS))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in EDGES:
            qc.h(i); qc.h(j)
            qc.cx(i, j); qc.rz(2 * g, j); qc.cx(i, j)
            qc.h(i); qc.h(j)
        for q in range(N_QUBITS):
            qc.rz(2 * b, q)
    qc.h(range(N_QUBITS))
    qc.measure(range(N_QUBITS), range(N_QUBITS))
    return qc


def approximation_ratio(counts):
    total = sum(counts.values())
    exp_cut = 0.0
    for bitstr, c in counts.items():
        bs = bitstr[::-1]  # qiskit LSB-first
        exp_cut += compute_cut_value(bs, EDGES) * c / total
    return exp_cut / MAX_CUT


def make_objective(build_fn, p, sim, shots):
    def obj(params):
        gamma = params[:p]
        beta = params[p:]
        qc = build_fn(p, gamma, beta)
        counts = sim.run(qc, shots=shots).result().get_counts()
        return -approximation_ratio(counts)  # minimize -> maximize ratio
    return obj


def optimize_method(build_fn, p, sim, shots, restarts, rng, maxiter):
    """Run `restarts` COBYLA optimizations from random inits.
    Returns (best_ratio, list_of_restart_ratios)."""
    restart_ratios = []
    for _ in range(restarts):
        x0 = rng.uniform(0, np.pi, size=2 * p)
        res = minimize(make_objective(build_fn, p, sim, shots), x0,
                       method='COBYLA', options={'maxiter': maxiter})
        restart_ratios.append(-res.fun)
    return max(restart_ratios), restart_ratios


def bootstrap_gap_ci(std_ratios, x_ratios, rng, n_boot=2000):
    """CI on (best_standard - best_xbasis) by resampling restarts."""
    std = np.array(std_ratios); x = np.array(x_ratios)
    gaps = []
    for _ in range(n_boot):
        gaps.append(np.max(rng.choice(std, size=len(std), replace=True))
                    - np.max(rng.choice(x, size=len(x), replace=True)))
    lo, hi = np.percentile(gaps, [2.5, 97.5])
    return float(lo), float(hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true', help='tiny run to check tractability')
    ap.add_argument('--restarts', type=int, default=16)
    ap.add_argument('--shots', type=int, default=4096)
    ap.add_argument('--maxiter', type=int, default=120)
    ap.add_argument('--pvals', type=str, default='1,2,3')
    ap.add_argument('--out', type=str,
                    default='/droid/repos/quantum/experiments/38b-xbasis-qaoa-optimized-results.json')
    args = ap.parse_args()

    if args.smoke:
        args.restarts, args.shots, args.maxiter, args.pvals = 3, 1024, 40, '1,2'

    p_values = [int(x) for x in args.pvals.split(',')]
    rng = np.random.default_rng(38)

    # Noiseless and noisy simulators (same run() API -> one code path)
    noiseless = AerSimulator()
    fake = FakeMarrakesh()
    noisy = AerSimulator(noise_model=NoiseModel.from_backend(fake))
    conditions = {'noiseless': noiseless, 'noisy': noisy}

    methods = {'standard': build_standard_qaoa, 'xbasis': build_xbasis_qaoa}

    results = {
        'experiment': '38b',
        'title': 'X-Basis QAOA vs Standard QAOA — PROPERLY OPTIMIZED (COBYLA multi-restart, noiseless-vs-noisy)',
        'author': 'Elder C6347',
        'corrects': 'Exp38 (analytic-params N=1 mislabeled COBYLA at C5656)',
        'backend': 'FakeMarrakesh + Aer-noiseless',
        'problem': '4-node ring MaxCut (max_cut=4)',
        'config': {'restarts': args.restarts, 'shots': args.shots,
                   'maxiter': args.maxiter, 'p_values': p_values},
        'data': {},
    }

    t0 = time.time()
    for cond, sim in conditions.items():
        results['data'][cond] = {}
        for mname, build_fn in methods.items():
            results['data'][cond][mname] = {}
            for p in p_values:
                best, ratios = optimize_method(build_fn, p, sim, args.shots,
                                               args.restarts, rng, args.maxiter)
                results['data'][cond][mname][p] = {
                    'best_ratio': float(best),
                    'restart_ratios': [float(r) for r in ratios],
                    'mean_ratio': float(np.mean(ratios)),
                    'std_ratio': float(np.std(ratios)),
                }
                print(f"  [{cond:9s}] {mname:8s} p={p}: best={best:.4f} "
                      f"mean={np.mean(ratios):.4f} std={np.std(ratios):.4f} "
                      f"(n={len(ratios)})  t={time.time()-t0:.1f}s", flush=True)

    # Analysis: gap + CI per (condition, p); noiseless-vs-noisy decomposition
    results['analysis'] = {}
    for cond in conditions:
        results['analysis'][cond] = {}
        for p in p_values:
            std_r = results['data'][cond]['standard'][p]['restart_ratios']
            x_r = results['data'][cond]['xbasis'][p]['restart_ratios']
            gap = max(std_r) - max(x_r)
            lo, hi = bootstrap_gap_ci(std_r, x_r, rng)
            excludes0 = (lo > 0) or (hi < 0)
            results['analysis'][cond][p] = {
                'best_standard': float(max(std_r)),
                'best_xbasis': float(max(x_r)),
                'gap_std_minus_x': float(gap),
                'gap_ci95': [lo, hi],
                'gap_ci_excludes_0': bool(excludes0),
            }
            print(f"  ANALYSIS [{cond:9s}] p={p}: gap(std-x)={gap:+.4f} "
                  f"CI95=[{lo:+.4f},{hi:+.4f}] excl0={excludes0}", flush=True)

    results['wall_seconds'] = round(time.time() - t0, 1)
    with open(args.out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {args.out}  ({results['wall_seconds']}s)")
    return results


if __name__ == '__main__':
    main()
