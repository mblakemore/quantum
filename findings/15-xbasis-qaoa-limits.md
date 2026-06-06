# Finding 15: X-Basis QAOA — Commutation Advantage is Structural, Not Practical

**Status**: CONFIRMED (FakeMarrakesh, Exp38 + Exp39)
**Discovery cycle**: Whisper C3943 (pre-reg) / Elder C5656 (Exp38) / Whisper C3946 (Exp39)
**Experiments**: Exp38 (COBYLA-optimized), Exp39 (low-budget sweep)

---

## Summary

The commutation principle (Finding 03: X-basis measurement reduces noise 3×; Finding 14: cos²η continuous law) does NOT extend to practical approximation-ratio advantage in X-basis QAOA mixer design on current NISQ hardware.

**Two-level structure discovered**:

| Level | X-basis effect | Implication |
|-------|---------------|-------------|
| Native circuit structure (entropy, heuristic params) | 18× entropy reduction (G3 PASS, Exp38) | Real: commutation preserves circuit coherence |
| Optimized performance (COBYLA, 3 restarts) | Standard QAOA r=0.992 vs X-basis r=0.746 (G1 FAIL) | Standard strictly preferable in practice |

---

## Root Cause (Pearl Causal Diagram)

```
X-basis QAOA design:
  Path A: Rz mixer → commutes with Z-dephasing → reduces mixer decoherence [SMALL benefit]
  Path B: XX cost layer → H-CX-Rz-CX-H → 32 extra H gates at p=4 → +9.6% error [LARGE cost]

  Net effect: Path B dominates → X-basis MORE noisy than standard

Standard QAOA:
  Rx mixer → some Z-dephasing → decoherence cost (not eliminated by commutation)
  ZZ cost layer → CX-Rz-CX → FEWER gates → LESS decoherence
  COBYLA → navigates noise landscape → finds good params regardless

  Net effect: LESS noisy + better optimizable
```

**do-calculus interpretation**: `do(use X-basis)` activates BOTH Path A (commutation benefit) and Path B (H-gate cost). Exps 38-39 measure `Net(A + B) < 0` on current hardware.

**Exp40 test**: `do(use X-basis AND remove H-gate overhead via native compilation)` — isolates Path A alone.

---

## Quantitative Evidence

### Exp38 (4-node ring MaxCut, COBYLA 3 restarts, 1024 shots)

| p  | Standard r | X-basis r | Standard Entropy | X-basis Entropy |
|----|-----------|-----------|-----------------|-----------------|
| 4  | 0.989     | 0.677     | 0.998           | **0.054**       |
| 8  | **0.992** | 0.746     | 0.997           | **0.056**       |
| 16 | 0.988     | 0.733     | 0.998           | **0.065**       |

X-basis entropy 18× lower (G3 PASS) — commutation preserves native circuit structure.
Standard QAOA approximation ratio 32% better (G1 FAIL) — COBYLA compensates for noise.

### Exp39 (low-budget COBYLA sweep, p∈{1,4})

| Budget | Standard r (p=4) | X-basis r (p=4) |
|--------|-----------------|-----------------|
| 10     | 0.898           | 0.475           |
| 50     | 0.965           | 0.670           |

Standard dominates at ALL budgets. Gap WIDENS at higher p (standard improves more). X-basis does NOT show advantage at low budget — the optimization landscape hypothesis is not supported.

---

## Scope and Generalization

**Confirmed (FakeMarrakesh)**: 4-node ring MaxCut. These results are noise-model simulations.

**Generalization risk**: 
- 4-node ring is the SIMPLEST MaxCut instance (2 optimal solutions, 8 COBYLA parameters at p=4). COBYLA may easily solve it regardless of noise.
- Larger/harder instances (8-12 nodes, dense random graphs) may expose the commutation advantage — not yet tested (Exp40 target).

**H-gate overhead caveat**: The finding is specific to the XX cost layer implementation using H-H wrapping. Native-gate compilation (Exp40) may alter the result.

---

## Relationship to Prior Findings

| Finding | Domain | Status |
|---------|--------|--------|
| Finding 03: X-basis 3× quieter for READOUT | Measurement choice | UNAFFECTED — different application |
| Finding 14: cos²η continuous law for READOUT | Measurement choice | UNAFFECTED — different application |
| Finding 15 (this): X-basis QAOA MIXER | Circuit structure | NEGATIVE — standard preferable in practice |

The commutation principle is **context-dependent**:
- READOUT context (Findings 03, 14): X-basis choice reduces noise by commutation with dominant Z-dephasing channel → applies measurement-only, no H-gate overhead
- CIRCUIT DESIGN context (Finding 15): X-basis mixer requires H-gate wrapping → H-gate cost dominates commutation benefit

---

## Practical Implications

1. **For quantum optimization on NISQ**: Use standard QAOA + COBYLA. X-basis QAOA as currently implemented is strictly worse.
2. **For compilation strategy**: The commutation principle is real but must account for ALL gates, not just the target gate.
3. **For Finding 03/14 extension**: The principle generalizes to readout improvement; does not generalize to arbitrary circuit structure changes without gate-count accounting.
4. **For Exp40**: Test whether native compilation (H-gate-free XX cost) restores the commutation advantage — direct Pearl Rung 2 intervention on the root cause.

---

## Open Questions

1. Does X-basis advantage appear on harder MaxCut instances (8-12 nodes)?
2. Does H-gate-free compilation (Exp40) restore the approximation ratio advantage?
3. Are there hardware conditions (lower H-gate error rate, different calibration) where X-basis QAOA becomes practical?
4. Does the entropy advantage (G3 PASS) translate to faster convergence in non-COBYLA optimizers?

---

*Experiments: 38 (FakeMarrakesh, Whisper/Elder), 39 (FakeMarrakesh, Whisper)*
*Pre-registration: Whisper C3943, C3944*
*Follow-up: Exp40 (Whisper C3952 pre-registration)*
