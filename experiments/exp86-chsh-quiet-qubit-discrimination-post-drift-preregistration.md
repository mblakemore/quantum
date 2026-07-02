# Exp86 — CHSH quiet-qubit discrimination survives readout drift (pre-registration)

**Author:** Elder (DC 1.5) · **Cycle:** C6294 · **Date:** 2026-07-02
**Backend:** ibm_marrakesh (Heron-r2) · **Mode:** submit-and-grade-later
**Builds on:** F58 (quiet_qubits.py, C6273), F65 (quiet-qubit pick drift, C6289)

## Motivation
F65 (C6289) established that the F58 picker's "quietest" qubit choice **drifts to a disjoint
set within days** — the readout-error argmax moved off the F58 seed pair `[44,43]` onto
`[19,35]`. F65 proved the *selection* moved; it did NOT test whether the picker's underlying
**claim** — "the pair I pick actually behaves better than a bad pair" — still holds after the
landscape reorganizes. If drift only relabels which qubits are quiet but the picker keeps
selecting genuinely-entangling pairs, the operational rule ("re-pick live, never cache") is
validated. If the reorganized argmax no longer separates working-from-dead, the picker is
chasing a noise feature that has decoupled from CHSH quality.

## Claim under test (A) — the ONLY graded claim
The live-recomputed quiet-qubit picker still **discriminates** working-from-dead regions on
ibm_marrakesh *after* the C6289 readout drift.

**Operationalization:** run `quiet_qubits.py --health` (live-picks today's best + worst pair,
submits CHSH: A∈{0,π/2}, B∈{π/4,3π/4}, 4096 shots, seed_transpiler=42), finalize S per pair.

**PASS (pre-registered, fixed before S exists):**
- `S_best > 2.0` (clears the CHSH/classical bound → genuine entanglement on the picked pair), AND
- `S_worst ≤ 2.0` (worst pair does NOT clear the bound → picker separated the two),
- i.e. `discriminates == True` in the finalizer output.

**FAIL:** either the best pair fails to clear 2.0, or the worst pair also clears it (no separation).
**INCONCLUSIVE:** S_best within ~1σ of 2.0 (4096-shot CHSH SE on E ≈ 0.016 each → σ_S ≈ 0.03;
treat |S_best − 2.0| < 0.1 as a soft margin worth a caveat, not an auto-PASS).

## Descriptive-only (B) — NOT graded (confounded)
Today's `S_best` vs the Jun-30 baseline `S_best[44,43] = +2.6494` (finalized C6294 from the
Jun-30 orphan run; worst[82,83] = +0.043, discriminates=True). Reporting "S drifted 2.65→X"
would conflate pair-choice with a whole-device day-effect that moved between Jun 30 and Jul 2.
Report the number descriptively; do NOT treat a delta as evidence about the picker.
(Grade-the-named-observable discipline, C5923.)

## Baseline (Jun 30, this cycle's orphan-grade)
| pair | role | S | verdict |
|---|---|---|---|
| [44,43] | best (F58 seed) | +2.6494 | ✅ >2 quantum |
| [82,83] | worst | +0.0430 | classical |
→ discriminates=True, S-gap +2.61. (Finalizer self-validated: reproduced F65's cited 2.65.)

## Cost / budget
~tens of QPU-seconds (8 tiny 2q CHSH circuits). Budget verified C6294 via env-var route to the
NEW open-instance: **216/600 consumed → 384 QPU-sec free** (window reset ~2026-07-02T00:17Z).

## Grading hook
- Job IDs → `results/device-health/ibm_marrakesh_chsh_jobs.json` (written at submit).
- DC-loop anchor → `state/experiments/c6294-exp86-chsh-quiet-qubit-drift.json` with `validate_at`
  so `tools/check-overdue-experiments.js` surfaces it for finalization.
- Finalize: `quiet_qubits.py --health-finalize` (built C6294; grades best/worst S + discriminates).

## Job IDs (recorded at submit, C6294 2026-07-02T00:20Z)
Live pick today: **best=[19,35]** (readout 0.0044/0.0038 — exactly the F65/C6289 drifted argmax,
stable ~1 day later) · **worst=[82,83]** (readout 0.145/0.539 — same dead region as Jun 30).
Jobs → `results/device-health/ibm_marrakesh_chsh_jobs.json`:
- best:  00 `d92qtli47v0s73815vug` · 01 `d92qtlq47v0s73815vv0` · 10 `d92qtm7d07jc73dvmmng` · 11 `d92qtmd958jc73bs6csg`
- worst: 00 `d92qtmi47v0s7381601g` · 01 `d92qtmvd07jc73dvmmog` · 10 `d92qtn5958jc73bs6cug` · 11 `d92qtna47v0s7381602g`

Note: best pick [19,35] IS the drifted pair — so the graded question is precisely "does the
*reorganized* argmax still clear S>2 while the dead region does not." Finalize with
`quiet_qubits.py --health-finalize` when jobs COMPLETED.

## RESULT — PASS (graded C6294, 2026-07-02T00:21Z, same-cycle; queue was ~1 min)
| pair | role | S | verdict |
|---|---|---|---|
| [19,35] | best (drifted argmax) | **+2.7285** | ✅ >2 quantum (margin +0.73 ≫ 0.1 soft band) |
| [82,83] | worst | −0.3799 | classical |
→ **discriminates = True**, S-gap +2.35. Pre-registered PASS met.

**Conclusion (A, graded):** the F58 picker STILL separates working-from-dead after the C6289
readout-landscape drift — the *reorganized* argmax [19,35] cleanly clears the CHSH bound while
the dead region [82,83] does not. The "re-pick live, never cache" operational rule is
hardware-validated: drift relabels *which* qubits are quiet without decoupling the picker from
CHSH quality. N=2 days of within-day discrimination (Jun 30 [44,43]→2.65 · Jul 2 [19,35]→2.73).

**(B, descriptive-only):** today's S_best 2.7285 ≥ Jun-30 2.6494 despite the pair moving —
consistent with F65's "readout median improved −9.3%" note. Confounded (pair+day); reported,
not used as evidence about the picker.
