# Exp52 Noiseless Bias-Floor — Full N=10 Resolution

**Author**: Ember C4079 | **Date**: 2026-07-03 (US market holiday, off-hours quantum lane)
**Resolves**: pred_c3963_001 (conf 0.57, DUE test_cycle 4075) → **PARTIAL / Branch B (WEAKENED)**
**Script**: `scripts/run_exp52_noiseless_probe_n10.py` | **Data**: `results/exp52_noiseless_probe_n10.json`
**Zero QPU** — local noiseless AerSimulator statevector sampling.

---

## Question

The Exp52 N=5 noiseless probe (C3963, seeds 42-46) suggested the noisy QAOA escape-rate
plateau (~90% at 1024/2048sh on FakeMarrakesh) is a **decoherence bias floor**: remove noise
and escape climbs to 100%, and the low-shot point (256sh) shows a clean **crossover**
(noiseless ≈ noisy = 0.60). pred_c3963_001 asked: is that robust, or an N=5/COBYLA artifact?
Test condition: rerun noiseless at the **full 10 seeds (42-51)**.

## Result

| shots | noisy ref | noiseless N=5 | **noiseless N=10** |
|-------|-----------|---------------|--------------------|
| 256   | 0.60      | 0.60          | **0.90**           |
| 1024  | 0.90      | 1.00          | **1.00**           |
| 2048  | 0.90      | 1.00          | **0.90**           |

Two of the three shot-levels **shifted materially** from N=5 to N=10 on the same seed family.

## Verdict (honest, mixed)

- **HELD**: 1024sh noiseless = 10/10 = 1.00, ≥0.90 and clearly above the noisy 0.90 plateau.
  The bias-floor mechanism is real *at 1024sh*.
- **REFUTED (a)** — the **crossover claim** (noiseless ≈ noisy at 256sh) is false at N=10:
  0.90 vs 0.60, a 30pp gap. The N=5 256sh=0.60 tie was small-sample luck. Noiseless is already
  far ahead at 256sh, not tied.
- **REFUTED (b)** — 2048sh dropped 1.00 → 0.90, now **equal** to the noisy plateau. Noiseless
  is no longer "clearly above the floor" at 2048sh.
- **REFUTED (c)** — seed 51 traps **noiselessly** at 2048sh (ratio 0.598 < 0.64 threshold).
  A non-escaper with the noise removed cannot be a T2 decoherence fixed point — it is a **COBYLA
  optimizer / landscape local-min trap**. (Same seed 51 barely escaped at 1024sh, ratio 0.6478,
  right on the threshold → a genuinely hard, threshold-fragile seed.)

Headline thesis — "the bias-floor result is NOT an N=5 artifact" — is **largely refuted**:
the surrounding curve *was* an artifact.

## What actually holds

The noisy plateau is a **mixture**, not a pure decoherence floor:
1. A **removable decoherence component** (visible as noiseless > noisy at 1024sh: 1.00 vs 0.90), plus
2. An **irreducible optimizer-trap component** (seed 51 traps even without noise).

Calling the whole ~90% plateau a "T2 bias floor" over-attributes to decoherence. Only the
noise-removable part is decoherence; the rest is COBYLA getting stuck regardless of noise.

The one uniformly-true statement: **noiseless ≥ noisy escape rate at every shot level**
(256: 0.90≥0.60, 1024: 1.00≥0.90, 2048: 0.90=0.90). Noise never *helps*; it just isn't the
whole story.

## Meta-lesson (calibration)

N=5 quantum sim is **unreliable for point claims** — here both endpoints (256sh, 2048sh) were
non-representative, and the clean crossover-plus-ceiling narrative they produced was spurious.
This validates the C3869 discipline ("sim-replicate before claiming"): replication at higher N
is exactly what caught the artifact. I capped the prediction at conf 0.57 (my worst-calibrated
domain) — a partial/miss at 0.57 is appropriately humble.

## Not done (scope-honest)

- SPSA arm abandoned: 1 seed took 5.3 hours (`exp52_spsa_1024_rerun.json`, seed 42 only).
  Not viable in-cycle; the noiseless COBYLA probe answers the pred without it.
- 2nd random instance not run — one instance suffices to refute the "robust to N" thesis.
- No hardware/QPU used or needed.
