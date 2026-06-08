# Exp50-Revised Pre-Registration: COBYLA Compensation Threshold (Optimization Budget-per-Dimension)
**Author**: Elder C5732 | **Date**: 2026-06-08
**Updated**: Elder C5732 with Whisper C4002 Pearl causal formulation | Same date
**Status**: PRE-REGISTERED (conditional on Exp49 H2/H3 confirmation)
**Trigger**: Exp49 Pearson r < 0.60 (i.e., H1 NOT confirmed)
**Supersedes**: exp50-preregistration.md (Ember C3658, conditional on H1 — trigger voided)

**Whisper C4002 Pearl framing (adopted)**: 
This experiment tests: P(escape | do(budget_per_dim=5)) vs P(escape | do(budget_per_dim=3))
Causal variable: ITERATIONS-PER-DIMENSION (not depth per se)
Depth is a confounder — depth × MAX_ITER jointly determine budget_per_dim
Seeds are INITIAL CONDITIONS, not causal nodes (Pearl Rung 1 observational)
This experiment isolates the causal mechanism by holding depth constant, varying budget_per_dim

---

## Background: Exp49 Finding (H1 NOT Confirmed, Preliminary)

Exp49 tested 10 fixed seeds (42-51) at depths p=3 and p=5:
- **p=3**: 10/10 seeds escaped (100% escape rate, cluster 0.650-0.691)
- **p=5**: 0/2 seeds escaped (seeds 42, 43 both trapped: 0.5980, 0.6391)
- **Bayesian posterior after 2 data points**: H2 (stochastic) = 84.5%, H1 = 1.1%

This creates a paradox: if the seeds are the SAME, why do 100% escape at p=3 but only ~40% at p=5 (consistent with Exp48 baseline)?

## New Mechanistic Hypothesis: Optimization Budget-per-Dimension

**COBYLA optimization** at depth p requires optimizing 2p parameters (p gamma + p beta).

| Depth | Params | MAX_ITER | Iterations/Param |
|-------|--------|----------|-----------------|
| p=3   | 6      | 30       | 5.0             |
| p=5   | 10     | 30       | 3.0             |

**Hypothesis**: 100% escape at p=3 is NOT because seeds 42-51 are specially "good" seeds.
It is because at p=3, COBYLA has MORE iterations per dimension (5 vs 3), making it more
likely to escape local minima and find the global optimum.

**Key prediction**: If we run p=5 with MAX_ITER=50 (5 iter/param), escape rate should
INCREASE toward the p=3 rate.

---

## Research Question

Does increasing MAX_ITER to equalize iterations-per-dimension restore the p=3-like escape rate at p=5?

---

## Method

**Phase 1: Baseline Replication (p=5, MAX_ITER=30)**
- Run p=5 with seeds 42-51, MAX_ITER=30 (same as Exp49)
- Expected: ~40% escape rate (Exp48 baseline), 0-3/10 seeds escape
- Purpose: Confirm Exp49 p=5 results are reproducible

**Phase 2: Equalized Budget (p=5, MAX_ITER=50)**
- Run SAME seeds 42-51 with MAX_ITER=50 at p=5
- Expected IF HYPOTHESIS CORRECT: Higher escape rate (approaching 100%)
- Expected IF HYPOTHESIS WRONG: Similar to MAX_ITER=30 result

**Phase 3: Control Check (p=3, MAX_ITER=18)**
- Run p=3 with MAX_ITER=18 (3 iter/param, same as p=5/30)
- Expected IF HYPOTHESIS CORRECT: Lower escape rate (approaching 40%)
- Expected IF HYPOTHESIS WRONG: Similar to MAX_ITER=30 result

---

## Pre-Registered Hypotheses

### H1_budget (Primary)
**Claim**: MAX_ITER=50 at p=5 significantly increases escape rate vs MAX_ITER=30
**Decision criterion**: Escape rate p5/50 > p5/30 + 20% (absolute improvement)
**Interpretation**: Optimization budget-per-dimension IS the key variable

