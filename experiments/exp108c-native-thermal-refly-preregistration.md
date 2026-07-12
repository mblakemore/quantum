# Exp108c — Native-Fluid Thermal Splitting RE-FLY, Drift-Tolerant (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4592. **Status: FROZEN at commit.**
**Relation to Exp108b** (`exp108b-native-thermal-preregistration.md`, NO-TEST C4591): identical
circuits, procedure targets, estimators, and WIN/LOSS structure. ONLY the gate constants and
null shot counts change, each justified by the measured C4591 drift data. This is a re-fly
after infrastructure NO-TEST, not a second bite at a graded result.

## What C4591 measured (the drift data sizing these gates)

T1 ran 38–59% longer at execution than submit-time calibration over ~19h queue
(r = T1_exec/T1_cal ∈ [1.38, 1.59]); p = exp(−1.386/r) maps tolerated r ∈ [0.7, 1.8] to
p ∈ (0.138, 0.463). The old therm band (0.06) implicitly required r ≈ 1 (null-vs-calib decay
exposure is circuit-time-asymmetric under drift; measured mismatch 6.1pp at r≈1.5).

## Changes vs 108b (all frozen here)

1. **Calib band**: (0.12, 0.40) → **(0.12, 0.47)** — tolerates r ∈ [0.7, 1.8].
2. **Null shots**: 2500 → **6000** per pub (shrinks the therm-gate SE).
3. **Therm band**: 0.06 → **0.10** — linted (`gate_feasibility_lint`): pass at fresh-cal
   residual (margin 0.016 at 6k shots) AND at moderate-drift residual 0.04; still CAN-FAIL on
   real breakage (0.17-class deviation fails at k_fail=2). First draft 0.08 was VACUOUS-FAIL
   under the moderate-drift scenario — linter catch #3, fixed pre-freeze.
4. Delays recomputed from **fresh calibration at submit** (unchanged procedure).
5. Everything else identical: WIN iff Δ − 5·SE > 0.06 AND p₁|₊ + 5·SE < min(p̂_A, p̂_B);
   retention ≥ 0.80; procedure theory from measured p̂; double-anchor self-validation.

## Accepted residual risk (stated before data)

If queue drift recurs at r ≳ 1.6, the therm gate may still NO-TEST — the gate must keep the
ability to fail, and full drift-immunity is not achievable with statically-baked delays. The
structural fix (execution-time-calibrated delays) does not exist for static jobs; short queue
is luck. A second consecutive drift NO-TEST would itself be a finding (queue-drift base rate).

## Prediction

Given fresh calibration and the C4591 ungated physics (Δ = 0.1775 ± 0.0129 at 13.8σ even
with broken prep): WIN conf 0.65; NO-TEST-again (drift recurrence) conf 0.25; LOSS conf 0.10.
