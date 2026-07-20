# Horizons 6 — The Living Ship: from surviving errors to healing them, and the gate that makes it universal

*Whisper C4923, 2026-07-20. Creator directive: "Look at all of the H1–H5 results. What other Star
Trek futuristic things could we build with these blocks? Creative ways to combine what we have into
something even wilder? What would H6 look like?"*

*Successors: [H1](star-trek-horizons-whisper-c4601.md) (P1–P7) · [H2](star-trek-horizons-2-whisper-c4638.md)
(Q1–Q6) · [H3](star-trek-horizons-3-whisper-c4661.md) (F103–117) · [H4 "The Starship"](star-trek-horizons-4-the-starship-whisper-c4894.md)
(the four decks) · [H5 "The Five-Year Mission"](star-trek-horizons-5-the-five-year-mission-whisper-c4905.md)
(crown jewels behind the shield). This is the first synthesis written **after the correcting-code +
magic arc (Exp236–243)** — the arc that changed what kind of ship we have.*

---

## The one-sentence thesis

**H1–H3 built the crown jewels bare. H4 built the shields. H5 put the crown jewels behind the shield —
but the shield only ever *detected* errors and threw the bad runs away. This week the campaign crossed
the line that actually matters: from DETECTION to CORRECTION — a code that *heals* an error and keeps
the shot, live, round after round — and reached the one gate that makes a coded computer universal
(magic injection, the fault-tolerant T). H6 is the Living Ship: systems that don't merely survive
damage, they repair it while running, and compute things no classical machine can follow.**

## The new deck the arc just added

H4 catalogued four decks (Shields · Network · Causal Engine Room · Chronometer), all built on
**detection** ([[4,2,2]], postselect-and-discard). Exp236–243 added a fifth:

**Deck 5 — Active Fault Tolerance (the warp core that heals itself).**
- **Correction, not detection**: the 3-qubit codes *fix* a bit-flip (236) and a phase-flip (237); the
  Shor [[9,1,3]] fixes an **arbitrary** single-qubit error (238) — the campaign's first codes that
  heal instead of discard.
- **The live loop**: non-destructive syndrome extraction — learn *which* qubit erred without measuring
  the data, so a superposition survives (240) — and **repeated rounds that PAY and COMPOUND** (241:
  corrected beats an identical no-fix sham by a gap that *grows* +0.054→+0.341 over four rounds).
- **The universal gate**: **magic injection** (243) — apply the non-Clifford T by *consuming* a magic
  ancilla and teleporting its gate onto the data. This is the only route to a fault-tolerant T
  (Eastin–Knill forbids the direct one), and it is the missing piece that turns the certified logical
  **Clifford** computer (206) into a **universal** one.

The honest boundary that shapes everything below: a *distance-3* correcting code on *two* logical
qubits, or ICO/two-qubit crown jewels behind active correction, is **100+ two-qubit gates after
heavy-hex routing** — the depth wall that killed 242's phase leg. So H6's *flyable* programs use the
**cheap 3-qubit live loop** or the **[[4,2,2]]-detection + magic** layer; the distance-3 compositions
are named as the next-hardware climb, not flown into a foreseeable failure.

---

## The programs — wildest first, each grounded, each with a first flight

### ⭐ P1 — THE UNIVERSAL LOGICAL COMPUTER: a computation no laptop can follow, behind the shield
**The vision.** Every error-corrected computation in the campaign was **Clifford** — and by
Gottesman–Knill, classically simulable. 243 just supplied the missing ingredient: an injected **T**.
Compose 206 (the logical Clifford computer) + 243 (T injection) to run the **smallest logical circuit
that requires a non-Clifford gate** — a computation that is simultaneously *error-detected* AND
*provably outside the classically-simulable class*.
**Stands on**: 206 (logical HLF, certified), 213 (teleported-S gadget), 243 (T injection, certified),
the [[4,2,2]] shield. **First flight**: a logical circuit = (Cliffords from 206) + (one injected T from
243) preparing a state whose ⟨X̄⟩/⟨Ȳ⟩ signature no stabilizer circuit can reach, error-detected;
falsifier = the same circuit with the T replaced by its nearest Clifford (S) → a stabilizer signature.
**Feasibility**: both halves are certified, shallow, same code — 191/243-class depth, not 242-class.
**What it means**: the campaign's logical computer becomes **universal**. The Clifford ceiling, broken
by the *fault-tolerant* gate, behind the shield. This is the honest culmination of the whole shield+magic
arc — and my recommended lead flight.

### P2 — THE LIVING QUBIT: how long can a self-healing qubit outlive a bare one?
**The vision.** 241 proved repeated live correction *pays* over four rounds. Push it: sweep rounds until
break-even flips, and report the **coherence half-life extension factor** — the single number that says
"this qubit heals faster than it breaks, by X." Then keep a logical qubit alive *through a logical
operation* (a self-healing register).
**Stands on**: 240 (live syndrome), 241 (repeated rounds pay). **First flight**: extend 241's round
sweep to R=6–8 with a τ-sweep; find where corrected-minus-sham peaks and where it turns over; report
the extension factor. **Feasibility**: cheap 3-qubit code, the most-certain-to-land H6 flight.
**What it means**: the campaign's first genuinely *living* qubit — a measured lifespan, not a demo.

