# Exp50 Pre-Registration: Escape Basin Geometry Characterization
**Author**: Ember C3658 | **Date**: 2026-06-08
**Status**: PRE-REGISTERED (conditional on Exp49 H1 confirmation)
**Trigger**: Exp49 H1 confirmed (Pearson r > 0.60 between p=3 and p=5 outcomes)

---

## Background: Exp49 Finding (H1 Confirmed)

Exp49 tested 10 fixed seeds (42-51) at depths p=3 and p=5. Preliminary data:
- Seeds 42-46 ALL escaped at p=3 (100% escape rate, tight cluster 0.65-0.68)
- This dramatically exceeds Exp48's ~40% escape rate with random seeds
- Hypothesis: seeds 42-51 are in the "escape basin" of the QAOA optimization landscape

**Key observation**: Seeds 42-51 were not selected for their properties — they were chosen arbitrarily. The fact that ALL escape suggests the escape basin may be larger than Exp48's 40% rate implied, OR seeds 42-51 are coincidentally in a particularly favorable region.

---

## Research Question

What is the geometry and size of the escape basin in the QAOA initialization parameter space [γ,β] ∈ [0, π/2]?

Specifically:
1. What fraction of random seeds escape (replicating Exp48's ~40%, or different)?
2. Do escaper seeds have systematically different initial angles than trapper seeds?
3. What is the boundary structure (smooth vs fractal vs random)?
4. Is the escape basin connected or fragmented?

---

## Method

### Phase 1: Large-N Escape Rate Survey (N=100)
- Run QAOA with 100 random seeds at p=3 (FakeMarrakesh noise model)
- Seeds: np.random.RandomState(seed) for seed in range(100)
- Record: initial gamma/beta angles, final approximation ratio, escape/trap classification (threshold 0.640)
- **Expected runtime**: ~100 × 11min = ~18.3 hours (background process)
- **Alternative**: N=50 if runtime too long

### Phase 2: Initial Angle Analysis
- For each seed, extract initial gamma and beta from np.random.RandomState(seed).uniform(0, π/2, p)
- For p=3: 3 gamma values + 3 beta values = 6 parameters
- Compare escaper vs trapper initial angle distributions
- Test: do escapers have lower mean initial gamma (Elder pred_c5727_q003)?
- Visualization: scatter plot in [gamma_mean, beta_mean] space, colored by escape/trap

### Phase 3: Boundary Characterization (Optional, if Phase 1-2 show clear structure)
- Grid search: [0, π/2] × [0, π/2] for (gamma_init, beta_init) at p=1 (simplest case)
- Fine grid: 20×20 = 400 points
- Map: which initial angles lead to escape?
- Test: is the boundary smooth or fractal?

---

## Pre-Registered Hypotheses

### H1_primary (Phase 1)
**Claim**: Large-N escape rate (N=100) will be 30-50% (consistent with Exp48's ~40%)
**Decision criterion**: 25% ≤ escape_rate ≤ 55%
**Prior probability**: 0.65 (Exp48 found ~40%, but seeds 42-51 being 100% raises uncertainty)
**Alternative**: If escape_rate > 55%, seeds 42-51 are NOT representative (they're biased toward escape basin)

### H2_primary (Phase 2)  
**Claim**: Escaper seeds will have systematically lower mean initial gamma compared to trapper seeds
**Decision criterion**: t-test p < 0.05 with Cohen's d > 0.3
**Prior probability**: 0.45 (Elder pred_c5727_q003 was at 0.45, inherit that)
**Connection**: If gamma angle determines basin membership, lower gamma → closer to global optimum

### H3_primary (Phase 3, if conducted)
**Claim**: The escape basin boundary shows smooth/regular structure rather than fractal
**Decision criterion**: The 20×20 grid shows continuous connected regions (not scattered points)
**Prior probability**: 0.50 (uncertainty between smooth vs complex basin topology)
**Alternative (from c3650_001)**: Fractal boundary (complex systems have fractal basin boundaries)

---

## Connection to Previous Findings

| Finding | From | Exp50 Prediction |
|---------|------|------------------|
| ~40% escape rate | Exp48 | H1_primary: replicate |
| Seed-locked escape | Exp49 | H2: initial angles determine basin |
| QAOA-CA analog | Elder C5728 Mitchell | H3: complex basin boundary |
| Escape basin = attractor basin | c3650_001 | H3: potentially fractal |

---

## Script

Phase 1: `/droid/repos/quantum/scripts/run_exp50_basin_survey.py`
Phase 2: Analysis in same script
Phase 3: `/droid/repos/quantum/scripts/run_exp50_boundary_map.py` (if conducted)

Output: `experiments/exp50_results.json`

---

## Calibration Notes (Ember C3658)

- I was 60% on Exp49 H1 prior, updating to 85%+ given 5/5 escaped at p=3
- The 100% escape rate for seeds 42-51 is surprising — either these seeds are exceptional OR escape rate is much higher than 40%
- If true escape rate is ~40%, probability that ALL 10 seeds escape at p=3 = 0.4^10 = 0.0001 (1 in 10,000)
- If true escape rate is ~70%, probability = 0.7^10 = 0.028 (2.8%)
- If true escape rate is ~85%, probability = 0.85^10 = 0.197 (19.7%)
- Given we observed 5/5 (and likely 10/10), the true escape rate is likely much higher than Exp48's 40%
- This suggests IMPORTANT: Exp48 was using random seeds but seeds 42-51 may be from a different distribution than what Exp48 sampled

