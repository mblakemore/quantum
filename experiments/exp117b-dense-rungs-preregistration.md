# Exp117b — Extraction Stroke, Dense Rungs (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4616. Re-fly of Exp117 (NO-TEST: bias swung to ~1.6, coarse
rungs straddled the sweet spot). **Status: FROZEN at commit.**

## Changes vs Exp117 (ONLY these)

Rungs: {1.5, 1.85, 2.2} → **{1.55, 1.7, 1.85, 2.0}** — four dense rungs bracketing the
8-value bias sample's median (~1.7). EVERYTHING else identical and inherited frozen:
selection rule (calib arms, closest-to-0.45 among qualifying), passive premise, retention,
therm, G-recert (uninverted-fluid fail scenario), G-integrity, W1 extraction magnitude
(>0.05 at 5σ), W2 post-stroke passivity, ungated deficit + work reports, shots per rung
(calib 2×6000, measure 2×14000, extract 2×14000, nulls 2×4000). Grader: `grade_exp117.py`
unchanged except the rung list (read from manifest).

## Rationale filed pre-data

Bias sample {1.38, ~1.6, 1.59, 1.68, 1.69, 1.82, 1.85, 2.15} swings both directions;
4 rungs at 0.15 spacing mean the nearest rung is within ±0.075 of any bias in [1.48, 2.08]
→ bath miss ≤ ~0.02 in population → qualifying probability HIGH and the selected rung lands
warm enough for a ≥5σ charge (theory: p̂ ≥ 0.43 gives inversion ≥ +0.045 ≈ 6-9σ at budget).

## Prediction

≥1 rung qualifies conf 0.92; G-recert passes conf 0.75; W1 WIN conf 0.75; W2 WIN conf 0.60
(demon cost now known small — 0.0017 E — so passivity mostly rides the charge level);
deficit δ ∈ [0.000, 0.012] conf 0.7 (updated on the C4615 measurement).
