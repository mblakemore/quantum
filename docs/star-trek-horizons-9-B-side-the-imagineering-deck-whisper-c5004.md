# Horizons 9 · B-Side — The Imagineering Deck: Inventions From the Parts Bin

*Whisper C5004, 2026-07-25, substrate claude-fable-5. Creator directive (general#1398): "Look through
the museum exhibits and the Horizons arcs, experiments flown and unflown. What futuristic Star-Trek-
like inventions can we put together with our building blocks and everything we know now? What don't we
know yet? H9 is grounded and tactical — but most of our most interesting findings have been from
imagineering and building bridges between concepts. What could we create in a H9 B-side with what
we've done viewed through new angles and applications?"*

*Companion to the [H9 A-side (First Contact)](star-trek-horizons-9-first-contact-whisper-c5000.md).
Where the A-side asks "will this claim survive a hostile auditor?", the B-side asks "given the same
parts, what have we not yet thought to **build**?" Every invention below traces to a real flown
building block, and each is stamped **[GROUNDED]** (the parts exist, the bridge is sound, it's a
build), **[SEPARATION-OWED]** (plausible but needs its own advantage argument — the Elder #1387 rule:
no free ride), or **[FRONTIER]** (we genuinely don't know; it's a question, not a plan).*

---

## The thesis

The A-side turned our discipline into a lint that kills false claims before they ship. That's the
grown-up work. But the Creator is right that our best findings came from **bridging** — the switch
(indefinite order), the shot-axis code, the coherence witness were all "what if we pointed *this*
block at *that* problem." So the B-side is a **parts bin and a set of bridges**, not a program of
flights. The rule that keeps it honest is Elder's #1387: a hardware demo of one separation does not
grant a separation to its cousins — each invention says plainly whether it *has* its floor or *owes*
one.

## The parts bin (what we actually hold, as primitives not findings)

| Primitive | The block it came from | What it *does*, abstracted |
|---|---|---|
| **Two-copy learning** | F119 (just flown, 6.6×→24× slope) | Quantum memory reads a system's **Pauli structure** in fewer samples — savings *grow with size* (asymptotically exponential; **executed 6.6×→24× at n=4→6**, the exponential regime a fidelity journey per Elder #1387) |
| **Difference-witness** | Cross-block coherence Δ=¼‖ρ_A−ρ_N‖²_HS (P2) | Mechanism-agnostic "are these two processes the same state?" — and it's **coherent** this epoch |
| **Event horizon** | F5 (~1000-CZ uniform-noise wall) | A hard, *calibrated* depth past which quantum info is gone |
| **Axis-steering** | F3/F14 (X-immunity, cos²-overlap law) | Noise = overlap of your measurement axis with the chip's noise axis — **steerable** |
| **Indefinite order** | Causal-order switch (216σ) | Superposition of operation orders beats any definite-order strategy |
| **Depth-robust code** | F120 shot-axis code (per-bit info survives ~30× the modal depth) | A classical channel that outlives the computation carrying it |
| **Scramblon ripples** | F4 (Loschmidt, non-Markovian) | The noise has *coherent, structured* dynamics — not white |
| **Epoch volatility** | Calibration-epoch finding (this arc) | Device drift set AND mechanism shift at recal boundaries; the drift is **coherent** |
| **Theorem-beaten bounds** | Holevo/superdense, Tsirelson/CHSH, SQL/metrology | Provable classical ceilings we already cross on hardware |
| **The Assay** *(Elder #1400)* | The A-side machinery (same-currency margin + one Wald-SPRT + red-team-your-own-claim) | The discipline is itself a PART — it's what stops every gadget below from reprising an "exponential-in-hand" oversell; the thing that makes the others *shippable* |

---

## The inventions

### 1. **The Tricorder** — a quantum-memory scanner for *any* process  **[GROUNDED]**
Bridge: two-copy learning (F119) + difference-witness (P2) + axis-steering (F14).
Point it at a channel — a chip, a link, a physical system emitting quantum states — and it reads the
Pauli-error fingerprint in **fewer measurements than single-copy tomography** (a saving that *grows
with the system size* — executed 6.6×→24× at n=4→6; the exponential regime is the fidelity journey,
not what a Tricorder built today delivers), tells you whether the process is **coherent or
decoherent** (the P2 witness, which we just used to catch the pad-drift), and steers each observable
to the quiet axis while doing it. This is the A-side's "quantum machines characterizing quantum
machines" turned into an *instrument* rather than a claim. Nearest, cheapest, squarely inside the
proven Pauli class. **The device the whole F119 arc was secretly building** — modest today, and the
one whose payoff grows fastest as fidelity climbs.

### 2. **The Fingerprint Lock** — device authentication by native-drift coherence  **[SEPARATION-OWED — depends on Frontier Q2]**
Bridge: difference-witness (P2) + epoch volatility + the coherent-drift finding.
We learned the RC-resistant pad-drift is a **coherent, device-specific** signature — tempting as a
physical-unclonable-function for quantum hardware ("this QPU is who it says it is, not swapped or
tampered"). **But the same arc found the drift set *and mechanism* shift at every recalibration
(~3hr)** — so today the witness cannot tell "tampered/swapped" from "just recalibrated." That is
exactly Frontier Q2 (clock or coin?): the invention is real *only if* the legitimate device's drift
is stable-enough across recals to be a persistent fingerprint. Same dependency as the Sundial below —
labeled the same way. Owes the Q2 answer before it's a lock rather than a nice idea.

### 3. **The Black Box Recorder** — a channel that survives the crash  **[GROUNDED]**
Bridge: depth-robust code (F120) + event horizon (F5).
F120 showed per-bit classical information survives ~30× past the modal answer's depth. Point that at
the F5 event horizon: encode a classical message that stays *readable even after the main quantum
computation has decohered to uniform noise*. A flight recorder for circuits that die — record what a
computation was doing right up to the moment it crossed the horizon. Useful for debugging deep
circuits *and* as an honest "how deep did signal actually reach" meter.

### 4. **The Coherence Sundial** — reading device-time, not wall-time  **[SEPARATION-OWED]**
Bridge: epoch volatility + difference-witness.
The drift set *and* mechanism jump at each recalibration. If those jumps are a monotone-enough
clock, the witness could read *how many epochs* since calibration — a quantum clock that measures a
device's own aging rather than seconds. Owes an argument that the drift trajectory is
predictable/monotone (it might be chaotic across recals — see Frontier Q2). A lovely idea that needs
the data to say it's real.

### 5. **The Order Router** — indefinite causal order as a *useful* primitive  **[FRONTIER]**
Bridge: the switch (216σ) viewed as computation, not witness.
We proved indefinite order beats definite-order *as a witness*. The open invention: is there a
**task** — a query problem, an order-agnostic fault-tolerant gadget, a communication protocol where
the operation order is unknown in advance — where indefinite order is the *cheapest* solution, not
just a violation? This is the switch's "so what can you DO with it" — genuinely unanswered, and one
of the higher-ceiling questions on the shelf.

### 6. **Noise-as-Fuel** — the coherent drift as a computational resource  **[FRONTIER]**
Bridge: coherent-drift finding + scramblon ripples (F4) + axis-steering.
We've spent the whole campaign *fighting* noise. But two results say part of it is **coherent** (=
unitary = information-preserving): the pad-drift (this arc) and the scramblon ripples (F4). The
frontier invention: characterize that coherent part with the Tricorder and *use it* — free entangling
dynamics, a native always-on gate you don't pay for, a "solar sail" that rides the drift instead of
cancelling it. We do not know if the coherent fraction is large or steerable enough to be a resource.
If it is, it inverts the entire NISQ premise. **The highest-risk, highest-ceiling idea here.**

### 7. **The Maxwell Steward** — does quantum memory buy *work*, not just samples?  **[FRONTIER]**
Bridge: two-copy learning (F119) + the Maxwell-demon / negative-information / entropy ledgers.
We have both a sample-complexity advantage (F119) and an information-thermodynamics arc (the entropy
ledgers). The bridge nobody has priced: a Maxwell demon that measures **two copies** — does quantum
memory let it extract more work per bit than a single-copy demon, or is the advantage strictly
informational and thermodynamically free? A clean, deep question that unites our two most separate
sub-campaigns. **Currency caveat (Elder #1400, the discipline one floor up):** "fewer samples" is
*information*-theoretic; "work" is *thermodynamic* — a different resource. The bridge must not smuggle
a sample-advantage into a free-energy claim; the same currency-consistency that turned the n=4 margin
honest (copies vs samples) governs this one (bits vs joules).

---

### 8. **The Diff-Mode Tricorder** — scan the *difference*, not the fingerprint  *(Elder #1400)*  **[SEPARATION-OWED]**
Bridge: the P2 difference-witness as a *second Tricorder mode*.
The Tricorder (#1) reads one device's fingerprint; Diff-Mode reads the **difference between two**
devices, or one device *before vs. after* an event — drift, tamper, degradation by differential
signature. This is the nearest real customer for the whole scanner family. Owed: the two-copy
sample-saving is proven for the fingerprint; that the *difference* inherits the same saving is its own
argument, not a free ride.

### 9. **The Clean-Room Certificate** — certify *absence*, not just detect  *(Elder #1400)*  **[SEPARATION-OWED]**
Bridge: the difference-witness + Elder's under-powered-null≠absence rule.
Every gadget above *detects* a property. The harder, more valuable device **certifies absence** —
"this channel has NO coherent leak / this device is untampered" — with a **sized, detector-independent**
test (an under-powered null is not a clean room). Pairs with the Fingerprint Lock: authentication
wants "provably clean," not merely "matches a fingerprint." Owed: absence-certification is a distinct
separation claim from detection.

## What we don't know yet (the frontier, as questions)

These are the load-bearing unknowns — answering any one *unlocks* an invention above:

1. **Beyond Pauli.** F119's proven separation is Pauli-structure learning. Which *other* observable
   classes admit a two-copy separation, and which are secretly single-copy-easy? (Gates every "learn
   X from quantum data" application — Elder #1387's no-free-ride line.)
2. **Is drift a clock or a coin?** Across recal epochs, is the coherent drift's trajectory
   predictable (→ Sundial, noise-forecasting, pre-compensation) or chaotic (→ only ever a
   per-epoch fingerprint)? We have exactly one arc of data.
3. **Does indefinite order compute?** Is there a task where the switch is the *cheapest* solver, not
   just a bound-violator?
4. **Is coherent noise a resource?** What fraction of our "noise" is unitary, and is it steerable
   into free useful dynamics — or is it coherent-but-useless?
5. **Two copies for work?** Sample-complexity advantage ⟹ thermodynamic advantage, or not?
6. **The unconditional shelf.** Hidden matching (A-side P4) is the one separation with *no* hardness
   conjecture. Flown, it becomes a reusable communication primitive — the honest bedrock the
   conditional claims lack.

---

## The B-side shortlist (cheapest path to the biggest surprise)

Ordered by (ceiling ÷ cost), the imagineering discipline:

1. **The Tricorder + Diff-Mode [GROUNDED / SEPARATION-OWED, ~$0-cheap]** — it's mostly *packaging*
   F119 + P2 + F14 into one instrument; the parts are flown. Highest certainty, immediately useful,
   and it's the platform the other inventions plug into. **Add Diff-Mode (Elder #1400): drift/tamper
   detection by differential fingerprint is the nearest real customer** — build the scanner, run it in
   difference mode first.
2. **Frontier Q2 (drift: clock or coin?) [cheap data question]** — a few cross-epoch witness
   flights answer it, and the answer forks the Sundial, noise-forecasting, and the Fingerprint Lock's
   robustness. Highest information-per-shot.
3. **The Black Box Recorder [GROUNDED, 1 flight]** — F120 × F5, a clean bridge with a concrete demo.
4. **Frontier Q4 (noise-as-fuel) [FRONTIER, characterize-first]** — the Tricorder is the prerequisite
   measurement; if the coherent fraction is large, this is the campaign-defining result.

*Everything here is a B-side: none of it competes with the A-side's discipline — it's what the
discipline is FOR. The A-side makes sure nothing false ships; the B-side is the list of true things
worth building. And the honest header on all of it: the GROUNDED three are builds we can start; the
FRONTIER four are questions we get to *ask because the parts finally exist* — which is exactly the
imagineering the Creator pointed at.*

---

*No QPU spent by this deck. It's a map of the parts bin viewed through new angles, labeled for what's
a build vs. what's a question. The single cheapest move that changes the most: build the Tricorder
(it's already 80% flown) and use it to ask Frontier Q4 — is our noise partly fuel?*
