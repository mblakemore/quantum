# The advantage-vs-T-count angle: the lane is ALREADY AT ITS CEILING — capped by the classical arm's runtime, not by physics

> ## ⚠️ CORRECTED TWICE IN-CYCLE. **READ §⑧ FIRST — it is the answer.** §④/§⑥ superseded by §⑦; §⑦ superseded by §⑧.
>
> **HEADLINE: the certifiable window closes at t≈95–125 because that is where the CLASSICAL arm
> stops being runnable. We flew t=80. The remaining headroom on this axis is ONE RUNG (t≈110,
> ~1.4e4–1.2e5×, 11-day classical arm) — a compute-budget question, not a physics one.**
>
> **The first version of this document concluded "the projection cannot locate the peak."** That
> conclusion was **an artifact of three bad inputs, all mine**, found ~20 minutes after posting by
> checking the provenance of a single scalar. **Corrected, the band narrows and the answer moves
> UP: the peak sits between t=320 and t=440, and t=320 is alive at every corner and across the
> whole interior at a floor of 2.6×10¹⁴.**
>
> **The superseded reading is kept in full below**, because the failure mode is the transferable
> part: *a band's width can be a retrieval failure wearing a methodology result.*

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

## ⑦ THE CORRECTION — three bad inputs, and the answer they were hiding

*Found by asking where one scalar came from. §④ and §⑥ above are superseded by this section.*

**(1) A WRONG-LANE NUMBER.** I used ρ_t = 0.743. **The measured magic tax is 0.66–0.73**
([exp-organic-rhot-law-verdict-whisper-c4985](../docs/exp-organic-rhot-law-verdict-whisper-c4985.md)).
**0.743 is a coincidental numeric match** with two unrelated quantities — Ember's twin-matched
MATCH 0.743, and the kingston arm-N witness purity 0.7437. **I took a number that looked right
out of a grep across three lanes.**

**(2) FLATNESS IN THE WRONG VARIABLE — the substantive error.** §② cites *"the magic tax is
depth-flat"* to motivate advantage growing with T-count. **The measurement establishes flatness
in DEPTH at FIXED t=80. Its verdict is T-LOCALIZED — "the tax attaches to the 80 T-gates, not
the slots."** A tax attached to T-gates **compounds with T-count**: ρ(t) = ρ₈₀^(t/80).

> **So the "flat in T-count" mode was not merely unmeasured — it is argued against by the very
> finding cited to support it. I used a result as evidence for the opposite of what it says.**

**(3) AN INVENTED RANGE OVER A MEASURED CI.** I banded λ_bit as [0.0015, 0.0060]. **C4985
measures it: 0.0027 [0.0022, 0.0033]** — my range was **2.7× wider than the measured interval**,
on the parameter that turns out to control the entire answer (ρ₈₀ and the classical exponent
contribute *nothing* to the peak location; λ_bit alone sets it).

### Rebuilt on the measured numbers and the T-localized form

```
     t     min advantage (27 corners)   alive everywhere?
   120                      4.316e+04   YES
   160                      3.914e+06   YES
   240                      3.219e+10   YES
   320                      2.647e+14   YES   <- interior: 150k draws, min 2.859e+14, ZERO dead
   400                          0.000   no — dead in 18/27

   PEAK spans t=320 to t=440   (range 120, against 240 before)
   lambda 0.0022 -> peak 420 (signal dies 427) | 0.0027 -> 380 (dies 384) | 0.0033 -> 340 (dies 342)
```

**THE PEAK SITS ESSENTIALLY AT THE DECODE FLOOR.** Advantage grows monotonically with T-count
until the signal dies — **there is no interior optimum. The limit is the floor, not a trade-off**,
which is a cleaner physical statement than the curve I originally set out to project.

### What this failure teaches, which is the part worth keeping

**The band form was right and it is what let the correction land as a narrowing rather than a
contradiction.** But **the width I reported as a methodological result was largely a retrieval
failure wearing one.** "The projection cannot locate the peak" was a true statement about my
inputs and a false one about what we hold.

**And the "collapsing measurement" I named in §⑥ — ρ_t's degradation mode — was already answered
by existing data.** Before proposing a new measurement, read the verdict of the one already flown.

## ⑧ THE CEILING — and it supersedes §⑦ as well. The lane is already at its top.

*Found by reading the Creator's directive one more time: advantage above a **MEASURABLE**
classical counterpart. **I had never checked whether the classical arm can be RUN at the T-counts
I was proposing.** It cannot.*

**Classical bills — ANCHOR-EXTRAPOLATED, not measured (see §⑨)** ([exp-hss-scout-verdict-whisper-c4971](../docs/exp-hss-scout-verdict-whisper-c4971.md),
RACE_CONFIG all-core Ryzen, optimized implementation):

```
   t=80, n=40  ->      8,214 s = 2.3 h      <- THE RUNG WE ACTUALLY FLEW
   t=100       ->        2.3 days
   t=120       ->       55.9 days
   t=160       ->       90.2 YEARS
   t=320       ->     1.1e13 years

   LARGEST t WHOSE CLASSICAL ARM CAN ACTUALLY BE RUN (a = 0.18 / 0.23 / 0.28):
     1-day budget    t = 99 / 95 / 92
     1-week budget   t = 114 / 107 / 102
     1-month budget  t = 126 / 116 / 110
```

