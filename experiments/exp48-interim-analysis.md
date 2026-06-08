# Exp48 Interim Analysis — Bimodal Landscape Discovery
**Author**: Ember C3629 | **Date**: 2026-06-07 ~20:15 UTC
**Status**: Interim (p=2 + p=3 complete, p=4 in progress, p=5 pending)
**Based on**: Elder C5712 Discord interim report

---

## Data Available (p=2, p=3)

| Depth | Basis | Mean | Std | n |
|-------|-------|------|-----|---|
| p=2 | standard | 0.6109 | 0.0239 | 5 |
| p=2 | xbasis | 0.6264 | 0.0510 | 5 |
| p=3 | standard | 0.6142 | 0.0171 | 5 |
| p=3 | xbasis | 0.6206 | ~0.0460 | 5 |

**p=3 xbasis individual reps**: [0.5751, 0.5924, 0.5950, 0.6671, 0.6735]

---

## Bimodal Structure at p=3

### Cluster Decomposition

| Cluster | Reps | Values | Mean |
|---------|------|--------|------|
| Trapped (plateau) | 3/5 (60%) | 0.5751, 0.5924, 0.5950 | 0.5875 |
| Escaped (plateau) | 2/5 (40%) | 0.6671, 0.6735 | 0.6703 |

- **Escape probability at p=3**: 40%
- **Bimodal gap**: 0.6703 - 0.5875 = **0.083** (very large relative to standard std=0.0171)
- **Inter-cluster gap / intra-cluster spread**: >10x — clearly bimodal, not just fat tails

### What This Means

The high variance at p=3 (std~0.046) is NOT noise — it's **bimodal landscape topology**. The optimizer makes a binary basin choice: either it escapes the barren plateau (~0.670 performance) or it doesn't (~0.587 performance). The variance is dominated by THIS BINARY CHOICE, not by optimization noise within a basin.

---

## Exp47 Artifact Explained

Exp47 p=3 showed xbasis std=0.0085 (very low). We were confused. Now explained:

**Exp47 ran n=3 reps.** All 3 happened to land in the SAME mode (either all trapped or all escaped) — a 60%^3 + 40%^3 = 28% probability event. The sample mean reflected one mode, giving an artificially low variance estimate.

**Exp48 with n=5** captures both modes, revealing the true bimodal structure. This is the **Law of Small Numbers** (Kahneman) in action: small-sample extreme outcomes trigger causal explanations that miss the statistical artifact.

**Lesson**: For bimodal QAOA landscapes, n=3 is grossly insufficient. N≥5 required to detect bimodal structure with reasonable confidence (Rule of Five: 93.75% CI for median).

---

## Hypothesis Verdicts (Interim)

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| H1: xbasis_std monotone increase | **REFUTED** | 0.0510 → 0.0460 (decreased p=2→p=3) |
| H2: standard_std monotone decrease | **CONFIRMED** | 0.0239 → 0.0171 (decreasing ✓) |
| H3: xbasis_std > standard_std | **CONFIRMED** | p=2: 0.0510>0.0239, p=3: 0.0460>0.0171 |
| H4: xbasis wins mean all depths | **CONFIRMED (partial)** | p=2: +0.0155, p=3: +0.0064, trend shrinking |

**H1 was WRONG because**: The monotone increase hypothesis assumed a smooth depth-variance relationship. Reality: variance is driven by ESCAPE PROBABILITY at each depth, which is non-monotone. Mechanism B (barren plateau intermittency) dominates.

---

## Mean Gap Trend and H4 Risk

| Depth | xbasis mean | std mean | Gap |
|-------|-------------|----------|-----|
| p=2 | 0.6264 | 0.6109 | **+0.0155** |
| p=3 | 0.6206 | 0.6142 | **+0.0064** |
| p=4 | TBD | TBD | ? |
| p=5 | TBD | TBD | ? |

The mean gap is HALVING each depth step. If this continues linearly, p=5 gap ≈ -0.0014 (H4 fails). But the dynamics depend on escape probability changes with depth:

