# Exp183 Pre-registration — THE TWO-OFFICER PROTOCOL: quantum secret sharing (HBB99)

**Cycle**: C4873 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 11 circuits
**New capability class**: secret sharing. **Blocks**: GHZ (Exp168, Mermin 3.467), sifting
discipline (Exp180). Creator go: ship-computer general#57.

## The protocol

Alice, Bob, Charlie share a GHZ state (|000⟩+|111⟩)/√2; each measures X or Y. In the four
*valid* basis combos (XXX, XYY, YXY, YYX — the Mermin family) the GHZ correlations enforce
a = b ⊕ c ⊕ σ (σ = 0 for XXX, 1 for the two-Y combos): **Alice's bit is reconstructable from
Bob AND Charlie together, and provably invisible to either alone** (GHZ two-party marginals are
maximally mixed — a theorem, not a design goal). One-Y and three-Y combos carry no correlation
(⟨XXY⟩ = ⟨YYY⟩ = 0) — the sifting rule is itself physics, and we measure it. The same four
valid-combo expectations assemble the **Mermin certificate** M = ⟨XXX⟩−⟨XYY⟩−⟨YXY⟩−⟨YYX⟩
(classical/LHV bound |M| ≤ 2) at zero extra circuit cost.

## Arms (one job)

| arm | circuits | purpose |
|-----|----------|---------|
| **ghz** | 6 (XXX, XYY, YXY, YYX + invalid XXY, YYY) | the protocol + certificate + sifting physics |
| noghz (product state) | 4 valid combos | null falsifier: everything flat |
| bellAB (Bell(A,B), C=\|0⟩) | 1 (XXX) | **the security anti-pattern**: wrong resource ⇒ ONE officer reads Alice alone (⟨AB⟩ ≈ +0.97) while group reconstruction fails (0.5) — what a compromised protocol looks like, in data |

## Pre-registered predictions

- **Primary** (all three must hold):
  1. Reconstruction P(a = b⊕c⊕σ) ≥ 0.85 on ALL four valid combos (band 0.90–0.97; Exp168's
     E ≈ 0.87 ⇒ ~0.93).
  2. Single-officer blindness: |⟨AB⟩| and |⟨AC⟩| < 0.05 in all valid combos (se ≈ 0.011).
  3. Mermin certificate M > 2 at ≥5σ (band 3.1–3.6; Exp168: 3.467).
- **Sifting physics**: |⟨XXY⟩|, |⟨YYY⟩| < 0.05 — discarded rounds are uncorrelated by nature.
- **Falsifiers**: noghz — all valid-combo E ∈ (−0.05, 0.05), reconstruction 0.47–0.53, M ∈
  (−0.2, 0.2). bellAB — ⟨AB⟩_XXX > 0.9 (single-officer leakage exposed) AND reconstruction
  0.47–0.53 (no group secret): the anti-pattern is the *complement* of the protocol.
- **The two-officer property is the conjunction**: group CAN (≥0.85) + individuals CANNOT
  (<0.05) + resource certified non-classical (M > 2). No single metric suffices; pre-registered
  as a three-legged claim.

## Discipline

ps aux: clean. Claim: exp183 (whisper C4873). Ledger prediction pre-submit. Prereg committed
before decode. Selftest gates: valid-combo reconstruction = 1.000, singles = 0.500, M = 4.000,
invalid combos E = 0, bellAB ⟨AB⟩ = 1 with reconstruction 0.5, noghz all null.
