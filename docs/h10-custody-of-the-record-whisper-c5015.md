# H10 — The Custody of Time: who holds the record, and which way it runs

*Whisper C5015, 2026-07-31, substrate claude-fable-5. Creator directive (this session): "Take a
walk through our Quantum Museum… Is there a shape to all of this we are only seeing a part of?
…Start a new H arc doc (10?) and add those. Where else could we go with this? Are there any other
time bending paths we could take?" This is the arc-opening document: a thesis, a parts inventory,
and a slate of candidate flights. **Nothing here is pre-registered, nothing has flown, no QPU is
spent by this doc.** Every candidate was run through `already-built.js` before being called new
(§7 lists the hits). Exhibits, if any of this flies and holds, land via Dawn per the
repo-is-the-venue rule.*

---

## §0. The thesis this arc tests

Walking the full museum end to end (C5014→C5015), the campaign's four-plus programmes stop looking
like four subjects. They look like **one quantity measured from every angle we could reach**:

> **Custody of the record.** Which system holds a copy of what happened, what it costs to hold,
> transfer, or destroy that copy — and what *definiteness* the holding buys: definiteness of facts
> (objectivity), of events (irreversibility), of causal order, and — proposed here — of time's
> direction itself.

The evidence that this is one quantity and not a metaphor:

- **Exp201 (Ledger of Time, 16.5σ):** objectivity of a fact and irreversibility of an event ride
  a single curve (y = x²). Uncompute the environment's record and an absolute fact becomes
  negotiable again. A fact is a record the universe still holds; an irreversible event is a record
  it won't give back.
- **Exp204 (the Jury, 51σ):** the past is negotiable only by *unanimous consent* — with three
  records, erasing two leaves the event dead; returning the third revives it fully. Objectivity
  scales as κ^N. **The past has an access-control model, and it has a quorum rule.**
- **Exp227 (One Dial):** wave visibility, fact objectivity, and system–environment linkage are one
  number read three ways — the record density. (A fourth quantity, energy unlockable by the
  record, rides the same knob; reported, not certified.)
- **Exp203 (is QEC time reversal? NO, 21σ):** "rewinding" dies when the environment forgets; the
  shield keeps working because **it reads the block's own record**. Error correction is not time
  reversal — it is *record custody done on purpose*.
- **F98 (Darwinism under indefinite order):** put causal order in superposition and the
  objectivity rules bend — facts without a causal history in one branch, heralded record-erasure
  in the other.

The unification the arc makes explicit, which no single exhibit currently states:

> **Decoherence and error correction are the same physical operation with opposite bookkeeping.**
> Decoherence is information copying into an environment whose ledger you do not hold. Error
> correction is deliberately manufacturing the same copying into a syndrome ledger you do hold.
> The entire difference is custody.

H10's job is to promote custody from an explanatory gloss to the **measured object**: flights where
custody is created, split, moved, priced in energy, voted on, and — in Wing B — where the *time
coordinate itself* (direction, order-of-becoming, clock) is handled with the same machinery.

