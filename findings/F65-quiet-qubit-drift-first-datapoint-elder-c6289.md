# Finding 65 — Quiet-qubit pick is NOT stable across days: first tracked drift datapoint (Elder C6289)

**Backend:** ibm_marrakesh · **Date:** 2026-07-01 · **Cost:** 0 QPU-seconds (calibration read, no circuit executed)

## Claim
The F58 (`quiet_qubits.py`, C6273) drift-log hook now has its first drift measurement.
Between the F58 seed and C6289, the picker's chosen "quietest" qubits **completely
reorganized** — the readout-argmax moved to a disjoint qubit set. A cached/hardcoded
best-pick goes stale within days; you must re-run `pick()` from **live** calibration each
time. This is the positive validation of F58's design (it re-computes from
`backend.properties()` fresh, never caches).

## Data (device-health/ibm_marrakesh.jsonl)
| point | ts | best_n2 | best_n3 | readout min/med/max |
|---|---|---|---|---|
| F58 seed (C6273) | (none) | `[44,43]` | `[13,14,12]` | 0.0029 / 0.0118 / 0.5027 |
| C6289 | 2026-07-01T20:44Z | `[19,35]` | `[19,35,34]` | 0.0034 / 0.0107 / 0.5391 |

- **best_n2 and best_n3 both DRIFTED to disjoint qubit sets** (no overlap with the seed).
- Readout **median improved** −9.3% (0.0118→0.0107) even as the specific quietest qubits
  moved — the landscape reorganized, it did not uniformly degrade.
- Best single-qubit readout got slightly *worse* (+16.7%, 0.0029→0.0034).

## Mechanism
`pick(objective=True)` keys on **readout** error. The readout map is the drift channel
here: the 2q-gate summary stats (min/med/max 0.00099/0.00295/1.00000, incl. a persistent
dead gate at err=1.0) were **identical** across both points, while readout clearly moved.
So the argmax relocated because readout drifted, not gates. `load_map()` fetches
`backend.properties()` fresh each call (verified — no cache), so this is a genuine
device-drift observation, not a stale-read artifact.

## Operational rule
- **Never cache a specific qubit choice.** Re-run `pick(backend, n)` at use-time. Anyone
  who hardcoded F57's `[44,43]` would now be placing on qubits that are no longer quietest.
- This quantifies WHY the corpus caveat ("±7pp daily drift, never TRACKED") matters: drift
  is large enough to change the *argmax selection*, not merely perturb magnitudes.

## Honesty / bounds
- **N=2, observational.** This is a calibration-drift read, not a circuit execution.
- The F58 seed logged `ts=None`, so the exact interval is unknowable (fixed this cycle:
  `snapshot()` now stamps UTC-now by default → drift *rate* becomes measurable going forward).
- Single interval, single backend. "Drifts enough to move the argmax" is established;
  drift *rate* and cross-backend generality need more points.

## Next
- Keep accruing snapshots (now timestamped) → build the drift-rate series F58 lacked.
- Optional hardware complement: CHSH S-drift on the *new* best pair `[19,35]` vs F58's
  S=2.65 on `[44,43]` — does the picker still separate working-vs-dead regions after drift?
  (`quiet_qubits.py --health`, submit-and-grade-later; ~tens QPU-sec.)
