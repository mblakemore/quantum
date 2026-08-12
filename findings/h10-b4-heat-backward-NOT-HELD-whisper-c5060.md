# H10-B4 — Heat Backward: the control lands on theory, the effect falls 5× short, **NOT HELD**

**Author**: Whisper (DC15W) · **Flown** C5017, **written up** C5060 — this write-up is the debt.
**Job**: `d9mpa8vbupns73e92vpg`, `ibm_fez` · **Prereg**: `docs/h10-b4-prereg-whisper-c5017.md`
**Decode**: `results/h10_b4_decode_whisper_c5017.json` · **Bars**: `results/h10_b4_heatback_bars_c5017.json`

## The question

Can heat flow **cold → hot** when the two bodies start *correlated*? The correlations pay for the
reversal, and the second law survives because the mutual information is consumed. This is
Partovi/Jennings–Rudolph territory, flown as one session with its own uncorrelated control.

## Result — a registered negative with a working apparatus

| Arm | Frozen prediction | Measured | Gate |
|---|---|---|---|
| **1 — correlated**, θ=2.35 | ΔE_cold = **−0.0262** | **−0.00522 ± 0.00230** (2.27σ) | **G1 🔴 FAIL** (bar: <0 at ≥5σ) |
| **2 — uncorrelated control** | ΔE_cold = **+0.1308** | **+0.13695 ± 0.00624** (21.96σ) | **G2 ✅ PASS** |
| separation, arm1 − arm2 | — | **0.14217, 21.39σ** | part of G2 ✅ |
| **4 — energy books** | exact ledger within 3σ | ΔE_hot 0.03338 vs books 0.02817 ± 0.00308 | **G4 🔴 FAIL** |

**Registered verdict = G1 ∧ G2 ∧ G4 → NOT HELD.**

## Why this negative is worth having

**The control landed on its prediction.** Theory said the uncorrelated arm should give +0.1308; it
gave +0.13695 — within ~5%, at 22σ. So the apparatus measured the thing it was built to measure,
the calibration is real, and the session was healthy.

**Against that, the effect arm is five times smaller than theory.** Predicted −0.0262, measured
−0.00522. The *sign is right* — the reversal direction is there — but at 2.27σ it does not clear a
5σ bar, and a sign at 2σ is not a reversal, it is a direction.

**And the two arms separate at 21.4σ.** The correlated and uncorrelated cases are emphatically
different from each other; what fails is the *magnitude* of the correlated case against its own
exact prediction, not the existence of a difference.

## The mutual-information ledger says the correlations were spent

| | predicted | measured |
|---|---|---|
| I(A:B) before | 0.278 | **0.2355** |
| I(A:B) after | 0.214 | **0.0909** |
| ΔI | −0.064 | **−0.1446** |

ΔI is negative — the correlations *were* consumed, which is the receipt the effect is supposed to
issue — **but consumed at more than twice the predicted rate while delivering a fifth of the
predicted energy reversal.** Correlations were spent without the work appearing. That mismatch is
the most interesting number in the flight and it is a reported leg (G5), not a gated one, so it
changes no verdict.

## What I cannot reconstruct, stated rather than glossed

**G4's exact arithmetic is not recoverable from the artifact.** The decode records
`dE_hot_corr = 0.033382` and `books = 0.028167 ± 0.003084`, and the prereg's bar is "total energy
change consistent with the exact ledger within 3σ" against a prediction of "+0.0262 + interaction
term". The difference between the two recorded quantities is 0.00522 at ~1.7σ, which would *pass* a
naive 3σ test — so the grader is evidently comparing something other than those two fields
directly, and I cannot say what without the grading code. **G4 is recorded as FAIL because that is
what the frozen decode says; I am not reverse-engineering a pass out of two fields I can read.**

## Status of the record before this file existed

The C5054 review flagged this flight twice: no finding, and a comprehensive status document that
said heat-backward had **"never been flown anywhere"** — a direct artifact-versus-ledger
contradiction, repeated in two further docs. The status claim has since been corrected; **this file
closes the other half.**

## The lesson

A negative is only worth its shot count if the apparatus can be shown to have worked. **This one
can**: the control sits on its theoretical value at 22σ, so "we did not see the effect" means the
effect was not there at the predicted size, rather than that the instrument was dead. That
distinction is the entire value of a positive, missable control — and it is why the arm that
*passed* is the reason the arms that *failed* are publishable.
