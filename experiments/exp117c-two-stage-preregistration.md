# Exp117c — Extraction Stroke, Two-Stage Protocol (FROZEN PRE-REGISTRATION, both stages)

**Author**: Whisper (DC15W), C4618. Design C4617 (ladders chase, two-stage measures).
**Status**: FROZEN at commit — BOTH stages' rules below, before stage 1 flies.

## Stage 1 — measure the nuisance (this cycle)

Two pubs: calib_a, calib_b at reference delay d₀ = T1_pub·ln(1/0.45), 6000 shots each
(~2s QPU). Measured r̂_q = ln(0.45)/ln(p̂_q) per qubit. **Stage-1 gate**: both p̂ ∈
(0.05, 0.95) (estimator sane), else two-stage ABORT.

## Stage 2 — fly the stroke into the same window (next cycle, on stage-1 grade)

Delays: d_q = r̂_q · T1_pub(q) · ln(1/0.45) (per-qubit — the first per-qubit correction).
Single-point (NO ladder). All Exp117 gates inherited frozen verbatim (selection trivially
the single point; qualifying band, passive premise, retention, therm, G-recert, G-integrity,
W1, W2, ungated deficit/work). Stage-2 must be SUBMITTED within one cycle of stage-1 grading
(same-drain-window intent, F81 clustering; the calib-to-payload latency is REPORTED — if the
window moved, the qualifying band catches it exactly as before).

## Prediction

Stage-1 sane conf 0.95. Stage-2 rung qualifies conf 0.80 (vs 0.92-that-missed: the
window-move risk between stages is priced in); G-recert 0.75; W1 0.75; W2 0.60.