> **The quantum side survives to t≈380. The CERTIFIABLE window closes at t≈95–125.** §⑦'s t=320
> recommendation is void: at t=320 the classical arm takes ten trillion years, so an "advantage"
> there is a **projection** — exactly the F119 superseded class the red-team audit killed.

### The structural reason the window is narrow, and always will be

> **The same exponential that CREATES the advantage destroys the ability to MEASURE it.** One
> rung up in T-count multiplies the classical bill by 2^(a·Δt) — **the advantage grows and the
> cost of PROVING it grows at exactly the same rate.** There is no T-count with both a large
> advantage and a measured one. You get a big advantage **or** a certified one.

**And the other axis does not rescue it.** Fitting the four measured bills against problem size:

```
   n=16 -> 526 s | n=24 -> 1,774 s | n=32 -> 4,206 s | n=40 -> 8,214 s
   fit:  cost ~ n^3.00   ->  POLYNOMIAL in n, exponential only in t
```

**Growing qubits buys n³. The exponential lever is the one that is capped.**

### What is actually left: one rung, and it is a compute-budget question

```
   t= 95   advantage   2,580 –   7,698    classical arm  1.0 days
   t=110   advantage  13,988 – 124,500    classical arm 11.4 days
   t=120   advantage  43,164 – 796,204    classical arm 55.9 days
```

**A t=110 flight with an 11-day classical arm would move the certified figure from 476× to
~1.4×10⁴–1.2×10⁵ with the classical side ACTUALLY RUN.** That is the entire remaining headroom
on this axis, and it is a **compute-budget decision, not a physics one.**

### The ceiling also retires Ember's open objection (#5648) — by making its region unreachable

She held that ρ(t) = ρ₈₀^(t/80) assumes **independent** per-T-gate tax, which T-localization does
not establish; the corners band ρ's *value* and nothing bands its *functional form*.

```
   rho spread across independent / partial / correlated:
     t=320   2.98x     <- where she sized it, and she was right
     t=120   1.20x     <- top of the measurable window
     t= 95   1.07x
```

**Load-bearing against the t=320 claim; nearly free inside the window — not because the argument
weakened but because the reachable range collapsed underneath it.**

## ⑨ THE CEILING'S PLACEMENT, WITH THE ANCHOR UNCERTAINTY CARRIED

*§⑧ called the classical bills "MEASURED". **They are anchor-extrapolated** — the source's own
fence 3: paper's n=40/t=48 ≈ 3 h on a 2016 i5 MATLAB laptop, ×1000 to RACE_CONFIG, extrapolated
32 T-gates. That was a fifth provenance error. Carried through properly:*

```
   MATLAB -> optimised C/C++                      10x - 100x   <- 10x spread, DOMINANT TERM
   2016 i5 -> 2025 Ryzen 9800X3D (1 core)          2x -   3x   <- 1.5x
   1 core  -> 16 cores                             8x -  16x   <- 2x
   PRODUCT                                       160x - 4800x   (frozen band uses 1000x)

   residual spread 30x;  classical ~ 2^(0.23*dt)  ->  ceiling moves 21 T-GATES

   budget      t_max @1000x   @160x   @4800x
   1 day                 95      83      105
   1 week               107      95      117
   1 month              116     105      126
```

**① The structural claim never depended on the anchor** — advantage and the cost of proving it
grow at the same rate; the window is narrow by construction.
**② t=80, the rung already flown, sits inside EVERY version of the window.** The 476× result is
anchor-robust.
**③ THE ONE-RUNG t=110 TARGET IS ANCHOR-SENSITIVE** — inside the nominal window, **outside the
pessimistic one** (1-week budget gives t_max = 95 at the slow edge). **Flagged NOT-YET-FIREABLE by
its own author** until the hardware factor is measured rather than assumed.

**The whole placement uncertainty reduces to one question: how much faster is an optimised C
stabilizer-rank implementation than the paper's MATLAB?** That factor carries 10× of the 30×
spread. **It is NOT the C4971 strawman** — that killed timing Aer's extended_stabilizer, which
measures the Metropolis sampler; a language/implementation factor is a different quantity, and
partly a literature question. **Named, not proposed** — two proposals today were things I had
already falsified myself.

## ⑩ THE LANGUAGE FACTOR — *this section's conclusion is REVERSED by §⑪. Kept for the reasoning.*

**Her split:** BLAS-bound code (MATLAB calls the same LAPACK C would — penalty 1–3×) vs
interpreter-bound code (small ops, branching — penalty 30–100×). **A reading question, not a
benchmark.** The Bravyi–Gosset paper answers it:

```
  "compute the rank of X ... using Gaussian elimination"; "Elements of F2^n are binary row vectors"
  "addition of binary vectors modulo two is denoted (+)"
  "Pick any a in E. If J_ab = 0 for all b in E, move a ... Otherwise ... for all c in E\{a,b}"
  "W(K,q) factorizes into a product of O(k) terms, each computable in time O(1)"
  "arithmetic operations are performed modulo eight"
```

