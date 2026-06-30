# Exp81 Pre-Registration — "Dodge the noise using the map": noise-aware qubit placement

**Author:** Elder (DC15) | **Cycle:** C6272 | **Date:** 2026-06-30 | **Backend:** ibm_marrakesh
**Script:** `scripts/run_exp81_noise_dodge_placement.py`
**Creator ask:** "if we know where the noise is, maybe we can get by it." Turn that into a hardware number.

## Question
Does placing the QQQ tail-prob loader (Exp78) on the calibration-map's QUIETEST qubits shrink the
hardware bias vs the NOISIEST qubits? This is the one noise lever that works — route AROUND noise
(placement), not subtract it (mitigation, which failed: F7).

## Design
- Reuse the validated Exp78 loader (genuine lognormal QQQ dist → P(top bit=1)=P(S_T>K)), RECENTERED to
  K=752 so a_true≈0.246 (NOT ~0.48 — near 0.5 the bias is invisible, the fixed-point trap). Sim-validated:
  a_discrete=0.2463, noiseless P(MSB=1)=0.2500.
- Live noise map: ibm_marrakesh readout error spans 0.0029..0.50 (171×); 2q error 0.001..1.0.
- Three arms (forced initial_layout for BEST/WORST; plain transpile for DEFAULT), objective qubit
  (virtual q2=MSB, answer=P(MSB=1)) placed on the path's best/worst readout qubit. 8192 shots, test-retest.

## Pre-registered prediction (frozen before HW)
- **|bias(BEST)| ≪ |bias(WORST)|** — the map buys a lot (171× readout spread; the worst readout ≈0.5
  randomizes the answer toward 0.5 → bias ≈ +0.25).
- **|bias(BEST)| > 0** — you get BY the noise, not PAST it. Placement is a constant-factor dodge; it does
  NOT move the depth wall. This is the honest bound on the whole "dodge" idea.
- **DEFAULT ≈ BEST** is plausible IF modern transpile is already noise-aware (an honest "the tool does it
  for you" outcome) — reported, not assumed.

## Honesty bounds
- N=1 instance/strike/backend; the bias DIRECTION and the BEST-vs-WORST CONTRAST are the content.
- Pure placement (no post-hoc subtraction) — keeps it a "dodge," not "mitigation."
- Reversibility: pure-additive (script + this pre-reg + result JSON). No existing file modified.
