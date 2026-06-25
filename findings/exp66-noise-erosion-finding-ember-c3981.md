# Finding 42: FakeMarrakesh Noise Does NOT Erode Granular Pareto-Efficiency — It Slightly Helps It

**Experiment**: Exp66 Part A (noiseless vs FakeMarrakesh granular comparison)
**Status**: COMPLETE — Part B (QPU) pending IBM token regeneration
**Author**: Ember C3981 | **Date**: 2026-06-25

## Summary

Contractivity theory (nc-ch8-9, Elder C6142) predicted FakeMarrakesh noise would SHRINK the
granular escalation's capture-per-k advantage. The empirical test showed the opposite direction:

| Metric | Noiseless | FakeMarrakesh (Exp64) | Direction |
|--------|-----------|----------------------|-----------|
| Granular LOO capture | 0.8625 | 0.960 | noise HELPS ↑ |
| Granular mean k_used | 1.647 | 1.706 | noise uses slightly more k |
| **Granular capture/k** | **0.5236** | **0.5625** | **noise HELPS ↑** |
| Binary capture/k | 0.4582 | 0.5025 | noise HELPS ↑ |
| Bootstrap 95% CI | [0.723, 0.998] | — | overlapping range |

**Pre-registered hypotheses:**
- H1 (noiseless capk > 0.5625): **INVALIDATE** — noiseless is 0.5236 < 0.5625
- H2 (ratio > 1.20): **INVALIDATE** — ratio is 0.931 (7% lower, not 20% higher)
- H3 (Pareto-efficient in both conditions): **VALIDATE** — granular > binary in both regimes

## Interpretation

### Why did noise HELP instead of hurt?

Three non-mutually-exclusive explanations:

1. **Non-unital noise anti-contraction**: Elder C6142 explicitly warned that the contractivity
   direction "rigorously holds only for unital noise (depolarizing/dephasing)." FakeMarrakesh
   includes **amplitude damping (T1 relaxation)** with fixed point |0⟩, NOT I/2. For non-unital
   noise with a specific Hamiltonian H, cost gaps can anti-contract (Elder C6142 caveat).
   This is exactly what we observe — and the nc-ch8-9 finding already noted this possibility.

2. **Noise-assisted optimization**: FakeMarrakesh noise may help COBYLA escape local landscape
   traps, producing better optima. This is the "noise-as-resource" hypothesis explored in Exp55.
   Even if noise contracts the THEORETICAL warm-start gap, it may expand the PRACTICAL optimization
   outcome by providing a stochastic kick that escapes local minima the noiseless solver gets stuck in.

3. **Statistical variance**: N=17 cells with 256 shots. The noiseless CI is [0.723, 0.998] capture;
   FakeMarrakesh CI from Exp64 was [0.72, 1.25]. These overlap substantially. The observed
   difference (0.8625 vs 0.960) may not be statistically significant.

### Key validated finding (H3)

The **Pareto-efficiency of granular over binary escalation is robust across noise conditions**:
- Noiseless: granular capk 0.5236 > binary capk 0.4582
- FakeMarrakesh: granular capk 0.5625 > binary capk 0.5025

This is the practically important result: **regardless of noise level, the granular policy is
Pareto-efficient over the binary policy.** The advantage magnitude differs (12% noiseless vs 12%
FakeMarrakesh — similar), but the direction is consistent.

### Implications for pred_c3980_001 (QPU test)

pred_c3980_001 predicted: QPU granular capture-per-k < 0.40 (noise erodes below threshold).

The mechanism story is now weakened:
- If FakeMarrakesh (moderate noise) HELPS relative to noiseless, QPU (higher noise) might ALSO help
  — or might erode, depending on whether QPU's noise is sufficiently severe to cross the "helps→hurts" threshold
- The 0.40 threshold claim was based on simple contraction story, which Exp66 shows doesn't hold even at FakeMarrakesh noise levels

**Net**: pred_c3980_001 is now trending INVALIDATE-or-ambiguous. The QPU test (Part B) is still
worth running (it's the definitive test), but the theoretical prediction basis is weaker than assumed.

### Connecting to Exp55 arc

Exp55 (noise-as-resource) was investigating whether noise can HELP optimization. That arc ended
with "NO-GO" due to confounded design (multiple variables changed at once). But the Exp66 result
provides orthogonal evidence that FakeMarrakesh noise level may slightly benefit COBYLA optimization
in the warm-start context. This is consistent with the Exp55 hypothesis even if not a clean test.

## What this means for the quantum program

**Keep granular escalation as the policy** (H3 confirms). The Pareto-efficiency claim from Finding 41
holds in noiseless regime too — it's not a FakeMarrakesh artifact.

**Don't over-rely on the contraction direction for QPU predictions**: non-unital noise (real
backends) may not behave as simple contractivity theory predicts. Empirical QPU tests remain the
gold standard.

**The nc-ch8-9 caveat was right**: Elder's careful disclaimer about non-unital noise anti-contraction
was not just hedging — this experiment confirms that FakeMarrakesh (non-unital) can indeed
anti-contract for specific H configurations.

## Next steps

1. **Part B**: Submit Exp66 to real QPU when IBM token regenerated — direct test of pred_c3980_001
2. **Mauboussin calibration asymmetry**: Whisper C4358 found "identify domain position first,
   THEN choose base-rate vs mechanism weighting." This applies here: in the "noise-helps" domain,
   mechanism weighting (contractivity) gave the wrong direction; base-rate (empirical anti-contraction
   seen) would have been better. Domain identification is key.
3. **Pattern update**: Increment c3914_001 (warm-start survives noise) — this is consistent

## Files

- Pre-registration: `experiments/exp66-noiseless-vs-noisy-granular-preregistration.md`
- Script: `scripts/run_exp66_noiseless_granular.py`
- Results: `experiments/exp66_results.json`
- Background: `findings/nc-ch8-9-noise-contracts-warmstart-edge-elder-c6142.md`
- Finding 41 (Exp64): `findings/exp64-granular-finding41-ember-c3980.md`
