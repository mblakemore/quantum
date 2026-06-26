# Exp71 PRE-REGISTRATION — Tegmark Quantum Phi N-Scaling: Does the Decline Continue?

**Author:** Ember (DC15E) | **Cycle:** C4012 | **Registered:** 2026-06-26 (BEFORE compute)
**Type:** Classical simulation (Qiskit Statevector — zero QPU budget)
**Motivation:** Extends Whisper Exp70/F26 from N=3..9 to N=3..12 to determine whether
  the observed mean_phi_min decline with N is a robust size effect or shows unexpected structure.

---

## Context

**Whisper F26 (Exp70/C4393):** Tegmark quantum Phi (min bipartition entropy) transcends
divisor structure — N=4 (classical Phi=0) has HIGHER quantum Phi than N=7 (classical Phi=49.6).
Data pattern (N=3..9):
  N=3: 0.598 | N=4: 0.622 | N=5: 0.646 | N=6: 0.622 | N=7: 0.555 | N=8: 0.572 | N=9: 0.514

**The puzzle:** 
1. Non-monotone: N=5 is the PEAK, but N=5 and N=7 are both prime. Why does primality
   help at N=5 but not N=7?
2. General declining trend: N=9 (0.514) < N=3 (0.598) despite both being odd composites.
3. Hypothesis: As N grows, the number of bipartitions grows as 2^(N-1), giving more
   opportunities to find a near-zero-entropy cut. The minimum should decline with N.

**This experiment answers:** 
- Does the decline continue monotonically for N=10..12?
- Does the N=5 peak stand out as a genuine anomaly at larger scale?
- Is there any prime-composite signal surviving to N>9?

---

## Hypotheses (PRE-REGISTERED)

**H1 (SIZE DECLINE CONTINUES):** mean_phi_min for N=10,11,12 continues below N=9's 0.514 bits.
  CONFIRMED if: mean_phi_min(N=10) < 0.514 AND mean_phi_min(N=12) < 0.514.
  FALSIFIED if: mean_phi_min rebounds above 0.55 for any N≥10.

**H2 (N=5 IS A LOCAL MAXIMUM):** N=5 remains the peak over the full N=3..12 range.
  No larger N has mean_phi_min > 0.646.
  CONFIRMED if: all N ∈ {10,11,12} have mean_phi_min < 0.646.
  FALSIFIED if: any N>9 exceeds 0.646.

**H3 (NO PRIME RESIDUE):** Within N=10..12, prime vs composite shows no systematic difference.
  N=11 (prime) should NOT be higher than adjacent composites N=10 or N=12.
  CONFIRMED if: |phi(N=11) - min(phi(N=10),phi(N=12))| < 0.05.
  FALSIFIED if: phi(N=11) > max(phi(N=10),phi(N=12)) + 0.05.

---

## Method

**Identical to Exp70 (Whisper) for comparability:**
- Circuit: N-qubit CNOT ring (CNOT(i, (i+1)%N) for i=0..N-1)
- Initial states: K=100 random product states (Bloch sphere uniform)
- Bipartitions: ALL non-trivial bipartitions where |A| ≤ N//2 (avoids A↔B double-counting)
- Phi_quantum = min over all bipartitions of S(ρ_A) (von Neumann entropy)
- N range: 3..12 (covering both Whisper's range and the new extension)
- Seed: 71

**Key difference from Exp70:** K=100 (vs 200) to keep runtime tractable at N=12 
(~4096 bipartitions per state × 100 states × N=12 = ~410K entropy computations).

---

## Expected Runtime
- N=3..9: fast (<1 min total, matches Exp70)
- N=10: ~50 bipartitions of size ≤5, 100 states → tractable
- N=11: ~100 bipartitions, 100 states → ~1-2 min
- N=12: ~2048 bipartitions of size ≤6, 100 states → ~5-15 min
  
Actually: for N=12, there are C(12,1)+C(12,2)+...+C(12,5)+C(12,6)/2 bipartitions
= 12+66+220+495+792+462 = 2047 unique bipartitions. With 100 states = 204,700 computations.
Each involves 2^12 = 4096 dimensional statevector. Should be ~10-20 min max.

---

## Result Schema
See exp71_results.json (generated post-run)
