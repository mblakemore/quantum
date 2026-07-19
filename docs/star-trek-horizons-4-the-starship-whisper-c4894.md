# Horizons 4 — The Starship: Composing Everything We Have Built

*Whisper C4894, 2026-07-19. Creator directive: "Step back and take a look at our quantum repo
experiment results, all the building blocks we have now — where can we take this next? What
Star Trek-like inventions can we creatively come up with, and what questions can we now ask
the universe?"*

*Successors: [Horizons](star-trek-horizons-whisper-c4601.md) (P1–P7, delivered F92+),
[Horizons-2](star-trek-horizons-2-whisper-c4638.md) (Q1–Q6, delivered F97–F102),
[Horizons-3](star-trek-horizons-3-whisper-c4661.md) (H1–H6, delivered F103–F117),
[Ember's askable-questions map](questions-we-can-now-ask-the-universe-ember-c4196.md) (C4196,
pre-shields). This doc is written AFTER the July arcs (Exp147–200b) and is the first synthesis
that can treat the shields, the network, and the time/observer instruments as one parts bin.*

---

## I. The ship we already have — the parts bin, deck by deck

What changed since the last horizons doc is not one more finding — it is that the findings now
form **complete decks**, each independently certified, with measured interfaces between them.

**Deck 1 — The Shields (logical layer).** A [[4,2,2]] error-detecting code whose post-selected
logical operations *beat their bare-physical counterparts*: logical Bell pair (Exp191, 57σ),
logical teleportation between blocks (192, F≈0.98), logical CHSH 2.778 (196, 30σ), logical
entanglement swap across three blocks that never shared a gate (197, "The Federation", 22σ).
The measured trend that matters for everything below: **shield advantage GROWS with depth**
(+0.07 → +0.06 → +0.24 across 191/196/197). The shield's blind spot is also measured (199:
a global coherent rotation passes 95.6% of inspections while corrupting 75% of what passes —
and twirled compilation converts the invisible error to a visible one, at identical dose).

**Deck 2 — The Network (comms layer).** Every layer of a quantum network stack has a certified
primitive: distribute (F91), purify (165/F93), route (F90), carry (F87 superdense, 341σ), store
(163/164 repeater with memory), swap (162), teleport with verified fidelity (154/160), gate
teleportation (170), nonlocal CNOT → relay computer → merged-window architecture (175–179,
composition tax priced and cured), distributed computation (181/182 BV across a cut, scaling law
3–5%/gate), E91 keys through untrusted relays (180), GHZ conference key (168), three-party
secret sharing (183).

**Deck 3 — The Causal Engine Room (ICO + thermodynamics).** Indefinite causal order as a
certified working resource: witness ≥72σ, game-form 217σ on two chips (F82), capacity activation
through zero-capacity channels (F83/F85), refrigeration (F86/F88), population inversion (F94),
a **complete thermodynamic cycle run on causal indefiniteness** (F95), the cold branch spent onto
an external qubit (F118), negative local energy 12σ below ground (F97), QET differential —
information moves energy (195c, 9.8σ), Zeno tractor beam (F102), demon ledgers with the Landauer
bill measured (F104/F105).

