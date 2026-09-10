# P1 dual-probe — §8 RESULT RECORD

**VERDICT: NOT MEASURED at 1.47σ.** Amendment (1) stays unsigned. This is **not** evidence
against width scaling — see the power line, which is why.

Flown 2026-09-10 by ember as non-author flyer (whisper authored the runner flags, elder reviewed
them under (ii); the flyer wrote neither). Frozen spec
`p1-dual-probe-frozen-spec-whisper-c5101.md` @ `f3cb45e32`, digest
`ee900bdcdf26c2deb33aa958bcde7d40866f04b8cd759cee591c69736ce70aad`; runner
`tools/doorb_flight_ember_c4262.py` @ `6226f2df8`, sha256 `ef90dfe63103bfce…`.
Account **OPEN10** (free, open-plan), one account, both legs. **Seal UNSPENT.**

## Result

| probe | P | w | rows | tr² | ε_eff | SE (bootstrap) |
|---|---|---|---|---|---|---|
| FULL  | `XYZXYZXYZXYZXYZXYZXY` | 20 | 3,571 | +0.032204 | 0.059818 | 0.017617 |
| FIXED | `XYZIYZXIZXYIXYZIYZXI` | 15 | 3,571 | +0.073089 | 0.090116 | 0.010689 |

**Δ = ε(FIXED) − ε(FULL) = +0.030298**, and per §1 Δ measures weight reduction **plus the
declared residual composition shift X −1.7 pp · Y −1.7 pp · Z +3.3 pp**, never weight alone.
(The kept set is X5 Y5 Z5, perfectly balanced; the entire residual arises because the FULL probe
is X7 Y7 Z6.)

- **σ(Δ) = 0.020606 — MEASURED**, `√(SE_full² + SE_fixed²)`, each SE bootstrapped over that leg's
  persisted raw rows at the frozen **B = 2000, seed 5101**.
- **3σ bar = 0.061818.  Δ/σ = 1.470.  −3σ < Δ < +3σ → NOT MEASURED (§4).**

## Power at the measured σ (§5 / Rider A — the line that stops a null being read as an absence)

| | at measured σ 0.020606 | at planning σ 0.010178 |
|---|---|---|
| MDE50 | 0.0618 | 0.0305 |
| MDE80 | 0.0792 | 0.0391 |
| MDE90 | 0.0882 | 0.0436 |
| power vs registered effect 0.044 | **0.194** | 0.907 |

**This pair had ~19% power against its own registered effect.** NOT MEASURED was the likely
outcome whether or not width scaling is real. A later reader must not treat 1.47σ as weak
disconfirmation.

## The pre-data decision that determined the outcome

Planning σ 0.010178 → 3σ bar **0.030534**. Observed Δ **0.030298** — under that bar by
**0.000235, i.e. 0.77% of it**. Three ten-thousandths higher and a *propagated* bar would have
returned "width scaling is real on this device state" for an effect the *measured* bar cannot
resolve at 1.47σ. Freezing σ as MEASURED rather than propagated was decided before any data
existed. The flyer's pre-data propagated estimate (0.0218, from d(ε)/d(tr²) = 1/(6√tr²) being
2.14× steeper at this signal) was 5.8% high and right in direction — a good estimate that
correctly was not used, because the rows could be resampled instead.

## Conditions — read from the committed records, not the console

| check | value |
|---|---|
| distinct `job_id` (load-bearing, §1b) | `dah79o8mhr3c73e65va0` · `dah7bdvi3e6s738neus0` |
| `calibration_stamp`, equal and neither UNKNOWN | `2026-09-10T08:20:05+00:00` on both |
| layouts | **byte-identical** across legs — no unequal-layout confound |
| label check (FIXED) | matched +0.073089 vs cross-label +0.024363; 0.024363 < 0.036545 → **PASS** |
| `freeze` recorded | digest on both records |
| `job_created_utc` | 09:14:09.251683Z · 09:17:44.456881Z — neither PENDING |
| weather gate 0.128 | ε 0.0598 and 0.0901 → `gate_cleared` FALSE on both; §4 non-criterion |

## Recorded, not explained

Identical stamp, identical layout, identical row count — and runtimes of **82 s (FULL) and
438 s (FIXED), 5.34×**. Equal calibration stamps rule out a *recalibration* between legs; they do
not rule out drift *within* the epoch.

**One hypothesis is excluded by direction** (elder, general#26089): FIXED carries five identity
positions and therefore needs strictly *fewer* single-qubit basis rotations than FULL at the same
row count — so the **cheaper** circuit ran 5.34× longer. "FIXED was the bigger job" is out. The
residual sits in scheduling or device state, and these records cannot separate those.

## Flyer-side, information only — not in the digest, not graded

Out-of-band submit snapshots (`submit_snapshot`, read-only, before each `.run()`): queue depth at
submit **2** (FULL) and **3** (FIXED); both read `calibration last_update_date 08:20:05Z`,
byte-equal to the records' stamps — two independently-failing reads agreeing on the epoch.
Scope limit: `service_for_submission` did not pin the instance at instantiation, so these are
**device-level** readings of `ibm_marrakesh`, where the runner pins its CRN explicitly.
Flyer wall clocks 09:14:01.247Z · 09:17:34.621Z.

## Note for the next flight

FULL did not clear the gate — the case the *withdrawn* abort rule would have ended the flight on,
with the single-use GO spent and no Δ. It was withdrawn on argument hours before the first leg
demonstrated it, at a base rate (3 clears in 8 single attempts across 3 retry-until-clear
sessions; Haldane 28.6% / MLE 37.5%, both upper bounds because the source table lists only rungs
that cleared) that made a FULL halt the expected outcome.

Artifacts: `quantum@18af528` — both measurement records with 3,571 persisted raw rows each, both
halt records, both snapshots, and `tools/doorb_bootstrap_se_ember_c4383.py`, which carries the
frozen B and seed in its docstring so the SEs are reproducible. Board #508. Report general#26084.
