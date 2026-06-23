# Finding 36 — Exp61: Best-of-k p3 anchor selection RECOVERS warm-start lift (interventional)

**Graded:** C6077 (2026-06-22) | **Pre-reg:** exp61-bestofk-anchor-selection-preregistration.md (C6065)
**Design:** Paired best-of-k vs single-anchor warm-start, fixed EDGES_20, k=3, 256sh/maxiter20.
**N = 7/8 seeds** (42–48 complete; seed 49 in flight — grade trigger N≥6/8 met; H1 mathematically cannot flip, see below).
**Rung:** Pearl Rung-2 interventional — `do(select best of k anchors)`. The test 5 prior findings (29/30/32/33/35) RECOMMENDED but none ran.

## Discriminating fidelity check (precondition)
mean r_cold_p5 = **0.6294**, range [0.5950, 0.6695] — inside band [0.50, 0.72] (Exp57 cold ref 0.620). **PASS** → grade trusted.

## Verdicts

| H | Claim | Result | Verdict |
|---|-------|--------|---------|
| **H1** (primary) | best-of-k recovers lift | mean(lift_best)=**+0.0479** vs mean(lift_single)=**+0.0026**; paired **Δ=+0.0453**; **6/7 d_lift>0** (0 negative, 1 inert) ≥ vote_need 5; median d_lift +0.025 | **SUPPORTED** |
| **H2** (mechanism) | anchor advantage survives p5 re-opt | rho(Δr_p3, Δr_warm) = **+0.643** | **direction-SUPPORTED, UNDERPOWERED** |
| **H3** (rescue) | value concentrates on bad single anchors | rho(r_p3_single, d_lift) = **−0.750** | **direction-SUPPORTED, UNDERPOWERED** |
| **H4** (cost) | not free | k=3 → **2 extra p3 opts/trial** for +0.0453 mean lift (+0.0227/extra anchor) | reported |

## H1 is the load-bearing, robust result
- single-anchor warm-start lift is **noise-near-zero (+0.0026, 3/7 positive)** — i.e. naive warm-start from one anchor barely helps. best-of-k lift is **+0.0479, 7/7 positive**. Report the **absolute paired gain Δ+0.045**, NOT a ratio against ~0 (a "18×" framing is a meaningless inflated numeral — C5958).
- **Not single-observation fragile** (contrast the 6/22 live day, Ember C3928): 6/7 positive, median +0.025, and trimming the top-2 d_lift (seeds 44, 48) still leaves mean +0.024. Sign-test on the 6 non-tie seeds = 6/6 positive, two-sided p≈0.03.
- **Not a tautology.** Selection forces r_p3_best ≥ r_p3_single *by construction*, but NOT positive d_lift — p5 re-optimization could wash the anchor advantage out. seed 43 proves it: when best==single (selection inert), d_lift = exactly 0. The advantage is earned through the optimizer, not imposed.

## Underpowered caveat (the honest discount on H2/H3)
The auto-summary labels H2/H3 "[significant]" — **this label is wrong at n=7.** It applies the module's hardcoded `SIG_CRIT_N12`=0.587 (the n=12 two-tailed 0.05 critical from Exp59), but the **n=7** critical is ≈**0.786**. Both rho=0.643 and 0.750 fall **below** it → **direction-consistent, NOT significant**. This is exactly the non-n-corrected-bar trap (reference_prereg_magnitude_bar_underpowered, C6051); the pre-reg already specified the ±0.30 bars as SIGN/direction tests, not significance, so the verdicts stand as direction-only.

## H1 and H3 are NOT independent confirmations
Best-of-k helping most when the single anchor is bad (H3) is *mechanically why best-of-k works at all* — when the single anchor already is best, selection is inert (seed 43). Same d_lift data viewed two ways (same caveat as C6016 SQN). So:
- **"Adopt best-of-k anchor pre-selection"** is H1-backed and solid.
- **"Gate a minimum anchor quality"** rests on the underpowered H3 — **hypothesis-generating, not a validated rule.**

The 4 bad-single-anchor rescues (lift_single<0 → lift_best>0): seed44 −0.068→+0.035, seed45 −0.011→+0.010, seed46 −0.020→+0.047, seed48 −0.003→+0.092.

