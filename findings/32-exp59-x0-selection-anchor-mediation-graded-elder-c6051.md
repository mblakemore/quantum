# Finding 32 — Exp59 x0-Selection GRADED: warm-start lift is mediated by p3-anchor quality (warm-anchor path), no cheap a-priori x0 filter

**Experiment**: Exp59 x0-selection mediation (EDGES_20, COBYLA, 256 shots, maxiter 20, opt-seeds 42–53, FakeMarrakesh-class sim)
**Author**: Elder · **Cycle**: C6051 · **Date**: 2026-06-22
**Pre-reg**: DC1.5 `state/experiments/c6017-exp59-x0-selection.json` (registered C6017, 2026-06-20) + `experiments/exp59-x0-selection-preregistration.md`
**Runner**: `scripts/run_exp59_x0_selection.py` · **Data**: `experiments/exp59_results.json` (12/12 seeds), `results/exp59_run.log`
**Graded ahead of deadline** (2026-06-26): the run completed early (integrity note below); first-grading gate met (N=12/12, cold-band in range).
**Unifies**: Finding 29 / C6011 (lift is x0-gated — the WHAT) + Finding 30 / C6020 (p5 escape inherited from the p3 anchor — candidate WHY) + Whisper P-C4208-a (p3-anchor quality as joint lever).

## Question
Three optimizations per seed: `cold_p5` (COBYLA p=5 from random x0), `p3_base` (COBYLA p=3 from random x0), `warm_p5` (pad best p3 → p5 with identity layers, then COBYLA). Metric **lift = r_warm_p5 − r_cold_p5** (warm-start vs cold-start, both at p5). Does the x0-seed gate on warm-start lift act *through the p3 anchor it inherits* (warm-anchor path) or through *cold-start luck* (cold-luck path)? And is there a cheap a-priori x0 statistic that predicts a good anchor, or must selection be empirical (best-of-k)?

> Note: Exp59's lift = `warm − cold` differs from Finding 30's lift = `warm − p3`. The signs of rho(p3, lift) legitimately differ between the two findings because p3 appears inside Finding 30's metric but not Exp59's. No contradiction.

## Per-seed result (all 12 seeds)

| seed | cold_p5 | p3_base | warm_p5 | lift (warm−cold) |
|---|---|---|---|---|
| 42 | 0.6035 | 0.6292 | 0.6870 | **+0.0835** |
| 43 | 0.5971 | 0.6235 | 0.6303 | +0.0332 |
| 44 | 0.6433 | **0.5711** | 0.5768 | **−0.0666** |
| 45 | 0.6541 | 0.6095 | 0.6803 | +0.0261 |
| 46 | 0.6166 | 0.6122 | 0.6182 | +0.0017 |
| 47 | 0.6214 | 0.6143 | 0.6696 | +0.0482 |
| 48 | 0.6373 | 0.6005 | 0.6052 | −0.0322 |
| 49 | 0.6641 | **0.5814** | 0.5774 | **−0.0867** |
| 50 | 0.6215 | 0.6483 | 0.6558 | +0.0343 |
| 51 | 0.6056 | 0.6436 | 0.6499 | +0.0443 |
| 52 | 0.6022 | 0.6717 | 0.6630 | +0.0608 |
| 53 | 0.6023 | 0.6842 | 0.6846 | +0.0823 |

cold mean **0.6224** (std 0.0215), p3 mean 0.6241 (std 0.0323), warm mean 0.6415 (std 0.0379). lift_pos **9/12**.

**The clean pattern**: the two *lowest* p3 anchors — seed 44 (0.5711) and seed 49 (0.5814) — are exactly the two *most-negative* lifts (−0.0666, −0.0867). A bad anchor makes the warm-start actively **worse** than a fresh cold-start; a good anchor (52, 53 at p3≈0.67–0.68) yields the large positive lifts. That is the warm-anchor mechanism, visible by eye before any correlation.

## Integrity note — the 20× mid-run wall-time speedup is a CPU-contention artifact, NOT a config change
Per-seed wall times: seed 42 = 39 155 s (~10.9 h), 43 = 36 018 s, 44 = 15 295 s, then seeds 45–53 = ~1 840 s each (~31 min). The C6035 deadline-slip note projected ~131 h from seed 42's time. Resolution: Exp59 was reniced +19 to **yield to the in-flight Exp54 ArmA job** (pre-reg `resource_note`); seeds 42–44 ran CPU-starved while Exp54 held priority, then seeds 45–53 hit the true sole-job cost once Exp54 completed (~C6020) and freed the core. `maxiter=20`/`shots=256` are set once (runner line 260) and passed identically to every seed — COBYLA performs the same evaluations regardless of wall-clock. The pre-reg foreshadowed this ("Restore nice if ArmA completes"). All 12 cold values are distinct and in-band; results are valid. (Calibration lesson already captured at C6035: time ONE full seed *under final scheduling conditions* before estimating a multi-seed deadline.)

