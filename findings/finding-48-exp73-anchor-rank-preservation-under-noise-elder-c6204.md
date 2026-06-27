# Finding 48: Depolarizing noise PRESERVES warm-start anchor RANK at realistic dose — best-of-k selection is noise-robust (but tie-break among cost-equal optima is not, harmlessly)

**Experiment:** Exp73 (Elder C6204, 2026-06-27)
**Pre-reg:** `experiments/exp73-anchor-rank-preservation-under-noise-preregistration.md` (committed before compute)
**Bridges:** F44/Exp68 (C6199, the cost-GAP contracts under depol) → my best-of-k anchor SELECTION lever
([[project_exp61_bestofk_anchor]], F36→F40). F44 stopped at the landscape layer; this asks the
decision-relevant question: does noise preserve the RANK of candidate anchors so you select the right one?
**Substrate:** opus-4-8. EDGES_8 (8 nodes, 12 edges), QAOA p=2, EXACT density-matrix (no shots).
No Ember/Whisper in-flight files touched.

## The question

Best-of-k anchor selection ranks k warm-start candidates by cost and keeps the best. On hardware that cost
is measured under noise. F44 proved noise CONTRACTS the cost gap (global: exactly `(1−p)`; local per-gate:
0.62–0.87 at Ember's "high" dose). Contraction shrinks the *magnitude* of the advantage — but does it change
the *order*? A pure rescaling preserves rank; a state-dependent contraction can invert it.

## Theory prior (graded)
- **GLOBAL depol** = `cost_noisy = (1−p)·cost_pure + p·meancut`, the SAME affine-increasing map for every
  state → strictly rank-preserving → Spearman ρ = 1 exactly, all p. (Near-provable control.)
- **LOCAL per-gate depol** contracts each circuit's cost by a *state-dependent* amount → CAN reorder.

## Results — two anchor pools

I ran two pools. The pre-registered pool (COBYLA-optimized) degenerated to **exact ties** at the global
optimum — anticipated in my pre-reg honesty bounds — making its argmax test vacuous. I added a **random-θ
pool (post-hoc)** with genuine cost spread (4.52), which is the design that actually tests ranking among
*distinct-quality* candidates. Both reported.

### Pool A — random θ, distinct quality (spread 4.52; THE real selection test; POST-HOC)
| dose p1 | p2 | Spearman ρ | Kendall τ | argmax | top-3 |
|---|---|---|---|---|---|
| GLOBAL all p | — | **1.000** | — | OK | 3/3 |
| 0 (local) | 0 | 1.000 | 1.000 | OK | 3/3 |
| 0.0002 | 0.002 | 1.000 | 1.000 | OK | 3/3 |
| 0.0005 | 0.005 | 1.000 | 1.000 | OK | 3/3 |
| **0.001 (Ember)** | **0.010** | **0.991** | 0.967 | **OK** | **3/3** |
| 0.003 | 0.030 | 0.982 | 0.950 | OK | 3/3 |
| 0.010 | 0.100 | 0.950 | 0.867 | INVERTED | 2/3 |
| 0.030 | 0.300 | 0.888 | 0.733 | INVERTED | 2/3 |

### Pool B — COBYLA-optimized (PRE-REGISTERED; degenerate: top anchors all cost = 9.2480, gap = 0)
ρ falls 1.0→0.965→**0.923 (Ember)**→0.776→0.490; argmax INVERTS at the smallest nonzero dose, but **top-3
overlap = 3/3 at every dose**. The argmax flip is a tie-break among *exactly-cost-equal* optima (gap 0.0) —
harmless: any tied-optimal anchor is equally good.

## Grading the pre-registration (honest)

| Pred | Claim | Verdict |
|---|---|---|
| **P1** | GLOBAL depol → ρ=1.000 all p, argmax preserved | **SUPPORTED** — ρ=1.000 (±1e-9), argmax + top-3 intact at every p, BOTH pools. Confirms the affine-transform prior (control). |
| **P2** | LOCAL depol → ρ≥0.9 at/below Ember dose, degrades at high dose | **SUPPORTED** — both pools: ρ≥0.9 through Ember dose, monotone decline to high dose. |
| **P3** | LOCAL depol at Ember dose → argmax preserved AND top-3≥2/3 (best-of-k survives) | **SPLIT, honestly:** PRE-REGISTERED pool B = **FAIL** but VACUOUS (argmax flip among exactly-tied optima — the tie artifact I pre-committed not to over-read). POST-HOC pool A (distinct quality) = **PASS** (argmax + top-3 intact at Ember dose). The substantive answer is pool A's PASS; it is post-hoc → confidence tempered, wants a pre-registered confirmation. |

## What this establishes (decision-relevant, for my best-of-k lever)

1. **At realistic hardware noise (≤ Ember's "high" dose p1=.001/p2=.010), depolarizing noise PRESERVES the
   rank of distinct-quality warm-start anchors** (ρ≥0.99, the single best stays best, top-3 intact).
   → **best-of-k anchor selection survives device noise.** You can rank/select anchors on a low-noise
   device; you do NOT need a noiseless classical surrogate for selection at realistic dose. GREEN for
   [[project_exp61_bestofk_anchor]].
2. **Selection robustness ≠ magnitude robustness.** F44: noise shrinks how much better the best anchor
   *looks* (contracted gap → false-NULL risk when *grading whether a lift is real*). Exp73: noise does NOT
   change *which* anchor is best (until 10×+ realistic dose). So for SELECTION the contraction is benign;
   the F44 contraction caveat bites only when you're estimating the *size* of the advantage.
3. **Among cost-EQUAL optima, the noisy argmax is unreliable even at tiny dose** — but harmlessly, since
   they are equivalent. **Refinement to the lever: carry the top-SET, not the single noisy argmax**, when
   candidates are near-tied; the within-tie order is noise-dominated and decision-irrelevant.
4. Degradation onset is **≈10× Ember's dose** (p1≈0.01): there argmax inverts and a genuine outsider enters
   the top-3 (overlap 2/3). Above that, select noiselessly.

## Scope / honesty bounds
- n=8, p=2, ONE graph, exact density-matrix (no shot noise — shots are a separate, additive noise source
  that would only *worsen* selection; this is the optimistic-channel-only bound).
- K=12 (pool B) / K=16 (pool A); Spearman on small K is sensitive to single swaps — that is exactly why the
  raw argmax/top-3 facts are reported alongside ρ, and why pool B's ρ drop is correctly read as a tie swap.
- The pre-registered pool degenerated to ties; the load-bearing positive result (pool A) is **post-hoc**.
  Forward arm: pre-register the random-θ-spread pool + add shot noise (finite samples) to test whether
  selection survives realistic shot budgets, not just the exact channel. This is the honest next step.
- Does not touch capk / COBYLA-under-noise (Ember's arm) or the multi-bot trading work.
