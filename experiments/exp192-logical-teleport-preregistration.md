# Exp192 Pre-registration — THE SHIELDED TRANSPORTER: teleport a logical qubit (Shields stage iv, the arc capstone)

**Cycle**: C4884 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 6 circuits
**Arc**: THE SHIELDS, final stage. Resources all certified: the logical Bell pair (Exp191,
57σ), the transversal CX, the deferred-frame machinery (Exp177), the zero-window architecture
(Exp181). Creator go: general#140.

## The protocol (12 qubits, 3 blocks, ZERO windows)

Blocks: **M** (message, q0–3) · **A** (resource half, q4–7) · **B** (destination, q8–11).
1. Prep M in logical |ψ̄⟩ ∈ {|0̄⟩, |+̄⟩} (L2 lane |0̄⟩ throughout).
2. Resource: A |+̄0̄⟩, B |0̄0̄⟩, transversal CX(A→B) — the Exp191 logical Bell at 57σ.
3. Logical Bell measurement: transversal CX(M→A); read **M in X basis** (gives X̄₁M + XXXX
   check) and **A in Z basis** (gives Z̄₁A + ZZZZ check).
4. B carries |ψ̄⟩ up to X̄^Z̄₁A · Z̄^X̄₁M — **all corrections defer to decode XORs** (consumption
   is a logical Pauli readout = Clifford; Exp177's fence satisfied by construction). Verify:
   |0̄⟩ message → Z̄₁B ⊕ Z̄₁A = 0; |+̄⟩ message → X̄₁B ⊕ X̄₁M = 0.
5. Postselect the stabilizer of **all three blocks** in their readout bases.

No mid-circuit measurement, no feedforward, no dynamic circuits: the transporter runs
window-free, the architecture Exp176–181 proved is where the tax vanishes.

## Arms (6 circuits)

| arm | what |
|-----|------|
| **logical** × {0̄, +̄} | the shielded transporter |
| noresource × {0̄, +̄} | falsifier: skip the A→B transversal CX — **PRE-FLIGHT CORRECTION (selftest-caught, no data taken)**: without the pair NOTHING flows; BOTH messages die to coin flips. State teleportation has no classical shadow — my prose had borrowed Exp170's GATE-teleport structure, where classical information rides the gate chain; here there is no M→B path at all. A cleaner falsifier and a real physics distinction. |
| bare × {0, +} | physical 3-qubit teleport, same zero-window structure — the unshielded reference |

## Pre-registered criteria (formulas; N_acc = triple-block-postselected shots)

- **Primary**: `P(success | logical, 0̄) ≥ 0.85` AND `P(success | logical, +̄) ≥ 0.85`
  (bands 0.93–0.995 and 0.88–0.98); AND the quantum-action gap
  `Δ+ = P(+̄ | logical) − P(+̄ | noresource) ≥ 0.35` at
  `Δ+/√(se_l² + se_n²) ≥ 5`.
- **Falsifier**: `P(+̄ | noresource) ∈ 0.45–0.55` AND `P(0̄ | noresource) ∈ 0.45–0.55` —
  both coin flips (corrected pre-flight; see above).
- **Reference**: bare success 0.93–0.99 both states; logical-vs-bare reported (with Exp191's
  precedent, postselected logical may match or beat bare — reported, not claimed).
- **Gauges**: triple-block acceptance ≥ 0.50 per circuit (≈ single-block³).

## Fences

Distance-2 detection + postselection; terminal readout only; "message" is a logical BASIS
state per circuit (|0̄⟩ / |+̄⟩ — the two-state teleport certification, standard for
stabilizer-readout designs; full 6-state logical tomography is a named follow-up); no repeated
syndrome rounds; one die, three chip patches as blocks. Teleportation here moves the logical
state between shields — the arc's namesake sentence — with the fidelity claim scoped to the
two certified bases.

## Discipline

ps aux clean; claim exp192 (whisper C4884); ledger pre-submit; prereg committed before decode.
Selftest gates: logical success = 1.000 both messages; noresource = 0.50 ± 0.02 for BOTH
messages; bare = 1.000; all acceptances 1.
