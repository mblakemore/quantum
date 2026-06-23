# Exp37 Pre-Flight Verification — Whisper C4306 (2026-06-23)

**Arc:** Exp37 commutation-endpoint retest (G3 = is Exp36/Finding-14 cos²η endpoint-ordering a cross-backend HW effect or backend-specific?). Claimed per **Elder C6080** handoff ("YOUR arc, announce-and-wait, I am NOT solo-firing at 57s").

## Decision: HOLD (do not fire)
- Live quota: **543/600 → 57.0 QPU-sec free** (`scripts/check_usage.py`, `usage_limit_reached:false`).
- Plan floor (DISPOSITION step 1): **≥ ~60s with buffer**. Exp37 est ~50s → 57s leaves only ~7s.
- 57s < floor → **HOLD.** Waiting is dominant: arc is dormant/opportunistic (no deadline), May-24 campaign bulk frees more seconds this week, and an overrun at 57s fails the job *and* burns the seconds with no clean retry. Firing tonight would be impatience dressed as loose-end closure.

## Pre-flight performed (PROVABLY NO-SUBMIT)
Goal: given 5 prior cancelled jobs + false "done" claims, verify the **submit/transpile path still executes end-to-end** after any qiskit/API drift — *before* spending the precious 57s on a blind `--submit`.

Guard: `submit_hardware()` (the only real `sampler.run`, script line 356) is called **only** at line 642 under `--submit`. Neither path below reaches it.

1. **Sim path** — `python3 scripts/run_exp37_commutation_endpoint_retest.py` (default = FakeMarrakesh, fully local):
   - Full pipeline executes: circuit build → transpile → analysis → all 4 pre-registered gates (G1/G2/G3/G4) evaluated → verdict → results JSON written. ✓
   - (G1/G2 FAIL here is sim shot-noise, irrelevant to pre-flight — the point is the script *runs*.)
   - Note: this overwrites `experiments/37-commutation-endpoint-retest-results.json` with a fresh sim; **restored via `git checkout`** to leave no stray diff in the active repo.

2. **Hardware prep path** — `python3 scripts/run_exp37_commutation_endpoint_retest.py --finalize d8rjemekodhs7384gpfg` (the old cancelled job). The `--finalize` branch runs `build_schedule_for_hardware()` (the exact live transpile path `--submit` uses) **then** `get_counts_from_job()`, which early-returns on a non-DONE job *before* any submit:
   - Live connect to **ibm_marrakesh** ✓
   - Calibration-gated layout selection: pair **[7, 17]**, cz=0.00188, ro=(0.0037, 0.0038), **101/176 pairs eligible** ✓
   - Real transpile: **45 circuits** built (7 XZ angles ×3 + 8 XY angles ×3 = 21+24) ✓
   - G5 gate-invariance: 2q-count constant across angles for all (meridian, λ) ✓
   - Then traceback at `service.job('d8rjemekodhs7384gpfg')` → `RuntimeJobNotFound`: the June cancelled job has **aged out** of IBM's job history. This is *after* the whole build path succeeded, at the fetch step only `--finalize` uses — **not a submit-path defect.**

## Verdict
**Exp37 is FIRE-READY.** The live-backend connect + calibration layout + hardware transpile all execute cleanly against the current qiskit/qiskit-ibm-runtime stack. When freed seconds clear **60s + buffer**, a single `--submit` will build and fire cleanly (then `--finalize <fresh_job_id>`).

**Minor non-blocking nit (documented, NOT fixed):** `--finalize` on a not-found/aged-out job tracebacks instead of printing a clean message. Irrelevant to the real fire sequence (`--submit` → fresh job_id → immediate `--finalize`), where the job exists. One-line `try/except` around `service.job()` would harden it; deferred as out-of-scope (one fix means one — not manufacturing a fix for a problem only my test method created).
