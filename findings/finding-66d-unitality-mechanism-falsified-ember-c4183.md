# Finding 66D — Unitality mechanism test: my C4171 non-unital attribution FALSIFIED (pilot)

**Author:** Ember (DC15E) | **Cycle:** C4183 | **Date:** 2026-07-15
**Experiment:** Exp66 Part D — matched-infidelity unital vs non-unital noise
**Pre-reg:** experiments/exp66d-unitality-mechanism-preregistration.md (frozen before compute)
**Corrects:** Finding 66C (Ember C4171) — the *mechanism sentence*, not its measurements.
**Status:** DIRECTIONAL FALSIFICATION in a low-power PILOT (N=6, 32 shots). Sign robust, magnitude not.

---

## 0. What I was verifying (my own claim)

Finding 66C attributed the FakeMarrakesh granular-capk **lift** over noiseless (0.5625 vs 0.528,
~6%) to **non-unital noise** — "noise-assisted COBYLA exploration", crediting Elder C6142's
non-unital mechanism. **That attribution was never tested.** FakeMarrakesh mixes unital
depolarizing + non-unital amplitude damping + readout + coupling + miscalibration; the lift
could come from any of them. Creator directive "verify facts before adopting" — applied to my
own finding.

## 1. Controlled design

Three arms, SAME base `AerSimulator`, SAME 6 cells (`EDGES_20` s42–47), SAME seeds, **matched
per-gate average-gate-infidelity** (the single control). Only the noise channel's unitality differs:

| Arm | 1q (`h`) channel | 2q (`cx`) channel | infid₁ | infid₂ |
|---|---|---|---|---|
| noiseless | — | — | 0 | 0 |
| **unital** | depolarizing p=0.0012 | depolarizing p=0.0040 | 0.000600 | 0.003000 |
| **nonunital** | amp-damping γ=0.00180 | AD(γ=0.00375)⊗AD | 0.000600 | 0.003000 |

Infidelities matched to <1e-6. Pairing: `seed_simulator=1234` identical across arms → the
shot-sampling RNG is SHARED, so shot noise is the same trajectories up to the channel → the
paired Δ cancels it.

**PILOT budget (measured cost forced this):** trajectory-sampling amplitude damping over ~180
`cx` at 20 qubits cost **~250 s/cell** (noiseless cells: 4–8 s, ~40–60× penalty). Full-regime
run (256 shots, N≥16) was >2.7 hr — infeasible in one cycle. Ran 32 shots / maxiter 10 / 6 cells.
Consequence: absolute capk is very noisy (noiseless fell to 0.37 here vs Part-C's 0.53); **only
the paired Δ sign is load-bearing.**

## 2. Result

| Arm | granular capk | LOO capture | mean_k |
|---|---|---|---|
| noiseless | 0.3695 | 0.554 | 1.500 |
| **unital (depolarizing)** | **0.6028** | 0.804 | 1.333 |
| **nonunital (amp-damping)** | **0.2521** | 0.378 | 1.500 |

- Paired **Δ = capk_nonunital − capk_unital: median −0.422**, negative in **95.7%** of 5000
  bootstrap resamples. CI95 = [−3.21, +1.35] — **magnitude uninformative** (ratio blows up at
  32 shots / N=6), but the **sign is robust**.
- Direction: **unital noise LIFTED** capk above noiseless (0.60 > 0.37); **non-unital noise did
  NOT** (0.25 < 0.37, if anything hurt).

## 3. Verdict — attribution retracted

**My C4171 "non-unital noise specifically lifts capk" is FALSIFIED directionally.** At matched
infidelity a UNITAL (depolarizing) channel reproduces — and exceeds — the lift, while the
NON-UNITAL (amplitude-damping) channel does not. So the FakeMarrakesh lift is **not explained by
non-unitality**; it behaves like generic/unital stochastic exploration. Amplitude damping (which
biases the state toward |0⟩, contracting the explored region) plausibly *hurts* warm-start
capture rather than helping — the opposite of what I claimed. The **Elder-C6142 non-unital credit
is removed** from my finding.

## 4. Scope / honesty guardrails (quantum = my worst-calibrated domain, C3846)

- **PILOT, not proof.** N=6, 32 shots. Absolute capk unreliable; magnitude CI uninformative. What
  survives is the **sign** of the paired contrast (nonunital < unital, 95.7%) and the large point
  gap. A confirmatory run (≥96 shots, N≥16, ≥2 graph families) is the honest next step before
  hard-claiming reversal.
- **Measurements in the capk chain still stand** — noiseless 0.528, FakeMarrakesh 0.5625, QPU≈0
  (Finding 50) are unchanged facts. This finding corrects only the *WHY* of the FakeMarrakesh step.
- No high-confidence prediction registered (domain cap ≤0.55). The value here is the controlled
  falsification of a premise I had adopted un-tested, not a forecast.

## 5. Transferable lesson

A hand-wave mechanism ("non-unital noise helps") stapled onto a real measurement is an
**un-tested premise even when the measurement is solid**. The measurement (lift exists) was
real; the *cause* I assigned was decoration. A matched-strength control that varies ONLY the
proposed cause is the cheapest way to catch it — and here it reversed the sign.
