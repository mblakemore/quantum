# CELL 11 — THE INERTIAL DAMPENER: pre-registration (frozen before flight)

*Whisper C5018. GO: Creator general#4300 "Fly Cell11!". Basis: the clock-or-coin census
(quantum@5201592) — drift on kingston's census drifters is a coherent epoch rotation
(q73: ~0.21°/layer, linear in depth, 50–90σ/row). Claim under test: a coherent rotation can
be measured and dialed out — the compensated epoch-pair agrees where the uncompensated pair
diverges. Scripts: `exp_cell11_inertial_dampener_whisper_c5018.py` (fit/fly),
`exp_cell11_decode_whisper_c5018.py` (fit-A/grade). Text frozen at commit; no bar moves
after data.*

## Design (measure-then-compensate — the dampener is feedback)

- **JOB A** (measure the clock): census rows, depths {160,280,400} × 3 bases, uncompensated,
  8k shots + in-job cal0/cal1. Decode → Bloch v_now(D) per drifter → fit fixed-axis,
  linear-in-depth rotation banked-epoch-1 → now (fitter validated on banked data, below).
- **JOB B** (dial it out): same session, same cal window (SAME-CAL GATE: aborts if
  `last_update_date` changed since Job A), both arms in one job — compensated rows (terminal
  inverse rotation per drifter, constants FROZEN from Job A's fit) + uncompensated controls.
- **Reference**: banked epoch-1 (job d9kq85…, 2026-07-29 06:56Z). The graded quantity is
  dθ(arm vs epoch-1) per drifter per depth, shot-noise σ propagated as in the census.

## Frozen verdict rule (three-state, per gated drifter {73, 26, 23} per depth)

- eligible: uncompensated dθ > 3σ (there is something to damp)
- **DAMPED**: eligible AND compensated dθ < 3σ
- **NOT-DAMPED**: eligible AND compensated dθ ≥ 3σ
- **UNDERPOWERED**: not eligible (nothing to damp at that depth; gates nothing)
- q53 (census-MIXED) flies **reported-not-gated** — its shrinkage component is exactly what
  a rotation cannot fix; it is the informative control, not a gate.
- Headline tally = gated rows only. Any NOT-DAMPED row is reported with its margin; the cell
  passes as a machine iff **q73 is DAMPED at every eligible depth** (primary), with q26/q23
  rows carried as secondary evidence either way.

## Model class (pre-registered) and its honest edges

Epoch shift ≡ fixed-axis rotation, linear in depth, acting on the final single-qubit state.
$0 self-test on banked epochs 1→2 (`cell11_banked_fit_c5018.json`): fitter recovers
**q73: rate −0.217°/layer, axis ≈ X̂ ([0.998, −0.02, −0.06]), rms 0.040** — matching the
census's 0.21°/layer independently. Edges: (i) the fit is per-drifter and per-epoch-pair;
Job A refits at flight epoch rather than extrapolating the banked constants across 5 days and
multiple recals — rate stability across epochs is the CHRONOMETER's question, deliberately
not assumed here. (ii) Axis is X-like, so compensation legitimately moves all three bases
(the naive "Z rows must not change" check does not apply; dropped from the design, on the
record). (iii) If Job A's fit is degenerate (rms > 0.15 or |rate| < 3× its depth-scatter),
the affected drifter is flown uncompensated and reported UNFITTABLE — a fit that cannot fail
would be a control that cannot fail.

## Cost and account

Two jobs, ~11 + ~20 pubs × 8k shots, ibm_kingston via IBMQ_ALT (pool 270 s at design time;
ALT2 371 s as fallback). Preflight account check run on the flight script before submit.

*— Whisper C5018, stamped claude-fable-5. Bars frozen at this commit.*
