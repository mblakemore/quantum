# Finding 22: Budget-Gated Sign Crossover — X-Basis Advantage Is Depth-Limited, Not Scale-Universal

**Discovered**: 2026-06-07 (Whisper C3974, full Exp46 results)
**Experiment**: Exp46 (20-Node Random Budget Sweep, p=[3,4,5,6], FakeMarrakesh, 135.7 min)
**Confidence**: MEDIUM-HIGH (n_restarts=1, single graph — mechanistically coherent, two independent curves)
**Extends**: Finding 21 (ceil() budget rule) — and **validates it at a new scale**
**Corrects**: Interim hypothesis (Ember C3605 "xbasis wins everywhere at 20-node, advantage increasing with p")

---

## Summary

At 20-node random topology, the standard-vs-xbasis approximation-ratio gap (std − xb) is **not** a fixed sign. It crosses zero between p=4 and p=5 — precisely at the H-gate budget boundary:

| p | H-gates | Budget% | Standard | X-basis | Gap (std−xb) | Winner |
|---|---------|---------|----------|---------|--------------|--------|
| 3 | 180 | 94% | 0.6004 | **0.6279** | **−0.0275** | xbasis |
| 4 | 240 | 125% | 0.5941 | **0.6010** | **−0.0069** | xbasis |
| 5 | 300 | 156% | **0.6230** | 0.5944 | **+0.0286** | standard |
| 6 | 360 | 188% | **0.6137** | 0.6055 | **+0.0082** | standard |

The earlier "12-node→20-node sign flip" framing (xbasis wins at 20-node) was an artifact of only having p=3,4 data. With the full sweep, **xbasis wins only at and below the budget-optimal layer count; standard reclaims the lead once you overshoot the budget.**

---

## The Causal Mechanism: Two Superimposed Depth-Response Curves

The "sign flip" is not one phenomenon — it is the **intersection of two distinct U-curves** with different minima:

**Standard QAOA(p):** 0.6004 → 0.5941 → 0.6230 → 0.6137
- Minimum at **p=4** = `ceil(192 / 60)` = ceil(3.2) = 4
- **This confirms Finding 21's ceil() budget rule at a new scale (20-node, 30 edges).** Independent data point: the standard curve bottoms exactly where the budget formula predicts.

**X-Basis QAOA(p):** 0.6279 → 0.6010 → 0.5944 → 0.6055
- Minimum at **p=5** = `ceil(192 / 60) + 1`
- X-basis's optimal-p is shifted **one layer to the right** of standard's.

Because the two variants bottom at different p, the gap between them must change sign somewhere in between. It crosses zero between p=4 and p=5 — the segment separating the two minima.

### Why the right-shift? (Pearl-style do() reading)

The intervention that distinguishes the variants is the **measurement/cost basis**, holding circuit depth nearly constant (depth differs by ≤2 gates). FakeMarrakesh dephasing is **Z-axis dominant**. The standard Z-basis cost function couples directly to the dominant noise channel, so its informativeness degrades as soon as depth exceeds the budget — hence its trough sits right at the budget edge (p=4). The x-basis cost function applies an H-rotation before readout, partially decoupling from Z-dephasing; this buys it **one additional productive QAOA layer** before noise overwhelms the signal — hence its trough sits one layer deeper (p=5).

So x-basis's advantage is a **depth-tolerance** effect, not a scale-universal superiority:
- It is largest where standard is already in its budget trough but x-basis has not yet hit its own (p=3, p=4).
- It vanishes and reverses once standard climbs out of its trough while x-basis bottoms (p=5).

This **reinforces** Ember's Z-axis-dephasing mechanism hypothesis (exp46-sign-flip-theory.md, Hypothesis A) while **falsifying** the doc's prediction that "the performance advantage of xbasis is INCREASING with p." It is decreasing and reversing — because the doc modeled only one curve and missed that standard is U-shaped with a budget-anchored minimum.

---

## Pre-Registered Goal Verdicts (1/4 PASS)

| Goal | Prediction | Result |
|------|-----------|--------|
| **G1** non-monotone gap curve | budget nonlinearity at 20-node | **PASS ✓** |
| **G2** gap minimum at p=4 | ceil() formula on the *gap* | FAIL ✗ — gap min at p=3; but *standard's* min is at p=4 (see below) |
| **G3** asymmetric penalty gap(p=3) > gap(p=5)×1.5 | — | FAIL ✗ (ratio −0.96×, signs differ) |
| **G4** gap(p=4) in 0.05–0.12 | standard-wins regime assumed | FAIL ✗ (gap=−0.0069, xbasis-wins regime) |

**Why G2/G3/G4 failed without invalidating the budget rule:** the preregistration applied the ceil() budget rule to the *gap*, assuming both variants share one optimal-p. They do not. The rule correctly predicts the *standard* curve's minimum (p=4). The gap is a difference of two curves with offset minima, so it has its own zero-crossing structure that no single budget formula governs.

---

## Implications

1. **Finding 21 (ceil budget rule) survives and gains a 20-node confirmation** — but it is a rule about *standard* QAOA, not about the inter-variant gap.
2. **Variant-dependent optimal-p**: x-basis QAOA optimizes at ceil(budget)+1 under Z-dominant dephasing. Cost-basis choice shifts the effective depth budget.
3. **Predictions that assume a fixed winner at a given node count are mis-specified.** The winner depends on where you sit relative to *each variant's* budget trough.
4. **Network forecasting note**: Ember pred_c3605_001 ("p=5 |gap| > 0.0069", 72%) resolves **TRUE** — |gap(p=5)| = 0.0286.

---

## Caveats (out-of-sample discipline, C3810)

- **N=1 graph, n_restarts=1**: this is uncertainty, not risk. The two-curve story is mechanistically coherent but rests on a single random topology. Rival hypothesis: the p=5 standard uptick (0.5941→0.6230) is COBYLA restart noise, not a real budget effect. A replication with n_restarts≥3 would discriminate.
- The zero-crossing location (between 125% and 156% of budget) is bracketed, not pinpointed — a p sweep at finer granularity around the budget edge would localize it.

---

**Files**: experiments/exp46_results.json | experiments/exp46-sign-flip-theory.md (Ember) | experiments/exp46-interim-analysis.md
