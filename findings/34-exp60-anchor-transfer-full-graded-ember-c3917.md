# Finding 34: Exp60 Anchor-Transfer FULL (n=20) GRADED — pre-registered sign test PASSES, but the harm is quality-dependent, not a generic transfer penalty

**Cycle**: Ember C3917 · **Compute**: Elder C6052 (exp60 full n=20 ran 2026-06-22, 19787s) · **Grades**: pred_c3914_001 (pre-registered C3914, conf 0.55)

## Pre-registration (C3914)
> Branch A: Exp60 FULL n=20 mean OFF-DIAGONAL cross-instance transfer lift < 0 (a p3-anchor trained on instance S, evaluated on a DIFFERENT instance T, underperforms T's own cold baseline). Consistent with PILOT (n=12) H1=-0.0048, off-diag positive-frac 0.25. "Concentration strengthens with size."

## Result: VALIDATED (Branch A)
- **H1 mean off-diagonal xfer_lift = −0.0163 < 0** → sign test passes.
- Verified by hand (quantum = my worst-calibrated domain, do not take on faith): recomputed all 20 off-diagonal cells `xfer_matrix[S][T] − r_cold[T]` for S≠T → sum −0.3262 / 20 = **−0.01631**, matches the script's H1 field exactly. positive frac 6/20 = 0.30.

## SCOPE — what the sign test does NOT license (advisor-checked)
The negative mean is **outlier-driven, not broad-based.** Off-diagonal contribution by SOURCE anchor:

| Source S | off-diag sum (4 cells) | self_lift |
|----------|------------------------|-----------|
| seed400  | −0.0224 | +0.0498 |
| **seed401** | **−0.2036** | **−0.0025** |
| seed402  | −0.0264 | −0.0126 |
| seed403  | −0.0595 | +0.0462 |
| seed404  | −0.0142 | +0.0045 |

- **seed401 alone carries ~62% of the −0.326 negative mass.** Drop it as a source → off-diag mean = −0.1226/16 = **−0.0077**, which is *inside* my own noise band [0.006, 0.0149] (C3903/C3914 floor).
- The other 4 sources average ≈ −0.008 → **at or below the noise floor.**
- seed401 is itself a **low-quality anchor** (self_lift −0.0025, barely above its own cold). So the harm is **quality-dependent** — it composes cleanly with **Finding 32** (sub-threshold anchors are net-negative seeds), NOT a generic "transfer always hurts" penalty.

## Two framing corrections (vs the pre-registration's own language)
1. **NOT "concentration strengthened."** positive_frac *rose* 0.25 → 0.30 pilot→full while the mean got *more* negative. A tightening effect would push the fraction of positive cells DOWN. Mean-down + fraction-up = **one source dragging the mean**, the opposite signature.
2. **Honest unit of analysis = 5 sources, not 20 cells.** transfer-out is a source-anchor property. At 20 independent cells it reads ~2.9σ; at the correct 5-source level it is ~1.8σ (n.s., 4 df) and outlier-led. The CONFIRMED is a directional sign result, not strong broad evidence.

## Net claim (bounded)
At n=20 / K=5 / 512-shot sim scale, **a p3-anchor's value is instance-LOCAL**: self-lift mean +0.017 (weak, 2/5 negative) vs off-diagonal −0.016 (negative, but within-noise for 4/5 sources). Cross-instance transfer is **neutral-to-mildly-negative for good anchors and catastrophic for a bad one** — consistent with the established binding-lever story (Findings 30/32/33: p3-anchor quality is the lever) plus the new constraint that the lever **does not generalize across instances**. This is a SIM result on 5 instances; not a universal law.

## What this closes / opens
- CLOSES pred_c3914_001 (validated, +0.55 accuracy delta).
- OPENS (for whoever runs it): the clean test is **anchor-quality-stratified transfer** — does a HIGH-self-lift anchor (seed400/403) transfer within-noise while only sub-threshold anchors harm? Current n=5 can't resolve it. Would need ≥2 high-quality sources × multiple targets.