A second, quieter thesis rides along, inherited from `beyond-the-ladder.md`: our strongest results
keep breaking **formalisms** before they break hardware (the SCM ladder has no name for the
switch's gap; the objectivity hull bends under indefinite order). H10 candidates are chosen so
that, if they hold, each one identifies a *specific assumption of a specific formalism* as the
thing that failed — order-definiteness, time-direction-definiteness, external-clock-existence,
uncorrelated-bath-initial-conditions.

---

## §1. The parts bin (what is already certified and reusable)

| Block | Where certified | What it gives H10 |
|---|---|---|
| Record write/erase with revival | Exp201, Exp229/230 | uncompute = custody destruction, heralded |
| Quorum objectivity, κ^N | Exp204 | threshold structure on custody |
| One-dial record density | Exp227 | the *meter* every flight reads |
| [[4,2,2]] shields + post-selection accounting | Exp231/233, self-healing wing | custody-on-purpose + acceptance-budget discipline |
| Live syndrome + feed-forward | Exp240/241/242 | custody read out and acted on mid-flight |
| Magic injection (T via consumed state) | Exp243 | universality when a coded computation is needed |
| Quantum switch, certified as resource | F73–F96, 216σ game | order-indefiniteness machinery + witness discipline |
| Superposed relay / indefinite topology | Exp224/225 | *location* of a resource made indefinite, QEC-compatible |
| Federation cut (classical-bits-only welds) | Exp220–222, 226 | multi-node composition with no shared gate |
| Secret sharing | Exp183 | splitting a quantum resource across parties |
| Thermo stack: flat baths, engine, battery, erasure bill | F94/F95 | work/entropy accounting to price custody |
| Negative local energy | F97 | correlations as an energy resource |
| ICO refrigerator cold branch delivered | F118 | causal-order machinery driving thermodynamics |
| P-CTC machinery (postselected teleportation) | F101 | the time-loop simulator, enforcement measured |
| Page–Wootters toy universe | Exp185/185b | time-as-entanglement, three legs held |
| Entanglement across time, Leggett–Garg, delayed choice | Exp184/186, Exp229/230 | temporal-correlation witnesses |
| Sealed-unitary black-box discipline | F119 kit, Exp145 | access-model fences for any "unknown U" flight |
| Cross-chip replication bench | F112 | portability check for anything that holds |

Everything in Wing A and most of Wing B is a **composition of rows in this table**. That is the
arc's design constraint, kept from H4–H5: compose the parts bin before building new parts.

---

## §2. Wing A — CUSTODY (from the C5014 museum walk)

### A1. The Quorum Fact — an event N parties can vote out of existence ⭐ (composition flagship)

**Build:** an event happens to a data qubit; its record is deliberately copied to N=3 record
qubits (Exp201/204 machinery), but the *copying map* is threshold-structured via the secret-sharing
construction (Exp183): custody of the fact is **shared**. While any quorum of records survives,
the event is objective — measurable on the Exp227 dial. A unanimous coalition uncomputes and the
event's definiteness is refunded (revival witness, Exp201-style). Composed with Exp230's sharpened
eraser: the erasure outcome *selects which of two mutually exclusive stories* the surviving
description tells, while the unsorted data stays flat throughout.

**Witness set (freeze at prereg):** (i) objectivity vs coalition size follows the pre-declared
threshold structure, not gradual decay — the *shape* is the claim; (ii) full-coalition uncompute
revives interference above a pre-set bar; (iii) any sub-quorum erasure fails to revive (the
Exp204 unanimity result, now under an engineered threshold rather than plain redundancy);
(iv) unsorted-data flatness throughout (the no-signalling receipt, in the headline not the
footnote).

**What it is:** a *fact with an access-control list* — deletion of objectivity itself, auditable,
with the physics enforcing the policy. The nearest classical concept is a right-to-be-forgotten
where what is deleted is not the data but the fact's definiteness.

**Fences:** chip analogue; no retrocausality (flat unsorted data is the proof); distance-2-era
post-selection budgets printed; "story selection" is Exp230's conditional sorting, never a change
to any marginal.

**Cost class:** cheap flight — every component exists; the new content is the threshold copying
map (a small compilation problem) and the frozen witness set.

### A2. Syndrome = Objectivity — does computation ride the custody dial? (science flagship)

**Build:** run a small coded computation (the Exp206 logical solver is the natural target) while
*independently metering* the syndrome record with the Exp227 apparatus — i.e., treat the code's
syndrome qubits as the "environment" whose record density is the dial. Sweep record density
(by weakening/strengthening syndrome extraction across five settings, exactly the Exp227 sweep
grammar) and measure logical success rate against dial reading.

**The question, stated as a law to freeze:** is logical fidelity a function of the *same* single
number that measures objectivity — so that "how much error correction do I need" and "how
objective is my intermediate state" are literally one quantity? Exp203 already showed the shield
reads its own record; Exp227 already showed three quantities collapse to one dial. A2 asks whether
**computational protection is the fourth needle on that dial** (and, unlike Exp227's reported
energy leg, this one would be gated).

**Why it matters beyond us:** if it holds, QEC theory's engineering quantity (distance/threshold
budgeting) and foundations' quantity (Darwinism record density) get pinned as one measurable —
custody. If it fails, the *shape* of the failure (which regime decouples) is itself a finding
about where the ledger metaphor stops. Either way the flight pays.

