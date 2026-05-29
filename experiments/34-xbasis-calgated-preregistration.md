# Exp34 — PRE-REGISTRATION: X-Basis Immunity, Calibration-Gated Retest (Whisper C3746)

**Backend**: ibm_kingston (Heron-r2, independent of marrakesh) | **Date**: 2026-05-29
**ORQ**: #1 — "Does X-basis immunity (Finding 03) generalize across the heavy-hex family?
Pre-reg gate: ≥2× X/Z fidelity ratio on an independent backend."

## Why this experiment exists

Exp31 (C3738) ran exactly this test on ibm_kingston and came back **INCONCLUSIVE**: an
anomalous ~20.36pp gate-independent fidelity floor swamped the ~3× X/Z mechanism. Exp32
(C3740) floor spectroscopy decomposed that floor with four `do()`-arms and proved it is
**layout-dominated**: the catastrophic case was a dead qubit (q146 readout 0.518, T1/T2 null,
cz error 1.0). On a *good* pair the floor drops to a stable ~9pp (2.7pp SPAM + 6.8pp incoherent
decoherence). Exp32's explicit retest recipe: **select the layout pair by calibration BEFORE
measuring, then the mechanism is no longer swamped.**

Exp31's flaw was a methodological one I own: it let the transpiler choose the layout
(`seed_transpiler=42`, no `initial_layout`), so it landed on/near a bad pair. Exp34 fixes the
*single* variable: it pins the Bell circuit to a calibration-verified-good coupled pair. Same
9-circuit basis-resolved ZNE design, same pre-registered criteria, same shots/seed — only the
layout-selection step is added. This is a clean `do(layout = good)` on Exp31.

## Calibration gate (FIXED before submission)

Scan every coupled pair `(a,b)` in the backend coupling map; a pair is **eligible** iff ALL hold:
- `readout_error(a) ≤ 0.05` AND `readout_error(b) ≤ 0.05`
- `T1(a), T2(a), T1(b), T2(b)` are all non-null (qubit is characterizable)
- `cz_error(a,b) < 0.01`

Among eligible pairs, **select** the one minimizing `cz_error + 0.25·(readout_a + readout_b)`
(2q gate error dominates a 2q-gate circuit; readout is the tie-breaker). The selected physical
pair is pinned via `initial_layout=[a, b]`, `optimization_level=0` (preserves ZNE folds, C3720),
`seed_transpiler=42`. The selected pair + its full calibration are recorded in the results JSON
so the gate is auditable. If ZERO pairs pass the gate, the run ABORTS (does not silently fall
back to a bad pair) and reports the backend as too degraded for the test that day.

## Design (unchanged from Exp31)

Bell |Φ+⟩ (H q0, CX q0→q1). Ideal ⟨ZZ⟩=+1, ⟨XX⟩=+1, ⟨YY⟩=−1 (all |1|). Basis-resolved global-fold
ZNE at λ∈{1,3,5}; append readout rotation (ZZ→none; XX→H both; YY→Sdg,H both); `measure_all`.
`err_basis(λ) = 1 − |⟨BB⟩|`. 3 bases × 3 λ = 9 circuits, 4096 shots, one co-submitted job
(single calibration snapshot ⇒ daily ±7pp drift cancels in the relative criteria).

## Pre-registered criteria (FIXED before submission)

Let `eXX,eYY,eZZ` = mean err across λ per basis; `gamma_basis` = OLS slope of err vs λ.

- **T1 (X-IMMUNITY REPLICATES, headline / README gate)**: `eZZ/eXX ≥ 2.0` AND `eXX < eZZ`
- **T2 (Y-INJECTION REPLICATES)**: `eYY > eXX` with `eYY − eXX ≥ 0.02`
- **T3 (SLOPE ORDERING)**: `gamma_ZZ > gamma_XX`

**T1 PASS** → Finding 03 X-basis immunity REPLICATES on an independent Heron device ⇒ upgrades from
a marrakesh-specific observation to a heavy-hex **architectural** principle (the README ORQ#1
upgrade gate is met).

**T1 FAIL (on a calibration-verified-good pair)** → this is now a *clean* falsification, not a
floor confound: X-basis immunity is marrakesh substrate/calibration-specific, NOT architectural,
and Finding 03's "first-class compilation concern" framing requires downgrade.

## What Exp34 can and cannot settle

- **Can**: whether the ~3× X/Z ratio survives on a *good* ibm_kingston pair (the question Exp31
  could not answer because of the floor).
- **Cannot**: n=1 backend beyond marrakesh; a single good pair (not a pair-ensemble); cross-
  *platform* generalization (ORQ#5, trapped-ion/photonic — different dominant noise channel) is
  untouched. A PASS upgrades to "heavy-hex architectural"; it does not claim cross-substrate.

Run (sim preview): `python3 scripts/run_exp34_xbasis_calgated.py`
Run (hardware):    `python3 scripts/run_exp34_xbasis_calgated.py --submit`
Finalize:          `python3 scripts/run_exp34_xbasis_calgated.py --finalize <job_id>`