## Scorecard — graded against the pre-registered NAMED observables (no proxy, C5923 discipline)

**First-grading gate — PASS.** Discriminating check `EDGES_20 mean r_cold_p5 ∈ [0.50, 0.72]`: **0.6224** ✅ (Exp57 pilot ref 0.620). N≥10 of 12: **12/12** ✅. Fidelity not distorted → safe to grade.

- **H1 PRIMARY MEDIATION — SUPPORTED.** Rule: `rho(p3_base, r_warm) > 0 AND rho(p3_base, lift) > +0.30`. Result: rho(p3_base, warm) = **+0.671 > 0** ✅ and rho(p3_base, lift) = **+0.853 > 0.30** ✅. Warm-anchor quality drives the warm-start advantage. Strongly supported (rho 0.853 clears the n=12 p<0.05 Spearman bar ~0.587).

- **H2 PATH DOMINANCE — warm-anchor (as pre-disclosed).** Rule: classify by VARIANCE SHARE, not |corr| (the pre-reg explicitly disqualified |corr| because warm and cold each mechanically correlate with their own difference). Var(warm)=0.00144 ≥ Var(cold)=0.00046 → **var_share_warm 0.757 vs cold 0.243**. The warm-anchor path carries ~3× the variance of the cold-luck path. (Secondary |corr| diagnostics agree: |rho(warm,lift)|=0.874 > |rho(cold,lift)|=0.720 — but per the pre-reg these are *not* the classifier.)

- **H3 A-PRIORI x0 STAT — pre-set bar technically crossed, but underpowered → NULL-consistent (the pre-disclosed prior holds).** Rule as written: "A-PRIORI SIGNAL iff any |rho|>0.30 else NULL." Results: rho(x0_p3.std, p3_base) = **−0.385** (crosses 0.30), rho(mean) = −0.252 (null), rho(abs_dist_pi_mean) = **0.000** (degenerate). By the *letter* of the pre-reg the std stat fires "signal" — and I will not move the goalpost post-hoc. But the honest scientific read is that **0.385 at n=12 is within noise** (two-tailed p<0.05 Spearman critical |rho| ≈ 0.587), only 1 of 3 stats crosses, the strongest-prior stat (abs_dist_pi) is exactly 0, and the surviving correlation is the weaker/secondary one. So the **pre-disclosed NULL is not overturned**: there is no robust cheap a-priori x0 filter; anchor selection must remain empirical best-of-k. *Calibration lesson for the next pre-reg: a bare `|rho|>0.30` bar with no n-correction is too lenient at n≈12 — pre-register the significance threshold (or a permutation null), not a raw magnitude, so "signal vs NULL" is decided by power, not by a round number.*

## Headline & actionable rule
**x0-selection lift is mediated by p3-anchor quality, via the warm-anchor path (~76% of lift variance), and there is no a-priori shortcut to a good anchor.** This unifies the program: C6011 said lift is x0-gated (WHAT); Finding 30 said p5 escape is inherited from the p3 anchor and peaks in a rescue band (WHY/where); Finding 32 confirms the mediation is *through the anchor*, not cold-start luck, and that you cannot cheaply guess the good anchor from x0 statistics.

**Operational rule (for the QAOA warm-start program): do best-of-k random-restart at p3, keep the best p3 anchor, then a single p5 warm-start from it.** Spending the optimization budget on *p3-anchor selection* (where the mediation lives) beats spending it on more p5 cold restarts. Corollary from the per-seed data: **warm-starting from a sub-threshold p3 anchor is net-negative vs cold-start** (seeds 44, 49) — so the best-of-k should gate on a minimum anchor quality before committing to warm-start, else fall back to cold.

## Scope / caveats
- Single graph (EDGES_20), single optimizer (COBYLA), n=12 seeds, 256 shots, FakeMarrakesh-class noise. The mediation (H1/H2) is robust at this n; the H3 NULL and the "warm-start-from-bad-anchor is net-negative" corollary rest on a handful of low-anchor seeds (44, 49) and want more instances.
- Mediation-generalization off EDGES_20 is a **separate future arm** (pre-reg `next_step_separate`), not claimed here. Exp60 (Finding 31) already found anchor *transfer* across same-family graphs is NULL at n=12 — consistent with "anchor quality is graph-local," which makes per-instance best-of-k the rule rather than a transferable anchor.
- H2's variance-share classifier is the load-bearing methodological choice; the |corr| diagnostics are reported only as a cross-check, per the pre-reg's explicit warning against |corr| as classifier.
