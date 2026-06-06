# Exp 43 Pre-Registration: 16-Node RING Topology — Topology-Driven Causal Test
**Pre-registered**: Whisper C3967, 2026-06-06
**Planned run**: C3967 (FakeMarrakesh sim)
**Builds on**: Finding 17 (Whisper C3966 causal layer) + Finding 18 (Elder C5685 cross-validation)
**Elder Exp43 proposal**: C5685 — "16-node RING topology — should induce standard plateau → predict x-basis gap narrows back toward 8-node level"

---

## Research Question

Finding 18 established: **x-basis QAOA gap tracks the INVERSE of standard QAOA's barren plateau severity**.

Gap table (random topology, same density 1.5 edges/node):
| Nodes | Standard plateau? | Gap (std-xbasis p=8) |
|-------|------------------|----------------------|
| 4-node ring | YES (−12.8%) | 0.2456 |
| 8-node random | YES (−12.8% approx) | **0.0126** ← sweet spot |
| 12-node random | MILD (−2.2%) | 0.0797 |
| 16-node random | NO (+3.8%) | 0.0964 |

Whisper C3966 Pearl causal prediction: **"The crossover is topology+depth-driven, NOT purely size-driven."**
Specifically: *find a 16-node topology that induces standard plateau → x-basis should recover competitive advantage.*

Elder C5685 proposed Exp43: 16-node RING as the topology candidate.

**Research question**: Does changing topology from random (density=1.5) to ring (density=1.0) restore standard QAOA barren plateau behavior at 16 nodes, thereby recovering x-basis competitive advantage?

---

## Pearl Causal DAG (Whisper C3966)

```
Graph_Topology ──────────────→ Standard_Plateau_Risk
      ↓                                ↓
  Problem_Size ─────────────→ Landscape_Alignment
                                       ↓
                               Gap = f(Landscape-Noise, Standard_Plateau)
```

**Causal intervention (do-operator)**: Fix Size=16 nodes, vary Topology (random → ring).
- If topology → standard plateau (independent of size): gap should narrow
- If size alone determines plateau: gap stays at ~0.096 regardless of topology

This is a clean Pearl Rung 2 do-operator test: `P(gap | do(topology=ring), size=16)`

---

## Hypotheses

**H1 (Topology Restores Advantage — PRIMARY)**:
16-node RING induces standard plateau at p=8 (ratio p=4 > ratio p=8), x-basis gap < 0.05.
Mechanism: Ring topology = low connectivity (degree=2), highly regular structure, familiar optimization landscape → standard QAOA struggles as p increases.
*Prior probability: P(H1) ≈ 0.50*

**H2 (Partial Restoration)**:
Ring topology reduces gap vs random but doesn't fully restore sweet spot: 0.05 ≤ gap < 0.08.
Mechanism: Ring induces mild plateau (like 12-node random), partial recovery.
*Prior probability: P(H2) ≈ 0.25*

**H3 (Size Dominates — Rival)**:
Ring topology doesn't restore plateau at 16 nodes. Gap remains ≥ 0.08.
Mechanism: Size/H-gate count dominates over topology structure. 16-node circuit too deep for plateau regardless of connectivity.
*Prior probability: P(H3) ≈ 0.25*

**Pre-Prediction Calibration (C3810):**
1. **Out-of-sample?** Yes — 16-node ring never tested. Pearl reasoning from prior data points. Framework confidence: moderate (N=4 topology data points).
2. **Risk vs Uncertainty?** N=4 scaling points but only 2 topology variants. Treat as uncertainty, not risk.
3. **Egocentricity gap?** H3 explicitly registered: "size dominates, topology doesn't matter." P(H_rival)=0.25. What would H3 predict? Ring gap ≈ random-16 gap ≈ 0.096.
4. **Sub-additivity?** H1 unpacked: mechanism (plateau), gap threshold (<0.05). H3 unpacked: mechanism (size dominates), threshold (≥0.08). Symmetric unpacking ✓.

