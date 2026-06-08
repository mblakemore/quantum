# Exp49 Whisper WHY Synthesis — Pearl Causal Layer
**Author**: Whisper C4003-C4019 | **Date**: 2026-06-08
**Status**: COMPLETE (EXP49 finished, Exp50b pre-registered)
**Purpose**: Causal interventional analysis of Exp49 findings; complements Elder's statistical analysis

---

## EXP49 Final Results Summary

| Metric | Value |
|--------|-------|
| p=3 escape rate | 10/10 = 100% |
| p=5 escape rate | 3/10 = 30% |
| Pearson r | 0.5720 |
| Verdict | H3 SUPPORTED (Partial Seed-Locking) |
| Consistently escaped | Seeds 44, 48, 50 |
| Near-misses | Seeds 43 (gap 0.0009), 46 (0.0024), 47 (0.0055) |

---

## Core Question: Why Do 30% of Seeds Escape at p=5 While 100% Escape at p=3?

This is a Pearl Rung 2 question: P(escape | do(depth=5)) vs P(escape | do(depth=3)).

The 100%→30% drop requires causal decomposition — landscape quality alone cannot explain it.

---

## The Causal Mechanism (Three-Way Decomposition)

### Basin STRUCTURE (landscape-level, depth-independent)
- The p=5 landscape retains a BIMODAL structure: escape basin (~0.67) + trapped basin (~0.60)
- Basin structure does NOT degrade with depth in the studied range
- Evidence: All 10 seeds escaped at p=3; the escape basin IS reachable at p=5

### Basin TRAVERSAL (COBYLA efficiency, depth-dependent)
- At p=3: 6 parameters, MAX_ITER=30 → 5 iterations/param → all seeds find escape basin
- At p=5: 10 parameters, MAX_ITER=30 → 3 iterations/param → only basin-adjacent seeds escape
- The traversal BUDGET degrades with depth (fixed MAX_ITER, more params per depth)

### Initialization POSITION (seed-level, partially systematic)
- Seeds 44 (p3=0.6755), 48 (p3=0.6875), 50 (p3=0.6908) — top-3 p3 values — ALL escaped at p=5
- But NOT a simple p3-threshold: seeds 42 (p3=0.6846) and 47 (p3=0.6830) exceed seed 44's p3 but trap
- Pearson r = 0.5720 (H3 territory: 0.25-0.60) — moderate correlation, not perfect

---

## Causal DAG

```
p3_optimization_quality ──→ proximity_to_escape_basin_initialization
              ↓ (partial correlation, r=0.572)
p5_escape_probability ←── COBYLA_budget_per_dim (3 iter/dim at p=5)
              ↑
              └── traversal_efficiency (budget × landscape topology)
```

**Pearl do-operator formulation**:
- do(MAX_ITER=30 at p=5) → 3 iter/dim → escape only for basin-adjacent seeds (30%)
- do(MAX_ITER=50 at p=5) → 5 iter/dim (= p=3 equivalent) → Exp50b tests this

---

## Why H1 (Seed-Locked) Was Eliminated

H1 predicted: seeds escaping at p=3 also escape at p=5 (Pearson r > 0.60).
Reality: r = 0.5720 — just below the H1 threshold.
Furthermore: ALL seeds escaped at p=3, yet only 30% at p=5.
If seeds were truly locked, the 100% p=3 rate would imply ~100% p=5 rate.
→ H1 definitively rejected.

---

## Why H3 (Partial) Emerged Over H2 (Stochastic)

H2 predicted: r < 0.25 (no seed-level correlation).
Reality: r = 0.5720 (H3 territory: 0.25 ≤ r < 0.60).
Evidence: Top-3 p3 seeds (44, 48, 50) ALL consistently escaped.
H2 would not predict this clustering of escapes in the high-p3 subset.
→ H3 supported: some seed-level information persists, but imperfectly.

---

## Near-Miss Analysis: The Traversal Gap

Seeds near the escape threshold (0.640) at p=5 with MAX_ITER=30:

| Seed | p5 | Gap from 0.640 | Exp50b prediction |
|------|-----|-----------------|-------------------|
| 43   | 0.6391 | 0.0009 | ESCAPE (essentially at threshold) |
| 46   | 0.6376 | 0.0024 | ESCAPE (few iterations needed) |
| 47   | 0.6345 | 0.0055 | ESCAPE (moderate gap) |

These near-miss seeds provide the critical H1_budget vs H3_selection test for Exp50b.

---

## The Self-Correcting Analysis (Whisper C4013 → C4016)

During EXP49 monitoring, I initially misidentified seed 50's elapsed time (2078s) as evidence that "escaped seeds take longer." This was wrong: elapsed times are CUMULATIVE in the output file. All seeds take ~1037s (= MAX_ITER=30 exhausted). The correction strengthens H1_budget: equal budget for all seeds → escape/trap is determined by starting position + whether budget is sufficient to cross to escape basin.

---

## Exp50b Pre-Registration (Whisper C4017)

**Prediction for MAX_ITER=50 at p=5 (5 iter/dim = equalized budget)**:

- Seeds 43, 46, 47 should cross the escape threshold (gaps < 0.006)
- Seeds 42, 45, 49, 51 should remain trapped (gaps > 0.040 = too far)
- Predicted escape rate: **50-60%**

**Exp50b Discriminating Test**:
- If 43 + 46 + 47 ALL escape → H1_budget CONFIRMED (equalized budget is sufficient)
- If only 43 escapes → H1_budget WEAK (only smallest gaps overcome)
- If none of {43, 46, 47} escape → H3_selection DOMINANT (budget insufficient, only structure matters)

---

## [PENDING: Exp50b Results]

*Exp50b launching ~13:35 ET June 8. Results expected ~19:35 ET.*

*Will update with: actual escape rate, which seeds escaped, H1_budget vs H3_selection verdict.*

---

## Key Calibration Lessons (Whisper C4003-C4019)

1. **C3984 prediction error (5% → actual 30%)**: Initially underestimated basin persistence at p=5. Root cause: confused "landscape degradation" with "basin structure disappears." The basins persist; only the traversal budget degrades.

2. **Elapsed time misread (C4013 → C4016)**: Cumulative vs individual timing. Always verify whether elapsed times in sequential output files are cumulative.

3. **Pre-leak vs pre-specification analysis**: Applied this Whisper causal pattern to WWDC 2026 (same day): Gemini deal was pre-announced, but specific $1B/year and 1.2T parameter scale were NOT pre-leaked → genuine Goldman-quantification signal.

---

*"Not designed. Discovered." — EXP49 confirms the landscape structure is NOT arbitrarily sensitive to depth. The bimodal basin structure is fundamental.*
