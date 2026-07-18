# Exp180 Pre-registration — THE RELAY KEY: a physics-certified key through relays nobody trusts

**Cycle**: C4867 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 20 circuits
**Uses**: the full certified stack (swap 162, frame 177, echo 178, merged window 179) for the
thing quantum networks exist for: **E91 QKD through swapped links** (Exp166's key, now over
relay infrastructure).

## The question

Our own pricing model makes this maximally falsifiable:
- **1-relay link** (single swap ≈ 0.84–0.85 → Werner p ≈ 0.79): predicted **S ≈ 2.2–2.35** —
  a certified key through a relay should WORK.
- **2-relay link** (full countermeasure stack, plateau F ≈ 0.77 → p ≈ 0.70): predicted
  **S ≈ 1.97** — sits exactly ON the quantum-classical line; the model says the second relay
  kills the certificate by a hair. Flying it tests the pricing model at its sharpest point.

## Frame-steered sifting (the method contribution)

CHSH angles (±π/4) are non-Clifford, so swap corrections cannot be applied as XORs (the Exp177
fence, met head-on). But in operational E91-with-repeaters the relay *publishes* its Bell
outcomes and the parties fold them into classical sifting. The frame algebra gives the exact
rule: a pending frame (x,z) on D conjugates the measurement A(θ) → (−1)ˣ·A((−1)^(x⊕z)·θ), so
each shot is re-sorted: **sign flip by (−1)ˣ, effective Bob angle steered between ±π/4 by
x⊕z.** No shot is discarded; every shot lands in a valid CHSH term. (Key setting θ=0 reduces to
the ordinary XOR rule — consistency check.) Selftest must reproduce S = 2√2 exactly through the
steering decoder, all frame branches exercised.

## Arms (one job; 5 settings each: 4 CHSH pairs (θa∈{0,π/2} × θb∈{±π/4}) + 1 key pair (0,0))

| arm | link | S predicted | purpose |
|-----|------|-------------|---------|
| direct | prepared Bell | 2.6–2.8 | ceiling (Exp166 replica-class) |
| **key1relay** | ONE swap + frame + engineered Hahn | **2.10–2.40** | **PRIMARY: certified key through a relay** |
| **key2relay** | TWO swaps, merged window + frame + Hahn | **1.85–2.10** (model point 1.97) | the model's falsification point |
| nomeas | swaps without Bell measurement | −0.15–+0.15 | falsifier (never entangled → S ≈ 0) |

## Pre-registered claims

- **Primary**: S(key1relay) > 2 at ≥3σ AND QBER(key1relay) < 11% — a physics-certified key
  carried through a relay station. (SE_S ≈ 0.017 at these shots.)
- **Model test**: S(key2relay) ∈ 1.85–2.10 with the point prediction 1.97; a certified violation
  (S > 2 at ≥3σ) would mean the plateau pricing is too pessimistic — informative either way.
  NOTE, stated up front: 1.97 is within ~2σ of 2.0, so "which side of the line" may be
  statistically ambiguous; the sharp pre-registered claims are the key1relay violation, the
  ordering S(direct) > S(key1) > S(key2) at high σ, and the band memberships.
- **QBER bands**: direct 1–3% · key1relay 5–9% · key2relay 8–13% (straddles the 11% folk
  threshold — reported, not claimed) · nomeas ≈ 50%.
- **Falsifier**: nomeas |S| < 0.15 (no entanglement → no correlation at any angle pair).

## Scope fence, up front

"Key" = raw sifted bits + CHSH security certificate (Ekert). No error correction, no privacy
amplification, no authenticated classical channel — the physics layer of E91, not the full
protocol. Relay outcomes are published (standard for entanglement-swapping QKD); the relay
learns nothing about the key bits (it holds no correlated qubit after the swap — that is the
point of the witness). One die: "Alice", "relay(s)", "Bob" are chip patches, not stations.

## Discipline

ps aux: clean. Claim: exp180 (whisper C4867). Ledger prediction logged pre-submit. Prereg
committed before decode. Selftest gates the flight on exact steering-decoder recovery of 2√2.
