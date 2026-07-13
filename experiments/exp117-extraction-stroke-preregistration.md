# Exp117 — The Extraction Stroke: Work Out of the Engine (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4614. Horizons P4 rung 2; sim tier C4613 (mechanism exact).
**Status**: FROZEN at commit. R5 selftest mandatory (108b anchors + the C4613 pooled
validator re-run).

## Claim structure

On the ladder-selected rung (Exp116b technique, same frozen selection): the measure arm
re-certifies the inverted − branch; the extract arm fires a mid-circuit conditional X
(physical feedforward — no software frame can move energy) and must drain it. The measured
extraction deficit vs the ideal flip = **the demon's cost of acting** (feedforward
thermodynamics, first direct measurement in energy units).

## Arms per rung (r ∈ {1.5, 1.85, 2.2}; P_TARGET 0.45)

calib_a/b (6000 ea) · measure-switch (2×14000; Exp116b circuit) · extract-switch (2×14000;
mid-circuit control readout + if_test X on fluid) · null_fwd/rev (2×4000, therm gate) ·
shared sentinels (3 retention + 1 deco @ 2000). ≈ 236k shots, ~55s QPU.

## Frozen gates on the selected rung (linted C4614)

- Ladder selection by calib arms (frozen 116b rule) · passive premise · retention ≥ 0.80 ·
  therm 0.10 — else NO-TEST.
- **G-recert**: p₁|₋(measure) − 5·SE > 0.5, else NO-TEST for extraction claims (cannot drain
  an uncharged battery; linter fix: the fail scenario is an uninverted fluid ≤0.48, decisive —
  a 0.50 fail-value was VACUOUS-PASS, the known at-threshold class).
- **G-integrity**: |p₁|₊(extract) − p₁|₊(measure)| + 5·SE_diff < 0.05 (the stroke must not
  touch the + branch; an inverted condition-mapping — the Exp112 anomaly class — deviates
  ~0.2, decisive), else NO-TEST.
- **W1 (extraction magnitude)**: p₁|₋(measure) − p₁|₋(extract) − 5·SE_diff > **0.05**
  (expected drop ≈ 0.10; robust to the deficit; margins 0.016/0.036).
- **W2 (post-stroke passivity)**: p₁|₋(extract) + 5·SE < **0.5** (margins 0.007 at 2%
  deficit — genuinely at-risk if the demon's cost exceeds ~2.5%, WHICH IS THE MEASUREMENT;
  W2's LOSS would itself quantify feedforward thermodynamics).
- **Reported ungated**: deficit δ = p₁|₋(extract) − (1 − p₁|₋(measure)) in E units = demon
  action cost; net work = drop × P(−) × E; demon ledger gains the work column live.

## Prediction

Rung qualifies 0.85; G-recert 0.80; W1 WIN **0.85**; W2 WIN **0.55** (the honest coin-flip —
either result is a finding); deficit δ ∈ [0.01, 0.04] conf 0.6.
