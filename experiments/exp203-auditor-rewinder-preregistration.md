# Exp203 — THE AUDITOR AND THE REWINDER: pre-registration (frozen before submission)

**Whisper C4897, 2026-07-19. Horizons-4 U3 (priority #3), flown on Creator go ("Fly #3 —
U3, is error correction time reversal!"). Committed BEFORE submission.**

## The whiteboard self-correction, stated first (F80 discipline)

Horizons-4's U3 text conjectured: *"does the shield's recovery decline on the
bath-forgetting clock? If yes, 'detection pays' and 'the arrow bends' are one curve."*
**The pre-flight derivation refutes the naive form.** The dephasing event writes TWO
records: one in the owned coin-bath (the demon's copy) and one in the block itself — a
Z1-flavored error anticommutes with the XXXX stabilizer, so the syndrome IS the block's own
record, read at measurement time. The coin's later fate cannot alter the block's parity
statistics. Pre-registered prediction, the *opposite* of the original guess:

- **THE REWINDER** (uncompute, 200b's machine): needs the coin's record intact → recovery
  **declines on the bath's clock** (200b measured 0.813/0.699/0.484). Costs no acceptance.
- **THE AUDITOR** (shield postselection): reads the block's own record → recovery
  **clock-free** with respect to the coin bath. Costs acceptance — priced exactly at the
  record's strength.

What survives as the U3 unification: **one ledger, two strategies**. Gated below.

## Design

Coin = owned bath qubit. Bare arms = Exp200b conventions verbatim. Block arms = [[4,2,2]]
|+̄0̄⟩ (196 prep), coin coupled to q1 — partially dephases logical X̄1 (=X0X1 on the L1 Bell
pair) with the coin recording which-branch. X-basis terminal readout; the **shield is a
decode-time filter** (unpost and post from the same shots). Storage echoes X⊗4 = the XXXX
stabilizer (code-transparent), outside the couple/uncouple window (inverse exactness).
Doses θ/π ∈ {0,¼,½,¾,1} at T=2µs; endpoints at T=4,8µs (194/200b's clock). 4 arms
(bb/bu/lc/lu) × 9 settings = 36 circuits, `ibm_fez`, 8000 shots.

## Exact predictions (selftest PASS, in-repo)

C_bb = cos(θ/2) · anchor; X̄1_unpost(lc) = cos(θ/2) (same event, two substrates);
X̄1_post(lc) = 1 with **acc = (1+cos(θ/2))/2** (rejection rides the record); lu: X̄1 = 1,
**acc = 1** (the refund); coin occupancy sin²(θ/2)/2 in bend arms, 0 in unbend arms.

## Frozen gates

- **G1 ANCHORS**: C_bb(0,2) ∈ [0.65,0.92] (200b band); X̄1_unpost(lc)(0,2) ≥ 0.50 at ≥5σ;
  acc(lc)(0,2) ≥ 0.70.
- **G2 SAME EVENT, TWO SUBSTRATES**: bare ratio tracks cos(θ/2) within 0.10; logical
  unpost ratio tracks the *bare measured* ratio within 0.12, every dose.
- **G3 TWO REVIVALS** (full kill, 2µs, each ≥5σ): auditor post−unpost ≥ 0.5·anchor;
  rewinder lu−lc(unpost) ≥ 0.5·anchor; bare revival ≥ 0.5·C_bb(0) (200b regression).
- **G4 ONE LEDGER** (the unification headline): |acc(θ)/acc(0) − (1+κ(θ))/2| ≤ 0.08 for
  θ/π ∈ {¼,½,¾,1}, with κ the **bare arm's measured** coherence ratio — the shield's
  rejection column priced by the arrow's coherence column, cross-substrate, parametric,
  no fit to θ (201's law-form).
- **G5 THE CLOCKS** (the verdict): Rec_rw(T) non-increasing with Rec_rw(8) ≤ Rec_rw(2)−0.10
  at ≥3σ; Rec_sh(T) flat (|Δ| ≤ 0.15 across 2→8µs); **gap at 8µs ≥ 0.25 at ≥5σ**.
- **G6 THE REFUND**: acc(lu)(π)/acc(lu)(0) ≥ 0.90 AND refund−auditor-cost ≥ 0.25 at ≥5σ
  (uncompute the record → the auditor finds nothing to reject).
- **G7 GAUGES**: coin occupancy tracks sin²(θ/2)/2 within 0.06 (bend arms); records
  returned ≤ 0.15 (unbend arms, everywhere).

**Registered verdict = G1∧…∧G7. The U3 answer = G4∧G5 jointly**: if both hold, error
correction is NOT time reversal — it is the same ledger's other strategy (the rewinder
erases the entry and dies on the bath's clock; the auditor reads the block's own copy,
clock-free, and bills the acceptance column at exactly the record's price). If G5's
flatness FAILS (shield declines on the coin's clock), the original U3 conjecture revives —
either outcome is a finding.

## Budget check (C4887) + filed predictions

Contrasts ~0.5 vs floors ~0 on anchors 0.7–0.9; parents: 200b revival 46σ, 191/196
postselected correlators ~0.98. Ample. **Filed**: acc(lc)(π)/acc(lc)(0) ∈ [0.42,0.58];
mean ledger residual ≤ 0.06; Rec_rw(8) ∈ [0.25,0.60]; Rec_sh(8) ∈ [0.85,1.05]; clock gap
∈ [0.30,0.65].

## Scope

Owned single-qubit bath (resource-theory scope, 200b/F118 lineage) — not the open fabric;
[[4,2,2]] error *detection* with postselection, not fault tolerance; one device, one window
per rung. The θ=π cry-special-angle and cry(0)-folding endpoint compilation facts are
handled as in 201/202: interior-dose skeleton uniformity enforced via deterministic seed
search; endpoints are banded anchors, counts reported.
