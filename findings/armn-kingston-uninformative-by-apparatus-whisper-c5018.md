# Kingston ladder: the frozen branch fired on a BROKEN INSTRUMENT

*Whisper C5018, 2026-08-06. Flight `d9ptuqa42q2c73b8f610` (ibm_kingston), 26 pubs /
144 kshot / ~50 QPU-s of a 156 s pool. Flown on the Creator's "fly the ladder on kingston?"
after a $0 re-decode withdrew the fez closure. Branches (a)–(d) frozen in the manifest before
submission. **Branch (c) fired. I am not carrying it, and the reason is my pre-registration's
fault, not the data's.***

## The result, and why it does not mean what the branch says

```
  shallow_2 (the witness), 15 VALID blocks of 16 flown
    mean u   0.2236        range [0.095, 0.667]        sd 0.1817
  FROZEN GATE (unchanged all campaign):  u >= 0.700
  FROZEN FOLD LINE:                      u <  0.600
```

**Kingston's witness sits at 0.224 against a 0.700 gate — a factor of three below, and well
under the fold line. The instrument does not work on this chip.**

Branch (c) — *"sd ≥ 0.030 → heavy-tailed spread is a real Heron-r2 property; re-file the
closure on this evidence"* — fired on sd = 0.182. **But an sd measured on a witness that
fails its own purity gate by 3× is not a measurement of the arm-N spread. It is a measurement
of a broken apparatus.** The kingston result therefore does **not** inform the fez feasibility
question, and the withdrawal filed earlier (0.7×–2.2×, from fez data) stands untouched.

**Class: UNINFORMATIVE-BY-APPARATUS** — the same class as the first arm-N flight of this
cycle, arriving again at the end of it.

## My error, and it is the seventh of this exact shape

**I froze the branches on the spread and never gated them on the purity gate.** The gate has
existed all campaign. It is the reason DD was turned off, the reason the 9-CZ geometry was
chosen, and the quantity the verdict flight measured in-job. **It was not among the branch
conditions, so a branch could fire on an instrument the campaign's own standard rejects.**

This cycle's running theme has been *checks that cannot fire, or that do not exist where they
are needed*: a cal-vs-cal check with one cal; an interface needing sealed labels; a duration
disclosure carrying only counts; a power guard emitting nothing; a constant verdict function;
a missing readout precondition. **This is the seventh — and unlike the sixth, the check
existed. It simply was not wired into the decision that needed it.**

Corrected form for any future pre-registration: **every outcome branch must carry the
apparatus gate as a precondition, not merely as context.** A branch that can fire on a failed
instrument is not a pre-registration, it is a formula.

## What IS established — and one genuine anomaly, recorded as unexplained

**Gates and readout are fine on kingston.** `shallow_0` (channel removed) = **0.9115**,
against fez's 0.9207. Whatever fails, it is not the gate layer.

**The loss is idle-specific, and roughly 3× worse than fez per idle:**

| | kingston | fez |
|---|---|---|
| shallow_0 (gates+readout) | 0.9115 | 0.9207 |
| shallow_1 (+1 idle) | 0.5670 | 0.8040 |
| shallow_2 (+2 idles) | 0.2236 | 0.6804 |
| **cost per idle** | **0.344** | **0.124** |
| idle : gate ratio | 7.8 : 1 | ~3 : 1 |

**And every obvious explanation is ruled out by measurement, not by argument:**

```
  coherence   kingston T1 244us / T2 146us   vs   fez T1 117us / T2 96us    -> kingston BETTER
  idle time   6.588us (1647dt)               vs   5.952us (1488dt)          -> same dt=4.0ns
  total delay 13.18us = 0.09 of kingston's T2 median                        -> should cost ~10%
  gate count  9 two-qubit gates, identical                                  -> matched
  structure   2 delays, 3294dt, identical across high and low blocks        -> matched
```

**Kingston has better coherence, comparable idle exposure, and identical circuits — and loses
three times as much purity per idle.** That is a real anomaly and I do not have a mechanism
for it.

**The within-chip split is stranger still, and points backwards from the obvious story.** The
15 valid blocks are **bimodal**, not heavy-tailed: two at ~0.666 (q21, q47) and thirteen at
0.095–0.198. If coherence explained it, the high blocks should have the best T2. They have the
**worst**:

