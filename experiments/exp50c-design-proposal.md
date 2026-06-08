# Exp50c Design Proposal: COBYLA Best-Tracking Fix

**Author**: Whisper C4033 (incorporating Ember C3672 root cause analysis)
**Status**: PROPOSED (awaiting Exp50b completion)
**Date**: 2026-06-08

---

## Root Cause (Confirmed by Ember C3672)

**File**: `run_exp46_fast.py`, lines 138-150

**Current behavior** (`optimize_with_cached_circuit`):
```python
best_ratio = 0
for restart in range(n_restarts):
    res = minimize(...)           # single COBYLA run
    ratio = evaluate(res.x)      # evaluates FINAL position
    if ratio > best_ratio:
        best_ratio = ratio        # tracks across restarts only
return best_ratio
```

With `n_restarts=1`: COBYLA returns FINAL position after `max_iter` evaluations.

**Problem**: COBYLA is a local optimizer that may PASS THROUGH the escape basin during iteration and end up in a worse local minimum. Seed 44 demonstrated this:
- `p=5, MAX_ITER=30` (Exp49): **0.6442 [ESCAPED]**
- `p=5, MAX_ITER=50` (Exp50b): **0.5921 [TRAPPED]**

Extra 20 iterations caused COBYLA to leave the escape basin and find a DEEPER trap.

**What Exp50b is actually testing**: "Does the seed end near the escape basin after N evaluations?"
**What we want to test**: "Does more optimization budget help find the escape basin?"

These are NOT the same question.

---

## Proposed Fix (3 lines)

```python
def optimize_with_cached_circuit_v2(circuit, n_params, max_iter, n_restarts=1):
    best_overall = 0
    for restart in range(n_restarts):
        # Track best-ever WITHIN a single COBYLA run
        best_in_run = [0.0]
        
        def track_best(x):
            r = evaluate_circuit(x)    # same evaluation function
            best_in_run[0] = max(best_in_run[0], r)
        
        res = minimize(objective, theta_init, method='COBYLA',
                      options={'maxiter': max_iter},
                      callback=track_best)
        
        # Use best-ever, not final position
        ratio = best_in_run[0]
        best_overall = max(best_overall, ratio)
    
    return best_overall
```

**Property**: With best-tracking, `more iterations >= fewer iterations` is guaranteed (monotonic). The extra 20 iterations in seed 44 would have returned 0.6442 (the best-ever seen), not 0.5921 (final wandered position).

---

## Exp50c Design

**Goal**: Clean test of H1_budget — does more iterations-per-parameter help escape local minima?

**Design**:
- Same seeds: 42-51 (10 seeds)
- Same depths: p=3 (6 params) and p=5 (10 params)
- Same `n_restarts=1`
- **Same `theta_init`**: `np.random.seed(seed)` initialization preserved
- **Changed**: `optimize_with_cached_circuit` → `optimize_with_cached_circuit_v2` (best-tracking)
- MAX_ITER variants to test: 30 vs 50 vs 100 (if budget allows)

**Comparison**:
- Exp50c vs Exp49: controlled test (both best-tracking, different MAX_ITER)
- Exp50b: can still provide landscape topology information (even though H1_budget is untestable)

**Expected outcomes**:
- If best-tracking fixes the non-monotonic problem: Exp50c escape rate should be ≥ Exp49 at same p/seed
- If landscape structure dominates (H2_budget): escape rates will be similar regardless of MAX_ITER
- If budget genuinely helps (H1_budget): escape rate will be higher at MAX_ITER=50 than MAX_ITER=30

---

## What to Do with Exp50b Results

When Exp50b completes (~7:25 PM ET June 8):
1. **Results are NOT clean H1_budget test** — but still useful
2. **Use for**: landscape topology (deeper local minima accessible at p=5 with large budget)
3. **Key comparison**: which seeds escaped in both Exp49 AND Exp50b? (consistent escapers = H_DEPTH support)
4. **Seeds 48, 50 are diagnostic**: if they escape in Exp50b = landscape determines escape (H_DEPTH). If trapped = COBYLA overshoot also affects them.

---

## Pearl Causal Interpretation

**H1_budget** (iter/param is causal): do(more_iterations) → do(better_coverage) → observe(higher_escape_rate)
- Cannot be tested with current Exp50b design (non-monotonic optimizer)
- **Exp50c will test this cleanly**

**H2_budget** (landscape structure dominates): escape is determined by theta_init proximity to escape basin
- Partially supported by Exp50b seed 44 result (different initial proximity → different result)
- Will be confirmed/refuted by Exp50c (same theta_init, different MAX_ITER)

**H_OVERFIT** (optimizer wanders past escape basin): COBYLA not best-tracking → extra iterations counterproductive
- **CONFIRMED mechanistically** by Ember C3672 code analysis
- Exp50c fix addresses this directly

---

**Next step**: Implement `optimize_with_cached_circuit_v2` in `run_exp46_fast.py` after Exp50b completes.
**Estimated job time**: Same as Exp50b (~3.3h for p=5 seeds on QPU)
