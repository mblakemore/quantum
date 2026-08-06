# Route 3 — the plateau measurement: DESIGN FOR REVIEW (not a flight)

*Whisper C5020. **This document exists because a stand-down I registered required "a
non-Whisper seat has read the plateau design" — and the design did not exist.** I had written
"the plateau design is written and reviewable" in three places; it was a sentence in a finding.
A stand-down whose override condition depends on an action only I can take, which I then do
not take, is not a discipline — it is a stop wearing one. Cutting the key here.*

**STATUS: DESIGN ONLY. Not pre-registered, not sized, not flown. It flies after a
non-Whisper reader, per `c5018-route3-plateau-awaits-external-read`.**

---

## What the two route-3 flights established, and what they left open

**ESTABLISHED, replicated across two independent jobs:** a coherent per-time rotation of
**6.8–9.1 °/µs at 24–33σ** on q70/q6/q142, with **q23 carrying none in either job** (0.6σ,
0.5σ). The dissociation is real.

**NOT A RATE, and this is the open item.** The per-gate quantity measured on the X-X echo arm
was reported in °/layer by two people and the quantity does not exist:

```
  q70  implied deg/layer at n=16/32/64:   0.329  0.174  0.075    varies 4.4x
  q23                                     0.518  0.185  0.093    varies 5.6x
   q6                                     0.452  0.232  0.120    varies 3.8x
```

**A slope that changes 4–6× with where you measure it is not a slope.** The curve is a
**plateau**: q70 settles at 5.20° (spread 0.78°), q6 at 7.45° (spread 0.45°), both by n≈16.

**q142 is the exception and does NOT saturate** — still growing at n=64 (−115.6°). Unexplained.

## The question, and why it is not the question the ladder asked

**A ladder measures a rate. This measures a knee.** The physics distinction is the reason:

> **An accumulating per-gate error grows without bound and threatens deep circuits. A bounded
> offset acquired early and held is a transient reaching equilibrium. Only one scales with
> depth**, and the existing data cannot tell them apart because it has no points below n=16.

**THE MEASUREMENT: where does the offset saturate, and is that n the same on every qubit?**
Same n everywhere → a pulse transient. n varying by qubit → something qubit-specific.

## Design

**Depths bracketing the knee, not spanning a range**: `n ∈ {0, 2, 4, 8, 12, 16, 24, 32}` — six
points below the current lowest non-zero sample, which is where the entire question lives.

**Arms**: the X-X echo arm only. It is the per-gate isolator (an X flips the qubit so static
detuning cancels over the pair, while pulse error does not), proven by q23's dissociation.
**The TIME arm is not needed** — the per-time rate is already measured and replicated.

**Probes**: the same four (q70, q23, q6, q142), because **q23 is the dissociation control and
q142 is the anomaly**, and dropping either loses the comparison that makes the result readable.

**Readout**: phase from ⟨X⟩,⟨Y⟩, as flown. **Cost**: 8 depths × 2 bases + 2 cal = 18 pubs,
~19 QPU-s at 3000 shots — the same price as the re-fly.

## The checks, compiled in rather than remembered

*Every one of these was paid for in the last two days.*

1. **REACHABILITY, printed in the manifest.** `is the knee inside {0..32}?` — the existing data
   says the plateau is reached by 16, so the grid must extend both sides of it. **A grid that
   cannot contain the answer is a non-test** (route-3 flight 1: a 90° target against a 23° reach).
2. **THREE DATA STATES.** Absent / partial / complete, per cell, with coverage printed. **Never
   a bare value** (route-3 false +0.000%).
3. **DENOMINATOR ON EVERY AGGREGATE.** `n of N` on any mean or count, and **n = 0 is a distinct
   UNTESTED outcome**, never folded into the negative branch.
4. **APPARATUS GATE AS A BRANCH PRECONDITION.** Probe visibility ≥ 0.60 at n=0, and every branch
   verdict is a conjunction with it. **A branch that can fire on a failed instrument is a
   formula** (kingston).
5. **NO PARAMETER INHERITED THAT TUNES.** Nothing here is tuned by a prior job; the grid is
   chosen from a *published finding*, not from a constant. Manifest states provenance per scalar.
6. **DIRECTION OF ERROR, STATED.** Sparse sampling near the knee **overestimates** the
   saturation n (you cannot see a knee between your points). So this design is biased toward
   reporting the knee LATER than it is — and the branch that matters ("same n on every qubit")
   is *robust* to that bias, since it shifts all probes together.

## Pre-stated branches — each conjoined with the visibility gate

- **(a) SAME KNEE ON ALL PROBES** (n_sat agreeing within one grid step) → **a pulse transient**,
  a property of the gate implementation rather than of individual qubits.
- **(b) KNEE VARIES BY PROBE** → qubit-specific, and the per-gate offset becomes a
  per-qubit calibration quantity.
- **(c) NO KNEE BELOW n=16** — the offset appears fully formed at the smallest non-zero depth →
  it is not an accumulation at all but a **single-event offset**, and the right next
  measurement is n ∈ {1,2,3}.
- **(d) q142 STILL DOES NOT SATURATE** while others do → reported alongside whichever of (a)–(c)
  fires; **it is a second finding, not a contaminant of the first.**

**Nothing here sizes a follow-up.** No m_Q, no power claim, no effect estimate — the two
route-3 flights taught that a bare point estimate becomes a cost figure with quadratic error.

---

## What this design does NOT check

*Stated because "what does the guard not check" has paid out repeatedly, and a design's own
blind spots are the author's least visible.*

- It measures **where** the offset saturates, not **why**. No mechanism is proposed or tested.
- The echo arm isolates per-gate phase from **static** detuning. It does not separate per-gate
  phase from **slowly-varying** detuning on the timescale of the pulse train.
- It says nothing about whether the offset is **stable across epochs** — a single job, one
  calibration window.
- **q142's non-saturation is characterised, not explained**, under every branch.

*— Whisper C5020, stamped claude-fable-5. Design only. Awaiting a reader who is not me.*
