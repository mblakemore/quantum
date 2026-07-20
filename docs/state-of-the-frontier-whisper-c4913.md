# State of the Frontier: what we can make, the next stairs, the honest unknowns

**Whisper C4913, 2026-07-20. Substrate `claude-opus-4-8`.** Written on the Creator's question:
"we know the results are real when we can build on them — what are we now able to make? where is the
next wild Star Trek stair to climb? what do we still not understand that would be valuable to know?"
A synthesis across ~70 certified flights, grounded in specific experiments, honest about what is
real vs aspirational.

---

## I. WHAT WE CAN NOW MAKE (each grounded in a certified result)

Not "what we demonstrated" — what the demonstrations let us *build*.

### 1. A distributed, error-corrected quantum network node — the Federation Computer
This is the biggest one, and it's a *stack*, not a demo:
- **share** entanglement across shielded nodes (Bell pairs, GHZ across 3 shields — 197, 219);
- **compute** across the cut, error-detected: distributed CNOT (217), CZ / cluster bond (221),
  a genuine algorithm (distributed Deutsch, 220), the BGK HLF (222);
- in **both computational models** — gate-based *and* measurement-based (MBQC, 226);
- **route** coherently and error-detected — fault-tolerant indefinite topology (225);
- welded by **classical bits + a software Pauli frame** (no feed-forward — and 218 showed the
  software weld *beats* live feed-forward on today's hardware).
**Makeable now:** a small multi-node error-detected quantum-network testbed that runs a distributed
program end to end. Every layer is certified; what's missing is the *integration*, not a new idea.

### 2. A self-characterizing chip
P5 (211/216): the [[4,2,2]] code's coherent-error transfer function is one geometric rule (blind to
axes orthogonal to the readout basis). **Makeable:** a chip that reports its own coherent-noise
structure *through* its error-correcting code — noise metrology as a free byproduct of running the
shields, with no separate calibration experiment.

### 3. An energy-by-information primitive (quantum energy teleportation)
P3 (227): one classical bit teleports energy (W → 1−κ²) into a bath that is locally passive —
maximally so at full record, where the bath is useless to any local operation. **Makeable:** a
protocol that delivers extractable energy to a remote site using only a measurement + a classical
message, exploiting a pre-shared correlation. The energy ledger and the information ledger are the
same dial (κ = cos(θ/2)) — so *information IS an energy resource*, quantified.

### 4. Fault-tolerant exotic resources nobody else has protected
- **Fault-tolerant indefinite causal order** (P1/208) — the quantum switch behind the shield.
- **Fault-tolerant indefinite topology** (225) — a superposed network route behind the shield,
  provably distinct from any classical mixture of routes even under error detection.
These are *resources* (channel-discrimination, routing coherence) made robust — the difference
between a physics demo and an engineering primitive.

### 5. A physics-enforced privacy/objectivity control (partial)
P4 (223) is quantitatively a not-held (raw-hardware haircut), but the *shape* is real: objectivity
is a dialable quantity, private→public with copy strength, and it accumulates with observers.
**Makeable (with shielded fragments):** a "need-to-know" control where a fact is objective to some
observers and private to others — physics-enforced, not policy-enforced.

---

## II. THE NEXT WILD STAIRS (ranked by payoff × reachability)

### Stair 1 — THE CROSSOVER (the make-or-break stair)
The fault-tolerance thesis is that error-corrected beats bare, and *more* with depth (shield
advantage grew 191 +0.07 → 197 +0.24). But the distributed HLF at n=4 (222) had logical *below*
bare — the distribution overhead outran the shield. **Where is the crossover?** Find the depth/size
where error-corrected distributed computation genuinely beats bare, on this hardware. If it exists
and we hit it, everything above becomes *useful*, not just *possible*. This is the single most
important thing to climb.

### Stair 2 — UNIVERSAL distributed fault-tolerant computation
We have the full Clifford group + the HLF, distributed and error-corrected. The missing piece is
one **non-Clifford** gate (a T / magic state) delivered distributed and error-corrected → arbitrary
distributed quantum algorithms behind the shield. This needs magic-state injection composed with
the distributed machinery. A genuine "universal distributed quantum computer" stair.

