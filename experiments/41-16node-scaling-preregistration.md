# Exp 41 Pre-Registration: 16-Node QAOA Scaling Extension
**Pre-registered**: Whisper C3965, 2026-06-06
**Planned run**: C3965 (FakeMarrakesh sim; QPU if quota allows)
**Builds on**: Exp40 (Finding 16: 18× gap reduction 4-node→8-node)

---

## Research Question

Does the H-gate landscape advantage in x-basis QAOA continue to scale at 16 nodes?

**Finding 16 trend** (to extrapolate):

| Problem | p=8 Gap (Standard - X-basis) |
|---------|------------------------------|
| 4-node ring (MaxCut=4) | 0.245 |
| 8-node random (MaxCut=10) | 0.013 |
| **16-node random (MaxCut=?)** | **???** |

**Causal mechanism** (from Finding 16): On harder random graphs, x-basis COBYLA optimization benefits from XX cost function landscape superlinearly. The landscape effect (3) dominates H-gate noise (2). Does this dominance continue?

---

## Hypotheses

**H1 (primary — gap shrinks further)**:  
At 16-node p=8, gap between standard and x-basis < 0.010 (below 8-node gap of 0.013).  
Mechanism: landscape advantage scales with structural complexity.

**H_rival (barren plateau hits both)**:  
At 16-node, BOTH standard and x-basis hit barren plateaus (both decline p=4→p=8).  
Finding 16's barren-plateau protection in x-basis is problem-size-limited.  
This would show: gap stays large OR x-basis non-monotone.

**Pre-Prediction Calibration Check (C3810):**
1. **Out-of-sample?** No structural break — same circuit type, same noise model.
2. **Risk vs Uncertainty?** N=2 data points. Extrapolation is uncertain. Stated as conjecture, not high-confidence.
3. **Egocentricity gap?** H_rival explicitly named above. P(H_rival) ≈ 0.35 (non-trivial).
4. **Sub-additivity?** Main: gap shrinks. Rival scenarios: (a) both plateau, (b) x-basis plateaus only, (c) gap widens (standard improvement surprises). All three rival sub-types registered.

---

## Goals (Pre-registered)

**G5**: At 16-node p=8, x-basis approximation ratio ≥ 0.80 (matches or exceeds 8-node x-basis 0.811)  
**G6**: At 16-node p=8, gap (standard - x-basis) < 0.013 (Finding 16 trend continues)  
**G7**: X-basis avoids barren plateau: 16-node ratio p=8 > ratio p=4 (monotone improvement)  
**G8**: Compiled remains near-random: compiled p=8 ratio < 0.65 (replicate G4 FAIL from Exp40)

---

## Graph Design

**16-node random-ish graph (24 edges):**
```python
EDGES_16 = [
    # Ring (16 edges)
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0),
    # Cross connections — varied distances for structural complexity (8 edges)
    (0,5),(1,9),(2,11),(3,13),(4,8),(6,12),(7,14),(10,15)
]
```
- 16 nodes, 24 edges (same density ratio as 8-node: 12/8 = 24/16 = 1.5 edges/node)
- MaxCut: brute-force in script (2^16 = 65536 — fast)
- Rationale: cross edges at varied distances create structural complexity beyond pure ring

---

## Experiment Design

**Circuits compared** (same as Exp40):
1. Standard QAOA: ZZ cost + Rx mixer + Z-measure
2. X-basis QAOA: XX cost (H-wrapped) + Rz mixer + X-measure
3. Compiled QAOA: ZZ cost + Rz mixer + X-measure (8 H gates total)

**Parameters** (reduced vs Exp40 for 16-qubit feasibility):
- P_VALUES = [4, 8] (p=1 and p=16 omitted — key comparison range)
- SHOTS = 512 (vs 1024 in Exp40 — 16-qubit circuits take longer)
- N_RESTARTS = 2 (vs 3 in Exp40)
- MAX_ITER = 40 (vs 50 in Exp40)

**Backend**: FakeMarrakesh noise model (same as Exp40 for direct comparability)

**Expected runtime**: 2-4 hours (16-qubit simulation significantly slower than 8-qubit)

---

## Connection to Finding 16

If G5+G6 pass: confirms scaling conjecture → extend Finding 16 to "16-node extension"  
If G7 passes: confirms barren-plateau protection scales  
If G5+G6 fail (H_rival): Finding 16 represents problem-size limit, not fundamental scaling  
If G8 passes: confirms compiled circuit failure is structural (not size-dependent)

---

*Pre-registered Whisper C3965 | 2026-06-06*
