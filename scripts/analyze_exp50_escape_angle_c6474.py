#!/usr/bin/env python3
"""
Exp50 Phase-2 Initial-Angle Analysis — grades pred_c5727_q003 / Exp50 H2_primary.
Elder C6474 | 2026-07-15

QUESTION (pre-registered, Ember C3658 Exp50 H2 + Elder pred_c5727_q003):
  Do p=3 ESCAPER seeds have systematically LOWER mean initial gamma than TRAPPER seeds?

DATA: real cached outcomes, Exp50c Phase C (p=3, MAX_ITER=30, xbasis QAOA, 26-node
      MaxCut, FakeMarrakesh noise). Zero new simulation — escape labels are the
      documented Phase-C outcomes; initial angles are DETERMINISTIC given the seed.

RECONSTRUCTION (verified against scripts/run_exp49_seed_locked_escape.py:79-85 and
      run_exp50c_phase_bc_continuation.py:97):
        np.random.seed(seed); x0 = np.random.uniform(0, 2*pi, 2*p)
        gamma = x0[:p], beta = x0[p:]     (evaluate_with_transpiled: params[:p]=gamma)
  NOTE: actual range is [0, 2*pi], NOT [0, pi/2] as the Exp50 pre-reg TEXT stated.
        => the absolute sub-threshold "gamma < pi/4" is mis-specified; graded below
           against the true null mean E[gamma]=pi. The DIRECTIONAL claim (escapers
           lower than trappers) is range-independent and is the primary grade.

METHOD: exact one-sided permutation test (the correct tool at N=10, not a t-test).
"""
import numpy as np
from itertools import combinations
from math import comb, pi

P = 3
SEEDS = list(range(42, 52))                       # 42..51
ESCAPERS = {42, 45, 47, 48, 49, 50, 51}           # Exp50c Phase C (p=3)
TRAPPERS = {43, 44, 46}
assert ESCAPERS | TRAPPERS == set(SEEDS) and not (ESCAPERS & TRAPPERS)

def x0_for(seed, p=P):
    np.random.seed(seed)
    return np.random.uniform(0, 2 * pi, 2 * p)

# Reconstruct initial angles
rows = {}
for s in SEEDS:
    x0 = x0_for(s)
    g, b = x0[:P], x0[P:]
    rows[s] = dict(gamma=g, beta=b, mean_gamma=g.mean(), mean_beta=b.mean(),
                   label='E' if s in ESCAPERS else 'T')

print("=" * 68)
print("Exp50 Phase-2 initial-angle analysis (p=3) — Elder C6474")
print("=" * 68)
print(f"{'seed':>4} {'lbl':>3} {'mean_gamma':>11} {'mean_beta':>10}   gamma_layers")
for s in SEEDS:
    r = rows[s]
    print(f"{s:>4} {r['label']:>3} {r['mean_gamma']:>11.4f} {r['mean_beta']:>10.4f}   "
          f"[{', '.join(f'{v:.3f}' for v in r['gamma'])}]")

esc = np.array([rows[s]['mean_gamma'] for s in ESCAPERS])
tra = np.array([rows[s]['mean_gamma'] for s in TRAPPERS])
diff = esc.mean() - tra.mean()                    # pred: NEGATIVE (escapers lower)

# pooled-SD Cohen's d
n1, n2 = len(esc), len(tra)
sp = np.sqrt(((n1 - 1)*esc.var(ddof=1) + (n2 - 1)*tra.var(ddof=1)) / (n1 + n2 - 2))
d = diff / sp if sp > 0 else float('nan')

# Exact one-sided permutation test over all C(10,3) trapper-set choices.
# Statistic = (mean_gamma of the 3 "trappers") - (mean of the other 7).
# Observed pred direction: trappers HIGHER => observed statistic large & positive.
vals = {s: rows[s]['mean_gamma'] for s in SEEDS}
all_mean = np.mean(list(vals.values()))
def stat(trap3):
    t = np.array([vals[s] for s in trap3])
    e = np.array([vals[s] for s in SEEDS if s not in trap3])
    return t.mean() - e.mean()
obs = stat(tuple(TRAPPERS))
perm = [stat(c) for c in combinations(SEEDS, 3)]
perm = np.array(perm)
# one-sided p: P(random 3-subset has trapper-minus-rest >= observed)
p_perm = np.mean(perm >= obs - 1e-12)

print("\n--- PRIMARY: mean initial gamma, escaper vs trapper ---")
print(f"  escaper mean_gamma = {esc.mean():.4f}  (n={n1})")
print(f"  trapper mean_gamma = {tra.mean():.4f}  (n={n2})")
print(f"  difference (E - T) = {diff:+.4f}   [pred_c5727_q003: NEGATIVE]")
print(f"  Cohen's d          = {d:+.3f}   (pred H2 wanted |d|>0.3, E<T)")
print(f"  exact permutation p (one-sided, trappers higher) = {p_perm:.4f}  "
      f"(N_perm={comb(10,3)})")

# Absolute sub-claim, corrected to true range
print("\n--- SUB-CLAIM (mis-specified in pre-reg): escaper mean_gamma < pi/4 ---")
print(f"  actual sampling range [0, 2pi] -> null E[gamma] = pi = {pi:.4f}")
print(f"  escaper mean_gamma {esc.mean():.4f} vs pi/4={pi/4:.4f} (orig) / pi={pi:.4f} (true null)")

# Exploratory (multiplicity-flagged): mean beta
esc_b = np.array([rows[s]['mean_beta'] for s in ESCAPERS])
tra_b = np.array([rows[s]['mean_beta'] for s in TRAPPERS])
print("\n--- EXPLORATORY (not pre-registered; multiplicity uncontrolled) ---")
print(f"  mean_beta  escaper {esc_b.mean():.4f} vs trapper {tra_b.mean():.4f} "
      f"(diff {esc_b.mean()-tra_b.mean():+.4f})")

verdict = ("SUPPORTED" if (diff < 0 and p_perm < 0.05 and abs(d) > 0.3)
           else "DIRECTION-ONLY" if diff < 0
           else "REFUTED")
print("\n" + "=" * 68)
print(f"VERDICT pred_c5727_q003 (directional, primary): {verdict}")
print("=" * 68)

import json
out = dict(cycle="C6474", experiment="exp50-phase2-angle", depth=P,
          escapers=sorted(ESCAPERS), trappers=sorted(TRAPPERS),
          escaper_mean_gamma=float(esc.mean()), trapper_mean_gamma=float(tra.mean()),
          diff_E_minus_T=float(diff), cohens_d=float(d),
          exact_perm_p_onesided=float(p_perm), n_perm=comb(10, 3),
          escaper_mean_beta=float(esc_b.mean()), trapper_mean_beta=float(tra_b.mean()),
          sampling_range="[0,2pi]", prereg_stated_range="[0,pi/2]_WRONG",
          verdict=verdict,
          note="N=10 (7E/3T) underpowered; exact permutation over C(10,3)=120; "
               "escape labels=Exp50c Phase C p=3; zero new simulation")
json.dump(out, open("results/exp50_phase2_angle_c6474.json", "w"), indent=2)
print("\nwrote results/exp50_phase2_angle_c6474.json")