```
  q21  u 0.665   block T2 [31.0, 89.1, 151.7, 417.3] us   MIN 31.0   <- worst min T2
  q47  u 0.667   block T2 [103.5, 21.2, 283.6, 338.7] us  MIN 21.2   <- worst min T2
  q65  u 0.143   block T2 [133.3, 122.0, 215.4, 217.6] us MIN 122.0  <- best min T2, low u
```

**Recorded as unexplained.** Inventing a mechanism at this point would be the failure mode
this whole arc has been about — and I have ~106 QPU-s left, at the end of a night whose
lesson was repeatedly that rushed apparatus is where the errors come from.

### FOUR EXPLANATIONS ELIMINATED, ALL AT $0 (Whisper + Ember #5158, from data already on disk)

| eliminated | by what |
|---|---|
| **coherence** | HIGH blocks have the **worst** min T2 (31.0, 21.2 µs); best-T2 block (122 µs) sits at u 0.143 — backwards |
| **correction conditioning** | HIGH mean cond **1.127** vs low **1.082**; low-cluster q45 (1.187) exceeds high-cluster q21 (1.065); zero negative mass throughout |
| **readout quality** | q45 and q47 carry an **identical** worst_readout 0.0889 — the two worst in the set by 3× — and land at u 0.131 vs 0.667 |
| **block symmetry** (anc1=q−1 ∧ anc2=q+1) | both HIGH are symmetric (2/2), but only **2 of 7** symmetric are HIGH; **p = C(7,2)/C(15,2) = 0.20** |

**And the test of the last one produced the result that outranks all four.** With **n = 2** in
the HIGH cluster, the significance ceiling is set by how common the property is:

```
  property held by  4 of 15  ->  P(both HIGH share it) = 0.057
                    6 of 15  ->                          0.143
                    7 of 15  ->                          0.200
                    9 of 15  ->                          0.343
```

**Any property common enough to be interesting is too common to be significant at n = 2.**
So the binding constraint is not *which* explanation — **it is the HIGH count.** The next
flight is therefore **a replication, not a mechanism hunt**: is the split real, and what is
the HIGH rate? At 2/15 ≈ 13 %, thirty blocks buys ~4 HIGH, which is still thin.

**One coincidence logged as a coincidence,** because it is the most seductive pattern here and
is the same shape that just produced two refuted hypotheses:

```
  shallow_1 (ONE idle):   q41 0.671   q67 0.662   q109 0.662
  shallow_2 HIGH pair:    q21 0.665   q47 0.667
  shallow_2 same subset:  q41 0.149   q67 0.163   q109 0.184
```

**q21 and q47 at two idles read exactly like the others at one idle.** The obvious story is
that their second delay is not doing its work — but scheduled delay was verified **identical
(3294 dt)** across high and low blocks, so the mechanism that story requires is absent. Named
a coincidence *in advance*, not after a test kills it.

## Both validity checks earned their place — and the free one was not redundant

| check | cost | what it did |
|---|---|---|
| **range check** (decode-time, Ember #5148) | **free** | flagged **q87 INVALID** — corrected u 0.823 with **−0.063 negative mass** |
| **readout bar 5%** (build-time, precondition 5) | **costs blocks** | screened **13 of 156** kingston qubits, worst **0.499** — a coin flip |
| cond-ceiling (secondary) | free | flagged nothing the range check did not |

**q87 is the proof the free check is not redundant with the costly one:** it passed the
build-time readout bar and still produced an impossible correction. **A readout bar screens
inputs; only the range check catches an invalid output.** And 13 failing qubits on kingston
confirms that fez's q72 was not bad luck — **bad-readout qubits are an unscreened population
on Heron-r2 that four preconditions never looked at.**

## What this changes

- **Kingston is not a drop-in substitute for fez for this witness.** Anyone reading "same
  Heron-r2, 156 qubits, better coherence" and expecting transfer would be wrong by 3×.
- **The fez feasibility question is still open at 0.7×–2.2×.** Kingston did not answer it and
  cannot, because its instrument fails the gate.
- **The idle anomaly is a cheap, well-posed follow-up** — a delay sweep on kingston at
  matched physical durations would localise whether the loss is really in the idle or in
  something the idle merely reveals. That is a next-session flight with a fresh
  pre-registration that carries the purity gate as a branch precondition.

*— Whisper C5018, stamped claude-fable-5. The frozen branch fired exactly as written, which
is how I found out the branches were written wrong.*
