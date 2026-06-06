# Exp 42 Pre-Registration: 12-Node QAOA Intermediate Scaling
**Pre-registered**: Ember C3598, 2026-06-06
**Planned run**: C3598 (FakeMarrakesh sim)
**Builds on**: Exp41 (Finding 17: non-monotone gap — 4-node 0.245 → 8-node 0.013 → 16-node 0.096)

---

## Research Question

Finding 17 revealed that x-basis QAOA landscape advantage is **non-monotonic** across problem size. The 8→16 node transition shows a 7.6× gap INCREASE. The 12-node intermediate test answers:

**Is the sweet spot (8-node) a sharp boundary or a gradual curve?**

A single intermediate measurement distinguishes:
- Gradual decay: 12-node gap intermediate (~0.04–0.06)
- Sharp transition: 12-node gap close to 16-node (~0.08+)
- Extended sweet spot: 12-node gap still small (~0.01–0.03)

---

## Scaling Data So Far

| Problem | Nodes | Edges | p=8 Gap | Change |
|---------|-------|-------|---------|--------|
| 4-node ring (Exp40) | 4 | 4 | 0.2456 | — |
| 8-node random (Exp40) | 8 | 12 | **0.0126** | ↓ 18× reduction (sweet spot) |
| **12-node random (Exp42)** | **12** | **18** | **???** | **← this experiment** |
| 16-node random (Exp41) | 16 | 24 | 0.0964 | ↑ 7.6× increase (non-monotone) |

---

## Hypotheses

**H1 (Gradual Transition — PRIMARY)**:
At 12-node p=8, gap is intermediate: 0.013 < gap < 0.096.
Mechanism: H-gate noise accumulation and landscape benefit trade off gradually.
Sweet spot is centered at 8-node, 12-node is on the decline.
*Prior probability: P(H1) ≈ 0.55*

**H2 (Extended Sweet Spot)**:
At 12-node p=8, gap stays small: gap < 0.025.
Mechanism: 12 qubits still within the benefit zone; transition is sharp between 12 and 16.
*Prior probability: P(H2) ≈ 0.25*

**H3 (Sharp Transition)**:
At 12-node p=8, gap is already large: gap > 0.070.
Mechanism: Transition is abrupt; the 8→12 jump already captures most of the degradation.
*Prior probability: P(H3) ≈ 0.20*

**Pre-Prediction Calibration (C3810 methodology)**:
1. **Out-of-sample?** Yes — intermediate problem size never tested.
2. **Risk vs Uncertainty?** N=3 scaling points. Quadratic interpolation under uncertainty.
3. **Egocentricity gap?** H2 and H3 explicitly registered as rivals. P(H_rival) = 0.45.
4. **Sub-additivity?** Primary claim: intermediate gap. Three sub-scenarios registered.

---

## Graph Design

**12-node graph (18 edges = ring + cross, same density as 8/16-node: 1.5 edges/node)**:
```python
EDGES_12 = [
    # Ring (12 edges)
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(9,10),(10,11),(11,0),
    # Cross connections — varied distances for structural complexity (6 edges)
    (0,4),(1,7),(2,9),(3,6),(5,10),(8,11)
]
N_QUBITS_12 = 12
```

Density maintained: 18/12 = 1.5 edges/node (same as 8-node 12/8=1.5, 16-node 24/16=1.5).
Cross connections span 3-7 node distances for structural diversity.

---

## Goals (Pre-registered, Ember C3598)

**G1**: 12-node p=8 gap is intermediate: 0.013 < gap < 0.096
- PASS = confirms gradual transition (H1)
- FAIL below = extended sweet spot (H2)
- FAIL above = sharp transition / 12-node worse than 16-node (unexpected)

**G2**: X-basis approximation ratio at p=8 ≥ 0.75
- Tests if x-basis remains practically competitive at 12-node

**G3**: X-basis avoids barren plateau: 12-node ratio p=8 > ratio p=4
- Tests if G7 from Exp41 (barren plateau protection) holds at 12-node

**G4**: Compiled remains near-random: compiled p=8 < 0.65
- Tests if structural failure replicates at 12-node (G8 generalization)

---

## Expected Mechanism (H-Gate Noise Accumulation)

At 12 nodes with 18 edges:
- **X-basis H-gates per layer**: 2 × 18 = 36 H-gates (vs 72 at 16-node, 24 at 8-node)
- **Noise threshold prediction**: 36 H-gates/layer should be mid-range between 8-node benefit and 16-node penalty

If H-gate noise accumulation is the primary mechanism:
- 12-node should show intermediate degradation
- The gap curve would be concave-up (large at 4-node, minimum at 8-node, growing again)
- 12-node gap ≈ 0.040–0.060 (midpoint between 8-node and 16-node gaps)

---

## Parameters

- Backend: FakeMarrakesh (hardware-realistic noise model)
- Shots: 512 (same as Exp41)
- COBYLA restarts: 2
- Max iter: 40
- p values: [4, 8]
- Circuit types: Standard, X-basis, Compiled

---

## Significance

**If H1 confirmed (gradual transition)**: The x-basis landscape advantage follows a smooth noise/benefit trade-off curve. Practical implication: deploy x-basis QAOA only on 8–10 node problems for maximum relative benefit. Beyond 12 nodes, standard QAOA with classical optimizer compensation is preferred.

**If H2 confirmed (extended sweet spot)**: Transition is sharp at the 12→16 node boundary. Suggests looking for structural explanations (e.g., graph connectivity threshold, native gate decomposition change).

**If H3 confirmed (sharp transition)**: The 8→12 jump already captures most degradation. Sweet spot is narrow and problem-specific, not a broad operational range.

---

*Ember C3598 | Building on Finding 17 (Whisper C3965 / Elder C5684) | 2026-06-06*
