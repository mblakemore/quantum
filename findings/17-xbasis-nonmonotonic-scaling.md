# Finding 17: X-Basis QAOA Landscape Advantage Shows Non-Monotonic Problem-Size Scaling

**Discovered**: 2026-06-06 (Whisper C3965, Elder C5684)
**Experiment**: Exp 41 (16-Node QAOA Scaling Extension)
**Confidence**: HIGH (direct empirical measurement, pre-registered goals evaluated)
**Extends**: Finding 16 (H-Gate Landscape Scaling — Exp40)

---

## Summary

The H-gate landscape advantage in x-basis QAOA does **not** scale monotonically with problem size. The gap between standard and x-basis QAOA is smallest at 8-node complexity (the "sweet spot"), then widens again at 16-node. The 8-node result was not a preview of asymptotic behavior — it represented an intermediate optimal zone.

**The rival hypothesis (H_rival from Exp41 pre-registration) is partially vindicated**: the gap does not continue shrinking at 16-node.

---

## Data

### Complete Gap Scaling Table (Standard - X-Basis Approximation Ratio at p=8)

| Problem | Nodes | Edges | p=8 Gap | Change |
|---------|-------|-------|---------|--------|
| 4-node ring (MaxCut=4) | 4 | 4 | 0.2456 | — |
| 8-node random (MaxCut=10) | 8 | 12 | **0.0126** | **18× reduction** |
| 16-node random (MaxCut=21) | 16 | 24 | **0.0964** | 7.6× increase ← non-monotone |

### Exp41 Full Results (FakeMarrakesh, 16-node)

| Circuit | p=4 | p=8 | Monotone? |
|---------|-----|-----|-----------|
| Standard | 0.8087 | **0.8405** | PASS (improving) |
| X-basis  | 0.7338 | **0.7441** | PASS (improving, G7) |
| Compiled | 0.5787 | **0.5846** | flat (near-random) |

**p=8 gap**: Standard 0.8405 − X-basis 0.7441 = **0.0964**

---

## Goal Evaluation (Exp41 Pre-Registration, Whisper C3965)

| Goal | Description | Result |
|------|-------------|--------|
| G5 | X-basis p=8 ≥ 0.80 (matches 8-node) | **FAIL** (0.7441 < 0.80) |
| G6 | Gap (standard − x-basis) < 0.013 | **FAIL** (0.0964 >> 0.013) |
| G7 | X-basis monotone improvement p=4→p=8 | **PASS** (0.7338 → 0.7441) |
| G8 | Compiled p=8 < 0.65 (structural failure replicates) | **PASS** (0.5846 < 0.65) |

Score: 2/4 goals met. H1 (primary) REFUTED. H_rival partially confirmed.

---

## Mechanism

Three effects from Finding 16 still apply:
1. **Rz commutation** (GOOD): reduces decoherence
2. **H-gate noise** (BAD): 72+ H-gates per circuit layer
3. **H-gate landscape** (GOOD): XX cost enables basis-native COBYLA

**Why the sweet spot is at 8-node**:

At 16 qubits, two forces compete:
- **Landscape benefit** scales with graph structural complexity (cross-connections, longer paths)
- **H-gate noise burden** scales with circuit size (more qubits × more edges = more H-gates per layer)

At 8-node: landscape benefit dominates → gap collapses to 0.013  
At 16-node: noise burden accumulates faster → standard QAOA recovers advantage  

The "optimal zone" for x-basis appears to be intermediate complexity (roughly 8-12 qubits) where structural landscape benefit exceeds gate-noise accumulation.

**Key contrast**: Standard QAOA IMPROVES monotonically at 16-node (0.809→0.840) while x-basis improves less (0.734→0.744). Standard's ZZ cost naturally scales — fewer H-gates means noise scales slower. Standard recovers cleanly at 16-node depth advantage.

---

## What G7/G8 PASS Tells Us

Despite the gap widening, two critical findings hold:

**G7 PASS (barren plateau protection generalized)**: X-basis QAOA still improves p=4→p=8 at 16-node, unlike standard QAOA at 8-node which DECLINED (0.940→0.824). This suggests x-basis maintains some barren-plateau resistance even when it cannot match standard quality.

**G8 PASS (compiled failure is structural)**: Compiled QAOA (8 H-gates) achieves only 0.585 at 16-node — confirming the H-gate landscape is NECESSARY for x-basis performance, not just beneficial. Removing H-gates (compiled) while keeping the x-basis cost function destroys the optimization.

---

## Revised Scaling Picture (Finding 16 → 17 Update)

Finding 16's conjecture: "landscape advantage scales superlinearly with problem complexity"  
Finding 17's correction: **"landscape advantage peaks at intermediate problem size (~8-node), then noise burden dominates"**

This is not a refutation of Finding 16 — it is a refinement:
- The dual H-gate role (noise + landscape) remains confirmed
- The landscape effect IS real and grows with complexity
- But noise accumulation grows FASTER at large qubit counts in NISQ devices
- The "crossover point" where noise > landscape is at approximately 12-16 qubits (FakeMarrakesh noise model)

---

## Implications

1. **NISQ regime sweet spot**: X-basis QAOA may be most valuable at 8-12 qubit problem instances — a near-term hardware range. At larger sizes, noise-corrected circuits or real hardware calibration may shift the crossover.

2. **Hardware dependence**: FakeMarrakesh noise model used throughout. On real IBM hardware (e.g., Marrakesh — 156 qubit, lower native error), the crossover may shift to larger problem sizes. QPU validation would refine this.

3. **Compiled circuit lesson confirmed**: Removing H-gates (Rz commutation alone) is insufficient — the basis-native landscape is the operative mechanism. This closes the Exp40 G4 story definitively at 16-qubit scale.

4. **Barren plateau asymmetry**: Standard QAOA barren plateaus emerge at 8-node p=4→p=8 (gap opens), but standard RECOVERS at 16-node (improves with depth). X-basis avoids plateau at both scales but never matches standard at 16-node.

---

## Connection to Prior Findings

- **Finding 16** (parent): H-gate dual role + 18× gap reduction 4→8 node
- **Finding 15** (X-basis QAOA limits): problem-size-dependent limits, now with mechanism
- **Finding 3** (Noise immunity): x-basis noise immunity is real but insufficient to overcome noise accumulation at 16-qubit scale

---

## Next Steps

- **QPU validation**: Run Exp41 circuits on real IBM Marrakesh (next quota window June 21-27) — noise model may shift crossover point
- **Intermediate sizes**: Test 12-node to locate crossover precisely (where does gap start widening?)
- **Noise model sensitivity**: Run 16-node on FakeNairobi (different noise profile) — does crossover shift?
- **Formal barren plateau analysis**: G7 PASS at 16-node but G5 FAIL suggests partial plateau resistance — formal gradient variance analysis would distinguish mechanism

---

*Found Whisper C3965 (Exp41 pre-registration + execution) | Elder C5684 (grading + Finding 17 write-up) | 2026-06-06*
