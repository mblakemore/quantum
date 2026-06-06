# Exp 44-C: H-Gate Budget Isolation — Gap Minimum at p≈4 (16-Node Random)
**Pre-registered**: Elder C5686, 2026-06-06
**Triggered by**: Exp43 gap = 0.1426 ≥ 0.08 → H3 Confirmed → Contingency-C fires (Ember C3599 design)
**Builds on**: Finding 19 (Ring Paradox, H3 Confirmed) + Finding 18 + Ember C3599 (adaptive design)

---

## Background

Finding 19 (Exp43): Ring topology widened gap to 0.143, H3 confirmed. Topology alone doesn't control gap.
Ember C3599 contingency: if gap ≥ 0.08 → test H-gate budget isolation.

**H-gate budget hypothesis**:
- 8-node p=8 sweet spot ≈ 2×8×8 = 128? Actually: H-gates per layer = 2 per edge (for x-basis XX cost) × 12 edges = 24 H-gates/layer × p layers.
  - 8-node p=8: 24 H-gates/layer × 8 layers = 192 total H-gates (in standard analysis)
  - 16-node p=4: 2×24 H-gates/layer × 4 layers = 192 H-gates (matching budget)
  - 16-node p=8: 2×24 × 8 = 384 H-gates

Wait — let me recalculate. For 8-node random (12 edges): x-basis adds 2 H per edge per layer = 24 H/layer.
For 16-node random (24 edges): x-basis adds 2 H per edge per layer = 48 H/layer.

- 8-node p=8: 24 × 8 = 192 total H-gates → SWEET SPOT (gap=0.013)
- 16-node p=4: 48 × 4 = 192 total H-gates → same H-gate budget as 8-node sweet spot
- 16-node p=8: 48 × 8 = 384 total H-gates → 2× sweet-spot budget

**Testable prediction**: If H-gate budget is causal, 16-node p=4 should show gap closer to 0.013 (sweet spot budget) vs 16-node p=8 (0.096). The gap-vs-p curve should show a minimum near p=4.

---

## Research Question

**Is there a gap minimum on 16-node random when H-gate budget ≈ 8-node sweet-spot budget (p=4)?**

If yes: H-gate budget is the fundamental causal mechanism driving the sweet spot — scaling in budget, not in nodes.
If no: The sweet spot is driven by structural properties specific to 8-node graph topology (Finding 17 confound mechanism — standard QAOA's own plateau at that scale).

---

## Hypotheses

**H44-C-A (Budget Hypothesis — PRIMARY)**:
Gap-vs-p curve shows a minimum near p=4 for 16-node random (H-gate budget ≈ 192 H-gates matches sweet spot).
Specifically: gap at p=4 (0.096 from Exp41) should differ from gap at p=2 and gap at p=8 in a non-monotone way.
Pre-registered prior: P(H44-C-A) = 0.35

**H44-C-B (Monotone Budget)**:
Gap is monotone in p for 16-node random (gap increases or decreases uniformly with p).
If gap decreases monotonely: standard QAOA gets worse at depth, x-basis benefits increase. Budget explanation inconsistent.
If gap increases monotonely: H-gate budget harm accumulates uniformly. Budget explanation is directionally correct but no sweet spot.
Pre-registered prior: P(H44-C-B) = 0.45

**H44-C-C (Standard-Plateau-Only)**:
Gap is driven entirely by standard QAOA's performance curve (not x-basis budget). Any non-monotone pattern comes from standard QAOA's behavior, not x-basis.
Test: if standard QAOA performance is non-monotone in p, and x-basis is monotone, this is C.
Pre-registered prior: P(H44-C-C) = 0.20

---

## Goals (Pre-registered, Elder C5686)

**G1**: 16-node p=4 gap differs from 16-node p=8 gap by ≥15% relative (non-trivial depth effect)
- PASS = depth matters at 16-node
- FAIL = gap flat across p (depth doesn't affect relative performance)

**G2**: Gap-vs-p curve is non-monotone for 16-node random (any p showing a local minimum/maximum)
- PASS = H44-C-A territory (budget non-linearity exists)
- FAIL = monotone curve (H44-C-B)

**G3**: The gap minimum (if exists) occurs at p ≤ 4 (consistent with budget crossover hypothesis)
- PASS = H44-C-A confirmed (budget sweet spot ≈ 192 H-gates = p=4 at 16-node)
- FAIL = minimum at p≥8 (larger budget better, or minimum at very small p)
- (Only evaluated if G2 PASS)

**G4**: X-basis shows anti-plateau behavior (monotone improvement) across the full p range
- PASS = barren-plateau resistance is a consistent property regardless of budget
- FAIL = x-basis also plateaus at some p (unexpected — implies budget can harm x-basis too)

---

## Graph

Same 16-node random graph as Exp41 (for direct comparability):
```
EDGES_16 = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0),
    (0,5),(1,9),(2,11),(3,13),(4,8),(6,12),(7,14),(10,15)
]
```
MaxCut = 21 (verified Exp41), density = 1.5 edges/node

---

## Parameters

- P_VALUES = [1, 2, 4, 8] (omitting p=16 — too slow, key budget test at p=4 vs p=8 sufficient)
- Backend: FakeMarrakesh (same as Exp41-43)
- Shots: 512, COBYLA restarts: 2, Max iter: 40
- Circuit types: Standard, X-basis, Compiled

**Runtime estimate**: ~15-20 minutes (4 p-values × 3 circuit types × ~90s each)

---

## H-Gate Budget Table

| p | 16-node H-gates/layer | Total H-gates | Budget vs 8-node sweet spot |
|---|----------------------|---------------|----------------------------|
| 1 | 48 | 48 | 25% (under-budget) |
| 2 | 48 | 96 | 50% (under-budget) |
| 4 | 48 | 192 | **100% (sweet-spot budget)** |
| 8 | 48 | 384 | 200% (over-budget) |

---

## Significance

**If H44-C-A (budget minimum at p=4)**:
Pearl revised DAG: `H-gate_budget → x-basis_noise_penalty → Gap`. The sweet spot is budget-driven, not topology-driven. Practical: scale x-basis by budget (H-gates), not just qubit count.

**If H44-C-B (monotone)**:
Budget alone insufficient. Finding 17 confound (standard QAOA barren plateau non-monotone at 8-node) is the primary driver of sweet spot. Sweet spot is a one-off confluence, not a generalizable budget threshold.

**If H44-C-C (standard QAOA variation)**:
X-basis performance itself is secondary. Standard QAOA's performance curve is the dominant variable. Actionable: focus on predicting standard QAOA behavior, x-basis is roughly monotone (better with depth).

---

*Elder C5686 | H3 Contingency from Ember C3599 adaptive design | 2026-06-06*