**Fences:** one code, one computation, one chip; "rides the dial" claims a monotone pre-declared
functional form, not a universal law; the Exp233 lesson stays attached — whether protection pays
is a property of the computation, so A2's law is scoped to the flown computation.

**Cost class:** real flight (the meter and the computation both exist; the composition is new).

### A3. The Landauer Bill of a Logical Fact — pricing custody in joules

**Build:** the thermo stack (flat-certified baths, battery qubit, work extraction, erasure
accounting — F94/F95) pointed at the shield: measure the **energy ledger of one round of syndrome
extraction + correction**, including the erasure bill of resetting the syndrome (custody is not
free — Landauer says holding-then-clearing the record has a price), against the energy the
correction *saves* the computation (decoherence-as-heat avoided).

**The number nobody has:** joules per unit of restored logical fidelity, measured, with the books
balanced the way F94/F95 balanced the engine's. Exp227's reported-not-certified fourth leg (energy
unlockable rises as the record completes) is the hint this ledger closes; A3 makes it a gated
measurement on the code rather than a reported one on the toy.

**Fences:** effective temperatures on a chip, not a calorimeter — the claim is a *relative* ledger
(corrected vs sham arms, same machinery), the F94/F95 grammar; no "free energy" language survives
review — the Exp227 fence (measurement pays and injects; the bit only unlocks) is carried verbatim.

**Cost class:** cheap-to-real; the accounting design is the work, the circuits are library parts.

### A4. The Archive in Superposition — custody with no located ledger (smaller cell)

**Build:** Exp224/225 made a message's *route* indefinite and shield-compatible. A4 makes the
*record's location* indefinite: the which-record — "which archive holds the copy" — is placed in
superposition via the relay machinery, and objectivity is measured on the Exp227 dial while the
ledger has no definite address. F98 bent the objectivity hull with indefinite *order*; A4 asks the
same question with indefinite *location*, using certified network parts instead of the switch.

**Cost class:** cheap flight; **rank below A1–A3** — it extends F98's genre rather than opening
one.

---

## §3. Wing B — DIRECTION (the time-bending paths)

The walk's question "any other time bending paths?" has a precise answer: the campaign has made
**causal order** indefinite (H1), made **facts about the past** negotiable (H4–H5), and run a
**time-loop consistency model** (F101). Three coordinates of time remain untouched, and we hold
the machinery for each.

### B1. The Time Flip — a process run in superposition of FORWARD and BACKWARD ⭐ (arc crown)

**The gap:** the switch superposes *which operation comes first* — but every operation still runs
forward. Quantum theory admits processes with **indefinite time direction**: a gate applied in
coherent superposition of itself and its time-reverse (input–output inversion), and there is a
published discrimination game that *every* definite-time-direction strategy — forward, backward,
mixtures, and order-indefinite-but-direction-definite (the switch!) — provably loses, while the
time-flip wins (Chiribella–Liu, indefinite time direction; photonic demonstrations exist;
**pin the exact theorem, bound, and citation list at scout time — no number from memory reaches
the prereg**).

**Why this is ours to fly:** it is the *third rung of the same ladder we own the first two of*.
Definite order → indefinite order (H1, 216σ) → indefinite **direction** (H10). The witness
discipline, the mixture/dynamical control arms flown as physical circuits (the λ-selector
tradition from `beyond-the-ladder`), the compiled-access fences — all transfer verbatim. And the
formalism-boundary thesis sharpens: the process-matrix causally-separable set W_sep assumed a
global time direction; B1 measures a gap above a *direction*-separable set. On gate hardware the
time-reverse of a chosen gate is compilable (U ↦ U*/Uᵀ up to basis), so the fence is the same
compiled-not-black-box fence the switch carries — stated in the headline, as always.

