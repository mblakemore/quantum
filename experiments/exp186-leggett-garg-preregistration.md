# Exp186 Pre-registration — THE PRESENT WITH NO DEFINITE PAST: Leggett–Garg with ideal negative-result measurement

**Cycle**: C4876 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 6 circuits
**Class**: foundations (Leggett & Garg 1985; Knee et al. 2012 INRM form). Creator go:
ship-computer general#92.

## The question

Macrorealism says a system always *has* a definite value Q = ±1, and you could in principle
find out without disturbing it. Then the two-time correlators of any dynamics obey
**K₃ = C₁₂ + C₂₃ − C₁₃ ≤ 1**. A qubit evolving by U = Ry(π/3) per interval, measured in Z,
predicts C₁₂ = C₂₃ = +½, C₁₃ = −½ → **K₃ = 3/2**: the qubit does not possess a definite value
between looks — the present has no definite past.

## The clumsiness loophole, addressed (the design's core)

A macrorealist's escape: "your t₂ measurement *disturbed* the system." We use Knee-style
**ideal negative-result measurement** for C₂₃, the only correlator needing a mid-time look:
- plus-circuit: ancilla couples (CX) **only if Q₂ = −1**; keep rounds where the ancilla did
  NOT flip → those rounds learned Q₂ = +1 from a detector that provably never interacted.
- minus-circuit: X-conjugated coupling (fires only if Q₂ = +1); kept rounds learned Q₂ = −1
  non-invasively. Estimator: C₂₃ = Σ_kept₊ Q₃/N₊ − Σ_kept₋ Q₃/N₋.
C₁₂ and C₁₃ need no mid-time measurement at all (Q₁ = +1 deterministically from |0⟩).

## Circuits (6)

| circuit | what |
|---------|------|
| c12 | U, measure — C₁₂ = ⟨Q₂⟩ |
| c13 | U, U, measure — C₁₃ = ⟨Q₃⟩ |
| c23_plus / c23_minus | the INRM pair |
| c13_deph | c13 with a dephasing CX at t₂ — **the macroreal control**: decoherence restores the classical Markov value C₁₃ = +¼ → K₃(deph) = ¾ ≤ 1 |
| c23_invasive | projective mid-time measurement, both branches kept — the clumsiness audit |

## Pre-registered predictions

- **Primary**: K₃ (with INRM C₂₃) > 1 at ≥5σ. Band **1.30–1.48** (ideal 1.50; shallow 1q
  circuits, so decoherence cost small; se_K ≈ 0.02).
- **Correlator bands**: C₁₂ ∈ +0.42..+0.52 · C₂₃ ∈ +0.40..+0.52 · C₁₃ ∈ −0.52..−0.40.
- **Macroreal control**: K₃(deph) = C₁₂ + C₂₃ − C₁₃(deph) ∈ **0.62–0.88** (ideal 0.75), UNDER
  the bound — kill the coherence and the macrorealist description works again.
- **Clumsiness audit**: |C₂₃(INRM) − C₂₃(invasive)| < 0.06 — quantum mechanics says the
  invasive and non-invasive protocols agree; a disturbance-based macrorealist excuse predicts
  they differ.
- **INRM bookkeeping gauge**: kept-fraction sum N₊/N + N₋/N ∈ 0.95–1.05.

## Fences

Single transmon + ancillas on one die; INRM addresses the clumsiness loophole at the standard
(Knee et al.) level — a macrorealist can still retreat to conspiratorial disturbance
(acknowledged; that retreat also has to explain the invasive/INRM agreement). Q₁ is
deterministic by preparation (standard economy, not a loophole: macrorealism must hold for
every preparation). θ = π/3 is the quantum-optimal working point, stated in advance.

## Discipline

ps aux: clean. Claim: exp186 (whisper C4876). Ledger prediction pre-submit. Prereg committed
before decode. Selftest gates: K₃ = 1.50 ± 0.03; deph K₃ = 0.75 ± 0.03; INRM = invasive ±
0.03; kept-sum = 1.00 ± 0.02. Method-rule checklist (C4875 lesson) applied: all criteria are
ratios/differences of same-job quantities or theorem constants — no absolute bars that absorb
circuit overhead.
