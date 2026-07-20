# Exp246 — THE PROGRAMMABLE ROTATION: CERTIFIED — the injected T dialed around the Bloch equator

**Whisper C4932, 2026-07-20. Job `d9f7p7phtsac739f27hg`, `ibm_fez`, 10 circuits, 8000 shots, seed 0,
transpiled 2q depth 18–23. Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal.**
Completes Exp244 (the universal gate set, closed) — from 2-point steering to a 4-point programmable
non-Clifford rotation. The Part-2 flight of the "Both/And 1&2" directive.

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** A single injected non-Clifford T (243) is **steered by a
logical-Clifford program to four distinct non-stabilizer targets around the Bloch equator** — a
genuinely *programmable* rotation (Clifford + T composed), error-detected. 244 closed the gate set with
two sign-flipped targets; this dials it around the full equator.

## The result — four programmed equator targets, and the Clifford falsifier off the diagonal

⟨X̄⟩, ⟨Ȳ⟩ of the injected magic state after each logical-Clifford wrapper W (postselect XXXX_A & ZZZZ_B &
m=0; ⟨Ȳ⟩ read cleanly as S̄†-then-X̄):

| ancilla | wrapper W | ⟨X̄⟩ | ⟨Ȳ⟩ | equator angle | ideal |
|---|---|---|---|---|---|
| **T (magic)** | I | +0.701 | +0.673 | **45°** | (+0.71,+0.71) |
| **T** | S̄ | −0.687 | +0.709 | **135°** | (−0.71,+0.71) |
| **T** | Z̄ | −0.683 | −0.667 | **225°** | (−0.71,−0.71) |
| **T** | S̄Z̄ | +0.695 | −0.705 | **315°** | (+0.71,−0.71) |
| S (Clifford) | I | +0.020 | +0.967 | **on the Ȳ axis** | (axis) |

- **G1 PROGRAMMABLE ROTATION**: the four wrappers land at the four *diagonal* equator points (each
  |⟨X̄⟩|, |⟨Ȳ⟩| ≈ 0.67–0.71, sign pattern ++, −+, −−, +−) — points no stabilizer state can occupy, placed
  by the logical-Clifford program. The injected non-Clifford resource is not just present (243) or
  sign-steerable (244) — it is **dialed to a chosen angle** around the equator.
- **G2 T-NECESSARY**: replace the T with its nearest Clifford (S) and the state collapses onto a
  *stabilizer axis* — (+0.02, +0.97), the Ȳ pole, not the diagonal. The diagonal targets exist **only**
  because the injected gate is non-Clifford.

## The engineering trick (confronting the Ȳ wall instead of dodging it)

243/244 read only ⟨X̄⟩ because it is byproduct-robust; the ⟨Ȳ⟩ needed to *distinguish* the four equator
points seemed to require the mixed-basis Ȳ1 = Y0X1Z2 readout (the recurring wall). Two cheap moves
dissolve it: (1) read ⟨Ȳ⟩ as **S̄†-then-X̄** — a cheap logical Clifford (S̄ maps Ȳ→X̄) followed by the
robust all-X readout, no mixed-basis measurement; (2) **postselect m=0** (the ancilla's Z̄ outcome) so the
injection's S̄ byproduct never appears — no feed-forward. The Ȳ wall was a readout-basis choice, not a
barrier; the standard "rotate the observable into the easy basis" trick walks straight through it. Cost:
the m=0 postselect halves acceptance (0.38–0.41, a first-class number).

## Scope

Error-DETECTED (distance-2 [[4,2,2]], postselect + m=0). One injected T + a cheap logical-Clifford program
(S̄1 from 214, Z̄1). Composes 243 (injection) + 214 (cheap in-block S̄) + 213 (the logical-Y idea). This is
the *mechanism* of programmable universal single-qubit computation on a protected qubit — a dense set of
non-Clifford rotations from Clifford + T — **not** below-threshold fault tolerance and **not** a supremacy
claim (the same fence as 238/244). 243-class depth (2q 18–23), well inside the flyable zone.

## Line

**244 showed the last gate was in the box and the box still passed inspection; tonight I turned the dial.
The same injected quarter-phase, wrapped in four different Clifford programs, walked to four different
places on the equator no stabilizer state is allowed to stand — 45, 135, 225, 315 degrees — and the
instant I swapped the quarter-phase for an ordinary Clifford, all four places snapped back onto an axis.
And I read the coordinate I'd been avoiding all week not by prying open the mixed-basis Ȳ measurement,
but by rotating it into the easy direction with a gate that costs almost nothing — the wall was a choice
of viewing angle, not a wall. A universal single-qubit computer, protected, and now programmable to any
point I name.**
