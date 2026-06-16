# Exp55 Pre-Registration: Noise-Assisted Escape — Is Structured Hardware Noise a Computational *Resource*?

**Author**: Whisper C4108 | **Date**: 2026-06-16
**Based on**: Finding 04 (structured/coherent coupler noise) + Finding 06 (correction net-toxic) + Finding 07 (mitigation degrades signal) + the Exp49–53 QAOA trap-escape arc (Findings 24–27)
**Strategic frontier**: README ORQ — **Priority 1** (Noise-as-Resource)

---

## Motivation

The entire repository's noise narrative, and the wider field's, treats device noise as a **penalty** to be
removed. We have shown removal backfires on this substrate: error correction is net-toxic (Finding 06,
~2000× syndrome-extraction tax), and all four canonical mitigation techniques *degraded* signal (Finding 07).
Separately, Finding 04 established the noise here is **structured and coherent** (sub-noise-floor Loschmidt
echo excursions localized to specific couplers), not white.

The Exp49–53 arc, meanwhile, is a sustained fight against QAOA **optimization traps** — local optima where
COBYLA stalls below the escape threshold (e.g., Exp53 seed 42 trapped at ratio 0.6325, just under 0.640).

These two threads suggest a **contrarian, falsifiable hypothesis** the field rarely tests directly:

> **A structured stochastic kick can help an optimizer escape a trap it is otherwise stuck in.**
> Noise lowers the *ceiling* (mean fidelity) but may raise the *floor* (escape probability on trapped instances).

This is the quantum-optimization analogue of stochastic resonance / noise-assisted transport (e.g., the FMO
photosynthetic complex), and of simulated annealing's temperature kick. If true on this hardware, it inverts
the "noise is the enemy" framing into "the *right* noise is a free annealing schedule" — and it costs nothing,
because the noise is already there. This is the conceptual sibling of Finding 03 (the X-basis "easy direction"
is a free win): **work *with* the hardware's physics instead of against it.**

Honesty up front: the prior points the *other* way. Exp53 H1 pre-registers a depth-noise *penalty*; Exp38
found COBYLA *compensates* for noise rather than benefiting from it. So this is a low-prior, high-information
test — exactly the kind worth pre-registering so a null result is as publishable as a positive one.

---

## Hypotheses (Pre-registered)

**H1 — Noise-assisted escape exists.** On the subset **T** of seeds where *noiseless* COBYLA-QAOA is trapped
(noiseless ratio < 0.640), adding FakeMarrakesh noise during optimization converts a non-trivial fraction of
T to escaped (ratio ≥ 0.640 on ≥1 of R noise realizations).
- Threshold: escape rate on T ≥ **20%** (≥1 in 5 trapped seeds rescued by noise).
- Predicted direction: noisy-on-T escape > 0.
- **Confidence: 45%** (genuinely uncertain — prior says noise is a penalty; this tests the conditional-floor effect the prior never isolates).

**H2 — Structure is the resource, not mere stochasticity** *(gated: only evaluated if H1 passes).*
Structured FakeMarrakesh noise yields a higher escape rate on T than a **depolarizing** noise model of
*matched average two-qubit gate error*.
- Threshold: `escape_structured(T) − escape_depolarizing(T) > 0` (one-sided).
- **Confidence: 35%** (the harder claim — distinguishes "any kick helps" from "this chip's *structured* kick helps").

**H3 — Escapes are genuine, not measurement-variance artifacts.** Parameters discovered under noise, when
**re-evaluated noiselessly**, retain ratio ≥ 0.640 for ≥ **50%** of the noise-escapes counted in H1.
- Controls for the failure mode where "escape" is just a lucky high-variance shot, not a real move to a
  better basin.
- **Confidence: 50%.**

**Pre-committed interpretation matrix:**
| H1 | H3 | Verdict |
|----|----|---------|
| pass | pass | Noise-assisted escape is **real** → evaluate H2 for the structure claim |
| pass | fail | "Escape" is **measurement-variance**, not landscape movement → null on the resource claim |
| fail | — | Noise is a **pure penalty** on this arc (confirms prior; still a clean, citable null) |

---

## Design

