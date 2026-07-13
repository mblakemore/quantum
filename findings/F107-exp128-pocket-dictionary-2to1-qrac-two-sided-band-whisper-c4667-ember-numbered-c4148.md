# F107 — Exp128 "The Pocket Dictionary": the 2→1 quantum random access code — two bits in one qubit, either retrievable — certified INSIDE the two-sided band (110.5σ above the classical law, 5.2σ below the quantum optimum)

**Finding**: F107 (assigned Ember C4148 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4667, under the frozen rule. Horizons-3.
F107 verified unused — F106 was the highest prior.)
**Experiment**: Exp128 (ibm_marrakesh, job `d9al7om6hjac73fejisg`, **qubit 75, zero two-qubit
gates**, 10 pubs, 200k shots — the **first zero-2q-gate *advantage* flight** of the campaign,
where F102 was zero-2q but a law-match not a bound-beat).
**Pre-registration**: `experiments/exp128-qrac-preregistration.md` (FROZEN; the classical bound
enumerated in-code; a **two-sided** gate — above the classical law, at-or-below the quantum law).

## Plain English — two bits in one qubit, read either on demand

A **quantum random access code** is a pocket dictionary: you pack **two classical bits into a
single qubit**, and later — *without knowing in advance which one you'll be asked for* — you can
pull out **either** bit. Classically that's impossible to do well: one classical bit forced to
answer for two can be right at most **75%** of the time (averaged over the four two-bit messages
and which bit is queried). A qubit does better — up to **cos²(π/8) ≈ 85.36%** — because a qubit's
state lives on a sphere and two bits can be encoded as directions that a single measurement
partially resolves. On this chip it hit **84.9%** — comfortably above the classical 75% and, as it
must be, just below the quantum ceiling. The elegant part of the test: the measurement had to land
**inside a band** — beating the classical law is the win, but *exceeding the quantum law would be a
red flag* (physically impossible, so it would mean an apparatus error), and it didn't.

## One-line result — QRAC-ADVANTAGE-CERTIFIED, all five gates PASS

Pooled success **0.84893 ± 0.00090** — **110.5σ above the enumerated classical ceiling 0.75** and
**5.2σ below the quantum optimum cos²(π/8) = 0.8536** (procedure-theory residual 0.0046). It lands
*inside* the two-sided band (0.75, 0.8536]. Two bits stored in one qubit, either readable on demand,
on real silicon.

## The grade — a two-sided band, not a one-sided floor

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1 (QRAC) | pooled > 0.75 + 5·SE | 0.84893 (110.5σ over classical) | **WIN** |
| W2 (min-case) | worst case > 0.75 + 5·SE | 0.84325 (36.3σ over classical) | **WIN** |
| **G_QBAND** | pooled ≤ 0.8536 + 5·SE (a value *above* the quantum law = apparatus error) | 5.2σ below the optimum | **PASS** (in-band, NO-TEST avoided) |
| G_class | executed optimal-classical arm ≤ its own 0.75 law | 0.74818 | **PASS** |
| G_sent | sentinels ≥ 0.95 | 0.998 / 0.995 | **PASS** |

Predictions 0.95 / 0.90 both **HIT**. The **G_QBAND** gate is the design's signature: rather than
just "beat the floor," it certifies the result sits in the *physically allowed* window — exceeding
the quantum optimum would be graded a NO-TEST (error), not a triumph. Certifying you are *inside*
the quantum regime, not merely above the classical one, is a stronger form of honesty.

## The underrated number (method subclaim): both laws honored on the same chip, only the quantum player crosses the line

The **executed optimal-classical arm** — a real hardware run of the best one-bit strategy — scored
**0.74818, parked 0.2pp *under* its own exact 0.75 law**. So on the same chip, in the same window,
the classical player sits at (just below) the classical ceiling and the quantum player sits at
(just below) the quantum ceiling — **both laws measured, only quantum crosses the classical line**.
That is the adversarial control the whole claim rests on, executed rather than assumed. The
classical bound itself is **enumerated in-artifact over all 256 strategy pairs** (= 0.75 exactly),
the Exp126/F106 house style now standard.

## Atlas calibration datapoint (method subclaim)

The FakeMarrakesh noise model was **pessimistic by 0.4pp here** (predicted 0.845 vs measured 0.849)
versus **optimistic by 0.9pp at Exp126's depth** — so **the noise-model optimism crossover sits
between 0 and ~2 CZ**: shallow enough, the model *under*-predicts. A useful new anchor for the
depth-decay/model-error atlas at the zero-gate end.

## What this does and does not show (scope, stated first in the prereg)

A **communication-primitive** quantum advantage (random-access storage), not a computational-speedup
claim. The 2→1 QRAC is **textbook** (Ambainis–Nayak–Ta-Shma–Vazirani; demonstrations exist on
multiple platforms); the contribution is the **pre-registered, enumerated-bound, two-sided-band,
classical-arm-executed gate-model certification**, and the first zero-two-qubit-gate advantage flight.
Device-characterized; the claim is that the measured success exceeds what *any* single classical bit
can deliver (enumerated), while respecting the quantum law.

## Lineage and reuse — the comms column is now a ladder

- **Arc**: communication primitives — with F107 the comms column spans three capabilities, each a
  provable-bound beat: **F87 superdense coding (341σ)** — assisted capacity; **F106 magic-square
  game (196σ)** — nonlocal games / contextuality; **F107 QRAC (110.5σ)** — random-access storage.
- **Method reuse**: the **two-sided band** gate (certify inside the physical regime; exceeding the
  quantum law = NO-TEST, not a win — a template for any protocol with both a classical floor *and*
  a quantum ceiling); enumerate-the-bound-in-artifact (F106 house style); executed optimal-classical
  arm as the same-window control; the zero-2q-gate advantage as the atlas's shallow-end anchor.
- **Status-ledger claim type**: **existence** (2→1 QRAC advantage, in-band). Figures of merit:
  **0.84893 / 110.5σ** over the classical law and the **0.0046** procedure-theory residual; the
  **executed-classical-arm-at-its-own-law** and the **fake-pessimism crossover** are reported method
  subclaims. HW tier; single run; UNTESTED.
