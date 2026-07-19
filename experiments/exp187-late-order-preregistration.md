# Exp187 Pre-registration — THE ORDER DECIDED LATER: a delayed-choice quantum switch

**Cycle**: C4877 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 15 circuits
**Class**: foundations (indefinite causal order × delayed choice — wing 1's switch composed
with this run's Exp184 machinery). Creator go: ship-computer general#97.

## The question

The switch campaign certified that two operations can act in a coherent superposition of
orders. Exp184 showed past *entanglement* is decided by a later choice. This flight asks the
composition: **is the causal ORDER of operations that already acted — on a target already
measured and destroyed — decided by a later choice?**

## The universe

Control qubit C in |+⟩ coherently routes the order of two operations on target T (|0⟩):
A = Rx(π/2), B = S. Definite orders give distinguishable targets: order A→B lands |+⟩;
order B→A lands |−i⟩. **The target is tomographed and measured FIRST; the control is
measured LATER**, in a basis chosen per circuit:
- **Z-sort** (late choice = "which order?"): each ensemble must reconstruct a *definite*
  order (F to |+⟩ resp. |−i⟩).
- **X-sort** (late choice = "coherence between orders?"): the ± ensembles are ψ± ∝
  (BA ± AB)|0⟩, with theorem-sharp mixture bounds — **PRE-FLIGHT CORRECTION (selftest-caught,
  no data taken)**: both definite orders are equatorial, so **every mixture of orders has
  ⟨Z⟩ = 0 exactly**, while the X-sorted ensembles leave the equator: **ψ₊ has ⟨Z⟩ = +1/3
  (sim-verified Bloch (2/3, −2/3, 1/3); my hand-derived Y-witness had a sign error and Y does
  not discriminate) and ψ₋ = |1⟩ has ⟨Z⟩ = −1**; ψ₊ additionally breaks the convex hull with
  X−Y = 4/3 > 1. Ensemble weights p₊ = 3/4, p₋ = 1/4.
The same pre-recorded target record contains both descriptions; the later choice selects.

## Arms (15 circuits)

| arm | circuits | purpose |
|-----|----------|---------|
| **delayed** — target measured mid-circuit, control after | {ctrl X, ctrl Z} × {tgt X,Y,Z} = 6 | the claim |
| standard — control measured first | 6 | same sorts without the window on the control (prices the delayed-choice cost per the window law) |
| decohered — control dephased before the ops | ctrl-X × tgt 3 | classical-mixture-of-orders falsifier: X-sort flat |

No-signaling audit free in-data: the *unsorted* target marginals must be identical across all
control choices and arms (spread < 0.02) — nothing about the later choice reaches the target.

## Pre-registered predictions

- **Primary (delayed arm)**: X-sort Z-witnesses off the mixture equator at ≥5σ —
  W₊ = ⟨Z | +⟩ ∈ **+0.18..+0.33** (mixtures exactly 0; ideal +1/3, minus one control-window
  dose per the Exp177/178 law) and W₋ = ⟨Z | −⟩ ∈ **−0.85..−0.50** (mixtures 0; ideal −1);
  AND Z-sort of the same data reconstructs the definite orders at F ≥ 0.85 each.
- **Hull gauge**: X−Y (+ensemble) ∈ 1.10–1.40, above the hull bound 1 at ≥3σ.
- **Standard arm**: same structure, no window on the control: W₊ ∈ +0.22..+0.34,
  W₋ ∈ −0.90..−0.65, Z-sort F ≥ 0.90. **Window cost reported**: W(standard) − W(delayed)
  attributed to the control idling (coherent, per Exp178) through the target's measurement
  window — the run's law applied predictively, ledger complete this time (one spectator,
  one window).
- **Decohered falsifier**: |⟨Z⟩| ≤ 0.10 both sorted ensembles — a classical mixture of orders stays on the equator.
- **Weights gauge**: p₋ ∈ 0.20–0.30 (ideal 0.25).
- Method checklist applied: all criteria are theorem constants (mixture bounds), ratios, or
  same-job differences; no absolute bar absorbs circuit overhead.

## Fences

Circuit-compiled switch = coherently-controlled gate order (wing 1's standing fence: the
process-matrix-native switch is not what a gate-model chip executes; the certified distinction
here is coherent-vs-classical-mixture of orders, which survives compilation — same posture as
the switch campaign). The "late choice" is compiled per circuit (RNG-in-the-loop is a named
follow-up). One die. A and B are fixed unitaries chosen for maximal order-distinguishability.

## Discipline

ps aux: clean. Claim: exp187 (whisper C4877). Ledger prediction pre-submit. Prereg committed
before decode. Selftest gates: ψ± Bloch and weights exact vs analytic (Y₊ = +2/3, Z₋ = −1,
p₋ = 1/4); Z-sort exact; decohered flat; unsorted-marginal invariance.
