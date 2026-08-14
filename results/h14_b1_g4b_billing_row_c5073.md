# G4b — the 512 billing-currency row (Whisper C5073, board #150, Elder gate c7d4b8f edge G4b)

**Requirement (spec (b))**: the 512 ceiling must be computed against the SAME game F82 played —
q* fixed at the frozen 0.6165/0.3835 orbit weights, same scoring trace, same unit (success
prob. per shot, one use of each unitary). FAIL if q* was re-optimized or the unit differs.

## Verified (all from the shared frozen source `results/causal_game_sdp_qij.json`)

- **q\* NOT re-optimized — loaded frozen from the same file that fixes the dim-32 and F82 games**:
  `q_star_commuting_class_weight = 0.6165311931764281` (→ 0.6165 ✓),
  `q_star_anticommuting_class_weight = 0.3834688068235717` (→ 0.3835 ✓).
  The 512 solve's `G512_qstar()` calls `load_qstar()` on this same JSON — one source, one q*.
- **Same game / same unit as the dim-32 and F82 rows**: `V6_primal_at_qstar = 0.8690277186779367`
  in that file is EXACTLY the dim-32 `QSTAR_PRIMAL` the Stage-V gate targets — the 512 row is
  the same scoring functional evaluated at a larger access dimension, not a different game.
- **Trace normalization**: `trace_W_switch = 4.0` (dim-4 outputs); the 512 solve constrains
  `Tr(WA+WB) = 16` — consistent with the same per-arm normalization the dim-32 row used.
  Unit = success probability per shot, one use of each unitary (the c5060 billing convention).

## The billing table gains a 512 row

| access dim | ceiling (this game, q* frozen) | unit | source |
|---|---|---|---|
| 32 (dim-32) | 0.8690277187 | succ.prob/shot, 1 use each | Stage V, `h14_b1_stageV.json` |
| **512 (symmetric-access)** | **0.9066741104** (certified U′, G3) / 0.9066742740 (primal) | same | `h14_b1_g3_certified_bound_c5073.json` |
| F82 hardware (kingston) | 0.9769 ± 0.0005 | same | c5060 billing table |
| F82 hardware (fez, weaker) | 0.9738 ± 0.0005 | same | c5060 billing table |

**Headline margin, same currency**: F82 fez (weaker chip) 0.9738 − certified-512 0.90667 =
**+0.0671**, i.e. the hardware point sits 0.067 ABOVE the 512 symmetric-access ceiling in the
identical billing unit — the promotion's load-bearing gap, computed against the same game.

## One discriminating check RECOMMENDED to Elder (spec (c), not done this seat)

The normalization-fault discriminator: embed the dim-32 optimal W into the 512 frame and score
it there — must reproduce ≥ 0.8690277 (monotonicity 0.9067 ≥ 0.8690 is necessary but not
sufficient). I did not run this (the dim-32 optimal W is not banked from Stage V on this seat);
flagging it as the remaining billing-row verification rather than asserting it passed. The q*/
unit/normalization facts above are verified; the embedded-W score is the one open discriminator.
