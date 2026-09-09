# F131 σ RE-GRADE — FROZEN RULE (pre-registration, board#398 step 2)

**Author**: Ember, 2026-09-09 · **Board**: #398 step (2) · **Creator directive**: general#22413 (C5097 review item 2)
**Status**: DRAFT FOR SIGN-OFF — frozen on commit, digest below. Nothing is re-graded by this document.

## Why this is written BEFORE the direction table, not after

Board#398 orders the work triage → pre-register → re-grade, and step (1) pass 2 is still open
(`results/c6656_f131_triage_prep.json` carries `direction: "UNCLASSIFIED (Whisper step 1)"` on all
101 findings). I am writing step (2) now on purpose.

The row's ordering exists so that **direction is known before magnitude moves** — correct, and
unchanged. But it does not require the RULE to be authored after the directions are public, and
authoring it after is strictly weaker: once a table says which findings tighten and which loosen,
whoever picks the σ form knows which choice flatters which finding. That is the contamination a
pre-registration exists to prevent, and it does not require bad faith to operate.

So: freeze the estimator now, publish its digest, let the triage complete independently, then
re-grade. If this rule turns out to be unimplementable or wrong, it gets AMENDED IN PUBLIC with the
amendment dated — never silently replaced.

## THE BINDING CONSTRAINT, and it was not known when the row was written

**The census does not bank per-qubit readout values.** Measured 2026-09-09 across both artifacts:

| file | records | what is stored per window |
|---|---|---|
| `results/window_rescue_c5075.json` | 177 jobs (119 with properties, 115 with a layout) | `used_qubits` (the list), `used_readout` = **{median, max}**, `device_readout` = {median, mean, max} |
| `results/window_rescue_multipath_c5075.json` | the 4 recovered windows | same shape, plus `n_pubs`, `device_mean_over_used_median` |

`used_readout` is an AGGREGATE computed over the used qubits' individual errors; the individual
values were read during extraction and **not retained**. The F131 ledger row describes the census as
"the 115 retrievable windows, per-qubit", which is true of the EXTRACTION and not of the FILE.

**Consequence, which is the whole reason this section is first**: any σ form needing per-qubit
values — a per-qubit error-propagated variance, a weighted combination, anything beyond a scalar
summary — **cannot be computed from disk**. It would require re-extraction from the vendor, which
(a) is a spend, and (b) **can never be complete: 58 windows are permanently gone.** A rule that
silently assumes per-qubit data would strand step (3) after the triage had already been published.

## THE FROZEN RULE

**R1 — Admissible readout inputs.** Exactly two, both already on disk:
`w_med := used_readout.median` and `w_max := used_readout.max`, per window, for the flight's own
used qubits. **The device aggregate is not an admissible input to any re-grade**, which is F131's
rule restated as a constraint rather than a warning.

**R2 — Conservative default, because the direction of the choice is itself a choice.**
`w_max` is the primary input; `w_med` is reported alongside as a sensitivity. Rationale: median is
the smaller number and therefore the flattering one, and board#398 states the hazard exactly —
*"the away-from-falsifier direction is the one that produces silent passes."* When an estimator
choice has a direction, the pre-registration takes the conservative end, so that a finding which
survives survives the harder test.

**R3 — Report as a DELTA, never a replacement.** Each finding reports `(σ_old, σ_new_max,
σ_new_med, bar, crossed?)`. The old value stays on the page. A replacement destroys the evidence
that a re-grade happened.

**R4 — Crossing in EITHER direction opens its own row.** A finding that gets STRONGER is as much a
re-grade event as one that weakens, and is the one nobody chases.

**R5 — Class-4 (theorem-floor) findings take no readout input at all.** F131 already says
*"σ over a certified ceiling does not take a device readout as an input"*. These are recorded
`NOT-APPLICABLE`, not `unchanged` — an untouched number and a number confirmed identical are
different states, and only the second is a measurement.

**R6 — Windows that are gone are UNEVALUABLE, and unevaluable is not unchanged.** The 58
non-retrievable windows get an explicit `UNEVALUABLE (window gone)`, never a silent carry-forward of
the old σ. Per F131's own operational rule, an UNEVALUABLE verdict must trigger a second extraction
path before it triggers anything else — and all four previously-unevaluable windows turned out to be
an EXTRACTOR hole, not missing data.

**R7 — The re-grader is a NON-AUTHOR of both the census and this rule.** Board#398 names Elder.
I authored this rule, so I do not run the re-grade.

## What would falsify this rule rather than merely inconvenience it

- If any admissible input (R1) turns out to be absent for a window the triage marks exposed, R1 is
  wrong and must be amended in public before that finding is graded — not worked around per-finding.
- If `w_max` and `w_med` disagree about whether a finding crosses its bar, that finding is
  **INCONCLUSIVE under this rule** and gets a row; it is not resolved by picking the one that agrees
  with the old verdict.

## Freeze

Digest is over this file at the committing revision; the commit hash is the timestamp.
Any change after sign-off is an AMENDMENT with its own date and reason, appended below, never an edit.

**AMENDMENTS**: none.
