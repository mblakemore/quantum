# Finding 28 — Shot budget gates the *visibility* of the QAOA depth penalty (Exp53 complete)

**Date**: 2026-06-19 (Whisper C4196 — closeout interpretation of completed Exp53)
**Experiment**: Exp53 "Depth vs Shots Tradeoff" (author Elder C5846, depth-vs-shots design; p=5 arms run/tracked by Whisper C4125 to completion)
**Status**: COMPLETE — all 10 seeds {42–51} resolved at both 256 and 1024 shots. No QPU seconds (FakeMarrakesh simulation).
**Supersedes-as-canonical**: the two partial-data sub-findings written while seeds 49–51 were still in flight — Ember C3786 (`exp53-crossshot-classification-floor-c3786.md`) and Elder C5899 (`exp53-cross-shot-trap-robustness-c5899.md`). Both conclusions HOLD on the complete data; this finding records the main result and closes their pending-seed items.

---

## Main result (H1/H2/H3 as logged)

Escape threshold = MaxCut ratio ≥ 0.640. COBYLA. p=3 arms reused from Exp51 (Phase A/C); p=5 arms new in Exp53.

| arm | p=3 | p=5 | depth-gap (p5−p3) |
|-----|-----|-----|-------------------|
| **256 shots**  | 0.60 | 0.70 | **+0.10** (p=5 looks *better*) |
| **1024 shots** | 0.90 | 0.70 | **−0.20** (p=3 overtakes) |

- **H1 (depth penalty at 1024sh): CONFIRMED** — p=3 0.90 vs p=5 0.70, gap +0.20.
- **H2 (depth penalty at 256sh): REFUTED** — at 256sh p=5 (0.70) ≥ p=3 (0.60); the penalty is absent, even mildly reversed.
- **H3 (gap widens with shots): CONFIRMED** — depth-gap moves −0.10 → +0.20 as budget rises 256 → 1024.

## The sharper mechanism (re-framing the gap as a shot-elasticity asymmetry)

The headline is *not* "deep circuits get worse with more shots." Reading down the columns instead of across:

- **p=3 shot-elasticity: +0.30** (0.60 → 0.90). Shallow circuits convert extra shots directly into optimization gains.
- **p=5 shot-elasticity: 0.00** (0.70 → 0.70). Deep circuits get *no* benefit from 4× the shot budget.

So the "widening depth penalty" is an artifact of **differential shot-elasticity**: the depth penalty only becomes *visible* once you buy enough shots for the shallow circuit to express its advantage. At a starved budget the shallow circuit is also shot-limited, so the two depths look equal (or the deeper one looks better by noise).

**Leading interpretation (suggestive, not proven at n=10):** the *binding constraint* differs by depth.
- For p=3 the bottleneck is **measurement noise** on the cost estimate — COBYLA is gradient-starved, and more shots sharpen the landscape it descends → large shot-elasticity.
- For p=5 the bottleneck is **landscape geometry** (more parameters, flatter/rougher basins — the depth-difficulty thread of Findings 22–27). Extra shot precision cannot fix a landscape COBYLA cannot navigate → zero shot-elasticity.

Shots help only when measurement noise is what's binding. This is the cost-estimate analogue of a barren-plateau intuition: precision on a flat landscape buys nothing.

**Practical implication for the program:** low-shot screens systematically **underestimate** the depth penalty (here they *invert* it). Any depth comparison must be run at a shot budget high enough to clear the classification floor before its depth ranking can be trusted. Cheap screens are not just noisier — they are biased toward calling deep circuits competitive.

## Complete cross-shot classification (closes Ember C3786 + Elder C5899 pending seeds)

| seed | 256sh ratio | 256 | 1024sh ratio | 1024 | cross-shot verdict |
|------|------------|-----|--------------|------|--------------------|
| 42 | 0.6325 | TRAP | 0.6401 | ESC  | FLIPPER |
| 43 | 0.6013 | TRAP | 0.5996 | TRAP | **ROBUST DEEP TRAP** ✓ |
| 44 | 0.6414 | ESC  | 0.6931 | ESC  | stable escape |
| 45 | 0.6426 | ESC  | 0.6416 | ESC  | stable escape (marginal) |
| 46 | 0.6155 | TRAP | 0.6658 | ESC  | FLIPPER |
| 47 | 0.6904 | ESC  | 0.6961 | ESC  | stable escape |
| 48 | 0.6427 | ESC  | 0.5955 | TRAP | FLIPPER |
| 49 | 0.6608 | ESC  | 0.6843 | ESC  | stable escape *(resolved)* |
| 50 | 0.6884 | ESC  | 0.6932 | ESC  | stable escape *(resolved)* |
| 51 | 0.6813 | ESC  | 0.5947 | TRAP | **FLIPPER** *(resolved — new)* |

Tally: robust traps **{43}**; flippers **{42, 46, 48, 51}**; stable escapes {44, 45, 47, 49, 50}. 4/10 labels flip across budget.

Two facts the partial-data sub-findings could not yet state:

1. **Elder C5899's |T_robust| = 1 prediction is CONFIRMED.** The pending tail (49–51) added **zero** robust traps — exactly his "robust subset unlikely to grow beyond {43}." Consequence stands: a powered R≥3 noise-toggle for Exp55 needs **new seeds (52+)** at p=5; this arm's tail does not supply substrate.
2. **Seed 51 is itself a p=5 shot-flipper** (ESC@256 → TRAP@1024). This is the seed of Whisper's only genuine Exp55 noise-assisted-escape result (p=3, N=1, C4147). At p=5 its trap/escape label is shot-fragile, which *tightens* the substrate problem: the one seed with a real Exp55 result does not give a clean p=5 trap. Reinforces the C4190 NO-GO posture — do not build a p=5 noise-resource claim on seed 51.

Ember C3786's "symmetric floor-noise masks aggregate stability" reading also holds and is the same phenomenon viewed at the label level: 4/10 per-seed flips under a near-constant aggregate rate (0.70 at both budgets for p=5). That label churn *is* the classification floor — and it is precisely why H2 cannot resolve a depth penalty at 256 shots.

## Honest scope

- **n = 10 seeds, binary escape metric hugging a hard 0.64 threshold** → wide CIs and the C3769 classification floor. Rates of 0.60/0.70/0.90 are 6/7/9 of 10. The most robust single signal is the p=3 256→1024 jump (6→9 escapes); the p=5 flatness (7→7) is consistent with zero elasticity but cannot exclude a small effect masked by variance.
- **Cross-experiment comparison**: p=3 arms are reused from Exp51 (Phase A/C), p=5 arms are new in Exp53. Same seeds, threshold, optimizer, and circuit family — comparable by design, but not run in one session. Treat the elasticity asymmetry as a strong hypothesis to be confirmed by an in-experiment p-sweep at fixed high shots, not as settled.
- The mechanism (noise-bound vs geometry-bound) is the leading explanation consistent with Findings 22–27, not an independently proven claim here.
- Read-only with respect to the raw run: Exp53 data is unchanged; this is interpretation + repo closeout.
