# Finding — Exp151: a discrete time crystal signature on ibm_fez ("a clock nothing set")

**Cycle**: C4839 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dhehphtsac739d2qfg`
**Setup**: driven disordered chain, L=6, imperfect π-pulse θ=π(1−ε), ε=0.12; 2 arms × t=0..12 periods, 4000 shots.
Seeded single disorder realization (J couplings, h fields fixed). New exotic-phases museum wing (Creator "fly it").

## The claim, scoped up front
A discrete time crystal (DTC) ticks at **half** the drive frequency and stays locked there even when the
drive is detuned. The self-verifying discriminator is the rectified period-2 amplitude **A(t) = (−1)ᵗ⟨Z(t)⟩**:
- **Control** (pulse only, no interactions): A(t) = cos(πεt) — the imperfection accumulates and the
  oscillation **beats to a null** at t ≈ 1/(2ε) ≈ 4.
- **DTC** (interactions + strong on-site disorder → many-body localization): A(t) stays **rigid** through
  that null — the subharmonic is locked.

The honest claim is the **contrast at the first beat-null**, where the non-interacting chain collapses and
the crystal does not. Not a thermodynamic-limit proof; a hardware signature of the DTC phase.

## Result — signature PRESENT on hardware

| t | A_dtc | A_ctl | contrast |
|---|-------|-------|----------|
| 0 | 0.996 | 0.995 | 0.001 |
| 2 | 0.863 | 0.720 | 0.143 |
| 3 | 0.778 | 0.411 | 0.366 |
| **4 (null)** | **0.775** | **0.064** | **0.711** |
| 5 | 0.682 | −0.312 | 0.370 |
| 8 | 0.578 | −0.979 | −0.401 |
| 12 | 0.376 | −0.189 | 0.186 |

**Beat-null window (t=3,4,5): DTC holds 0.745, control collapses to 0.262 → rigidity contrast 0.482.**
At the exact moment the imperfect drive drove the non-interacting chain to zero, the crystal was still
ticking at 0.775. That rigidity — robustness of the subharmonic to a 12% drive detuning — is the DTC
signature, measured on real silicon.

## Two things worth noting
1. **It held better than the noise model predicted.** The DTC amplitude decayed 0.996 → 0.376 over 120
   two-qubit gates (t=12), where the measured-noise feasibility model predicted ≈0.12. The many-body
   localization that rigidifies the subharmonic also suppresses heating of the observable — the phase is
   partly self-protecting. A measure-beat-predict in the honest direction (cf. Exp146).
2. **The late-time crossover is a disclosed asymmetry, not a failure.** Past t≈6 the control's beat
   *revives* (|A| → 0.98 at t=8) while the DTC keeps slowly decohering, so the raw contrast goes negative.
   This is expected and was flagged pre-flight: the control has **zero** two-qubit gates (interactions off),
   so it barely decoheres, while the DTC pays the full gate cost. The clean claim lives at the first
   beat-null (t≈3–5); the late-time DTC decay is the finite-coherence fence made visible.

## Fences (headline-level)
- Finite chain (L=6), finite coherence — a **signature** of the DTC phase, not a thermodynamic-limit proof.
- Single seeded disorder realization; the phase is a disorder-averaged concept — this is one instance.
- The control is not gate-matched (it has no interactions, hence no 2q gates). The first-null contrast is
  valid regardless (it tests robustness to drive imperfection at fixed shallow depth), but a **gate-matched
  control** — a non-localizing interacting chain at the same 2q count — is the clean next rung (Exp151b) and
  would let the comparison extend honestly to late times.

## Gates (passed pre-flight)
Truth-gate (noiseless): control beats to 0.063 at the null, DTC holds 0.811 (contrast 0.748); falsifiability
fires (interactions-off reproduces the control — the crystal is the interactions, not the pulse). Feasibility
under measured noise: first-null contrast 0.49 predicted readable. Transpile dry-run: t=4 depth 99 / 40 CX.

## Museum
First exhibit of a new **exotic-phases** wing: "The Time Crystal — a clock nothing set." The rigid-vs-beat
contrast at the null is the interactive aha; the disclosed late-time decay and the gate-matched-control note
are the honest fence built into the exhibit.
