# Cell 11 — The Inertial Dampener: LARGE PARTIAL compensation, frozen rule NOT MET

*Whisper C5018, 2026-08-05. Creator GO general#4300 "Fly Cell11!". Jobs
`d9ofd15oh1qc73bbs3a0` (A, measure) + `d9pkk6u28h6s739rfdgg` (B, compensate), ibm_kingston.
Prereg frozen pre-flight: `docs/cell11-inertial-dampener-prereg-whisper-c5018.md`. Grade
artifact: `results/cell11_grade_d9pkk6u28h6s739rfdgg.json`.*

## Verdict by the frozen rule — stated first, because it is the one that binds

**DAMPED 3 · NOT-DAMPED 6 · UNDERPOWERED 0** across the nine gated rows.

The frozen criterion was *full restoration within noise*: DAMPED iff the compensated
divergence from banked epoch-1 is **< 3σ**. Six of nine gated rows leave a residual above
that bar. **The dampener does NOT restore epoch-1's Bloch vectors to within noise at most
depths.** No re-reading of the bar: 3σ was written before the flight and it is 3σ now.

## The measured effect — reported, not gated

At **every depth of every drifter**, compensation removed the great majority of the drift:

| qubit | depth | uncompensated dθ | compensated dθ | removed | frozen verdict |
|---|---|---|---|---|---|
| q26 | 160 | 26.33 ± 0.98° | 8.61 ± 0.97° | 67% | NOT-DAMPED |
| q26 | 280 | 59.90 ± 1.05° | **1.11 ± 1.07°** | **98%** | DAMPED |
| q26 | 400 | 89.56 ± 1.19° | 5.20 ± 1.18° | 94% | NOT-DAMPED |
| q23 | 160 | 20.26 ± 0.77° | 6.85 ± 0.76° | 66% | NOT-DAMPED |
| q23 | 280 | 46.60 ± 0.93° | **2.32 ± 0.90°** | **95%** | DAMPED |
| q23 | 400 | 75.30 ± 1.13° | 5.74 ± 1.11° | 92% | NOT-DAMPED |
| q73 | 160 | 10.50 ± 0.93° | 3.99 ± 0.93° | 62% | NOT-DAMPED |
| q73 | 280 | 15.75 ± 1.01° | **2.37 ± 1.01°** | **85%** | DAMPED |
| q73 | 400 | 27.05 ± 1.12° | 5.92 ± 1.11° | 78% | NOT-DAMPED |
| q53* | 160 | 1.64 ± 1.04° | 3.02 ± 1.04° | — | UNDERPOWERED |
| q53* | 280 | 6.96 ± 1.29° | 1.49 ± 1.29° | 79% | DAMPED |
| q53* | 400 | 9.91 ± 1.67° | 6.43 ± 1.68° | 35% | NOT-DAMPED |

\* q53 = the census-MIXED drifter, flown **reported-not-gated** by design (its shrinkage
component is what a rotation cannot fix).

A 94% removal of an 89.56° divergence leaves 5.20°, which fails a bar demanding < 3.5°. **The
frozen criterion asks whether the residual is consistent with ZERO, and that is a strictly
harder question than whether the compensation works.** Both answers are in this table and
neither is allowed to hide the other.

## Why the residual survives, and it is diagnostic rather than noise

**The verdict pattern is depth-ordered: DAMPED at d280 on every single qubit, NOT-DAMPED at
d160 and d400 on every single qubit.** That is not scatter. The fit minimizes residual across
all three depths simultaneously, so a model with the wrong *depth-dependence* fits best in the
middle and leaves signed residuals at both ends — exactly what is observed, on four qubits
independently.

**Conclusion: the epoch rotation is NOT exactly linear in depth over a seven-day,
multi-recalibration interval.** The census measured linearity across ~12 hours (constant
°/layer, 50–90σ/row). Cell 11 stretched the same model across 7 days and several recals and
the linear term still removes 62–98% of the effect — but a residual curvature term is now
resolvable, and it is what the frozen bar is catching.

## Pre-stated caveats that held (all posted before the grade, general#4801)

- **The reference interval is 7 days, not the 12 hours the model was validated on.** Flagged
  before grading; it is the leading explanation for the residual.
- **The clock moved qubits.** The ~0.22°/layer X-axis rotation was q73's across the banked
  12h pair and is **q26's** across this 7-day pair (q26 −0.219°/layer, axis ≈ X̂). The
  *phenomenon* is stable; its *host qubit* is not — consistent with the census's own
  epoch-volatility finding, now observed on the rotation rate itself.
- **Fit residual degraded 0.040 → 0.065 rms** across the longer interval, pre-flagged as the
  expected signature if the model class were being over-stretched. It was.

## Machinery notes (both earned their keep on first use)

- **The execution-window gate fired on a real event.** Kingston recalibrated *while Job A sat
  in an 18-hour queue* (submit-cal Aug-3 19:03 → landing-cal Aug-5 13:39). A submission-time
  comparison would have frozen compensation constants against a calibration the job never ran
  under. The gate — added because the long queue prompted asking what "same cal window" means
  for a job that waits overnight — caught it, and the fit used the landing cal.
- **A rounding artifact was caught by a library tolerance, not by review.** The stored
  rotation axis is rounded to 4 decimals and is therefore not exactly unitary; qiskit's
  `UnitaryGate` refused it. Fixed by renormalizing at construction. A looser library would
  have flown a slightly non-unitary "compensation" silently.

## What this buys, and what it does not

**Buys:** the first demonstration that this machine's coherent epoch drift is *engineering-
addressable* — a measured rotation, dialed out, removing up to 98% of a divergence that was
50–90σ from zero. And a sharper model: linear-in-depth is right locally and incomplete across
a week.

**Does not buy:** the Inertial Dampener as a certified machine. The frozen rule was full
restoration within noise and it was not met at 6 of 9 rows. The claim that survives is
**large partial compensation with a resolvable residual curvature**, which is a weaker and
truer statement than the one the cell was named for.

**The cheap next rung** (named, not claimed): re-fly with the reference arm at a *recent*
epoch rather than 7 days back — Job A measures, Job B compensates, both inside one
calibration window against a same-day reference. If the residual collapses under a short
interval, the curvature is an interval effect and the linear model is exact within an epoch;
if it survives, the depth-dependence is genuinely non-linear and the model needs a second
term. Either outcome is a real result, and the apparatus for both already exists.

*— Whisper C5018, stamped claude-fable-5. Negatives and partials kept with full accounting.*
