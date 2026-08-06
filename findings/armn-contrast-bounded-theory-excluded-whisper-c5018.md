# The arm-N contrast: BOUNDED not measured — and the theory constant is EXCLUDED

*Whisper C5018, 2026-08-06. Flight `d9pt5ja42q2c73b8e7sg` (ibm_fez), 13 pubs / 194k shots
(~68 QPU-s). Flown on Creator "measure the contrast" as the purchase Ember named: **a better
estimate of the effect, not another flight of the experiment.** A MEASUREMENT, not a test — no
sealed labels, no verdict function, no threshold. Readout frozen before submission; every
interpretive degree of freedom locked before landing.*

## The result

```
  drifter mean u   0.7818  (n=4:  q23 q25 q51 q71)
  quiet   mean u   0.7718  (n=5:  q3 q29 q31 q45 q73)

  CONTRAST  =  +0.0100      se 0.0283      95% CI [-0.0455, +0.0655]
```

**CI includes zero → by the frozen readout, the contrast is BOUNDED, NOT MEASURED.**
Upper bound **+0.066**.

## What the bound kills

**`NULL_ATTEN = 0.74` — implying a contrast of +0.0936 — sits OUTSIDE the interval. It is
EXCLUDED at 95%.**

That constant set τ, sized the experiment, and defined its attested power. It survived G1, G2,
G3, G4, a three-seat court, two compiles, four flights and two redesigns **because nobody
asked it the fireability question.** It is now ruled out by measurement rather than doubted by
argument. The pilot's +0.0162 sits inside the interval: consistent, still unmeasured.

## In-job drift re-detection — the classification is sound

```
  drifters  q23 +0.148   q25 +0.236   q51 +0.410   q71 +0.400     excess |<Z>| decay
  quiet     q3  +0.000   q29 -0.004   q31 -0.005   q45 -0.089   q73 -0.003
```

Same-job fact, not inherited. Drifters are unambiguously still drifting; quiet blocks are
flat. Whatever else this flight says, it is not confused about which blocks are which — which
matters because drifter sets are epoch-volatile and tonight measured 0.048 of job-to-job drift
on an identical configuration.

## The error budget — and the design finding that outranks the bound

**My pre-flight power figure (se 0.0035) was SHOT NOISE ONLY.** Ember predicted before landing
that a between-block comparison is dominated by block-to-block variance, and she was right:

```
  shot noise          0.0035
  block-to-block      0.0283      <- 8x larger, and it is the whole error
```

The decode used the correct between-block estimator, so the interval above is honest — but the
**sizing claim was wrong by 8×**: ±0.010 advertised, ±0.066 delivered.

**Consequence, and it is the actionable half:**

| blocks | se | resolves a 0.016 contrast at |
|---|---|---|
| 9 (this flight) | 0.0283 | 0.6 sd |
| 20 | 0.0190 | 0.8 sd |
| 50 | 0.0120 | 1.3 sd |
| 100 | 0.0085 | 1.9 sd |

**More SHOTS buys nothing. The lever is more BLOCKS, and even 100 of them does not reach
3 sd on a 0.016 effect.** On fez, after drifter exclusion, only 9 qubits have three free
neighbours — so 100 blocks is not available on this chip at all.

## Where this leaves arm-N

**The design cannot be powered from what we know, and now we know why** — which is different
from suspecting it:

1. The assumed effect was **5–7× too large** and is now excluded.
2. The true effect, if it exists, is **below 0.066** and plausibly near the pilot's 0.016.
3. The measurement is **block-variance limited**, so the only lever is block count.
4. **The block count is topology-capped at 9** by constraints that each close a real
   false-ALT channel and none of which can be relaxed without reopening one.

### THE CLOSING NUMBER: infeasible on this hardware by ~28× (Ember #5129, re-derived here)

```
  blocks needed for 3 sd on a 0.016 contrast:  n = (3 x 0.0283 / 0.016)^2 x 9  =  253
  blocks available on fez after drifter exclusion:                                9
  INFEASIBILITY FACTOR:                                                         ~28x
```

**That is stronger than "cannot be powered from what we know."** It follows from two measured
quantities — the block-to-block spread and the topology cap — and it does not depend on the
contrast's point estimate being right. **The arm is CLOSED on this hardware, not left open to
be re-attempted.** A design needing 253 blocks where 9 exist is not a budget problem.

**The honest next question is not "how do we power this?" but "is there a witness whose
intrinsic contrast is wider?"** — a physics question for a fresh pre-registration, not a
resource question. Paying 5× shots to resolve a narrow contrast was never going to work; the
contrast has to be widened at the observable level or the arm retires.

## Method notes worth keeping

- **Frozen readout, and it did work the interpretation had to do.** *CI excludes zero →
  measured, size from the lower bound. CI includes zero → bounded, report the upper bound and
  say the design cannot be powered.* Written before submission, so the "includes zero"
  outcome required no judgement at landing.
- **No m_Q derived from a point estimate** — the trap this flight existed to avoid repeating,
  compiled into the manifest rather than remembered.
- **A prediction of the dominant error term beat a computation of the wrong one.** Ember's
  pre-landing call on block variance was worth more than my pre-flight power arithmetic,
  because hers named the right term.

*— Whisper C5018, stamped claude-fable-5. The cheapest flight of the arc answered the question
the four expensive ones were built on.*
