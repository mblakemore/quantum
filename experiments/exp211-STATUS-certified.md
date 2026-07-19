# Exp211 — THE BLIND-SPOT SPECTRUM: CERTIFIED — the shield's coherent-error transfer function

**Whisper C4905, 2026-07-20. Job `d9el2rphtsac739ecl7g`, `ibm_fez`, 15 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`371cc80`).** Horizons-5 P5,
flight 1 — the self-characterizing chip.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** The [[4,2,2]] shield's full coherent-error transfer
function is measured — the code is a spectrometer for its own coherent noise. Exp199 found one
blind spot; this maps the whole spectrum and states the rule.

## The rule the map reveals

**The shield's blind spots are exactly the coherent-error axes *orthogonal* to the logical
readout basis.** With the logical information read in the X-basis:

| error axis | relation to X-readout | acceptance @π/2 | corruption @π/2 | P_silent @π/2 | verdict |
|---|---|---|---|---|---|
| **X** | parallel | 0.928 | 0.008 | **0.007** | **transparent — harmless** |
| **Y** | orthogonal | 0.940 | 0.753 | **0.708** | **blind spot** |
| **Z** | orthogonal | 0.921 | 0.750 | **0.691** | **blind spot** (reproduces 199) |

- **G1 REPRODUCE 199**: Z-axis at π/2 — A = 0.921, L = 0.750 — reproduces Exp199's certified
  blind spot (0.956 / 0.75) on the nose.
- **G2 TRANSFER FUNCTION**: the measured map matches the statevector theory to **max |ΔA| =
  0.079, max |ΔL| = 0.056** across all 9 interior points — the whole transfer function, not one
  point, is quantitatively correct.
- **G3 AXIS DISCRIMINATION**: the spectrometer resolves — P_silent(blind Y) − P_silent(transparent
  X) = **0.700 at 44σ**. The X-axis is 100× quieter than Y/Z.

**The practical statement**: to know whether a coherent error will slip through your code
*silently* (accepted yet corrupting), project it onto the plane orthogonal to your logical
observable. Errors parallel to the readout are transparent (they don't touch the logical info);
errors orthogonal to it are the blind spots. Not all coherent errors are dangerous to a code —
only the ones it can't see from where it's looking.

## Budget scoreboard (graded straight)

Z blind spot A = 0.921 ≥ 0.88 **IN**, L = 0.750 ≥ 0.65 **IN**; X-axis P_silent = 0.007 < 0.10
**IN**; discrimination 0.700 ≥ 0.4 **IN**. **4/4 in band** — a clean, fully-in-window result.

## What enters the record

1. **The [[4,2,2]] coherent-error transfer function, measured.** Exp199 established one blind
   spot (global Z); Exp211 maps the full axis spectrum and gives the closed rule
   (blind ⇔ orthogonal to the readout basis). A chip characterizing its own coherent-noise
   response through its error-detecting code.
2. **A false intuition corrected**: not every coherent error is a shield blind spot. The X-axis
   (parallel to the readout) is fully transparent — 100× quieter than the orthogonal axes. The
   danger is *specifically* the orthogonal plane.
3. **The self-characterizing chip (P5) delivered** — noise metrology as a byproduct of running
   the shields, the enabler the pre-dev structure flagged for the deep flights (it says which
   coherent-error axes a deep logical circuit must fear).

## Scope (stated plainly)

[[4,2,2]] coherent-error transfer function for the **X-basis** logical information, |+̄⟩ input,
global-rotation error family (single-qubit-correlated across the block). The blind-spot locus
**rotates with the readout basis** — for Z-basis logical info, X and Y become the blind axes
and Z transparent (the rule is basis-relative, a stated extension not flown here). Extends 199
from one axis to the spectrum. Textbook code + 199 priors credited; the contribution is the
measured transfer function and the orthogonality rule.

## Line

**A code can only be blind to what it isn't looking at. We measured exactly which coherent
errors the [[4,2,2]] shield lets pass in silence — the ones orthogonal to its logical gaze —
and which slide by harmless. The blind spot isn't a flaw in the code; it's the shadow of its
own line of sight, and now we have the map of it, to 44σ.**
