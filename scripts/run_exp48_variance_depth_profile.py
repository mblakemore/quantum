#!/usr/bin/env python3
"""
Exp48: Variance-Depth Profile — xbasis vs standard variance across p=2,3,4,5
Ember C3613 | 2026-06-07

CONTEXT: Exp47 (3 restarts, p=3,5) revealed a striking asymmetry:
  - xbasis std  : 0.0085 (p=3) → 0.0184 (p=5)  [+116%, INCREASES with depth]
  - standard std: 0.0183 (p=3) → 0.0091 (p=5)  [-50%,  DECREASES with depth]

This is counter-intuitive: xbasis wins in MEAN but becomes LESS CONSISTENT at higher
depth while standard becomes MORE consistent. Open questions:
  1. Is this monotonic or does it peak/valley at some intermediate depth?
  2. At what depth does xbasis variance exceed standard variance?
  3. Is the variance crossover sharper than the mean gap crossover?

METHOD: p=2,3,4,5 × {xbasis, standard} × 5 restarts each.
  - 5 restarts (vs 3 in Exp47) gives better variance estimate.
  - p=2 and p=4 fill the gaps in the variance curve.
  - Primary metric: std(ratios) per condition at each depth.
  - Secondary: mean gap and significance (same as Exp47).

HYPOTHESIS (pre-registered at C3613):
  H1: xbasis variance monotonically increases with depth (p=2→3→4→5)
  H2: standard variance monotonically decreases with depth (p=2→3→4→5)
  H3: variance crossover (xbasis_std > standard_std) occurs at some p ∈ {3,4,5}
  H4: mean gap (xbasis - standard) remains positive at all depths (no crossover)

MECHANISM HYPOTHESES:
  A: COBYLA landscape roughness hypothesis — xbasis initialization starts near
     phase transitions in the energy landscape. At higher p, more local minima
     exist near the xbasis starting point, creating wider outcome distribution.
  B: Barren plateau entry hypothesis — xbasis hits barren plateau intermittently
     at higher depths (some restarts escape, some don't), creating bimodal
     distribution visible as high variance.
  C: Standard convergence basin hypothesis — all-zeros standard initialization
     converges to the same basin at higher depths (lower variance), but this basin
     is suboptimal (lower mean).
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
N_REPS = 5           # 5 restarts per condition (vs Exp47's 3) for better variance estimate
MAX_ITER = 30
OPT_LEVEL = 1
P_VALUES = [2, 3, 4, 5]   # full depth sweep (vs Exp47's p=3,5 only)

if __name__ == '__main__':
    print("Exp48: Variance-Depth Profile (p=2,3,4,5 x 5 reps each)", flush=True)
    print(f"Graph: {N_QUBITS_20} qubits, {len(EDGES_20)} edges, "
          f"shots={SHOTS}, reps={N_REPS}, max_iter={MAX_ITER}", flush=True)
    print("Hypotheses:", flush=True)
    print("  H1: xbasis variance monotonically INCREASES with depth", flush=True)
    print("  H2: standard variance monotonically DECREASES with depth", flush=True)
    print("  H3: variance crossover (xbasis_std > std_std) at some p in {3,4,5}", flush=True)
    print("  H4: mean gap (xbasis > standard) at ALL depths (no mean crossover)", flush=True)
    print()

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
                ratio, _ = optimize_with_cached_circuit(
                    tqc, gpar, bpar, p, sim, EDGES_20, max_cut,
                    N_QUBITS_20, SHOTS, n_restarts=1, max_iter=MAX_ITER)
                ratios.append(round(float(ratio), 4))
                print(f"    {circ_name:9s} rep{rep+1}: ratio={ratio:.4f} "
                      f"({time.time()-t0:.0f}s)", flush=True)
            data[p][circ_name] = ratios
            print(f"    {circ_name:9s} mean={np.mean(ratios):.4f} "
                  f"std={np.std(ratios, ddof=1):.4f} "
                  f"[{min(ratios):.4f}, {max(ratios):.4f}]", flush=True)

    elapsed = time.time() - start
    print(f"\nTotal runtime: {elapsed/60:.1f} min", flush=True)

    # ─── Summary table ───
    print("\n" + "═"*78, flush=True)
    print("VARIANCE-DEPTH SUMMARY", flush=True)
    print(f"{'p':>3}  {'std_mean':>9}  {'std_var':>8}  {'xb_mean':>8}  {'xb_var':>8}  "
          f"{'gap_mean':>9}  {'var_winner':>10}", flush=True)
    print("─"*78, flush=True)

    summary = {}
    xb_stds = []
    std_stds = []

    for p in P_VALUES:
        s = np.array(data[p]['standard'])
        x = np.array(data[p]['xbasis'])
        s_std = float(np.std(s, ddof=1))
        x_std = float(np.std(x, ddof=1))
        gap_mean = float(x.mean() - s.mean())  # positive = xbasis wins
        gap_se = float(np.sqrt(s.var(ddof=1)/len(s) + x.var(ddof=1)/len(x)))
        var_winner = 'standard' if x_std > s_std else 'xbasis'  # lower variance = more consistent
        consistent_winner = 'standard' if x_std > s_std else 'xbasis'

        xb_stds.append(x_std)
        std_stds.append(s_std)

        summary[p] = {
            'std_ratios': list(s), 'xbasis_ratios': list(x),
            'std_mean': round(float(s.mean()), 4), 'std_std': round(s_std, 4),
            'xb_mean': round(float(x.mean()), 4), 'xb_std': round(x_std, 4),
            'gap_mean': round(gap_mean, 4), 'gap_se': round(gap_se, 4),
            'xbasis_wins_mean': gap_mean > 0,
            'variance_crossover': x_std > s_std,  # True = standard more consistent at this depth
        }
        print(f"  p={p}  std={s.mean():.4f}±{s_std:.4f}  xb={x.mean():.4f}±{x_std:.4f}  "
              f"gap={gap_mean:+.4f}±{gap_se:.4f}  "
              f"{'STD more consistent' if x_std > s_std else 'xbasis more consistent'}", flush=True)

    # ─── Hypothesis verdicts ───
    print("\n" + "─"*78, flush=True)
    print("HYPOTHESIS VERDICTS", flush=True)

    # H1: xbasis variance monotonically increases
    h1 = all(xb_stds[i] <= xb_stds[i+1] for i in range(len(xb_stds)-1))
    print(f"  H1 (xbasis var increases monotonically): {'CONFIRMED ✓' if h1 else 'REFUTED ✗'}", flush=True)
    print(f"       xbasis std by depth: {[round(v,4) for v in xb_stds]}", flush=True)

    # H2: standard variance monotonically decreases
    h2 = all(std_stds[i] >= std_stds[i+1] for i in range(len(std_stds)-1))
    print(f"  H2 (standard var decreases monotonically): {'CONFIRMED ✓' if h2 else 'REFUTED ✗'}", flush=True)
    print(f"       standard std by depth: {[round(v,4) for v in std_stds]}", flush=True)

    # H3: variance crossover exists (at some depth xbasis_std > standard_std)
    var_crossovers = [p for p in P_VALUES if summary[p]['variance_crossover']]
    h3 = len(var_crossovers) > 0
    print(f"  H3 (variance crossover at some depth): {'CONFIRMED ✓' if h3 else 'REFUTED ✗'}", flush=True)
    if h3:
        print(f"       Variance crossover depths: {var_crossovers}", flush=True)

    # H4: mean gap positive at all depths (xbasis wins mean everywhere)
    h4 = all(summary[p]['xbasis_wins_mean'] for p in P_VALUES)
    print(f"  H4 (xbasis wins mean at all depths): {'CONFIRMED ✓' if h4 else 'REFUTED ✗'}", flush=True)
    depths_where_xb_wins = [p for p in P_VALUES if summary[p]['xbasis_wins_mean']]
    print(f"       Depths where xbasis wins mean: {depths_where_xb_wins}", flush=True)

    out = {
        'experiment': 'Exp48-variance-depth-profile',
        'cycle': 'C3613',
        'date': '2026-06-07',
        'backend': 'FakeMarrakesh',
        'shots': SHOTS,
        'n_reps': N_REPS,
        'max_iter': MAX_ITER,
        'p_values': P_VALUES,
        'max_cut': max_cut,
        'summary': {str(p): summary[p] for p in P_VALUES},
        'hypothesis_verdicts': {
            'H1_xbasis_var_increases': h1,
            'H2_standard_var_decreases': h2,
            'H3_variance_crossover_exists': h3,
            'H4_xbasis_wins_mean_all_depths': h4,
            'variance_crossover_depths': var_crossovers,
        },
        'mechanism_hypothesis': 'A (landscape roughness) or B (barren plateau entry) - see script docstring',
        'exp47_reference': {
            'p3_xbasis_std': 0.0085, 'p3_standard_std': 0.0183,
            'p5_xbasis_std': 0.0184, 'p5_standard_std': 0.0091,
        },
        'runtime_sec': round(elapsed, 1),
    }
    outfile = '/mnt/droid/repos/quantum/experiments/exp48_results.json'
    with open(outfile, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved: {outfile}\nExp48 complete.", flush=True)
