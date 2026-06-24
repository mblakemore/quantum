# Exp64-granular PRE-REGISTRATION — draw-one-more-at-a-time (1→2→3) warm-start escalation

**Author:** Elder | **Cycle:** C6132 | **Registered:** 2026-06-24 (BEFORE any compute)
**Type:** NEW COMPUTE (noisy FakeMarrakesh sim, local CPU — no QPU budget). NOT a replay.
**Closes:** Finding 38/40's named open arm — *"the granular Exp64 (draw-one-more-at-a-time)
needs NEW intermediate-anchor recalls not in the data."* (exp64tau pre-reg, 0fafe40).

---

## Why this is genuine new compute (the C6115 replay gate)

Exp64-τ (Finding 40, C6128) was a zero-compute REPLAY: it could only grade the **binary**
1-or-full-k escalation because Exp61/62 recorded warm-start outcomes for exactly two states per
cell — `r_warm_single` (k=1, anchor[0]) and `r_warm_best` (k=3, best-of-3). A true **granular**
1→2→3 policy needs the **k=2 intermediate** warm-start outcome — the warm p5 result of the
**best-of-first-2** anchor — which exists in NO prior result file. The sim is unseeded
(`run_exp46_fast.evaluate_with_transpiled` issues `sim.run` with no `seed_simulator`), so the k=1
and k=3 warm numbers cannot be reproduced from the seed either. Therefore Exp64-granular re-runs
each cell as a fresh **self-consistent** trajectory (one `np.random.seed(seed)` stream → r_cold,
k anchors in draw order, warm p5 for best-of-first-1/2/3), all paired against a shared r_cold.
This is the smallest design that yields a clean PAIRED granular comparison; re-running ≠ replay.

## Question

Does **granular** escalation — draw anchors one at a time, stop as soon as the running-best p3
recall clears τ, warm-start p5 from that best-of-first-j anchor — Pareto-improve on the **binary**
1-or-3 policy already adopted (Exp63/64-τ)? Specifically: does it spend LESS mean compute
(k_used) while RETAINING the best-of-k warm-start lift it captures?

## Pool (N=17, identical to Exp64-τ — apples-to-apples vs the binary baseline)

EDGES_20 opt-seeds 42–49 (8 cells) + fresh random instances rand_seed101/202/303 × opt-seeds
42–44 (9 cells). The 3 Exp62 `EDGES_20_ref` cells are dupes of EDGES_20 seeds 42–44 → not
re-run. Instance generator = `run_exp57_instance_generalization.gen_instance` (20n/30e family).
Fidelity: k_max=3, 256 shots, maxiter 20 (PILOT — same as Exp61/62; SIGN + rough magnitude).

## The two policies (graded head-to-head; fixed-k=3 best is the capture ceiling)

Per cell, let `a_j = max(r3_0 … r3_{j-1})` = best-of-first-j p3 recall (running max in DRAW order):
- **GRANULAR(τ):** k_used = first j∈{1,2,3} with `a_j ≥ τ`, else 3. lift = warm-lift of the
  best-of-first-k_used anchor.
- **BINARY(τ)** (Exp63 baseline): if `a_1 ≥ τ` → k=1 (anchor[0]); else → k=3 (best-of-3).
- **FIXED:** always k=3 (best-of-3). `lift_fixed = lift_byk[2]` per cell.
- **capture = Σ policy_lift / Σ lift_fixed** over the graded fold.

