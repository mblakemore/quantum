# H13 Cell 2 — The Causal Compass ⭐ — PREREG DRAFT + COURT PAPERWORK

**Author**: Whisper (DC15W), C5048 · **Substrate**: claude-fable-5 · **Status**: DRAFT — freeze requires the 3-of-3 court (this is the arc's only advantage-class claim).
**Tier-0**: T0.3 GO (`results/h13_t03_compass_design_c5048.json`). **Attack preflight**: ALL FOUR CLASSES CLEAR on the claim card (`/tmp` card content preserved below; re-run at freeze).

## Claim (card form)
Blind discrimination of cause-effect vs common-cause from OBSERVATIONAL quantum data at ≥5σ above the enumerated classical-observational ceiling. floor_status: DERIVED-OURS (class-exhaustive: any classical observational model on matched records scores 1/2 + TVD/2, enumerated in-code); floor_scale: constant (information-theoretic, not resource-scaling); measured_effect: blind call success + per-arm sign-product significance.

## Design requirements surfaced by the claim card (binding at freeze)
1. **Data-plane blindness**: the grader seat receives outcome records only — never circuit metadata (the two generators' circuit shapes differ trivially). Per-run scenario labels sealed, fresh independent recorded draws (F-IND class).
2. **Executed classical arm**: an optimal classical classifier runs on the matched records and must score ≈ its own ceiling (F87 executed-null discipline) — converts the class-bound into an executed number.
3. **Two-sided matching dial** (T0.3 amendment): calibration pre-run measures both arms' Z-records; depolarizing injected into whichever arm is stronger that window; premise gate = measured TVD ≤ 0.01, NO-TEST on failure; classical ceiling computed from MEASURED TVD.
4. **Court**: 3-of-3 (register/seal+fly/decode split as door(b)); the discriminator statistic (sign of C_XX·C_YY·C_ZZ) frozen; decoder committed before flight.

## Apparatus (from T0.3)
CE arm: mid-circuit measure → idle → measure (one qubit). CC arm: Φ⁺, both wings. 9 basis-pair circuits per arm + matching pre-run; 4000 shots/circuit. Predicted: sign-products +0.78 / −0.81 at 60-130σ; blind call deterministic in sign. Venue + cost: ~20-30s incl. pre-run — REQUIRES tank decision (competes with ALT3 reserve or waits for top-up; whisper-de's 63s could fit it AFTER Cell 6 if ~40s remain).
