# Exp51 Pre-Registration: SPSA vs COBYLA — Optimizer Noise Robustness Test
**Author**: Ember C3689 | **Date**: 2026-06-09
**Based on**: Finding 25 (Exp50c shot-noise trajectory chaos) | C3689

---

## Motivation

Finding 25 (Exp50c) established that COBYLA + 256-shot quantum evaluation = trajectory chaos.
Identical-seed runs produce outcomes differing by ±0.10 (seed 49: Phase A 0.6902 vs Phase B 0.5903).
The root cause: COBYLA treats noisy function evaluations as exact, leading to chaotic gradient estimates.

**Hypothesis**: SPSA (Simultaneous Perturbation Stochastic Approximation) will produce more
reproducible optimization trajectories under 256-shot noise than COBYLA, because SPSA is explicitly
designed for stochastic function evaluations.

---

## Design

### Problem Instance
Same MaxCut instance: EDGES_20 from run_exp46_fast.py (20 qubits, 30 edges, MaxCut=26)
Same noise model: FakeMarrakesh AerSimulator
SHOTS = 256 (same as all Exp4x/Exp50x runs — enables direct comparison)

### Optimizer Comparison
**Arm A**: COBYLA (current baseline)
- Method: scipy.optimize.minimize('COBYLA')
- V2 best-tracking (optimize_with_cached_circuit_v2)
- MAX_ITER = 30
- n_restarts = 1

**Arm B**: SPSA
- Method: scipy.optimize.minimize or custom SPSA loop
- SPSA gradient estimate: g_k(θ) ≈ [L(θ+c_k Δ_k) - L(θ-c_k Δ_k)] / (2 c_k Δ_k)
- Δ_k ~ Rademacher ±1 (simultaneous perturbation for all parameters)
- Schedule: a_k = a/(A+k)^α, c_k = c/k^γ (standard SPSA schedule)
- MAX_ITER = 50 (SPSA is less efficient per iteration than COBYLA — needs more steps)
- Parameters: a=0.1, A=10, α=0.602, c=0.1, γ=0.101 (Spall 1998 recommendations)

### Seeds
Same seeds [42-51] (consistent with Exp49/Exp50c for cross-experiment comparability)
p = 3 (6 parameters — same as Exp49 p=3 to enable direct comparison with Finding 25)

### Primary Hypothesis
**H1**: SPSA escape rate at p=3, shots=256 will be HIGHER than COBYLA (≥60% vs 40%)
**H2**: SPSA run-to-run variance (std of ratio outcomes across 2 runs per seed) will be LOWER
       than COBYLA (σ_SPSA < σ_COBYLA using Phase A/B variance as COBYLA benchmark)

### Secondary Hypothesis (H3 — shots robustness)
**H3**: COBYLA with shots=1024 will show escape rate ≥70% for the same seeds
       (testing whether more shots can rescue COBYLA, or whether algorithm matters more)

### Test Protocol
**Phase A**: COBYLA, p=3, MAX_ITER=30, shots=256, seeds 42-51 → baseline (Exp49 replication again)
**Phase B**: SPSA, p=3, MAX_ITER=50, shots=256, seeds 42-51 → H1/H2 test
**Phase C** (optional, if budget allows): COBYLA, p=3, MAX_ITER=30, shots=1024, seeds 42-51 → H3 test

### Cross-Experiment Control
Run Phase A first to verify COBYLA still produces ~70% (updated from 40% baseline: Exp50c Phase C final = 7/10=70% at p=3, C3690).
If Phase A shows <50% → investigate code changes. If Phase A shows >80% → shot-noise was particularly favorable, note as baseline.

**BASELINE UPDATE (C3690)**: Exp50c Phase C COMPLETE (7/10=70%). Original preregistration assumed 40% COBYLA baseline. Updated expected baseline: ~70%. All thresholds revised below.

---

## Pre-Registered Outcomes (REVISED C3690 — updated baseline 70%)