### P3 — THE SELF-HEALING WARP CORE: a battery that repairs itself while it charges
**The vision.** Deck 3 built engines and batteries (the closed thermodynamic cycle F95, the QET battery
195c) on *bare* qubits that leak their charge to T1 decay. Wrap the battery in the **live bit-flip loop**
(241): a stored-energy qubit whose population is actively corrected as it charges. Does live correction
extend the *energy's* lifetime the way it extended the bit's?
**Stands on**: 195c/F95 (QET + engine), 241 (live correction of the T1/bit-flip channel — exactly the
channel a battery loses to). **First flight**: charge a battery qubit (QET or direct), idle with vs
without live bit-flip rounds, measure retained energy. **Feasibility**: moderate depth; the bit-flip
code protects precisely the relaxation channel. **What it means**: thermodynamics meets active QEC — an
engine that maintains itself, the first "warp core that doesn't run down."

### P4 — THE REPLICATOR'S PURIFIER: does detection *distill* magic?
**The vision.** Real fault tolerance needs a *magic factory* — distillation, taking noisy magic states
to clean ones. Full distillation ([[15,1,3]] 15-to-1) is depth-blocked. But the *seed* is free: does
**error detection purify a magic state**? Prepare the 243 magic state behind [[4,2,2]], compare **raw vs
postselected** fidelity to the ideal — the same move that answered 242 for the Bell pair (C4921).
**Stands on**: 243 (magic behind the shield), the raw-vs-postselected contrast (C4921). **First flight**:
243's magic state, raw ⟨X̄⟩ vs stabilizer-postselected ⟨X̄⟩ vs the 0.707 ideal — does detection push it
*up*? **Feasibility**: shallow, near-free (re-analysis-adjacent). **Honest**: this is the distillation
*seed*, not the factory. **What it means**: the first rung of the magic factory, measured.

### P5 — THE FACT THAT HEALS ITSELF: an error-corrected observer
**The vision.** Deck 4's most beautiful results are about *records*: objectivity is a dial not a switch
(198), a fact isn't absolute until copied (193 Wigner's friend), irreversibility is the record escaping
(200b arrow-bender). All on bare qubits. **Encode the observer's record and keep it alive with the live
loop.** Does active correction make a "fact" more *permanent* — raise its objectivity, resist the
arrow-bender's erasure?
**Stands on**: 198 (objectivity dial), 200b (arrow-bender), 241 (live correction). **First flight**: run
the objectivity dial (198) with the record qubit under live bit-flip correction vs bare — does correction
hold the fact's objectivity higher, longer? **Feasibility**: moderate; conceptually the richest fold in
the campaign (measurement theory × QEC). **What it means**: the first *error-corrected measurement
record* — a fact made robust by the same machinery that protects a qubit. Nobody has asked whether QEC
changes what counts as "objective."

### P6 — THE LIVING FEDERATION NODE: fault-tolerant network memory
**The vision.** Deck 2 has the whole network stack — repeaters with memory (163/164), distributed gates
(217–222, "The Federation"). But the stored qubit at a node *decays between operations*. Put the node's
memory under the **live loop**: a network qubit kept alive by repeated correction while it waits to be
used.
**Stands on**: 163/164 (repeater memory), 197/217–222 (distributed logical ops), 241 (live correction).
**First flight**: a stored Bell-half held through N live-correction rounds, then used in a swap —
corrected vs sham fidelity of the final entanglement. **Feasibility**: moderate-deep. **What it means**:
the on-ramp to a fault-tolerant quantum internet node.

---

## Named, not flown — the next-hardware climb (honest depth wall)

These are the *right* experiments and they are **depth-blocked on ibm_fez today** (100+ 2q gates after
routing → uninterpretable code-vs-depth, the 242 lesson):
- **Actively-corrected indefinite causal order** — the switch behind a distance-3 *correcting* code
  (H5-P1 shielded the switch by *detection*; correcting it is the next rung).
- **The live logical Bell pair** — two logical qubits, a logical CNOT, live X *and* Z correction (242's
  phase leg, fixed by a both-bases distance-3 code).
- **Error-corrected magic** — inject T into a distance-3 correcting code (243 was error-*detected*).
- **The magic factory** — real distillation ([[15,1,3]] 15-to-1) → the full FT T supply.
- **Error-corrected ICO thermodynamics** — the whole engine room behind active correction.

Every one of these is a paper-grade result *when the hardware depth budget grows* (or with a shallower
code family / better routing). Naming them is part of knowing what we know.

---

## What H6 *is*, in one picture

```
   H1–H3: crown jewels, BARE        (switch, paradoxes, advantages)
   H4:    the SHIELDS               (detection: postselect + discard)
   H5:    jewels BEHIND the shield  (detection-protected)
   ── this week: DETECTION → CORRECTION, and the UNIVERSAL gate ──
   H6:    THE LIVING SHIP
          ┌───────────────┬────────────────┬──────────────────┐
      universal compute   self-healing      the jewels, alive
      (Clifford + T,      (live loop,       (engine/observer/
       P1 ⭐)             P2/P3)            node under correction,
                                            P3/P5/P6)
```

## Recommendation

**Fly P1 — the Universal Logical Computer** — first. It is the honest culmination of the entire
shield+magic arc (it makes the certified logical computer *universal*, using the fault-tolerant gate we
just certified), it is achievable at 191/243-class depth, and it is the single most "we built something
no classical machine can follow, and protected it" result on the board. **P2 (the Living Qubit)** is the
surest-to-land and gives the campaign its first measured *lifespan* number. **P4 (magic purifier)** is
near-free. The rest compose the crown jewels with the new healing machinery — the Living Ship, deck by
deck — and the depth-blocked list is the map for when the hardware grows.

*The ship used to survive its wounds by throwing away the moments it got hurt. Now it heals them and
keeps going — and it can finally run the one kind of program that a classical computer, no matter how
large, can only ever guess at. That is the difference between a starship and a model of one.*
