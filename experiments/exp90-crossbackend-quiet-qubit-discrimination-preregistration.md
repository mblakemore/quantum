# Exp90 — Cross-backend quiet-qubit discrimination (pre-registration)

> **GRADED C6308 → PASS → Finding F70** (`findings/F70-crossbackend-quiet-qubit-discrimination-elder-c6308.md`).
> S_best[136,143]=+2.6958 (>2.0, ~23σ clear), S_worst[72,73]=+0.3608 (≤2.0), discriminates=True, S-gap +2.335.
> Retires the "single backend (ibm_marrakesh)" honesty bound F65/F66 both flagged. Cross-DEVICE (Heron-r2 family), NOT cross-generation.

**Author:** Elder (DC 1.5) · **Cycle:** C6306 · **Date:** 2026-07-02
**Backend:** ibm_fez (Heron-r2) — SECOND device, cross-backend test
**Mode:** submit-and-grade-later
**Builds on:** F58 (quiet_qubits.py, C6273), F65 (pick drifts to disjoint set, C6289),
F66 (picker still discriminates working-from-dead AFTER drift, on ibm_marrakesh, C6294)

## Motivation
F65 and F66 established that the F58 quiet-qubit picker, on **ibm_marrakesh**, (a) re-picks
live so the chosen pair drifts to a disjoint set within days, and (b) still discriminates
working-from-dead (S_best clears the CHSH bound, S_worst does not) *through* that drift. Both
findings list the SAME top honesty bound in their own words: **"N=2 days, single backend
(ibm_marrakesh); cross-backend generality still needs more points."**

This experiment directly retires that bound with the cheapest possible test: does the picker's
discriminate-working-from-dead property hold on a **different physical device**? The picker is
a DESIGN — `pick()` reads `backend.properties()` fresh and greedily selects the connected pair
minimizing objective-weighted readout+2q error. If the design generalizes, it should separate
good-from-bad qubits on ibm_fez (independent calibration, different coupling map, different
dead-qubit locations) with no code change. If it fails, the discrimination was
marrakesh-landscape-specific and the picker needs per-backend validation before trust.

## Claim under test (A) — the ONLY graded claim
The live-recomputed quiet-qubit picker **discriminates** working-from-dead regions on
**ibm_fez** (a device it has never been validated on), out of the box.

**Operationalization:** run `quiet_qubits.py --health --backend ibm_fez` (live-picks today's
best + worst pair on fez from fresh properties, submits CHSH: A∈{0,π/2}, B∈{π/4,3π/4}, 4096
shots, seed_transpiler=42, 8 jobs = best×4 + worst×4), then `--health-finalize --backend
ibm_fez` to compute S per pair.

**PASS (pre-registered, fixed before S exists):**
- `S_best > 2.0` (clears the CHSH/classical bound → genuine entanglement on the picked pair), AND
- `S_worst ≤ 2.0` (worst pair does NOT clear the bound → picker separated the two),
- i.e. `discriminates == True` in the finalizer output.

**FAIL:** either the best pair fails to clear 2.0, OR the worst pair also clears it (no separation).

**INCONCLUSIVE:** S_best within ~1σ of 2.0 (4096-shot CHSH SE on each E ≈ 0.016 → σ_S ≈ 0.03;
so a soft band S_best ∈ [1.94, 2.06] is called INCONCLUSIVE rather than PASS/FAIL).

## What each outcome means (both directions pinned, C5923 anti-motivated discipline)
- **PASS** → the no-cache live-repick DESIGN is not marrakesh-specific; it is a cross-device
  operational rule. Retires the "single backend" bound: 2 devices, same architecture (Heron-r2).
  Does NOT yet establish cross-GENERATION generality (see bounds).
- **FAIL** → the F66 discrimination was (at least partly) marrakesh-landscape-specific; the
  picker must be validated per-backend before its pick is trusted. Equally publishable — it
  would mean "re-pick live" is necessary but not sufficient; you also need a per-device sanity check.

## Confounds / honesty bounds (pre-committed)
- **Same architecture.** ibm_fez and ibm_marrakesh are BOTH Heron-r2. This tests cross-**device**
  (independent chip, calibration, coupling map, dead-qubit map) generality, NOT cross-**generation**
  (Eagle/Condor/Heron-r3). A PASS strengthens the operational rule to 2 devices of one family; it
  does NOT license claims about other processor generations. State this in the finding.
- **N=1 day on fez.** This is a single-window discrimination check on the new device, not a drift
  series. It answers "does it separate here at all," not "does it separate through fez's drift."
- **S_best magnitude is descriptive-only**, confounded by pair-choice + whole-device day-effect;
  report it but do NOT compare fez-S vs marrakesh-S as evidence about the picker (C5923).
- Absolute S expected in (2, 2√2≈2.828) for a good pair on a NISQ device; a value near 2√2 is
  not required for PASS — only clearing 2.0 while worst does not.

## Cost / logistics
- ~tens of QPU-seconds (8 shallow 2q CHSH circuits × 4096 shots), same envelope as F66.
- Quota at submit: 264/600 QPU-sec consumed (336 remaining), rolling-28d, VERDICT AVAILABLE.
- ibm_fez queue ~37 at submit; grade may land a later cycle (submit-and-grade-later is expected).
- Job manifest → `results/device-health/ibm_fez_chsh_jobs.json`; grade →
  `..._chsh_jobs_results.json`. Finding = F70 (next free) when graded.
