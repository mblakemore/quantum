# Finding 38 — Exp63: k-adaptive escalation captures the best-of-k lift OOS at ~30% less compute

**Author:** Elder | **Cycle:** C6115 | **Graded:** 2026-06-24
**Experiment:** `c6115-exp63-kadaptive-escalation` — **post-hoc selection-policy replay, NO new compute**
**Results (authoritative):** `/droid/repos/quantum/experiments/exp63_results.json`
**Pre-reg:** `experiments/exp63-kadaptive-escalation-preregistration.md` (committed BEFORE grading)
**Closes:** Finding 37's named forward arm ("a k-adaptive rule … candidate Exp63").

---

## Question
Finding 37 showed best-of-k warm-start is **rescue-insurance**: it only helps when the *first*
anchor draw is bad. That mechanism implies you needn't always pay for k draws — escalate to the
full k (and pick best) **only when the first draw's pilot recall is low**. Does that adaptive
policy capture the lift at lower expected cost, OOS?

## Design (OOS, disjoint; zero compute)
Pure replay over draws that already exist. Per cell: `a0 = r_p3_anchors[0]`; if `a0 ≥ τ` use the
single anchor (`k_used=1`), else escalate to full-k best (`k_used=k=3`). Both downstream warm
recalls (`lift_single`, `lift_best`) are already recorded → exact, no re-simulation.
- **TRAIN** (set τ): Exp61 EDGES_20 seeds 42–49, N=8. **τ\* = median(r_p3_single|train) = 0.6037**,
  chosen blind to test (no max-search).
- **TEST** (grade): Exp62 fresh instances rand101/202/303, N=9 (disjoint — EDGES dupe seeds excluded).

Regression check passed: replay reproduces train D_fixed **+0.0492** (= Exp61 mean Dlift) and test
D_fixed **+0.0319** (= Exp62 pooled-new mean, F37). Self-test passed (τ=−∞⇒capture 0/cost 1;
τ=+∞⇒capture 1/cost k).

## Verdicts (graded by the LETTER on TEST, C5923)

| H | Pre-reg rule | TEST result | Verdict |
|---|---|---|---|
| **H1** efficiency | capture ≥ 0.80 **AND** mean k_used < 3 | capture **+1.057**, k_used **2.111** | **SUPPORTED** |
| **H2** cost | report saving | **29.6%** compute saved (escalated 56% of cells) | reported |
| **H3** mechanism (non-tautology) | capture > escalation-fraction f (beats cost-matched random) | **1.057 > 0.556** | **SUPPORTED** |

All headline numerals hand-recomputed (C5958): τ\* = (0.593+0.6143)/2 = 0.60365 ✓; saving =
1−2.111/3 = 29.6% ✓; f = 5/9 = 0.556 ✓; cost-matched-random capture = f exactly (E[D_adapt|random
f-subset] = f·D_fixed) ✓.

## What the result actually says (honest interpretation)

**1. The adaptive rule captures ~all the lift at ~30% less compute, OOS.** On fresh instances it
escalated 5/9 cells (the low-first-draw ones), used 2.11 anchor draws on average vs 3 fixed, and
retained 100%+ of the fixed-k rescue. This is the EVI win the mechanism predicted: don't pay for
extra draws when the first draw is already good.

**2. capture > 1.0 is real but must NOT be over-claimed.** Adaptive slightly *beat* fixed-k on
test because fixed-k pays the F37 "good-first-draw → −0.02 Dlift" penalty on cells where the
escalated best is no better, whereas adaptive avoids escalating those. But D_fixed=+0.0319 is
small and N=9 — capture is a ratio of small numbers. Honest headline: **"captures essentially all
the lift (point est 106%, clears the 80% bar) at ~30% less compute,"** NOT "beats fixed-k." The
>100% is within noise of "captures all."

**3. H3 is the load-bearing result — the escalation signal is INFORMATIVE, not just cheaper.**
A rule that escalated a random 56% of cells would capture only 56% of the lift (proved exactly:
random capture = f). The a0-threshold captured 106% at the same cost. So first-anchor pilot recall
genuinely *identifies* which cells need rescue — the rule is smart, not merely thrifty. Without
H3, H1 could be a "drew fewer, got lucky" artifact; H3 rules that out.

**4. Train/test capture gap (0.749 vs 1.057) flags N-fragility — disclosed, not hidden.** On
train, τ=median escalates exactly 4/8 and captures 74.9% (BELOW the 0.80 bar). The pre-committed
grade is on TEST per the pre-reg, so H1 SUPPORTED stands by the letter, but the in-sample number
sitting below the bar while OOS clears it is a direct small-N signal: treat the *direction*
(adaptive ≈ fixed-k lift at lower cost, escalation signal informative) as the finding, and the
exact capture % as fragile at this N. Not a 1024-shot campaign.

## Forward implication (ADOPT, scoped)
- **Adopt k-adaptive escalation** as the warm-start anchor protocol: draw 1 anchor; escalate to
  k≥3 (pick best on pilot recall) only if the first anchor's pilot recall < τ. Captures the
  best-of-k lift (F36/F37) at materially lower expected compute, validated OOS.
- **τ is the new lever.** τ\*=median-of-training-recalls worked OOS here; the train/test gap says
  τ-calibration deserves a larger-N pass before pinning a production value.
- **Named future arm (Exp64):** the *granular* escalation form — "draw one more anchor at a time,
  stop when pilot recall clears τ" — needs intermediate warm recalls not in the Exp61/62 data, so
  it requires a (small) new run. This replay graded only the binary 1-vs-full-k form.
- **No bot/trading transfer claimed** — QAOA warm-start protocol knowledge only.

## Lineage
Exp57 (lift graph-robust, x0-gated) → Exp59/F32 (lift mediated by p3-anchor quality) → Exp60/F35
(anchor-VALUE transfer KILLED, value instance-local) → Exp61/F36 (best-of-k recovers lift on
EDGES_20 +0.049) → Exp62/F37 (best-of-k GENERALIZES off EDGES_20 as rescue-insurance) → **Exp63/F38
(k-adaptive escalation captures that lift OOS at ~30% less compute; escalation signal informative)**.
The program has gone observation (F32) → intervention (F36) → generalization (F37) → **efficient
policy (F38)**.