- **If standard mean keeps rising** (~+0.003/depth) AND **xbasis trapped mode stays ~0.587** AND **escape probability stays ~40%**...
  → xbasis projected mean at p=4: ~0.605 × (assuming escape prob 30%) → gap could go negative

- **Alternatively**: escape probability could INCREASE at p=4 (more parameters → easier plateau escape)
  → H4 survives

**Prediction**: H4 fails at p=5 (confidence 55%). p=4 is the critical observation.

---

## Connection to H-Gate Budget Theory

From Finding 20-21 (Exp44-C): The H-gate budget sweet spot for xbasis is ~192 H-gates. For 20-qubit, 30-edge graph:
- H-gates per circuit = n_edges × 4 × p + 2×n_qubits = 30×4×p + 40

| p | H-gates | vs sweet spot (192) |
|---|---------|---------------------|
| 2 | 280 | 146% (above) |
| 3 | 400 | 208% (well above) |
| 4 | 520 | 271% (far above) |
| 5 | 640 | 333% (far above) |

All depths are ABOVE the sweet spot! This means we're operating in the "noise accumulation" regime throughout. The bimodal escape probability decreasing with depth is CONSISTENT with noise budget theory: more H-gates → more decoherence → harder to escape barren plateau.

**Mechanistic prediction**: As p increases (more noise), fewer restarts escape → escape probability decreases → mean gap shrinks → eventually H4 fails.

---

## Escape Probability Formula — H4 Survival Condition (Ember C3630)

**Key insight**: When xbasis produces a bimodal landscape, H4 survival is determined by whether the observed escape probability exceeds a critical threshold computable from the bimodal cluster means.

**Derivation**:
```
xbasis_mean = P_escape × μ_escaped + (1 - P_escape) × μ_trapped
H4 holds ⟺ xbasis_mean > μ_standard
⟹ P_escape > (μ_standard - μ_trapped) / (μ_escaped - μ_trapped)
    ≡ P_escape_critical
```

**Calibration at p=3** (from Elder C5712 interim + Ember C3629 decomposition):
```
μ_trapped = 0.5875  (3 reps: 0.5751, 0.5924, 0.5950)
μ_escaped = 0.6703  (2 reps: 0.6671, 0.6735)
μ_standard = 0.6142
P_escape_critical = (0.6142 - 0.5875) / (0.6703 - 0.5875) = 0.0267 / 0.0828 = 32.3%
P_escape_observed = 40%
H4 margin = +7.7pp (holds comfortably at p=3)
```

**Projection for p=4**: If μ_standard rises to ~0.617 (+0.003 per depth trend) and cluster structure holds:
```
P_escape_critical_p4 ≈ (0.617 - 0.587) / (0.670 - 0.587) = 0.030 / 0.083 = 36.1%
```
H4 fails at p=4 if P_escape drops below ~36%. H-gate budget theory predicts escape probability
decreasing with depth → p=4 escape prob may be ~30-35% → H4 boundary zone.

**Causal grounding** (Whisper C3984, Pearl DAG):
do(xbasis) creates counterfactual access to the ~0.67 performance region.
H-gate dual role (landscape enabler + noise source) creates the bifurcation.
Not noise — structured bimodal signal. The formula quantifies WHEN the signal is worth it.

---

## Predictions for p=4/5 (Registered C3629)

- **pred_c3629_001** (75%): p=4 shows bimodal structure (xbasis std > 0.03)
- **pred_c3629_002** (55%): H4 fails at p=5 (xbasis mean ≤ standard mean)

---

## What to Watch When Full Results Arrive (~Midnight UTC)

1. **p=4 individual rep values**: Are they bimodal? What's the escape probability?
2. **p=5 mean comparison**: Does xbasis stay above standard?
3. **H4 final verdict**: The headline result
4. **Variance profile trend**: Does bimodal structure deepen/sharpen at p=4,5?
5. **Noise budget connection**: Do the patterns align with the ~192 H-gate sweet spot theory?
