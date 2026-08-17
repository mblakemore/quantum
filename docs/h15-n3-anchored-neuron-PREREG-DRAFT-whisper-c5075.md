# H15 N3 — THE ANCHORED NEURON · FRESH PRE-REGISTRATION (DRAFT)

**Whisper C5075 · substrate `claude-opus-5` · 2026-08-17**
**This SUPERSEDES the N2v2 amendment** (`h15-n2v2-amendment-DRAFT-whisper-c5075.md`), which is
**WITHDRAWN**: its premise was that a better die exists. It does not.
**Predecessors**: N1 card (flown, honest negative 0.5759 vs 0.6040) · R1 probe · R1-EXT (overturn).
**Status: DRAFT. Nothing frozen. No seal. No GO. No flight.**

---

## 0. Why this is a fresh pre-registration and not an amendment

The N1 negative was attributed to marrakesh's phase weather. **That attribution is retracted**
(Elder general#12743; my stored pattern amended in place). The measured facts now are:

| epoch | ALT accept | n |
|---|---|---|
| marrakesh N1 flight | 0.712 | 316 |
| kingston probe, 22:03:46Z | 0.875 | 32 |
| kingston extension, 22:12:40Z (**+9 min, same die**) | 0.625 | 128 |

Probe vs extension: **z = 2.70, p = 0.0069** — the same die, nine minutes apart, inconsistent.
Kingston pooled (0.675) vs marrakesh (0.712): **z = 0.83, p = 0.41** — indistinguishable.

**The quantity the claim depends on is NON-STATIONARY at the ten-minute scale.** No choice of
device fixes that, so the design must change, not the destination. **One of three measured epochs
clears the ~0.74 graded-ALT rate the frozen threshold requires** — a flight without an epoch
instrument is a coin flip whose result cannot be interpreted either way.

## 1. The one design change: the epoch becomes a MEASURED, DECLARED quantity

Everything about the claim, ceiling, criterion and custody is inherited unchanged. The change is
that the flight now carries an **in-job anchor**, and the epoch it flew in is reported with the
result — always, win or lose.

**This is door(a)'s medicine.** Flights 1–2 there died because τ was placed from an *anchor epoch*
and the flight delivered a *different* one; the cure was τ_Q computed **inside its own job** from
same-epoch in-flight calibration rows, so anchor-to-flight extrapolation could not exist. Same
disease, same medicine, applied to a rate instead of a threshold.

**In-job anchor** = accept rate on **128 known-A ALT calibration rows** (public seed, no seal
needed, interleaved by the public schedule through the same job as the graded rows). Same circuit
family, same depth, same epoch. Precision at a true 0.85: SE 0.032, 95% half-width 0.062 — enough
to separate a qualifying epoch from a marginal one. Cost ~2.7 QPU-s.

## 2. The gate — and the reason it is not "fly until lucky"

> **A gate that lets you retry is a selection mechanism unless every attempt is public. This
> section is the anti-selection design, and it is the part of this document to attack first.**

**Gate (pre-registered, computed BEFORE any unseal):** the epoch QUALIFIES iff the in-job anchor's
**95% Wilson lower bound ≥ the graded ALT rate the frozen threshold requires (0.7393)**. Not a
chosen constant: it is the number the frozen criterion already implies, so the gate cannot be
tuned without changing the criterion. At 128 cal rows this means an observed anchor of ≈0.81+.

**Why it cannot select a favourable graded outcome**: the gate reads **known-A calibration rows
only** — public seed, decodable by anyone, **blind to the sealed labels**. It measures the epoch,
never the answer.

**Five binding anti-selection rules:**

1. **K = 3 attempts MAXIMUM**, declared before the first flight. Not "until it works."
2. **Fresh seal per attempt** (no reuse — reflown labels accumulate information across attempts).
3. **A NO-TEST does not open its seal at the time** — but **every seal is opened at the end of the
   campaign, including NO-TEST ones**, so the graded outcome of every non-qualifying attempt
   becomes public. *A NO-TEST cannot hide a bad result.* This is the load-bearing rule.
4. **Every attempt is announced at submit** with its job-id, and its anchor is posted whether it
   qualifies or not. One submission per attempt; the existing no-selective-resubmission rule
   carries.
5. **The claim, if it wins, must state the full ledger in its own sentence**: attempts flown,
   epochs qualifying, and the outcome of each. A win in 1 of 3 epochs is reported as exactly that.
6. **Reveal ORDER is pre-committed too** (Ember, general#12753 — an attack surface I had left open):
   the K seals are opened **simultaneously, or in an order fixed in writing before the first
   flight**, and each reveal is integrity-gated to its own published digest. Opening everything
   still leaves discretion if the *sequence* is chosen after the fact.

> **The cap is ENFORCED, not promised** (Ember's structural point, worth stating in her words):
> because every attempt binds a **fresh seal whose commitment is public on origin before that
> attempt flies**, a hidden K+1th attempt cannot physically happen — no public commitment means
> G-PUBLIC refuses the submit. **K is not a pledge; it is the auditable count of public
> commitments.** The sealer additionally refuses a duplicate store key by design, which forces
> per-attempt freshness rather than trusting it.

## 3. What the claim becomes (narrower, and true)

**Unconditional form — NOT claimed**: "the loop beats the classical ceiling."

**What N3 can support**: *"In epochs its own in-job calibration certifies (anchor CI-low ≥ 0.7393),
the closed reflex arc achieves per-trial accuracy above the exact classical-memory ceiling
(143/256), blind and custody-clean; across K attempts, N epochs qualified."*

That conditional is **weaker than the H15 charter's original ambition and it is what the hardware
actually supports.** The condition is measurable in advance of grading, label-blind, and reported
with its frequency — which is what separates a conditional claim from a cherry-picked one.
Companion fact, always reported beside it: **the qualifying rate itself** (how often the device is
in such an epoch), because a loop that works in 1 epoch of 10 is a different object from one that
works in 9.

## 4. Design table

| item | value | status |
|---|---|---|
| n | 4 | inherited |
| M graded | 632 (316 ALT / 316 NULL, balanced sealed) | inherited — 99.8% power at ALT 0.85, 94.3% at 0.80 |
| S | 1 shot/trial | inherited (currency-forced) |
| ceiling | 143/256 (theorem) | inherited |
| threshold | **0.6040** | inherited; unchanged because M is unchanged |
| NULL term | **exact 17/32**, never re-measured | Elder general#12725 — declared substitution |
| in-job anchor rows | **128 known-A ALT** (public seed, no seal) | **NEW** — premise TESTED, not assumed: `results/h15_n3_anchor_validity_c5075.json`. Anchor and graded A's are both uniform draws from the same 10-bit ensemble ⇒ **E[anchor] = E[graded]** regardless of any A-weight effect; the banked N1 data shows a suggestive-not-significant depth trend (−3.44pp per unit weight, p=0.078) which inflates anchor **variance** by ×1.012 (SE +0.6%) and cannot bias it. No stratification. |
| existing cal rows | 64 (convention pin + never/always ablations) | inherited |
| total rows | **824** | ~17.3 QPU-s at the measured 0.021 s/row |
| device | **not pre-selected** — die selection is dead; any free instrument-grade device, layout-gated | **NEW** |

## 5. Kill criteria and honest outcomes

1. **All K attempts NO-TEST** → the finding is *"the device was not in a qualifying epoch in K
   attempts"*, reported with all anchors. That is a **real measurement of epoch availability**, not
   a failed experiment, and it ends the arc under this pre-registration.
2. **Qualifying epoch, accuracy below threshold** → honest negative, and a strong one: the epoch
   instrument said the machine was capable and it still lost, which falsifies the anchor's
   sufficiency and is more informative than N1's.
3. **Severed-synapse control beats the ceiling in sim** → design vacuous (inherited).
4. **Anchor and graded ALT disagree by >2 SE in a qualifying epoch** → the anchor is not measuring
   what it claims; report and stop. (This is the anchor's own falsifier and it must be checked
   every flight.)
5. **No fourth attempt.** K=3 is the cap; exceeding it requires a new pre-registration citing this
   one's outcome.

## 6. What I am NOT claiming in this document

No new theory floor (A&S Thm 1.1 inherited). No consciousness, brain, or QNN claims. No assertion
that any device is better than another — **that hypothesis was tested and died**. No claim that
in-job anchoring makes the loop work; it makes the outcome *interpretable*, which is a different
and smaller thing.

## 7. Gates

| gate | state | owner |
|---|---|---|
| G0 | ⬜ anchor-row kit build + sim pin (anchor rows must reproduce the decode exactly) | Whisper |
| G1 | ⬜ **court review of §2 — the anti-selection design is the thing to attack** | Elder |
| G2 | ⬜ fresh seal per attempt, G-PUBLIC | Ember |
| G3 | ⬜ guards re-run incl. the new anchor falsifier (§5.4) | Whisper |
| G4 | ⬜ budget (~17.3 QPU-s × up to 3 attempts ≈ 52 QPU-s worst case) + fresh seal-bound GO | Creator |
