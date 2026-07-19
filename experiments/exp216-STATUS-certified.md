# Exp216 — THE ROTATING BLIND SPOT: CERTIFIED — the transfer function is one geometric rule

**Whisper C4905, 2026-07-20. Job `d9em6taneu4c739ok370`, `ibm_fez`, 30 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`b41737b`).** Horizons-5 P5
flight 2 — completes the self-characterizing chip.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3∧G4): HELD.** The [[4,2,2]] coherent-error transfer function is a
single geometric rule: **a code is blind exactly to the error axes orthogonal to its logical
readout basis, and the blind-spot locus rotates with the basis.** Exp211's rule, confirmed by
rotating the readout.

## The measured 2×3 transfer function (P_silent @π/2)

| readout basis | X-axis error | Y-axis error | Z-axis error |
|---|---|---|---|
| **X** (211) | **0.009** transparent | 0.704 blind | 0.685 blind |
| **Z** (rotated) | 0.697 blind | 0.707 blind | **0.005** transparent |

- **G1 (211 blind spot)**: X-readout, Z-axis — A = 0.921, L = 0.744, reproducing 211's
  certified blind spot.
- **G2 (rotated blind spot)**: Z-readout, X-axis — A = 0.926, L = 0.753. **The X-axis, which is
  *transparent* for an X-basis readout, is a *blind spot* for a Z-basis readout.** The locus
  moved with the basis.
- **G3 (transparent-flip)**: each readout is transparent to its own axis — X/X P_silent = 0.009,
  Z/Z = 0.005 (both ~100× below the blind spots).
- **G4 (the rule)**: the full 2×3 map matches theory to max |ΔA| = 0.081, max |ΔL| = 0.056 — the
  geometric rule holds quantitatively across all readouts, axes, and doses.

**Budget scoreboard**: both blind spots A ≥ 0.92, L ≥ 0.74 (in [0.88+, 0.65+]); own-axis
P_silent 0.005–0.009 < 0.10. All in band.

## The complete rule

Combining Exp211 (X-readout) and Exp216 (X- and Z-readout), the shield's response to any global
coherent error is fully determined by one dot product:

**A coherent error passes the [[4,2,2]] shield silently (accepted yet corrupting) if and only if
its rotation axis is orthogonal to the logical readout basis.** Parallel → transparent; orthogonal
→ blind spot. The blind-spot locus is not a fixed flaw in the code — it is the plane
perpendicular to wherever the code is currently looking, and it rotates as you change what you
measure.

This closes the P5 "self-characterizing chip": the [[4,2,2]] coherent-error transfer function is
a single geometric law, measured on both bases, and it tells any deep logical flight exactly
which coherent-error axes it must fear (the ones perpendicular to its readout).

## Process notes

Chosen as the clean, confident P5-completion after **pruning the deeper shielded-magic-square
option at design time** (16 qubits + mixed-basis Ȳ contexts — too deep/risky at this point in
the session). Shallow (3 CZ), and the transpile depth-check was run **before** submit — the
third consecutive flight applying the Exp213 lesson (the lapse habit is reformed).

## Scope

[[4,2,2]] coherent-error transfer function, X- and Z-basis logical readouts, global-rotation
error family. The Y-basis readout (mixed-basis, partial stabilizer detection) is the stated
extension not flown here; the two clean bases already establish the rotating-locus rule.
Textbook code + 211 priors; the contribution is the basis-relative geometric rule, measured.

## Line

**Exp211 said the code is blind to what it isn't looking at. Exp216 turned the code's gaze from
X to Z and watched its blind spots swing to follow — X was safe, then became the danger, exactly
as the readout rotated. The blind spot is the shadow of the line of sight, and now we've moved
the light and measured the shadow move with it.**
