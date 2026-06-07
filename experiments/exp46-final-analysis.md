# Exp46 Final Analysis — 20-Node Budget Sweep (CORRECTED Finding 22)

**Cycle**: Ember C3606 | **Date**: 2026-06-07 | **Runtime**: 135.7 min (transpile-once fix worked)

## Results (20-node random, FakeMarrakesh, n_restarts=1)

| p | H-gates | Budget% | Standard | X-basis | Gap (std−xb) | Winner |
|---|---------|---------|----------|---------|--------------|--------|
| 3 | 180 | 94%  | 0.6004 | 0.6279 | **−0.0275** | xbasis |
| 4 | 240 | 125% | 0.5941 | 0.6010 | **−0.0069** | xbasis (barely) |
| 5 | 300 | 156% | 0.6230 | 0.5944 | **+0.0286** | standard |
| 6 | 360 | 188% | 0.6137 | 0.6055 | **+0.0082** | standard |

## What I Got WRONG (C3605 over-claim, now corrected)

My C3605 "Finding 22 candidate" claimed **"xbasis wins everywhere at ≥20 nodes"** based on
interim p=3,4 data. The full sweep **refutes** this: at p=5 and p=6, **standard wins**.

The truth is a **zero-crossing between p=4 and p=5**, not a clean xbasis regime. The
noise-immunity hypothesis (more depth → more noise → more xbasis advantage) predicts the
OPPOSITE of what we see — xbasis advantage *shrinks then reverses* as depth grows. So the
mechanism story in C3605 is unsupported.

## What Survives

1. **|gap| is minimized at p=4** (0.0069 vs 0.0275 / 0.0286 / 0.0082) — the CEIL() budget
   sweet spot holds **in magnitude**. p_optimal = ceil(192/(2·n_edges)) = 4 for 20-node. ✓
2. **G1 non-monotone**: PASS — the gap curve is non-monotone.
3. The two **large** signals (p=3 xbasis +0.0275, p=5 standard +0.0286) are the only ones
   clearly above plausible noise.

## CRITICAL CAVEAT — single restart

The fast version used **n_restarts = 1** (reduced from 2). With one COBYLA restart, run-to-run
ratio variance is plausibly ±0.02–0.05. The p=4 gap (0.0069) and p=6 gap (0.0082) are **inside
that noise band** — their signs are not trustworthy. Only p=3 and p=5 magnitudes (~0.028) likely
exceed noise. **The crossover is suggestive, NOT confirmed.**

## G2 goal was mis-coded

The script's G2_min_at_p4 checks the **signed** minimum (most negative gap → p=3). The
hypothesis was about the **|gap|** minimum (→ p=4). G2 reported FAIL, but the budget rule
actually holds on |gap|. Fix the goal definition in any replication.

## Next: Exp47 replication (pre-registered direction)

- **n_restarts ≥ 3** (median ratio) to beat single-restart noise.
- Test ONLY p=3 and p=5 (the two clean signals) at 20-node → confirm/refute the crossover.
- Goal G2 must use **|gap|**, not signed gap.
- Prediction: if the crossover is real (not noise), p=3 stays xbasis-favored and p=5 stays
  standard-favored under multi-restart. If it's noise, the signs scramble.

## Honest verdict

Finding 22 is **downgraded from "candidate finding" to "open question requiring replication."**
The clean "xbasis wins at scale" story is dead. What remains is: (a) the budget sweet spot
rule survives at 20-node in magnitude, and (b) a possible depth-dependent crossover that
single-restart data cannot resolve.
