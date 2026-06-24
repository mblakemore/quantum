# Exp64-τ PRE-REGISTRATION — τ-calibration of k-adaptive escalation via leave-one-out CV (N=17)

**Author:** Elder | **Cycle:** C6128 | **Registered:** 2026-06-24 (BEFORE any LOO-CV computed)
**Type:** post-hoc selection-policy replay, **NO new compute** (reads Exp61+Exp62 results only)
**Closes:** Finding 38's named forward arm — *"τ-calibration deserves a larger-N pass before pinning a production value."*
**Distinct from:** the *granular* Exp64 (draw-one-more-at-a-time) which needs NEW intermediate-anchor recalls not in the data. This arm grades ONLY the τ-choice rule for the binary 1-vs-full-k form already in Exp63.

---

## Motivation (the load-bearing caveat from F38)

Exp63 adopted k-adaptive escalation with **τ\* = median(train r_p3_single) = 0.6037**, chosen on
Exp61 EDGES_20 train (N=8). It disclosed an N-fragility flag: **train capture 0.749 (BELOW the 0.80
bar) but test capture 1.057 (ABOVE)** on N=9 fresh instances. The pre-committed grade was on TEST so
H1 stood by the letter — but a single 8/9 split cannot say whether the *median-τ rule itself*
generalizes, or whether 0.80+ on test was a small-N coin-flip. F38 named this as the next pass.

## Question

Does the **pre-specified rule** "τ = median of the in-sample r_p3_single" produce ≥0.80 capture of
the best-of-k lift **out-of-sample at larger effective N**, when evaluated by leave-one-out CV over
the full clean pool — and is the resulting OOS capture robust to the *quantile choice* (q25 / median
/ q75) or fragile to it?

## Design (zero compute, no test-argmax — snooping-disciplined per [[reference_incumbent_dsr_haircut_replay]] C6121)

**Pool (N=17, clean, de-duped):** Exp61 EDGES_20 seeds 42–49 (8 cells) + Exp62 fresh instances
rand101/202/303 (9 cells). The 3 Exp62 `EDGES_20_ref` cells are dupes of Exp61 seeds 42–44 →
EXCLUDED (same de-dup F38 used for its N=9 test).

**Per cell, the adaptive policy (identical to Exp63):** `a0 = r_p3_single`; if `a0 ≥ τ` → use single
anchor (`k_used=1`, lift = `lift_single`); else → escalate to full-k best (`k_used=3`, lift =
`lift_best`). `D_fixed_i = lift_best − cold` is the fixed-k benchmark per cell as in Exp63 (D = lift
relative to cold p5). Capture = Σ adaptive_lift / Σ fixed_best_lift over the graded fold.

**LOO-CV (the honest larger-N estimator):** for each held-out cell *i*, set
`τ_i = median(r_p3_single over the other 16 cells)` (rule fit blind to *i*), classify cell *i* with
τ_i, accumulate. Pooled OOS capture = Σ_i adaptive_lift_i / Σ_i lift_best_i. This is a genuine
17-fold OOS read of the SAME median rule Exp63 adopted — no threshold is searched against outcomes.

**Quantile-sensitivity (3 PRE-SPECIFIED rules, each run through the identical LOO loop):**
τ-rule ∈ {q25, median(=q50), q75} of the in-sample r_p3_single. Reporting all three is NOT a search
for the best — all three are pre-named; I report the spread to measure τ-choice fragility.

**Descriptive frontier (haircut-flagged):** I will additionally plot capture-vs-cost as τ sweeps the
full pool range. This is DESCRIPTIVE ONLY. Per C6121, picking the pool-argmax τ is a snooping axis and
is explicitly NOT the finding — it owes a DSR/multiple-testing haircut and will be labeled as such.

**Baselines / nulls (per [[reference_prereg_magnitude_bar_underpowered]] C6051 — no bare magnitude bar):**
- Cost-matched random null for the non-tautology check: a rule escalating a RANDOM f-fraction
  captures exactly f in expectation (Exp63 proved E[capture|random f-subset]=f). P3 requires LOO
  capture > realized escalation fraction f.
- Bootstrap 95% CI on pooled LOO capture (resample the 17 cells with replacement, 2000 draws) — the
  capture is a ratio of small numbers (D≈0.03–0.05), so I grade by the LETTER on the bar AND report
  the CI so the power is visible, not hidden.

## Forward predictions (committed BEFORE computing — Brier-scored)

| ID | Prediction | refuted_if | conf |
|----|-----------|-----------|------|
| **P1** | Pooled LOO-CV capture of the median-τ rule **≥ 0.80** | pooled LOO capture < 0.80 | 0.60 |
| **P2** | The rule still saves compute: pooled mean `k_used` **< 3** (escalation fraction < 100%) AND > 1 | mean k_used ≥ 3 OR == 1 | 0.90 |
| **P3** | Non-tautology: pooled LOO capture **> realized escalation fraction f** (beats cost-matched random) | LOO capture ≤ f | 0.70 |
| **P4** | τ-choice is **robust** at this pool: range of pooled LOO capture across {q25, median, q75} **≤ 0.20** | range > 0.20 | 0.45 |

Rationale for the confidences: P1 0.60 — train was below the bar, test above; pooling should land
near/above 0.80 but genuinely uncertain (this IS the fragility question). P2 0.90 — median τ sits
inside the r_p3_single distribution so some cells will be ≥τ (k=1) and some <τ → escalation strictly
between 0 and 1 unless the distribution is degenerate. P3 0.70 — Exp63 cleared this on both train and
test, expect it to hold pooled, but the load-bearing result so non-trivial. P4 0.45 — I lean toward
τ-choice MATTERING (the disclosed fragility suggests sensitivity), so I am NOT confident in
robustness; registering 0.45 makes "robust" the slight underdog I'd be mildly surprised to see win.

## Grading rule

Grade each P1–P4 by the LETTER against the computed pooled-LOO numbers (no convenient proxy, per
[[feedback_grade_named_observable]]). Brier-score the 4 points. Write Finding 40. The descriptive
frontier informs the forward implication but does NOT enter the grade. Commit results JSON +
finding. Read-only on all upstream result files.

## Reversibility

Pure analysis artifact — new files only (preregistration, results JSON, finding). No modification of
Exp61/62/63 data or any code. No CPU/QPU. Fully reversible by deletion.
