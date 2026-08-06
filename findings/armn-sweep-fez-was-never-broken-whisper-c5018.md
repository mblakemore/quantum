# The witness fix: fez was never broken, and the kingston bimodality does not exist

*Whisper C5018, 2026-08-06. Matched delay sweep, `d9pu5s97s9kc73auhnu0` (ibm_kingston, 42 pubs)
+ `d9pu5sh7s9kc73auhnug` (ibm_fez, 22 pubs), 87 QPU-s of a 119 s pool. Flown on the Creator's
"fix the witness / anything else we can do at the same time?" as step (1) of the forced
ordering. **Identical absolute D grid on both chips (dt = 4.0 ns on each), so equal D is equal
physical time.** Branches frozen in the manifests, every one gated on the apparatus.*

## ① Step 1 answered — and the answer relocates the whole program

```
  LARGEST D CLEARING u >= 0.700 (mean), WITH THE 95% CI THE FIRST VERSION OMITTED
    fez       1647 dt (6.59us)   mean 0.7596  n=4  CI [0.7243, 0.7950]  CLEARS — lower CB above gate
    kingston   412 dt (1.65us)   mean 0.7437  n=7  CI [0.6685, 0.8190]  MEAN clears, LOWER CB BELOW GATE
```

**⚠️ SELF-CAUGHT, and it weakens the kingston half of my own headline.** I first published
*"largest D clearing u ≥ 0.700: kingston 412 dt, fez 1647 dt"* from the **means alone**.
A gate is an apparatus criterion; applying it to a mean without a confidence bound is the same
species of error as the three withdrawn earlier tonight.

**kingston at D=412 is NOT established as clearing** — CI [0.6685, 0.8190] straddles the gate,
and one block (q109, 0.622) is below it outright. kingston's sd there is **0.0814** against
fez's **0.0267** at the same D, so kingston remains markedly unstable even where its mean
passes. **Branch (b) is downgraded from "FIXED at reduced exposure" to "mean clears at 412 dt;
not established at 95 %".**

**fez holds at every D on the grid, including the largest**, with the lower bound at 0.724
above the 0.700 gate. The load-bearing claim survives the check; the incidental one does not.

**fez clears the gate at the largest D on the grid, lower confidence bound included. fez was
never broken.** Its curve stays
between 0.76 and 0.94 across the entire sweep, and the D=1647 value reproduces the DD-off
measurement from the DD sweep (0.7218 at D=1488) with the expected small shift.

So the instrument we needed does not have to be built — **it already exists on fez**, and the
job of step (1) turns out to be *choosing the host*, not repairing the witness.

## ② THE BIMODALITY DOES NOT REPRODUCE — and that ends steps 2 and 3

The kingston ladder found two blocks at ~0.666 against thirteen at 0.095–0.198, and the plan
was 30–45 blocks to make any mechanism testable. **The same blocks, re-flown:**

```
  earlier (kingston ladder, D=1647):   q21 0.665, q47 0.667  = the HIGH pair of 15

  this sweep, D= 824:  q151 0.788  q109 0.774 | q105 0.385  q41 0.349  q21 0.348  q47 0.335  q67 0.218
                       q21 rank 5/7      q47 rank 6/7
  this sweep, D=1647:  q21 0.611  q105 0.580  q41 0.576 | q151 0.262  q67 0.249  q47 0.170  q109 0.146
                       q21 rank 1/7      q47 rank 6/7
```

**The membership completely reshuffles.** q47 — half of the original HIGH pair — is **6th of 7
at both** new D values, and lands at **0.170**, the second-lowest. The blocks that are high at
D=824 (q151, q109) are the two **lowest** at D=1647.

**There is no stable subgroup. The split was instability at a D where kingston's instrument had
already failed its own gate, not structure.** The third pre-registered tertiary branch fired —
*"tracks others = the original split was noise"* — and it fired harder than written, because
the identity did not merely blur, it inverted.

**Steps (2) and (3) are moot. The 30–45 block replication and every mechanism hypothesis
behind it are cancelled** — there is no phenomenon to replicate. Four mechanisms were
eliminated at $0 last night; the fifth act was to discover there was nothing to explain.

## ③ The anomaly is D-DEPENDENT, not a chip property — this is what the control bought

The claim entering tonight was *"kingston loses 3× the purity per idle"*, measured at
kingston D=1647 against fez D=1488. **At matched D:**

| D (dt) | D (µs) | kingston | fez | k loss | f loss | **ratio** | both clear the gate? |
|---|---|---|---|---|---|---|---|
| 206 | 0.82 | 0.8708 | 0.8974 | 0.0343 | 0.0380 | **0.90** | **yes** |
| 412 | 1.65 | 0.7437 | 0.8736 | 0.1614 | 0.0617 | **2.61** | **yes** |
| 824 | 3.30 | 0.4569 | 0.8792 | 0.4482 | 0.0561 | 7.98 | fez only |
| 1647 | 6.59 | 0.3706 | 0.7596 | 0.5345 | 0.1757 | 3.04 | fez only |

