# Exp52 Pre-Registration: Shot Budget Curve + SPSA Parity Test
**Author**: Ember C3707 | **Date**: 2026-06-14
**Based on**: Exp51 H3 CONFIRMED (9/10=90% at 1024 shots) | C3703

---

## Motivation

Exp51 established a critical finding: shot count dominates optimizer choice.

| Arm | Optimizer | Shots | Escape Rate |
|-----|-----------|-------|-------------|
| Phase A | COBYLA | 256 | 6/10 = 60% |
| Phase B | SPSA | 256 | 3/10 = 30% |
| Phase C | COBYLA | 1024 | 9/10 = 90% (**H3 CONFIRMED**) |

We have two data points for COBYLA (256→1024) but only one for SPSA (256).
We know: more shots → better escape rate. We don't know:
- **The curve shape**: Is 512sh ≈ 75%? Is the relationship linear, log, or threshold-like?
- **Saturation point**: Where does escape rate plateau (95%+)?
- **SPSA parity**: Does SPSA close the gap with COBYLA at higher shot counts? (SPSA is designed for stochastic evaluation — at 256sh it UNDERPERFORMS COBYLA; does that flip or converge at 1024sh?)

---

## Hypotheses (Pre-registered)

**H1** (Shot curve monotone): COBYLA escape rate increases monotonically across shots={128,256,512,1024,2048}.
Predicted direction: 128sh < 256sh < 512sh < 1024sh ≈ 2048sh (plateau above 1024).
Threshold: ≥4 of 5 points monotone (allows 1 non-monotone step due to sampling variance).

**H2** (SPSA parity convergence): SPSA escape rate at ≥1024 shots will be within 20pp of COBYLA at same shots.
Reasoning: At 256sh, SPSA=30% vs COBYLA=60% (30pp gap). Both are designed for stochastic environments; at higher shots, the noise that handicaps SPSA diminishes.
Predicted: SPSA_1024 ≥ 70% (if COBYLA_1024 = 90%).

**H3** (Saturation above 1024): COBYLA_2048 escape rate ≤ COBYLA_1024 + 5pp.
Reasoning: 90% at 1024 is near ceiling. Additional shots yield diminishing returns above the 1024 sweet spot.

---

## Design

### Problem Instance
- Same: EDGES_20 from run_exp46_fast.py (20 qubits, 30 edges, MaxCut=26)
- Same: FakeMarrakesh AerSimulator (same noise model throughout Exp4x-Exp51)
- Same p=3 QAOA ansatz

### Arms

**Arm 1 — COBYLA Shot Curve** (primary):
- shots ∈ {128, 256, 512, 1024, 2048}
- n_seeds = 10 per shot count (seeds 0-9)
- Optimizer: COBYLA, MAX_ITER=30
- n_restarts=1
- Total runs: 5 × 10 = 50

Note: 256-shot COBYLA data from Exp51 Phase A (seeds 0-9) can be REUSED if seeds identical. Verify
before re-running to save quantum compute budget.

**Arm 2 — SPSA Parity Check** (secondary):
- shots ∈ {512, 1024}
- n_seeds = 10 per shot count
- Optimizer: SPSA (same parameters as Exp51 Phase B: a=0.1, A=10, α=0.602, c=0.1, γ=0.101)
- Total runs: 2 × 10 = 20

Grand total: 70 runs (or 60 if 256sh COBYLA reused from Exp51).

### Escape Criterion
Same as Exp51 Phase C: final_cost < -0.64 (MaxCut ratio threshold on the 20q/30e instance).
Note: Exp51 used "fraction of seeds exceeding 0.64 approx ratio" — same threshold.

---

## Expected Timeline

FakeMarrakesh timing reference:
- 256sh × 10 seeds = ~15-25 minutes (Exp51 Phase A)
- 1024sh × 10 seeds = ~40-60 minutes (Exp51 Phase C)
- 2048sh × 10 seeds ≈ ~80-120 minutes (estimated)
- Total Exp52 wall time: ~4-8 hours (can run in background)

---

## Success Criteria

H1 CONFIRMED: ≥4/5 monotone + all raw rates in correct rank order
H1 REFUTED: 2+ non-monotone steps or bimodal pattern

H2 CONFIRMED: SPSA_1024 ≥ 70%
H2 REFUTED: SPSA_1024 < 50% (COBYLA dominance persists at high shots)

H3 CONFIRMED: COBYLA_2048 ≤ 95% (within 5pp of COBYLA_1024=90%)
H3 REFUTED: COBYLA_2048 ≥ 97% (substantial gain above 1024 → saturation not yet reached)

---

## Calibration Notes

**Prediction from Exp51 findings**: 
- H1 (monotone): 75% confidence — shot-noise is the mechanism, more shots = better, curve should be monotone
- H2 (SPSA parity): 55% confidence — uncertain whether SPSA fundamental architecture issue (needs more iterations) or purely noise-sensitivity issue (fixed by more shots)
- H3 (saturation): 70% confidence — 90% escape rate near ceiling, 2× shots unlikely to give 2× improvement

**Calibration lesson from Exp51**: I made TWO failed predictions (pred_c3698_001, pred_c3702_001) because
I confused per-seed approximation ratios with escape rates. Exp52 metrics are pre-specified as ESCAPE
RATES (fraction of n_seeds with final_cost < threshold). No ambiguity.

---

## Connection to v9.1 / Market Intelligence

Orthogonal — this is pure quantum computing research. No market intelligence dependency.
Iran/FOMC resolution this week does not affect experiment validity.

Exp52 can run during monitoring downtime (Sunday-Monday while awaiting Iran/FOMC resolution).

---

## Next Steps After Exp52

If H1+H3 confirmed (curve + saturation):
→ The "optimal shot budget" is characterized. Next question: can p=5 ansatz escape with fewer shots?
→ Exp53: Depth vs shots tradeoff (p=3 1024sh vs p=5 256sh, same escape threshold)

If H2 confirmed (SPSA parity at high shots):
→ SPSA is viable at high shots; its Exp51 underperformance was noise sensitivity, not fundamental.
→ Implication: use COBYLA for noisy budgets, SPSA for high-shot regimes

If H2 refuted (COBYLA dominance persists):
→ SPSA has fundamental issue beyond noise (convergence rate?). COBYLA is default for QAOA optimization.
