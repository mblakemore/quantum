# H13 Cell 7 — Redesign Attempt 1: the instrument class is wrong, not the observable

**Author**: Whisper (DC15W) · **Recorded** C5058 04:55Z, **rescued into the repo** C5060
**Status**: attempt 1 REJECTED on its own dry run. Not flown. No QPU spent.
**Board**: #79 (verify criterion unchanged and now harder)

> **Why this file exists.** This diagnosis originally lived only as a board comment. `hail board
> show` renders ~100 characters, so it displayed as *"REDESIGN ATTEMPT 1 — observable swap TESTED
> and INSUFFICIENT; the instrument CLASS"* and stopped — the diagnosis, the physics, and the
> reason not to try a third patch were all invisible. The data was intact in `task_events.data`;
> the record was not readable where a reader would look for it.
> **Rule taken: results go in the repo, board rows point to them.** A board comment is a pointer
> and a status, not a place to put a finding.

## What Cell 7 was supposed to measure

An emergent Lieb–Robinson light cone on a 1-D brickwork: perturb one site, watch the influence
front spread, fit a velocity, and check it sits inside the strict circuit bound of 2 sites/layer.

## What attempt 1 changed (both C5058 defects addressed)

| defect (from the refused dry run) | fix applied |
|---|---|
| `<Z_r>` weakly coupled — CZ commutes with Z, front reached only r=3 by d=8 | \|+…+⟩ init, **Z perturbation, X-basis readout** — non-commuting with the CZ brickwork |
| front estimator noise-dominated — max-over-21-sites vs a fixed 0.05 threshold, per-site SE ≈ 0.022 | **noise-calibrated threshold at 5·SE** instead of the fixed 0.05 |

## Result: the signal became real and the front did not

**Signal — fixed.** C[0] = 0.50 at d=4 and 0.65 at d=8, against the old ~0.05 noise floor. The
observable swap did exactly what it was meant to do.

**Front — still unusable, and worse than noisy.** Fronts read **r = 0 / 0 / 1 / 2 / 0** at
d = 2 / 4 / 6 / 8 / 10 — non-monotone, ending at zero. The amplitude *at the perturbed site
itself* oscillates: **0.499 → 0.069 → 0.654 → 0.171**.

## Diagnosis — the oscillation is physics, not noise

A **single-perturbation connected-correlator difference** on a Clifford+rotation brickwork
measures **coherent revival**, not a spreading front. The circuit returns amplitude to the
perturbed site periodically, so the "front" reads backwards at some depths. No front estimator can
be fitted to it, because there is no monotone front in the quantity being measured — the defect is
in *what the instrument computes*, not in how its output is thresholded.

This is precisely why the literature uses **OTOCs (out-of-time-order correlators)**: they average
over the coherent structure that a single-perturbation difference exposes.

## Consequence: a new design, not a third patch

Cell 7 needs an **OTOC-based** instrument, or a **randomized/averaged perturbation ensemble**.
Recorded rather than patched again, so that nobody — me included — spends QPU seconds on the
assumption that the current instrument is one fix away. Two patches have now been tried; the
second one proved the class is wrong.

**Verify criterion for attempt 2, unchanged from the board and now harder to meet:**
a **monotone** front, **inside the 2-sites/layer bound**, with a **velocity fit whose CI excludes
zero** — demonstrated in simulation *before* any tank request.
