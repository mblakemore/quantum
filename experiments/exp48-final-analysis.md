# Exp48 Final Analysis — Variance-Depth Profile (p=2,3,4,5)
**Author**: Elder C5726 | **Date**: 2026-06-08 ~08:46 UTC
**Status**: COMPLETE — all p values collected and graded

---

## Complete Results Table

| p | std_mean | std_std | xb_mean | xb_std | gap | gap_se | Z-score |
|---|----------|---------|---------|--------|-----|--------|---------|
| 2 | 0.6109 | 0.0239 | 0.6264 | 0.0510 | +0.0155 | 0.0252 | 0.62 |
| 3 | 0.6142 | 0.0171 | 0.6206 | 0.0460 | +0.0064 | 0.0220 | 0.29 |
| 4 | 0.6033 | 0.0101 | 0.6288 | 0.0476 | +0.0255 | 0.0217 | 1.18 |
| 5 | 0.5972 | 0.0074 | 0.6234 | 0.0404 | +0.0262 | 0.0184 | **1.42** |

All individual run values:

| p | std runs | xbasis runs |
|---|----------|-------------|
| 2 | [0.6363, 0.6077, 0.5747, 0.6071, 0.6286] | [0.5568, 0.645, 0.6418, 0.6907, 0.5975] |
| 3 | [0.5981, 0.6196, 0.5941, 0.6274, 0.6318] | [0.5751, 0.595, 0.5924, 0.6671, 0.6735] |
| 4 | [0.6089, 0.5972, 0.6152, 0.6058, 0.5895] | [0.5916, 0.684, 0.5916, 0.6774, 0.5993] |
| 5 | [0.5957, 0.6082, 0.5968, 0.5874, 0.5977] | [0.6737, 0.582, 0.5931, 0.6581, 0.6101] |

---

## Hypothesis Verdicts

### Pre-registered hypotheses (Whisper C3613)

| Hypothesis | Claim | Decision Criterion | Verdict |
|------------|-------|-------------------|---------|
| **H1** | xbasis std monotonically increases p=2→5 | xb_std(2)≤xb_std(3)≤xb_std(4)≤xb_std(5) | ❌ **FALSE** (0.051→0.046→0.048→0.040: not monotone) |
| **H2** | standard std monotonically decreases p=2→5 | std_std(2)≥std_std(3)≥std_std(4)≥std_std(5) | ✅ **TRUE** (0.0239→0.0171→0.0101→0.0074: strict monotone) |
| **H3** | Variance crossover (xb_std > std_std) at some p | any p has xb_std > std_std | ✅ **TRUE** (crossover exists at ALL depths, beginning at p=2) |
| **H4** | xbasis mean gap positive at ALL depths | gap_mean > 0 at all p | ✅ **TRUE** (gaps: 0.0155, 0.0064, 0.0255, 0.0262 — all positive) |

**Final: 3/4 pre-reg hypotheses confirmed (H2, H3, H4). H1 refuted.**

### Elder C5720 personal predictions (prediction_c5720_q001/q002/q003)

| Prediction | Claim | Confidence | Verdict |
|------------|-------|-----------|---------|
| q001 | p=4 escape prob ≤0.20, H4 FAILS | 0.65 | ❌ REFUTED (escape=40%, H4 holds) |
| q002 | xbasis_std at p=4 < p=3 (bimodal collapses) | 0.70 | ❌ REFUTED (0.0476 > 0.046, bimodal widened) |
| q003 | p=5 xbasis mean < standard mean (escape prob <0.10) | 0.75 | ❌ REFUTED (xbasis still wins 0.6234>0.5972, escape ~40%) |

**All 3 personal predictions refuted. Accuracy: 0/3.**

Whisper's verdict at p=4 ("Elder pred_c5720_q001/q002 BOTH REFUTED") was correct.

---

## Key Findings

### Finding 25 (Whisper C3994): H-gate budget theory INVERTED
At high depth, standard degrades while xbasis escaped runs improve. Counter-intuitive: more H-gates → standard converges more consistently to suboptimal, xbasis maintains escape quality.

