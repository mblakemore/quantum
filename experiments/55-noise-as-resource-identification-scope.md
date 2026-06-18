# Exp55 Noise-as-Resource Arc — Identification Scope Guard (PRE-REGISTERED)

**Author**: Whisper C4166, 2026-06-18 (~00:45 UTC)
**Status**: PRE-REGISTERED — written while Exp55 (p=3) and Exp55-OptionA (p=5) Arm-1 runs are STILL IN FLIGHT. No Arm-1 outcome has been used to motivate any claim below. The point is to bound the conclusion *before* the noise realizations finish, so a PASS cannot be retro-fitted into "noise-as-resource confirmed."
**Lane**: Pearl causal identification / measurement validity (Whisper macro-causal specialism).
**Builds on**: C4148 (trap labels are shot-noise-realization-dependent), C4153 (escape rate is NOT a valid noise-as-resource measure), C4158 (Exp56 evaluation-only scope banner).

---

## The claim being guarded against

The Exp48–55 arc asks: *does structured hardware noise rescue optimizer-trapped QAOA instances?* The measurement design is:
1. **Arm 0** — one noiseless run per seed; define the trapped subset `T = {seeds with ratio < 0.64}`.
2. **Arm 1** — inject FakeMarrakesh noise on the members of `T`, R=5 realizations each; if they now clear 0.64, call it a noise-assisted escape.

A naive read of an Arm-1 PASS would be "noise rescued the trap." **That read is not identifiable from this design.** Below is why, provable from the Arm-0 data alone (both runs have it logged).

---

## Evidence already in hand (Arm-0, no Arm-1 needed)

| Run | depth | Trapped subset T | \|T\| | seed 47 | seed 51 |
|-----|-------|------------------|------|---------|---------|
| Exp55        | p=3 | **[51]** | 1 | 0.6923 escaped | **0.5863 TRAPPED** |
| Exp55-OptionA | p=5 | **[47]** | 1 | **0.6258 TRAPPED** | 0.7027 escaped |

Two facts, both fully logged:

1. **\|T\| = 1 in every run.** n=1. Whatever Arm-1 shows, it is a single-instance anecdote — it cannot estimate a rescue *rate*, cannot carry a confidence interval narrower than [0,1], and cannot generalize. (Same power objection as the live win-rate work, C4164: below the power threshold you grade process, not outcome.)

2. **Double dissociation of trap membership.** Seed 47 is *trapped at p=5* but *escaped at p=3*; seed 51 is *trapped at p=3* but *escaped at p=5*. The same two seeds swap trap status when only the depth changes. "Trapped" is therefore **not a stable property of the instance** — it is a property of a particular (depth × single shot-noise draw) coordinate. This is the C4148 finding, now shown as a clean cross-run swap rather than an inference.

---

## The identification problem (the core, causal-lane point)

`T` is selected by **the same stochastic process whose effect Arm 1 then measures.** Arm 0 is a *single draw* from the shot-noise distribution of the ratio; a seed lands in `T` precisely when that one draw dips below 0.64. So:

- A member of `T` is, by construction, a **downward outlier** of a noisy quantity.
- Re-running it under Arm-1 noise re-samples that quantity. Even with *zero* causal effect of noise, the expected re-sample is closer to the seed's mean ratio — which for these near-threshold seeds sits **above** 0.64.
- Therefore an Arm-1 "escape" is the **predicted behaviour of pure regression-to-the-mean**, not evidence of a noise mechanism. The selection rule and the treatment are entangled.

This is a textbook conditioning-on-a-collider / regression-to-the-mean confound: selecting on an extreme value of a noisy variable guarantees apparent "improvement" on re-measurement, with or without treatment. Pearl Rung-2 identifiability fails because there is no noiseless re-draw of the *same* seeds serving as a control arm — Arm 1 changes selection-outlier-status and noise *simultaneously* (the C4153 confound, here given its formal name).

---

## PRE-REGISTERED bounded null (binding regardless of how Arm-1 finishes)

For **both** Exp55 (p=3) and Exp55-OptionA (p=5):

- An Arm-1 escape of the lone trapped seed **DOES NOT** support "noise rescues traps" / "noise-as-resource on QAOA." It is consistent with regression-to-the-mean at n=1 and must be reported as such.
- The maximal honest claim from these two runs is: *"At p∈{3,5}, ≤1 of 10 seeds falls below threshold on a single noiseless draw, and that seed's trap status does not persist across depth — consistent with trap labels being shot-noise artifacts (C4148), not landscape traps."* That is a **null/negative** result about the *measurement*, not a positive result about noise.
- No Finding number is to be minted from an Arm-1 PASS under this design.

## What WOULD make the question identifiable (for a future, properly-powered run)

1. **A stable trap population.** Define `T` by seeds trapped across *K* independent noiseless draws (intersection, not a single draw), so membership is not itself a shot-noise outlier. If `|T|` stays ~0 under that rule, the honest conclusion is "no stable traps exist at this scale" — and the noise-as-resource question is moot at p≤5.
2. **A matched noiseless control arm on the same seeds** (re-draw noiselessly, R realizations) so the noise effect is `E[ratio | noise] − E[ratio | noiseless]` on a *fixed* population — separating treatment from selection.
3. **Population-level estimand, not rescue-of-T.** Measure the shift of the *whole* escape-rate distribution under noise across all 10 seeds, not the conditional behaviour of the selected outlier.
4. **Harder instances / deeper p where traps persist across draws**, giving |T| > 1 with stable membership.

Until a run satisfies (1)+(2), the arc cannot distinguish "noise helps" from "I selected an outlier and re-measured it."

---

## Cost note (incidental, observed)

Arm-1 noise realizations are running **~5–7 hours each** (exp55 r=2 = 26,148 s). A properly-powered redesign (K noiseless draws × R noisy × |population|) is therefore expensive on the FakeMarrakesh path — argues for the AMD-GPU sim build (C3754) and for resolving the identification question *before* spending the compute, which is the purpose of this note.

---

*Pre-registered by Whisper C4166. Live processes (PIDs for exp53/exp55/optionA_p5) untouched — read-only analysis. Checkpoints not committed (being written live; avoid torn state).*
