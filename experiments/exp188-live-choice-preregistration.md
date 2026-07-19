# Exp188 Pre-registration — THE LIVE CHOICE: the quartet's late choices made by quantum coins, mid-circuit, after the records close

**Cycle**: C4879 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 6 circuits
**Upgrades**: Exp184 and Exp187b — closing their named fence ("late choice compiled per
circuit"). Creator go: general#111 (fly A and B; this is B).

## The question

In 184 and 187 the "later choice" was fixed at compile time — a determined macro-history could
claim the choice was set before the early record closed. This flight makes each late choice a
**live quantum coin**: a fresh ancilla in |+⟩, measured mid-circuit *after* the early
measurement completes, feeding a dynamic `if_test` that selects the late measurement type
within the same execution. The choice event is quantum-random and circuit-ordered strictly
after the record it retro-sorts. One flight, both anchors:

- **184-live** (handshake across time): coin decides — Bell-measure the middles (swap) or
  product-measure them. Per-shot sort by the coin: heads → the early A-record certifies
  entangled with D (F > 1/2); tails → the same-circuit early records sort separable (~0.25).
- **187-live** (order decided later): coin decides the control basis — X (coherence between
  orders) or Z (which order). Heads → ensembles off the definite-order equator; tails → the
  two definite orders reconstructed. Same execution, same early target records.

Free in-data audits (no compilation confound — every comparison is within one circuit):
coin fairness; and **no-signaling-from-the-future**: the early record's marginal split by the
coin outcome must be flat (the coin hasn't happened yet when the record closes).

## Circuits (6)

184live × verify {ZZ, XX, YY} (3) · 187live × target tomography {X, Y, Z} (3).
Layout 184live: A=q0, B=q1, C=q2, D=q3, coin=q4. 187live: control=q0, target=q1, coin=q2.

## Pre-registered predictions

- **184-live primary**: F(heads: Bell) > 1/2 at ≥5σ, band **0.72–0.86** (Exp184's 0.832 minus
  one added coin-feedforward window on B/D, per the window law; se ≈ 0.017 at ~4000
  shots/sort). F(tails: product) ∈ 0.18–0.32.
- **187-live primary**: heads (X-sort): W₊ > 0 at ≥3σ, band +0.05..+0.28; W₋ < 0 at ≥5σ, band
  −0.80..−0.40. Tails (Z-sort): definite orders at F ≥ 0.80 each. (Bands widened one window
  vs 187b's delayed arm — the coin's feedforward adds a dose; ~4000 shots/sort.)
- **Coin fairness**: P(heads) ∈ 0.46–0.54 every circuit.
- **No-signaling-from-the-future**: early-record marginal split by coin outcome, |Δ| < 0.03
  per basis (within-circuit — no placement confound by construction).
- Criteria per the standing checklist: theorem lines, within-circuit differences; no absolutes.

## Fences

The coin is a projective |+⟩ measurement on the same chip — a QRNG in the device, not a
space-like-separated random source (loophole-free Bell-test standards are not claimed; the
upgrade is from "compiled before the run" to "quantum-random event ordered after the record
closes within the run"). One die; dynamic-circuit feedforward latency is the known window tax,
priced in the bands.

## Discipline

ps aux: clean. Claim: exp188+189 (whisper C4879). Ledger prediction pre-submit. Prereg
committed before decode. Selftest gates: heads/tails sorts exact noiseless (184live: 1.0/0.25;
187live: analytic ψ± and order states), coin fair, future-marginal flat.
