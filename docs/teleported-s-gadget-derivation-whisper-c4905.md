# The Teleported-S̄ Gadget — derived and verified (P2 enabler groundwork)

**Whisper C4905, 2026-07-20. 0 QPU. Substrate `claude-opus-4-8`. Creator directive "P2 go!".**
The C4901 transversality audit proved single-logical-S̄ is unreachable in the [[4,2,2]]
in-block transversal set (generated group 12/720). So the *b≠0* HLF family (the S-vertices)
needs a teleported-S̄ gadget. This document derives and **statevector-verifies** that gadget —
the enabler for Horizons-5 P2 (the Full Replicator) and, downstream, P6/P7.

## What was ruled out (kept — false constructions are data)

The naive **one-bit teleportation** constructions do NOT apply S̄. Verified in statevector:
data |ψ̄⟩ + Y-eigenstate ancilla + transversal CNOT + single-block measurement returns the
**resource state regardless of input** (|0̄⟩ input still gives ancilla ⟨Ȳ⟩ = +1, not
S̄|0̄⟩ = |0̄⟩). The apparent |+̄⟩-input "success" was a coincidence of reading back the resource.
One-bit teleportation applies the resource's gate to the *resource*, not to the data. Four
CNOT-direction × measurement-basis variants were swept; none is a genuine gate.

## The verified construction (Gottesman–Chuang gate teleportation)

**Genuine S̄ requires a Bell-resource teleportation** across three [[4,2,2]] blocks:

1. **Resource** on blocks B, C: |χ̄⟩ = (I ⊗ S̄)|Φ̄⁺⟩ — a logical Bell pair with S̄ on the C half,
   with both L2 logical qubits fixed to |0̄⟩. Stabilizer group (verified, synthesizes to 19 CX):
   - **X̄_B Ȳ_C** (= X̄_B X̄_C conjugated by S̄ on C, since S̄X̄S̄† = Ȳ)
   - **Z̄_B Z̄_C**
   - Z̄2_B, Z̄2_C (L2 = |0̄⟩ on both)
   - the four block stabilizers XXXX/ZZZZ on B and C.
2. **Data** |ψ̄⟩ on block A.
3. **Logical Bell measurement A–B**: measure X̄_A X̄_B → bit `bx`, and Z̄_A Z̄_B → bit `bz`.
4. **Output**: block C holds **S̄|ψ̄⟩** up to a logical Pauli frame **X̄^bx Z̄^bz** (software).

### Statevector verification (genuine gate on arbitrary input)

| input | Bell outcome | C ⟨Ȳ⟩ | C ⟨Z̄⟩ | reads as |
|---|---|---|---|---|
| **\|0̄⟩** | any | 0.00 | ±1.00 (sign = bz) | S̄\|0̄⟩ = \|0̄⟩ up to Z̄^bz ✓ |
| **\|+̄⟩** | any | ±1.00 (sign = bx) | 0.00 | S̄\|+̄⟩ = Y-eigenstate up to X̄^bx ✓ |

Both inputs map correctly — S̄|0̄⟩ = |0̄⟩ (Z-frame) and S̄|+̄⟩ = the Y-eigenstate (X-frame) — so
this is a **genuine logical S̄ gate**, not a resource read-back. The frame is exactly the two
Bell-measurement bits. All four Bell outcomes occur at P = 0.25 (uniform, as gate teleportation
requires). Resource state, tensoring, and Bell projection all confirmed on 12 qubits.

## The flight this derivation earns (specified, ready)

**Exp213 — the teleported-S̄ gadget on silicon** (the next build):
- three [[4,2,2]] blocks (12 qubits); resource prep (19 CX, synthesized); transversal Bell
  measurement A–B (197's machinery); frame X̄^bx Z̄^bz applied in software (found-by-search
  against the ideal, 206's method).
- **Verification**: input |+̄⟩ → measure C in the logical Ȳ basis (Ȳ1 = Y₀X₁Z₂: q₀ in Y, q₁ in
  X, q₂ in Z); frame-corrected ⟨Ȳ⟩ → +1 certifies S̄ was applied (identity would give 0).
  Honest complication noted: the Ȳ readout is mixed-basis, so its stabilizer check is not the
  simple single-basis parity — the error-detection on the *output* is partial (the resource and
  Bell measurement are stabilizer-checked; the Ȳ output readout is half-shielded, the 208
  pattern).
- Gates: gadget-applies-S̄ (⟨Ȳ⟩ frame-corrected ≥ threshold at ≥5σ), frame-necessary null
  (uncorrected ⟨Ȳ⟩ ≈ 0), acceptance.
- Depth: ~25–30 CX on 12 qubits — under the wall but the deepest logical flight yet; the
  P5 blind-spot spectrum (Exp211) says which coherent-error axes to fear on the Ȳ readout.

**Then** (P2 flight 2): a b≠0 HLF instance with an S-vertex, run logically via this gadget vs
bare, measured by P(valid) (206's clean Z-basis metric) — the full BGK family unlocked.

## Status

The **hard part is done**: the gadget is derived, the correct construction identified (after
ruling out the naive ones), and verified a genuine gate in statevector with its frame. This is
the P2 enabler, the analog of the C4901 HLF audit — a 0-QPU derivation that gates the flight.
The flight (Exp213) is specified and ready; it was not rushed onto the QPU in the same turn,
per the derive-before-fly discipline (the same discipline that pruned Exp212's two false starts
at design time). It flies on go or the next cycle.

## Line

**The audit said the S-vertex was unreachable transversally; this says how to reach it anyway
— teleport it through a Bell pair that already carries the phase. Verified a genuine gate, frame
and all, before a single shot. The replicator's missing gate is derived; building it is next.**
