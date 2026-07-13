# Friction Report 02 — Published T1 Systematically Underestimates Live T1 (queue-length-independent)

**Status: DRAFT, NOT FILED** (Creator approval required to file). Target: IBM Quantum
calibration/properties data. Prepared by Whisper (DC15W) C4595 from the Exp108b/Exp108c runs;
mechanism section of finding F88.

## Summary

On `ibm_marrakesh` qubits 6 and 8, the T1 values served in backend properties underestimated
the T1 actually governing on-device decay by **+38% to +69%, on 2 of 2 runs**, and the bias is
**not explained by queue latency** (one run waited ~19 h, the other minutes — same direction,
same magnitude class). Any experiment that bakes absolute durations calibrated against
published T1 (delay-based state preparation, dynamical-decoupling spacing, T1-referenced
schedules) inherits a large systematic.

## Data

Back-computed T1 = delay / ln(1/p_measured), from thermalization-prep circuits whose measured
excited population directly encodes the decay actually experienced:

| Run | Job | Queue wait | Qubit | Published T1 (submit) | Back-computed T1 (execution) | Ratio |
|---|---|---|---|---|---|---|
| Exp108b | `d998ch0tcv6s73dmvqr0` | ~19 h | q6 | 201 µs | ~277 µs | 1.38 |
| Exp108b | 〃 | 〃 | q8 | 155 µs | ~246 µs | 1.59 |
| Exp108c | `d99qjmt2su3c739kq9n0` | short (same day) | q6 | 166 µs | ~281 µs¹ | ~1.69 |
| Exp108c | 〃 | 〃 | q8 | 112 µs | ~188 µs¹ | ~1.68 |

¹ From measured reservoir populations p̂_A = 0.4415, p̂_B = 0.4388 at delays 231/155 µs.
Full grade records: `results/exp108b_grade.json`, `results/exp108c_grade.json`; preregs in
`experiments/`.

## Anticipated objection, answered

*"T1 fluctuates; a snapshot is always stale."* Fluctuation predicts a symmetric, roughly
zero-mean error. We observe a one-signed bias (+38–69%, 4/4 qubit-runs), stable across a
1000× difference in queue latency and across two calibration snapshots taken a day apart.
That is consistent with a systematic in how the published value is measured or aggregated
relative to idle-decay conditions in a running job (e.g., measurement conditions, spectator
activity, or aggregation window), not with staleness noise.

## Why it matters to users

Delay-based protocols compute durations as d = T1·ln(1/p_target). A +50% T1 bias turns a
p = 0.25 target into p ≈ 0.40 — enough to break pre-registered acceptance bands (it produced
a NO-TEST for us before we re-sized gates around the measured bias). Users cannot correct for
a bias they are not told about; they can easily correct for a documented one.

## What we ask

Either (a) documentation of the conditions under which published T1 applies (and the expected
in-job deviation), or (b) an in-job T1 estimate exposed via the properties API, or minimally
(c) confirmation of whether this bias class is known for Heron-class devices.

## Environment / Reproduction

`qiskit 2.4.1`, `qiskit-ibm-runtime 0.47.0`, `ibm_marrakesh` (Heron r2), 2026-07-11/12.
Reproduce: X + calibrated delay + measure (the Exp108b/c calib arms); compare measured
population to the published-T1 prediction. Circuits: `experiments/exp108b_native_thermal.py`
(calib arms).

## Addendum (C4610): the bias is larger and more variable than first measured

Exp116 (job `d9a5e0af47jc73a9q540`, delays already corrected by ×1.65): back-computed
r = T1_live/T1_published reached **2.15 (q6) and 1.85 (q8)** — the observed sample is now
{1.38, 1.59, ~1.68, ~1.69, 1.85, 2.15} across 3 jobs / 2 qubits / 3 days, trending upward.
A fixed correction factor cannot hit a ±15% target window under this variance; any
delay-calibrated protocol needs either an in-job T1 estimate (the ask) or a pre-registered
delay LADDER with calib-arm-based rung selection (our Exp116b workaround). This run's
premise gate (baths must be passive at 5σ) caught the miss and NO-TESTed a +23σ pseudo-win —
the cost of the missing calibration data is now a wasted flight, documented.

Exp116b (C4612): bias r≈1.82 this run (r1 rung assumed 1.5 landed baths at 0.52). Sample now 7 values, 1.38–2.15. The delay-ladder workaround VALIDATED (rung-2 landed on target; experiment certified through the bias).
