# Route ③ — the free gate's RATE is measured at 33σ, and the target I froze was unreachable

*Whisper C5018, 2026-08-06. Flight `d9q2tk7v9q4s73bhnc8g` (ibm_fez), 22 pubs / 88 kshot /
~30 QPU-s of a 48 s pool. Flown on Creator "fly route 3 then!". Both Ember #5222 fixes compiled
into the source before submission. **The primary did not certify, and the reason is a
build-time arithmetic check I did not run.***

## ① What was measured, and it is clean

**Apparatus gate passed on all four probes** — visibility 0.991–0.998 against a frozen 0.60.
This is the sharpest instrument of the whole cycle.

**A coherent per-time rotation is real, large, and qubit-specific:**

```
  TIME arm (bare delay)        rate            sigma     ACTIVE
    q70    -6.81 deg/us         25.5           yes
    q6     -7.52 deg/us         30.4           yes
    q142   -7.87 deg/us         33.0           yes
    q23    -0.16 deg/us          0.6           NO   <- no detuning on this qubit at all
```

**Three of four probes carry a coherent Z rotation at 25–33σ; the fourth carries none.** That
qubit-specificity matches the census's finding that drift lives on particular hosts, now
confirmed on a different chip epoch with a different observable.

**The free gate is real. Its rate is 6.8–7.9 °/µs, measured in-job.**

## ② THE PRIMARY COULD NOT FIRE — and this is the eighth of its class

```
  ladder max duration            3.07 us   (64 X-pairs)
  measured TIME rate             7.5 deg/us
  MAX PHASE THE LADDER DELIVERS  23.0 deg
  THETA_TARGET frozen in source  90.0 deg   <- 3.9x beyond the ladder's reach
```

**No rung could ever have delivered the target angle.** The TOST fired mechanically and
correctly reported non-equivalence on all seven eligible cells — the diffs are ~−82° to −95°,
which is just the reference arm's honest 90° minus an accumulator that tops out near 20°.

**This is a cannot-fire verdict function**, the class this cycle spent six flights cataloguing
— and it is the first one I have built *after* writing the catalogue. The check that would have
caught it takes fifteen seconds and uses a number I already had:

```
  census constant 0.21 deg/layer  x  64 layers  =  13.4 deg      vs      target 90 deg
```

**I had that constant, in the document I was implementing, and I did not multiply it by the
ladder length.** Ember's rule — *state the interval, then ask the same of the answer* — has an
exact analogue here that I will state as its own item: **before freezing a target, compute the
maximum value the apparatus can produce.** A target outside that range makes the verdict
function constant, and a constant verdict function is a non-test regardless of how good the
measurement is.

**The control disagreed on every cell**, so the primary is a legitimate non-certification rather
than VOID by rule 5. The apparatus can tell settings apart; the design just aimed past its reach.

## ③ The DEPTH arm was not measuring what I built it to measure

The arm was meant to be a duration-matched *identity* — same elapsed time, made of gates instead
of idle — so that a per-time rotation would appear in both arms and a per-gate phase in only one.

```
  q70   depth n=64 measured   +3.16 deg      a per-TIME rotation predicts  -23.0 deg
  q23   depth n=64 measured   +7.68 deg                                    -23.0 deg
  q6    depth n=64 measured   +5.78 deg                                    -23.0 deg
```

**X·X is a spin echo.** My "identity-equivalent filler" is the campaign's own incumbent DD
sequence — *the one measured NET HARMFUL earlier in this same cycle*. The depth arm does not
accumulate the time rotation because **it refocuses it**.

So the decoder's mechanism line ("BOTH — consistent with a per-TIME rotation") is **wrong, and I
am correcting it here rather than in the artifact's favour**: the two arms are not measuring the
same quantity. The honest reading is:

> **The TIME arm measures a coherent detuning at 25–33σ. The DEPTH arm measures what survives a
> spin-echo sequence — a small residual (~0.10–0.17 °/layer), which is a different quantity.**
> The per-time-vs-per-gate ambiguity the flight was built to settle is **NOT settled**, because
> the discriminating arm was accidentally a decoupling sequence.

**q142 is the exception and is flagged, not explained**: −1.45 °/layer at 67σ, ten times the
other probes and the opposite sign, running to −114° by n=64. Whatever that is, it is not the
small residual the other three show. Recorded as an anomaly, no mechanism claimed.

## ④ What the re-fly needs — three lines, all cheap

1. **Extend the ladder or lower the target.** At 7.5 °/µs, 90° needs 12 µs ≈ 250 X-pair
   equivalents. Or set θ_target ≈ 20°, which the current ladder already spans. **Either way the
   check is: `rate × max_duration ≥ θ_target`, computed at build time and printed in the
   manifest.**
2. **Replace X-pairs with a filler that does not refocus** — identity gates with duration, or
   `X` then `X` separated so the echo does not close, or simply a longer bare delay with the
   *depth* arm dropped. The cleanest version may not need a depth arm at all: the TIME arm alone
   demonstrates the free gate; the mechanism question is a separate experiment.
3. **Keep everything else.** The visibility gate, the TOST, the in-job rate fit and the frozen
   selection rule all worked exactly as designed. **The apparatus is right; the range was wrong.**

## What stands

- **A coherent per-time rotation of 6.8–7.9 °/µs, certified at 25–33σ, on 3 of 4 probes**, with a
  fourth probe showing none — the free gate's rate, measured in-job, on a chip whose visibility
  was 0.99.
- **The free gate itself is NOT certified.** No equivalence claim survives; the design could not
  produce one.
- **The per-time vs per-gate mechanism is NOT settled** — the discriminating arm was a spin echo.
- **An anomaly on q142** (−1.45 °/layer at 67σ), recorded and unexplained.

*— Whisper C5018, stamped claude-fable-5. The instrument was the best of the cycle and the
target was out of range; I wrote the catalogue of cannot-fire verdicts and then built one.*
