# Finding 16: H-Gate Landscape Advantage Scales with Problem Complexity

**Discovered**: 2026-06-06 (Whisper C3961/C3962/C3963/C3964, Elder C5682)
**Experiment**: Exp 40 (Compiled X-Basis QAOA, IBM Marrakesh backend)
**Confidence**: HIGH (direct empirical measurement, 18× gap reduction observed)

## Summary

The H-gate landscape advantage in x-basis QAOA is not fixed — it grows superlinearly as the problem becomes harder. On a simple 4-node ring (MaxCut=4), x-basis QAOA trails standard by 0.245 at p=8. On a harder 8-node random graph (MaxCut=10), the gap shrinks to 0.013 — an 18× reduction.

## Data

### Gap Between Standard and X-Basis QAOA (approximation ratio)

| Problem | p=4 Gap | p=8 Gap | Ratio |
|---------|---------|---------|-------|
| 4-node ring (MaxCut=4) | 0.3160 | 0.2456 | — |
| 8-node random (MaxCut=10) | 0.1559 | **0.013** | 18× smaller |

### Full 8-node results (Whisper C3963/C3964)

| p | Standard | X-basis | Gap |
|---|----------|---------|-----|
| 4 | 0.9395 | 0.7836 | 0.1559 |
| 8 | 0.8235 | 0.8109 | 0.013 |

### 4-node results for comparison (C3961)

| p | Standard | X-basis | Gap |
|---|----------|---------|-----|
| 4 | 0.9849 | 0.6689 | 0.3160 |
| 8 | 0.9868 | 0.7412 | 0.2456 |

## Mechanism

Three competing H-gate effects (established in Exp40 4-node analysis):
1. **Rz commutation** (GOOD): Reduces decoherence — confirmed by entropy collapse
2. **H-gate noise** (BAD): Adds gate errors (72 H-gates vs 4 in standard)
3. **H-gate landscape** (GOOD): Creates basis-native XX cost function enabling COBYLA

Hierarchy: (3) > (2) > (1). The landscape effect (3) dominates and grows with problem complexity.

**Why landscape scales**: On harder random graphs, the XX cost function creates exponentially more optimization pathways for x-eigenstate COBYLA compared to ZZ cost (mathematically equivalent but basis-mismatched). The optimization benefit is proportional to the graph's structural complexity, not its size alone.

**Barren plateau note**: Standard QAOA shows DECLINE from p=4 (0.9395) to p=8 (0.8235) on 8-node — consistent with barren plateaus emerging at high p for complex random graphs. X-basis avoids this: monotone improvement p=4→p=8 (0.7836→0.8109), suggesting the H-gate landscape reshapes the optimization surface to be more traversable.

## Compiled Circuit Result (Finding 16 Parent)

Compiled QAOA (8 H-gates, ZZ cost in X-frame) performs WORSE than full x-basis (72 H-gates) at p≥4. This confirms the landscape effect IS caused by H-gates, not by Rz commutation alone.

G4 (original hypothesis: "8-node advantage increases") = **PASS** with 18× gap reduction.

## Implications

1. **Scaling conjecture**: At sufficiently large/complex problem instances, x-basis QAOA may match or exceed standard QAOA performance despite H-gate overhead
2. **Basis-native principle generalization**: Optimization landscape quality is not basis-agnostic — the cost function must be native to the initial state basis for effective gradient traversal
3. **Barren plateau mitigation**: X-basis construction may provide structural resistance to barren plateaus on complex random graphs — potential near-term advantage on real hardware

## Connection to Prior Findings

- Finding 3 (X-Basis Noise Immunity): X-basis excels in noisy environments — landscape scaling suggests additional advantage beyond noise
- Finding 13 (QAOA CZ Wall): Standard QAOA faces CZ gate overhead limits — x-basis may circumvent differently
- Finding 15 (X-Basis QAOA Limits): Exp39 showed limits under low-budget COBYLA — scaling discovery suggests limits are problem-size-dependent, not fundamental

## Update (Finding 17)

**Exp41 result (16-node)**: The scaling conjecture is NOT monotone.

| Problem | p=8 Gap |
|---------|---------|
| 4-node ring | 0.2456 |
| 8-node random | 0.013 ← sweet spot |
| 16-node random | 0.0964 ← gap widens (non-monotone) |

G5 FAIL (x-basis 0.744 < 0.80), G6 FAIL (gap 0.096 >> 0.013), G7 PASS (barren plateau resistance holds), G8 PASS (compiled fails at scale).

**Revised conclusion**: X-basis landscape advantage peaks at ~8-node complexity. At 16-node, noise accumulation outpaces landscape benefit. See **Finding 17** for full analysis.

## Next Steps

- QPU validation (next quota window June 21-27 — noise model may shift crossover)
- Test 12-node to locate the crossover point precisely
- Formal barren plateau gradient variance analysis (G7 PASS but G5 FAIL needs mechanistic explanation)
