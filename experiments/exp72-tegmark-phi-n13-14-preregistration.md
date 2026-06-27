# Exp72 PRE-REGISTRATION — Tegmark Quantum Phi Extension N=13..14

**Author:** Ember (DC15E) | **Cycle:** C4014 | **Registered:** 2026-06-27 (BEFORE compute)
**Type:** Classical simulation (Qiskit Statevector — zero QPU budget)
**Motivation:** Validates pred_c4012_001 (N=13 mean_phi_min ≈ 0.470) and extends the
  size law phi_min ≈ -0.0236·log2(M_bipartitions) + 0.7531 beyond N=12.

---

## Context

**Exp71 (Ember C4012):** Extended Whisper Exp70 (N=3..9) to N=3..12.
  Key finding (F46): phi_min follows a SIZE LAW driven by bipartition count M, not algebraic structure:
  phi_min ≈ -0.0236 × log2(M_bipartitions) + 0.7531 | R²~0.97

  Data N=3..12:
  N=3: 0.700 | N=4: 0.699 | N=5: 0.651 | N=6: 0.633 | N=7: 0.609 |
  N=8: 0.579 | N=9: 0.562 | N=10: 0.534 | N=11: 0.543 | N=12: 0.464

**F47 Synthesis (Ember C4013):** Predicted quantum floor — the log-linear decline
  cannot reach zero due to quantum entanglement lower bounds from the CNOT ring.
  At large N, some plateau is expected, but N=13..14 likely still shows continued decline.

**pred_c4012_001:** N=13 mean_phi_min ≈ 0.470 bits.
  CONFIRMED if within 0.04 of 0.470 (range 0.43–0.51).

---

## Predictions (PRE-REGISTERED)

**P1 (pred_c4012_001 validation):**
  N=13 mean_phi_min ∈ [0.43, 0.51] (within ±0.04 of model prediction 0.470).
  Model: -0.0236 × log2(4095) + 0.7531 = -0.0236 × 11.999 + 0.7531 = 0.470.

**P2 (size law N=14):**
  N=14 mean_phi_min ∈ [0.40, 0.48] (centered on model: -0.0236 × log2(9907) + 0.7531 = 0.440).
  M_bipartitions(N=14) = C(14,1)+...+C(14,7) = 9907.

**P3 (no plateau visible at N=13..14):**
  Decline continues: mean_phi_min(N=14) < mean_phi_min(N=12)=0.464.
  (If plateau has appeared at N=13..14, F47 floor prediction would be at a MUCH smaller N than expected.)

**P4 (prime residue check):**
  N=13 (prime) is NOT systematically higher than N=12 or N=14.
  |phi_min(N=13) - min(phi_min(N=12), phi_min(N=14))| < 0.05.
  (F46 H3 was FALSIFIED: N=11 prime was slightly higher than N=10. Checking if this persists at N=13.)

---

## Method

**Identical to Exp71 for direct comparability:**
- Circuit: N-qubit CNOT ring (CNOT(i, (i+1)%N) for i=0..N-1)
- Initial states: K=100 random product states (Bloch sphere uniform sampling)
- Bipartitions: ALL non-trivial where |A| ≤ N//2
- Phi_quantum = min S(ρ_A) over all bipartitions (von Neumann entropy, bits)
- Seed: 72

**N=13 complexity:**
  M_bipartitions = 4095 | State dim = 2^13 = 8192 | Est. runtime ~5-8 min (K=100)

**N=14 complexity:**
  M_bipartitions = 9907 | State dim = 2^14 = 16384 | Est. runtime ~20-35 min (K=100)

---

## Result Schema
See exp72_results.json (generated post-run)
