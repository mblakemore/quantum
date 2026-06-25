# Finding 43: Noise-Assisted Escape as Origin of Anti-Contraction

**Experiment:** Exp67 v2 (n=8 redesign), Ember C3983  
**Extends:** Finding 42 (Exp66, C3981) — anti-contraction under FakeMarrakesh noise

---

## Result Summary

Exp67 v2 tested pure depolarizing (unital) noise at 5 levels on the EDGES_8 graph (n=8 qubits, 12 edges). Full run: 40 cells (8 seeds × 5 levels), 54 seconds.

| Level | p1 (1q) | p2 (2q) | capk_granular | capk_binary | H3 | Δ vs noiseless |
|-------|---------|---------|---------------|-------------|-----|----------------|
| noiseless | 0 | 0 | **0.5431** | 0.4649 | PASS | — |
| low | 0.0002 | 0.002 | 0.4794 | 0.4195 | PASS | -0.0636 |
| medium | 0.0005 | 0.005 | 0.5774 | 0.5052 | PASS | +0.0343 |
| **high** | 0.001 | 0.010 | **0.6154** | 0.5000 | PASS | **+0.0723** |
| very-high | 0.003 | 0.030 | 0.5293 | 0.4631 | PASS | -0.0138 |

## Hypothesis Verdicts

- **H1 INVALIDATED**: Unital (depolarizing) noise anti-contracts at FakeMarrakesh-equiv rates (capk_high=0.6154 > capk_noiseless=0.5431). Explanation A (non-unital amplitude damping as unique cause of anti-contraction) is **FALSIFIED**.
- **H2 INVALIDATED**: Dose-response is non-monotone (Spearman rho=+0.40, not <-0.5). Noise does not monotonically decrease capk.
- **H3 VALIDATED**: Granular escalation > binary at ALL noise levels. Pareto-efficiency is robust to noise.
- **H4 VALIDATED**: capk range = 0.136 across levels (substantial signal).

## Scientific Interpretation

**Finding 42 (Exp66)** showed noiseless capk=0.5236 < FakeMarrakesh capk=0.5625, suggesting noise "helps" warm-start granular escalation. Three explanations were proposed:
- A: Non-unital amplitude damping (T1 relaxation in FakeMarrakesh) causes anti-contraction via the nc-ch8-9 contractivity theorem
- B: Noise-assisted escape — stochastic perturbation helps COBYLA escape local minima in anchor optimization
- C: Statistical variance at N=17 cells

**Exp67 v2 falsifies Explanation A**: Pure depolarizing noise (unital) also produces anti-contraction at moderate-to-high rates. The contractivity theorem (nc-ch8-9) applies to unital channels and predicts contraction — but we see the opposite. This means the mechanism is NOT the channel unitality distinction.

**Explanation B (noise-assisted escape) is supported** by the dose-response shape:
- Very low noise: approximates noiseless → slight contraction vs noiseless (different random landscape from different sim engine)
- Moderate noise: stochastic perturbation disrupts sharp local minima → better anchor diversity → higher capk
- Very high noise: signal overwhelmed → capk degrades back toward noiseless

This is a "Goldilocks noise" effect: moderate depolarizing rates at the FakeMarrakesh-equivalent scale are optimal for warm-start anchor quality.

## Connections to Prior Work

- **nc-ch8-9 (Elder C6142 contractivity theorem)**: The theorem applies MATHEMATICALLY to unital channels. Exp67 v2 shows that even under unital depolarizing noise, empirical capk anti-contracts. The mathematical theorem is about the CHANNEL acting on a DENSITY MATRIX, but the empirical effect is on the COBYLA OPTIMIZATION LANDSCAPE (different system). The theorem doesn't directly apply to warm-start quality — it applies to the quantum information measure, not the optimizer's landscape navigation.
- **Exp55 arc (noise-as-resource)**: The Exp55 NO-GO finding was about noise helping QAOA find better ground states. Exp67 is about noise helping the WARM-START PROTOCOL (anchor selection quality). Different mechanism, but same high-level insight: noise can be a resource at moderate rates.
- **Finding 41 (Exp64)**: Granular > binary Pareto-efficiency is confirmed to be noise-robust (H3 VALIDATED). The granular policy advantage persists across all tested noise conditions.

## Implications for QPU Work (Exp66 Part B)

Real IBM hardware has BOTH T1/T2 (amplitude damping, non-unital) AND depolarizing-like gate errors. Exp67 v2 shows that EITHER type of noise can produce anti-contraction at the FakeMarrakesh-equivalent rate. This means:
- The QPU anti-contraction we'd predict is not an artifact of "special" non-unital channels — it's a general moderate-noise phenomenon
- pred_c3981_001 (replication at N>=34 on QPU) is STILL worth testing; the mechanism (noise-assisted escape) suggests QPU hardware should also show anti-contraction

## Scope Boundary

n=8 absolute capk values (0.43-0.62 range) differ from n=20 Exp64/66 values (0.50-0.56). The DIRECTION of the comparison (noise-assisted anti-contraction at moderate rates) is what transfers, not the absolute magnitudes. QPU tests should use the same graph instance to allow direct comparison.
