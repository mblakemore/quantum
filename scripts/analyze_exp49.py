#!/usr/bin/env python3
"""
EXP49 Analysis Script
Elder C5732 | 2026-06-08
Run AFTER exp49_results.json is saved to get comprehensive analysis.
"""
import json
import numpy as np
from scipy import stats
import sys
import os

RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '..', 'experiments', 'exp49_results.json')

def analyze():
    with open(RESULTS_FILE) as f:
        data = json.load(f)

    results3 = data['results']['3']
    results5 = data['results']['5']
    analysis = data['analysis']

    seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
    p3 = [results3[str(s)] for s in seeds]
    p5 = [results5[str(s)] for s in seeds]

    thresh = 0.640
    n_esc3 = sum(1 for r in p3 if r >= thresh)
    n_esc5 = sum(1 for r in p5 if r >= thresh)

    print("="*70)
    print("EXP49 FORMAL RESULTS: Seed-Locked Escape Characterization")
    print("="*70)

    print("\n=== p=3 Results (baseline) ===")
    for s, r in zip(seeds, p3):
        status = "ESCAPED" if r >= thresh else "trapped"
        print(f"  Seed {s}: {r:.4f} [{status}]")
    print(f"Escape rate: {n_esc3}/{len(p3)} = {n_esc3/len(p3):.0%}")

    print("\n=== p=5 Results (test) ===")
    for s, r3, r5 in zip(seeds, p3, p5):
        s3 = "ESCAPED" if r3 >= thresh else "trapped"
        s5 = "ESCAPED" if r5 >= thresh else "trapped"
        consistent = "SAME" if (r3 >= thresh) == (r5 >= thresh) else "DIFF"
        print(f"  Seed {s}: p3={r3:.4f}[{s3}] → p5={r5:.4f}[{s5}] | {consistent}")
    print(f"Escape rate: {n_esc5}/{len(p5)} = {n_esc5/len(p5):.0%}")

    print("\n=== Formal Analysis ===")
    pearson_r = analysis['pearson_r']
    pearson_p = analysis['pearson_p']
    consistency = analysis['consistency_rate']
    verdict = data['verdict']
    interpretation = data['interpretation']

    print(f"Pearson r = {pearson_r:.4f} (p = {pearson_p:.4f})")
    print(f"Consistency rate: {consistency:.1%} ({int(consistency*10)}/10 same outcome)")
    print(f"\nVERDICT: {verdict}")
    print(f"INTERPRETATION: {interpretation}")

    # Bayesian posterior (final)
    print("\n=== Bayesian Final Posterior ===")
    prior0 = {"H1": 0.55, "H2": 0.30, "H3": 0.15}
    # We need to compute this properly from the data
    # Using sequence of updates
    h1, h2, h3 = prior0["H1"], prior0["H2"], prior0["H3"]

    for s, r3, r5 in zip(seeds, p3, p5):
        escaped = r5 >= thresh
        if escaped:
            # P(escape|H1)=0.95, P(escape|H2)=0.40, P(escape|H3)=0.65
            p1, p2, p3h = 0.95, 0.40, 0.65
        else:
            # P(trapped|H1)=0.05, P(trapped|H2)=0.60, P(trapped|H3)=0.35
            p1, p2, p3h = 0.05, 0.60, 0.35

        norm = p1*h1 + p2*h2 + p3h*h3
        h1 = p1*h1/norm
        h2 = p2*h2/norm
        h3 = p3h*h3/norm

    print(f"H1 (seed-locked): {h1:.4f}")
    print(f"H2 (stochastic): {h2:.4f}")
    print(f"H3 (partial): {h3:.4f}")

    # Key practical finding
    print("\n=== Key Finding: COBYLA Compensation Threshold ===")
    print(f"p=3: {n_esc3}/10 escaped (100%) — 6 COBYLA params × 5 iter/param")
    print(f"p=5: {n_esc5}/10 escaped ({n_esc5*10:.0f}%) — 10 COBYLA params × 3 iter/param")
    print(f"Iter/dim ratio: p=3 has {5.0:.1f}x, p=5 has {3.0:.1f}x")
    print(f"NEXT: Exp50-revised — do(MAX_ITER=50) at p=5 → test if escape rate → 100%")

    # Secondary analysis
    if 'initial_params' in data.get('secondary_analysis', {}):
        sec = data['secondary_analysis']['initial_params']
        print("\n=== Secondary Analysis: Initial Parameters ===")
        for group, info in sec.items():
            print(f"  {group}: gamma_mean={info.get('gamma_mean',0):.4f} "
                  f"beta_mean={info.get('beta_mean',0):.4f} "
                  f"n={info.get('n',0)}")

if __name__ == '__main__':
    if not os.path.exists(RESULTS_FILE):
        print("Results file not yet available. Run after exp49_results.json is saved.")
        sys.exit(1)
    analyze()
