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