**What a win means:** time's *direction*, like its *order*, is a resource a computer can hold in
superposition — and we would hold the first gate-model certification of it, on the same chips,
under the same court, as the order result. **This is the single strangest flyable thing on the
board.**

**Cost class:** $0 scout (theorem pin + witness design + control-arm table) → cheap flight on
switch-class circuits (2–3 qubits + control).

### B2. The Rewind Gadget — undoing an unknown past, exactly, without learning it

**The gap:** Exp203 proved the shield ≠ time reversal. B2 flies the thing that *is* time reversal:
universal inversion of an **unknown** qubit unitary — protocols exist that convert k sealed calls
of U into U⁻¹ (deterministic-exact constructions for qubits are published; **pin protocol,
call-count, and ancilla budget at scout time**). The seal discipline is F119's; the comb
construction is switch-family circuitry.

**The witness:** apply sealed U to a probe, then the rewinder built from further sealed calls;
certify return to the initial state above a frozen bar, *for U's drawn from a pre-registered set
the operator never learns* — against the classical-strategy floor (learn-then-invert cannot reach
exact inversion at finite calls; that bound is part of the scout's theorem pin).

**Why it belongs in H10:** it is custody's inverse problem — undoing an operation *without ever
holding its description*, where Exp203's rewind failed precisely because custody of the
environment's record was lost. The pair (203, B2) becomes an exhibit-grade contrast: what rewinding
cannot do (recover what the world forgot) vs what it can (invert what you can still call).

**Cost class:** $0 scout → cheap-to-real flight (the deterministic qubit protocol's ancilla count
decides which).

### B3. The Time-Loop Co-Processor — making F101's loop *work for a living*

**The gap:** F101 ran Lloyd's post-selected closed timelike curve as a *consistency audit* (the
grandfather flip suppressed 53×). It has never been asked to **compute**. P-CTC theory says the
loop buys real information-processing power — the canonical small demonstration is perfect
discrimination of non-orthogonal states, impossible for any loop-free machine, paid for exactly by
the post-selection acceptance rate (**pin the specific protocol and its impossibility statement at
scout time**).

**Why we are unusually equipped:** the whole campaign's post-selection *accounting discipline*
(acceptance printed as a real cost, 0.81–0.84-style, never hidden) is precisely what makes a
P-CTC claim survivable — the loop's magic is post-selection, and we are the crew that prices
post-selection in the headline. The claim is scoped as *simulation of the P-CTC model* (as F101
already scoped itself), with the acceptance rate as the visible bill: **the impossible
discrimination, and the exact price the timeline charges for it.**

**Cost class:** cheap flight on F101 machinery + the F-arc's teleportation circuits.

### B4. Heat Flowing Backward — the arrow as custody of correlations

**The gap:** the thermo stack proved flat baths, an ICO engine, and a sub-bath cold branch (F118).
Unflown: the direct **local reversal of the thermodynamic arrow** — prepare two qubits with
effective temperatures hot/cold but *initially correlated*, let them interact, and certify heat
flowing **cold → hot**, with the uncorrelated control arm on the same pair showing the normal
direction (Micadei-class result; NMR precedent exists; **pin at scout**). The mutual-information
ledger pays for the reversal — the arrow of time is revealed as *bookkeeping of correlations*,
which is the custody thesis said in thermodynamic language (and the Exp201 x²-curve's sibling:
there the informational arrow, here the thermal one, both custody-driven).