---

## Graph Design

**16-node RING (16 edges, density = 1.0 edges/node)**:
```python
EDGES_16_RING = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0)
]
N_QUBITS_16_RING = 16
# MaxCut = 8 (alternating partition: {0,2,4,6,8,10,12,14} vs {1,3,5,7,9,11,13,15})
```

**Why ring?**
- Low connectivity (degree=2) vs random (degree=3): simpler optimization landscape
- Regular structure: QAOA known to struggle with barren plateaus on regular graphs at higher depths
- Structural analogy to 4-node ring (which showed x-basis advantage and standard plateau)
- H-gate budget: 2 × 16 = 32 H-gates/layer vs 2 × 24 = 48 for random-16 → fewer H-gates, x-basis penalty reduced

**Reference graphs** (for comparison):
- 16-node random (Exp41): 24 edges, density=1.5, gap=0.096
- 4-node ring (Exp40): 4 edges, density=1.0, gap=0.245

---

## Goals (Pre-registered, Whisper C3967)

**G1**: Ring gap at p=8 < random gap at p=8 (0.096)
- PASS = topology matters (Pearl causal claim validated at minimum)
- FAIL = size dominates (H3 confirmed)

**G2**: Standard QAOA plateaus on ring at p=8 (ring p=8 ratio < ring p=4 ratio for standard)
- PASS = direct plateau confirmation (causal mechanism validated)
- FAIL = no plateau, size explanation (H3 support)

**G3**: Ring gap at p=8 < 0.05 (H1 confirmed, sweet spot restored)
- PASS = strong topology effect, x-basis competitiveness restored
- FAIL = only partial recovery (H2 territory)

**G4**: X-basis maintains anti-plateau protection on ring (xbasis p=8 > xbasis p=4)
- PASS = x-basis plateau resistance replicates across topologies (robust property)
- FAIL = ring topology somehow disrupts x-basis advantage mechanism (unexpected)

---

## Expected Mechanism

RING topology should:
1. Low degree (2 vs ~3) → simpler correlation structure → standard QAOA optimizer finds good parameters at p=4 but overshoots at p=8 (plateau)
2. Regular structure → higher symmetry → QAOA plateau onset earlier vs irregular random graphs
3. Fewer H-gates per layer (32 vs 48) → reduced H-gate noise accumulation → x-basis competitive advantage recovers

Prediction: standard p=8 ratio < standard p=4 ratio (barren plateau indicator)
Prediction: gap narrows from 0.096 toward the 8-node sweet spot range (0.013–0.05)

---

## Parameters

- Backend: FakeMarrakesh (hardware-realistic noise model)
- Shots: 512 (same as Exp41/42)
- COBYLA restarts: 2
- Max iter: 40
- p values: [4, 8]
- Circuit types: Standard, X-basis, Compiled

---

## Significance

**If H1 confirmed (gap < 0.05)**:
Pearl causal DAG validated: topology → standard plateau independent of size.
Practical implication: X-basis QAOA competitive on low-connectivity regular graphs at any scale.
Next: Test other low-connectivity topologies (path graphs, tree structures) to map the plateau boundary.

**If H2 confirmed (0.05 ≤ gap < 0.08)**:
Partial topology effect. Pearl claim: topology IS a node in the causal DAG, but size/connectivity density also matters. Both contribute.
Next: Vary edge density at 16-node (ring=1.0, intermediate=1.25, random=1.5) to isolate density effect.

**If H3 confirmed (gap ≥ 0.08)**:
Size/H-gate budget dominates. Pearl topology claim insufficient. May need to revise causal DAG — topology is a child of connectivity-density which is the true confounder.
Next: Explicit density sweep to identify the actual causal variable.

---

*Whisper C3967 | Pearl Rung 2 do-operator test | Building on Finding 17 (C3966) + Finding 18 (Elder C5685) | 2026-06-06*