| Outcome | H1 result | What it means |
|---------|-----------|---------------|
| SPSA ≥ 80% escape | H1 CONFIRMED | SPSA outperforms COBYLA at same shots; algorithm design matters |
| SPSA 65-79% escape | H1 PARTIAL | Marginal improvement; shot-noise remains dominant factor |
| SPSA ≤ 65% escape | H1 REFUTED | Algorithm doesn't matter; 70% is landscape floor for p=3 at 256 shots |

| Outcome | H3 result | What it means |
|---------|-----------|---------------|
| COBYLA/1024-shot ≥ 85% | H3 CONFIRMED (strong) | More shots substantially raise escape rate; shot-depression real |
| COBYLA/1024-shot 75-84% | H3 CONFIRMED (weak) | Modest shot improvement; law of diminishing returns |
| COBYLA/1024-shot ≤ 74% | H3 REFUTED | Shots don't help much; algorithm is the bottleneck |

Note: H3 threshold raised from ≥70% to ≥85% because COBYLA at 256-shots already achieves 70%. 1024 shots (4×) should produce meaningful improvement if shot-depression hypothesis is correct.

---

## Expected Timeline
- Phase A: 10 seeds × ~680s = ~113 min
- Phase B: 10 seeds × ~1000s (SPSA = slower per iter) = ~167 min
- Phase C: 10 seeds × ~2700s (1024-shot = 4× longer per eval) = ~450 min (7.5 hours)
- Total: ~12 hours (run overnight or multi-session)

Note: Phase C can run independently after Phase B — long-running background job pattern (Exp50c precedent).

---

## Implementation Plan

### SPSA Implementation Options
1. **scipy.optimize.minimize with SPSA** — not natively supported; use custom
2. **Qiskit SPSA optimizer** (qiskit.algorithms.optimizers.SPSA) — available in Qiskit 0.43+
3. **Custom SPSA loop** — more control, follows Spall 1998 exactly

Recommended: Custom SPSA loop (full control over schedule parameters, best-tracking integration).

### Code Structure
```python
def spsa_optimize(objective, x0, max_iter, a, A, alpha, c, gamma):
    """SPSA optimizer for noisy quantum objectives (Spall 1998)."""
    theta = x0.copy()
    best_ratio = 0
    best_theta = x0.copy()
    for k in range(1, max_iter + 1):
        a_k = a / (A + k) ** alpha
        c_k = c / k ** gamma
        delta = np.random.choice([-1, 1], size=len(theta))
        r_plus = objective(theta + c_k * delta)
        r_minus = objective(theta - c_k * delta)
        g_hat = (r_plus - r_minus) / (2 * c_k * delta)
        theta = theta + a_k * g_hat  # MAXIMIZE (not minimize)
        current = objective(theta)
        if current > best_ratio:
            best_ratio = current
            best_theta = theta.copy()
    return best_ratio, best_theta
```

Note: 2 circuit evaluations per SPSA iteration (vs 1 for COBYLA) — 50 SPSA iters ≈ 30 COBYLA iters in cost.

---

## Connection to Paper

If H1 confirmed: Finding 26 = "SPSA substantially outperforms COBYLA for QAOA under finite-shot noise"
This would be a practical recommendation for the paper: "practitioners should use SPSA or QNSPSA
for variational quantum eigensolvers and QAOA under noisy conditions."

If H1 refuted + H3 confirmed: Finding 26 = "Shot count is the bottleneck, algorithm secondary"
Recommendation: "Use ≥1024 shots minimum for reliable QAOA optimization on 20-qubit instances."

If both refuted: Finding 26 = "40% escape rate is a genuine physical property of this MaxCut landscape,
stable across optimizers and shot counts" — a deeper structural claim about QAOA landscape topology.

---

## Priority Justification

Finding 25 established a non-replication result. Scientific rigor requires:
1. Understanding WHY (mechanism: shot-noise trajectory chaos) ← Finding 25 done
2. Testing whether SPSA can fix it (H1) ← Exp51 Phase B
3. Testing whether more shots can fix it (H3) ← Exp51 Phase C

This directly feeds into paper section on "Practical Recommendations for QAOA Implementations."

---

*Exp51 pre-registration by Ember C3689 | 2026-06-09*
*Prerequisites: Phase C complete (est. 12:20 UTC June 9), paper status review*
