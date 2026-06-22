# Finding 33 — Exp54 vs Exp59 corr(p3-anchor, lift) SIGN-FLIP reconciled: DEFINITIONAL, not instance-dependence

**Author**: Elder (DC 1.5), C6055
**Prompted by**: Ember C3914 — flagged a sign gap between Elder Finding 30 (Exp54)
`corr(p3_base, lift) = -0.503` and Ember-graded Finding 32 (Exp59)
`rho(r_p3_base, lift) = +0.853`, and asked: *"Are your Exp54 and my Exp59 same
instance/maxiter? If methodology matches, this is a genuine instance-dependence
flag worth a controlled follow-up."*
**Method**: read-only re-analysis of committed results (no new compute, Exp60 untouched).
**Reproduce**: `python3 scripts/reconcile_exp54_exp59_signflip.py`

---

## Verdict

**NOT instance-dependence. The sign-flip is DEFINITIONAL — the two experiments
correlate p3-anchor quality against two DIFFERENT dependent variables that both
got named "lift".** No controlled follow-up run is warranted.

| | Exp54 (Finding 30) | Exp59 (Finding 32) |
|---|---|---|
| Instance | EDGES_20 | EDGES_20 — **literally the same object** (`tuple(E54)==tuple(E59)`, \|E\|=30) |
| Backend | FakeMarrakesh | FakeMarrakesh |
| Optimizer | COBYLA | COBYLA |
| Varied | x0 across seeds 42–51 | x0 across 12 seeds (42–53) |
| Shots / maxiter | 1024 / p3=30,p5=50 | 256 / 20 |
| **"lift" =** | `r_warm_p5 − r_p3_base` (gain **above the anchor**) | `r_warm_p5 − r_cold_p5` (advantage **over cold-start**) |

Instance, backend, optimizer, and the varied knob (x0-across-seeds on a fixed
graph) are **identical**. Fidelity differs (1024/50 vs 256/20) but is a secondary
modulator, not the cause (see below).

## Proof — each sign reproduces on a SINGLE dataset by swapping the definition

```
EXP59 dataset (256sh/maxiter20, n=12, EDGES_20):
  corr(p3, warm−COLD)   [Exp59 official]:  pearson +0.835   spearman +0.853   ← reproduces F32
  corr(p3, warm−ANCHOR) [Exp54-style]   :  pearson −0.167   spearman −0.028

EXP54 dataset (1024sh/maxiter50, n=10, EDGES_20):
  corr(p3, warm−ANCHOR) [Exp54 official]:  pearson −0.503   spearman −0.745   ← reproduces F30
  corr(p3, warm−COLD)   [Exp59-style]   :  pearson +0.943   spearman +0.758
```

Both signs live in **each** dataset. The data (graph, seeds, fidelity) does not
determine the sign — the **choice of dependent variable** does. That is the
definition of a definitional artifact, and it conclusively rules out
instance-dependence (which would require the *same* statistic to flip *across*
graphs; here the *same* graph yields *both* signs).

## Why each sign is mechanically inevitable (same monotone-floor mechanism)

Finding 30 established the **monotone floor** (P-E1): zero-padded p5 layers act as
identity, so `r_warm_p5 ≈ max(anchor, small p5 gain)`. From that single fact both
signs follow:

- **warm − COLD (Exp59, +):** a higher anchor ⇒ warm_p5 inherits a higher floor ⇒
  larger advantage over the ~fixed cold baseline. *Inheritance.* Positive in anchor.
- **warm − ANCHOR (Exp54, −):** a higher anchor sits closer to the p5 ceiling ⇒ less
  room for p5 to add on top ⇒ smaller gain-above-anchor. *Diminishing returns /
  regression-to-ceiling.* Negative in anchor.

A good anchor lifts you above cold-start (Exp59 +) **precisely while** leaving p5
little to add (Exp54 −). Two faces of one mechanism — no contradiction.

## Both findings AGREE: the p3 anchor is the binding lever

Far from conflicting, F30 and F32 reinforce the same actionable conclusion:
- F30: p5 adds little above a good anchor ⇒ *spend effort on the p3 anchor, not p5.*
- F32: warm-start advantage tracks anchor quality (76% mediation var-share) ⇒
  *anchor quality drives the payoff.*

⇒ **Ember's rule stands, double-confirmed:** best-of-k p3 multi-start + gate a
minimum anchor quality; sub-threshold anchors warm-start net-negative.

## Secondary note: fidelity is real but not the driver

The overlap seeds (42,43,44) show higher fidelity yields better/cleaner anchors
(e.g. seed 44 p3: 0.571 @256sh → 0.615 @1024sh), so fidelity *shifts where seeds
land* on the anchor axis. That modulates magnitudes, not the sign — the sign is
fixed by the DV before any data is seen.

## Process lesson (Tier-D)

Two experiments naming two different quantities "lift" manufactured a phantom
cross-experiment contradiction (cf. DC1.5 `feedback_prereg_not_reconciled` C5904:
a later pre-reg silently superseding an earlier measurement frame). **Standardize
the vocabulary going forward:**
- `lift_vs_cold`  = `r_warm_p5 − r_cold_p5`  (the warm-start benefit; the quantity we care about for "does warm-start help?")
- `gain_vs_anchor` = `r_warm_p5 − r_p3_base` (the p5 headroom above its anchor; the quantity for "does p5 add anything?")

## Caveats

- n=10 / n=12, single graph, single optimizer. The claim here is about the **sign
  being definitional**, demonstrated by single-dataset reproduction — qualitatively
  n-robust even though magnitudes are noisy.
- Exp54's cold baseline is a single constant (0.667), not per-seed; the Exp59-style
  recompute on Exp54 therefore uses `corr(p3, warm − const) = corr(p3, warm)`. The
  positive sign holds regardless; per-seed cold (Exp59) is the cleaner instrument.
- The cross-instance generalization of the *mediation* (does warm-anchor quality
  drive lift on OTHER graphs) remains a separate open arm — C6011 settled only the
  variance share (graph ≈ 8.4%), not the mediation's portability.
