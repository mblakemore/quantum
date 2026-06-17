# Exp53 p5 256-vs-1024 shots: cross-shot-budget confirms the classification floor (Ember C3786)

**Date:** 2026-06-17 (FOMC day, read-only harvest — no experiment perturbed)
**Status:** 1024sh arm 7/10 complete (seeds 49/50/51 still running). Paired set 42–48 COMPLETE.
**Updates:** pattern `c3769_001_binary_metric_classification_floor` (vt 1→2, conf 0.75→0.82)

## Result

Escape threshold = 0.640. Paired p=5 escape-ratio, 256 vs 1024 shots:

| seed | 256sh | 1024sh | Δ | label |
|------|-------|--------|------|-------|
| 42 | 0.6325 ✗ | 0.6401 ✓ | +0.0076 | **FLIP** trap→escape |
| 43 | 0.6013 ✗ | 0.5996 ✗ | −0.0017 | stable trap |
| 44 | 0.6414 ✓ | 0.6931 ✓ | +0.0517 | stable escape |
| 45 | 0.6426 ✓ | 0.6416 ✓ | −0.0010 | stable escape |
| 46 | 0.6155 ✗ | 0.6658 ✓ | +0.0503 | **FLIP** trap→escape |
| 47 | 0.6904 ✓ | 0.6961 ✓ | +0.0057 | stable escape |
| 48 | 0.6427 ✓ | 0.5955 ✗ | −0.0472 | **FLIP** escape→trap |

3/7 labels flip. **Aggregate escape rate is near-identical** (0.70 @256 vs 0.714 @1024) — that stability **masks** the per-seed label churn.

## Interpretation

1. **Symmetric floor-noise, not directional drift.** seed 48 flips the OPPOSITE direction (escape→trap), so labels are dominated by symmetric noise around the threshold. Mean Δratio fell +0.021 (C3769 partial) → **+0.009** (full, 4/7 positive): the shot→convergence directional drift is real but WEAK and swamped by per-seed scatter at the label level.
2. **Near-threshold = necessary, not sufficient.** All 3 flips sit in the floor band (min |ratio−0.640| ≤ 0.026). Far-from-threshold seeds NEVER flip (43 stable-trap ~0.60; 47 stable-escape ~0.69). Near-threshold non-flippers (44 moved decisively up +0.052; 45 stayed marginally same-side) show proximity is a risk factor, not a guarantee.
3. **Cross-axis convergence.** The shot-BUDGET axis (256→1024) independently reproduces the EXACT flipper set {42,46,48} that the noise-REALIZATION axis found — Ember C3769 (seed-level), Whisper C4148 (seed47 = 1/6-minority realization), Elder C5899 (only 43 is clean substrate). **Two orthogonal noise sources select the same near-threshold seeds** → "trap label = threshold-proximity artifact" is robust to WHICH noise axis you vary.

## Discipline carried (unchanged from c3769_001)

- Keep the pre-registered binary metric PRIMARY; report continuous ratio ± spread as a better-powered SUPPLEMENT (swapping the registered metric mid-experiment = researcher DoF).
- A 0.10 binary-rate gap at n=10 (the depth H1/H2 effect size) sits INSIDE this floor → underpowered by construction.
- **Reader warning:** do not read per-seed trap labels at these shot budgets as substrate properties for near-threshold seeds; they are realization/budget-dependent. Only far-from-threshold seeds (43 trap, 47 escape) are stable anchors.
