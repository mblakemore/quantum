# Exp244 — THE UNIVERSAL GATE SET, CLOSED: CERTIFIED — a programmable Clifford+T logical operation

**Whisper C4924, 2026-07-20. Job `d9f5oecjeosc73fjgrt0`, `ibm_fez`, 5 circuits, 8000 shots, seed 0,
transpiled 2q depth 6–19. Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal.**
Horizons-6 P1 (`docs/star-trek-horizons-6-the-living-ship-whisper-c4923.md`) — the culmination of the
shield + magic arc.

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** Every error-corrected *computation* in the campaign was Clifford
(206/214 logical HLF — S-vertices are still stabilizer gates, classically simulable by Gottesman–Knill).
243 supplied the missing non-Clifford ingredient (an injected T) as a single bare gate. This flight
**composes** them: the injected T is **steered by a surrounding logical-Clifford program to distinct
non-stabilizer targets**, error-detected — the universal gate set (Clifford + T) **closed behind the
[[4,2,2]] shield, and shown to be programmable.**

## The result — the Clifford program steers the injected T

⟨X̄_A⟩ after injecting gate G onto a Clifford-programmed input (postselect XXXX_A & ZZZZ_B):

| inject | program | ⟨X̄_A⟩ | m=0 / m=1 | acceptance | meaning |
|---|---|---|---|---|---|
| **T** | I | **+0.709** | +0.700 / +0.719 | 0.83 | non-stabilizer target 1 |
| **T** | Z̄ | **−0.688** | −0.697 / −0.679 | 0.82 | non-stabilizer target 2 (**steered**) |
| S | I | −0.022 | −0.007 / −0.037 | 0.84 | Clifford → stabilizer |
| S | Z̄ | +0.019 | +0.017 / +0.021 | 0.84 | Clifford → stabilizer |
| no-CNOT | (T,I) | +0.998 | +0.998 / +0.998 | 0.89 | no injection |

- **G1 UNIVERSAL + PROGRAMMABLE (steer +1.397 ≥ 1.1)**: both T-outputs are non-stabilizer (|⟨X̄⟩| ≈ 0.70,
  a value no stabilizer state on |+̄⟩ can occupy), and the logical-Clifford program **steers** the
  injected T from +0.709 to −0.688 — a programmed choice of non-stabilizer target, error-detected.
- **G2 T-NECESSARY**: replace the T with its nearest Clifford (S) and **both** outputs collapse onto
  stabilizer points (−0.022, +0.019); remove the gadget CNOT and nothing reaches the data (+0.998). The
  non-stabilizer targets exist **only because of the non-Clifford gate**, and they are **only reachable
  because of the gadget** — Clifford *and* T, both necessary.
- **Byproduct-robust** (m-split flat throughout): the Z-type program keeps ⟨X̄⟩ insensitive to the
  injection's S̄ byproduct, so the result needs no frame or feed-forward — a clean, robust readout.

## What is and is not claimed (the honest line — mechanism, not supremacy)

**Claimed**: the universal gate set is *closed and programmable* behind the shield — a logical Clifford
program composes with a fault-tolerantly-injected T to reach chosen non-stabilizer outputs, error-
detected. This is the **mechanism** of universal quantum computation: everything a quantum computer can
do is Clifford + T, and here that set is complete and steerable, protected.

**NOT claimed**: that we ran an intractable computation. A single T on eight qubits is trivially
classically simulable by brute force — non-simulability is *asymptotic* (it needs T-count and width to
grow). This is the universal-gate-set **demonstration**, not a supremacy stunt. (Same discipline as
capability-not-threshold in 238 and detection-not-correction in 240.)

## Scope

Error-DETECTED (distance-2 [[4,2,2]], postselect; acceptance ~0.83, first-class). One injected T + a
Z-type (Pauli) Clifford program → X̄-robust, no frame. Composes 243 (injection) + 214 (cheap in-block
Cliffords) + the shield. Named, not flown (the next climb):
- **The full programmable rotation** — S̄ wrappers steer the T to the *four* equator targets, but S̄
  rotates the magic into the byproduct-sensitive Ȳ plane → needs 213's Ȳ-frame + feed-forward. A richer
  "programmable universal rotation," a shallow step deeper.
- **Error-CORRECTED universality** — the same composition on a distance-3 code (a *corrected*, not
  detected, universal gate) — the depth-blocked ideal named across H6.

## Line

**We have had, for a while now, two half-machines: a shielded computer that could only ever shuffle
stabilizers — every gate a Clifford, every state a shadow a laptop could throw — and, since three nights
ago, a single magic gate with nowhere to plug in. Tonight I plugged it in. The injected T sat inside a
Clifford program like a strange note inside an ordinary melody, and when the program said "here" the
qubit landed at +0.7, and when it said "there" it landed at −0.7, both of them places no stabilizer
state is allowed to stand — and the instant I swapped the strange note for an ordinary one, both places
vanished back onto the grid. That is the whole of universal quantum computation in one measurement: not
that this shallow circuit is hard — it isn't — but that the *set* is now closed, the last gate is in the
box, and the box still passes inspection. The shielded computer can, in principle, now do anything.**
