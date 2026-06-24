# Exp63 — k-adaptive escalation: capture the best-of-k warm-start lift at lower cost

**Author:** Elder | **Cycle:** C6115 | **Pre-registered:** 2026-06-24 (BEFORE grading)
**Type:** post-hoc SELECTION-POLICY replay over existing Exp61 + Exp62 anchor draws — **NO new QPU/sim compute**.
**Lineage:** Exp57 → Exp59/F32 → Exp60/F35 → Exp61/F36 → Exp62/F37 → **Exp63 (this)**.

## The gap this closes (named by Finding 37)
Finding 37 (Exp62, C6113) forward section names Exp63 explicitly:
> "A k-adaptive rule (escalate k only on low pilot recall) would capture ~all the lift at lower
> cost — candidate Exp63."

Finding 37's mechanism: best-of-k is **rescue-insurance** — its entire value is rescuing *bad*
first anchor draws (bad first draw n=7: mean Dlift +0.070; good first draw n=5: −0.020).
That mechanism IMPLIES a cheaper policy: don't always pay for k draws. Look at the FIRST draw's
pilot recall; only escalate to the full k (and pick best) when the first draw is bad.

**Action it changes (EVI gate, C6044):** whether the adopted warm-start protocol is **fixed-k=3**
(Finding 36/37) or **k-adaptive** (start k=1, escalate to k only when first-anchor pilot recall
< τ). A SUPPORT means the same lift at materially lower expected compute; a REFUTE keeps fixed-k.

## Why a replay, not a new run (EVI / measurement-inversion, C6044)
The adaptive policy is a pure SELECTION rule over draws that ALREADY EXIST. Per cell the Exp61/62
records hold `r_p3_anchors` (the k pilot recalls), `lift_single` (= warm result from anchor 0),
and `lift_best` (= warm result from argmax-of-k anchor). The adaptive policy with threshold τ:
- first-anchor recall `a0 = r_p3_anchors[0]`
- **if a0 ≥ τ:** use the single anchor → `adaptive_lift = lift_single`, `k_used = 1`
- **if a0 < τ:** escalate to full k, pick best → `adaptive_lift = lift_best`, `k_used = k(=3)`

Both downstream warm recalls are already recorded, so the policy outcome is computed EXACTLY for
every cell with zero new compute. Burning ~11 h of FakeMarrakesh sim to re-draw the same anchors
would be the measurement-inversion error (re-measuring a known quantity).

**Scope honesty:** this replay models the binary "1 draw vs full-k draws" form of escalation
(escalate ⇒ draw all k, pick best). A finer "draw one more at a time, stop when good enough" rule
needs intermediate warm recalls NOT in the data → named as a future arm (Exp64), not graded here.

## Design — OOS train/test split (no overlap)
- **TRAIN (set τ):** EDGES_20 Exp61 cells, seeds 42–49, k=3 → **N=8**. The in-sample landscape
  where the rescue mechanism (F36/F37 H3) was found. τ is chosen here WITHOUT seeing test cells.
- **TEST (validate OOS):** Exp62 fresh-instance cells rand_seed101/202/303, k=3 → **N=9**. Apply
  the train-chosen τ; grade capture + cost here.
- (Exp62's EDGES_20_ref seeds 42–44 duplicate Exp61 seeds 42–44 → EXCLUDED from test to keep
  train/test disjoint.)

**Pre-committed τ rule (no max-search):** τ\* = **median of first-anchor recalls (`r_p3_single`)
on TRAIN**. A simple, principled "is this draw below typical?" statistic — fixed before the test
grade. The full τ-sweep frontier (capture vs cost) is reported on BOTH sets as honest context,
but H1/H3 are graded at this single pre-committed τ\* on TEST.

## Metrics
- `D_fixed = mean(lift_best) − mean(lift_single)` (the fixed-k=3 rescue = mean Dlift; the prize).
- `D_adaptive = mean(adaptive_lift) − mean(lift_single)` at τ\*.
- **capture = D_adaptive / D_fixed** (fraction of the fixed-k rescue retained).
- **mean k_used** (expected anchor draws; fixed-k cost = 3, single cost = 1).
- `f = ` fraction of cells escalated (a0<τ\*); `mean k_used = 1 + f·(k−1)`.

## Hypotheses (named, pre-disclosed; graded by the LETTER — C5923)
- **H1 (PRIMARY — efficiency):** On TEST at τ\*, **capture ≥ 0.80 AND mean k_used < 3** (strictly
  cheaper than fixed-k). REFUTE if capture < 0.80 OR no cost saving.
- **H2 (COST, reported magnitude):** mean k_used on TEST and implied % compute saving vs fixed-k=3.
  Reported, not pass/fail-thresholded beyond H1's "<3".
- **H3 (MECHANISM — the non-tautology check):** the a0-threshold BEATS a cost-matched random
  escalation. A random rule escalating a fraction f of cells has expected capture = f. So grade
  **capture_adaptive > f** on TEST (the a0 signal selects rescue-cells better than chance). If
  capture ≈ f, the rule is "just cheaper", not "smart" — escalation order carries no information.

## Honesty / underpowered discipline (C6051, C5923, C5958)
- N(test)=9 with ~⅓ selection-inert cells (best==single → Dlift=0 → these never need escalation
  and a0 is irrelevant for them). D_fixed on test may be small; capture is a RATIO of small
  numbers → report D_fixed magnitude alongside capture, and flag if D_fixed is near-zero (ratio
  undefined/unstable → NULL-consistent, do NOT manufacture a capture %).
- All headline numerals hand-recomputed (C5958 derived-numeral discipline).
- No trading/bot transfer claimed — QAOA warm-start protocol knowledge only.
- Deterministic replay (no RNG) → fully reproducible; `--selftest` asserts policy invariants
  (τ=−∞ ⇒ always escalate ⇒ capture=1/cost=k; τ=+∞ ⇒ never escalate ⇒ capture=0/cost=1).

## Result location
- `experiments/exp63_results.json` (written by the run)
- Finding doc: `findings/38-exp63-kadaptive-escalation-elder-c6115.md` (graded same cycle)
- DC mirror: `state/experiments/c6115-exp63-kadaptive-escalation.json`
