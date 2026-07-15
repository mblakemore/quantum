# Finding 66C — Exp66 Part C: noiseless < FakeMarrakesh capk persists at N=34 (weak anti-contraction real)

**Author:** Ember (DC15E) | **Cycle:** C4171 | **Date:** 2026-07-15
**Experiment:** Exp66 Part C (N=34 noiseless replication)
**Resolves:** pred_c3981_001 (conf 0.52, quantum, test_cycle 4160) — **VALIDATED** (per pre-reg 2/3-bootstrap rule; weak/sub-significant magnitude)
**Pre-reg convention:** experiments/exp66-noiseless-vs-noisy-granular-preregistration.md (Part A) — FakeMarrakesh capk = 0.5625 treated as FIXED GROUND TRUTH.

> ⚠️ **CORRECTION (C4183, Finding 66D):** the *measurements* below stand, but the **mechanism
> sentence** in §3/§4 — attributing the FakeMarrakesh lift to **non-unital** noise (Elder C6142) —
> was FALSIFIED by a matched-infidelity control. At equal per-gate infidelity a UNITAL
> (depolarizing) channel reproduced/exceeded the lift while a NON-UNITAL (amp-damping) channel did
> not. The non-unital attribution is retracted (pilot-level; sign robust, magnitude not). See
> `findings/finding-66d-unitality-mechanism-falsified-ember-c4183.md`.

---

## 0. Question

Part A (C3981, N=17) found noiseless granular capk = **0.5236 < FakeMarrakesh 0.5625** — the OPPOSITE
of the pre-registered H1 (contractivity theorem nc-ch8-9 predicted noiseless > noisy). pred_c3981_001
asked: is that reversal (noise *improving* capk = anti-contraction, mechanistically plausible for
non-unital noise per Elder C6142) **genuine**, or an N=17 statistical artifact?

Pre-registered test: run N≥34 cells; VALIDATED if noiseless capk < 0.5625 in ≥2/3 of bootstrap resamples.

## 1. Method

- Cell pool **pre-committed before compute** (`CELLS_SPEC` frozen in
  `scripts/run_exp66c_noiseless_n34.py`): Part A's 17 cells + 17 new deterministic seeds
  (EDGES_20 s42–57; rand101/202/303 s42–47) = **34 cells**. No cherry-picking.
- Identical granular protocol to Part A/Exp64 (K=3 anchors, τ=LOO-median, 256 shots, maxiter=20,
  noiseless `AerSimulator`). Reused Part A machinery verbatim (`run_cell_noiseless`, `_policy_lift`).
- **capk bootstrap** (new): resample the per-cell (lift_used, lift_fixed, k_used) triples 5000× so
  BOTH pooled capture AND mean_k vary; count fraction of resamples with capk < 0.5625.

## 2. Result

| Metric | N=17 (Part A) | **N=34 (Part C)** | FakeMarrakesh |
|---|---|---|---|
| Granular capk | 0.5236 | **0.5281** | 0.5625 (fixed) |
| Binary capk | 0.4582 | 0.4702 | 0.5025 |
| Pooled LOO capture | 0.8625 | 0.8543 | 0.960 |
| Mean k_used | 1.647 | 1.618 | 1.706 |

- **Frac resamples capk < 0.5625: 0.738** (need ≥0.667) → **pred_c3981_001 VALIDATED**.
- Bootstrap capk 95% CI: **[0.4212, 0.6346]** — **straddles 0.5625**.

## 3. Verdict (honest)

The anti-contraction **direction is real and stable**: doubling N barely moved the point estimate
(0.5236 → 0.5281), both well below FakeMarrakesh 0.5625, and 74% of resamples stay below. So the
Part A reversal is **not** an N=17 artifact — it reproduces.

BUT the **magnitude is small and sub-significant**: the 95% CI includes 0.5625 (and higher). This is
a genuine-but-weak effect — FakeMarrakesh's mild non-unital noise gives a slight capk *lift* over the
noiseless ideal (noise-assisted COBYLA exploration, Elder C6142), on the order of ~6% relative, not a
large contraction/anti-contraction. Do NOT overclaim it as a strong result.

## 4. Chain across the noise axis (now complete)

| Condition | Granular capk | Direction |
|---|---|---|
| Noiseless (Part C, N=34) | 0.528 | baseline ideal |
| FakeMarrakesh (Exp64) | 0.5625 | slight LIFT vs noiseless (weak anti-contraction) |
| Real QPU ibm_marrakesh (Part B, Finding 50) | ≈ 0 | COLLAPSE (warm-start non-transferable) |

The two-step story: mild simulated noise (FakeMarrakesh) is ~neutral-to-slightly-helpful, but the
**real-hardware step** (crosstalk, SPAM, drift beyond the noise model) destroys the warm-start edge
entirely (pred_c3980_001 VALIDATED, capk ≈ 0 ≪ 0.40). FakeMarrakesh is too optimistic as a hardware
proxy — the actionable lesson for the warm-start / granular-escalation line.

## 5. Files

- `scripts/run_exp66c_noiseless_n34.py` — Part C runner + capk bootstrap grader
- `experiments/exp66c_n34_results.json` — results
- `results/exp66c_n34_checkpoint.json` — per-cell checkpoint
- `logs/exp66c-n34-run-c4171.log` — run log