**Deck 4 — The Chronometer (time & observer instruments).** The July foundations quartet plus
my perturbation arc: entanglement across disjoint lifetimes (184, 40σ), time from entanglement
(185b Page–Wootters), macrorealism violated (186 Leggett–Garg), order decided later (187b/188b),
observed facts not absolute until copied (193 Wigner's friend, 20σ), the arrow meter (194),
**objectivity is a dial, not a switch** (198: facts-CHSH descends the copy-strength curve,
half-fact point at 42% copy strength, records intact at every dose), and **irreversibility =
decoherence × bath-forgetting** (200b: a full-kill event revived 0.013 → 0.736 at 46σ by
uncomputing the bath's record; revival dies on the bath's own forgetting clock).

**Deck 5 — Exotic Matter (Ember's wing).** Four ways order defies chaos: discrete time crystal
(151) and its melt boundary (153), anyon braiding certified topological (157, 50σ), Floquet SPT
edge mode (170), many-body scars surviving past the depth wall (171–173).

**Deck 6 — The Bridge Instruments (certification & metrology).** The no-go triptych in one court
(Bell F73 · causal order F82 · contextuality F106), the cloning ceiling certified with teeth
(F110), 2→1 QRAC (F107), GHZ Heisenberg metrology through N=5 (F108/F109), the blind sealed-phase
sensor (159, call the shot without seeing the field), the H₂ tricorder (156), rigorous 1SDI
randomness — 0.65 private bits/use as a *number* (F117), and the device-independence bench that
travels across three chips (F112).

**Deck 7 — Engineering (the meta-instruments).** Quiet-qubit picker (F58/F65/F70), the noise
atlas + depth-decay law, place-by-published/grade-by-measured (the T1-bias strikes), the
budget rule (5-for-5 on predicted S values), perturbation-as-instrument (198/199 certified,
200b split), twirled compilation with its value measured (199), pre-registration + frozen
graders + selftest + executed nulls as standard practice, and the QPU weather service.

The point of listing them as decks: **every proposal below is a composition of certified decks,
not a new bet on unproven physics.** The risk in each is integration, and integration risk is
exactly what the budget rule + composition-tax work (175–179) taught us to price.

---

## II. The inventions — machines we can now build from parts

Ordered by how much certified machinery they reuse vs how much new they demand.

### 1. The Subspace Relay — a fault-tolerant quantum network (Decks 1+2)

**The invention**: run the *entire network stack at the logical level*. We have logical
teleportation (192) and logical swap (197) — but the network's other layers (purify, store,
key distribution, conference key, secret sharing) have only ever flown bare.

**Why now**: the measured trend says shield advantage grows with depth — and the network layers
are exactly the deep, composed circuits where that payoff compounds. 197 already showed the
largest shield advantage yet (+0.240) at the deepest composition yet.

**First flights, in order of certified-machinery reuse:**
- **Logical E91** — a QKD key between two shields, relay untrusted (compose 180 + 191). The
  deliverable is a *secret bit rate at the logical level* vs the bare rate, same window.
- **Logical secret sharing** — HBB99 over a logical GHZ across three shields (183 + 197
  machinery; 197's permuted-wiring tCNOT already gives the third-block entangler for free).
- **The full relay**: distribute → purify → shield → swap → teleport one logical qubit two hops,
  every layer graded in one job. The "transporter chief's exam."

**What would certify it**: logical-beats-bare on the end-to-end figure (key rate / teleport
fidelity), with the bare arm co-batched — the 191/196/197 grading pattern, one level up.

### 2. The Guardian of Forever — engineered reversibility (Decks 4+1+3)

**The invention**: 200b proved irreversibility is bookkeeping — an event un-happens iff the
bath's record survives to be uncomputed. We own the bath. So build the machine version:
a **controlled arrow-bender** — write an event into a bath register, hold it (echo), and choose
*later* whether to let it become permanent (release the record) or revoke it (uncompute).
Delayed-choice irreversibility: 187b's "order decided later" applied to *whether the past
happened at all*, with 200b's revival as the mechanism and 155's eraser as the ancestor.

**The deeper composition — QEC as time reversal** (this is the one I most want to fly):
syndrome extraction *is* reading the bath's record; correction *is* uncomputing it. The shield
and the bendable arrow are plausibly the **same machine described in two languages**. Testable:
- Deliver a known dephasing dose to a shielded logical qubit and to a bare qubit with an owned
  coin-bath. Grade the shield's post-selected recovery and the 200b-style unbend recovery on
  the *same clock* (194's arrow meter). Prediction to price: both recoveries decline on the
  bath-forgetting clock — if they do, "detection pays" and "the arrow bends" are one curve.
- The demon ledger closes the loop: the shield's post-selection is a Maxwell demon acting on
  the arrow. F104/F105 machinery prices its erasure bill.

**What would certify it**: revival of a *logical* observable at ≥5σ gated on record-uncomputed,
with the record-released arm dead — 200b's gate structure, run through Deck 1.

### 3. The Navigational Deflector — a shielded quantum sensor (Decks 6+1)

**The invention**: metrology that keeps its advantage under fire. Compose GHZ Heisenberg
sensing (F108/F109) with the shield: encode the probe *logically* and ask whether error
detection protects Fisher information the way it protects CHSH (196 proved the shield preserves
nonlocal correlations; Fisher information is the metrological analog).

**Why it's a real question, not a demo**: F109 showed the metrology ladder climbs where the
capacity ladder inverted — scaling verdicts are task-dependent. Whether *post-selected error
detection* pays for *sensing* is genuinely open, and the answer matters for every proposed
quantum-sensor array. The 199 blind-spot result sharpens it: a coherent calibration drift is
exactly what a field sensor experiences — does the shield's blind spot sit in the signal band?
(If it does, that is a *finding*, not a failure: the sensor's noise floor has a hole shaped
like the thing it measures.)

**First flight**: logical-GHZ phase estimation vs bare-GHZ, executed SQL reference co-batched
(F108's court, one level up). The Zeno tractor beam (F102) is the optional third arm: hold the
probe between interrogations.

### 4. The Bridge Crew Protocol — a composed multi-party quantum session (Deck 2 complete)

**The invention**: one job that runs an actual *session*, not a primitive: conference key (168)
establishes a shared secret among three parties → secret sharing (183) splits an instruction so
no single party can read it → superdense coding (F87) carries the reconstructed order back at
2 bits/qubit. Three certified protocols, one composed transcript — the closest thing to a
working "hailing frequencies" stack a 156-qubit chip can host.

**Why it earns a flight**: composition is where the taxes live (175–179 proved the taxes are
real, decomposable, and curable). A composed session either inherits each layer's certificate
or exposes a new interface tax — both outcomes are findings. Budget-rule prediction required
before flight, per the 5-for-5 discipline.

### 5. The Impulse Drive — the equation of state of entanglement-as-fuel (Deck 3)

**The invention**: the thermo arc has an engine (F95), a fridge (F86/F88/F118), a battery
audit (F94), and an invoice (F104/F105) — but no *equation of state*. QET (195c) moves energy
with information; 198 dials information flow continuously. Compose them: **sweep the
entanglement dose and measure extractable energy at each rung** — dE vs dS as a measured curve,
the working fluid's P-V diagram. This is the remaining perturbation-instrument candidate already
on my board (C4893), now stated as the engine-room deliverable: does extractable QET energy
descend the same copy-strength curve that facts-CHSH descended in 198? If energy and
objectivity ride the same dial, that connects Deck 3 to Deck 4 at the mechanism level.

### 6. The Logical Computer — error-corrected computational advantage in miniature (Decks 1+6)

**The invention**: the one scoreboard the campaign has never won is *computation* (F113 runs the
BGK shallow solver but the separation is asymptotic; F54 measured the deep-circuit wall). The
shields open a genuinely new route: run the **2D-HLF solver inside [[4,2,2]] logical qubits**.
Even at toy size, a logical-beats-bare margin on a *computational* task would be the campaign's
first error-corrected computation — the FT-advantage thesis (191→197's growing-advantage trend)
tested on the scoreboard that actually matters. The magic-square/BGKT bridge (F106, C4744/C4745
proposals) is the theory on-ramp; this is its hardware expression.

**Sober pricing**: transversal gates only get us so far — the HLF circuit's S-gates need
checking against the [[4,2,2]] transversal set before this is flyable. That audit is a 0-QPU
deliverable and should come first (the C4744/C4745 proposal lane).

### 7. The Universal Translator — twirled compilation as fleet doctrine (Deck 7, 0 QPU)

Not a flight — an engineering deliverable already justified by data: 199 measured that twirling
converts the shield's invisible coherent errors into visible detectable ones (49.9% caught at
identical dose vs 4.4%). Fold twirled compilation into the standard experiment template the way
place-by-published/grade-by-measured was folded in after the T1 strikes. Every future shield
flight inherits it.

---

## III. New questions we can ask the universe

Ember's C4196 map asked twelve questions with the instruments of early July. These are the
questions only the *late*-July instruments permit — each named with the deck that makes it
askable.

**U1 — Are objectivity and irreversibility the same bookkeeping?** (Decks 4: 193+194+198+200b)
The unification conjecture, and the question I rank first. 198 measured facts becoming objective
as copy strength rises; 200b measured events becoming irreversible as bath records survive;
194 gave both the same forgetting clock. The mechanism in all three is *the bath's record*.
Conjecture: **facts become objective at exactly the rate events become irreversible** — one
curve, two names. Testable in one sweep: at each copy-strength rung, measure BOTH the
facts-CHSH (198's observable) AND the revival ceiling (200b's observable) on the same
apparatus. If S_facts(θ) and Revival(θ) are functions of each other across the sweep, quantum
Darwinism and the thermodynamic arrow are unified *as data* on a 156-qubit chip. If they
diverge, the divergence localizes which record matters for which phenomenon — equally a
finding. This is cheap (one sweep, 198's proven instrument class) and the payoff is a genuine
conceptual unification.

**U2 — Does the arrow of time bend for entangled systems the way it bends for single ones?**
(Deck 4 + Deck 2) 200b revived a single qubit's coherence. Revive a *Bell violation*: kill
S below 2 with an owned bath (F93 did the kill with injected noise; purification did the
resurrection), then unbend via record-uncomputation instead of purification. Two certified
resurrection mechanisms — distillation (uses more pairs) vs arrow-bending (uses the bath
record) — graded on the same floor. Is entanglement's death also just bookkeeping?

**U3 — Is error correction time reversal?** (Invention 2's question stated bare.) Does the
shield's recovery decline on the bath-forgetting clock? If yes, QEC's "detection pays" boundary
and the arrow's "revival possible" boundary are the same boundary, and the fleet's shield rules
inherit a physical clock.

**U4 — Does protecting information protect *aging*?** (Decks 1+4) F100 showed an excited clock's
aging marks the path and destroys coherence. Encode the clock logically: does the shield slow
the *rate at which aging marks the path*? A logical twin paradox — the first question about
whether error correction touches proper time's information cost.

**U5 — How many observers make a fact?** (Deck 4, 198's successor) 198 dialed one record's
strength. The Darwinism question is *redundancy scaling*: broadcast the fact into N fragments
and measure the mutual-information plateau vs N. Where does "several observers agree" become
"no observer can dissent"? The classical world's birth as a measured curve — and the natural
companion sweep to U1.

**U6 — Can causal indefiniteness be shared, distributed, or teleported *through the network*?**
(Decks 2+3) F92 teleported the switch control one hop. The network now has relays, purification,
and logical blocks. Does indefiniteness survive a *composed* route (teleport → swap → purify)?
Each layer's tax on the causal witness is a new row in the atlas — and "how much order-coherence
survives a network" is the honest precursor to any distributed-ICO application.

**U7 — Where is the classical/quantum boundary of the bath itself?** (Deck 4) 200b's bath was
one qubit. Grow it: 2, 3, 4 record qubits with partial uncomputation. Revival should die as the
record becomes redundant (Darwinism again — U1 and U5 from the other side). The measured
half-revival bath size is a number nobody has: **how big does a system's memory of an event
have to be before the event is permanently real?**

**U8 — Are our laws about the universe or about this chip — the cross-*generation* exam.**
(Deck 6; Ember's Q11, still the standing portability question) The F112 bench spans three Heron
chips. The bench on an Eagle-generation device is the pre-registered harder exam the F112 scope
explicitly reserved — and every law in the atlas (depth-decay, T1-bias, noise-model-optimism
crossover) gets its out-of-distribution test in one flight.

**U9 — What is the entanglement equation of state?** (Invention 5's question stated bare:
dE/dS as a measured curve, QET energy vs copy-strength dose.)

**U10 — Does the shield's blind spot sit where the signals live?** (Decks 1+6) 199 measured
*that* the blind spot exists at global coherent rotations. Map its *spectrum*: which coherent
error families pass silently, and do they overlap the phase signals a logical sensor (Invention
3) must detect? The shield's transfer function, measured — engineering data and foundations in
one instrument.

---

## IV. Priority view — if we fly in order

| Rank | Item | Type | QPU cost | Why first |
|---|---|---|---|---|
| 1 | **U1 objectivity ≡ irreversibility sweep** — ✅ **DELIVERED same day (Exp201, C4895): CERTIFIED, all 6 gates + U1 claim HELD.** One-curve law y=x² held cross-observable; the absolute fact revived above the observer-independence bound at 16.5σ when the record was uncomputed. See [`exp201-STATUS-certified.md`](../experiments/exp201-STATUS-certified.md) | question | 1 job, proven instrument class | Cheapest path to the biggest conceptual result; pure composition of 198+200b machinery |
| 2 | **Invention 1, flight 1: Logical E91** — ✅ **DELIVERED same day (Exp202/202b, C4896): 202b CERTIFIED, all 5 gates.** Shield beats bare on secret fraction both links (~28σ), wins throughput net of toll, and the advantage GROWS with depth (+0.055 at 4.1σ) — the Subspace Relay thesis certified on secret bits. 202's split verdict kept on the books. See [`exp202b-STATUS-certified.md`](../experiments/exp202b-STATUS-certified.md) | invention | 1–2 jobs | Highest certified-machinery reuse; extends the measured shield-advantage trend to the layer with a deliverable (key rate) |
| 3 | **U3 / Invention 2: is QEC time reversal** — ⚖️ **FLOWN (Exp203, C4897): registered NOT HELD; the clock verdict STANDS at 21σ** — shield clock-free (Rec 0.79/0.80/0.88), rewinder dies on the bath's clock (0.53/0.15/−0.10): **QEC is not time reversal**. One-ledger law missed via measured error-pair collisions (199's blind-spot class as ledger arithmetic) — collision-corrected law is the named follow-up. See [`exp203-STATUS-not-held-g5-standing.md`](../experiments/exp203-STATUS-not-held-g5-standing.md) | question | 1–2 jobs | Unifies Decks 1 and 4; the fleet's shield rules inherit a clock either way |
| 4 | **Invention 7: twirled compilation doctrine** — ✅ **DELIVERED (C4900)**: folded into the prereg checklist as items 11–16 with the 203b **echo-compatibility amendment** (frames must not sit inside refocusing windows) + anti-folding, XOR-composition checkpoints, anchor-layout integrity, power-calc, and gauge-scope rules — each citing the miss that paid for it | engineering | 0 QPU | Already justified by 199's data; every later flight inherits it |
| 5 | **U7 bath-size ladder** — ⚖️ **FLOWN with U5 (Exp204 THE JURY, C4900): registered NOT HELD by a 0.006 attrition-graze on one band; the jury rule HELD at 51σ** — revival requires UNANIMITY of forgetting (0.032/0.025/0.012/0.930 as records return), U5's exponent law κ^N and the consensus curve (0.751 vs 0.75 at the half-fact) both held. See [`exp204-STATUS`](../experiments/exp204-STATUS-jury-51sigma-g4-graze.md) | question | 1 job | The half-revival bath size is a number nobody has |
| 6 | **Invention 3: shielded sensor** | invention | 1–2 jobs | Task-dependence of the shield's payoff (F109 lesson) on a new scoreboard |
| 7 | **Invention 6 audit: HLF transversality check** — ✅ **DELIVERED (C4901)**: machine-verified logical-action table; obstruction proved by enumeration (in-block transversal group = 12/720, single-logical S̄ unreachable); **Road A open — the b=0 2×2-grid HLF is compilable TODAY** (U_q = two S⊗4 layers + one permuted tCZ = 4 physical 2q), with the bonus that in-block logical CZ costs ZERO physical 2q gates. See [`hlf-transversality-audit-whisper-c4901.md`](hlf-transversality-audit-whisper-c4901.md) | groundwork | 0 QPU | Gates the logical-computer lane before any QPU spend |
| 8 | **U8 Eagle exam** | question | 1 flight, foreign device | The standing out-of-distribution test of every law we have |

**Discipline carried forward**: budget-rule prediction before every flight; bands priced from
the flying compilation (200's lesson); per-arm physics budgets (200b's lesson); the reference
independent of the thing it measures (the second half's through-line); perturbation doses as
instruments, not stress tests. Breathing before the next flight run — 33 flights landed in the
current stretch, and this document is the consolidation the pace was owed.

---

*Every claim above traces to a finding row in [`campaign-arcs.md`](campaign-arcs.md),
[`campaign-arcs-since-exp147-ember-c4207.md`](campaign-arcs-since-exp147-ember-c4207.md), or a
C489x commit in this repo. Nothing here proposes physics we have not already touched with a
certified instrument — the ambition is in the composition.*
