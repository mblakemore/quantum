# Finding — Exp187: THE ORDER DECIDED LATER — primary held (10σ/32σ off the mixture equator); falsifier band and gauge missed instructively

**Cycle**: C4877 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e4pd9htsac739dqbrg`
(15 circuits, 8000 shots). Delayed-choice quantum switch — wing 1's crown composed with this
run's late-choice machinery. Creator go: general#97. Companion re-flight: Exp187b (below).

## Result — the physics

**PRIMARY HELD.** The target was measured — its record closed — before the control was looked
at. The later choice of control basis then sorts that same record two incompatible ways:

- **Z-sort ("which order?")**: the ensembles reconstruct the two *definite* causal orders at
  F = 0.973 (A→B → |+⟩) and 0.980 (B→A → |−i⟩).
- **X-sort ("coherence between orders?")**: the ensembles leave the equator that **every**
  definite-or-mixed order is pinned to (⟨Z⟩ = 0 exactly, a theorem of the construction):
  W₊ = **+0.129 (+10σ)**, W₋ = **−0.718 (32σ)**; the + ensemble also breaks the convex hull
  (X−Y = 1.319 > 1). Weights p₋ = 0.194 (band 0.20–0.30, grazed).

Whether the two operations *had* an order is not a property the past possessed — it is
structure selected by a later measurement choice. With Exp184 (no fixed moment for
entanglement) and Exp186 (no definite value between looks): **no definite order either.**

**The window law, applied predictively**: the delayed arm pays for the control idling through
the target's measurement window — measured cost dW₊ = 0.144, dW₋ = −0.197 vs the standard
arm (W₊ = +0.273, W₋ = −0.915). My one-dose estimate under-priced it (~2×): W₊'s band
(+0.18..+0.33) **missed low** at +0.129, though the ≥5σ primary criterion held with room.

## The two registered misses (honest, and both instructive)

1. **Decohered falsifier: NOT HELD by 0.0004.** Registered |⟨Z⟩| ≤ 0.10; measured W₊ = −0.091,
   W₋ = −0.100(4). The structure exonerates the physics while convicting my band: both
   ensembles shifted *together* (a common-mode hardware Z-offset), with **sort-dependence
   |W₊ − W₋| = 0.009** — the mixture prediction is precisely "the late sort does nothing," and
   it did nothing (delayed arm: 0.847 split). My absolute band absorbed a hardware offset —
   the Exp185 error class again, checklist applied to the primary but **not** to the falsifier.
   Rule extended: *every* criterion, falsifiers included, must be difference/ratio/theorem form.
2. **No-signaling gauge: 0.030 vs < 0.02.** Suspect: per-circuit compilation placement (each
   control-basis choice is a separately transpiled circuit; different placements shift the
   target's readout marginal). Signaling is excluded by quantum mechanics; the gauge as
   registered nonetheless failed and is recorded as failed. Fix is structural: pin one layout
   for all circuits.

## Disposition — Exp187b (pre-registered before its flight)

Same physics, three changes, all rule-derived: (1) falsifier in **difference form**
(sort-dependence |W₊ − W₋| ≤ 0.10; mixture theory: 0); (2) **pinned layout** across all
circuits (placement variance removed from the no-signaling gauge; gauge < 0.025 = 2σ shot
noise); (3) W₊ band forward-priced from this flight's measured window dose (+0.08..+0.25).
Plus one addition that makes the re-flight a demonstration rather than a repair: a
**delayed_echo arm** — the run's engineered Hahn (X–delay–X) applied to the control through
the target's measurement window, predicting recovery of most of the 0.144 delayed-choice cost.

## Fence

Circuit-compiled switch = coherently-controlled gate order (wing 1's standing fence); the
certified distinction — coherent vs classical-mixture of orders, and its late-choice
selection — survives compilation. Late choice compiled per circuit (RNG-in-the-loop remains
the named follow-up). One die.
