# Exp116 — Certified Population Inversion From Causal Indefiniteness (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4609. Horizons P4; design C4608 (banked +2.2σ hint, F88 data).
**Status**: FROZEN at commit. R5 selftest mandatory (108b double-anchor chain).

## Claim

Two certifiably PASSIVE thermal reservoirs (p̂ < 0.5 at 5σ each) + ICO switch → the − branch
of the working fluid is population-INVERTED (p₁|₋ > 0.5 at 5σ): an active state carrying
extractable work, from causal structure + the demon's information. Binary template vs the
EXACT passive bound 0.5, both directions (baths below, branch above).

## Apparatus (Exp108b/c harness; frozen overrides)

P_TARGET 0.45; delays = **1.65×published-T1** × ln(1/0.45) (bias midpoint of recent runs,
friction report 02; band tolerates r∈[~1.2, 1.75]); SHOTS: switch 2×20000, null 2×6000,
calib 2×12000; chain (5,6,7,8), layout [5,7,6,8], 22-CZ audit, opt=3, transpile seed 4562.

## Frozen gates

- Calib band (0.35, 0.50) AND **passive premise**: p̂_A+5·SE < 0.5 AND p̂_B+5·SE < 0.5, else
  NO-TEST (margins: pass 0.027 at p̂=0.45; an inverted bath 0.51 fails decisively).
- Retention ≥ 0.80; therm band 0.10 (108c constants).
- **WIN (inversion certified)**: p₁|₋ − 5·SE > **0.5** (n₋ ≈ 14k → 5SE ≈ 0.021; preview
  margin +0.010 — THIN, stated: hardware haircut may push below cert).
- LOSS: p₁|₋ + 5·SE < 0.5. Else AMBIGUOUS.
- Reported ungated: ergotropy/run = max(0, 2p₁|₋−1)·P(−)·E; cooling Δ (secondary); demon
  ledger with work column.

## Tiers

Noiseless: 2-tau self-validation anchors (frozen code). Fake true-point: p̂ 0.451/0.451,
p₁|₋ = 0.5311 ± 0.0052 (+6.0σ inversion in-model; proc-theory 0.5533, model haircut 0.022).
Fake bias-corrected run also recorded (validates machinery at p̂=0.29; the bias correction is
live-chip-only — lesson noted).

## Prediction (honest risk profile)

WIN conf **0.55**; AMBIGUOUS 0.25; NO-TEST (calib/passive) 0.15; LOSS 0.05. Either verdict
prices the inversion's hardware ceiling; the banked +2.2σ made this flight worth it.
