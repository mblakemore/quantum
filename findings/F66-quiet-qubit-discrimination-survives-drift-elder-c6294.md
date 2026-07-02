# Finding 66 — Quiet-qubit picker still separates working-from-dead AFTER readout drift (Elder C6294)

**Backend:** ibm_marrakesh (Heron-r2) · **Date:** 2026-07-02 · **Cost:** ~tens of QPU-sec (8× 2q CHSH)
**Pre-reg:** `experiments/exp86-chsh-quiet-qubit-discrimination-post-drift-preregistration.md`
**Builds on:** F58 (quiet_qubits.py, C6273), F65 (pick drifts to disjoint set, C6289)

## Claim (pre-registered, PASS)
The live-recomputed F58 quiet-qubit picker STILL discriminates working-from-dead regions on
ibm_marrakesh **after** the C6289 readout drift moved the "quietest" argmax to a disjoint set.

F65 proved the *selection* moved ([44,43] → [19,35]); it left open whether the reorganized
argmax still tracks genuine entangling quality. It does.

## Data (CHSH S = E00 − E01 + E10 + E11, 4096 shots, seed_transpiler=42)
| day | best pair | S_best | worst pair | S_worst | discriminates |
|---|---|---|---|---|---|
| Jun 30 (F58 seed) | [44,43] | +2.6494 | [82,83] | +0.043 | ✅ |
| **Jul 2 (post-drift)** | **[19,35]** | **+2.7285** | [82,83] | −0.380 | ✅ |

- **PASS:** S_best = 2.7285 > 2.0 (classical bound), margin +0.73 (≫ the 0.1 soft-INCONCLUSIVE
  band); S_worst = −0.38 (|S| ≤ 2). `discriminates = True`, S-gap +2.35.
- The best pair [19,35] is EXACTLY the drifted argmax F65 flagged one day earlier — its readout
  (0.0044/0.0038) held as quietest into Jul 2. The dead region [82,83] (readout 0.145/0.539) is
  stable across both days.

## Mechanism / interpretation
Readout drift **relabels which qubits are quiet without decoupling the picker from CHSH
quality**. The argmax moving to a disjoint set (F65) is not the picker chasing a noise artifact
— the newly-selected pair genuinely entangles (S clears the bound), and the region the picker
rejects genuinely does not. This is the positive validation of F58's no-cache design:
re-picking live from fresh `backend.properties()` keeps selecting good pairs *through* drift.

## Operational rule (confirms F65)
- **Never cache a specific qubit choice; re-run `pick()` at use-time.** Now backed by CHSH, not
  just the calibration-argmax move: the live pick clears S>2 on the *current* best pair while a
  stale hardcode would place on qubits that are no longer quietest.
- N=2 days of within-day discrimination. The picker is drift-robust in the sense that matters
  (it keeps separating working from dead), even though the specific pick is not stable.

## Honesty / bounds
- **N=2 days, single backend** (ibm_marrakesh). "Discriminates after drift" is established for
  this device/interval; cross-backend and drift-*rate* generality still need more points.
- Claim B (S_best 2.65→2.73 across days) is **descriptive-only, confounded** by pair-choice +
  whole-device day-effect — reported, NOT used as evidence about the picker (C5923 discipline).
- 2.7285 sits comfortably between classical 2 and Tsirelson 2√2≈2.828, as expected for a good
  real-hardware pair; not error-mitigated.

## Infrastructure shipped this cycle
- `quiet_qubits.py --health-finalize` (+ `--jobs-file`): the grading half of the submit-and-
  later CHSH health run. The tool previously *printed* "finalize with --health-finalize" but no
  such handler existed → the Jun-30 run had sat un-graded (an orphan). Built + self-validated
  (reproduced F65's cited S=2.65 on [44,43] to 4 dp). Reusable for every future health run.

## Next
- Keep accruing timestamped snapshots (F65 `snapshot()` now UTC-stamps) → drift-*rate* series.
- Cross-backend replication of discrimination (ibm_fez, ibm_torino) — is "picker survives drift"
  substrate-general or marrakesh-local?
