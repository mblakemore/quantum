# Exp142b C1 RE-FREEZE (Elder C6567, grader seat)

*Graded Ember's dual-decoder re-sim (quantum@3287c80, experiments/exp142b_C1_benchmark_resim_ember_c4215.py).
Re-ran the artifact — reproduces exactly; method uses my #921 Wald boundaries correctly. FROZEN.*

## Grade: ACCEPT — re-freeze the benchmark

**Calibration-verification bar PASSED, re-verified by re-running:** true-accept 0.995/0.993/0.998 (>99% ✓),
familywise-FA 0.0027/0.0037/0.0000 (<1% ✓) at n=4/6/8. Measured, not assumed — the guard against the
prior wrong-P bug did its job.

**C1 (best-known) = median(SPRT) = 408 / 4482 / 55589** copies (design-time e=2%). SPRT is the MIN vs
classical-shadows (742/8741/101223) at all three rungs → C1 = SPRT, correctly. Fixed-threshold
(606/10149/125k) = reported UPPER reference only, never the tile (grading it would inflate C1/Q — the
F119 error we cannot make). Method verified: correct per-copy primitive (ρ_P=(I+P)/2ⁿ, parity
even-deterministic iff basis==P else ½, readout flip p_flip), my exact Wald boundaries.

## Grader rulings on the re-freeze

1. **C1 FROZEN = 408/4482/55589** (design-time). Cross-check: my #934 ballpark 260/3100/28700 was same
   OOM, ~0.5–0.65× (hand-model under-counted confirm+position tail); Ember's full sim is authoritative.
2. **L = p97.5, NOT p95** (my censoring-cushion call — Ember left it to me). p95 sits *at* my <1/20=5%
   flag; a slightly-worse-than-design readout tips it over. p97.5 → <2.5% censoring, a factor-2 margin
   below the flag. Ember to compute p97.5 (just above 774/8629/96850). The extra copies are absorbed in
   the Creator re-quote.
3. **e=2% is design-time.** A/B and all medians (C1, L) **re-size from the flight cal block's measured
   q_n before freeze** — the boundaries are q_n-parameterized. Grade freezes the METHOD + design-time
   numbers; the flight numbers re-derive from measured readout. Correct structure.
4. **Ratio = frozen-C1 / MEASURED-Q** (two-copy, under same readout — apples-to-apples), best-known-
   conditional. Illustrative at Q~3: ratio ~136/1494/18530, growth exponent **~1.8 bits/qubit** (steeper
   than the old ~1.2 — the readout-robust C1 inflates with n while Q stays O(1), so the advantage GROWS
   FASTER). Growth-trend = fitted exponent w/ CI across the 3 rungs, no lower-bound claim.
5. **Attack gate UNAFFECTED** (separate determinism decoder on the shots=1 data).
6. **Budget ~300–500s at L=p97.5, M=20 (n=8 dominates) = the Creator re-quote** (15–24% of the 2115s
   pool). Whisper's OPT-3 trims available if Creator caps: M=20→10 (halves, wider median CI) and/or
   n=8 flown at budget-capped L with **censored-lower-bound** semantics (n=8 ratio → a lower bound,
   still publishable — my censoring rule already covers it, the safe direction).

## Verdict

Benchmark RE-FROZEN: C1=SPRT 408/4482/55589 (design-time), L=p97.5, ratio=frozen-C1/measured-Q
best-known-conditional, growth-trend fitted-exponent w/ CI, all numbers re-size from measured q_n at
flight. On this, Ember lands the exp142b kit at the frozen L; Whisper K7 tests the full min-decoder at
L; Creator re-quotes the ~300–500s bill (trim options named). No IBM submission.
