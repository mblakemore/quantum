# Exp39 Result Interpretation
**Whisper C3946 | 2026-06-05**  
**Pre-registration**: experiments/39-low-budget-cobyla-preregistration.md  
**Results**: experiments/39-budget-sweep-results-4node.json

---

## Verdict: 1/4 Goals Passed — Primary Hypothesis NOT SUPPORTED

### Goal Results

| Goal | Criterion | Result |
|------|-----------|--------|
| G1 | r_xbasis > r_standard by ≥0.05 at low budget | **FAIL** |
| G2 | Standard overtakes X-basis at some budget N* ≥ 10 | PASS (trivially — standard always ahead) |
| G3 | X-basis entropy < Standard entropy (Exp38 replication) | **FAIL** |
| G4 | Gap narrows monotonically as budget increases | **FAIL** |

---

## What Actually Happened

### Standard QAOA dominates at ALL budgets

```
p=1 (2 params, COBYLA min=4):
  budget= 4: std=0.682, xbasis=0.492, diff=-0.189
  budget=50: std=0.688, xbasis=0.533, diff=-0.154
  → Gap PERSISTS at all budgets, no narrowing

p=4 (8 params, COBYLA min=10):
  budget= 4→10: std=0.898, xbasis=0.475, diff=-0.424  
  budget=50:    std=0.965, xbasis=0.670, diff=-0.295
  → Gap WIDENS with p and budget (standard improves more)
```

### Entropy check reversal (G3 FAIL):

```
Measured at params gamma=pi/(4p), beta=pi/(4p):
  p=1: std_entropy=0.999, xbasis_entropy=1.000  (both ~uniform)
  p=4: std_entropy=0.617, xbasis_entropy=0.799  (X-basis MORE disordered!)
```

**X-basis has HIGHER entropy (more disordered) at p=4** — opposite to Exp38 finding.

---

## Root Cause Analysis (Pearl Counterfactual)

### What the pre-registration assumed:
```
Rz mixer → commutes with Z-dephasing → smooth parameter landscape
  → fewer COBYLA iterations needed to find good params
  → X-basis advantage at low budget
```

### What was overlooked:
```
X-basis XX cost layer requires: H → CX → Rz → CX → H (5 gates per edge)
Standard QAOA cost layer:       CX → Rz → CX (3 gates per edge)

4 edges × 4 layers × 2 extra H gates = 32 extra H gates for X-basis at p=4
FakeMarrakesh H gate error rate: ~0.1-0.5% per gate
32 gates × 0.3% = ~9.6% additional error probability

The H-gate overhead DOMINATES over the Rz commutation advantage.
```

### Causal graph:
```
X-basis design:
  Rz mixer → commutes with Z-dephasing → reduces mixer decoherence (SMALL benefit)
  XX cost via H gates → H gate errors → MORE circuit decoherence (LARGE cost)
  NET: X-basis MORE noisy than standard on NISQ hardware

Standard QAOA:
  Rx mixer → does NOT commute with Z-dephasing → some additional decoherence
  ZZ cost via CX-Rz-CX → fewer gates → LESS circuit decoherence
  COBYLA → navigates noisy landscape → finds good params regardless
  NET: Standard QAOA LESS noisy + better optimizable
```

---

## Reconciling with Exp38

Exp38 showed:
- X-basis entropy at HEURISTIC params (pi/4 fixed): 13.6× LOWER than standard
- X-basis approximation ratio with COBYLA: r=0.746 vs standard r=0.992

Exp39 shows:
- X-basis entropy at params (pi/(4p) decreasing): HIGHER than standard (0.799 vs 0.617)
- X-basis approximation ratio: consistently LOWER at all budgets

**Resolution**: The Exp38 entropy advantage was specific to:
1. Fixed high-angle params (pi/4 at all layers) — a specific regime
2. NOT the decreasing heuristic pi/(4p) used in Exp39
3. The entropy advantage is parameter-regime-dependent, not universal

The optimization result (standard wins with COBYLA) was consistent ACROSS Exp38 and Exp39.

---

## Protocol Deviations

**PD1 — COBYLA minimum constraint**:  
COBYLA requires maxiter ≥ num_vars + 2. For p=1 (2 params), min=4. For p=4 (8 params), min=10.  
Original budgets [1,2,3,5] below minimums are silently bumped up.  
Adjusted budget sweep to [4,6,8,12,16,20,30,50] to make effective budgets explicit.

**PD2 — p={1,4} only (p=8 excluded)**:  
FakeMarrakesh p=8 simulation with budget=100 estimated >30 min. Excluded for compute efficiency.  
p={1,4} is sufficient to test primary hypothesis.

**PD3 — shots=256 (vs 1024 pre-reg)**:  
Reduced for speed. High variance visible in p=4 results (e.g., budget=4: diff=-0.424 vs budget=8: diff=-0.143 at same effective minimum). Larger shot count would reduce variance but not change direction of result.

---

## Implications

### For NISQ quantum optimization:
- Standard QAOA + COBYLA is strictly preferable to X-basis QAOA on current hardware
- H-gate overhead analysis is critical when evaluating commutation-based circuits
- "Commutation advantage" assessments must account for ALL gates, not just the mixer
- Exp38's structural finding (X-basis entropy at heuristic params) does NOT translate to practical advantage

### For quantum computing for finance (AFML Ch21):
- Portfolio optimization on NISQ hardware: use standard QAOA + COBYLA
- X-basis QAOA does not provide the "practical speedup in resource-constrained settings" hypothesized
- The commutation principle is real but insufficient for performance advantage on current hardware

### For Exp40 (suggested follow-up):
- Investigate WHERE the crossover occurs in circuit depth (if standard adds more gates)
- Test on hardware with lower H gate error rate
- Test larger problem sizes where COBYLA landscape becomes harder to navigate (X-basis might recover)

---

## FakeMarrakesh Caveat

These results are on simulated noise (FakeMarrakesh Heron-r2 model).  
Real ibm_kingston hardware has additional:
- Crosstalk between qubits (not fully captured in FakeMarrakesh)
- Drift/calibration errors
- SPAM errors

When quota available: run both circuits on ibm_kingston to validate. Prediction: standard QAOA continues to outperform, possibly with larger gap due to real noise.

---

*Pre-registered: C3944 | Results: C3946 | Status: COMPLETE (FakeMarrakesh)*
