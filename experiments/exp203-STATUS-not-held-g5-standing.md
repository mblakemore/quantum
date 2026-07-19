# Exp203 — THE AUDITOR AND THE REWINDER: NOT HELD (registered), with the verdict gate standing

**Whisper C4897, 2026-07-19. Job `d9ee1akjeosc73fim3kg`, `ibm_fez`, 36 circuits, 8000 shots.
Prereg frozen pre-submit (`e53c64f`).** Horizons-4 U3 on Creator go.

## Verdict, without blending

**REGISTERED VERDICT (G1–G7): NOT HELD** — five of seven gate groups missed.
**U3 ANSWER as frozen (G4∧G5): NOT RESOLVED** — by my own registered rule, since G4 missed.
**THE CLOCK DISCRIMINATION (G5) — the pre-registered whiteboard prediction — HELD at 21σ**,
and it stands on its own frozen gate:

| Recovery @ full kill | 2µs | 4µs | 8µs | clock |
|---|---|---|---|---|
| **Rewinder** Rec_rw (uncompute) | 0.528 | 0.150 | **−0.098** | **dies on the bath's clock** (13.2σ decline) |
| **Auditor** Rec_sh (postselect) | 0.789 | 0.796 | **0.883** | **flat — clock-free** |
| Gap at 8µs | | | **+0.981 (21σ)** | |

The whiteboard self-correction was right: the syndrome is the *block's own* record, and the
shield's recovery survives the coin bath's complete forgetting (at 8µs the rewinder returns
*nothing* — Rec −0.098 ≈ 0 — while the auditor still recovers 88% of its anchor). The
auditor and rewinder revivals at 2µs both held (+0.701 at 36σ; +0.263 at 17σ). **Error
correction is not time reversal — that half of U3 is now measured.** What is NOT certified
is the one-ledger law tying their accounts together (below).

## The five misses, each with its cause named

1. **G1 (marginal)**: baseline acceptance 0.678 vs the ≥0.70 floor — priced from 196's
   no-idle gate; the 2µs echoed idle adds physical errors the floor didn't include. 0.022.
2. **G2 (instrument — the anchor-layout artifact)**: κ(0.25) = 1.086 > 1 — the θ=0 bare
   anchor transpiled to **zero** 2q gates (cry(0) folded), freeing the layout to different
   physical qubits than the coupled interior circuits. Every ratio normalized by that
   anchor is poisoned. The 198 sweep rule ("dial changes information flow, not burden")
   was defeated by the transpiler's folding — the fix is structural: decompose cry
   manually (ry–cx–ry–cx) so θ=0 cannot fold. Third appearance of the endpoint-compilation
   class (201 cry(π), 202 SABRE, 203 cry(0)-layout).
3. **G3 (2 of 3 held)**: bare revival +0.343 vs floor 0.380 — today's seed-searched layout
   drew a worse coin than 200b's (its unbend hit 0.73 absolute; ours 0.36). Layout
   roulette on the record qubit; the *logical* rewinder gate still held at 17σ.
4. **G4 (the interesting miss — real physics)**: the naive multiplicative ledger
   acc(θ)/acc(0) = (1+κ)/2 failed at high dose (+0.228 residual). Measured acc(π) = 0.502 —
   dead on the *ideal absolute* 0.5, far above the independent-composition prediction 0.34.
   **Rejection is sub-additive because errors collide**: a record-error (Z1) times a
   noise-error (Z_j) is a weight-2 Z — X-parity EVEN — accepted but logically corrupt.
   This is the **199 blind-spot class appearing as ledger arithmetic**, visible twice in
   the same data: acceptance too high AND post(π) = 0.708 < post(0) = 0.897 (the accepted
   ensemble at high dose contains error pairs). The ledger law needs a collision term —
   a derivation deliverable, not a shot-budget one.
5. **G6/G7 (consequences)**: the refund is partial (0.867 vs ≥0.90; diff +0.126 vs ≥0.25 —
   both sides mispriced by the naive model), and the records-returned gauge failed only at
   the 8µs rung (coin residue 0.207 vs ≤0.15) — **a gauge over-extended into the regime
   where the headline physics guarantees residue**: the record leaking during storage is
   exactly why the rewinder dies there. 200b's original gauge applied only at 2µs; my
   extension to all rungs was a design error. Coin-tracking gauge passed everywhere
   (max resid 0.041 vs 0.06).

**Budget scoreboard (graded straight)**: acc-ratio(π) 0.740 vs [0.42, 0.58] **OUT** (the
collision physics); mean ledger residual 0.108 vs ≤0.06 **OUT**; Rec_rw(8) −0.098 vs
[0.25, 0.60] **OUT** (bath forgot faster on a worse coin); Rec_sh(8) 0.883 ∈ [0.85, 1.05]
**IN**; clock gap +0.981 vs [0.30, 0.65] **OUT** (larger than predicted — the good
direction, driven by the rewinder's total death). 1/5. The day's humility ration arrived
all at once.

## What stands, what's next

**Stands**: the clock discrimination at 21σ (shield clock-free, rewinder clock-bound —
its own frozen gate); the auditor and rewinder revivals at 36σ/17σ; the coin-tracking
gauges; and a genuine discovery in the G4 residuals — **error-pair collisions make the
shield's ledger sub-additive**, connecting 199's blind spot to 201's ledger at the
arithmetic level.

**Not a 203b today.** The failed gates need derivation, not shots: (a) the
collision-corrected ledger law (predict the sub-additivity quantitatively from measured
single-error rates, then gate it); (b) anti-folding compilation (manual cry decomposition
so anchors share the interior's layout); (c) coin-quality selection for the record qubit
(the 200b lesson: place-by-measured). When the corrected law makes a sharp frozen
prediction, it earns a flight. Post-hoc diagnostics above are labeled as such; no gate was
re-graded.

## Line

**The rewinder runs on the universe's memory; the auditor runs on its own. We asked if
they were one machine — the clocks answered no at 21σ, and the books answered "not so
simply": when errors collide, even the auditor's ledger bends.**
