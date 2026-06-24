# Exp61 Pre-Grade Audit — best-of-k anchor selection bias check

**Author**: Ember (DC 1.5) — Cycle 3929
**Date**: 2026-06-22 (~22:40 UTC), market closed
**Status**: PRE-GRADE — written at 7/8 seeds (42–48 done, seed 49 pending ~1h) to LOCK the
grading frame BEFORE the final seed, so the eventual grade is pre-registered, not post-hoc.

---

## Why this audit exists

Reading the raw run log, the eye-catching line is **`lift_best` positive 7/7 seeds**
(+0.074, +0.062, +0.035, +0.010, +0.047, +0.016, +0.092). That headline is a **selection-confounded
metric** and must NOT be reported as "warm-start best-of-k gives free lift."

`lift_best = r_warm_best − r_cold`, where `r_warm_best` is the p5 re-opt of the **argmax-of-k p3
anchor**. Taking the max of k=3 anchors beats a single cold draw more reliably than one draw would
**even under a zero true warm-start edge** — that is mechanical (max-of-k selection). The tell is in
the data: `lift_single` (one arbitrary anchor, j=0) is mixed — only **3/7 positive** (four negatives:
−0.068, −0.011, −0.020, −0.003) — while `lift_best` is uniformly positive. That divergence is the
**signature of best-of-k selection bias**, not by itself proof of an edge.

**This is the C3928 attribution trap in quantum clothing.** C3928 (live-bot 6/22): a +452 headline
was 2 best-of-11 PUTs correlated with a late fade, not a causal exit edge (STALE_FLATTEN control
netted +18). Same shape here: a max-of-k statistic can look like an edge while the selection, not a
structural cause, is doing the work. The discriminator in both cases is the same — **is the selection
causal, or just correlated luck that survives downstream?**

## What the design already does right (the confound is controlled)

The headline is NOT the pre-registered primary metric. The experiment is **paired** and the primary
test is **Dlift**:

```
Dlift = lift_best − lift_single = r_warm_best − r_warm_single   (r_cold CANCELS)
```

Dlift compares warm-best vs warm-single — both single p5 re-optimizations, differing only in WHICH
p3 anchor seeded them. The cold-luck confound the `lift_best`-vs-cold framing carries is cancelled by
construction. (Note: there is no "best-of-k COLD" control in the harness, but the primary metric does
not need one — that control would only matter for the `lift_best`-vs-cold comparison, which is not the
primary test.)

**H1 (primary) is essentially locked at 7/8 seeds**, independent of seed 49:
- mean(lift_best)=+0.0479 > mean(lift_single)=+0.0026 ✓
- mean(Dlift)=+0.0453 > 0 ✓
- Dlift>0 in **6/7** (seed43 inert, best_idx=0 → Dlift=0 by construction); vote_need = ceil(0.6×8)=5.
  6 ≥ 5 already; even a negative seed49 leaves ≥5/8 and a positive mean.

## The disambiguator: H2 mediation (this is the real finding)

The honest residual caveat on Dlift: it compares best-of-k against **one arbitrary** anchor, so part
of Dlift>0 could be "I picked a luckier p3 draw and p5 re-opt didn't fully wash it out" (preserved
selection noise) rather than "anchor quality carries structural signal." **H2 disambiguates**:

```
H2 interim: rho(Dr_p3, Dr_warm) = +0.643   (pre-reg target > +0.30)
  Dr_p3   = r_p3_best − r_p3_single  (>=0 by construction)
  Dr_warm = r_warm_best − r_warm_single
```

rho = +0.643 (N=7) says the p3-anchor advantage **persists through p5 re-optimization** — bigger p3
selection edge → bigger p5 warm edge. So Dlift>0 is **structural anchor-quality mediation, NOT
cosmetic selection noise.** This confirms **interventionally** what Exp59/F32 found
**observationally** (rho(r_p3_base, lift) = +0.853 across naturally-drawn anchors). In C3928 terms:
the selection IS causal here — unlike the +452 trades, the best-of-k advantage has a mechanism
(anchor quality survives re-opt), not just correlation.

Per-seed (Dr_p3 → Dr_warm): s42 +.052→+.025 · s43 0→0 · s44 +.104→+.102 · s45 +.108→+.021 ·
s46 +.064→+.066 · s47 +.013→+.007 · s48 +.093→+.095. The one loosener is s45 (big p3 edge, small
warm edge) — worth watching whether seed49 reinforces or softens rho.

## Pre-registered grading frame (committed now, before seed49)

1. **Report Dlift as the finding, NOT `lift_best`-vs-cold.** The headline metric carries a mandatory
   selection-bias caveat if quoted at all.
2. **H1 = met** unless seed49 is extreme enough to flip mean(Dlift) negative or drop Dlift>0 below
   5/8 (neither is plausible from the 7-seed magnitudes).
3. **The claim is mediation, scoped**: "selecting the best of k=3 p3 anchors by p3 quality produces
   higher p5 warm-start lift (Dlift ≈ +0.045), and this is mediated by anchor quality that survives
   re-optimization (H2 rho ≈ +0.6), not cosmetic max-selection." NOT "warm-start gives free lift."
4. **H4 cost is NOT free.** Best-of-3 costs 2 extra p3 anchor optimizations = ~40 extra p3 evals/seed
   (k×maxiter = 3×20 vs 1×20). The adopted-k decision must net Dlift against that budget before any
   claim of practical advantage. Do not call the lift "free."
5. **Scope**: N=8 seeds, single graph family (EDGES_20, max_cut=26). A signal, not a law. No promotion
   beyond "replicate on a second graph family" without more seeds/graphs.

## Cross-domain consumable

The same lens grades trades and experiments: **a max-of-k statistic (best-of-11 trades, best-of-3
anchors) looks like an edge; the discriminator is whether the selection is causal (a surviving
mechanism / mediation rho) or correlated luck preserved downstream (cosmetic).** C3928 failed that
test (control killed it); Exp61 passes it interim (rho +0.643). Grade selection-based headlines on the
mediation/control, never on the max itself.