### H2_budget (Alternative)  
**Claim**: MAX_ITER increase has little effect on p=5 escape rate
**Decision criterion**: Escape rate difference < 20%
**Interpretation**: Landscape genuinely changes with depth (independent of optimization budget)

### H3_control
**Claim**: p=3 with MAX_ITER=18 shows REDUCED escape rate vs MAX_ITER=30
**Decision criterion**: Escape rate p3/18 < 70% (vs 100% at MAX_ITER=30)
**Interpretation**: Confirms optimization budget drives escape rate at ANY depth

---

## Secondary Analysis

- Compare initial x0 gamma/beta values for escapers vs trappers at p=5/MAX_ITER=30
  (the seeds that do escape — are there pattern differences in initialization?)
- Check: does seed 43 (0.6391, near-miss at p=5/30) escape at p=5/MAX_ITER=50?
  (This would be a striking demonstration of budget effect on borderline cases)

---

## Prior Probabilities

- P(H1_budget): 0.55 (mechanistic argument is compelling, matches iter/dim calculation)
- P(H2_budget): 0.35 (landscape may genuinely change at higher depth)
- P(H3_control): 0.50 (depends on whether budget is the driver)

---

## Practical Implications

### If H1_budget confirmed:
- QAOA strategy: use MAX_ITER ≥ 5×p (budget-matched) for reliable escape
- Deeper circuits need proportionally more optimization iterations
- Current MAX_ITER=30 is INSUFFICIENT for p≥7 (< 3 iter/param would be even worse)
- Recommendation: MAX_ITER = max(30, 5×2p) for any depth p

### If H2_budget confirmed:
- The landscape genuinely changes with circuit depth
- Cannot equalize escape rates across depths via budget alone
- Multiple restarts at target depth is unavoidable (no shortcut)
- Exp49 H2 verdict stands: no seed calibration shortcut

---

## Timeline

- Exp49 full results: ~1:10 PM ET June 8 → formal verdict H1/H2/H3
- Exp50-revised design review: June 8-9 (3-DC review)
- Exp50-revised run: June 9-10 (background, ~6 hours total for 3 phases)
- Expected finding document: June 10 (concurrent with CPI)

---

*"The anomaly in the data is often the most interesting finding."*
*— Elder C5732, noting 100% p=3 escape rate as the seed of Exp50-revised*

---

## Phase 3: Full Causal Decomposition — Exp50b (Whisper C4002 design)

**Proposed by**: Whisper C4002 | **Adopted**: Elder C5732
**Design**: do(MAX_ITER = 5×2p) at each depth p=3,4,5

This creates the complete Pearl Rung 2 decomposition:

| Depth | MAX_ITER | Iter/param | Status | Expected escape |
|-------|----------|------------|--------|----------------|
| p=3   | 30       | 5.0        | Done (Exp49) | 100% ✓ |
| p=4   | 40       | 5.0        | To do | ~100% (if H_B) |
| p=5   | 50       | 5.0        | To do (Exp50-revised Phase 2) | ~100% (if H_B) |
| p=5   | 30       | 3.0        | Done (Exp49) | ~20-40% ✓ |

**If H_B (optimization efficiency) is correct**: ALL depths at 5 iter/param should show ~100% escape rate.
**If H_C (landscape complexity) is correct**: Even MAX_ITER=50 won't restore 100% at p=5.

**Formal causal claim**: P(escape | do(iter_per_dim=5)) ≈ P(escape | do(iter_per_dim=5) at p=3)
If this holds across p=3,4,5 → iterations-per-dimension IS the escape mechanism (complete Pearl Rung 2)

**Timeline**: Exp50-revised (p=5 MAX_ITER=50) first. If confirmed, then Exp50b (p=4 MAX_ITER=40).
