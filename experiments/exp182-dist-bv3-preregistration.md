# Exp182 Pre-registration — THE SCALING LAW: n=3 distributed BV (per-gate cost at three doses)

**Cycle**: C4870 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 20 circuits
**Upgrades**: Exp181's single ratio (2nd gate = 3%) into a measured scaling law — the same
anecdote→dose-response move as Exp175→176. Creator go: general#24.

## The question

Is the per-teleported-gate cost a **constant**? n=3 BV gives 8 hidden strings spanning Hamming
weight w = 0, 1, 2, 3 teleported oracle gates. If P(correct | w) ≈ P₀·r^w with one fixed r,
distributed computation has a *law* (and an extrapolation license: r¹⁰ prices a 10-gate oracle).
If r degrades with w, resource scale (3 simultaneous e-bits, 10 qubits, heavy-hex routing
congestion) breaks the near-free composition — equally worth knowing, named in advance.

## Arms (zero-feedforward architecture throughout, as Exp181)

| arm | strings | circuits | purpose |
|-----|---------|----------|---------|
| local | all 8 | 8 | monolithic ceiling |
| **dist** | all 8 | 8 | the scaling measurement |
| noresource | weight representatives 000, 001, 011, 111 | 4 | falsifier floors (weight-determined by symmetry: ≈ 1, 0.5, 0.25, 0.125 × clean bits) |

10 qubits: data q0–q2, ancilla q3, e-bits (q4,q5), (q6,q7), (q8,q9). Decode as Exp181
generalized: s_i = m_i ⊕ (z_i if gate_i). Corrections defer identically (X → global phase on
|−⟩; Z → decode XOR) — the algebra is n-independent, selftest must reprove it exactly at n=3.

## Pre-registered predictions

- **Primary**: dist beats noresource at ≥3σ in every weight class (w=1,2,3) AND the modal
  decoded string is the programmed string **8/8**.
- **Scaling law test**: successive per-gate ratios r₁=P̄₁/P̄₀, r₂=P̄₂/P̄₁, r₃=P₃/P̄₂ (P̄_w =
  weight-class mean) mutually consistent within 2σ → constant-cost law; report r̂ (pooled
  log-linear fit) and the extrapolation r̂¹⁰. **Band: r̂ ∈ 0.93–0.99.** If ratios degrade
  monotonically beyond 2σ → resource-scale interaction (named suspects: routing congestion at
  10 qubits, simultaneous e-bit prep crosstalk).
- **Bands** (per the C4869 calibration rule — priced from per-CX error, wide for the first
  10-qubit flight): local all strings 0.85–0.99 · dist P̄₀ 0.90–0.99, P̄₁ 0.84–0.97, P̄₂
  0.78–0.95, P₃ 0.72–0.93 · noresource w=1 0.42–0.56, w=2 0.19–0.31, w=3 0.09–0.17.
- **Cross-experiment note** (informational): Exp181's n=2 ratio 0.971 should be consistent with
  r̂ if conditions are comparable; divergence is a conditions datum, not a contradiction
  (within-job comparisons remain the claims).

## Discipline

ps aux: clean. Claim: exp182 (whisper C4870). Ledger prediction pre-submit. Prereg committed
before decode. Selftest gates: local & dist exact 1.000 on all 8 strings; noresource
representatives ≈ 1.0 / 0.5 / 0.25 / 0.125.