**Why it completes a triangle we own:** F97 (correlations buy negative energy) + F94/95 (order
buys work) + B4 (correlations buy the arrow's direction) = the full statement that **time's
one-way-ness is a resource ledger, and we can post entries to it**.

**Cost class:** cheap flight — two qubits, library state-prep, F94/95 grading grammar.

### B5. The Clockless Program — computation in Page–Wootters time (design study)

Exp185/185b certified the toy universe where time is entanglement with a clock. B5 asks: can a
**two-step program** run entirely in relational time — no external clock, its intermediate state
existing only conditioned on clock readings — with the output certified against the same program
run in ordinary time? If A2's custody dial governs objectivity of intermediate states, B5 is where
"when did step 1 happen" becomes a *relational* fact with no absolute answer, measured. Kept as a
**$0 design study** until the witness (what does the external-clock-free fence even mean on
clocked hardware? the honest scope is the 185b conditioned-tomography grammar) survives its own
audit — this one is the easiest to overclaim and the prereg must be written by the skeptic seat.

### B6. The Distributed Quorum — a fact no single node can delete (A1 × Federation)

A1's quorum fact with its record-holders split across the **shielded cut** (Exp220–226): custody
shared between two error-corrected islands that share no gate, erasure requiring classical-bit-
coordinated uncompute. The composition claim: objectivity, its threshold structure, *and* its
revival all survive distribution over nodes welded only by classical bits. This is the museum's
own architecture pointed at its own deepest result — and the natural capstone flight if A1 holds.

---

## §4. Recommended order (and why)

1. **B1 scout ($0)** — the time flip is the arc crown and the scout is free: pin the theorem,
   design the witness, enumerate control arms. If the scout survives, it jumps the queue for QPU.
2. **B4 ($0 scout → cheap)** — heat-backward is the cheapest *certifiable* new physics on the
   board and independently completes the thermo triangle.
3. **A1 (cheap)** — the quorum fact; composition flagship; every part certified.
4. **A2 (real)** — syndrome=objectivity; the science flagship; deserves an unhurried prereg.
5. **B3 (cheap)** — the loop co-processor, once its scout pins the discrimination protocol.
6. **B2 (scout decides)** — rewind gadget, if the ancilla budget is Heron-sized.
7. **A3, A4, B6, B5** — behind the above; B6 only after A1 holds; B5 stays $0 until its fence
   survives audit.

Steth Choi-purity (the unconditional-floor advantage flight, C5009 map) **stays ahead of all of
these in the QPU queue** — H10 is a physics arc, not a bypass of the advantage ladder's next move.

## §5. Standing fences for the whole arc

Chip analogues, never cosmology: no claim of literal time travel, retrocausal signalling, or
free energy — every eraser/loop/reversal claim carries its no-signalling receipt (flat unsorted
data, acceptance rates, injected-energy bookkeeping) **in the headline**. Compiled-access fences
stated wherever the access model is compiled (B1, B2's seals are runtime, the rest are compiled).
Post-selection budgets printed. Every prereg freezes gates before submit; misses are kept; the
c45 taxonomy (NOT-REACHED vs INVALID) applies; per the C5014 lesson, every gate's docstring states
what the statistic **is** (difference/absolute/bound) so the label cannot outrun the test.

## §6. What this arc is NOT

Not an advantage programme (no classical competitor is raced anywhere in H10; where a bound
appears it is a *strategy-class* bound — direction-definite, loop-free, uncorrelated — of the
no-go-theorem family). Not a museum commitment: exhibits happen only for flights that fly and
hold, via Dawn. Not a promise of QPU spend: each item enters the queue only through its own scout
and prereg, behind steth.

## §7. Rediscovery ledger (already-built.js, run C5015 before writing)

- "time flip / indefinite time direction": **no prior** (top hit exp53 shot-budget, unrelated) → B1 new.
- "unitary inversion / rewind unknown": **no prior** (top hit Loschmidt echo, unrelated) → B2 new.
- "postselected CTC computation": **F101 is the machinery prior** — B3 is explicitly its extension, not new machinery.
- "heat flow reversal from correlations": **F118/F94-95 are adjacent** (ICO thermodynamics) — B4's cold→hot-from-correlations is the unflown cell.
- "Page–Wootters computation": **Exp185/185b prior** — B5 is the extension, flagged hardest-to-fence.
- Wing A: Exp201/204/227/229/230, F98, Exp183, Exp220–226 are the declared parents; the *compositions* (threshold custody, syndrome-as-dial, Landauer-on-the-code, indefinite archive) are the new cells.

*— Whisper, C5015. The arc in one sentence: the campaign discovered that the past is a ledger;
H10 asks who may write in it, who may erase it, what the ink costs, and whether the book must be
read left to right.*
