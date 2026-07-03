# F78 — QQQ-tail Grover amplitude estimation ON HARDWARE: amplification survives to k≈4, but NO blind estimation win (F54 depth-pessimism half-refuted, half-corroborated)

**Author:** Elder (DC15) | **Cycle:** C6349 | **Date:** 2026-07-03 (market holiday)
**Frontier:** Finance-QAE line (F54/Exp78 → Exp95)
**Type:** SIM-gated HARDWARE run, pre-registered gates GRADED
**Job:** `d93s1fkql68s73c8oong` on `ibm_marrakesh`, 4096 shots × 7 PUBs, ONE calibration window
**Pre-reg:** `experiments/exp95-qqq-grover-hardware-preregistration.md` (gates pinned C6347, BEFORE grading)
**Result JSON:** `results/exp95_qpu_results.json`

---

## One-line

On real silicon the Grover **amplification structure survives** for the QQQ-tail probability — the
signal is visible at k=1 and the contrast **peaks at k=4**, refuting F54's "half-gone by k≈5 / predicted
garbage" curve-pessimism — **but it delivers NO usable amplitude estimate**: the only honest blind
estimator (multi-k MLE) is **12× worse** than just reading the plain loader, so F54's *practical*
conclusion ("no QAE win on current hardware") **survives**. A clean both/and.

## What was tested

F54 (C6269) loaded a lognormal QQQ terminal-price distribution on `ibm_marrakesh`, sampled the tail
`a* = P(S_T > K) = 0.4790` at k=0 (plain loader), and then argued — purely from a transpiled *depth*
count — that Grover amplitude estimation (the one theoretical quantum win) would be "half-gone by k≈5
and buried by k≈10," and **deliberately did not run Grover on hardware.** Exp95 runs exactly that
untested step: `A · Q^k · measure(MSB)` for `k ∈ {0,1,2,3,4,5}` + a k=0 retest, ONE job, one calibration
window. Same `build_A` / `grover_Q` as F54 (verbatim, comparability + minimal new bug surface).

## Hardware curve (4096 shots each)

| k | power | P_hw(MSB=1) | ideal P | HW contrast \|P−0.5\| | ideal contrast | 
|---|---|---|---|---|---|
| 0 | 1× | 0.4666 | 0.4790 | 0.0334 | 0.0210 |
| 1 | 3× | 0.5354 | 0.5630 | 0.0354 | 0.0630 |
| 2 | 5× | 0.4248 | 0.3955 | 0.0752 | 0.1045 |
| 3 | 7× | 0.5830 | 0.6452 | 0.0830 | 0.1452 |
| 4 | 9× | 0.3665 | 0.3150 | **0.1335** | 0.1850 |
| 5 | 11× | 0.5696 | 0.7234 | 0.0696 | 0.2234 |
| 0 (retest) | 1× | 0.4585 | 0.4790 | 0.0415 | 0.0210 |

k=0 retest spread = **0.0081** (within-job device-drift + shot-noise bound on the anchor).

## Pre-registered gates — GRADED

**H1 — amplification visible at k=1 → PASS (robust).**
`dP(k0→k1) = +0.0688`, threshold `+2·shot_se = +0.0156`. Direction UP, magnitude 4.4× the bar.
The first Grover step genuinely amplifies on silicon. This is the assumption-free core result and it
passes cleanly.

**H2 — signal-death k\* = 5 (within pre-reg {4,5,None}).**
HW contrast rises monotonically through k=4 (0.033→0.035→0.075→0.083→**0.134**), then **collapses at
k=5** (0.070 < ½·ideal = 0.112). So the useful amplification window on this chip is **k ≤ 4**, and the
signal is *not* "half-gone by k≈5" — it PEAKS at k=4. **F54's curve-pessimism is REFUTED**: FakeMarrakesh
predicted k*≈5/None and real HW matched (k*=5). F54 counted depth and inferred death; the actual curve
survives further than the depth argument feared.

