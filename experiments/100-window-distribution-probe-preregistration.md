# Exp100 pre-registration — Calibration-window distribution probes (time-since-calibration hypothesis)

**Author:** Elder (DC 1.5), C6378 (2026-07-04) — Creator-directed follow-up to F81
**Script:** `scripts/run_exp100_window_distribution_probe.py`
**Backend:** `ibm_marrakesh`, qubits pinned [54,53,55] (QQQ) / [0] (IWM) — F78/F81's controlled triple
**Cost:** ~5–6 quantum-seconds per probe (4 PUBs × 4096 shots); target 8–15 probes over ~1–3 weeks

## Motivation (what F81 + the calibration forensics left open)

F81: identical deep circuits, identical qubits, 11h apart → blind-MLE err 0.154 → 0.0003.
Forensics addendum: published calibration (CZ/readout/T1/T2) was flat across the two windows
(predicted 3% k5-contrast difference; observed 3×) — **published data cannot pick the window**.
The one residual observable that differed: **time since the last calibration update**
(good window ran 38 min after a fresh calibration; bad window 79 min after).
N=1 each. This experiment accumulates the distribution.

## Probe design (fixed, all probes identical)

PUBs: `QQQ_k0` (7 2q), `QQQ_k3` (~76 2q), `QQQ_k5` (124 2q), `IWM_k0` (0 2q, sentinel control).
Layout pinned via `initial_layout` to hold the F78/F81 controlled variable. 4096 shots.

**Window-quality metric:** `R5 = |P_meas(k5) − 0.5| / |P_ideal(k5) − 0.5|`, clipped [0, 1.3];
if the measured deviation has the wrong SIGN, R5 := 0. Classes: **GOOD ≥ 0.8**, **BAD ≤ 0.5**, else MID.
Anchors (includable rows, same circuits/qubits/backend): Exp98 R5 = 0.99 (tsc 38 min, GOOD),
Exp95 R5 = 0.33 (tsc 79 min, BAD).

## Pre-registered hypotheses & gates (pinned BEFORE first probe submission)

- **H-TSC (primary):** window quality declines with time since calibration.
  **Grade at N ≥ 8 usable rows AND tsc spread ≥ 180 min:** one-sided Spearman
  ρ(tsc_minutes, R5) with 20k-permutation p.
  **SUPPORTED:** ρ ≤ −0.5 AND p < 0.05. **Otherwise NULL** (no salami-slicing:
  if the gate misses, the verdict is NULL regardless of how suggestive the scatter looks).
- **H-BASE (secondary, estimation not test):** good-window base rate = fraction GOOD.
  Decision use: ≥ ~40% GOOD → "wait-for-green sentinel" is a practical protocol;
  ≤ ~10% → deep-loader QAE is effectively unusable on demand regardless of sentinel.
- **H-SENT (control):** IWM sentinel err stays < 0.05 in ALL windows (shallow-stays-clean,
  3rd+ replication). Any violation is reportable — it would break the sentinel logic itself.

## Honesty rules

- The two F78/F81 anchor rows are declared HERE, before data: they enter the scatter
  as rows 1–2. They are the *reason* for the hypothesis, so the H-TSC grade must ALSO be
  reported excluding them (sensitivity line) — if SUPPORTED only *with* anchors, say so plainly.
- Queue timing is uncontrolled → tsc values are observational, not assigned. This is a
  correlation study; a SUPPORTED verdict motivates (not proves) a scheduling rule.
- Small-N discipline (C5923/C6338 family): report SIGN + scatter, no headline extrapolation
  before the pre-registered N gate.
- Probes are cheap but not free (~6 q-sec each; open-plan budget 600 q-sec / 28 days shared
  across all DC quantum work). Cap: ≤ 15 probes total for this experiment without re-registration.

## Grading artifacts

Rows append to `results/exp100_window_probes.jsonl` (one JSON per probe: per-PUB P, R5,
window class, executed_utc, calibration_last_update, tsc_minutes, quantum_seconds).
`--analyze` prints the scatter, base rate, and the H-TSC grade when the gate is reachable.
Finding number reserved: **F82** on grade.

## Amendment A1 (C6378, same cycle, BEFORE any probe results — circuit-identity note)

First submission (`d94k7jkql68s73c9l3og`) revealed that pinning `initial_layout=[54,53,55]`
reproduces the anchor jobs' *qubits* but not their exact *routing*: probe circuits carry
**10 / 82 / 130** 2q gates (k0/k3/k5) vs the anchors' 7 / 76 / 124 (VF2-chosen initial layout
with end-of-circuit permutation absorbed). Probes are ~5% deeper than anchors at k5.

Ruling (pinned now): probes stay pinned-layout — probe↔probe identity across windows is the
primary controlled variable for H-TSC. Anchor rows are retained but are *slightly milder*
circuits; the mandatory with/without-anchors sensitivity line covers this. R5 thresholds unchanged.
