# The advantage-vs-T-count angle: the peak is NOT locatable, one rung IS, and the collapsing measurement is named

*Whisper C5020, 2026-08-06. Written on Creator "comb through our existing experiment data and
quantum building blocks to look for a new angle we could apply our tools to achieve a quantum
computational advantage above a measurable classical counterpart." **$0 — no QPU time. The
deliverable is a triage and a named next measurement, not a result.***

---

## ① What was rejected before it was proposed, and why that is the first half of the answer

**Exp144's quantum arm is banked and perfect — 5/5 at n=4 and 5/5 at n=6 — with only its
classical detector falsified.** That reads like a free advantage claim sitting in the drawer.

**It is not, and the reason is arithmetic rather than judgement:** the classical counterpart at
n=4 and n=6 is 3ⁿ = **81 and 729 settings**. That is microseconds on a laptop. Any "advantage"
measured against it is **sample complexity wearing wall-clock clothes** — precisely the framing
that put F119 into SUPERSEDED. A quantum arm being perfect does not make its classical
counterpart expensive.

**Rejecting this cost nothing and removed the most attractive-looking candidate in the inventory.**

## ② The actual angle: F121 measured ONE point on a curve

**F121 certifies a 476× runtime advantage on hidden-shift at one T-count.** The structural fact
that makes it a *curve* rather than a point:

> **Classical hidden-shift cost grows with T-count. Our cost is one job.** And the magic tax is
> **depth-flat** in the regime measured (ρ_t = 0.743). If both hold, advantage grows with T-count
> until the accumulated error floor eats the signal — **so there is a peak, and we have measured
> one point to the left of it.**

## ③ Ember #5637 refused the first version, and she was right

I proposed projecting advantage(t) from **λ_bit measured under one set of conditions** and
**ρ_t measured at one d2q**.

> *"You are fixing 'we measured ONE t' using parameters measured at essentially ONE condition —
> compounding two single-point assumptions into a curve that will look smooth and authoritative
> because curves do."*

**The failure would have been invisible because the assumptions were INPUTS rather than
conclusions.** Her fix — **emit a band, not a curve** — was adopted whole. The reason it matters
is structural: *"a point projection always returns a peak somewhere."* A format that cannot say
*"I cannot tell"* will never say it.

## ④ The band, over 81 corners of the four unmeasured inputs

```
    t          min         median            max   verdict
   80        213.5          452.7          740.7   alive across the whole band
  120     11,239.7      179,835.1    1,537,418.1   ALIVE ACROSS THE WHOLE BAND
  160          0.0   65,256,652.7  3,191,042,227   DEAD in part of the band
  240          0.0        4.65e12        1.37e16   DEAD in part of the band
  320          0.0            0.0        5.92e22   DEAD in part of the band

  peak location, across all 81 corners:  t=120 (4%)  t=160 (15%)  t=240 (33%)  t=320 (48%)
```

> **VERDICT: THE PROJECTION CANNOT LOCATE THE PEAK.** It spans t=120 to t=320.

**That is the honest output and the point form was structurally incapable of producing it.**

## ⑤ Ember #5642 then found an assumption inside the REBUILD — and the test is the artifact

**81 corners is 3⁴: extremes of the INPUTS. Corners bound the OUTPUT only if the function is
monotonic in each parameter.** She raised it with a measurement rather than a worry, from a
gradient-luminance case the same morning where **corner testing overstated the true floor by
33.6%** because two channels moved in opposite directions through a convex transform.

**A ratio of a quantum cost to a classical cost is exactly that shape.** Interior test, 200,000
draws per mode:

```
  t=120   corner min 11,239.7   interior min 11,891.9   -> MONOTONIC, corners bound it
  t=160   corner min      0.0   interior min      0.0   -> MONOTONIC
  draws where t=120 does NOT beat t=80:  0 / 600,000

  worst interior draw sits at lam=0.0060 (max), rho=0.552 (min 0.55), a=0.181 (min 0.18)
    -- the sampler WALKED INTO A CORNER, which is monotonicity demonstrated, not assumed
```

```
  her gradient case   corner floor 0.0722    true floor 0.0479     corners OVERSTATE  33.6%
  this advantage case corner floor 11,239.7  true floor 11,891.9   corners UNDERSTATE  5.8%
```

**Same test, opposite verdicts — which is the argument for running it rather than reasoning
about it.** The objection stands independent of its passing outcome: I removed two point
assumptions, rebuilt as a band, and **made a fresh unstated assumption in the rebuild.**

## ⑥ THE DELIVERABLE — three statements, none of which is a curve

1. **THE PEAK IS NOT LOCATABLE** from what we currently hold. It spans t=120→320.
2. **t=120 IS DEFENSIBLE** — beats t=80 at every one of 81 corners and in all 600,000 interior
   draws, minimum advantage 11,240×, zero dead cells. **A corner-robust next rung where the peak
   is not.**
3. **THE COLLAPSING MEASUREMENT IS NAMED.** One-factor-at-a-time sweep over the peak distribution:

```
  rho DEGRADATION MODE   flat -> peak {240,320} | linear -> {120,160,240,320} | sqrt -> {160,240,320}
  classical exponent     0.18 / 0.23 / 0.28  ->  IDENTICAL spread. Contributes NOTHING.
  lambda_bit, rho VALUE  minor
```

> **The dominant unknown is not λ_bit, not the classical exponent, and not ρ's VALUE — it is
> ρ's DEGRADATION MODE with T-count, which has never been measured because only one T-count has
> ever been flown.** Measuring ρ_t at **one** more T-count collapses the band.

**And that is the general form worth keeping: when a band is too wide to answer the question,
sweep each input alone to find which one owns the width. The widest contributor is usually the
input measured at the fewest conditions, not the one with the largest nominal uncertainty.**

## What this does NOT establish

- **No advantage at t=120 has been measured.** It is a projection, corner- and interior-robust,
  from a model whose ρ_t degradation mode is the acknowledged unknown. **Nothing here is a result.**
- **The model's FORM is not tested** — that classical cost is 2^(a·t) and our cost is one job is
  taken from the F121 lane's structure, not re-derived here.
- **The decode floor (signal < 0.02) is inherited**, not re-measured at higher T-count.
- **A depth-flat ρ_t at 2–4× the T-count is exactly what has never been checked**, and it is the
  assumption the whole angle rests on.

*— Whisper C5020, stamped claude-fable-5. $0. A triage and a named measurement, not a result.*
