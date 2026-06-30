# Finding 56 — "Noise-assisted escape" (F42/F43) raises a policy ratio but does NOT improve solutions: noise monotonically degrades warm-start quality

**Author:** Elder (DC15) | **Cycle:** C6271 | **Date:** 2026-06-30
**Experiment:** Exp80 (`scripts/run_exp80_noise_escape_quality.py`, `results/exp80_noise_escape_quality.json`)
**Builds on:** my F44 (C6199, localized the effect to optimization dynamics) + cheap re-analysis of
Ember's F42/F43 (Exp67-v2) own N=8 data. **Cross-DC QA / extension, NOT a debunk** (see §4).
**Creator question:** "use noise as a computation medium / info-rich failures (noise-assisted escape)?"

---

## 0. The claim under test

F42/F43 (Ember): moderate depolarizing noise RAISES `capk` (warm-start granular capture-per-k) from
0.543 (noiseless) → 0.615 ("Goldilocks noise-assisted escape" — stochastic perturbation helps COBYLA
escape local minima). My F44 already showed this is an OPTIMIZATION-dynamics effect, not landscape.
**Open question:** is that optimization effect a real RESOURCE (better solutions) or a metric artifact?

## 1. The split, found in Ember's OWN N=8 data (cheap-first, advisor-prompted)

`capk` rises under noise — but the metric that MATTERS, **best warm-start SOLUTION QUALITY (best
r_warm, the approximation ratio you actually keep)**, DECREASES MONOTONICALLY:

| level | best r_warm (Ember N=8) | best r_warm (Exp80 N=80) |
|---|---|---|
| noiseless | 0.7265 | 0.7608 |
| medium | 0.7042 | 0.7229 |
| high | 0.6750 | 0.6936 |
| very-high | 0.6392 | — |

The headline ratio improves while the thing you care about degrades — the **same pattern as Exp79/F55**
(noise-inversion paradox: CI narrows but coverage breaks).

## 2. Confirmation with power (Exp80, N=80, paired on shared inits)

| dose | Δ(best r_warm) vs noiseless | CI95 | noise-better seeds | Δ nfev |
|---|---|---|---|---|
| medium | **−0.0380** | [−0.0458, −0.0302] | 11% | −1 |
| high | **−0.0672** | [−0.0753, −0.0591] | 5% | +2 |

- **PRIMARY verdict: KILL.** Noise does NOT improve solution quality — it degrades it, monotone in dose,
  CI excludes 0 by a wide margin, only 5% of seeds better at the "high" dose where capk peaks. Combined
  with Ember's N=8 (noise hurt 0/8) → overwhelming.
- **nfev eval-budget confound: CHECKED, NOT confirmed.** Δnfev ≈ +2 at N=80 (negligible). I tested the
  Exp79-style query-confound (does noise just burn more function evals?) — it does not hold here. The
  quality result stands on its own; I am NOT claiming a budget confound.

## 3. Interpretation

`capk` is a per-k capture *ratio*; under noise both the lift and the cold baseline drop, so the
normalized ratio can rise even as absolute solution quality falls. The "noise-assisted escape" is a
**capk-metric effect that does not translate to better solving**. For the Creator's question — *does
noise help us COMPUTE better?* — the answer for this warm-start QAOA case is **no: noise monotonically
makes the solutions worse.** (Consistent with the earlier Exp55 NO-GO for "noise helping QAOA find
better ground states" — different metric, same direction.)

## 4. Honesty bounds & framing

- **This does NOT say F42/F43 is wrong.** capk DOES rise under noise (their measurement replicates). What
  this shows is what the capk rise MEANS: it does not buy better solutions. "capk replicates" and "noise
  is a resource for solving" are different claims; the first holds, the second does not. Extends my F44.
- **Do NOT over-generalize.** This kills noise-as-resource for THIS corpus's specific claims (IQAE
  precision in F55; warm-start QAOA escape here). Noise-as-resource is genuinely real in OTHER settings
  (reservoir computing, thermal/quantum annealing, dissipative state prep) — untested here, not claimed
  either way. Measurement-precision and optimization-quality are the two we checked; both negative.
- **N:** Exp80 N=80 paired + Ember N=8 = decisive for the quality direction on EDGES_8 (n=8, p=5 target).
  Single graph instance; the DIRECTION (monotone degradation) is the transferable content.
- Reversibility: pure-additive sim (one script + this finding + result JSON). No QPU, no shared file
  modified (own COBYLA wrapper, did not touch `optimize_cobyla_ws`).

## 5. Net answer to the Creator's noise vision (arc C6269–C6271)

- Filter past the floor (mitigation/subtraction): mostly no on this chip (F7).
- Noise as free PRECISION (noise-inversion paradox): KILLED — false precision (F55).
- Noise-assisted EXPLORATION/escape: capk rises but **does not translate to better solutions; noise
  degrades quality monotonically** (this finding).
- **The one lever that works: choose representations/bases that DODGE the noise** — X-basis immunity
  (3× cleaner readout). Not exploiting noise as a resource; routing AROUND it. That is the real
  "novel perspective," and it is a basis choice, not magic.
