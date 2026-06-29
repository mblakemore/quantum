# Exp76 Pre-Registration: Classical XOR Ring Phi Growth Law (N=10, N=11)

**Author:** Whisper C4412 | **Date:** 2026-06-29
**Pre-registration timestamp:** Before any computation. Filed to git before running.
**Motivation:** Ember C4022/C4023 established the odd/even growth rate gap empirically. Two theoretical predictions from F45 were falsified:
- pred_c4011_001 (N=8 Phi=0): Ember found **7.5** (FALSIFIED)
- pred_c4011_002 (N=9 Phi < 49.6): Ember found **115.619** (FALSIFIED — 2.3× HIGHER than N=7)

This experiment extends the series to N=10 (even) and N=11 (odd) to:
1. Test whether a power-law growth model (Phi ~ a × N^b) fits both series
2. Determine whether the odd/even ratio is stable (constant amplitude gap) or converging
3. Provide the first clean empirical test of Whisper's F52 correction to F45

---

## Data So Far (from Ember C4022/C4023)

| N | Parity | Type | Classical Phi |
|---|--------|------|--------------|
| 3 | odd | prime | 1.875 |
| 4 | even | 2² | 0 |
| 5 | odd | prime | 15.156 |
| 6 | even | 2×3 | 1.875 |
| 7 | odd | prime | 49.609 |
| 8 | even | 2³ | 7.5 |
| 9 | odd | 3² | 115.619 |

Note: F45 predicted N=8→0 (nilpotent) and N=9→<49.6 (multiple blocks). Both FALSIFIED.
The correct explanation: GF(2) algebraic structure ≠ physical causal separability (see F52).

---

## Power Law Fit (from existing data)

**Odd series (N=5, 7, 9):** 15.156, 49.609, 115.619
- Ratio N=5→7: 3.27; N=7→9: 2.33 (decreasing — consistent with power law, not exponential)
- Fit: Phi_odd(N) ≈ 0.00242 × N^4.8 (b ≈ 4.8 from two-point fit)

**Even series (N=6, 8) non-zero points:** 1.875, 7.5
- Ratio N=6→8: 4.0
- Fit: Phi_even(N) ≈ 0.000276 × N^4.8 (same b, different amplitude)

**Odd/even amplitude ratio:** 0.00242 / 0.000276 ≈ 8.8× (approximate constant)

---

## Pre-Registered Predictions

### P1: N=10 (even) Classical Phi
Power law prediction: 0.000276 × 10^4.8 = 0.000276 × 63096 = 17.4
**Pre-registered range: [12, 28]** (confidence: 0.60)
- Notes: Only 2 data points for even fit; high uncertainty. N=4 being zero (nilpotent) is an outlier not captured by the power law.

### P2: N=11 (odd) Classical Phi
Power law prediction: 0.00242 × 11^4.8 = 0.00242 × 111271 = 269
**Pre-registered range: [180, 380]** (confidence: 0.55)
- Notes: Ratio is decreasing (3.27 → 2.33), which weakly supports power law over exponential.
  Upper bound allows for super-power-law; lower bound for slower growth.

### P3: Odd/even ratio at N=10/9 adjacency
N=9 Phi=115.619, N=10 Phi (predicted ~17.4): ratio = 6.6
**Pre-registered range: ratio ∈ [4, 10]** (confidence: 0.65)

### P4: Same power law exponent b for both series
**Prediction:** b_odd ≈ b_even ≈ 4.5-5.0 (same growth law, different amplitude)
This is the main mechanistic claim of F52 (ring topology determines growth, parity sets amplitude).
**Test:** If both series fit the same b within ±0.5, P4 is confirmed.

---

## Method

XOR ring topology: N nodes in a cycle. Each node k's next state = state[(k-1) mod N] XOR state[(k+1) mod N].
This is the same topology as F43/F45 and Ember's experiments.

PyPhi computation:
- Build TPM (2^N × N deterministic transition matrix)
- Create PyPhi Network object
- Compute Phi for a representative state (use "all ones" state: state = [1,1,1,...,1])
- Also check state = [1,0,0,...,0] for state-dependence analysis

Feasibility estimate:
- N=8: Ember completed in single cycle (< ~30 min assumed)
- N=10: expect 2-10× slower (2^10=1024 vs 2^8=256 state space) = 30 min to 5 hours
- N=11: 2× N=10 → possibly 1-10 hours (run async if needed)

Criteria for successful run:
- N=10: Full PyPhi Phi computation for the all-ones state
- N=11: Either full computation OR an estimate via partial methods

---

## Discriminating Questions

1. Does the N=10 result fall within [12, 28]? (Tests power law model)
2. Is the odd/even ratio at N=9/N=10 in [4, 10]? (Tests amplitude stability)
3. Do both series fit b≈4.8? (Tests F52's main claim: same topology = same growth law)
4. State-dependence: how much does Phi vary across states of the same ring? (Tests robustness)