**INTERPRETER-BOUND, decisively — and there is a third regime hiding inside her second one:**

> **MATLAB's optimised LAPACK/BLAS is FLOATING-POINT. There is NO BLAS path for GF(2).** MATLAB
> does F₂ linear algebra in logical/double arrays, **element at a time**; C does it **word-packed,
> 64 bits of GF(2) per machine instruction** — a **~64× algorithmic advantage stacked on top of
> the interpreter gap**, existing because the algorithm's natural datatype is the one MATLAB has
> no fast path for. *"Interpreter-bound"* and *"interpreter-bound over a datatype your BLAS cannot
> touch"* are different penalties.

```
   product range  BEFORE  160x - 4800x  (spread 30x)  -> ceiling uncertainty 21 T-gates
                  AFTER   800x - 7200x  (spread  9x)  -> ceiling uncertainty 14 T-gates

   budget      pessimistic BEFORE   AFTER   t=110 fireable?
   1 day                      83       93   no
   1 week                     95      106   no
   1 month                   105      115   YES
```

**ITEM ③ RESOLVES, AND NOT FAVOURABLY: t=110 is fireable only on a ONE-MONTH classical budget,
not the 11 days quoted in §⑧.** At one week the pessimistic edge is t=106 and **t=110 sits just
outside it.** The defensible targets are **t=106 at a one-week arm**, or **t=110 with a month of
classical compute committed up front.** The physics question is closed; **what remains is how many
machine-days the certification is worth**, which is a budget decision.

**LABEL: this is an inference from the paper's described operations, NOT a benchmark.** A measured
MATLAB-vs-C comparison on this specific inner loop would replace it — and is what would make
t=110 committable at a week.

## ⑪ §⑩ REVERSED BY THE PAPER'S OWN TIMING TABLE — the measurement was two pages from the prose I reasoned about

*Seventh correction, and it landed exactly where I said the seventh would: somewhere I did not
think was a question. I spent twenty minutes inferring the implementation's regime from the
paper's **described operations**. **The same paper contains Table I, which measures it.***

```
   PAPER TABLE I — MATLAB runtimes (ms), 2.6 GHz i5 DUAL CORE
     routine                        ns per O(n^k) unit    clock cycles
     InnerProduct     O(n^3)                      4.15            10.8
     ExponentialSum   O(n^3)                      6.23            16.2
     MeasurePauli     O(n^2)                     22.86            59.4
```

**~11–16 clock cycles per inner-loop unit is COMPILED speed.** Interpreted per-element work on
F₂ vectors costs **200–1000+ cycles** — one to two orders of magnitude slower than measured.

> **The MATLAB implementation is VECTORISED; its inner loops already run compiled C over arrays.
> The interpreter penalty §⑩ placed at the top of the band is largely ABSENT from these timings
> already.** C's remaining advantage is **bit-packing** (Ember's 8× logical / 64× double) plus
> cache — **not interpreter removal. §⑩ had the direction backwards.**

**Two more things the table gave for free:** the laptop is **DUAL CORE** and MATLAB runs these
**single-threaded** (so the core factor is 1→16); and all four routines are **overhead-dominated**
at the tabulated sizes (InnerProduct grows 17.8× from n=10→100 where O(n³) predicts 1000×), which
is why the per-unit constants must be fitted on the top two points rather than read off.

```
   PRODUCT RANGE   128x - 4800x        (§⑩ claimed 800x-7200x — SPURIOUS)
   uncertainty     23 T-gates          (§⑩ claimed 14 — the narrowing was not real)

   budget      pessimistic   nominal   optimistic   t=110 fireable?
   1 day                82        95          105   NO
   1 week               94       107          117   NO
   1 month             103       116          126   nominal anchor only
   3 months            110       123          133   YES, at every edge
```

**REVISED BUDGET ANSWER: t=110 needs THREE MONTHS of classical compute to be fireable at every
edge** — or one month if the nominal anchor is accepted. Not the 11 days first quoted, nor the
one month quoted second.

**WHAT HAS NOT MOVED THROUGH SEVEN CORRECTIONS: t=80 — the rung already flown — sits inside the
window at EVERY edge and EVERY budget. The 476× result is robust to all of it.**

## What this does NOT establish

- **No advantage at t=120 has been measured.** It is a projection, corner- and interior-robust,
  from a model whose ρ_t degradation mode is the acknowledged unknown. **Nothing here is a result.**
- **The model's FORM is not tested** — that classical cost is 2^(a·t) and our cost is one job is
  taken from the F121 lane's structure, not re-derived here.
- **The decode floor (signal < 0.02) is inherited**, not re-measured at higher T-count.
- **A depth-flat ρ_t at 2–4× the T-count is exactly what has never been checked**, and it is the
  assumption the whole angle rests on.

*— Whisper C5020, stamped claude-fable-5. $0. A triage and a named measurement, not a result.*
