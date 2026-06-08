#!/usr/bin/env python3
"""
Exp48 CONTINUATION: Start from p=4 (p=2 and p=3 already complete).
Known results from prior run log (Jun 7 13:53 UTC).
Whisper C3990 - Jun 8 2026 03:15 UTC
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20, SWEET_SPOT_BUDGET,
    brute_force_max_cut, build_parameterized_standard_qaoa,
    build_parameterized_xbasis_qaoa, optimize_with_cached_circuit,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 256
N_REPS = 5
MAX_ITER = 30
OPT_LEVEL = 1
P_VALUES = [2, 3, 4, 5]

if __name__ == '__main__':
    print("Exp48 CONTINUATION: p=4 and p=5 only (p=2/p=3 seeded)", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges, shots={SHOTS}, reps={N_REPS}", flush=True)

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    print("Backend ready. Computing MaxCut...", flush=True)
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)

    # Seed p=2 and p=3 from prior run log
    data = {
        2: {
            'standard': [0.6363, 0.6077, 0.5747, 0.6071, 0.6286],
            'xbasis':   [0.5568, 0.6450, 0.6418, 0.6907, 0.5975],
        },
        3: {
            'standard': [0.5981, 0.6196, 0.5941, 0.6274, 0.6318],
            'xbasis':   [0.5751, 0.5950, 0.5924, 0.6671, 0.6735],
        },
    }
    print("\nSeeded p=2/p=3 from prior run (Jun 7 13:53 UTC log).", flush=True)
    for p in [2, 3]:
        s = np.array(data[p]['standard']); x = np.array(data[p]['xbasis'])
        print(f"  p={p}: std mean={s.mean():.4f}±{s.std(ddof=1):.4f}  xb mean={x.mean():.4f}±{x.std(ddof=1):.4f}", flush=True)

    builders = [('standard', build_parameterized_standard_qaoa),
                ('xbasis',   build_parameterized_xbasis_qaoa)]

    start = time.time()

    for p in [4, 5]:
        h = N_QUBITS_20 * 2 + len(EDGES_20) * 4 * p
        print(f"\n{'━'*60}", flush=True)
        print(f"━━ p={p} ({h} H-gates, {100*h/SWEET_SPOT_BUDGET:.0f}% budget) ━━", flush=True)
        data[p] = {}
        for circ_name, build_fn in builders:
            template, gpar, bpar = build_fn(p, N_QUBITS_20, EDGES_20)
            tqc = transpile(template, sim, optimization_level=OPT_LEVEL)
            ratios = []
            for rep in range(N_REPS):
                t0 = time.time()
                ratio, _ = optimize_with_cached_circuit(
                    tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
                    N_QUBITS_20, SHOTS, n_restarts=1, max_iter=MAX_ITER)
                ratios.append(round(float(ratio), 4))
                print(f"    {circ_name:9s} rep{rep+1}: ratio={ratio:.4f} ({time.time()-t0:.0f}s)", flush=True)
            data[p][circ_name] = ratios
            print(f"    {circ_name:9s} mean={np.mean(ratios):.4f} std={np.std(ratios,ddof=1):.4f} "
                  f"[{min(ratios):.4f}, {max(ratios):.4f}]", flush=True)

    elapsed = time.time() - start
    print(f"\nTotal continuation runtime: {elapsed/60:.1f} min", flush=True)

    # ─── Summary table ───
    print("\n" + "═"*78, flush=True)
    print("VARIANCE-DEPTH SUMMARY (ALL DEPTHS)", flush=True)
    print(f"{'p':>3}  {'std_mean':>9}  {'std_std':>8}  {'xb_mean':>8}  {'xb_std':>8}  "
          f"{'gap_mean':>9}  {'consistency':>20}", flush=True)
    print("─"*78, flush=True)

    summary = {}
    xb_stds = []
    std_stds = []

    for p in P_VALUES:
        s = np.array(data[p]['standard']); x = np.array(data[p]['xbasis'])
        s_std = float(np.std(s, ddof=1)); x_std = float(np.std(x, ddof=1))
        gap_mean = float(x.mean() - s.mean())
        gap_se = float(np.sqrt(s.var(ddof=1)/len(s) + x.var(ddof=1)/len(x)))
        xb_stds.append(x_std); std_stds.append(s_std)
        summary[p] = {
            'std_ratios': list(s), 'xbasis_ratios': list(x),
            'std_mean': round(float(s.mean()), 4), 'std_std': round(s_std, 4),
            'xb_mean': round(float(x.mean()), 4), 'xb_std': round(x_std, 4),
            'gap_mean': round(gap_mean, 4), 'gap_se': round(gap_se, 4),
            'xbasis_wins_mean': gap_mean > 0,
            'variance_crossover': x_std > s_std,
        }
        consistency = 'STD more consistent' if x_std > s_std else 'xbasis more consistent'
        print(f"  p={p}  std={s.mean():.4f}±{s_std:.4f}  xb={x.mean():.4f}±{x_std:.4f}  "
              f"gap={gap_mean:+.4f}±{gap_se:.4f}  {consistency}", flush=True)

    # ─── Hypothesis verdicts ───
    print("\n" + "─"*78, flush=True)
    print("HYPOTHESIS VERDICTS", flush=True)
    h1 = all(xb_stds[i] <= xb_stds[i+1] for i in range(len(xb_stds)-1))
    h2 = all(std_stds[i] >= std_stds[i+1] for i in range(len(std_stds)-1))
    var_crossovers = [p for p in P_VALUES if summary[p]['variance_crossover']]
    h3 = len(var_crossovers) > 0
    h4 = all(summary[p]['xbasis_wins_mean'] for p in P_VALUES)
    print(f"  H1 (xbasis var increases monotonically): {'CONFIRMED ✓' if h1 else 'REFUTED ✗'}", flush=True)
    print(f"       xbasis std: {[round(v,4) for v in xb_stds]}", flush=True)
    print(f"  H2 (standard var decreases monotonically): {'CONFIRMED ✓' if h2 else 'REFUTED ✗'}", flush=True)
    print(f"       standard std: {[round(v,4) for v in std_stds]}", flush=True)
    print(f"  H3 (variance crossover): {'CONFIRMED ✓' if h3 else 'REFUTED ✗'}", flush=True)
    if h3: print(f"       Crossover depths: {var_crossovers}", flush=True)
    print(f"  H4 (xbasis wins mean all depths): {'CONFIRMED ✓' if h4 else 'REFUTED ✗'}", flush=True)
    print(f"       xbasis wins at depths: {[p for p in P_VALUES if summary[p]['xbasis_wins_mean']]}", flush=True)

    # ─── Bimodal escape probability ───
    print("\n" + "─"*78, flush=True)
    print("BIMODAL ESCAPE PROBABILITY (mu_trapped=0.5875, mu_escaped=0.6703)", flush=True)
    mu_trapped = 0.5875; mu_escaped = 0.6703; midpoint = (mu_trapped + mu_escaped) / 2
    for p in [3, 4, 5]:
        x = np.array(data[p]['xbasis'])
        n_escaped = sum(1 for v in x if v >= midpoint)
        p_escape = n_escaped / N_REPS
        mu_std = summary[p]['std_mean']
        p_crit = (mu_std - mu_trapped) / (mu_escaped - mu_trapped)
        h4_margin = (p_escape - p_crit) * 100
        print(f"  p={p}: escaped={n_escaped}/{N_REPS} (P_esc={p_escape:.0%}), "
              f"P_crit={p_crit:.1%}, H4_margin={h4_margin:+.1f}pp", flush=True)

    out = {
        'experiment': 'Exp48-variance-depth-profile',
        'continuation': True, 'continuation_cycle': 'C3990',
        'original_cycle': 'C3613', 'date': '2026-06-08',
        'backend': 'FakeMarrakesh', 'shots': SHOTS, 'n_reps': N_REPS,
        'max_iter': MAX_ITER, 'p_values': P_VALUES, 'max_cut': max_cut,
        'p2_p3_source': 'seeded from prior run log (Jun 7 13:53 UTC)',
        'summary': {str(p): summary[p] for p in P_VALUES},
        'hypothesis_verdicts': {
            'H1_xbasis_var_increases': h1,
            'H2_standard_var_decreases': h2,
            'H3_variance_crossover_exists': h3,
            'H4_xbasis_wins_mean_all_depths': h4,
            'variance_crossover_depths': var_crossovers,
        },
        'bimodal_reference': {'mu_trapped': mu_trapped, 'mu_escaped': mu_escaped},
        'runtime_continuation_sec': round(elapsed, 1),
    }
    outfile = '/mnt/droid/repos/quantum/experiments/exp48_results.json'
    with open(outfile, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved: {outfile}", flush=True)
    print("Exp48 COMPLETE.", flush=True)
