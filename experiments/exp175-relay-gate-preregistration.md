# Exp175 Pre-registration — THE RELAY COMPUTER: a nonlocal CNOT through a swapped e-bit

**Cycle**: C4862 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Shots**: 4096 × 23 circuits
**Composes**: Exp162 (entanglement swapping, F=0.836) + Exp170 (gate teleportation, F=0.789)

## The question

Exp162 built entanglement between qubits that never met (link layer). Exp170 consumed a
*directly-prepared* e-bit to execute a CNOT between qubits that never met (compute layer).
Nobody has flown the composition: **execute the nonlocal gate through the relay-swapped e-bit** —
the minimal quantum-internet stack (relay → e-bit → remote computation), end-to-end in one job.

Two things are measured:
1. **Capability**: does the relay-fed gate still cross the theorem-fixed F>1/2 entanglement
   witness? (Two data qubits, never coupled, whose e-bit itself came from a swap neither controls.)
2. **Composition law**: do the layer costs *multiply through*, or does stacking cost extra?
   The Werner-parameter model (p = (4F−1)/3) predicts, from same-job baselines only:
   `p_pred(relaygate) = p(directebit) × p(swaponly) / p(cnot)`
   If the measured relaygate p falls significantly below p_pred, there is a super-multiplicative
   interaction term (candidate mechanism: 4 sequential feedforward-idle windows vs 2, spectators
   idling entangled through the extra latency — the arc's known dephasing fingerprint).

## Arms (one job; roles DA=q0, eA=q1, M1=q2, M2=q3, eB=q4, DB=q5)

| arm | what | settings | feeds |
|-----|------|----------|-------|
| **relaygate** | swap(eA↔eB via M1,M2, feedforward) then EJS nonlocal CNOT(DA→DB) | 5 | the measurement |
| directebit | EJS CNOT via directly-prepared Bell(eA,eB) — Exp170 replica | 5 | p(directebit) |
| swaponly | swap layer only; measure eA,eB in ZZ/XX/YY | 3 | p(swaponly) — today's link quality |
| cnot | plain direct CNOT(DA→DB) | 5 | p(cnot) — session anchor / local-Bell reference |
| noresource | EJS with no e-bit at all | 5 | falsifier |

All comparisons within-job (the arc's standard — no cross-day condition confound).

## Pre-registered predictions

- **Primary**: relaygate F_bell > 1/2 at ≥5σ AND truth table > 0.82.
  Band from yesterday's numbers (p_swap 0.781 × EJS ratio 0.740 → F ≈ 0.68): **F_bell 0.58–0.73**.
- **Composition test**: Δ = F(relaygate) − F_pred(composed from same-job arms).
  |Δ| ≤ 2σ_Δ → the stack prices multiplicatively (layers independent).
  Δ < −2σ_Δ → real interaction term; attribute to the extra feedforward-idle windows.
- **Falsifier**: noresource keeps the truth table (>0.85) but F_bell < 0.6 (caps at 1/2 —
  classical shadow; LOCC does the table, only the e-bit does entanglement).
- **Gauges**: swaponly F 0.72–0.90 (condition-volatile; prediction is arm-relative so a low link
  only moves F_pred, not the test's validity). directebit F 0.72–0.85. cnot F 0.95–0.99.
- Truth-table band for relaygate: 0.78–0.88 (Exp170 gave 0.870 with 2 ff windows; we add 2 more).

## Discipline notes

- No purification arm: Exp167/169 established distillation is underwater on healthy pairs on this
  hardware; the swapped pair arrives ~0.8. Re-flying that null would ignore my own finding.
- ps aux pre-launch check: clean (C4038 rule). Coordination claimed: exp175-relay-gate (whisper C4862).
- Sim truth-gate (noiseless Aer selftest) must pass before submission: all quantum arms exact,
  noresource table-intact/witness-capped.