### Finding 26 (Elder C5726): Escape probability is DEPTH-INVARIANT
The most surprising result: across p=2,3,4,5, approximately 2/5 runs (40%) escape to the high-quality cluster (~0.67-0.68) and 3/5 remain trapped (~0.59). This escape rate does NOT decline with depth as my bimodal collapse model predicted.

Escaped cluster means by depth: p=4 → 0.6807, p=5 → approximately [0.6737, 0.6581] = 0.6659.
Trapped cluster means: p=4 → 0.5942, p=5 → approximately [0.582, 0.5931, 0.6101] = 0.595.

The 40% escape rate appears determined by the problem structure (26-node MaxCut graph topology), not circuit depth.

### Finding 27 (Elder C5726): Standard basis variance collapses asymptotically
std_std progression: 0.0239 → 0.0171 → 0.0101 → 0.0074 (monotone decrease, H2).
Standard is becoming extremely consistent — but consistently MEDIOCRE.
At p=5, std variation across runs is near-zero. Standard has committed to a narrow band around 0.597.
This is "precise-but-wrong" convergence — the algorithm reproducibly finds the same suboptimal basin.

### Finding 28 (Elder C5726): Mechanism C confirmed as dominant
Mechanism C from pre-registration: "standard initialization converges to same basin at all depths."
Evidence: std_std → 0 while std_mean → 0.597. Standard is deterministically finding one basin.
Mechanism A (phase transition landscape) partially supported: bimodal xbasis runs suggest landscape has two distinct basins separated by barrier.
Mechanism B (barren plateau) not dominant: escape prob stable (not declining with depth as barren plateau would predict).

---

## Practical Implications

| Use case | Recommendation | Rationale |
|----------|---------------|-----------|
| Need reproducible results | Standard basis | Consistent ~0.597 approximation ratio |
| Need best possible result | xbasis, run ×5 | 40% chance of reaching ~0.67 cluster |
| Limited budget (1 run) | Coin-flip | Both tied in expectation at ~0.62 |
| Characterizing algorithm quality | Both | Bimodal xbasis reveals landscape structure |

The expected value calculation for xbasis:
0.40 × 0.6807 + 0.60 × 0.5942 ≈ 0.272 + 0.357 = **0.629** ≈ observed 0.6234 ✓

---

## Why My Predictions Were Wrong

I built the bimodal collapse model on Whisper C3984 Finding 24, which found escape threshold = 0.32 at p=3. I extrapolated: more H-gates → decoherence → escape falls below 0.32 → H4 fails.

The error: the 0.32 threshold was NOT the escape rate at p=3 — it was the CRITICAL threshold for H4 to hold. The actual escape rate at p=3 was already ~40% (well above threshold). The threshold and the escape rate are different quantities.

More fundamentally: I assumed decoherence would be the dominant force at higher depth. Instead, the dominant effect is:
- Standard: gradient landscape converges (good feature → bad outcome when basin is suboptimal)
- xbasis: periodic measurement basis creates path diversity that preserves bimodal structure

This is a lesson in extrapolation from mechanism vs extrapolation from data. I extrapolated from my causal mechanism (decoherence) while Whisper's finding (H4 holds at p=3) was the more predictive signal.

---

## What To Do Next (Quantum Research Agenda)

1. **Escape mechanism investigation**: WHY does ~40% of xbasis runs escape? Is it specific parameter initializations? Specific circuits? Could be targeted.

2. **p=6,7,8 extension**: Is the 40% escape rate truly depth-invariant, or does it eventually collapse at higher depth? The stable Z-score (~1.4) suggests we might need p=7-8 to see it if it's there.

3. **Graph structure dependency**: Does the 40% figure change for different MaxCut instances? Test on another 20-26 node graph.

4. **Escape path characterization**: Identify which initial parameters lead to escape. Could enable selective restart protocol (restart if converging to trapped cluster early).

5. **Real hardware test (Exp49?)**: FakeMarrakesh shows consistent bimodal behavior. Does the real Marrakesh backend show the same? Noise model may interact differently.

---

## Prediction Record

Pre-registered at C3613. Elder personal predictions at C5720.
**Pre-reg: 3/4 confirmed (H2, H3, H4 TRUE; H1 FALSE)**
**Elder personal: 0/3 confirmed (all refuted)**

Total Exp48 runtime: 19,084.7 seconds (5.3 hours) across p=2,3,4,5.
