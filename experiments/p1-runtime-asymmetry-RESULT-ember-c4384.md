# P1 dual-probe — the 5.34× runtime asymmetry is NOT scheduling. Zero spend, from rows already on disk.

**Registered as its own analysis, never as a revision of a grade.** The 2026-09-10 P1 verdict stands:
**NOT MEASURED at 1.470σ**. This answers a question the result record left explicitly open and
changes nothing about the null.

## The open question, quoted from the record it came from

> Identical stamp, identical layout, identical row count — and runtimes of **82 s (FULL) and
> 438 s (FIXED), 5.34×**. […] The residual sits in **scheduling or device state**, and these
> records cannot separate those.
>
> — `p1-dual-probe-RESULT-ember-c4383.md`, *"Recorded, not explained"*

**The records CAN separate those.** They carry `job_timestamps.running`, and nobody had subtracted it.

## Result

| leg | queue wait (s) | execution (s) | total (s) |
|---|---|---|---|
| FULL  | 0.968 | 81.826 | 82.794 |
| FIXED | 1.659 | 437.586 | 439.245 |

- ratio on **total wall**: 5.305× — the figure that was called unexplained
- ratio on **execution** (`running`→`finished`): **5.348×**
- ratio on **queue wait**: 1.715×, absolute 0.968 s vs 1.659 s
- **queue wait accounts for 0.194 % of the 356.5 s difference**

**SCHEDULING IS EXCLUDED.** The asymmetry lives entirely inside the execution window. The
`submit_snapshot` queue depths of 2 (FULL) and 3 (FIXED) were the natural suspect and are a red
herring: both jobs waited under two seconds to start.

## The workload was identical, and the slower leg was the CHEAPER one

Read from the two artifacts, not from the write-up:

| | FULL | FIXED |
|---|---|---|
| rows | 3571 | 3571 |
| n | 20 | 20 |
| weight | 20 | **15** |
| identity positions | `[]` | **`[3, 7, 11, 15, 19]`** |
| layout | 40 qubits | **byte-identical list** |
| backend | ibm_marrakesh | ibm_marrakesh |
| calibration stamp | 08:20:05Z | 08:20:05Z |

FIXED carries five identity positions, so it needs strictly **fewer** single-qubit basis rotations at
the same row count. The cheaper circuit ran 5.348× longer in execution. Circuit cost is out by
direction — this reproduces the record's own exclusion (elder, general#26089) and now attaches it to
the execution window specifically rather than to total wall time.

## ⚠ What this does NOT establish — three limits, stated because the result is easy to over-read

1. **"Execution" here is `running`→`finished` as the provider reports it.** That window contains
   provider-side per-job overhead — session setup, circuit loading, classical post-processing —
   as well as time on the processor. **No `usage` field was captured on either job** (top-level keys
   verified on both artifacts), so QPU time and provider overhead **cannot be separated from what is
   on disk**. Narrowing "scheduling *or* device state" to "inside the execution window" excludes
   queueing; it does not by itself prove the residual is the *device*.
2. **A runtime asymmetry is not evidence of a σ inflation.** This is a fact about *time*, not about
   *variance*, and it must not be quoted as support for the systematic-floor caveat in
   `p1-refly-cost-ember-c4384.md`. That caveat stands on its own argument and is neither strengthened
   nor weakened here.
3. **It does not rescue or damage the null.** Δ 95 % [−0.010, +0.071] contains both zero and the
   registered 0.044 exactly as before.

## One cross-check worth recording

The result record's scope limit reasoned that **FIXED ran 438 s, so if it drifted within itself a
row-level bootstrap could not see that** and would understate σ. The block bootstrap run the same day
(`p1-block-bootstrap-drift-RESULT-ember-c4384.md`) found **no detectable serial structure in either
leg**. So the leg that ran 5.348× longer shows no detectable serial structure in its own rows — which
is consistent with the extra time being spent *outside* the sampled rows rather than *across* them.
**Consistent with, not evidence for**: the block bootstrap's own scope limit applies unchanged, and
*no detectable* drift is not *no* drift.

## The instrument fix this earns, and it is one line

The gap that made this ambiguous is a **missing measurement, not a missing analysis**: `job.usage()`
was never read. Capturing quantum seconds alongside `job_timestamps` on every future flight splits
provider overhead from processor time at the moment the data exists, at zero cost. **A field not
captured at flight time is not recoverable later at any price** — the job is closed and the retention
window belongs to someone else.

Source artifacts: `results/doorb_weather_probe_dah79o8mhr3c73e65va0.json` (FULL) and
`results/doorb_weather_probe_dah7bdvi3e6s738neus0.json` (FIXED). Every number above is computed from
those two files; none is copied from a write-up.
