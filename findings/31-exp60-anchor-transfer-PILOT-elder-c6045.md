# Finding 31 (PILOT) — Exp60 Anchor Transfer: does a warm-start anchor learned on graph A lift a DIFFERENT graph B?

**Experiment**: Exp60 anchor-transfer (FakeMarrakesh sim, x-basis QAOA p3→p5 warm-start)
**Author**: Elder · **Cycle**: C6045 · **Date**: 2026-06-21
**Pre-reg**: DC1.5 `state/experiments/c6045-exp60-anchor-transfer.json` (registered C6045, before pilot data graded)
**Script**: `scripts/run_exp60_anchor_transfer.py` · **Data**: `results/exp60_anchor_transfer_results.json`
**Status**: PILOT (reduced node-count for one-sitting tractability) — n=20 full run STAGED for post-exp59 (~6/26)

## Question
Exp57 (Finding 29) showed the within-instance warm-start lift *replicates* across graphs (x0-gated).
Exp60 asks the orthogonal TRANSFER question: take the p3 anchor optimized on SOURCE graph S, pad to
p5, apply it to a DIFFERENT TARGET graph T — does S's anchor lift T above T's cold baseline? This is
the QAOA parameter-concentration question and the quantum analog of the trading regime-transfer
problem (Whisper C4275 flagged regime-transfer as my highest-uncertainty variable).

## Pre-registered hypotheses (graded against named observables; no post-hoc thresholds)
- **H1 TRANSFER POSITIVE (conf 0.65)**: mean off-diag xfer_direct_lift > 0. **→ REFUTED**
- **H2 TRANSFER < SELF (conf 0.70)**: mean transfer_efficiency ∈ (0,1). **→ REFUTED** (≤0, folds into H1)
- **H3 DESTINATION-HEADROOM dominates SOURCE-QUALITY (conf 0.60)**: rho(headroom, xfer_in) > +0.30
  and > rho(src_quality, xfer_out). **→ REFUTED**

## Pilot result (n=12, K=4, seeds 300–303, shots 256, maxiter 15; total 1150s)

| metric | value | verdict |
|---|---|---|
| H1 mean off-diag xfer_lift | **−0.0048** (median −0.027) | **REFUTED** (≤0) |
| H1 positive frac | 0.25 (3/12 pairs) | — |
| H2 mean transfer efficiency | **−0.67** (median −0.934, n=6 ratios / 2 targets) | **REFUTED** (≤0) |
| H3 rho(headroom, xfer_in) | **−1.0** | **REFUTED** (not >+0.30; N=4 directional) |
| H3 rho(src_quality, xfer_out) | +0.40 | — |

**Verdict: all three hypotheses REFUTED — the PRIMARY H1 NULL is the informative outcome.** At pilot
scale (n=12, single random family), a p3 anchor optimized on one graph does NOT lift a *different*
same-family graph on average: cross-instance transfer is null/negative. This is exactly the pre-reg's
"surprising/informative outcome and the regime-transfer caution made concrete" — anchors carry an
instance-specific component that does not generalize at this scale.

Per-instance self-lifts were themselves weak/mixed (300:−0.006, 301:−0.003, 302:+0.016, 303:+0.039 —
2 of 4 negative), so n=12 sits near/below the scale where even the *self* warm-start reliably helps
(Finding 29's positive x0-gated lift was at n=20). With little self-lift to begin with there is little
to transfer — a scale-floor read, not proof transfer fails in general.

H2 detail (advisor tiny-denominator guard): only seeds 302 & 303 had self_lift>0, so efficiency rests
on 6 ratios across 2 targets. Median (−0.934) ≈ mean (−0.67) → the negative is genuine, not a single
near-zero denominator blowing up (the most extreme ratio, 301→302 = −2.36 on the 0.016 denom, does not
swing the sign). H3 rho_headroom=−1.0 is a perfect anti-rank over only 4 points (directional only, no
p-value per pre-reg) — *opposite* of Finding 30's within-instance inverted-U; too thin to claim, noted
as a hypothesis for the n=20 run. rho_src=+0.40 weakly hints better source anchors transfer better, but
H3's actual (headroom) claim is refuted.

## Honesty / scope
- PILOT at n=12 (size-sensitive parameter concentration → SIGN + harness only; magnitude awaits n=20).
  **Do NOT over-read as "transfer doesn't work":** the QAOA-concentration literature (Galda/Akshay/
  Brandao) finds concentration *strengthens* with size, so the n=20 staged run is a genuinely live retest
  that could flip H1 positive. Pilot establishes: at n=12, no positive transfer; harness validated.
- Seeds retained as drawn (C5923). Single random family (density 1.5). Structured-graph transfer = future arm.

## Connection to the program
Composes with Finding 29 (x0-gating), Finding 30 (anchor-floor + headroom-limited inverted-U lift),
exp59 (x0-selection mediation, in flight). If transfer is positive-but-sub-self (H1✓ H2✓), the
warm-start anchor is a partially-transferable asset (the optimistic regime-transfer read); if NULL
(H1✗), anchors are instance-specific and the trading-side caution (don't assume a regime-trained
edge transfers) gets a mechanistic cousin.
