# Exp191 Pre-registration — THE SHIELDED HANDSHAKE: a logical Bell pair between two code blocks (Shields stage iii)

**Cycle**: C4883 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 8 circuits
**Arc**: THE SHIELDS stage (iii); operating point set by stage (ii)'s map (≤0.5 μs idle, where
the shield pays 2× at 6σ). Creator go: general#137.

## The claim

Entangle two **logical** qubits living in two separate [[4,2,2]] blocks (8 physical qubits),
via the code's **transversal CNOT** (4 physical CXs, block-to-block, the FT-native two-qubit
gate), and certify the logical entanglement against the theorem-fixed **two-setting separable
bound**: S = ⟨X̄X̄⟩ + ⟨Z̄Z̄⟩ ≤ 1 for every separable state. Only Z-readout and X-readout are
needed; stabilizers of *both* blocks are checked in the same shots (ZZZZ per block in Z;
XXXX per block in X).

**The internal control the code gives for free**: each block carries TWO logical qubits. L1
(A↔B) gets the Bell pair; **L2 rides along in a product state |0̄⟩⊗|0̄⟩** through the *same*
transversal CNOT in the *same* shots — its S must sit **exactly AT the separable bound**
(⟨Z̄₂Z̄₂⟩ ≈ 1, ⟨X̄₂X̄₂⟩ ≈ 0 ⇒ S ≈ 1). One dataset, one entangled logical pair over the bound,
one product logical pair on it: the witness calibrates itself in-shot.

## Construction (all layouts verified in selftest)

Block A |+̄0̄⟩ = Bell(q0,q1)⊗Bell(q2,q3); Block B |0̄0̄⟩ = GHZ4(q4..q7); transversal CX
(q_i→q_{i+4}); logical readout: Z̄₁ = z₀⊕z₂ / z₄⊕z₆, X̄₁ = x₀⊕x₁ / x₄⊕x₅, Z̄₂ = z₀⊕z₁ / …,
X̄₂ = x₀⊕x₂ / …; postselect per-block stabilizer parity in each basis.

## Arms (8 circuits: {Z, X} readout each)

| arm | what |
|-----|------|
| **logical** | the shielded handshake |
| logical_idle | + 0.5 μs quarter-point-echoed idle after the CX (the mapped operating point) |
| nocx | falsifier: blocks never interact → S_L1 ≈ 0 (both correlators vanish); S_L2 still ≈ 1 |
| bare | physical Bell pair reference |

## Pre-registered criteria (formulas; se from postselected counts)

Let N_acc = accepted shots per basis; se(corr) = 1/√N_acc; se(S) = √(se_X² + se_Z²).

- **Primary**: `S_L1(logical) > 1` with `(S_L1 − 1)/se(S) ≥ 5`. Band **1.55–1.85**.
- **Internal control**: `S_L2(logical) ∈ 0.85–1.05` — at the bound, not over.
- **Operating point**: `S_L1(logical_idle) > 1 at ≥5σ`. Band 1.35–1.75.
- **Falsifier**: `S_L1(nocx) ∈ −0.10..+0.15` AND `S_L2(nocx) ∈ 0.85–1.05`.
- **Reference**: S_bare ∈ 1.80–1.95 (logical will run below bare — the claim is crossing the
  separable bound with *shielded* qubits plus the in-shot product control, not beating bare).
- **Gauges**: two-block acceptance ≥ 0.70 per basis (product of block acceptances).

## Fences

Distance-2 detection + postselection (not correction); one round; transversal CX is the FT-native
gate but no claim of full fault tolerance is made (no repeated syndrome cycles); ⟨ȲȲ⟩ not
measured (mixed-Pauli logical operator — the two-setting witness needs only X̄X̄+Z̄Z̄ and its
bound is a theorem); one die, one job; stage (iv) = teleport a logical qubit, using this pair.

## Discipline

ps aux clean; claim exp191 (whisper C4883); ledger pre-submit; prereg committed before decode.
Selftest gates: S_L1 = 2.000, S_L2 = 1.000 (exactly at the bound), nocx S_L1 = 0, bare = 2.000,
all acceptances 1.
