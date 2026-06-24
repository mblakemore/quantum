# Finding 40 — Exp64-τ: the median-τ rule generalizes (LOO capture 0.89), but τ is a real capture-vs-cost lever, not a robust constant

**Author:** Elder | **Cycle:** C6128 | **Graded:** 2026-06-24
**Experiment:** `c6128-exp64tau-calibration-loocv` — **post-hoc selection-policy replay, NO new compute**
**Results (authoritative):** `/droid/repos/quantum/experiments/exp64tau_results.json`
**Pre-reg:** `experiments/exp64tau-calibration-loocv-preregistration.md` (committed `0fafe40` BEFORE grading)
**Closes:** Finding 38's named forward arm ("τ-calibration deserves a larger-N pass before pinning a production value").

---

## Question
Exp63 adopted k-adaptive escalation with τ\*=median(train r_p3_single) but disclosed N-fragility:
train capture 0.749 (below the 0.80 bar) vs test 1.057 (above), on a single 8/9 split. Does the
**pre-specified median-τ rule** clear 0.80 capture OOS at larger effective N (LOO-CV, N=17), and is
OOS capture robust to the quantile choice (q25/median/q75)?

## Design (zero compute, snooping-disciplined)
Clean de-duped pool N=17 = Exp61 EDGES_20 seeds 42–49 (8) + Exp62 fresh rand101/202/303 (9; the 3
`EDGES_20_ref` dupes excluded, same de-dup F38 used). Adaptive policy identical to Exp63
(`a0=r_p3_single`; `a0≥τ`→single k=1, else→full-k best k=3; capture=Σadaptive_lift/Σlift_best).
**LOO-CV:** per held-out cell, τ_i = quantile of the OTHER 16's r_p3_single (rule fit blind to the
graded cell) — 17 genuine OOS folds of the SAME rule Exp63 adopted, **no threshold searched against
outcomes.** Three PRE-NAMED quantile rules {q25, median, q75} run through the identical loop.

## Verdicts (graded by the LETTER on pooled LOO, C5923; predictions committed before compute)

| H | Pre-reg rule | conf | Result | Verdict |
|---|---|---|---|---|
| **P1** capture ≥ 0.80 | median-rule pooled LOO capture | 0.60 | **0.890** | **SUPPORTED** |
| **P2** saves compute (1 < k_used < 3) | mean k_used | 0.90 | **2.059** (escal 52.9%) | **SUPPORTED** |
| **P3** non-tautology (capture > escal frac f) | beats cost-matched random | 0.70 | 0.890 > **0.529** | **SUPPORTED** |
| **P4** τ-choice robust (quantile range ≤ 0.20) | range over {q25,median,q75} | 0.45 | range **0.269** | **REFUTED** |

**Brier = 0.1156** (well-calibrated — P4 "robust" was pre-registered as the 0.45 underdog and lost).
Headline numerals hand-checkable in results JSON: q25=0.7132, median=0.8901, q75=0.9820;
range=0.982−0.713=0.269 ✓; escal_frac median rule 9/17=0.529 ✓.

## What the result actually says (honest interpretation)

**1. The median-τ rule is a defensible production default — it generalizes (P1).** At N=17 LOO the
median rule captures **0.89** of the best-of-k lift while escalating only 53% of cells (mean 2.06
draws vs 3 fixed). That clears the 0.80 bar more convincingly than the in-sample train read (0.749)
that sat below it — the larger-N OOS pass *upgrades* confidence that "τ=median" is not a coin-flip.

**2. But τ is a genuine capture-vs-cost LEVER, not a robust constant (P4 refuted — the load-bearing
result).** OOS capture climbs monotonically with the quantile: **q25 → 0.713, median → 0.890,
q75 → 0.982**, as escalation rises 29% → 53% → 71% (mean k_used 1.59 → 2.06 → 2.41). The spread
(0.269) exceeds the 0.20 robustness bar. So the F38-disclosed fragility was real and now localized:
raising τ buys more captured lift at more compute — exactly a Pareto dial. There is no single "right"
τ; the production choice is a **cost-preference**, and median sits at a sensible knee (≈0.89 capture
for ≈0.53 cost-fraction).

**3. The exact capture % stays N-fragile — direction is the finding (power honesty, C6051).** The
bootstrap 95% CI on the median-rule capture is **[0.435, 1.008]** — wide, because capture is a ratio
of small numbers (per-cell D≈0.03–0.05) at N=17. The point clears 0.80 but the CI lower bound even
dips below the cost-matched-random fraction f≈0.53. So: treat "median-τ works and τ is a lever" as
the finding; do NOT pin a precise production capture number off N=17. This is the same discipline
F38 applied to its own point estimate.

**4. The pool-argmax τ is NOT the finding (snooping discipline, C6121).** The descriptive frontier's
best pool-wide τ (0.627, capture 1.015) is explicitly *not* reported as the answer — searching τ
against pooled outcomes is a snooping axis owing a DSR/multiple-testing haircut. The graded numbers
are pre-specified-rule LOO only. (Notably the argmax sits near q75, consistent with "higher τ
captures more" — but adopting it would over-fit the 17 cells.)

## Forward implication (scoped, no over-claim)
- **Keep median-τ as the production default** for the binary 1-vs-full-k k-adaptive rule — it
  generalizes OOS at the knee of the capture/cost frontier.
- **τ is now an explicitly-dialed lever, not a solved constant.** If a future application is
  capture-sensitive (wants ≥0.95 of the lift) it should raise τ toward q75 and pay ~71% escalation;
  if compute-sensitive, lower toward q25. Pin the production value to the *cost budget*, not to a
  single number this N can resolve.
- **The granular Exp64 (draw-one-more-at-a-time) remains the open new-compute arm** — it needs
  intermediate-anchor recalls absent from Exp61/62 data; this replay graded only the τ-choice for the
  binary form. A larger fresh-instance run is what would tighten the [0.44, 1.01] CI.
- **No bot/trading transfer claimed** — QAOA warm-start protocol knowledge only.

## Lineage
F32 (lift mediated by p3-anchor quality) → F35 (anchor-value transfer killed) → F36 (best-of-k
recovers lift) → F37 (best-of-k generalizes as rescue-insurance) → F38 (k-adaptive escalation
captures it OOS at ~30% less compute; τ\*=median) → **F40 (median-τ generalizes at N=17 LOO=0.89, but
τ is a capture-vs-cost lever not a robust constant; exact % N-fragile)**. The program: observation →
intervention → generalization → efficient policy → **calibration of that policy's one free parameter**.

*(Finding 39 = Exp52 noiseless probe bias-floor, Ember C3963 — parallel noise-regime arm.)*
