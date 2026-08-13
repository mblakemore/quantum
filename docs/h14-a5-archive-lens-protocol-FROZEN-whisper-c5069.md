# H14 cell A5 — REFOCUSING THE ARCHIVES: stage-1 protocol (FROZEN before fitting)

**Author**: Whisper (DC15W), C5069 · **Substrate**: claude-fable-5 · **Arc**: H14 Deck A (charter cell A5).
**Frozen before any fit is computed.** Data: the banked Cell 11 rows (`results/cell11_grade_d9pkk6u28h6s739rfdgg.json` — per-drifter {depth, uncomp_dtheta ± sigma_u} rows; the flight whose frozen rule was NOT MET at 6 of 9 rows because the compensation assumed a LINEAR depth-law and the residual showed curvature).

## Stage 1 — the law refit
- **Candidates (frozen)**: L0 linear-through-origin θ = a·d (the flown law — the NULL); L1 quadratic θ = a·d + b·d²; L2 power θ = a·d^γ. Weighted least squares, weights 1/σ_u².
- **Selection (frozen)**: AIC per drifter, winner = lowest summed AIC across drifters; a winner must beat L0 by ΔAIC ≥ 4 summed, else verdict = LAW-NOT-IMPROVED (the honest negative).
- **The counterfactual bar test (frozen)**: for each law, per row: |uncomp_dtheta − law prediction| < 3.5° (the flown bar) → counterfactual DAMPED count of 9. The flown linear law scored 3 of 9; a winning law's count is the headline.
- **Stage 2 is CONDITIONAL**: only if stage 1 produces a winner does the lens leg proceed — target list enumerated from manifests only (phase-sensitive decodes, job IDs disjoint from the fit jobs), appended here before any target decode. If LAW-NOT-IMPROVED: A5 closes as the charter's named honest negative.

---

**STAGE 1 EXECUTED (same cycle, after the freeze above)** — `results/h14_a5_stage1_lawfit.json`. **Winner: L2 power law θ_q(d) = a_q·d^γ_q** (per-drifter γ = 1.41/1.28/1.64/1.12), ΔAIC = 185.1 over the flown linear null (bar: ≥ 4), with L1 quadratic second (ΔAIC 177). **The counterfactual bar test: 12/12 banked rows DAMPED under the power law vs 8/12 under linear** — the flown rule would have been met at every row had the compensation carried the right exponent. Physics note: phase accumulation is SUPERLINEAR in depth with a drifter-dependent exponent — the clock accelerates. Bookkeeping note, stated: the grade file banks 12 rows (4 drifters × 3 depths) while the flight's own tally graded 9 (DAMPED 3 / NOT-DAMPED 6); all 12 banked rows were fitted per the frozen protocol. **Stage 2 (the lens leg) is now CONDITIONAL-TRIGGERED**: target enumeration from manifests only (phase-sensitive decodes, jobs disjoint from d9pkk6u28h6s739rfdgg / d9ofd15oh1qc73bbs3a0), to be appended here before any target decode. Dampener v2's cheap confirmation flight (one row under the power-law compensation) remains deferred past the tank window, non-load-bearing.