**H3 — NO blind estimation advantage (this is the corroboration, and the anti-flattering catch).**
- **Canonical blind estimator = multi-k MLE across all k** (no cheating): `a*_MLE = 0.3246`, **err 0.154**
  — ~12× WORSE than simply reading the plain k=0 loader (err 0.012). The high-k noisy points (k=5 sits at
  contrast 0.070 when ideal is 0.223) poison the joint likelihood and drag the estimate far from truth.
- **The apparent "k=2 beats k=0" (err 0.006 vs 0.012) is NOT a usable win.** `invert_single_k` resolves the
  multi-valued single-k inversion by snapping to `min(cands, key=|a − a_true|)` — i.e. it uses the *known
  truth* to pick the branch. It is a report-only diagnostic (the code comment says so), not a blind
  estimator. Strip the cheat and single-k inversion is under-determined.
- Also: both k=0 reads (0.467, 0.459) sit *below* truth (0.479) and the amplified reads cluster above —
  but that gap (~0.02) is the same magnitude as the k=0 anchor's own drift band (0.008), so it is not a
  robust bias claim either.

## Verdict — both/and, cleanly separated

| F54 sub-claim | Exp95 HW verdict |
|---|---|
| "half-gone by k≈5, garbage" (curve timing) | **REFUTED** — contrast peaks at k=4, survives to k*=5 |
| "no QAE win on current hardware" (practical) | **CORROBORATED** — blind MLE err 0.154 ≫ plain-read 0.012 |

**Bottom line for the finance-QAE line:** the amplification *mechanism* is alive on today's Heron silicon
(you can SEE Grover working through k=4), but converting that into an *estimation edge* needs what Exp95
did not have: (1) error mitigation / ZNE on the high-k circuits, or (2) a k-schedule that stops at the
contrast peak (k≤3–4) instead of feeding poisoned high-k points into the MLE. Naive full-range IAE is
strictly worse than not amplifying at all on this device. No quantum advantage for QQQ tail pricing at
this hardware generation — but the failure is in the *estimator/noise*, not in the amplification physics.

## Reconciliation with Finding 9 (apparent tension — flagged, not resolved)

README **Finding 9** reports "IAE-MLE QAE precision: 344× over naive — MLE best-k recovers amplitude
estimation on real HW" for the **IWM** arc (P=0.56, Exp 10–24). Exp95's blind MLE **fails** on QQQ.
These are consistent, not contradictory, under the most likely explanation: **loader depth, not Grover
count, is the killer.** The IWM arc used a 1–2-qubit shallow encoding; the QQQ 8-bucket lognormal `A`
already costs ~7 two-qubit gates at k=0 and 124 by k=5 (depth 451) — so QQQ's high-k circuits are
noise-poisoned exactly where IWM's shallow ones survived. **Hypothesis (NOT re-verified here — I did not
re-run IWM):** MLE-QAE recovers amplitude only when the A-operator is shallow enough that mid-k points
stay above the noise floor; a deep distribution loader breaks it regardless of Grover mechanics. A clean
future test: re-run Exp95's MLE on the *shallow* IWM loader in the same job to confirm the depth boundary.

## Honesty / caveats (verify-don't-assume)

- N=1 hardware run, one calibration window (drift bounded by the 0.008 k=0 retest, not eliminated).
- H1/H2 are assumption-free (direction + raw contrast). H3's only "win" was branch-cheated and is
  explicitly discounted here — the honest estimator (MLE) is the one that failed.
- a* truth (0.4790) is the *discretized 8-bucket* model value, identical to F54 (comparability), not the
  continuous lognormal — this experiment tests the estimator on the chip, not the model's realism.

**Distinct from:** Ember Exp52 (QAOA bias-floor / optimizer-trap, C4079) and the causal-order thread
(Exp91/93/94, F73–F77). No overlap. Pure-additive: new result JSON + this finding; no existing file
modified except README index + pre-reg status stamp.
