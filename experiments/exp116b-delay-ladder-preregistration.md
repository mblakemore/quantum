# Exp116b — Inversion Certification via Delay Ladder (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4611. Re-fly of Exp116 (NO-TEST: bias r~2.15 overshot the
fixed correction; premise gate caught a +23σ pseudo-win). **Status: FROZEN at commit.**

## The technique under test (reusable beyond this experiment)

Under uncontrollable calibration bias (published-T1 r observed 1.38–2.15, friction report
02), no fixed delay hits a tight operating window. Fix: **three delay rungs** at assumed
r ∈ {1.5, 1.85, 2.2} (delay_k = r_k · T1_pub · ln(1/0.45)), all flown in one job;
**the graded rung is selected by the CALIB ARMS ONLY** (frozen rule below) — selection on
premise, never on outcome. If this works it becomes the standard pattern for every
delay-calibrated protocol we run.

## Frozen selection rule

Qualifying rung: BOTH p̂_A, p̂_B ∈ (0.35, 0.4677) (passive-certifiable: 0.4677 = 0.5 − 5·SE
at 6000-shot calib). Among qualifying rungs, grade the one whose mean(p̂_A, p̂_B) is closest
to 0.45. Other rungs: reported ungated. Zero qualifying rungs → NO-TEST (and friction row).

## Gates on the selected rung (Exp116 constants)

Passive premise (each bath +5SE < 0.5) · retention ≥ 0.80 · therm band 0.10 ·
**WIN: p₁|₋ − 5·SE > 0.5** · LOSS: p₁|₋ + 5·SE < 0.5 · else AMBIGUOUS.
Reported: ergotropy/run, Δ, demon ledger work column.

## Shots and expectation basis (stated honestly)

Per rung: calib 2×6000, switch 2×14000, nulls 2×4000; + 3 retention + 1 deco sentinels
(2000 each) ≈ 152k shots total, ~35s QPU. Expectation anchored on the TWO HARDWARE residuals
of this observable (p₁|₋ tracked procedure-theory to 0.0015 and 0.002 in Exp108c/116) rather
than the FakeMarrakesh haircut (0.022, pessimistic for this family per the atlas): at
p̂ = 0.45, proc-theory 0.553 → expected measured ≈ 0.551, cert margin ≈ +0.027 at
5SE = 0.0245 (n₋ ≈ 10.4k).

## Prediction

≥1 rung qualifies conf 0.85; WIN on selected rung conf 0.65; NO-TEST 0.15; AMBIG 0.15;
LOSS 0.05. Rung-2 (r=1.85) most likely selected, conf 0.45.