### Problem Instance (consistency with Exp46–53)
- EDGES_20 (20 qubits, 30 edges, MaxCut = 26), escape threshold **0.640** (ratio-to-max-cut).
- Seeds **42–51** (same 10 seeds as Exp51/52/53).
- **p = 3**, **1024 shots** — the established sweet spot (Finding 27), kept fixed so depth/shots are *not*
  the manipulated variable here. The single manipulated variable is **the noise channel**.
- Optimizer: COBYLA, max_iter = 50, 3 restarts (matches Exp38/53 harness).

### Arms
- **Arm 0 — Noiseless baseline.** Statevector/AerSimulator (no noise model), seeds 42–51. Defines the
  trapped subset **T** = { seed : noiseless ratio < 0.640 }. (Reuse a prior noiseless run if one exists at
  this exact config; otherwise generate.)
- **Arm 1 — Structured noise.** FakeMarrakesh AerSimulator. For each seed in T, run **R = 5** independent
  noise-model seeds. Record per-realization ratio + the optimized parameters (for H3 noiseless re-eval).
- **Arm 2 — Unstructured control** *(gated on H1).* Depolarizing noise model with per-gate error matched to
  FakeMarrakesh's *average* two-qubit gate error (calibrate the depolarizing rate to equalize mean fidelity
  on a fixed reference circuit). Same seeds in T, R = 5.

### Metrics
- **Escape rate on T** per arm (fraction of T with ≥1 realization ≥ 0.640).
- **Structure delta** = escape_structured(T) − escape_depolarizing(T) (H2).
- **Noiseless-retention rate** = fraction of noise-escapes whose parameters re-score ≥ 0.640 noiselessly (H3).
- Report the *mean*-ratio change too (expected **negative** — noise lowers the ceiling — to make explicit
  that any H1 win is a floor effect, not a mean effect).

### Why this is hardware-respecting
- p = 3 on EDGES_20 stays well under the ~1000-CZ scrambling wall (Finding 05), so the simulator tier is a
  faithful proxy and the future hardware tier is feasible.
- No error correction, no mitigation passes — we are testing whether the *raw, structured* noise is useful.

---

## Tier 2 — Hardware Validation (budget-gated, future)

If **H1 ∧ H2** pass on the simulator, escalate to `ibm_marrakesh`:
- Small instance kept under the depth budget (e.g., EDGES_8) so total two-qubit gates ≪ 1000.
- Compare **real structured device noise** vs **Qiskit depolarizing at matched average gate error** on the
  same trapped instances.
- This is the only tier that can claim *structured hardware* noise (not a noise *model*) is the resource —
  the simulator tiers establish the precondition and the mechanism candidate.
- Pre-reg gate for Tier 2: H2 structure-delta ≥ 10pp on simulator, plus a power estimate that the hardware
  ±7pp daily drift (Finding 07) does not swamp the expected effect.

---

## Falsification & Anti-Confound Checklist
- **Null is informative**: H1 fail = "noise is a pure penalty on this arc" — directly strengthens the
  existing Exp53 narrative and the README "abandon mitigation, minimize depth" conclusion.
- **Variance artifact guard**: H3 noiseless re-evaluation separates a real basin change from a lucky shot.
- **Stochasticity-vs-structure guard**: Arm 2 depolarizing control prevents over-claiming "structure" when
  any random kick would do.
- **Seed-locking**: pin `seed_transpiler` (README actionable #6) so routing artifacts don't masquerade as a
  noise effect.
- **Matched-strength discipline**: H2's depolarizing rate is calibrated to equal mean fidelity, not guessed.

---

## Relationship to the Strategic Frontier
This is the concrete first iteration of **README ORQ Priority 1 (Noise-as-Resource)**. It is intentionally
sequenced *after* Exp54 (warm-start) because warm-starting changes the trapped-subset T; Exp55 should use the
cold-start T to keep the noise channel as the sole manipulated variable, then optionally re-run on the
warm-start T as a robustness check.

*Harness reuse*: built on Elder's Exp53 `run_exp53_depth_vs_shots.py` infrastructure (per-seed checkpoint +
resume, transpiled evaluation, EDGES_20 loader). Only the noise-channel arm logic and the trapped-subset
gating are new.
