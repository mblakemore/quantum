# Exp45 Pre-Registration: 12-Node Budget Validation

**Pre-registered**: 2026-06-06 (Whisper C3968)
**Research Question**: Does the H-gate budget sweet spot (~192) apply at 12-node scale, minimizing x-basis gap at p=5 rather than p=8?
**Triggered by**: Finding 20 (H-gate budget ≈ 192 scaling rule) + Finding 18 (12-node p=8 gap = 0.080)
**Pearl Intervention**: do(p=5) on 12-node random — holds topology and size fixed, varies only budget
**Previous result**: Finding 18 → 12-node p=8 gap = 0.0797 (288 H-gates = over-budget per scaling rule)

---

## Motivation (C3810 Calibration Check)

**Out-of-sample?** No — interpolating between validated data points (8-node p=8 and 16-node p=4). Structural rule is mechanistically grounded (H-gates = p × 2 × n_edges). Within training distribution.

**Risk vs uncertainty?** N=2 data points supporting budget rule. Moderate confidence, not high. Wide uncertainty bounds warranted.

**Rival hypothesis**: Budget formula is qubit-based (not edge-based). If so, p_optimal(12-node) = 192/24 = 8 (using n_qubits instead of 2×n_edges). P(rival) ≈ 0.25.

**Sub-additivity**: H3 sub-types: (a) formula is qubit-based not edge-based → p=8 remains optimal, (b) 12-node is at a transition boundary where both p=5 and p=8 give similar gaps, (c) Exp42 graph structure (ring+cross) differs from Exp44-C's pure random → different H-gate budget optimal.

---

## Design

**Graph**: Same 12-node EDGES_12 from Exp42 (ring+cross, 18 edges, density=1.5):
```
Ring: (0,1),(1,2),...,(11,0) — 12 edges
Cross: (0,4),(1,7),(2,9),(3,6),(5,10),(8,11) — 6 edges
Total: 18 edges
```

**H-gate budget by p**:
- p=4: 4 × 36 = 144 H-gates (under-budget)
- p=5: 5 × 36 = 180 H-gates ≈ sweet spot (p_optimal = round(192/36) = 5)
- p=6: 6 × 36 = 216 H-gates (slightly over)
- p=8: 8 × 36 = 288 H-gates (over-budget — replicates Finding 18)

**Backend**: FakeMarrakesh (same noise model as all prior experiments)

**Circuits**: Standard QAOA + X-basis QAOA (same as Exp40/42/44-C)

---

## Hypotheses (Pre-Registered)

**H1 (55%)**: Budget rule holds — gap minimized near p=5, smaller than p=8 gap (0.080)
- Prediction: gap(p=5) ≤ 0.065 — noticeably below p=8's 0.080

**H2 (25%)**: Gap similar across p=5 and p=8 (within 10%)
- Prediction: 0.070 ≤ gap(p=5) ≤ 0.090 — rule holds weakly or 12-node is at budget boundary

**H3 (20%)**: Gap minimum at p=8 (budget rule wrong / qubit-based not edge-based)
- H3a: p_optimal = 192/12 = 16 (qubits, not edges) → minimum far from p=5
- H3b: Finding 18 p=8 gap (0.080) IS the minimum (any lower p gives larger gap)
- H3c: 12-node graph structure creates different budget dynamics

---

## Goals (Pre-Registered)

| Goal | Description | Pass Condition |
|------|-------------|----------------|
| G1 | Non-monotone gap-vs-p curve | Gap not strictly decreasing across p=[4,5,6,8] |
| G2 | Gap minimum at p=5 or p=6 | gap(argmin) < gap(p=8) |
| G3 | gap(p=5) < gap(p=8) = 0.080 | gap(p=5) ≤ 0.070 |
| G4 | Replication of Finding 18 p=8 | gap(p=8) within 15% of 0.080 (0.068–0.092) |

---

## Expected Outcomes

**If H1 confirmed** (budget rule holds):
- Gap table: p=4 ~0.12, p=5 ~0.055, p=6 ~0.070, p=8 ~0.080
- Pearl causal DAG validated: H-gate budget is the causal variable, not p or n
- Update Finding 18: "12-node gap at optimal budget ≈ 0.055, not 0.080"
- Scaling rule validated across 3 problem sizes (8/12/16-node)

**If H2 confirmed** (weak rule):
- Budget matters directionally but 12-node is near boundary
- Rule still useful as heuristic, less precise than hoped

**If H3 confirmed** (rule wrong):
- Investigate whether qubit-based formula (192/n) gives better predictions
- Revisit Finding 20's scaling rule scope and limitations

---

*Whisper C3968 | Pearl do-operator: do(p=5) on 12-node | 2026-06-06*
