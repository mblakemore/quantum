# Exp195b PRE-REGISTRATION — BEAM THE POWER (clean readout) — Whisper C4887

**Committed before decode.** Follow-up to Exp195 (selftest-gated DEFER at C4886).

## Protocol (Hotta quantum energy teleportation)

H = h(Z_A+Z_B) + k·X_A X_B with h=1, k=1.5. Exact entangled ground |g⟩ (E = −2.5;
Bob-local share E_B = h⟨Z_B⟩ + k⟨X_A X_B⟩ = −1.7). Alice measures **X_A** (the coupling
basis — Z_A destroys the needed correlation, the C4886 lesson) → bit s, real feed-forward
(if_test) to Bob; Bob applies Ry(+2θ) if X_A=+1, Ry(−2θ) if X_A=−1, θ=0.17 (numeric optimum).

## What changed from Exp195 (why the gate now passes)

1. **LOCC bit / readout separation**: Alice's measurement writes c0 once and freezes
   X_A = 1−2s; ⟨X_A X_B⟩ reconstructed as ⟨(1−2s)·x_B⟩ with X_B read from q1. q0 never
   touched again in the qet arm.
2. **Conditioning sign corrected**: old s=0→Ry(−2θ) gives ΔE_B = **+0.297** (pays!);
   correct s=0→Ry(+2θ) gives **−0.1028**. This inversion is what the Exp195 selftest refused.
3. **noLOCC falsifier fixed**: no re-entangling of A after Bob's kick (old reset+re-prep CX
   scrambled Bob's state).
4. **Falsifier prediction corrected by exact numerics**: no-information arms give
   ΔE_B = **+0.0973** (positive — ground-state passivity: a local kick without the bit COSTS
   energy), not ~0 as Exp195's prereg assumed. Discriminator gap: −0.103 vs +0.097 ≈ 0.200.

## Pre-registered outcomes (ibm_fez, 8000 shots, 6 circuits)

- **PRIMARY**: ΔE_B(qet) < 0 at ≥5σ, band **[−0.15, −0.05]** (exact −0.1028).
- **FALSIFIERS**: ΔE_B(noLOCC) and ΔE_B(nomeasure) both **POSITIVE**, band **[+0.03, +0.17]**
  (exact +0.0973). The same feed-forward machinery driven by an uncorrelated coin, and the
  fixed kick, must both PAY energy while the informed kick extracts.

## Selftest (passed pre-flight, C4887)

Embedded exact statevector derivation (numpy-only, independent of qiskit) gives
ground −2.5000, baseline −1.7000, dE_qet −0.1028, controls +0.0973. Aer at 200k shots:
qet **−0.1056**, noLOCC **+0.0926**, nomeasure **+0.0931** — circuit reproduces the exact
derivation within tolerance. Ground-prep fidelity 1.000000 (Ry(3.7851)+CX, re-verified).

## Claim if it holds

Bob's lab loses energy it did not locally contain, paid for by pre-existing A–B ground-state
correlations, delivered by a 1-bit classical message — with the in-shot proof that the
identical kick minus the information moves energy the OTHER way. 5th flight of the
teleportation lineage; first where the teleported quantity is energy.
