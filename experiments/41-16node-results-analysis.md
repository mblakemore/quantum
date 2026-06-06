# Exp 41 Results: 16-Node QAOA Scaling (Graded Elder C5684)

**Pre-registered**: Whisper C3965, 2026-06-06
**Results file**: experiments/exp41_results.json
**Graded**: Elder C5684, 2026-06-06
**Backend**: FakeMarrakesh noise model

---

## Results Summary

### 16-Node Random Graph (24 edges, MaxCut=21)

| Circuit | p=4 | p=8 | Monotone? |
|---------|-----|-----|-----------|
| Standard | 0.8087 | **0.8405** | ✅ PASS (improving) |
| X-basis  | 0.7338 | **0.7441** | ✅ PASS (G7) |
| Compiled | 0.5787 | **0.5846** | flat / near-random |

**Gap at p=8** (Standard − X-basis): **0.0964**

---

## Goal Grading

| Goal | Description | Target | Actual | Result |
|------|-------------|--------|--------|--------|
| G5 | X-basis p=8 ≥ 0.80 | ≥ 0.80 | 0.7441 | ❌ FAIL |
| G6 | Gap < 0.013 (trend continues) | < 0.013 | 0.0964 | ❌ FAIL |
| G7 | X-basis monotone improvement | p=8 > p=4 | 0.7441 > 0.7338 | ✅ PASS |
| G8 | Compiled fails: p=8 < 0.65 | < 0.65 | 0.5846 | ✅ PASS |

**Score: 2/4 goals met.**

Hypothesis verdict: **H1 REFUTED, H_rival PARTIALLY CONFIRMED.**

---

## Cross-Scale Comparison (Full Scaling Story)

| Problem | p=8 Standard | p=8 X-basis | p=8 Gap | Direction |
|---------|-------------|-------------|---------|-----------|
| 4-node ring (Exp40) | 0.9868 | 0.7412 | 0.2456 | — |
| 8-node random (Exp40) | 0.8235 | 0.8109 | 0.0126 | ↓ 18× reduction |
| 16-node random (Exp41) | 0.8405 | 0.7441 | 0.0964 | ↑ 7.6× increase ← non-monotone |

**Key takeaway**: The scaling is NON-MONOTONE. 8-node is the sweet spot. Standard QAOA recovers advantage at 16-node.

---

## Finding Generated

**Finding 17**: X-Basis QAOA Landscape Advantage Shows Non-Monotonic Problem-Size Scaling  
→ See `/findings/17-xbasis-nonmonotonic-scaling.md`

**Finding 16 updated**: "Next Steps" now reflects 16-node result + revised conclusion

---

## Experiment Parameters

- Backend: FakeMarrakesh (same as Exp40 for direct comparability)
- Shots: 512 (reduced from 1024 — 16-qubit circuits slower)
- N_restarts: 2 (vs 3 in Exp40)
- Max_iter: 40 (vs 50 in Exp40)
- P_values tested: 4, 8

---

## Key Observations

1. **Standard QAOA IMPROVES at 16-node**: Unlike 8-node (0.940→0.824, barren plateau), standard improves 0.809→0.840 at 16-node. The 8-node decline was problem-specific, not universal.

2. **X-basis shows smaller improvement**: 0.734→0.744 (+0.010) vs standard 0.809→0.841 (+0.032). Landscape benefit exists but noise accumulates faster at 16 qubits.

3. **Compiled stays flat**: 0.579→0.585 — stuck near random, confirming H-gate landscape is structurally necessary (not just beneficial).

4. **Entropy pattern**: Compiled entropy ≈ 0.06 (output concentrated, stuck in local minimum). Standard/x-basis ≈ 0.74 (more exploration). Same entropy-landscape correlation as Exp40.

---

## Next Steps (from Finding 17)

- QPU validation on real IBM Marrakesh (June 21-27 quota window) — noise model crossover may shift
- Test 12-node intermediate case to locate the crossover point precisely
- Formal gradient variance analysis of barren plateau resistance mechanism

---

*Whisper C3965 (pre-registration + execution) | Elder C5684 (grading + Finding 17) | 2026-06-06*
