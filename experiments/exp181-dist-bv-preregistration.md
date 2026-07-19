# Exp181 Pre-registration — THE DISTRIBUTED COMPUTER: Bernstein–Vazirani across a cut

**Cycle**: C4869 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 12 circuits
**Uses**: Exp170 (EJS nonlocal CNOT) + Exp177 (frame algebra) + Exp179 (merged windows) —
composed into the campaign's first **distributed computation**.

## The question

Can two processors that never touch jointly run an algorithm — every cross-register gate
teleported — and get the right answer in one query? Bernstein–Vazirani, n=2: Alice holds the
data register, Bob holds the oracle ancilla; the oracle's CNOTs cross the cut as EJS teleported
gates consuming pre-shared e-bits.

## The design discovery (why this flight is architecturally clean)

For BV, the *entire* EJS correction structure defers out of the circuit:
- The X^x correction lands on Bob's ancilla, which sits in |−⟩ — an X eigenstate — so it is a
  **global phase: dropped entirely** (phase kickback absorbs the correction).
- The Z^z correction on Alice's data commutes through her final H into a **classical bit-flip of
  the readout**: s_i = m_i ⊕ z_i at decode.
Result: the distributed algorithm needs **zero live feedforward and zero mid-circuit
measurement** — every measurement merges into one final layer (Exp179's architecture applied to
computation). No gate ever waits on a cross-cut message; classical communication happens only in
post-processing (sifting), exactly like Exp180's key. Fence: the e-bits are pre-shared resources,
distributed before the computation — that is the standard distributed-computing model, stated
openly. Deferral is legitimate here *because BV's post-oracle operations are all local
Cliffords + measurement* (Exp177's fence, satisfied by construction).

## Arms (one job; 4 hidden strings s ∈ {00, 01, 10, 11} each)

| arm | oracle CNOTs | e-bits | purpose |
|-----|--------------|--------|---------|
| local | direct cx(a_i→anc) | — | monolithic ceiling |
| **dist** | **teleported** (EJS, deferred corrections) | 1 per s_i=1 (both prepped, uniform) | the measurement |
| noresource | same structure, e-bits NOT entangled | none (|00⟩) | falsifier |

Decode (all arms, uniform): s_i = m_i ⊕ (z_i if a teleported gate acted on qubit i else 0),
where m_i = data readout, z_i = that gate's e2 H-measurement. Success = decoded string equals
the programmed string, per shot. Also report the modal (argmax) decoded string.

## Pre-registered predictions

- **Primary**: dist beats noresource on every nontrivial string (01, 10, 11) at ≥3σ each, and on
  the 3-string average at ≥5σ; AND dist's modal decoded string is the programmed string 4/4.
- **Bands** (priced from Exp170's per-gate truth table ~0.87–0.91, *improved* by the
  zero-window architecture; se_P ≈ 0.005):
  local: every string 0.90–0.99.
  dist: s=00 0.92–0.99 · 1-gate strings (01, 10) 0.78–0.92 · s=11 (2 teleported gates) 0.62–0.85
  · 3-string average 0.68–0.88.
  noresource: s=00 0.90–0.99 (uninformative by design — no gates) · 01/10 0.40–0.55 (fake gate
  randomizes that bit: ~0.5 × clean bit) · s=11 0.18–0.32 (pure 2-bit guessing ≈ 0.25).
- **Physics check**: the falsifier floor IS the classical guessing bound — without e-bits the
  "distributed computer" degrades to a coin-flipping impostor on every gate-bearing bit.
- **Scaling note** (reported, not claimed): P(correct|11) / P(correct|01) estimates the per-gate
  cost of the second teleported gate; compare against Exp175's composition-tax expectation.

## Discipline

ps aux: clean. Claim: exp181 (whisper C4869). Ledger prediction logged pre-submit. Prereg
committed before decode. Selftest gates: noiseless local & dist = 1.000 on all four strings;
noresource ≈ 1.0 / 0.5 / 0.5 / 0.25 pattern.
