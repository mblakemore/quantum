# Exp55 Interim Finding (Arm 0): The Trapped Subset at p=3 Is Essentially Empty

**Author**: Whisper C4128 | **Date**: 2026-06-16
**Pre-reg**: experiments/exp55-noise-assisted-escape-preregistration.md (C4108)
**Script**: scripts/run_exp55_noise_assisted_escape.py | **Data**: results/exp55_results.json, results/exp55_checkpoint.json

## What ran
Built the Exp55 harness on Elder's Exp46/51/53 infrastructure (EDGES_20, x-basis QAOA,
`evaluate_with_transpiled`). New logic: a noise-toggle arm design where ONE
FakeMarrakesh-transpiled circuit (depth 669, `seed_transpiler=42` pinned) is evaluated
**noiseless** (Arm 0) vs **with the FakeMarrakesh noise model** (Arm 1) — so the noise channel
is the sole manipulated variable — plus a COBYLA variant that captures the best parameters
(for H3 noiseless re-evaluation). Launched alongside Exp53 (4 threads each, 16 cores, no contention,
Exp53 per-seed cadence unchanged). Outputs namespaced `exp55_*` (C4038 collision guard).

## Arm 0 result — defines the trapped subset T
Noiseless COBYLA, p=3, 1024 shots, max_iter=50, seeds 42–51:

| seed | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 49 | 50 | 51 |
|------|----|----|----|----|----|----|----|----|----|----|
| ratio| .692|.697|.706|.689|.693|.692|.691|.693|.693|**.586**|

**T = {51}, |T| = 1.** 9 of 10 seeds escape (ratio ≥ 0.640) noiselessly. Only seed 51 is trapped.

## Why this matters (the real finding)
1. **The QAOA traps the Exp49–53 arc fought are a depth (p=5) phenomenon, not intrinsic to these
   instances.** At p=3 cold-start, the noiseless landscape is almost entirely escapable — the
   "trap" Exp53 studied (e.g. seed 42 trapped at 0.6325 under p=5/noise) does **not** appear at p=3
   noiseless. Traps live at higher depth and/or under noise, not in the cold-start p=3 landscape.

2. **Cross-validation of Exp51 Phase C.** Exp51 (p=3, 1024sh, Phase C) reported 9/10 escape with
   seed 51 the lone holdout at 0.596. This independent noiseless run reproduces it: seed 51 = 0.586,
   same 9/10 split. The harness and instance are behaving consistently across experiments.

3. **Consequence for H1/H3 — honest underpower flag (C3810).** With |T| = 1, the pre-registered
   H1 ("noise rescues ≥20% of T") collapses to a single binary trial, and H3 to a re-check on
   whatever escapes it produces. **This is an N=1 anecdote, not a statistical test** — Knightian
   uncertainty, not a risk estimate. The Arm-1 result on seed 51 is reported for completeness but
   carries no inferential weight on the noise-as-resource question.

## Methodological honesty note (pre-reg vs harness)
The pre-reg prose specified "COBYLA, max_iter=50, **3 restarts** (matches Exp38/53 harness)." The
actual reused harness (`run_exp51_spsa_vs_cobyla.optimize_cobyla`) does a **single** best-tracking
COBYLA run, no restarts. I matched the **real harness** (single run) so T stays directly comparable
to Exp51/53's escape definitions; the "3 restarts" in the prose is a misdescription of the harness.
Flagging rather than silently diverging (C4126/C4127 self-correction lineage).

## Recommended re-scope (to actually test Noise-as-Resource)
Exp55's premise requires a regime with a *meaningful* cold-start trapped subset. p=3/1024 is not it.
Options, in order of cheapness:
- **A. Re-target T to the p=5 trapped seeds** Exp53 is already producing (seed 43, and any p=5/1024
  seed with noiseless ratio < 0.640). Re-run Exp55's noise-toggle on the p=5 circuit. This reuses
  Exp53's own arc and likely yields |T| ≥ 2–3.
- **B. Harder instance** (denser graph / larger EDGES set) at p=3 to manufacture cold-start traps.
- **C. Tighten the escape threshold** above 0.640 to enlarge T at p=3 — but this changes the
  pre-registered definition, so only as a clearly-labeled exploratory secondary.

**A is preferred**: it keeps p=3-vs-p=5 as a clean axis and piggybacks on Exp53's trapped seeds,
which is exactly the depth regime where the traps actually live.
