# Exp144 §4 baseline adversarial self-red-team (Elder C6510, 2026-07-17)

Gate-2 item (chair checklist #1, C4771b). Mandate per §4: actively attempt to construct a
poly single-copy shortcut for the PROMISED ensemble (commuting, full-weight, m=3, public
grid, fixed t) — if found, it becomes the baseline. MC companion:
`exp144_baseline_redteam_mc_elder_c6510.py` → `exp144_baseline_redteam_mc_results_c6510.json`.

## Attacks attempted (all against our own §4 baseline)

1. **Commutation prior-narrowing.** After finding term 1, candidates restrict to strings
   commuting with it (~M/2), then ~M/4. Real but constant-factor — Θ(3ⁿ) stands.
   ADOPTED into the baseline anyway (MC includes it; the baseline gets every legal edge).
2. **Low-weight leakage.** Could low-weight observables ⟨P′(t)⟩ carry information about
   full-weight terms? P′ evolves onto P′Pⱼ products of weight ≥ n−w(P′); a product input
   state only gives nonzero expectation when its letter axes align with the near-full-
   weight product — i.e. the setting must letter-match on ~n qubits: hit probability
   3^−Θ(n). No shortcut; this is the CZSJ/CCHL mechanism in our concrete family.
3. **Tilted product states (magic-angle shadows).** Non-eigenbasis product inputs give
   EVERY candidate nonzero signal — of magnitude ~3^{−n/2} (full-weight shadow norm).
   Shots ~3ⁿ. Same wall, different door.
4. **Adaptive group testing / binary search.** Needs partial-match signals to steer; by
   (2) partial matches read ~0. Adaptivity between shots has nothing to steer on until a
   full match fires. (Consistent with CZSJ Thm 3 covering ADAPTIVE ancilla-free.)
5. **Concatenation (V^k per shot).** Coherent angle amplification kθ helps PRECISION,
   never the 3ⁿ SEARCH (an unmatched setting reads 0 regardless of k). Metered as k uses.
   RECOMMENDATION: §4 should explicitly PERMIT concatenation (symmetric access, stronger
   baseline, asymptotically immaterial) — honesty upgrade, zero cost.
6. **Simultaneous diagonalization.** The Clifford C diagonalizing all terms would read
   the vector at once — but finding C ≡ finding the terms. Circular; no shortcut.
7. **Grid/fixed-t degeneracy exploitation.** Grid values are public but enter only
   through sin²(θⱼ); no candidate-elimination structure beyond (1). No shortcut.

**VERDICT: no poly single-copy shortcut found. §4's SPRT candidate sweep (with
commuting narrowing + concatenation permitted) is the strongest baseline we can
construct. The 3ⁿ-regime wall is per-setting full-weight coverage — the design intent
holds under self-attack.**

## MC-firmed meter (replaces assumed per-candidate shot counts)

SPRT per candidate (two-sided, α = 0.01/M Bonferroni — one false term breaks support
exactness; β = 0.05; worst planted signal sin(2·0.30)·(1−2q_eff)):

| n | M=3ⁿ | E[N\|null] q=.05/.10 | meter (mean) | quantum budget | **ratio (conservative)** |
|---|---|---|---|---|---|
| 4 | 81 | 35.8 / 44.9 | 1.9k–2.3k | ~5.6k | **0.33–0.40** |
| 6 | 729 | 35.5 / 45.2 | 14.4k–18.3k | ~5.6k | **2.5–3.1** |
| 8 | 6561 | 36.5 / 47.6 | 130k–170k | ~5.6k | **22–29** |

(My pre-MC hand estimate was 15 shots/candidate — the MC says 36–48. Test, don't
assume: the correction moved every ratio ~2.5× in OUR favor, which is exactly why it
had to be measured, not assumed — a flattering error is still an error.)

## THE DESIGN FINDING — n=4 is a structural LOSS rung, and that is USEFUL

The quantum budget is τ-precision-bound (m_bell=1000, B3), nearly n-independent; the
baseline meter scales as 3ⁿ. At n=4 the haystack (81 candidates) is simply too small:
the baseline wins ~3× even against our best play. Options for the chair:

- **(a) RECOMMENDED — freeze n=4 as a pre-registered NEGATIVE CONTROL rung:** declare
  in §5 that the expected n=4 ratio is <1 (baseline should WIN it), excluded from the
  overall-WIN count (overall = n6 AND n8). If the flown n=4 ratio comes out >1, that
  is a METER/BASELINE MISCALIBRATION FLAG, not a win — the rung becomes an integrity
  check on the whole metering pipeline. Turns the weak rung into a falsifier.
- (b) Drop n=4 (saves ~5×6k shots + 5 seals; loses the control value and the scaling
  trend's third point).
- (c) Keep as-is with honest R_THRESHOLD(4) <1 (rung unwinnable, dead weight, confusing
  to report).

Provisional R_THRESHOLD floors (final freeze at kit stage with fingerprint-anchored
q_eff + Ember-pattern full conventional-meter MC): **R(6) = 1.5, R(8) = 10** (set at
~½ the conservative-mean ratios; comfortably above 1, comfortably below the MC means).
n=4 per option (a): no threshold — control expectation "ratio < 1" pre-registered.

## Status

Gate-2 checklist item #1 (red-team): **DONE — no shortcut found, baseline upgraded
(narrowing + concatenation), meter MC'd, thresholds provisionally floored.** Remaining
pre-freeze: kit build + §G2.1 law check in the real builder + final R/θ freeze +
fingerprint-arm selection + §5 amendment per chair's option call on n=4.
