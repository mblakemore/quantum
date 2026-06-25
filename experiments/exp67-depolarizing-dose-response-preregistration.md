# Exp67 PRE-REGISTRATION — Depolarizing Noise Dose-Response for Warm-Start Granular Escalation

**Author:** Ember (DC15E) | **Cycle:** C3982 | **Registered:** 2026-06-25 (BEFORE any compute)
**Type:** Simulation only (local CPU, FakeMarrakesh-style depolarizing noise model)
**Resolves:** pred_c3981_001 mechanism hypothesis (anti-contraction: unital vs non-unital test)
**Extends:** Exp66 Finding 42 (anti-contraction: noiseless capk 0.5236 < FakeMarrakesh 0.5625)

## Motivation

Finding 42 (Exp66, C3981) showed an unexpected result: warm-start granular escalation performance is
BETTER under FakeMarrakesh noise than in the noiseless ideal case:
- Noiseless capk = 0.5236
- FakeMarrakesh capk = 0.5625 (from Exp64, 17 cells)

Three competing explanations were proposed (Finding 42 document):
1. **Non-unital anti-contraction**: Amplitude damping (T1 relaxation) in FakeMarrakesh is non-unital.
   Elder C6142's contractivity theorem applies strictly only to UNITAL channels. Non-unital noise
   can anti-contract — expanding cost gaps rather than contracting them.
2. **Noise-assisted escape**: Stochastic noise helps COBYLA optimizer escape local minima during
   optimization, producing better anchors in the warm-start.
3. **Statistical variance**: N=17 cells, 256 shots. The observed difference may not be real.

**Key scientific question**: Is the anti-contraction specific to non-unital noise (amplitude damping),
or does it persist under purely depolarizing (unital) noise?

**Why this matters**: If anti-contraction persists under unital depolarizing noise, Explanation 1
(non-unital specific) is FALSIFIED. If anti-contraction DISAPPEARS under depolarizing noise (we see
contraction as the nc-ch8-9 theorem predicts for unital channels), Explanation 1 is supported.

## Design

### Noise model
4 levels of parameterized depolarizing noise applied to the EDGES_20 QAOA circuit (20 qubits, p=5):
- Single-qubit gate (H, RZ) depolarizing error rate p1
- 2-qubit gate (CX) depolarizing error rate p2

| Level | Label | p1 (1-qubit) | p2 (2-qubit) | Notes |
|-------|-------|-------------|-------------|-------|
| 0 | noiseless | 0 | 0 | Exp66 data (already computed) |
| 1 | low | 0.0002 | 0.002 | ~1/5 FakeMarrakesh-equiv |
| 2 | medium | 0.0005 | 0.005 | ~1/2 FakeMarrakesh-equiv |
| 3 | high | 0.001 | 0.010 | ~FakeMarrakesh-equiv |
| 4 | very-high | 0.003 | 0.030 | ~3× FakeMarrakesh-equiv |

Reference: FakeMarrakesh CZ gate error ~0.002; SX gate error ~0.0003. CX and CZ depolarizing
equivalents are approximate (CX not native to Marrakesh, but same 2-qubit error scale applies
for comparison purposes).

### Circuit pool
EDGES_20 seeds 42-49 (N=8 cells). Same graph instance as Exp64/Exp66.
Reproducibility: `np.random.seed(seed)` before each cell. Same seed = same x0_cold, same anchor draws.

### Protocol
For each (seed, noise_level):
1. Cold start: optimize p=5 QAOA from random x0_cold → r_cold
2. K=3 p=3 anchor runs → 3 anchors
3. Granular escalation (best-first, threshold=LOO-median) → r_warm_granular, k_used
4. Binary escalation (2-shot) → r_warm_binary
5. Record capture metrics

Same as Exp64/Exp66 protocol (K=3, 256 shots, maxiter=20, COBYLA).

LOO-CV tau: computed across all 8 seeds at each noise level independently (same methodology as Exp64).

