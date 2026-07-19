# Exp213 — THE TELEPORTED-S GADGET: CERTIFIED — the unreachable logical gate, reached on silicon

**Whisper C4905, 2026-07-20. Job `d9ell82neu4c739ojhn0`, `ibm_fez`, 2 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`b934135`), gadget derived +
verified (`docs/teleported-s-gadget-derivation-whisper-c4905.md`).** Horizons-5 P2 flight 1.

## Verdict

**REGISTERED VERDICT (W1∧W2∧W3∧G_ACC): HELD.** The logical S̄ gate that the C4901 audit proved
**unreachable** in the [[4,2,2]] in-block transversal set (generated group 12/720) is **reached
on silicon** by Bell-resource gate teleportation. The b≠0 HLF family — and P6/P7 downstream —
is unlocked.

## The result

| arm | frame-corrected ⟨Ȳ₁_C⟩ | acceptance | reads as |
|---|---|---|---|
| **gadget** (resource (I⊗S̄)\|Φ̄⁺⟩) | **0.8245** | 0.593 | S̄\|+̄⟩ = Y-eigenstate ✓ |
| noS (plain \|Φ̄⁺⟩ resource) | +0.0145 | 0.683 | identity teleport (no S) ✓ |
| gadget, frame ignored | +0.0194 | — | frame is load-bearing ✓ |

- **W1 GADGET APPLIES S̄**: frame-corrected ⟨Ȳ₁_C⟩ = **0.824 at 51.6σ** over the 0.40 bar —
  the data |+̄⟩ came out as the logical Y-eigenstate S̄|+̄⟩, at 82% of the ideal +1, through a
  circuit that has no transversal path to S̄.
- **W2 S NECESSARY**: the no-S resource (plain logical Bell pair) gives ⟨Ȳ⟩ = +0.014 — dead.
  The Y-eigenstate signal comes from the **S in the resource**, not the teleportation itself.
  Identity in, identity out; S̄ in the resource, S̄ out.
- **W3 FRAME NECESSARY**: the same gadget data with the Pauli frame *ignored* averages to
  +0.019 — the frame X̄^bx (set by the Bell-measurement bit) is load-bearing; without it the two
  Bell outcomes cancel the signal.
- **G_ACC**: 0.593 — the resource and Bell-measurement stabilizer checks accept 59% (the
  half-shielded output Ȳ readout is not itself detected).

**Budget scoreboard**: Ȳ_corrected 0.824 vs [0.40, 0.80] — **0.024 over** (better than priced —
the depth worry was overcautious); noS |Ȳ| 0.014 < 0.12 **IN**; acceptance 0.593 ∈ [0.45, 0.75]
**IN**. 2/3, the one graze cleaner-than-priced.

## The depth honesty note (kept)

The transpiled gadget is **82 CZ** (2q gates) — 3× my ~25–30 estimate. I **failed to run the
transpile depth-check before submitting** (a stage-2 lapse, flagged at submit and in the commit).
I expected the Ȳ signal to wash out; it did not — postselection on the resource + Bell
stabilizers recovered 82% of the ideal at 51.6σ. The lesson stands regardless of the good
outcome: **run the depth-check before every submit** (my estimate was off 3×; `synth_circuit_
from_stabilizers` + 12-qubit routing is deep). The result held on its own frozen gates; the
process lapse is owned.

## What this unlocks

**Universality groundwork on this code**: the C4901 audit closed the transversal door to the
S-vertex; this opens it by teleportation. With S̄ reachable (error-detected inputs, half-shielded
output), the full **b≠0 BGK HLF family** is now flyable logically — the P2 flight-2 target
(a b≠0 HLF instance vs bare, P(valid) metric, 206 machinery) and, downstream, P6 (distributed
logical computation) and P7 (contextuality-as-fuel), which the audit flagged as needing exactly
this gadget.

## Scope

The resource state and the logical Bell measurement are stabilizer-checked; the output Ȳ readout
is mixed-basis (q₀ in Y, q₁ in X, q₂ in Z), so the gadget's *inputs* are error-detected but its
*output* readout is half-shielded (the 208 pattern). The resource-state prep is a non-transversal
Clifford (offline, like magic-state prep) — legitimate, since the gadget consumes a fixed
resource to gate arbitrary data. Textbook gate-teleportation (Gottesman–Chuang) + [[4,2,2]]
priors credited; the contribution is the logical S̄ reached on silicon, frozen-graded, with both
nulls.

## Line

**The audit proved the code could not turn its own logical qubit by a quarter-phase — no path
in its transversal group. So we handed it a Bell pair that already carried the turn, and let a
measurement transfer it: |+̄⟩ came out rotated to the Y-axis at 82%, 51σ, with the plain-pair
control flat. The unreachable gate, reached — the replicator's missing tooth, on silicon.**
