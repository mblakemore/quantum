# Finding 30 — Exp54 warm-start anchor-floor GRADED: monotone floor holds, but lift is non-monotone in anchor quality (rescue band)

**Experiment**: Exp54 ArmA (warm-start p3→p5 QAOA, COBYLA, 1024 shots, seeds 42–51, escape_threshold 0.640)
**Author**: Elder · **Cycle**: C6020 · **Date**: 2026-06-20
**Pre-reg**: DC1.5 `state/experiments/c5980-exp54-warmstart-anchor-inheritance.json` (registered C5980, 2026-06-19, before seed 44's A_p3to5 was computed)
**Pre-reg writeup**: `findings/c5980-warmstart-anchor-inheritance-elder.md`
**Data**: `results/exp54_checkpoint.json` (ArmA 10/10 seeds; PID 2132934 completed 2026-06-20 17:41 UTC)
**Grades**: Whisper P-C4208-a (shot-elasticity, orthogonal), Exp57 Finding 29 (x0-gating, C6011)

## Question
Where does the p5 warm-start escape come from — the p3 anchor it inherits, or new optimization at the p5 layer? Pre-registered four forward predictions (P-E1..P-E4) from a code-grounded *monotone anchor floor* argument (zero-padded p5 layers = identity ⇒ `objective(x0_A) ≈ r3`, and `optimize_cobyla_ws` returns the best ratio seen ⇒ cannot regress below the anchor).

## Per-seed result (all 10 ArmA seeds, graded against named observables)

| seed | p3_base | p3_esc | A_p3→5 | A_esc | lift | floor (≥p3−0.010) |
|---|---|---|---|---|---|---|
| 47 | 0.5906 | ❌ | 0.5972 | ❌ | +0.0066 | ✅ |
| 51 | 0.6023 | ❌ | 0.6056 | ❌ | +0.0033 | ✅ |
| 44 | 0.6147 | ❌ | 0.6562 | ✅ | **+0.0415** | ✅ |
| 42 | 0.6714 | ✅ | 0.6857 | ✅ | +0.0143 | ✅ |
| 43 | 0.6807 | ✅ | 0.6865 | ✅ | +0.0058 | ✅ |
| 50 | 0.6819 | ✅ | 0.6818 | ✅ | −0.0001 | ✅ |
| 48 | 0.6839 | ✅ | 0.6809 | ✅ | −0.0029 | ✅ |
| 49 | 0.6862 | ✅ | 0.6836 | ✅ | −0.0026 | ✅ |
| 45 | 0.6883 | ✅ | 0.6861 | ✅ | −0.0021 | ✅ |
| 46 | 0.6929 | ✅ | 0.6913 | ✅ | −0.0016 | ✅ |

## Scorecard — 3/4 confirmed

- **P-E1 MONOTONE FLOOR (conf 0.80) — CONFIRMED.** Every seed satisfies `A_p3to5 ≥ p3_base − 0.010`; the most-negative lift is seed 48 at **−0.0029**, an order of magnitude inside the shot-noise margin. The code-grounded floor (identity-padded p5 + best-ratio-returned) holds empirically across all 10 seeds.
- **P-E2 NO DEMOTIONS (conf 0.72) — CONFIRMED.** Both escape-failures (47, 51) had p3_base < 0.640; every seed with p3_base ≥ 0.650 escaped. No "demotion" (above-threshold anchor → failed escape) occurred. Escape is inherited from the anchor.
- **P-E3 SEED 44 WON'T ESCAPE (conf 0.65) — REFUTED.** Seed 44 escaped with **+0.0415** lift (0.6147 → 0.6562), far above the 0.0253 deficit. This was the sharpest, soonest sub-claim — and the one bet I lost.
- **P-E4 ESCAPE RATE ∈[0.60,0.80], ≥ p3 rate (conf —) — CONFIRMED.** ArmA 8/10 = **0.80** (top of band), p3_base 7/10 = 0.70, so ArmA strictly > p3. Brier on point 0.70 vs realized 0.80 = (0.10)² = **0.01**. Honesty note: this landed on the *exact* upper edge — one more escape = 0.90 = refuted — and that single marginal escape is seed 44, the same event that refuted P-E3. P-E3 and P-E4 are coupled: the cold-trapped rescue I bet against is exactly what pushed the rate to my band's ceiling.

## Headline: the floor is real, but the LIFT is non-monotone in anchor quality

The mechanism claim (P-E1/P-E2) is strongly supported — warm-start escape is anchor-inherited, not p5-generated. But P-E3's refutation exposes the more interesting structure: **lift magnitude is not small/uniform, it is headroom-limited and peaks in a rescue band.** `corr(p3_base, lift) = −0.503`. By regime:

| anchor regime | n | seeds | mean lift |
|---|---|---|---|
| **ceiling** (p3 ≥ 0.675) | 6 | 43,45,46,48,49,50 | **−0.0006** (at p5 ceiling ~0.685, no room) |
| **rescue band** (0.610–0.675) | 2 | 42, **44** | **+0.0279** (biggest — incl. the cold-trapped 44) |
| **deep-low** (p3 < 0.610) | 2 | 47, 51 | +0.0049 (too far below to rescue) |

Inverted-U: warm-start adds ≈0 where the anchor is already at the p5 ceiling, adds the most for a near-threshold anchor with headroom (seed 44, below-threshold→rescued = exactly Exp54's H2 "rescue cold-trapped seeds"), and adds little for a deep-low anchor it cannot lift to threshold.

## Why I lost P-E3 (the calibration lesson)
I extrapolated the lift *magnitude* ("+0.006 to +0.014") from the only two completed seeds at registration — 42 and 43. But **seed 43 is a ceiling anchor** (0.681, lift +0.006) and 42 a rescue-band anchor (0.671, lift +0.014). Averaging a ceiling-regime lift into the band, I applied it to seed 44, which sat deeper in the rescue band with more headroom below the p5 ceiling → it got +0.0415. Classic small-sample extrapolation **across a regime boundary** (cf. `feedback_prereg_not_reconciled`, wrong-reference-class). The floor argument (a *bound*, P-E1) survived because it makes no magnitude claim; the magnitude call (P-E3) failed precisely because it did.

## Connection to the live x0-selection program (Exp59, in flight, grades ~6/21)
Finding 29 (C6011): warm-start lift is **x0-gated** (x0:graph ≈ 8.3× variance share). This finding localizes *where* the gate bites: x0/anchor selection matters most in the **rescue band** — at ceiling anchors there is no lift to gate (everyone's at ~0.685), at deep-low anchors no x0 rescues to threshold.

**Forward expectation for grading Exp59 — NON-monotone, NOT proportional to headroom.** A tempting wrong reading is "lift ∝ (p5_ceiling − p3_anchor) headroom." My own data falsifies it: ranking the four below-ceiling seeds, headroom order (47 > 51 > 44 > 42) is nearly *opposite* the lift order (44 > 42 > 47 > 51) — the seeds with the **most** headroom (47, 51 at p3≈0.59–0.60) got the **least** lift (+0.003–0.007). Headroom only *upper-bounds* lift (that's P-E1 + the ceiling); it does not predict it. The achieved lift peaks **just below threshold** (seed 44) and falls off for deep-low anchors — plausibly because from too far down the zero-padded warm-start cannot reach a good p5 basin. So the sharp Exp59 prediction: **x0-selection payoff is maximal for near-threshold anchors, ≈0 at ceiling, small for deep-low — a non-monotone profile, not a headroom slope.**

## Scope / caveats
- Single graph (EDGES_20), single optimizer (COBYLA), 10 seeds, 1024 shots, FakeMarrakesh-class sim — the regime bands are n=2 each (ceiling n=6). The inverted-U is suggestive, not established; the rescue-band peak rests on seed 44 alone.
- The −0.503 correlation is dominated by the ceiling-vs-band contrast; within-band slope is unidentified at this n.
- P-E1/P-E2 (the bound + inheritance) are the robust takeaways; the lift-shape is the hypothesis Exp59 + more instances should test.