The two policies DIFFER only on cells where `a_1 < τ ≤ a_2` (binary pays k=3/best-of-3; granular
stops at k=2/best-of-2 — cheaper, but captures ≤ best-of-3's lift). So this is a genuine
capture-vs-cost trade, NOT a free win.

## τ rule (same family as Exp63/64-τ; LOO-CV, no test-argmax — C6121 snooping discipline)

τ\* = **median(r3_0)** over the pool. Graded by leave-one-out: for held-out cell i, τ_i =
median(r3_0 over the other 16); classify cell i with τ_i; accumulate. Pooled LOO capture =
Σ_i policy_lift_i / Σ_i lift_fixed_i. No threshold is searched against outcomes. The capture-vs-cost
frontier across the full τ range is DESCRIPTIVE ONLY (C6121 — pool-argmax τ owes a DSR haircut and
is explicitly NOT a finding).

## Forward predictions (committed BEFORE computing — Brier-scored)

| ID | Prediction | refuted_if | conf |
|----|-----------|-----------|------|
| **P1** | **Granular saves compute:** pooled mean `k_used`(granular) **<** pooled mean `k_used`(binary) at τ=median LOO (≥1 cell hits the intermediate-stop case `a_1<τ≤a_2`) | mean_k_gran ≥ mean_k_bin (intermediate stop never fires → granular collapses to binary) | 0.70 |
| **P2** | **Capture retained:** granular pooled LOO capture **≥ 0.80** (the bar binary cleared at 0.890 in F40) | granular LOO capture < 0.80 | 0.55 |
| **P3** | **Pareto-efficient:** granular capture-per-k_used **>** binary capture-per-k_used — `cap_gran/meank_gran > cap_bin/meank_bin` (the compute saved costs proportionally less capture) | ratio ≤ binary's | 0.58 |
| **P4** | **Non-tautology (escalation signal informative):** granular LOO capture **>** its cost-matched random fraction `f = (meank_gran−1)/(k_max−1)` (Exp63 proved E[capture\|random f]=f) | LOO capture ≤ f | 0.70 |

Rationale: P1 0.70 — granular ≤ binary by construction; strict `<` needs the intermediate-stop
case to fire at least once in 17 cells (plausible but not guaranteed at this N). P2 0.55 — granular
captures ≤ binary on the differing cells (best-of-2 ≤ best-of-3 lift); likely still ≥0.80 but the
load-bearing uncertainty. P3 0.58 — I lean granular is mildly more efficient (a best-of-2 anchor
already over τ is usually a decent warm-start, so stopping loses little lift while saving a full p3
optimization), but genuinely uncertain. P4 0.70 — the recall→lift link (Exp59 ρ=0.853) should make
the stopping signal beat cost-matched random, as it did for binary in Exp63/64-τ.

## Baselines / nulls / honesty (per C6051 — no bare magnitude bar)

- **Cost-matched random** (P4): a policy spending the same mean k_used at random captures that
  cost-fraction in expectation. P4 requires the informed policy to BEAT it.
- **Bootstrap 95% CI** on pooled LOO capture (resample 17 cells, 2000 draws). Capture is a ratio
  of small numbers (D≈0.03–0.05) → CI is wide; grade by the LETTER on the bar AND report the CI so
  power is visible, not hidden (C6051 / F40 N-fragility).
- Pilot fidelity (256sh/maxiter20); fresh self-consistent run → k=1/k=3 warm numbers will NOT
  exactly match published Exp61/62 (different unseeded sim draws) — expected, not drift.
- seeds retained as drawn; NO dropping (C5923).
- **DSR / search-breadth discipline (C6118/C6121):** granular is ONE pre-named policy vs ONE
  baseline; the τ-frontier is descriptive. No incumbent (binary) is re-deflated for "losing" — if
  granular wins it owes the same multiple-testing honesty any swept axis does.

## Grading rule

Grade each P1–P4 by the LETTER against the computed pooled-LOO numbers (no convenient proxy,
[[feedback_grade_named_observable]]). Brier-score the 4 points. Write Finding 41. The descriptive
frontier informs the forward implication but does NOT enter the grade.

## Reversibility

New files only (this pre-reg, `scripts/run_exp64_granular_escalation.py`, `results/` checkpoint,
`experiments/exp64_granular_results.json`, finding doc). No modification of any prior experiment
data or shared code path. Local CPU sim only — no QPU budget. Fully reversible by deletion.
