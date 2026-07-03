#!/usr/bin/env python3
"""
Exp49 seed-locking robustness re-analysis (Elder C6347).
Applies Ember C4079's small-sample-fragility discipline to a DIFFERENT finding.
Zero QPU: recomputes from stored exp49_results.json ground truth.

Question: is the "H3 partial seed-locking SUPPORTED (r=0.572)" verdict robust,
or is it carried by a single seed (the analog of Ember's single surviving shot-level)?
"""
import json, itertools
from statistics import mean, pstdev

d = json.load(open('experiments/exp49_results.json'))
p3 = d['results']['3']; p5 = d['results']['5']
seeds = d['settings']['seeds']
THR = d['settings']['escape_threshold']  # 0.64
x = [p3[str(s)] for s in seeds]
y = [p5[str(s)] for s in seeds]

def pearson(a, b):
    n = len(a); ma, mb = mean(a), mean(b)
    num = sum((ai-ma)*(bi-mb) for ai, bi in zip(a, b))
    da = sum((ai-ma)**2 for ai in a)**0.5
    db = sum((bi-mb)**2 for bi in b)**0.5
    return num/(da*db) if da and db else float('nan')

# two-sided p via t-approx
def pval(r, n):
    import math
    if abs(r) >= 1: return 0.0
    t = r*math.sqrt((n-2)/(1-r*r))
    # survival of |t| under t(n-2), crude via normal-ish for small df use series? use scipy if avail
    try:
        from scipy import stats
        return 2*stats.t.sf(abs(t), n-2)
    except Exception:
        # normal approx (conservative-ish for df=8)
        import math
        z = abs(t)
        return 2*(0.5*math.erfc(z/math.sqrt(2)))

r_full = pearson(x, y)
p_full = pval(r_full, len(x))
print(f"FULL N={len(seeds)}: Pearson r = {r_full:.4f}, p = {p_full:.4f}")
print(f"Pre-registered criterion: r>=0.25 -> H3.  Full verdict: {'H3' if r_full>=0.25 else 'H2'}")
print()

# escape rates
esc_p3 = sum(1 for v in x if v >= THR); esc_p5 = sum(1 for v in y if v >= THR)
print(f"Escape rate (ratio>={THR}): p3 = {esc_p3}/{len(seeds)} ({esc_p3/len(seeds):.0%}), "
      f"p5 = {esc_p5}/{len(seeds)} ({esc_p5/len(seeds):.0%})")
print()

print("=== LEAVE-ONE-OUT SEED JACKKNIFE ===")
print(f"{'drop':>5} {'r_LOO':>8} {'p_LOO':>8} {'verdict':>8}  {'Δr':>8}")
loo = []
for i, s in enumerate(seeds):
    xa = x[:i]+x[i+1:]; ya = y[:i]+y[i+1:]
    r = pearson(xa, ya); p = pval(r, len(xa))
    loo.append((s, r, p))
    print(f"{s:>5} {r:>8.4f} {p:>8.4f} {'H3' if r>=0.25 else 'H2':>8}  {r-r_full:>+8.4f}")
print()

rs = [r for _, r, _ in loo]
print(f"LOO r range: [{min(rs):.4f}, {max(rs):.4f}]  spread={max(rs)-min(rs):.4f}")
flip = [s for s, r, _ in loo if r < 0.25]
print(f"Seeds whose removal FLIPS verdict to H2 (r<0.25): {flip if flip else 'NONE'}")
most = min(loo, key=lambda t: t[1])
print(f"Most influential (largest r drop when removed): seed {most[0]} -> r {most[1]:.4f}")
print()

# also: fraction of LOO subsets that are non-significant (p>0.05)
nonsig = sum(1 for _, _, p in loo if p > 0.05)
print(f"LOO subsets non-significant at p>0.05: {nonsig}/{len(loo)}  (full p={p_full:.3f} already non-sig)")
print()

# range restriction note: p3 spread (all escaped p3 -> narrow)
print(f"p3 spread: [{min(x):.4f},{max(x):.4f}] width={max(x)-min(x):.4f}  (range-restricted; all 10 escaped at p3)")
print(f"p5 spread: [{min(y):.4f},{max(y):.4f}] width={max(y)-min(y):.4f}")
