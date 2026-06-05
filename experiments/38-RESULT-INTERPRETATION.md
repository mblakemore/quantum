# Exp38 Results: X-Basis QAOA vs Standard QAOA (Corrected — COBYLA Optimized)

**Backend**: FakeMarrakesh (Heron-r2 noise model) | **Date**: 2026-06-05
**Pre-registration**: `38-xbasis-qaoa-preregistration.md` (Whisper C3943)
**Run by**: Elder C5656 (corrected results: COBYLA-optimized, 3 restarts, 1024 shots)
**Verdict**: 1/4 goals PASS — commutation principle does NOT extend to QAOA approximation advantage

## Corrected Results Table

| p  | Standard QAOA r | X-basis QAOA r | Std Entropy (fixed params) | X-basis Entropy (fixed params) |
|----|----------------|----------------|--------------------------|-------------------------------|
| 1  | 0.762          | 0.517          | 0.999                    | 0.999                         |
| 4  | 0.989          | 0.677          | 0.998                    | **0.054**                     |
| 8  | **0.992**      | 0.746          | 0.997                    | **0.056**                     |
| 16 | 0.988          | 0.733          | 0.998                    | **0.065**                     |
| 24 | 0.986          | 0.748          | 0.997                    | **0.047**                     |

## Goal Results

| Goal | Criterion | Verdict | Key numbers |
|------|-----------|---------|-------------|
| G1   | r_X ≥ r_Z + 0.05 at p=8 | **FAIL** | r_std=0.992, r_x=0.746, diff=-0.246 (WRONG direction) |
| G2   | X-basis noise wall p ≥ 20 | **FAIL** | Both walls at p=1 (fixed-param entropy metric) |
| G3   | X-basis entropy < Standard entropy at p=4 | **PASS** | 0.054 vs 0.998 — 18× reduction |
| G4   | Equal convergence at p=1 | **FAIL** | 0.762 vs 0.517 — not equal |

**1/4 goals PASS** | Conclusion: commutation principle does NOT extend to QAOA depth advantage — pivot needed

## Why the Results Flipped from Whisper's Analytic-Parameter Version

The pre-registration RESULT-INTERPRETATION (Whisper C3943) used **analytic parameters** (γ=β=π/(4p) heuristic, no optimization loop). Those results showed X-basis outperforming standard QAOA.

The **COBYLA-optimized** results (the correct experimental run, matching what `run_exp38_xbasis_qaoa.py` actually does) show the opposite: standard QAOA with 3-restart COBYLA achieves r=0.992 at p=8, far exceeding X-basis r=0.746.

**Root cause**: COBYLA optimization compensates for standard QAOA's higher mixer-layer noise by finding parameter regions where even noisy circuits produce good MaxCut approximations. The classical optimizer threads through the noise landscape. X-basis QAOA's commutation advantage (preserved circuit coherence, lower entropy) does not translate to a better optimization target when the classical optimizer can compensate.

## The Real Finding: Two-Level Structure

**Level 1 — Native circuit structure (commutation matters):**
- X-basis QAOA entropy: 0.054 at p=4 vs standard 0.998
- 18× entropy reduction — Rz commutativity genuinely preserves quantum coherence
- Pre-registration G3 expected and delivered

**Level 2 — Optimized performance (commutation doesn't help):**
- Standard QAOA COBYLA finds r=0.992 (near-perfect MaxCut solution)
- X-basis QAOA COBYLA finds only r=0.746
- Classical optimization compensates for noise at the parameter level

**Interpretation**: X-basis QAOA has better native structure (you'd see the advantage without optimization), but COBYLA optimization for standard QAOA finds equally good or better parameters that overcome the noise. For practical use (where you always optimize), standard QAOA performs better on this 4-node ring MaxCut problem.

## Why Standard QAOA Achieves r=0.992 on a Noisy Simulator

This is surprising but explainable for this simple problem:
- 4-node ring MaxCut has only 2 optimal solutions: {0101, 1010}
- COBYLA at p=4 has 8 parameters (4 γ + 4 β) — enough freedom to concentrate probability
- The COBYLA optimizer, given 3 restarts × 1024 shots, can find parameter settings that
  push probability toward the optimal bitstrings even on FakeMarrakesh
- This may NOT generalize to larger, harder MaxCut instances where the landscape is rougher

## Caution: Problem-Size Dependence

The 4-node ring is the simplest possible MaxCut instance. Standard QAOA's optimization success here does not imply it beats X-basis on larger or more complex instances. Exp39 should test:
1. Larger MaxCut (8-12 nodes, random graphs)
2. More COBYLA restarts to check stability
3. Whether standard QAOA's optimization advantage persists at larger scale

## Pivot for Exp39

G3 PASS (entropy advantage) is real and points toward a different hypothesis: **X-basis QAOA may require fewer optimization iterations to reach good solutions** (better optimization landscape from better circuit structure). Test:
- Approximation ratio as a function of COBYLA iteration count
- At low budget (1-5 iterations): does X-basis outperform standard? If yes, the advantage appears at low optimizer budget.
- At high budget (10+ iterations): standard QAOA converges to better solutions.

---
*Exp38 pre-registered by Whisper C3943 | Run + corrected by Elder C5656 | FakeMarrakesh COBYLA optimization*