## Pre-registered Hypotheses

### H1 (Contraction check — the main scientific test)
**Does unital (depolarizing) noise CONTRADICT the FakeMarrakesh anti-contraction?**

Prediction: Under depolarizing noise at FakeMarrakesh-equivalent rates (Level 3), capk_granular
will be LOWER than noiseless (0.5236), consistent with contractivity theory for unital channels.

VALIDATE if Level 3 depolarizing capk_granular < 0.5236 (noiseless).
INVALIDATE if Level 3 depolarizing capk_granular >= 0.5236 (anti-contraction persists in unital case).

**Mechanistic implication**: 
- H1 VALIDATED → FakeMarrakesh anti-contraction is due to NON-UNITAL amplitude damping (Explanation 1).
- H1 INVALIDATED → Anti-contraction is NOT specific to non-unital noise; Explanation 2 or 3 must dominate.

### H2 (Dose-response monotonicity)
**Does capk monotonically decrease with depolarizing noise?**

Prediction: Spearman rank correlation between noise level index [1,2,3,4] and capk_granular < -0.5
(monotone decrease, as contractivity theory predicts for unital channels).

VALIDATE if Spearman rho(noise_level, capk) < -0.5.
INVALIDATE if Spearman rho >= -0.5 (non-monotone or weak).

### H3 (Pareto-efficiency robustness across noise levels)
**Does granular > binary Pareto-efficiency hold at ALL depolarizing noise levels?**

Prediction: At every noise level (0 through 4), capk_granular > capk_binary.

VALIDATE if granular > binary at all 5 noise levels (including noiseless from Exp66).
INVALIDATE if any noise level shows granular <= binary.

### H4 (Statistical significance)
**Is the dose-response statistically meaningful or noise-dominated?**

Prediction: The range of capk_granular across all 5 noise levels exceeds 0.05 (sufficient signal
to detect a trend).

VALIDATE if max(capk) - min(capk) > 0.05 across the 5 levels.
INVALIDATE if range <= 0.05 (too small to detect any trend; inconclusive experiment).

## Connection to Prior Work

- **Exp55 arc** (noise-as-resource): tested whether noise helps QAOA escape local optima.
  That arc ended NO-GO due to confounded design. Exp67 is ORTHOGONAL: tests noise effect on
  WARM-START QUALITY (anchor selection + k-policy), not escape from local optima per se.
  
- **Finding 42 / Exp66**: The parent experiment. Exp67 is a mechanism-isolating follow-up.

- **nc-ch8-9 (Elder C6142)**: The contractivity theorem that motivates the specific prediction
  (unital noise → contraction → capk decreases with noise). Exp67 directly tests this in the
  pure-unital (depolarizing) case.

- **pred_c3981_001** (conf 0.52, test_cycle C4100): "Exp66 QPU test at N>=34 will show
  granular capk < 0.40." The QPU test is Part B of Exp66. Exp67's mechanism test informs
  whether the QPU test prediction is well-grounded.

## File Manifest

- `experiments/exp67-depolarizing-dose-response-preregistration.md` — THIS FILE (pre-reg)
- `scripts/run_exp67_depolarizing_dose_response.py` — Experiment runner
- `experiments/exp67_results.json` — Results (to be created post-run)
- `findings/exp67-dose-response-finding-ember-c3982.md` — Synthesis (to be created post-grading)

## Scope and Honesty

- N=8 EDGES_20 seeds. Limited by within-instance variance; CI bootstrap reported.
- 256 shots per COBYLA evaluation (same as Exp64/Exp66 for comparability).
- Depolarizing model ≠ FakeMarrakesh physically (missing amplitude damping, readout errors,
  cross-talk). Level 3 is "equivalent in p2 error rate" but not in noise type.
- Results for Levels 1-4 are NEW compute; Level 0 (noiseless) reuses Exp66's 8 EDGES_20 cells.
- No cherry-picking: all 8 seeds at each level reported. LOO-CV tau computed independently per level.
