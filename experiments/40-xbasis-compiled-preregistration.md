# Exp 40 Pre-Registration: X-Basis QAOA with H-Gate-Free Compilation
**Pre-registered**: Whisper C3952, 2026-06-06
**Planned run**: June 26-27, 2026 (FakeMarrakesh sim; QPU if quota allows)
**Builds on**: Exp38 (G3 PASS: entropy advantage), Exp39 (G1-G4 FAIL: H-gate overhead root cause)

---

## Research Question

**Causal structure (Pearl framework)**:

Exp39's root cause analysis identified TWO conflated pathways in X-basis QAOA:

```
X-basis QAOA:
  Path A: Rz mixer → commutes with Z-dephasing → reduces mixer decoherence [BENEFIT]
  Path B: XX cost via H-CX-Rz-CX-H → 32 extra H gates at p=4 → increases error [COST]
  
Exp38/39 measured: Net(A + B) < 0  (cost dominates benefit on current hardware)
```

**Counterfactual (Rung 3)**: If we had designed X-basis QAOA without Path B's H-gate cost, would the commutation advantage from Path A produce measurable approximation ratio improvement?

**do-calculus intervention**: do(use X-basis mixer, compiled without H-gate overhead) by synthesizing the XX cost operator natively from the hardware's CZ basis without wrapping in Hadamards.

---

## Hypothesis

**H0 (null)**: Standard QAOA outperforms X-basis QAOA regardless of compilation strategy.

**H1 (primary)**: When H-gate overhead is eliminated via native-gate compilation, X-basis QAOA achieves approximation ratio r ≥ r_standard + 0.05 at some depth p.

**Causal mechanism for H1**:
- Native X-basis compilation reduces XX cost to native CZ gates without H wrapping
- Rz mixer still commutes with dominant Z-dephasing noise channel
- Net effect becomes positive: commutation benefit > (now reduced) gate overhead

---

## Experimental Design

### Circuits to Compare
1. **Standard QAOA**: ZZ cost (CX-Rz-CX) + Rx mixer (Ry(π/2)-Rz-Ry(-π/2))
2. **Standard X-basis QAOA** (Exp38/39 design): XX cost (H-CX-Rz-CX-H) + Rz mixer
3. **Compiled X-basis QAOA** (NEW): XX cost synthesized from native CZ+Rz (no H wrapping) + Rz mixer

### Native Compilation Strategy for Circuit 3
The XX interaction can be decomposed WITHOUT Hadamards using the identity:
```
XX(θ) = CZ · Ry(π/2) ⊗ Ry(π/2) · Rz(θ) ⊗ I · Ry(-π/2) ⊗ Ry(-π/2) · CZ
```
Or equivalently, via basis transformation at the start/end of the circuit only (absorb H into initial state prep and final measurement), rather than repeating H gates at each layer.

**H-gate count**:
- Standard X-basis (Exp39): 4 edges × p layers × 4 H gates = 16p H gates total
- Compiled X-basis (Exp40): 4 H gates (state prep only, once) + 4 H gates (measurement, once) = 8 H gates total
- Reduction: 8 vs 16p — at p=4, 8 vs 64 H gates

### Problem
- 4-node ring MaxCut (same as Exp38/39 for direct comparison)
- 8-node random 3-regular MaxCut (NEW — harder landscape, COBYLA may struggle)

### Optimizer
- COBYLA, 3 restarts, 50 iterations max (same as Exp38 for comparability)

### Depth values
- p ∈ {1, 4, 8, 16}

### Backend
- FakeMarrakesh (noise model, no quota) — primary
- ibm_marrakesh (real hardware) — if quota available June 26-27

### Shots
- 1024 (same as Exp38)

---

## Goals and Falsifiability

| Goal | Criterion | Type |
|------|-----------|------|
| G1 | Compiled X-basis achieves r ≥ r_standard + 0.05 on 4-node ring at some p | Approximation advantage |
| G2 | Compiled X-basis entropy < Standard QAOA entropy at p≥4 (Exp38 G3 replication in new circuit) | Structural advantage |
| G3 | Compiled X-basis approximation ratio ≥ Standard X-basis ratio (Exp38/39) at all p | H-gate removal helps |
| G4 | On 8-node MaxCut, compiled X-basis advantage increases relative to 4-node (landscape effect) | Problem-size scaling |

**If G1 PASSES**: H-gate overhead was the confound. Commutation principle holds at approximation level when properly implemented. Major finding — X-basis QAOA viable with correct compilation.

**If G1 FAILS but G3 PASSES**: H-gate removal helps but not enough. The Rz commutation benefit is too small relative to other noise sources on current hardware. Standard QAOA remains preferable.

**If G1 FAILS and G3 FAILS**: Compilation strategy does not matter. The underlying X-basis structure is fundamentally less compatible with COBYLA optimization regardless of gate count. The commutation advantage is purely structural (entropy), not functional (approximation ratio).

---

## Connection to Prior Findings

| Finding | Exp | Relevance |
|---------|-----|-----------|
| Finding 03: X-basis 3× quieter (measurement choice) | 10-19 | Original commutation principle — for READOUT |
| Finding 14: Commutation follows cos²η law | 36 | Confirmed mechanism — for READOUT |
| Exp38: X-basis entropy 18× lower at heuristic params | 38 | Structural advantage real — but COBYLA compensates |
| Exp39: H-gate overhead dominates | 39 | Root cause of failure — this experiment removes it |

**The causal chain this experiment completes**:
```
Original hypothesis (Finding 3): "Measure in X-basis for quieter circuits"
                        ↓
QAOA extension (Exp38 pre-reg): "Use X-basis as mixer for QAOA"
                        ↓
Failure diagnosis (Exp39): "H-gate overhead cancels commutation benefit"
                        ↓
Causal intervention (Exp40): "do(remove H-gate overhead) — what remains?"
```

---

## Protocol Deviation Rules
- If native compilation produces gates not in Heron backend basis: abort and document
- If FakeMarrakesh runtime > 4 hours: reduce to p ∈ {1, 4} only
- If 8-node MaxCut has ground truth ambiguity: report Goemans-Williamson bound ratio instead

---

## Expected Runtime
- FakeMarrakesh: ~2-4 hours total (4 p values × 3 circuits × 3 restarts × 1024 shots)
- QPU: ~80-120s (if run on ibm_marrakesh at p={4,8} only)

---

## Significance
This experiment directly tests whether the X-basis commutation principle — validated for MEASUREMENT choice (Findings 3, 14) — can be extended to CIRCUIT DESIGN (mixers, cost layers) when implementation overhead is correctly controlled. The answer determines whether X-basis compilation is a viable strategy for quantum optimization on NISQ hardware, or whether the principle is limited to readout-only contexts.

*Pearl Rung 2 experiment: do(compile without H overhead) and observe whether approximation ratio improves — isolating the causal effect of commutation from the confound of gate overhead.*
