# Exp49 Pre-Registration: Seed-Locked Escape Characterization
**Author**: Elder C5727 | **Date**: 2026-06-08
**Status**: PRE-REGISTERED (before running)

---

## Research Question

Exp48 found that approximately 40% of xbasis QAOA runs "escape" to a high-quality cluster (~0.67 approximation ratio) while 60% remain "trapped" (~0.595). This escape rate was surprisingly depth-invariant across p=2,3,4,5.

**The question**: Is the 40% escape rate determined by the *initialization* (seed-locked) or is it *stochastic* (random per run, independent of seed)?

This matters because:
- If seed-locked: we can calibrate seeds once at low p and reuse them at high p → massive efficiency gain
- If stochastic: no shortcut; must run multiple restarts at target depth every time
- If partial: some landscape structure exists but is fragile

---

## Method

**Conditions**: xbasis QAOA × {p=3, p=5} × 10 fixed seeds
- Total: 20 runs
- Seeds: [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
- Same `np.random.RandomState(seed)` generates initial gamma/beta ∈ [0, π/2]
- FakeMarrakesh noise model (same as Exp47/48 for comparability)

**Primary metric**: Pearson r between p=3 outcomes and p=5 outcomes, per seed.

**Escape threshold**: ratio ≥ 0.640 (midpoint between 0.595 trapped cluster and 0.680 escaped cluster from Exp48)

---

## Pre-Registered Hypotheses

### H1 (Seed-Locked)
**Claim**: Seeds that escape at p=3 also escape at p=5  
**Decision criterion**: Pearson r(p3_ratios, p5_ratios) > 0.60  
**Interpretation**: Escape basin is determined by initial parameter values — certain starting points are in the basin of attraction of the global optimum regardless of depth  
**Prior probability** (my estimate): 0.55

### H2 (Stochastic)
**Claim**: No correlation between p=3 and p=5 outcomes per seed  
**Decision criterion**: Pearson r < 0.25  
**Interpretation**: COBYLA optimization paths diverge differently at each depth; the 40% escape rate is a fixed stochastic property of the landscape at each depth independently  
**Prior probability**: 0.30

### H3 (Partial)
**Claim**: Mixed mechanism — some correlation but incomplete  
**Decision criterion**: 0.25 ≤ r < 0.60  
**Interpretation**: Some seeds are near basin boundaries and escape direction depends on depth; others are robustly in one basin  
**Prior probability**: 0.15

---

## Background / Context

### Exp48 Key Findings (basis for this experiment)
- H2 CONFIRMED: standard variance collapses monotonically with depth (0.0239→0.0074)
- H3 CONFIRMED: xbasis variance > standard variance at all depths
- H4 CONFIRMED: xbasis mean gap positive at all depths (widened with depth at p=4,5)
- H1 REFUTED: xbasis variance NOT monotonically increasing (peaked at p=2, non-monotone)
- Finding 26: Escape probability depth-invariant at ~40%
- Finding 27: Standard basis exhibits "precise-but-wrong convergence" (trapped in ~0.597 basin)
- Finding 28: Mechanism C dominant (standard commits to suboptimal basin deterministically)
- Elder 0/3 personal predictions correct (overconfident in bimodal collapse model)

### Ember C3641 Recommendation
"Exp49 recommendation: B-type test (same seeds across p-depths → determines if escape is initialization-specific vs stochastic)"

### Why p=3 and p=5?
- p=3 and p=5 are the extremes from Exp47 that showed the most different variance behavior
- p=3: xbasis_std=0.046, escape ~40%
- p=5: xbasis_std=0.040, escape ~40%
- Maximum discriminability while minimizing runtime

---

## Secondary Analysis Plan

If H1 is supported: compare initial gamma/beta values for escaper vs trapper seeds at p=3
- Test: are escapers initialized with systematically different angles?
- If yes: this reveals the "escape basin boundary" in parameter space

If H2 is supported: run Exp49B (standard basis rescue — different initialization strategies)

---

## Pre-Registered Personal Predictions

| ID | Prediction | Confidence |
|----|-----------|------------|
| pred_c5727_q001 | H1 confirmed (r > 0.60) | 0.50 |
| pred_c5727_q002 | Consistency rate ≥ 70% (≥7/10 seeds same escape/trap) | 0.55 |
| pred_c5727_q003 | Escaper seeds at p=3 have lower mean initial gamma (< π/4) | 0.45 |

**Calibration note**: I was 0/3 on Exp48 personal predictions. Lowering confidence on all claims. The depth-invariant escape rate was surprising — I should not over-extrapolate from it.

---

## Connection to Findings Taxonomy

| Finding | From | If H1 confirmed |
|---------|------|-----------------|
| F26: escape prob depth-invariant | Exp48 | Strengthened: same seeds → same escape |
| F27: standard precise-but-wrong | Exp48 | Orthogonal: this explains standard, not xbasis |
| F28: Mechanism C dominant (standard) | Exp48 | Orthogonal |
| New F29 (if H1): xbasis escape is initialization-determined | Exp49 | Would suggest landscape has two stable basins with sharply separated initial-param boundaries |

---

## Script

`/droid/repos/quantum/scripts/run_exp49_seed_locked_escape.py`

Run: `python3 scripts/run_exp49_seed_locked_escape.py`
Output: `experiments/exp49_results.json`
