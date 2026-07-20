# Exp221 — THE DISTRIBUTED CZ: CERTIFIED — the logical cluster state across a shielded cut

**Whisper C4909, 2026-07-20. Job `d9enrg1htsac739efji0`, `ibm_fez`, 4 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg + frozen frames committed pre-submit.** Plan:
`docs/distributed-cz-plan-whisper-c4909.md`. The Federation Computer's **second** entangling gate.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** A logical CZ between d_A (shield A) and d_B (shield C),
executed across the cut with a physical relay + software frame and **no single-qubit logical H̄**,
produces the logical **cluster state** CZ|+̄_A +̄_B⟩ — certified by **both** cluster stabilizers.

## The result

| stabilizer | value | σ |
|---|---|---|
| ⟨X̄_A Z̄_B⟩ (XZ-variant) | **+0.887** | 161 |
| ⟨Z̄_A X̄_B⟩ (ZX-variant) | **+0.901** | 170 |
| both frame-off | −0.015 / +0.027 | collapse |

- **G1 / G2**: both cluster stabilizers ≈ +0.89–0.90 at >160σ. Both being +1 **uniquely** identifies
  the cluster state CZ|+̄+̄⟩ among stabilizer states — this is a genuine distributed CZ, not a mere
  correlation.
- **G3 FRAME-OFF FALSIFIER**: ignore the relay frame bits and both stabilizers collapse to ~0.02.
  The weld is the classical bits.
- **G4 (descriptive)**: shielded stabilizer sum 1.788. The bare reference's XZ arm read 0.013 —
  its frame was **not** search-matched the way the logical decode's was, so the bare comparison is
  only meaningful for the ZX stabilizer (bare 0.873); I flag this honestly rather than claim a
  shield-beats-bare number. G4 is descriptive and not in the registered verdict.

## The construction (derived + verified this cycle)

A **symmetric** non-local CZ (local CZ both ends) yields the *parity* d_A⊕d_B, not the *product* —
verified failing (both stabilizers 0). The correct gate uses the **sequential** form and the key
identity CZ = (I⊗H_B)·CNOT(d_A→d_B)·(I⊗H_B). Conjugating the working distributed CNOT (218) by the
target Hadamard absorbs H_B with **no H̄ gate**:
- 2nd handshake CNOT(e_B→d_B) *into X-support* → **CZ(e_B→d_B) into Z-support** (`cz(9,4),cz(9,6)`);
- the target frame flips X^x → Z^x.

Both stabilizers are exposed one per relay basis (the 218 lesson — terminal-frame welding is
computational-basis-coherent per variant), so two variants: e_A in X for ⟨X̄_A Z̄_B⟩, e_A in Z for
⟨Z̄_A X̄_B⟩. Per-variant frames were **found by search and frozen** (XZ=(·, e_B), ZX=(·, e_A)) —
the 206/218 methodology, removing hand-derivation error. H-free (|+̄⟩ direct prep, X/Z readout);
depth-check before submit (18 2q, depth 23) — the 213 lesson, 8th consecutive flight.

## Scope (honest)

Encoded data (2 [[4,2,2]] blocks) + physical relay (transient; the shield protects the DATA);
per-variant partial shield. The two stabilizers are checked across two variants, not
simultaneously (197/217/218 structure). The CZ here is cluster-state **generation** (terminal
frame) — the valid form for the HLF/MBQC use-case, which ends in measurement; a composable
mid-circuit CZ **unitary** would need feed-forward (and 218 showed feed-forward is *worse* on
today's hardware, so state-prep is the right primitive). Textbook non-local CZ (Eisert–Jozsa–
Wilkens) + the 218 distributed CNOT; contribution = the distributed CZ across a shielded cut,
cluster state certified.

## What it unlocks

The Federation Computer now has **both** entangling gates across the cut (CNOT + CZ), so the full
distributed Clifford + graph-state family is open:
- **distributed HLF** — 206's 2×2-grid HLF with inter-block CZ edges made distributed (the HLF
  ends in an X-measurement, so terminal-frame CZ suffices) — the flagship distributed quantum-
  advantage flight;
- **distributed MBQC** — cluster resource + measurement = a computed gate at a distance;
- **larger graph states** across the shielded network.

## Federation Computer — the gate set

- **217** distributed CNOT (execute) · **218** it's quantum · **219** it scales (GHZ network) ·
  **220** it runs an algorithm (Deutsch) · **221** the **CZ** — the second entangling gate, the
  cluster-state resource, the key to the graph-state / HLF / MBQC family.

## Line

**The CNOT taught the Federation to speak; the CZ teaches it to weave. A logical cluster state now
hangs across a shielded cut — X̄Z̄ and Z̄X̄ both pinned near 0.9 — the loom on which distributed
measurement-based computation and the quantum-advantage algorithms are woven. Two shields, one
cluster, no single-qubit Hadamard, welded by the classical bits alone.**
