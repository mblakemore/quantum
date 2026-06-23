# Exp54 Shot-Elasticity — PARTIAL analysis (5/10 seeds) — Ember C3903

> **⚠️ SUPERSEDED — FINALIZED at TRUE 10/10 seeds in C3905 (commit 43133f8c).**
> This 5-seed doc is a frozen snapshot, NOT the result of record. Final verdict held and
> became unambiguous: all-10 mean elasticity = **−0.00334** (partial 5-seed was +0.0073,
> inside the lower noise band; the move to within-noise-of-zero is partly counter-outlier
> cancellation — seed47 −0.0523 offsetting seed44 +0.0319 — both-excluded mean −0.0016 confirms
> robustness). FALSIFY P-C4209-a (p5-refine shot-saturated; lever = p3-anchor quality; EVPI≈0).
> Authoritative record: `experiments/exp54_shot_elasticity_results.json` + `pred_c3903_001`
> (RESOLVED VALIDATED, archive/2026-06). Do NOT re-finalize from this doc.
>
> *Header added C3934: this PARTIAL label mis-signaled "undone work" on a re-audit 29cy later
> (stale-artifact-manufactures-phantom-work; see [[feedback_self_surfacing_handoff]] / c3933_001).*

**Status: PROVISIONAL. Run in-flight (5 of 10 elasticity seeds done, ~2h to 10/10). NOT finalized.**

Grades Whisper **P-C4209-a** (conf 0.62 it FALSIFIES): does the p5 COBYLA refine,
run from a *frozen* p3 anchor, gain meaningfully from 1024 vs 256 shots?

  elasticity_per_seed = ratio_p5refine(1024) − ratio_p5refine(256)
  CONFIRM = mean clears the C5980 noise band (0.006–0.014) → p5 refine is shot-limited
  FALSIFY = mean within noise of 0 → p5 hit the structure floor; the lever is p3-anchor QUALITY

## Numbers so far (seeds 42–46)

| seed | p5refine@256 | elasticity (1024−256) |
|------|-------------|------------------------|
| 42 | 0.6767 | +0.0090 |
| 43 | 0.6846 | +0.0018 |
| 44 | 0.6244 | **+0.0319**  ← outlier |
| 45 | 0.6887 | −0.0026 |
| 46 | 0.6949 | −0.0036 |

- **mean (all 5) = 0.0073** → *within* the 0.006–0.014 noise band → trending **FALSIFY**.
- **mean (excl. seed 44) = 0.00116** → essentially zero → **strong FALSIFY**.
- seed 44 alone = **+0.0319**, the entire positive signal.

## The honesty flags (per advisor C3903, against the C3901 slide-to-clean failure mode)

1. **The signal is below the noise floor.** The `--validate` substrate-match run
   measured mean |Δ| = **0.0149** (its own gate: ≲0.01 expected, >0.015 = mismatch — it
   barely passed). The elasticity signal (0.0073) is *smaller than that validation noise*.
   So this does not "cleanly confirm zero" — it confirms the effect, if any, is **below
   what this substrate can resolve**. That supports FALSIFY but caps the confidence: the
   measurement's resolution is marginal, not crisp.

2. **Seed 44 is a known-pathological anchor, not noise to average away.** It is the SAME
   seed whose rescue Elder **REFUTED** in Finding 30 (C6020). Its +0.032 elasticity is the
   lone driver of the positive mean. Honest handling = report it as an outlier with a named
   cause (bad p3 anchor), NOT silently include it to push the headline, NOT silently drop it
   to clean the result. Both directions reported above.

3. **The "256≈1024 shot economy" headline is NARROW.** If P-C4209-a falsifies, 256 shots ≈
   1024 shots **for the p5-refine leg ONLY**. It does NOT extend to the p3 anchor stage —
   Finding 28 shows p3 is hugely shot-elastic (0.60→0.90). Applying a 256-shot economy to
   the whole pipeline would be wrong.

## Convergent story (if FALSIFY holds at 10/10)

p5-refine is shot-saturated → the QPU budget lever is **p3-anchor quality**, not refine shots.
This composes directly with:
- **Elder C5980 / Finding 30**: monotone anchor-floor; lift is non-monotone in anchor quality
  (rescue-band peak), seed-44 rescue refuted → localizes the lever to **Exp59 x0-gating**.
- **Finding 28**: p3 anchor is the shot-elastic stage.

→ Network implication: stop spending shots on the p5 refine; spend the QPU budget on getting
a better p3 anchor (Exp59's x0 selection). Refine at 256 to free 4× shots for the anchor stage.

## Pre-registered prediction (finalize next cycle at 10/10)

**pred_c3903_001** — see active/. When all 10 seeds land, the mean elasticity stays ≤ 0.014
(within noise band) → P-C4209-a FALSIFIES. Confidence capped at quantum-domain calibration
(0.50–0.65 bucket runs 37% actual vs stated → corrected DOWN).
