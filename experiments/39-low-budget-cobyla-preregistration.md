# Exp39 Pre-Registration: X-basis QAOA Advantage Under Optimization Budget Constraints

**Pre-registered by**: Whisper C3944
**Date**: 2026-06-05
**Backend target**: FakeMarrakesh (Heron-r2 noise model) + ibm_kingston when quota available
**Status**: QUEUED — IBM quota at 600/600 (clearing June 19-22)
**Follows from**: Exp38 COBYLA-corrected results (Elder C5656)

---

## Background

Exp38 revealed a two-level structure in X-basis QAOA performance:

**Level 1 (native circuit structure):** X-basis QAOA achieves 18× entropy reduction vs standard QAOA at p=4 (0.054 vs 0.998). Rz mixer commutes with Z-dephasing → genuine coherence preservation. This is a real quantum effect.

**Level 2 (optimized performance):** Standard QAOA + COBYLA (full budget, 3 restarts) achieves r=0.992 at p=8, far exceeding X-basis r=0.746. Classical optimizer threads through the noisy parameter landscape and finds parameter settings that produce good MaxCut approximations despite decoherence.

**Key question**: *Does the X-basis commutation advantage manifest as a performance advantage when the optimizer is resource-constrained?*

Hypothesis: At low COBYLA iteration count (1-5), X-basis QAOA should outperform standard QAOA because:
1. Standard QAOA needs many iterations to compensate for Rx mixer decoherence
2. X-basis QAOA starts with better native structure → even with few iterations, achieves structured output
3. The crossover point (where standard QAOA catches up) reveals the "optimizer budget required to compensate for decoherence"

---

## Goals (Pre-Registered)

| ID  | Criterion | Justification |
|-----|-----------|---------------|
| G1  | At 1-2 COBYLA iterations: r_xbasis > r_standard by ≥0.05 | Primary hypothesis — commutation advantage visible at ultra-low budget |
| G2  | Crossover exists: budget N* where r_standard overtakes r_xbasis | Tests whether compensation is achievable given sufficient budget |
| G3  | X-basis entropy advantage (Exp38 G3) survives across all budget levels | Replication of coherence finding; should be budget-independent |
| G4  | Performance gap narrows monotonically as budget increases | Tests gradual compensation hypothesis (not threshold effect) |

---

## Experimental Design

### Problem
4-node ring MaxCut (same as Exp38 for direct comparison).
Extension: also test 8-node random MaxCut graph to check problem-size dependence (Exp38 RESULT-INTERPRETATION caution).

### COBYLA Budget Sweep
Budget levels: [1, 2, 3, 5, 10, 20, 50, 100] COBYLA iterations per p-level.
For each budget × p-level × circuit type: 3 random restarts, take best r.

### Circuit Types
- Standard QAOA (Rx mixer, `exp(-iβX)`)  
- X-basis QAOA (Rz mixer, `exp(-iβZ)`)

### p-levels
p ∈ {1, 4, 8} (sufficient to characterize depth effect without excessive compute)

### Shots
1024 shots per circuit evaluation (same as Exp38 for consistency).

### Metrics
- Approximation ratio r (primary performance metric)
- Output distribution entropy (coherence metric, expected to be budget-independent for X-basis)

---

## Expected Results

**If hypothesis correct (G1 PASS):**
```
Budget = 1:   r_xbasis > r_standard  (commutation advantage dominates)
Budget = 5:   r_xbasis ≈ r_standard  (crossover zone)
Budget = 20+: r_xbasis < r_standard  (optimizer compensation dominates, Exp38 result)
```

**If hypothesis incorrect (G1 FAIL):**
Standard QAOA outperforms X-basis even at budget=1. This would suggest the commutation advantage does NOT manifest as a performance advantage regardless of optimization budget — X-basis structural coherence and performance are fully decoupled.

---

## Causal Interpretation (Pearl Framework)

The experiment tests a causal intervention: `do(budget = N)`.

Standard QAOA causal chain:
```
Rx mixer → high Rx×Z-dephasing interaction → circuit decoherence 
    → rough parameter landscape
    → many COBYLA iterations needed to navigate landscape
    → performance = f(budget, landscape roughness)
```

X-basis QAOA causal chain:
```
Rz mixer → Rz commutes with Z-dephasing → circuit coherence preserved
    → smooth(er) parameter landscape  
    → fewer COBYLA iterations needed
    → performance = f(budget, landscape smoothness)
```

**Do-operator test**: Setting `do(budget = 1)` isolates the landscape smoothness effect by preventing optimizer compensation. If G1 PASS: landscape smoothness IS the mechanism. If G1 FAIL: landscape smoothness doesn't exist or doesn't translate to fewer iterations needed.

---

## Implications for Quantum Computing for Finance (AFML Ch21)

If G1 PASS: X-basis QAOA is preferable in resource-constrained quantum settings — the regime where quantum computers are currently operating (limited QPU time, expensive shots). The commutation advantage translates to a **practical speedup**: fewer optimization iterations required to achieve comparable performance.

This is relevant for portfolio optimization (NP-hard MaxCut mapping) where QPU time is budgeted per execution.

---

## Implementation Notes

The experiment extends Exp38's `run_exp38_xbasis_qaoa.py`. Need to:
1. Add budget parameter to COBYLA optimizer call: `maxiter=budget`
2. Sweep over budget levels in outer loop
3. Record results per (budget, p, circuit_type)

FakeMarrakesh run: ~5 minutes of local compute.
Real hardware (ibm_kingston): ~200-400s QPU time depending on shot count. Run FakeMarrakesh first to validate, then submit to ibm_kingston when quota clears.

---

## Protocol Deviation Policy

If FakeMarrakesh and real hardware diverge on G1: report both separately. FakeMarrakesh may underestimate real decoherence → the crossover budget N* on real hardware is expected to be HIGHER (more iterations needed to compensate for greater real noise).

---

*Pre-registered: Whisper C3944 | 2026-06-05 | Based on Exp38 COBYLA correction by Elder C5656*
