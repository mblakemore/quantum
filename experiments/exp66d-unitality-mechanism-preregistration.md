# Exp66 Part D — Unitality mechanism test (pre-registration)

**Author:** Ember (DC15E) | **Cycle:** C4183 | **Date:** 2026-07-15
**Status:** PRE-REGISTERED BEFORE COMPUTE (frozen cell set + hypotheses + grader below).

## 0. Motivation — verify my own C4171 claim

Finding 66C (Ember C4171) closed the noise-axis capk chain:

| Condition | Granular capk | Direction |
|---|---|---|
| Noiseless (Part C, N=34) | 0.528 | baseline ideal |
| FakeMarrakesh (Exp64) | 0.5625 | slight **LIFT** vs noiseless (weak anti-contraction) |
| Real QPU ibm_marrakesh (Finding 50) | ≈ 0 | COLLAPSE (warm-start non-transferable) |

I attributed the FakeMarrakesh lift to **non-unital noise** ("noise-assisted COBYLA
exploration", crediting Elder C6142's non-unital mechanism). **That attribution was a
hand-wave — never tested.** FakeMarrakesh mixes MANY effects at once (unital depolarizing +
non-unital amplitude damping + readout error + coupling constraints + gate miscalibration).
The lift could come from ANY of them. Attributing it specifically to *non-unitality* is an
un-verified premise. Creator directive: "verify facts before adopting them" — including my own.

## 1. Question

At **matched per-gate infidelity**, does **non-unital** noise (amplitude damping) lift the
granular capk above noiseless, while **unital** noise (depolarizing) does NOT?

This isolates unitality as the single variable — same base simulator (AerSimulator, no
coupling constraints), same cells, same protocol, only the noise channel's unitality differs.

## 2. Fixed design (frozen before compute)

- **Base sim:** `AerSimulator()` (all-to-all, no coupling map) — identical across all 3 arms.
- **Three arms, same 16 cells:**
  - `noiseless` — no noise model (re-run here on the same 16 cells for a clean matched baseline; must reproduce Part C ≈0.528 within noise).
  - `unital` — depolarizing noise, `depolarizing_error(p1,1)` on 1q gates, `depolarizing_error(p2,2)` on 2q gates.
  - `nonunital` — amplitude-damping noise, `amplitude_damping_error(g1)` on 1q gates, 2q = `amplitude_damping_error(g2) ⊗ amplitude_damping_error(g2)` on 2q gates.
- **Matched infidelity (the control):** target avg-gate-infidelities **ε1 = 0.0006 (1q, on `h`), ε2 = 0.003 (2q, on `cx`)** — device-scale, chosen to stay IN the FakeMarrakesh regime where the lift was observed (the p=3 circuit has ~180 cx; ε2=0.003 → cumulative 2q error ≈1−0.997^180 ≈ 0.42, comparable to FakeMarrakesh, not the QPU-collapse regime). For EACH arm solve the channel parameter numerically so `1 − average_gate_fidelity(error)` equals the target ε per gate class. Verified `|infid_unital − infid_nonunital| < 1e-4` per class and logged before the run.
- **1q noise applies to `h` only** (`rz` is a virtual Z rotation — physically noiseless; noising it would be unphysical). **2q noise applies to `cx`.**
- **Power comes from PAIRING, not N:** `run_cell_noiseless(seed,...)` calls `np.random.seed(seed)` internally, so cold-start and anchor initial parameters are IDENTICAL across all three arms for a given seed. Arms differ ONLY in the execution noise channel. The paired bootstrap `Δ = capk_nonunital − capk_unital` therefore cancels cell-to-cell variance — N=16 paired resolves a real directional effect that N=34 unpaired could not.
- **Protocol:** K=3 anchors, τ=LOO-median, **96 shots, COBYLA maxiter=15** (REDUCED from Part A/C's 256/20 — see compute-budget note). Reuses `run_cell_noiseless` verbatim (it takes `sim`), only the sim's noise model changes. `seed_simulator` fixed per cell so shot noise is shared across arms (tightens the pairing).
- **COMPUTE-BUDGET NOTE (measured during setup, C4183):** trajectory-sampling amplitude-damping (non-Clifford) over ~180 `cx` on 20 qubits is ~60× the noiseless per-cell cost — a measured **491 s for one unital cell even at 96 shots / maxiter 15** (noiseless cells were 4–11 s). A 3-arm × 10-cell run at those settings is ~2.7 hrs, infeasible in one cycle. **Final PILOT budget: 32 shots / maxiter 10 / 6 cells.** Scientifically valid for the CONTRAST because `seed_simulator` is FIXED IDENTICAL (1234) across arms → the shot-sampling RNG is SHARED, so shot noise is *paired* and cancels in Δ = capk_nonunital − capk_unital (not just symmetric — literally the same trajectories up to the noise channel). Absolute capk values are low-power/noisy at 32 shots and are NOT to be over-read; only the paired Δ and its sign are the deliverable. Explicitly labeled a PILOT.
- **Cell set (6, PRE-COMMITTED, first 6 of Part C's 34-cell pool by its frozen order):**
  `EDGES_20` seeds 42–47 = 6 cells.
- **Metric:** granular capk = pooled-LOO capture / mean_k (same `summarize`/`_pooled_loo` as Part A/C). Bootstrap 5000× the per-cell (lift_used, lift_fixed) pairs for a capk CI per arm and a paired unital−nonunital difference CI.

## 3. Pre-registered hypotheses & grader

- **H_mech (my C4171 attribution)** — predicts non-unitality is the cause:
  `capk_nonunital > capk_unital` AND `capk_nonunital ≥ capk_noiseless`.
- **Primary graded outcome (paired):** VALIDATED if the paired bootstrap
  `Δ = capk_nonunital − capk_unital > 0` in **≥ 2/3 of resamples**.
- **FALSIFIER (attribution wrong):** if `capk_unital ≥ capk_nonunital` (Δ ≤ 0 in ≥1/2 resamples)
  → the FakeMarrakesh lift is **generic noise-assisted exploration**, NOT unitality-specific.
  My C4171 mechanism sentence must then be corrected to "noise (either kind) mildly helps",
  and the Elder-C6142 non-unital credit removed from my finding.
- **NULL branch:** if BOTH noise arms sit within ±1 bootstrap-SE of noiseless (no lift from
  either) → at this scale neither channel helps; the Part A/C ~6% lift is FakeMarrakesh-specific
  (readout/coupling/calibration), not a generic depolarizing-or-damping effect. Also informative
  (redirects the mechanism search away from the Kraus channel entirely).

## 4. Confidence discipline (quantum = worst-calibrated domain, C3846)

No high-confidence point prediction registered. If any prediction is registered it is capped
≤0.55 and run through `pre-prediction-check.js CONF quantum` first. The value here is the
CONTROLLED FALSIFICATION, not a confident forecast — a mechanism I asserted gets a real chance
to be wrong at matched infidelity.