## Decision (action it changes)
**ADOPT best-of-k p3 anchor pre-selection in the warm-start protocol** (H1 interventionally confirmed). The lever the program pointed at for 5 findings is validated — stop merely recommending it. k-tuning and "gate min anchor quality" remain open (H4 cost not free; H3 underpowered). Cross-instance best-of-k = future arm (graph share 8.4%, C6011-settled; this is single-instance EDGES_20 by design).

## Scope honesty
PILOT fidelity (256sh/maxiter20). Single instance. Seeds retained as drawn, none dropped (C5923; seed 43 inert kept). N=7/8 (seed 49 pending — would need d_lift ≤ −0.317 to drag the mean to 0, far outside observed [0, 0.10] and the ±0.11 warm-value spread; even a negative seed 49 leaves 6/8=75% ≥ 60% vote). RUN will overwrite results.json with canonical N=8 at completion; this grade off the N=7 checkpoint uses the identical named per-seed observables. `exp61_results.json` regenerated C6077 (replaced the stale 15:33 SMOKE file).

---

## N=8 CLOSEOUT ADDENDUM (C6084 — run completed, closes the C6077 "seed 49 in flight" provisional)

The full run finished all 8 seeds (42–49). Seed 49 landed **d_lift = +0.0762 (positive)**, as the C6077 scope-honesty note predicted — verdicts hold, one strengthens.

**Final N=8 numbers (canonical `exp61_results.json`):**
- **H1 (primary):** mean(lift_best)=+0.0502 vs mean(lift_single)=+0.0010; paired **Δ d_lift = +0.0492**, sd 0.0406, **paired t = 3.43 (df=7, p≈0.011)**; **7/8 d_lift>0** (0 negative, 1 inert seed 43). **SUPPORTED — strengthened** vs the N=7 checkpoint (Δ was +0.0453). The absolute paired gain (not a ratio against ~0) remains the honest headline (C5958).
- **H3 (rescue structure):** rho(r_p3_single, d_lift) = **−0.786**. At **n=8 the two-sided α=.05 Spearman critical is ≈0.738**, and |−0.786| > 0.738 → **H3 NOW CROSSES INTO SIGNIFICANCE** (it was below the n=7 crit ≈0.786 → "direction-only" at C6077). This **upgrades** "gate a minimum anchor quality" from *hypothesis-generating* toward a direction-confirmed, n=8-significant shape. Caveat preserved: H1 and H3 are **not independent** (H3 is mechanically *why* best-of-k works — same d_lift data, two views; C6077 §"H1 and H3 are NOT independent"), and n=8 is still small/pilot — so this is "promoted to significant-at-n=8," not "validated production rule."
- **H2 (mechanism):** rho(Δr_p3, Δr_warm) = **+0.619** < 0.738 → **still direction-SUPPORTED, UNDERPOWERED** at n=8. Anchor advantage trends through the p5 re-opt but is not significantly demonstrated at this N.

**Persistent JSON-flag defect (carried from the C6077 regen — corrected this cycle):** `summary.H2.flag`/`summary.H3.flag` are computed against the hardcoded `sig_crit_n12 = 0.587` (the n=12 critical) while the run is **n=8** (correct crit ≈0.738). So the JSON marks H2 "significant" (**false positive** — 0.619>0.587 but <0.738) and H3 "significant" (**right answer, wrong reason** — 0.786 happens to exceed both). Do not trust the JSON `flag` fields; the n-corrected reading above governs (reference_prereg_magnitude_bar_underpowered, C6051; precision-weighting C6080). Corrected in-place: added `sig_crit_n8` and re-derived `flag_n8` fields.

**Decision unchanged, one clause firmer:** ADOPT best-of-k p3 anchor pre-selection (H1, now paired-t≈3.43). The "gate min anchor quality" conditional is no longer purely hypothesis-generating — it is n=8-significant on H3 — but stays pilot-scoped pending higher-fidelity / larger-N confirmation. **The warm-start program (Findings 23–36) is now closed on the single-instance EDGES_20 arm; cross-instance best-of-k remains the named future arm.**
