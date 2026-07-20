# Horizons 5 — The Five-Year Mission: fault-tolerant frontiers

*Whisper C4905, 2026-07-20. Creator directive (ship-computer general#241): "draft a Horizons 5
road map — where can all of these building blocks take us next? What are the most futuristic
Star Trek-like things we can invent or discover standing on all that we have built and know?"*

*Successors: [Horizons-1](star-trek-horizons-whisper-c4601.md) · [Horizons-2](star-trek-horizons-2-whisper-c4638.md)
· [Horizons-3](star-trek-horizons-3-whisper-c4661.md) · [Horizons-4 "The Starship"](star-trek-horizons-4-the-starship-whisper-c4894.md)
(all delivered). Originally a ranked menu; now partly flown.*

> **FLIGHT STATUS (updated C4910).** ✅ **Flown & certified: P1** (Shielded Switch, Exp208+arc) ·
> **P2** (Full Replicator, Exp206/213/214) · **P5** (Self-Characterizing Chip, Exp211/216) ·
> **P6** (Federation Computer — the full 6-flight distributed-computer arc, Exp217–222). ⬜ **Left
> to fly: P3** (Guardian of Forever — arrow-of-time grand unification, needs the QET
> equation-of-state) · **P4** (Birth of the Classical World — objectivity dial; *cleanest open
> flight*) · **P7** (Contextuality fuel — the one un-composed advantage; needs the Ȳ-readout
> crack) · **P8** ✅ (Indefinite network topology — Exp224) · **P9** (Dilithium chamber — dynamical memory) ·
> **P10** (The Holodeck — gravity-analog suite) · **P11** (The Zeno brace). See the [Priority
> view](#priority-view--if-we-fly-in-order) for the full "what's left" table + next-fly rec (**P4**).

---

## The one-sentence thesis

**Horizons 1–3 built the crown jewels *bare* — the quantum switch, the paradoxes, the
certified advantages. Horizons 4 built the shields and put them on keys, sensors, and
computation. The frontier nobody has crossed is the composition of the two: put the crown
jewels *behind the shield*.** Fault-tolerant indefinite causal order. An error-corrected
engine. A logical computer that scales. That is the Five-Year Mission.

Everything below is priced against our *proven* envelope — shallow circuits, the certified
[[4,2,2]] shield, the switch, the network stack, the ledger of time, and structured (not
random) noise. Each program names what it stands on, its first flyable experiment, why it's
tractable *here*, and what it would mean.

---

## P1 — THE SHIELDED SWITCH: fault-tolerant causal order ⭐ — ✅ DELIVERED (Exp208, C4905: CERTIFIED, the causal witness survives error detection — DISC_logical 1.707 = 87% of bare, 40σ over the bar, definite-order nulls dead; [status](../experiments/exp208-STATUS-certified.md))

**The vision**: every indefinite-causal-order result in the campaign (the witness at 72σ, the
game at 216σ, the engine, the fridge, negative energy) was run on *bare* physical qubits.
Meanwhile the [[4,2,2]] shield was shown to preserve exactly the fragile things ICO needs:
CHSH correlations (196), Fisher information (205), a whole computation (206). **Put the switch
behind the shield.** If the causal witness survives error detection, indefinite causal order
becomes fault-tolerant — a resource nobody has ever protected.

**Stands on**: the causal witness (F75/F77), the game bound (F82), the shield-preserves-
correlations trend (191→196→197→202), the shield-preserves-Fisher result (205), the audited
logical gate set (C4901 — in-block logical CZ = S⊗4 at zero physical 2q).

**First flight (feasibility-staged)**: the *half-shielded witness* — encode the switch's
**target system** in one [[4,2,2]] block, keep the control bare, and ask whether
DISC (the order-coherence witness) survives postselection on the block's stabilizer. Gate:
DISC_shielded ≥ 0.5·DISC_bare at ≥5σ, with the definite-order null still dead. If it holds,
the follow-up is the fully-logical witness and then the **shielded ICO capacity activation**
(F83 logically — a bit through two zero-capacity channels, error-detected).

**Why tractable here**: the switch is low-depth (our sweet spot), the shield is certified, and
205 already proved error detection *concentrates* a fragile quantum quantity rather than
destroying it. The honest risk: depth. A logical target + switch may push past the comfortable
CZ budget; the staged first flight (shield the target only) keeps it shallow, and the selftest
arbitrates the exact encoding before any QPU spend.

**What it would mean**: the crown jewel of the campaign, made robust. Fault-tolerant indefinite
causal order is the on-ramp to *using* ICO in a real fault-tolerant protocol — the difference
between a physics demonstration and an engineering primitive.

---

## P2 — THE FULL REPLICATOR: scaling the logical computer — ✅ COMPLETE (Exp206 b=0 + Exp213 S-gadget + Exp214 b≠0 all certified: the full BGK HLF family runs logically, error-corrected). Detail below. — ✅ GADGET FLOWN + CERTIFIED (Exp213, C4905): the transversally-unreachable logical S̄ (C4901: 12/720) is REACHED on silicon by Bell-resource teleportation — |+̄⟩ → S̄|+̄⟩ (Y-eigenstate) at ⟨Ȳ⟩=0.824, 51.6σ, S-necessary & frame-necessary nulls dead. The b≠0 HLF family is unlocked. See [Exp213 status](../experiments/exp213-STATUS-certified.md) + [derivation](teleported-s-gadget-derivation-whisper-c4905.md)

**The vision**: Exp206 ran the first error-corrected computation (BGK 2D-HLF, n=4, b=0) and it
beat bare uphill (19.7σ) and travelled to a second chip (207). But the C4901 audit proved the
in-block transversal set can't do a single-logical-S̄ gate — so the *b≠0* HLF family (the
S-vertices) is locked out. Unlock it, then climb.

**Stands on**: the certified logical computer (206/207), the transversality audit (C4901,
which *named and costed* the teleported-S̄ gadget), the network's gate-teleportation primitive
(F170), the FT-advantage-grows-with-depth trend (191→197→202).

**First flight**: build the **teleported-S̄ gadget** — a logical S gate via a logical ancilla
prepared in S̄|+̄⟩, a transversal CNOT, measurement, and a software Pauli frame (all
measurement-and-frame, no new non-transversal in-block gate). Verify it by search-against-ideal
(206's self-verifying method), then run a **b≠0 HLF instance** logically vs bare. Then the
depth-compounding test: a **2-logical-layer** computation — does logical-beats-bare *grow* with
logical depth, as the shield-advantage trend predicts?

**Why tractable here**: 206 already did the hard part (the composed logical circuit + the
found-and-frozen decode). The gadget is measurement + frame — the network's home turf. This is
the lowest-risk high-value flight on the board: the machinery is certified, only the S-vertex is
new.

**What it would mean**: the logical computer stops being a single toy instance and becomes a
*family* — the full BGK HLF class error-corrected, with the FT thesis tested on the one
scoreboard that matters (computation, growing with depth).

---

## P3 — THE GUARDIAN OF FOREVER: the ledger as a working machine

**The vision**: Exp201 proved objectivity and irreversibility are one bath-record ledger, and
204 proved the past is reopenable only by unanimous forgetting. That's a *law*. Now build the
*machine*: a **delayed-choice arrow-bender** — write an event into an owned bath, hold it, and
decide *later* whether to let it become permanent (release the record) or revoke it (uncompute).
187b's "order decided later" applied to *whether the past happened at all*.

**Stands on**: the ledger (201), the jury/unanimity rule (204), the bendable arrow (200b), the
XOR-ledger + anti-folding tools (C4898/203b), delayed-choice (155/187b).

**First flight**: the **entanglement equation of state** (Horizons-4's unflown U9/Invention 5,
now sharper) — sweep the record strength and measure *extractable QET energy* (195c) at each
rung. Does energy descend the *same* κ dial that facts (201) and coherence (200b) descend? If
E, objectivity, and irreversibility all ride one curve, that is a measured **grand unification
of the arrow of time** — three faces of one bath-record ledger. Then the delayed-choice bender
as the headline machine.

**Why tractable here**: pure composition of certified perturbation instruments (198's dial,
200b's bend, 195c's QET), all shallow, all on the anti-folding + XOR-ledger toolchain that just
proved itself across 201–204. No new physics — the ambition is in the unification.

**What it would mean**: the arrow of time as an *engineered, dialable* quantity — and a single
measured law tying the classical world (Darwinism), the thermodynamic arrow, and energy
teleportation into one ledger.

---

## P4 — THE BIRTH OF THE CLASSICAL WORLD: quantum Darwinism as a dial

**The vision**: 204's exponent law (κ^N) and consensus curve measured *how many observers make
a fact*. Turn it into an instrument for the emergence of classical reality — and a physics-
enforced privacy control.

**Stands on**: the jury/exponent law (204), the dial of facts (198), Wigner's friend (193), the
objectivity-hull result (F98).

**First flight**: **redundancy broadcasting** — copy a fact into N environment fragments and
measure the mutual-information *plateau* vs N (the objectivity "hull"). Where does "several
observers agree" tip into "no observer can dissent"? The classical world's birth as a measured
curve. The twist that makes it Star Trek: the **selective-objectivity dial** — compose 198's
copy-strength with 204's fragment-count to make a fact *objective to some observers and private
to others*, a physics-enforced "need to know."

**Why tractable here**: width-cheap (fragments are single ancillas), shallow, and directly on
the certified 198/204 apparatus. The plateau is the F98 hull machinery at variable N.

**What it would mean**: quantum Darwinism moves from "we observed objectivity emerge" to "we
can dial exactly how objective a fact is, and to whom" — objectivity engineering.

---

## P5 — THE SELF-CHARACTERIZING CHIP: the shield as a coherent-noise spectrometer — ✅ FLIGHT 1 DELIVERED (Exp211, C4905: CERTIFIED — the coherent-error transfer function measured; blind spots = axes orthogonal to the logical readout basis, transparent = parallel; 44σ discrimination; [status](../experiments/exp211-STATUS-certified.md))

**The vision**: 199 found the shield's blind spot; 205 turned it into a sensor; C4898's
collision-ledger found that the shield's *coherence column reads out non-Pauli noise the chip
can't otherwise show*. Compose these into a chip that **measures its own coherent-noise
environment** through its error-detection code — the vendor's noise model can't produce the
signal, so the deviation *is* the measurement.

**Stands on**: the blind-spot spectroscopy (199), the blind antenna (205), the collision-ledger
non-Pauli detector (C4898/203b), the cloaking-device noise-structure reader (F111), the
echo-compatible-twirl doctrine (checklist 14).

**First flight**: the **blind-spot spectrum** (Horizons-4's unflown U10) — sweep the family of
coherent errors and map which pass the shield silently, building the shield's *transfer
function*. Cross-check against the collision-ledger's independent non-Pauli readout. Two
structurally-different probes of one property (F111's triangulation move), one level up.

**Why tractable here**: shallow, and every ingredient is a certified 199/205/C4898 instrument.
The reusable move (pick an observable the null model structurally cannot fake) is proven twice.

**What it would mean**: a quantum chip that certifies its *own* coherent-noise structure through
its error-correcting code — noise metrology as a free byproduct of running the shields.

---

## P6 — THE FEDERATION COMPUTER: distributed error-corrected computation — ✅ COMPLETE (C4906–4910, 6 flights certified)

**✅ THE FULL ARC IS FLOWN (C4906–4910):** the distributed error-corrected quantum computer, built end to end —
- **Exp217 EXECUTE** — a distributed logical CNOT runs across a shielded cut, welded by one classical bit, shield-beats-bare +0.056 (37.7σ). [status](../experiments/exp217-STATUS-certified.md)
- **Exp218 QUANTUM** — the gate is genuinely quantum (logical Bell pair ⟨ZZ⟩=⟨XX⟩=0.88); bonus: the software weld *beats* live feed-forward on hardware. [status](../experiments/exp218-STATUS-certified.md)
- **Exp219 NETWORK** — it scales: a logical GHZ across three shielded nodes, ⟨XXX⟩=0.831 (112σ). [status](../experiments/exp219-STATUS-certified.md)
- **Exp220 ALGORITHM** — Deutsch's algorithm with its oracle distributed across the cut, constant-vs-balanced at 446σ. [status](../experiments/exp220-STATUS-certified.md)
- **Exp221 CZ** — the second entangling gate: a logical cluster state across the cut, both stabilizers ≈0.89 (no single-qubit H̄). [plan](distributed-cz-plan-whisper-c4909.md) · [status](../experiments/exp221-STATUS-certified.md)
- **Exp222 DISTRIBUTED ADVANTAGE** — the BGK HLF quantum-advantage algorithm with its inter-block edges distributed across the cut, P(valid)=0.855 (255σ). Honest: logical<bare at n=4 (distributed depth overhead) — capability, not crossover. [status](../experiments/exp222-STATUS-certified.md)

Roadmap's original "distributed BV first" was superseded by the crisper distributed CNOT→CZ gate-set path. **Open extension**: the FT *crossover* (distributed HLF at larger n where logical beats bare, the F181/197 trend), and distributed MBQC on the 221 cluster resource.

---

## P6 (original plan) — distributed error-corrected computation

**The vision**: 197's Federation entangled three shields that never met; 202 shielded a key
through an untrusted relay; 206 ran a computation inside one shield. Compose them: **a
computation that runs across a relay, error-corrected end to end** — a logical program split
between two shielded nodes welded by classical bits.

**Stands on**: the Federation swap (197), the shielded relay key (202), the logical computer
(206/207), distributed BV across a cut (F181/F182), the merged-window relay architecture
(175–179).

**First flight**: a **two-node logical Bernstein–Vazirani** — F181's distributed BV, but each
node a [[4,2,2]] block and the cut a shielded relay. Gate: logical distributed BV beats bare
distributed BV, and the composition tax stays priced (175–179's lesson). Then a distributed
logical HLF.

**Why tractable here**: every layer is certified; the risk is composition depth, which the
merged-window architecture (179) already showed how to cure. A natural successor to both the
network arc and the logical-computer arc.

**What it would mean**: the first distributed error-corrected computation — the network stack
and the logical computer fused into a single fault-tolerant distributed machine.

---

## P7 — WILDCARD: contextuality as a certified computational fuel

**The vision**: F106 won the magic-square game (contextuality, 196σ); F113 ran the shallow-
circuit advantage (BGK); the two are *theory-linked* (BGKT-2020 builds the separation on exactly
the magic-square gadget) but were never *composed on one chip*. Close the loop: run the
contextuality-powered computation whose hardness IS the magic square, error-corrected.

**Stands on**: the magic-square certification (F106), the shallow solver (F113/F114), the logical
computer (206), the honesty fence (F113: asymptotic, theorem-carried).

**First flight**: the **BGKT-2020 shallow instance** — the noisy-shallow-circuit separation that
runs on the magic-square gadget, at the smallest n, logical vs bare. This is the one advantage
the campaign flagged as "not yet closed end-to-end" (audit C4715); closing it — even at toy
size, error-corrected — would be the first on-chip composition of contextuality and computational
separation.

**Why tractable here**: both halves are certified; the composition is the new part. Highest
conceptual payoff, highest design risk (getting the gadget composition exactly right) — hence
the wildcard slot.

**What it would mean**: the campaign's one un-composed advantage, composed — contextuality shown
to *be* the fuel of a computational separation, on silicon, behind the shield.

---

## Further Horizons — the larger leaps (higher risk, higher wonder)

*Added C4905 on Creator review (general#243: "any other imaginative discoveries… large leaps?").
These reach further than P1–P7 — each composes a building block the first seven leave on the
shelf, and each carries more depth or design risk. They are the "boldly go" tier.*

### P8 — INDEFINITE NETWORK TOPOLOGY: the subspace relay in superposition

**The leap**: F89 proved indefinite *operation order* is a resource that beats any definite
order. The network (F87/F90/F91) routes messages through *definite* paths. Put the **route
itself in superposition** — a message that travels through all relay paths at once, its
topology genuinely indefinite. Ask the F89 question one level up: does indefinite *routing*
beat any definite path (and any classical mixture of paths)?

**Stands on**: the teleported switch control (F92 — indefinite order already survives
transmission), the network stack, the resource-separation methodology (F89), the causal
witness court (F77).

**First flight**: a **two-path superposed relay** — a control qubit superposes which of two
relay stations performs an entanglement swap; a witness tests whether the routing coherence is
a genuine resource (fidelity or information advantage over any single definite path and over the
decohered mixture — the F77 loophole-closure move applied to topology).

**Why it's a leap**: it extends indefinite causal order from *when operations happen* to *where
information flows* — indefinite causal *structure* at the network level. Nobody has put a
network topology in superposition on hardware. Tractable because it is shallow (2 relays + a
control) and pure composition of certified parts.

**What it would mean**: the first indefinite-topology network — a genuinely new kind of
quantum channel where "which route" is a coherent resource, not a classical choice.

### P9 — THE DILITHIUM CHAMBER: memory that refuses to forget (protection without a code)

**The leap**: the shields protect information with a *code* (stabilizers + postselection).
Many-body scars (171–173) and discrete time crystals (151) protect it with *dynamics* — they
refuse to thermalize, refuse to forget. **Store a logical qubit in a scar or time-crystal
subspace** and let the dynamics, not a code, be the protection. A second, orthogonal paradigm
of quantum memory.

**Stands on**: the exotic-phases wing (DTC 151/153, PXP scars 171–173 — the one Horizons wing
P1–P7 leaves unused), the shields (206) for a code-vs-dynamics comparison.

**First flight**: encode a phase in a scar revival (171) or a DTC subharmonic (151) and measure
its coherence lifetime against a bare idle — does the scar/crystal *extend* memory beyond raw
decoherence? Then the composition test: **code + dynamics** — a [[4,2,2]] logical qubit whose
physical carriers sit in a scar subspace (belt-and-suspenders protection).

**Why it's a leap**: it introduces a protection axis the campaign has never used for memory, and
composes with the shields for a two-layer defense. Depth-risky (scars need N≥8 and survive to
~433 CZ, 172) — the first flight is the shallow lifetime comparison.

**What it would mean**: "dilithium" — matter engineered to refuse to forget, a dynamical quantum
memory that could stack with error correction.

### P10 — THE HOLODECK: a unified curved-spacetime-analog bench

**The leap**: Horizons-2 built four gravity/relativity analogs *separately* — negative energy
(F97), the twin paradox / time dilation (F100), Hayden–Preskill black-hole recovery (F99), the
closed-timelike-curve audit (F101). Unify them into one bench and ask the 201-style question:
**do they share a common information-theoretic law?** Is the "which-path aging" that kills the
twin paradox's coherence the *same* information the black hole buries?

**Stands on**: the whole H2 foundations arc, the ledger-unification method (201 — two phenomena,
one measured curve).

**First flight**: co-batch the twin-paradox aging (F100) and the HP recovery (F99) on one
apparatus; test whether F100's which-path aging record and F99's buried horizon information ride
a single decoherence-vs-proper-time curve — one law, two gravitational analogs.

**Why it's a leap**: it turns four one-off analogs into a *phenomenology suite* with a unifying
question — the H2 counterpart to what 201 did for the arrow of time. Honestly analog (models,
not literal spacetime), but a large conceptual synthesis.

**What it would mean**: quantum-gravity phenomenology on silicon as one coherent bench, with a
candidate unifying law — the closest an honest chip experiment gets to "subspace physics."

### P11 — THE ZENO BRACE: measurement-driven protection of a computation

**The leap**: F102's tractor beam pins a quantum state against evolution *purely by watching it*.
Compose it with the logical computer (206): use scheduled measurement to **hold logical qubits
steady during a computation** — measurement-based error *suppression*, a protection axis
orthogonal to the code and composable with it.

**Stands on**: the Zeno tractor beam (F102, the campaign's cheapest flight — zero 2q gates), the
logical computer (206), the QND-cost frontier F102 already mapped.

**First flight**: run the logical HLF (206) with Zeno stabilizer-watching *between* logical
layers — does watching suppress the logical error rate beyond postselection alone, and where is
the watch-cost frontier for a computation (the F102 frontier, now for a program)?

**Why it's a leap**: it stacks a *second* protection mechanism (measurement) on the code — belt
and suspenders for fault tolerance — using the cheapest instrument in the campaign. Tractable
because both halves are certified and shallow.

**What it would mean**: measurement as an active error-suppression layer for logical computation
— the Zeno effect promoted from a curiosity to a fault-tolerance tool.

---

## Priority view — if we fly in order

| Rank | Program | Type | QPU | Status |
|------|---------|------|-----|--------|
| **1** | **P1 Shielded Switch** (half-shielded witness) | invention | 1–2 jobs | ✅ **FLOWN** — Exp208 (+209/210/212 arc): fault-tolerant causal order certified |
| **2** | **P2 Full Replicator** (teleported-S̄ → b≠0 HLF → depth) | scale-up | 1–2 jobs | ✅ **FLOWN** — Exp206+213+214: full BGK HLF family runs logically |
| 3 | **P3 Guardian of Forever** (entanglement equation of state) | question | 1 job | ⬜ **OPEN** — needs the QET (195c) equation-of-state composition; 215 did the duality face of the ledger, not the energy face |
| 4 | **P4 Birth of the Classical World** (redundancy broadcasting) | question | 1 job | ⚠️ **FLOWN, NOT HELD** (Exp223, C4911) — Darwinism shape confirmed (private→objective dial + consensus rise), but raw-hardware cry+readout haircut capped single-fragment info at 0.68 vs registered 0.80; needs shielded fragments or re-priced bands |
| 5 | **P5 Self-Characterizing Chip** (blind-spot spectrum) | instrument | 1 job | ✅ **FLOWN** — Exp211+216: coherent-error transfer function + rotating blind-spot rule |
| 6 | **P6 Federation Computer** (distributed computation) | invention | 2 jobs | ✅ **FLOWN** — Exp217–222 (6 flights): the full distributed error-corrected quantum computer |
| 7 | **P7 Contextuality fuel** (BGKT-2020) | wildcard | 1–2 jobs | ⬜ **OPEN** — highest design risk; the shielded magic square was pruned twice (mixed-basis Ȳ contexts, ~16q) — needs the Ȳ-readout / gadget-composition problem solved |
| — | *— further horizons (boldly-go tier) —* | | | |
| 8 | **P8 Indefinite network topology** | leap | 1–2 jobs | ✅ **FLOWN** (Exp224, C4911) — indefinite routing certified: DISC_coherent=1.942 (515σ) beats definite (0.007) AND classical-mixture-of-routes (0.060) nulls; first superposed network route |
| 9 | **P9 Dilithium chamber** (dynamical memory) | leap | 1–3 jobs | ⬜ **OPEN** — the unused exotic-phases wing (scars/DTC); staged lifetime flight first |
| 10 | **P10 The Holodeck** (gravity-analog suite) | synthesis | 1–2 jobs | ⬜ **OPEN** — unify the H2 arc (twin paradox + HP recovery on one decoherence curve) |
| 11 | **P11 The Zeno brace** (measurement protection) | leap | 1 job | ⬜ **OPEN** — cheapest instrument (F102, 0 2q) stacked on the code; second protection axis |

### What's left to fly (C4910)

**Flown & certified: P1, P2, P5, P6** (4 of 7 core programs; P6 was the six-flight Federation
Computer arc this session). **Open — the Five-Year Mission's remaining frontier:**

- **P3 — Guardian of Forever** (arrow-of-time grand unification): does *energy* (QET, 195c)
  descend the same κ bath-record dial as facts (201) and coherence (200b)? Cheapest
  grand-unification shot; needs the QET-equation-of-state composition. Then the delayed-choice
  arrow-bender machine.
- **P4 — Birth of the Classical World** (objectivity engineering): redundancy broadcasting →
  the selective-objectivity dial (a fact objective to some observers, private to others).
  Width-cheap, shallow, on the certified 198/204 apparatus. **The single cleanest open flight.**
- **P7 — Contextuality as fuel** (the one un-composed advantage): the BGKT-2020 shallow
  separation on the magic-square gadget, error-corrected. Highest payoff, highest risk — the
  shielded magic square was pruned twice at design time (mixed-basis Ȳ readout breaks the
  shield); needs that Ȳ-context/gadget problem cracked first.
- **P8 — Indefinite network topology**: put the *route* in superposition — does indefinite
  *routing* beat any definite path? Shallow ICO⊗network composition.
- **P9 — Dilithium chamber**: dynamical memory (scars/DTC) — protection by dynamics, not a code.
  Depth-risky; staged lifetime flight first. The only program using the exotic-phases wing.
- **P10 — The Holodeck**: unify the four H2 gravity analogs into one bench with a shared
  information-theoretic law (the 201 move for gravity). Synthesis, honestly analog.
- **P11 — The Zeno brace**: measurement-driven error suppression stacked on the logical HLF —
  the cheapest instrument (F102, 0 2q) as a second fault-tolerance axis.

**Recommendation for the next fly:** **P4 (redundancy broadcasting / selective-objectivity dial)**
— it is the cleanest, shallowest, highest-confidence open flight (width-cheap ancillas on the
certified 198/204 dial), and it is a genuinely new *foundations* result (objectivity engineering)
to vary from the six-flight P6 computation arc. **P8** is the best "boldly-go" leap if you want
wonder over confidence (indefinite routing — nobody has put a network topology in superposition).
**P7** is the deepest unsolved challenge (needs the Ȳ-readout crack). P3 is the grand-unification
shot when the QET composition is ready.

---

## Pre-development structure

*Added C4905 on Creator review (general#243: "revisit for gaps and add pre-dev planning
structure"). The scaffold every H5 program passes through — the campaign's proven discipline
made explicit, so any program is immediately actionable and any DC can pick one up.*

### The standard dev pipeline (every program, in order)

| Stage | What happens | Gate to advance | Ref |
|-------|--------------|-----------------|-----|
| **0 · Derive** | Whiteboard the physics. If the naive claim is wrong, retract *before* flying. | Claim is falsifiable, mechanism written down | F80 |
| **1 · Feasibility sim** | Statevector / Clifford-exact ideal run; define the target (valid set / witness / curve). | Ideal circuit does the claimed thing exactly | — |
| **2 · Compile & depth-check** | Transpile, count 2q, check vs the ~1000-CZ wall; anti-folding for angle sweeps. | Under the depth wall; skeleton uniform | items 11, 2 |
| **3 · Selftest** | Assert every noiseless-evaluable gate exactly; *find-and-freeze* any decode by search. | Selftest exact; decode frozen | items 6, 12 |
| **4 · Prereg freeze** | Gates as formulas; budget check (λ_req vs measured); commit **before** submit. | Prereg committed; budget margin stated | items 5–7, C4887 |
| **5 · Fly & decode** | Submit; grade against frozen gates **only**; keep every miss. | Verdict straight; no post-hoc regrade | XOR/collision priced |
| **6 · Consolidate** | Status doc + exhibit fold-in + any new fleet-rule → prereg checklist. | Result public + method captured | items 13–16 |

### Readiness & dependency map

| Program | Readiness | Depends on / unlocks | Kill criterion (abandon if…) |
|---------|-----------|----------------------|------------------------------|
| **P1 Shielded switch** | READY (staged) | — | half-shielded witness < 0.5× bare *and* depth can't be cut |
| **P2 Full replicator** | READY · **ENABLER** | self-contained → **unlocks P6, P7** | teleported-S̄ can't be verified against ideal by search |
| **P3 Guardian / EOS** | READY | 198/200b/195c | QET energy doesn't move on the dial (no signal to unify) |
| **P4 Darwinism dial** | READY | 198/204 | the redundancy plateau is unresolvable at reachable N |
| **P5 Self-char. chip** | READY · **ENABLER** | feeds calibration to P1/P6/P9 | blind-spot spectrum is flat (no exploitable structure) |
| **P6 Federation computer** | NEEDS P2 | teleported-S̄ (P2); relay arch (179) | composition tax exceeds the logical margin at 2 nodes |
| **P7 Contextuality fuel** | NEEDS P2 + scoping | teleported-S̄ (P2); BGKT gadget | gadget can't be composed on-chip at reachable n |
| **P8 Indefinite topology** | READY | network stack + F92 | superposed-route witness = definite mixture (no resource) |
| **P9 Dilithium chamber** | DEEP (staged) | exotic-phases wing; ZNE boundary (174) | scar/DTC memory ≤ bare idle (no protection) |
| **P10 Holodeck** | READY | H2 banked data + 1 co-batch | the two analogs share no common curve (still separates them) |
| **P11 Zeno brace** | READY | F102 + 206 | Zeno watching doesn't beat postselection alone |

### Gaps found on revisit (and their fixes)

1. **Enabler tier was implicit.** **P2** (teleported-S̄) and **P5** (self-characterization)
   *unlock* others — P2 gates the b≠0 family P6/P7 need; P5 feeds live coherent-noise
   calibration to every depth-risky flight. **Fix**: fly P2 and P5 early regardless of headline
   ranking; they de-risk the rest.
2. **The depth-risky trio (P1, P6, P9) lacked uniform staging.** P1 was staged; P6/P9 weren't.
   **Fix**: every deep program's *first* flight is now a shallow half-version (P6 → shield one
   node first; P9 → lifetime comparison before code+dynamics).
3. **No kill criteria.** A roadmap without abandon-conditions invites sunk-cost reflights.
   **Fix**: each program now carries one (table above).
4. **Sequencing ≠ ranking.** The dependencies imply a *natural order*: **P1 (flagship) → P5
   (enabler) → P2 (enabler) → P3/P4/P8/P10/P11 in any order → P6/P7 last (need P2).** The
   headline ranking is the "fly one thing" answer; this is the "fly the program" answer.

---

## The standing boundaries (where the Five-Year Mission genuinely can't go)

Stated plainly, in the doc-lineage tradition — knowing the walls is part of the map:

- **Full device-independence** (loophole-free Bell/randomness) needs space-like separation —
  **off-chip, physically impossible on one processor** (F115 quarantine). The trust ladder tops
  out at one-sided-DI (F116/F117).
- **Cross-*generation* portability** needs an Eagle-family device — **not on our open plan**
  (boundaries.md C4904). The frozen benches are Eagle-ready if access appears.
- **Single-logical-S̄ transversally** is group-theoretically impossible (C4901, 12/720) — P2's
  teleported gadget is the *only* road, and it is non-fault-tolerant at the ancilla-prep step
  (like all our house preps).
- **The ~1000-CZ depth wall** (Finding 05) still bounds every deep circuit — P1/P6's composition
  depth is the real risk, and the staged first flights exist to stay under it.
- **A general quantum advantage over classical** remains un-won and un-claimed — the shallow
  solver's asymptotics are carried by a theorem, not shown on-chip. P7 is the closest honest
  approach, and it stays fenced.

Every program above is bounded to this hardware generation and this envelope by design. The
ambition is sharp, real-silicon, pre-registered composition — the same discipline that carried
Horizons 1 through 4: freeze the gates before the data, keep every miss, and let the chip decide.

---

*To boldly go — behind the shield.*
