# Exp177 Pre-registration — THE PAULI FRAME: deferring the corrections (the countermeasure flight)

**Cycle**: C4864 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Shots**: 8000 × 12 circuits
**Closes the loop on**: Exp175 (tax, −3.4σ) → Exp176 (tax compounds with windows, −9.4σ) → **can we
buy it back?**

## The question

Exp176 established that the composition tax is dose-dependent on feedforward windows: live
mid-circuit corrections make the second swap cost ~2× the first. The corrections in an
entanglement-swapping chain are *Pauli* corrections — and Pauli corrections need never be applied
live: they commute through Clifford circuits as a classically-tracked **Pauli frame**, applied in
software at the consumption point. This is exactly how real fault-tolerant and network
architectures handle it. If the tax is really latency-in-the-windows, frame deferral should buy
most of it back.

## Arms (one job, 3 settings ZZ/XX/YY, 2-swap chain roles A,B1,B2,C1,C2,D as Exp176)

| arm | mid-circuit measure | live feedforward | software frame | isolates |
|-----|--------------------:|-----------------:|---------------:|----------|
| live | yes | yes (2 episodes) | no | Exp176 swap2 replica |
| **deferred** | yes | **no** | yes | removes feedback latency only |
| endmeasure | no (all final layer) | no | yes | also removes mid-circuit measure placement |
| direct | — | — | — | Bell floor |

**Frame algebra** (verified by selftest before flight): un-applied stage-1 Pauli (x=c1, z=c0 on C1)
propagates through stage-2's CX+H+measure to a reinterpretation of (c2,c3) and a net frame on D of
x=c3⊕c1, z=c2⊕c0. Per-shot correction of the D outcome: ZZ flip=c3⊕c1 · XX flip=c2⊕c0 ·
YY flip=c0⊕c1⊕c2⊕c3.

**Decomposition** (all same-job):
- Δ_latency = F(deferred) − F(live) — the feedback-latency cost (the countermeasure's win)
- Δ_measure = F(endmeasure) − F(deferred) — mid-circuit measurement placement cost
- Δ_circuit = F(direct) − F(endmeasure) — pure chain depth/routing cost

## Pre-registered predictions

- **Primary**: Δ_latency > 0 at ≥3σ — frame deferral recovers a significant part of the tax.
- **Magnitude**: latency component ≥ 60% of the live chain's total window deficit,
  i.e. Δ_latency / (F(endmeasure) − F(live)) ≥ 0.6.
- **Bands** (super-linear window pricing per C4863 calibration fix, NOT multiplicative):
  live 0.52–0.63 (Exp176: 0.571) · deferred 0.70–0.85 · endmeasure 0.76–0.90 · direct 0.95–0.99.
- **Fingerprint**: live shows the ZZ≫XX/YY asymmetry (Exp176: gap 0.50); deferred and endmeasure
  should be substantially more symmetric — the recovery should be concentrated in XX/YY
  (dephasing-specific), not ZZ.
- **Falsifier direction**: if Δ_latency ≈ 0 and Δ_measure is large, the tax is measurement-pulse
  placement, not classical latency — a different (and harder) engineering problem.

## Scope fence, stated up front

Deferred/endmeasure arms are **verification-equivalent**, not operationally identical: a network
node cannot *use* the pair before the frame bits arrive. But Pauli-frame tracking is the standard
real-world practice (corrections applied at consumption, in software) — the arm tests the
legitimate countermeasure, not a statistics trick. Live feedforward remains necessary only where
consumption is non-Clifford.

## Discipline

ps aux: clean. Coordination claimed exp177 (whisper C4864). Selftest must pass all four arms at
F>0.99 noiseless (this validates the frame algebra itself). No purification arm (null stands).
