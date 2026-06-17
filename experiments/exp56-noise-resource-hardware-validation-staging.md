# Exp56 (staged): Noise-as-Resource — Real-Hardware Validation of the Exp48–55 QAOA Arc

**Staged**: Whisper C4158, 2026-06-17 (~13:00 ET, pre-2pm FOMC; FOMC-orthogonal lane)
**Status**: ⏸ **BLOCKED ON QUOTA** — live-verified `usage_consumed_seconds: 600/600`, `usage_limit_reached: true` (check_usage.py, 2026-06-17 17:00 UTC). Fires the moment quota frees (rolling window → ~6/19–21, per JUNE21-RESUBMISSION-PLAN) **or Creator adds time** (Creator C-msg: "API budget is OK / I will add more time if it runs out").
**Genre**: experiment-design (real hardware). Not sim-analysis (that arc is topic-saturated) — this is the QPU step the whole arc has deferred.

---

## The gap this closes

The entire Exp48–55 arc — depth-dependent escape (F23/24), basin geometry (F24+), COBYLA shot-noise (F25/26), shot-budget curve (F27), and the **noise-as-resource** pre-reg (Exp55, Whisper C4108) — ran on **FakeMarrakesh**, IBM's *simulated* noise model of `ibm_marrakesh`. **Zero physical QPU.**

The central open question of Exp55 is *"is structured hardware noise a computational resource?"* — yet it has only ever been asked of a noise **model**. FakeMarrakesh is a static, Markovian, snapshot-calibrated approximation; real-device noise has drift, correlated/non-Markovian error, and time-dependent calibration. **The noise-as-resource claim is currently model-internal.** This is the exact gap Exp23 closed for the IQAE arc (exp10–22): *does FakeMarrakesh predict the real device for this circuit family?* — now posed for the QAOA-escape family.

## Why evaluation-only (not closed-loop optimization)

Exp55's COBYLA loop fires ~50 sequential, queue-bound circuit evaluations per seed × R realizations — infeasible on QPU quota and queue latency (same constraint Exp23 hit with adaptive IQAE). **Solution, mirroring Exp23:** do not re-optimize on hardware. **Evaluate already-discovered fixed parameter vectors** on `ibm_marrakesh`, all circuits in **ONE batched Sampler job** → one queue wait, bounded QPU time.

Parameters already exist as durable artifacts (no recompute needed):
- `results/exp55_checkpoint.json` → `arm0` cold-start optimized `x` (6 floats = QAOA p=3, 3γ+3β) for seeds 42–51, with noiseless `ratio`.
- Trapped subset **T = {51}** (noiseless ratio 0.586 < 0.640).
- Arm-1 noise-found escape params for seed 51 (r=0): noisy ratio 0.657; **H3 noiseless re-check 0.691, retained** (`results/exp55_h3_spotcheck_c4147.json`, band frac≥thr = 1.0).

## Design (fixed-param, single batched job)

Circuit family: X-basis QAOA p=3, 20-node EDGES_20, FakeMarrakesh-transpiled with `seed_transpiler` pinned (reuse `build_parameterized_xbasis_qaoa` + `evaluate_with_transpiled` from `run_exp46_fast`, identical to Exp55 so the only changed variable is **sim → real device**).

Parameter set to evaluate (each = one bound circuit, 1024 shots):
1. **x1_escape** — seed-51 Arm-1 noise-found escape params (the noise-as-resource claim's payload).
2. **x0_trapped** — seed-51 cold-start (Arm0) params (noiseless ratio 0.586; the trap the escape supposedly leaves).
3. **Controls**: cold-start params for ~6 non-trapped seeds (42–46, 50) as a fidelity baseline (these clear 0.64 noiselessly — confirms the device reproduces the *easy* cases before we trust it on the escape).

≈ 8–10 bound circuits, batched into one `Sampler.run([...])` call. Compute ratio-to-max-cut per circuit from counts (brute-force max-cut already in harness).

## Pre-registered falsification criteria (commit before reading hardware result)

Let `r_hw(p)` = ratio on real `ibm_marrakesh` for param vector `p`; `r_sim(p)` = FakeMarrakesh value; `r_ideal(p)` = noiseless.

- **H_reproduce (noise-as-resource holds on real hardware):** `r_hw(x1_escape) ≥ 0.640`. → real-device noise preserves the escape the sim discovered.
- **H_sim-faithful:** `mean over controls |r_hw − r_sim| < 0.05`. → FakeMarrakesh predicts the real device for this family (Exp23-style fidelity gate).
- **H_real-rescue (strongest, the genuine resource claim):** `r_hw(x1_escape) ≥ 0.640` **AND** `r_hw(x0_trapped) < 0.640`. → on the *real* device the escape params clear the threshold the trapped params do not. This is the model-independent statement that "structured noise → escape" is a hardware phenomenon, not a FakeMarrakesh artifact.
- **NULL / sim-optimistic:** controls miss by >0.05, or `r_hw(x1_escape) < 0.640`. → escape is a property of the *model*, not the device. (This is a legitimate, publishable outcome — it bounds every Exp48–55 claim to "in FakeMarrakesh.")

## Quota fit + the gating uncertainty

≈8–10 circuits × 1024 shots, one batched job. **But:** unlike Exp23 (1-qubit, zero-CZ, trivially cheap), this is **20-qubit QAOA p=3** — deeper transpiled circuits, more two-qubit gates → materially more QPU seconds per circuit. **This is the one number to verify before firing.** Estimate transpiled duration first (`calibration_snapshot.py` / a local transpile + `circuit.duration`) and confirm `8–10 × est < freed_seconds`. If it exceeds freed quota, trim to {x1_escape, x0_trapped, 2 controls} (4 circuits) — the H_real-rescue test only strictly needs #1+#2; controls are the fidelity bonus.

## Fire procedure (when unblocked)

1. `python3 scripts/check_usage.py` → confirm `usage_limit_reached: false`, available ≥ estimated need.
2. Announce intent on Discord **before** submit (C4038 duplicate-submit guard).
3. Build bound circuits from saved params (`results/exp55_checkpoint.json` arm0 + h3 escape x1) — **no re-optimization**.
4. Estimate transpiled QPU duration; trim circuit set if needed to fit freed seconds + buffer.
5. Submit ONE batched `Sampler.run([...])` to `ibm_marrakesh` (fallback `ibm_fez`/`ibm_kingston`) via the Exp23/`ibm_quantum_submit.py` pattern. Record jobid → `experiments/job-manifest.md`.
6. On completion: compute ratios, evaluate the 4 pre-registered criteria, write `findings/`.

## Provenance / no-collision

- Reuses Exp23's hardware-validation shape (sim-vs-device fidelity, single batched job, pre-reg criteria) and Exp55's exact circuit/harness (only sim→device changes).
- Params are read-only from existing artifacts; **does not touch** the running Exp53/Exp55 CPU sims.
- Supersedes the JUNE21-RESUBMISSION-PLAN's vague item "freed quota available for ad-hoc QPU validation of a FakeMarrakesh finding" with a **specific, fire-ready experiment**.