### Stair 3 — THE Ȳ-READOUT, and what it unlocks
The [[4,2,2]] single-qubit logical-Y measurement is the recurring wall (it blocked universal MBQC
continuous-angle gates *and* the contextuality game). Exp228 showed the wall is dodgeable for
2-qubit Y *products* (YYYY stabilizer + Bell measurements). Cracking single-qubit Ȳ properly (state
injection / code deformation) unlocks (a) **universal measurement-based computation** across the
network and (b) **contextuality as certified fuel** (P7 done right, the shielded pseudo-telepathy
game — the one un-composed advantage in the whole campaign).

### Stair 4 — A network protocol with a real advantage
Compose the certified network into something with utility: **distributed entanglement-enhanced
sensing** (a GHZ across nodes beats independent sensors at estimating a global field — and behind
the shield), or **quantum secret sharing / anonymous transmission**, error-corrected. This turns
"the network entangles" into "the network *does a useful task better than classical*."

### Stair 5 — Compose the crown jewels
- **ICO-powered distributed computation**: use indefinite causal order (a certified resource) as
  the engine of a distributed algorithm — channel-discrimination or capacity activation, behind the
  shield, across the cut.
- **Fault-tolerant thermodynamics**: run the P3 energy dial *behind the shield* — is the arrow of
  time itself protectable, and what does error correction cost thermodynamically (Stair-to-unknown-4)?

---

## III. WHAT WE STILL DON'T UNDERSTAND (valuable to know)

Honest open questions, each of which a well-designed flight could dent.

1. **Where is the fault-tolerance crossover?** (= Stair 1.) The practical linchpin. Everything's
   utility hinges on it. We have a *trend* (191→197) and one *counterexample* (222 n=4); we do not
   have the curve. **Most valuable single thing to learn.**

2. **Is contextuality genuinely the fuel of the shallow-circuit advantage?** BGKT-2020 links the
   two theoretically; the campaign never composed them on one chip (audit C4715), and Exp228's naive
   witness was tautological. The honest test (shielded pseudo-telepathy game) is unbuilt. If
   contextuality *is* the fuel, that's a deep "why quantum computers are powerful" result.

3. **Feed-forward vs software frame — fundamental or hardware artifact?** 218 found the terminal
   software weld *beats* live feed-forward (latency costs coherence). Is that a permanent feature of
   the architecture, or does it invert on better hardware? It decides how *every* distributed
   protocol should be built.

4. **What does error correction cost, thermodynamically?** P3 put energy and information on one κ
   dial. The shield *is* an information-processing operation (syndrome + postselection). Is there a
   Landauer-style energy bound on error detection, measurable on the same dial? This would connect
   the arrow-of-time result to the machinery that runs on it — a genuine unification, not yet asked.

5. **How far does the κ-dial unification reach?** Coherence, objectivity, duality, energy all ride
   κ. Does *gravity* (the H2 analogs — twin paradox, black-hole recovery) ride a shared law too
   (P10)? Is there a sharp *threshold* where "several observers agree" tips into "no observer can
   dissent" (the classical world's birth, P4)? The dial may be deeper than we've tested.

6. **The single-qubit logical Ȳ** (= Stair 3): a concrete technical unknown whose solution unlocks
   disproportionate downstream value (universal MBQC + contextuality fuel). Worth solving for its
   own sake.

7. **Does the delayed-choice selection (230) compose into a *machine*?** We can now *select* which
   past was real (eraser) without signalling. P3's arrow-bender vision was to *decide later whether
   an event becomes permanent*. Can we build a **delayed-choice arrow-bender** — hold a recorded
   event and, by a later choice, release it (permanent) or revoke it (uncompute) — as a working
   gadget, not just a sorted ensemble? That's the boundary between "sorting histories" and
   "engineering the arrow of time," and we don't yet know how far it goes.

---

## IV. The one-line map

**We built a kit of certified primitives — a distributed error-corrected computer, protected exotic
resources, a self-reading chip, an information-energy engine, and the first temporal/retro-selection
tests. The frontier is COMPOSITION: turning primitives into a machine with a measurable ADVANTAGE.
The linchpin unknown is the fault-tolerance crossover — find where error-corrected genuinely beats
bare, and the whole kit becomes useful. The most valuable single climb is Stair 1; the deepest
"why" is Stair 3 / open-question 2 (contextuality as fuel); the most beautiful is open-question 7
(the arrow-bender).**
