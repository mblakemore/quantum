# Cell 11 RUNG 2 — the depth-dependence test: pre-registration (frozen before flight)

*Whisper C5018, on Creator "Run Cell 11's next rung". Basis: Cell 11's graded result
(`findings/cell11-inertial-dampener-partial-whisper-c5018.md`) — frozen rule NOT MET
(3 DAMPED / 6 NOT-DAMPED), 62–98% of drift removed, and a **depth-ordered residual**
(DAMPED at mid-depth on all four qubits, NOT-DAMPED at both extremes on all four) pointing at
a wrong depth-dependence rather than at noise.*

## What the $0 pre-test found, and why it redesigned this rung

Before proposing any spend, the curvature hypothesis was tested on data already in hand
(Job A `d9ofd15oh1qc73bbs3a0`, no new QPU):

| qubit | linear rms | quadratic rms | fitted curvature | hold-out (fit d160+d400 → predict d280) |
|---|---|---|---|---|
| q26 | 0.0630 | 0.0243 | −0.226 | **3.24°** (~3σ) |
| q23 | 0.0640 | 0.0376 | −0.172 | 0.94° (within noise) |
| q53 | 0.0238 | 0.0224 | −0.048 | 3.04° (~3σ, but weak-rotation qubit) |
| q73 | 0.0654 | 0.0645 | +0.044 | 0.69° (within noise) |

**Verdict: CANNOT SEPARATE, and the reason is structural.** Cell 11 flew **3 depths**, and a
2-parameter angle model (rate + curvature) fit to 3 depth points is *exactly determined* — the
rms improvement on q23/q26 is not distinguishable from over-fitting. The hold-out test is the
honest one and it splits 2–2. **The blocker is not the interval, it is the number of depth
points**, and no re-fly at any interval fixes that if it carries 3 depths again.

**So this rung changes the depth sampling, not the interval.** The interval question
(7-day vs same-day reference) is real and stays named as rung 3 — it cannot be answered while
the depth-dependence is unresolved, because a residual attributed to interval could equally be
curvature.

## Design

- **Job A2 (measure)**: uncompensated census rows at the **five banked depths**
  {160, 280, 320, 360, 400} × 3 bases + in-job cal. Five depth points against the banked
  epoch-1 reference (which carries all five) — the angle model becomes **over-determined by 3**
  instead of exactly determined.
- **Job B2 (compensate)**: same rows, both arms, compensation constants **frozen from A2's
  fit**, applied with whichever model the pre-registered selection rule picks (below).
- Same-cal / execution-window gate as Cell 11: A2's landing cal is the reference, B2 aborts if
  the chip recalibrates between executions, grade re-checks post-hoc.

## Pre-registered model-selection rule (frozen BEFORE A2 lands)

Fit both models to A2's five depths. Adopt the quadratic **only if**:

> **quadratic rms < 0.7 × linear rms** AND **the fitted curvature exceeds 3× its own
> jackknife scatter** (leave-one-depth-out refits, scatter = sd of the five curvature
> estimates).

Otherwise compensation uses the **linear** model. The rule is written before the data exists
precisely because "the quadratic fits better" is guaranteed by parameter count and must not be
the criterion.

## Frozen verdict rule (three-state, unchanged in form from Cell 11)

Per gated drifter {73, 26, 23} per depth, vs banked epoch-1:
- eligible: uncompensated dθ > 3σ
- **DAMPED**: eligible AND compensated dθ < 3σ
- **NOT-DAMPED**: eligible AND compensated dθ ≥ 3σ
- **UNDERPOWERED**: not eligible
- q53 reported-not-gated (census-MIXED control).

**The headline claim this rung can earn, stated in advance so it cannot inflate:** if the
selection rule adopts the quadratic AND the DAMPED count rises materially over Cell 11's 3/9,
the finding is *"the epoch rotation carries a resolvable curvature term, and compensating it
restores epoch-1 within noise where the linear model could not."* If the rule keeps the linear
model, or adopts the quadratic and the DAMPED count does **not** rise, the finding is
*"3-depth curvature was over-fitting; the residual is not a depth-dependence effect"* — which
sends the question to rung 3 (the interval) with the depth explanation eliminated. **Both
outcomes are informative and both are cheap.**

## Cost

Two jobs on kingston (queue observed at 1 pending, ALT pool 196 s at design time, re-read at
submission). ~5 depths × 3 bases × 2 jobs + cal ≈ a few QPU-seconds.

*— Whisper C5018, stamped claude-fable-5. Bars frozen at this commit.*
