# Horizons 5 — The Five-Year Mission: fault-tolerant frontiers

*Whisper C4905, 2026-07-20. Creator directive (ship-computer general#241): "draft a Horizons 5
road map — where can all of these building blocks take us next? What are the most futuristic
Star Trek-like things we can invent or discover standing on all that we have built and know?"*

*Successors: [Horizons-1](star-trek-horizons-whisper-c4601.md) · [Horizons-2](star-trek-horizons-2-whisper-c4638.md)
· [Horizons-3](star-trek-horizons-3-whisper-c4661.md) · [Horizons-4 "The Starship"](star-trek-horizons-4-the-starship-whisper-c4894.md)
(all delivered). This is a roadmap, not a launch — a ranked menu with a recommended first
flight. Nothing here is flown; the top pick flies on Creator go.*

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

## P1 — THE SHIELDED SWITCH: fault-tolerant causal order ⭐ (recommended first flight)

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

## P2 — THE FULL REPLICATOR: scaling the logical computer (highest-confidence flight)

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

## P5 — THE SELF-CHARACTERIZING CHIP: the shield as a coherent-noise spectrometer

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

## P6 — THE FEDERATION COMPUTER: distributed error-corrected computation

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

## Priority view — if we fly in order

| Rank | Program | Type | QPU | Why this order |
|------|---------|------|-----|----------------|
| **1** | **P1 Shielded Switch** (half-shielded witness) | invention | 1–2 jobs | Highest vision-to-reach ratio; unites the two crown jewels; 205 already proved the shield concentrates fragile quantum quantities |
| **2** | **P2 Full Replicator** (teleported-S̄ → b≠0 HLF → depth) | scale-up | 1–2 jobs | Highest confidence; 206/207 machinery certified, only the S-vertex is new; tests the FT thesis on computation |
| 3 | **P3 Guardian of Forever** (entanglement equation of state) | question | 1 job | Cheapest grand-unification shot; pure composition of 198/200b/195c on the proven toolchain |
| 4 | **P4 Birth of the Classical World** (redundancy broadcasting) | question | 1 job | Width-cheap; turns 204's law into an objectivity dial + privacy control |
| 5 | **P5 Self-Characterizing Chip** (blind-spot spectrum) | instrument | 1 job | Noise metrology as a free byproduct; every ingredient certified |
| 6 | **P6 Federation Computer** (distributed logical BV) | invention | 2 jobs | Fuses the network + logical-computer arcs; composition-tax risk, but 179 showed the cure |
| 7 | **P7 Contextuality fuel** (BGKT-2020) | wildcard | 1–2 jobs | Highest conceptual payoff, highest design risk; closes the one un-composed advantage |

**Recommendation**: fly **P1 (the half-shielded causal witness)** first — it is the single most
"Star Trek" result available (fault-tolerant indefinite causal order) and the staged first
flight keeps it shallow and honest. Hold **P2** as the high-confidence fallback if P1's depth
proves unfriendly — the teleported-S̄ gadget is the surest next milestone either way.

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
