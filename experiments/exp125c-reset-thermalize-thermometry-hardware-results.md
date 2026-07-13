# Exp125c — CERTIFYING THE FRONTIER: hardware results (Whisper C4665)

**Verdict: G-therm FAIL → the pre-registered META-FINDING. Three independent axes converge: the erasure
effect lies below NISQ's certification floor. STOP — no Exp125d.** Job `d9ak0i7u62qs738o5e8g`
(ibm_marrakesh, q4, 6 pubs, 240k shots, ~seconds QPU incl. 590 µs idles). Prereg FROZEN, advisor-audited.
Grader `scripts/grade_exp125c.py`, results `results/exp125c_grade.json`.

## What the reset-thermalize ladder found

| delay (≈×T1) | P(1) | | delay | P(1) |
|---|---|---|---|---|
| 0.1 µs (post-reset) | 0.00875 | | 360 µs (3×) | 0.00630 |
| 40 µs (⅓×) | 0.00750 | | 590 µs (5×) | 0.00660 |
| 120 µs (1×) | 0.00695 | | | |

**ΔP = P(590µs) − P(0.1µs) = −0.00215 ± 0.00062 (−3.5σ).** The population **decays** with idle, it does not
rise: q4's active reset leaves it **warmer** (P₁≈0.0088) than its thermal equilibrium (P₁≈0.0063–0.0066),
which then relaxes down (τ_fit ≈ 59 µs, a real relaxation on a ~0.002 signal). **G-therm (ΔP−5·SE>0): FAIL.**

## Why this certifies the boundary, not a soft null

The conservative estimator worked exactly as designed. ΔP is a lower bound on `d·p_eq`; ΔP < 0 means reset
could not prepare a reference **colder** than equilibrium, so the thermal population cannot be resolved from
below — and the equilibrium reading itself (P₁ ≈ 0.0063) sits **at/below q4's readout error (0.0073)**, so it
cannot be resolved from readout either. **q4's effective temperature is below the SPAM floor from both
directions.** Crucially the method did **not** fabricate a positive p_eq: QND-repeat would have read
measurement-induced 1→1 correlations as thermal population and returned a false ACCESSIBLE — the reset-
thermalize cancellation (readout + meas-induced excitation are t-independent) is why the answer is honest.

## THE META-FINDING (pre-registered as the acceptable outcome)

Three independent measurement axes now agree that the coherent-erasure advantage cannot be **certified** on
this NISQ hardware — each for a different, named instrument reason, none of them the physics:

| Axis | Finding | Instrument wall |
|---|---|---|
| **F104** (classical floor vs credit) | demon pays directionally 1.3–1.7×, 2.9σ | single-window credit SE (0.0098) |
| **F105** (coherent bonus vs tax) | bonus 0.109 E beats both taxes at point, STRADDLE | tomographic SPAM (floor bracket →0) |
| **F125c** (q4 effective temperature) | ΔP = −0.0021, thermal unresolvable | q4 colder than its readout error; reset warmer than equilibrium |

The physics has been consistent and clear at every point estimate (the demon pays; the bonus beats the tax;
the entanglement is 42σ-ample). What is **not** available is a 5σ certificate — and F125c closes the question
of whether a cleaner thermometer would deliver it: **the standard one (ef-Rabi) is boundary-blocked
(open_pulse:False), and the best gate-model substitute finds q4's temperature below its own resolution.**
Per the frozen ceiling (advisor C4665): **this convergence IS the finding. STOP. No fourth refinement.**

## The honest close of the H4 arc

The thermodynamic arc's final invoice (F86→F104→F105→F125c) reads, in full and without softening: the ICO
engine runs; information does thermodynamic work; the classical demon's erasure bill is directionally paid;
the coherent demon holds ample entanglement (42σ) for its negative-entropy bonus to beat every measured tax
at the point estimate — **but none of the three erasure sub-claims reaches 5σ, and all three walls are named,
measurement-limited, and (for the credit-SE one) actionable off-NISQ.** A trustworthy null-of-certification
around a directionally-clear physics, closed by three converging axes rather than an endless refinement
ladder. Nothing is free — not even the certificate.

## Predictions (Whisper C4665) — calibration

| Pre-filed | Conf | Outcome |
|---|---|---|
| G-therm resolves ΔP>0 at 5σ | 0.50 | **MISS** (ΔP=−0.0021; reset warmer than equilibrium) — well-hedged at 0.50 |
| ladder fit τ ~ T1 (rise is thermalization) | 0.70 | **PARTIAL** — real decay τ≈59 µs on a tiny signal; dynamics present, magnitude rough |
| if resolved: coherent CERTIFIED / classical straddle | 0.60/0.55 | N/A (not resolved) |

## One line

The frontier is not certifiable: q4 is colder than any thermometer this chip allows, and three independent
axes agree the coherent-erasure advantage lives below NISQ's certification floor — the physics points home at
every point estimate, the certificate stays out of reach, and the honest move is to stop.
