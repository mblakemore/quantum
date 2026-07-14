# Adversarial audit — F117 rigorous 1SDI randomness certificate (Whisper C4713, Creator-directed)

**Substrate**: claude-opus-4-8. **Directive**: Creator (Discord, 2026-07-14): *"run an adversarial
cycle on one of our quantum repo claims, anything that sounds too good to be true."*
**Target**: F117 (Exp137) — *"0.65 rigorous one-sided-DI private random bits per use at 5σ, and the
model-free number BEAT the Werner model (0.682 > 0.656), so the real state is closer to ideal than
isotropic noise assumes."* **Method**: pre-registered parametric Monte-Carlo, no QPU.
**Result JSON**: `results/exp137_adversarial_bias_mc.json`. **Script**:
`scripts/adversarial_exp137_bias_mc.py`.

## The spine (holds regardless of any simulation)

The grade (`scripts/grade_exp137.py`) reports **H_min = 0.6823 ± 0.0063** where the ± is a 40-sample
**bootstrap that resamples the observed counts and re-runs the SAME reconstruct→project→SDP pipeline**.
That measures **fluctuation** — and fluctuation is not the problem here: H_min / SE ≈ 0.682 / 0.0063 ≈
**108**. The certified floor clears zero by ~100 bootstrap-SE, so the advertised **"5σ" gate is doing no
real work** (it clears by ~100σ in fluctuation terms). The certificate reports a *precise* bar on the
error that doesn't matter and is **structurally silent on the error that does** — the systematic
**bias** between the point estimate and the truth, which a resample-around-the-observed-point bootstrap
cannot see by construction.

## The test

Feed the **full pipeline** finite-shot data from a **plain isotropic (Werner) state** whose *true* H_min
is exactly the "model estimate": v = 1.6813/√3 = 0.9707 → **H_min_true = 0.6556**, S3_true = 1.6813
(the marrakesh Exp136 fit). Sample 9 tomography circuits × 20000 shots (matching Exp137) → reconstruct →
`project_valid` → guessing-SDP → H_min. Repeat 160×. **Pre-registered discriminator (filed before
results, C4713):** mean recovered ≥ 0.675 → "beats-the-model" collapses into bias; ≈ 0.656 → payoff is
real, retract that critique.

## Result (160 reps)

| Quantity | Value |
|---|---|
| Ground-truth H_min (isotropic v=0.9707) | 0.6556 |
| **Mean recovered H_min through the pipeline** | **0.6616** (std 0.0067) |
| **Pipeline bias** | **+0.0060 bits** ( = +0.9 × the reported 0.0063 SE) |
| Mean recovered S3 | **1.6813 (unbiased)** |
| Observed F117 rigorous H_min | 0.6823 |
| Observed − isotropic-through-pipeline | **+0.0207 (NOT explained by bias)** |

## Verdict — PARTIAL. One claim confirmed, my own stronger claim refuted.

**CONFIRMED (the defect is real and now quantified):** the certificate carries an **uncorrected positive
bias of ≈ +0.006 bits — the same size as its own reported error bar — and the bootstrap is blind to it.**
The honest central estimate is **~0.676, not 0.682**, and "±0.0063" omits a systematic offset of equal
size. The mechanism is textbook finite-count tomography bias (E[|r̂|²] = |r|² + Var ⇒ reconstructed
conditional states are on average more polarized/pure than truth ⇒ look more steerable). It is confirmed
cleanly by the split in this very run: the **first-moment S3 is unbiased (1.6813)** while the **nonlinear
SDP H_min is biased upward (+0.006)** — exactly the robust-correlator-vs-biased-tomographic-quantity
divide the thesis predicted.

**REFUTED (I retract my headline critique):** the bias does **not** reproduce 0.682 from isotropic
noise (it reaches only 0.662). The **"rigorous beats the model" gap is genuine**, ~0.021 of the raw
0.027 — corroborated independently by the observed reconstructed **S3 = 1.6876 > 1.6813** (the real state
*is* more steerable than the isotropic fit, and S3 is unbiased so that excess is signal). My pre-
registered strong claim ("the payoff is an artifact") failed its own test; honoring it, I withdraw it.

**SURVIVES UNTOUCHED:** the *existence* of positive certified randomness. Even the bias-corrected floor
(0.6509 − 0.006 ≈ 0.645) is ≫ 0. The front-door headline **"0.65 bits @5σ"** is the certified floor and
is **robust** — no walk-back there.

## Net correction owed to F117

1. Report the number **bias-corrected: ~0.676**, or state the +0.006 method bias alongside the ±0.0063
   fluctuation SE. Do not present "±0.0063" as the whole uncertainty.
2. Reframe "5σ": the gate passes with ~100σ of fluctuation margin; the honest limiting factor is a
   **systematic bias of ≈1 SE that the method does not quantify**, not the 5σ statistical bar.
3. "Beats the model" is **real but smaller** than stated: ~0.021 signal, ~0.006 method bias (≈22% of the
   claimed 0.027 gap is pipeline artifact, not physics).

## Scope of this audit (its own honesty)

This MC models only **statistical/tomographic** bias from an *isotropic* truth. Real hardware carries
**coherent/readout asymmetries** Werner does not — so **+0.006 is a lower bound** on the certificate's
true bias, and any hardware-systematic component is *also* invisible to the bootstrap. That strengthens,
not weakens, the spine: the honest error bar on the F117 number is wider than reported, and in a
direction the current grader cannot detect. A bias-aware certificate would resample from the *fitted
physical model* (parametric bootstrap) rather than the observed counts, or report the projection-bias
term explicitly.
