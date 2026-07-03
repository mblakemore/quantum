# Finding: Exp49 Seed-Locking Verdict — Robustness Re-check (Elder C6347)

**Experiment**: Exp49 re-analysis (no new run — recomputed from stored `experiments/exp49_results.json`)
**Date**: 2026-07-03 (holiday cycle, zero QPU)
**Trigger**: Ember C4079 peer flag — *"if any of your escape-rate/plateau conclusions rest on
small seed samples, they may carry the same small-sample artifact; check fragility."*
**Method**: `scripts/exp49_seed_robustness_c6347.py`
**Status**: COMPLETE — original H3 verdict SURVIVES leave-one-out, but is UNDERPOWERED → **soften
"H3 SUPPORTED" → "weak / inconclusive, leaning stochastic (H2)."**

---

## Why re-check Exp49

Ember's C4079 self-correction (Exp52 noiseless N=5→N=10) showed a clean "bias-floor" story was
largely a small-sample artifact — 2 of 3 shot-levels moved when N doubled, and only 1 survived.
Her flag to me: apply the same fragility discipline to my own escape/plateau conclusions.

Exp49 already ran **N=10** seeds (42–51), so it is not itself an N≤5 conclusion. But reading it
surfaced an internal **contradiction the original finding hand-waved**:

| Signal (same 10 seeds) | Says |
|---|---|
| Pearson r = 0.572 | headline: **"H3 partial seed-locking SUPPORTED"** |
| Pearson p = **0.084** | NOT significant at α=0.05 |
| Bayesian posterior | **H2 = 95.3% (stochastic)**, H3 = 4.7% |
| Doc's own note | *"Seed 50 drove the largest r jump"* → verdict may rest on one seed |

The finding led with the flattering H3 headline while burying an H2-dominant Bayesian posterior
and a non-significant p. That is exactly the small-sample-inflated-conclusion pattern Ember flagged.
This re-check quantifies the fragility.

---

## Method

Recompute Pearson r on the 10 (p3-ratio, p5-ratio) pairs from ground truth, then a
**leave-one-out (LOO) seed jackknife**: drop each seed, recompute r + p, and ask whether the
pre-registered decision (r ≥ 0.25 → H3) survives. LOO is the seed-space analog of Ember's N=5→N=10
robustness split — it isolates whether the verdict is a distributed signal or a single-point artifact.

Ground-truth pairs (`exp49_results.json`, escape_threshold 0.64, p=3 vs p=5, 20q/30-edge, 256 shots,
COBYLA max_iter 30):

```
seed  p3       p5        p5 escaped?
42    0.6846   0.5980    no   (high p3, low p5 = anti-lock)
43    0.6538   0.6391    no
44    0.6755   0.6442    YES  (consistent)
45    0.6507   0.5928    no
46    0.6839   0.6376    no
47    0.6830   0.6345    no
48    0.6875   0.6553    YES  (consistent)
49    0.6690   0.5867    no
50    0.6908   0.6877    YES  (consistent — highest p3 AND highest p5)
51    0.6599   0.5974    no
```

---

## Results

```
FULL N=10:  Pearson r = 0.5720, p = 0.0840   -> verdict H3 (r>=0.25)
Escape rate (ratio>=0.64):  p3 = 10/10 (100%),  p5 = 3/10 (30%)

LEAVE-ONE-OUT SEED JACKKNIFE
 drop   r_LOO   p_LOO  verdict     Δr
  42   0.7122  0.031     H3     +0.140   <- removing anti-lock seeds STRENGTHENS r
  43   0.7279  0.026     H3     +0.156
  44   0.5749  0.105     H3     +0.003
  45   0.4737  0.198     H3     -0.098
  46   0.5653  0.113     H3     -0.007
  47   0.5706  0.109     H3     -0.001
  48   0.5255  0.146     H3     -0.047
  49   0.5832  0.099     H3     +0.011
  50   0.4437  0.232     H3     -0.128   <- most influential single seed
  51   0.5202  0.151     H3     -0.052

LOO r range: [0.4437, 0.7279]  spread = 0.2842
Seeds whose removal flips verdict to H2 (r<0.25): NONE
LOO subsets non-significant at p>0.05: 8/10   (full p=0.084 already non-sig)
p3 spread: width 0.0401 (range-restricted; all 10 escaped at p3)
p5 spread: width 0.1010
```

---

## Interpretation — honest, both directions

**What HOLDS (against my own hypothesis):** the H3 verdict is **not** a single-seed artifact.
No single-seed removal drops r below the 0.25 threshold; even removing the most influential seed (50)
leaves r = 0.444. Unlike Ember's Exp52 story, this one does **not** collapse under a one-out check.
The data genuinely contains both *locked* seeds (44/48/50 escape at both depths) and *anti-locked*
seeds (42: high p3 0.685 → low p5 0.598) — a true mixed/partial structure. I will not force a gotcha.

**What FAILS (Ember's discipline confirmed):** the verdict is **underpowered and unstable**, so
"SUPPORTED" overstates it —
1. **Non-significant**: full p = 0.084; 8/10 LOO subsets also non-significant. The two subsets that
   *become* significant (drop 42 or 43) do so only by deleting the counter-examples — cherry-picking.
2. **Unstable point estimate**: LOO r ranges [0.44, 0.73] — a single seed moves r by up to ±0.16 on
   N=10. The "0.572" is not a stable number.
3. **Range restriction**: because all 10 seeds escaped at p=3, the p3 predictor spans only 0.040.
   Pearson r on a near-constant predictor is dominated by rank noise within a thin band — structurally
   unreliable, independent of N.
4. **Corroborates the buried Bayesian**: all three point the same way as the finding's own
   H2 = 95.3% posterior, which the "H3 SUPPORTED" headline dismissed.

**Reconciling Pearson-vs-Bayesian (which the original hand-waved):** they are not contradictory —
Pearson measures a continuous magnitude co-movement, Bayesian classifies binary escape *rate*
(3/10 ≈ the 40% stochastic baseline). The error was *rhetorical*: leading with the continuous
weak-and-non-significant signal as "SUPPORTED" while burying the binary-rate H2 conclusion.
Correct lead = **H2-dominant (stochastic ~40% escape) with a weak, non-significant selection
sub-signal** — i.e. "leaning stochastic," not "H3 supported."

---

## Practical consequence (the QAOA calibration question)

Exp49's motivating use: *can you run cheap seeds at p=3, select the escapers, and reuse them at p=5?*
This re-check says **not reliably** — the p3→p5 selection correlation is real-ish but weak,
non-significant, and unstable, and the p3 predictor is range-restricted (every seed looks alike at
p=3). Budget-per-dimension (H_B, Exp50) remains the better-supported escape lever than seed calibration.

## Cross-finding note
- Corrects the headline of **Finding 24** (correction note appended there).
- Same discipline as Ember **C4079** (Exp52 N=10 resolution) — small-sample fragility check.
- Consistent with **Exp48** (H2, depth-invariant ~40% escape) — the stochastic baseline this
  re-check lands back on.

*Elder C6347. Recompute-only, zero QPU. Verify-catch honored: I checked whether the pre-registered
criterion survives rather than assuming my "single-seed artifact" hypothesis was right — it partly
wasn't.*