**At D = 206 kingston is not worse than fez — it is marginally better (0.90).** The divergence
appears with D and grows. **There is no flat "kingston is 3× worse" fact.** The 3× was measured
at a D where kingston's witness had already fallen to 0.22, i.e. where the instrument was not
reporting physics at all.

**Only the top two rows may be carried** — both chips clear their own gate there — and across
those the ratio spans **0.90 to 2.61**, which is not a stable constant. The bottom two rows are
reported, not carried; the apparatus gate binds the *claim*, not merely the branch.

**Without the matched fez arm this would have been filed as a chip property.** The rider cost
26 QPU-s and overturned the headline it was flown to check.

## ④ Functional form: kingston is SATURATING, not super-exponential

The three-point ladder suggested kingston lost purity *faster* than multiplicative decay
predicts. Five points say otherwise:

```
  kingston  u0 0.9051   loss/D per 1000dt:  0.167  0.392  0.544  0.325   <- RISES THEN FALLS
  fez       u0 0.9353   loss/D per 1000dt:  0.184  0.150  0.068  0.107   <- flat, ~5x smaller
```

**Loss per unit D peaks near D≈824 and falls by D=1647** — the signature of a curve
**approaching a floor**, not of runaway decay. Kingston's u = 0.371 at the longest D is heading
toward the maximally-mixed value (~0.25 for the two-qubit reduced state this witness reads),
so the apparent "worse than exponential" in the ladder was **saturation seen through three
points**. Neither chip is linear or multiplicative; fez simply never gets far enough down the
curve to show it.

## ⑤ Arm-N feasibility on fez — three independent spread estimates now, and both terms moved

### ⚠️ CORRECTED — the "both land on 2.2×" was a DENOMINATOR ARTIFACT (Ember #5179)

**As I first reported it, the two rows I called convergent used different denominators:**

```
  contrast, q72-free (n=7)   sd 0.0068 ->   6 blocks vs  9 available = 0.7x
  ladder shallow_2  (n=6)    sd 0.0120 ->  20 blocks vs  9 available = 2.2x   <- 20/9
  sweep D=1647      (n=4)    sd 0.0222 ->  69 blocks vs 32 available = 2.2x   <- 69/32
```

**20/9 = 2.22 and 69/32 = 2.16 is the same ratio from a different numerator AND a different
denominator — a coincidence of arithmetic, not a convergence of measurement.** And the
agreement *was* the evidence: what made 2.2× look trustworthy was two independent jobs, with
different blocks and different n, landing on it. That support evaporates.

**The same three estimates against one denominator:**

```
  vs  9 blocks:   0.67x    2.22x    7.67x
  vs 32 blocks:   0.19x    0.62x    2.16x

  required-block counts: 6, 20, 69   ->   an 11.5x spread
```

**THE HONEST STATEMENT: 6–69 blocks needed against 32 available — feasible on the low
estimate, roughly 2× short on the high one.** Each sd comes from n = 4, 6, 7 and carries
~30–40 % uncertainty of its own *before* any of them is compared to another. What is
established is directional: **arm-N on fez sits somewhere between comfortably feasible and a
few-fold problem** — which is still the difference between an arm that is closed and an arm
that needs a modest design change.

**What survives the correction:** the denominator genuinely moved. Precondition 5 admits
**32** qualifying fez blocks against the **9** the withdrawn closure assumed — a real 3.5×
improvement. It simply has to be applied to **all** rows or none.

**How I got it wrong, because the mechanism is instructive:** I wrote *"both terms changed and
they moved in opposite directions, which is why the ratio is stable while its inputs are
not."* That sentence **notices** the denominators differ and then treats the resulting
stability as meaningful rather than as the artifact it is. I rationalised a coincidence
instead of flagging it — the same class as everything else this cycle, arriving in the
paragraph written to explain it.

## ⑥ Method notes

- **q87 was INVALID at all five D values, including D = 0.** The free range check caught it
  5/5 — a persistently broken block that the build-time readout bar admitted. Second clean
  instance of the free check catching what the costly one cannot.
- **The dry run caught the control reproducing its own confound.** The first grid used
  fractions of each chip's *own* D0 (1647 vs 1488) and would have flown the exact mismatch the
  fez arm exists to remove. A control that inherits the confound it controls for is not a
  control.
- **Step (2) was deliberately kept out of this job** because it depended on this job's outcome
  — and that discipline is what let the outcome cancel it rather than half-fund it.

*— Whisper C5018, stamped claude-fable-5. The rider overturned the headline, and the
phenomenon we were about to spend 45 blocks explaining turned out not to exist.*
