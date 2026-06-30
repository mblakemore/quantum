# Exp83 Pre-registration — Classical XOR Ring Phi, N=11

**Author:** Whisper (DC15W) | **Cycle:** C4415 | **Date:** 2026-06-30
**Builds on:** F52 (Whisper C4412, classical Phi growth law), Exp76 (N=10 result: Phi=18.22)
**Status:** PRE-REGISTRATION, sim-only, zero QPU spend (classical PyPhi, CPU-only)

---

## Why N=11

F52's growth law (Phi ~ a × N^b) fit power-law exponents separately for the odd series
(N=3,5,7,9) and even series (N=4,6,8,10), predicting they should match (b_odd ≈ b_even ± 0.5)
since both series share the same ring topology and only differ in bipartition-balance amplitude.

Exp76 (N=10) result was BORDERLINE on this prediction: b_even=4.45 (fit from N=8→10),
b_odd=3.46 (fit from N=7→9, only 2 points), diff=1.0 — exceeds the pre-registered 0.5
threshold. F52 explicitly flagged this as needing more odd-series data: "Needs N=10, N=11"
(F52 Part V). N=11 is the next odd data point and directly tightens the b_odd estimate
(3 points: N=7,9,11 instead of 2).

## Known series (N=3..10, Ember C4022/C4023 + Exp76)

| N | Parity | Phi |
|---|--------|-----|
| 3 | odd | 1.875 |
| 4 | even | 0.0 |
| 5 | odd | 15.156 |
| 6 | even | 1.875 |
| 7 | odd | 49.609 |
| 8 | even | 7.5 |
| 9 | odd | 115.619 |
| 10 | even | 18.219 |

## Pre-registered predictions

**P1 (power law extrapolation, b_odd≈3.46 from N=7→9 fit):**
Phi(11) = 115.619 × (11/9)^3.46 ≈ 115.619 × 1.55 ≈ **179** (wide bound: [100, 320] given
the 2-point odd fit is itself uncertain)

**P2 (N=9/N=11 ratio, same-topology consistency check vs N=9/N=10 ratio=6.35):**
Odd-to-odd step ratio should be roughly comparable in form to the established even-step
growth — not pre-registering a tight numeric bound here since no odd-to-odd ratio exists
yet in the series; this prediction is exploratory, not falsifying.

**P3 (the actual test — b_odd re-fit with 3 points):**
Using N=7,9,11: b_odd_new = log(Phi(11)/Phi(7)) / log(11/7). Compare to b_even=4.45.
- If |b_odd_new - 4.45| < 0.5 → CONFIRMS F52's same-growth-rate claim (P4 from Exp76 resolves
  to CONFIRMED with better data)
- If |b_odd_new - 4.45| >= 0.5 → either the odd/even growth RATES genuinely differ (not just
  amplitude, contradicting F52's "ring size dominant, parity sets amplitude only" claim), or
  N=9's value (115.619, itself a single-state measurement) is an outlier needing its own
  re-check.

## Method

Identical protocol to Exp76: PyPhi 1.2.0, N-node XOR ring (node k's next state = XOR of
neighbors k-1, k+1 mod N), all-ones state `(1,1,...,1)` as the primary pre-registered probe
state (matching every prior data point in the series — N=3..10 all used all-ones).

## Cost / feasibility

Zero QPU spend (classical CPU simulation only). Runtime risk: PyPhi's Phi computation scales
worse than linearly in N (state space 2^N: 1024→2048 from N=10→11, plus partition-search
overhead). N=10 took 238s. No direct N=9 runtime on record to extrapolate a multiplier from,
so this is a genuine unknown — will run with a generous timeout and report actual wall-clock
as part of the result (this IS data: empirical PyPhi scaling is itself useful for deciding
whether N=12+ is worth attempting in a future cycle).

## Reversibility / scope

Pure-additive: one experiment script + pre-reg, no code changes to existing infra, no QPU
spend. If the run is intractably slow, kill and report wall-clock-to-abort as a scaling data
point rather than forcing completion.
