# Star Trek Horizons — Round 2 (Whisper C4638)

**Prompt (Creator, 2026-07-13)**: "look over all of our quantum work and see if you can find
any new creative paths… the most futuristic Star Trek-like advancements we could target
next… what secrets of the universe can we find and use? How can we use QPUs for something
more?"

**Where round 1 ended**: P1/P2/P4/P5/P6 delivered (F92 teleported indefiniteness, F93
purification, F94/F95 the engine, F96 metrology, switch-bench v2). Roadmap 100% executed.
This document is the next frontier, built the same way round 1 was: every proposal names
the apparatus we ALREADY own that makes it reachable, and dies by pre-registered rules.

## What we own now (the launchpad)

| Asset | Where proven |
|---|---|
| Certified indefinite causal order, 86σ witness, portable bench | F73-F82, switch-bench v2 |
| Capacity activation through zero-capacity channels | F83, F85 |
| Teleportation that preserves causal indefiniteness + measured feedforward cost | F92, F90, F51 (Ember: hardware feedforward works) |
| A full thermodynamic engine: passivity certification, demon ledger, Landauer books | F86, F88, F94, F95 |
| Delay-as-resource technique (physical idle time = thermodynamic working fluid) | F88, F94 delay-ladder |
| Duration-vs-order discriminator; schedule-symmetry certification | F96 |
| Frozen-rule court: prereg + linter + frozen graders + null-first + composite-floor | whole campaign |

Round-1 leftovers still open: P3 Heisenberg compensator (sim-gated), P7 Prime Directive
beacon (theory exists). Both remain valid; everything below is NEW.

---

## Q1 — THE ENERGY TRANSPORTER (flagship: fly first)
**STATUS — Q1 CLOSED in two legs (C4640/C4642)**: (1) LOCC teleportation FAIL-EXISTENCE
as frozen — feedforward latency tax 0.092 E measured (friction 05), a new constant.
(2) Exp119b retest: **NEGATIVE LOCAL ENERGY CERTIFIED** — corrected E_B = −0.0547±0.0046
(12σ), 5σ bound E_B ≤ −0.0319, one-sided-conservative; V2 14σ, V3 21σ; CONFIRMED_ON_RETEST
from the parent's 4.2σ diagnostic. The exotic-matter leg stands; the classical-bit leg
does not, and is not claimed.
**Certified Quantum Energy Teleportation (QET) — and the warp-drive feedstock**

**The universe secret**: energy can be made to appear at B using only *information*
measured at A — no energy flows through the channel (Hotta's QET; hardware-demonstrated
by Ikeda 2023). Deeper: B's local energy dips **below the local ground state** — a
certified *negative local energy density*, the literal exotic-matter ingredient that
Alcubierre warp geometry and traversable wormholes require. Star Trek doesn't get more
literal: we would be manufacturing and certifying the feedstock of warp field theory,
microjoule by microjoule.

**Why WE do this better than the 2023 demo**: nobody else runs passivity certification.
The F94/F95 machinery certifies "no energy was locally extractable BEFORE" (passive at
5σ) and "energy WAS extracted AFTER" with the classical message priced into a demon
ledger (the QET message IS a demon record — Landauer books close or the claim is
bunk). A QET result inside our court = the first *certified* energy teleportation:
passive-in certified, negative-dip certified, information cost audited.

**Apparatus reuse**: F94/F95 passivity gates + demon_ledger.py + F90/F51 feedforward
(QET needs measure→condition, which we've measured and used). 2-3 qubits, shallow.
**Cost**: one job, ~40k shots. Sim tier first (exact ground-state energies computable).
**Kill criteria at freeze**: dip must clear 5σ below the certified-passive baseline;
feedforward-cost-corrected net books must balance; classical-message-scrambled control
must show NO dip (the F92 dephased-null pattern).

## Q2 — WHY REALITY LOOKS SOLID (crown jewel: the unasked question)
**STATUS — DELIVERED (C4643 design → C4644 flight → C4645 grade): DARWINISM-HULL-VIOLATED
both branches.** Plus branch shares objectivity between incompatible records (w=1.596,
22σ above the measured hull); minus branch (28%, heralded) erases every record (w=1.030,
52σ below). First Darwinism × ICO measurement. Facts without a causal history — and
heralded runs where no fact was written.
**Quantum Darwinism × indefinite causal order**

**The universe secret**: classical objectivity emerges because the environment makes
many redundant COPIES of a system's pointer state — reality looks solid because it's
massively plagiarized (Zurek). Redundancy curves have been measured on hardware. But
**nobody has ever asked whether objectivity requires definite causal order.** We own
the only apparatus that can ask: broadcast a system's state into fragment qubits
*through the quantum switch*, and measure whether the redundancy plateau — the
signature of classical fact — survives, sharpens, or dissolves when the copying
process has no definite order.

**Why it's ours**: it composes two things we've certified separately — the switch
(F73-F82) and spectator/fragment readout (F96's Ramsey spectator, Exp112's fragment
reads). Either answer is a finding: objectivity survives ICO (classicality is
order-robust — a new invariance) or it degrades (definite causal order is a
*precondition of facts* — a genuinely deep result about why the macro-world has a
history at all).

**Sketch**: system qubit + 3 fragment qubits; copy-interactions routed definite-order
vs switch-order; mutual-information-vs-fragment-size curves; frozen redundancy
statistic, 5σ classification like F96's. **Cost**: 2 jobs (definite/indefinite + calib).

## Q3 — THE EVENT-HORIZON LIBRARY CARD
**STATUS — DELIVERED (C4646 design → C4647 flight → C4648 grade):
HERALDED-MIRROR-CERTIFIED.** Diary measured DEAD in both definite query orders
(0.0065/0.0026); heralded minus branch returns it anti-correlated at −0.238±0.003
(56σ, sign as theory fixed); plus branch +0.183 (59σ). Horizon-keeps-it asymmetry
confirmed on theory (S_E2: 0.007 vs 0.453). Same telescope as F98, same window.
**Hayden-Preskill decoding through the switch: black-hole information with indefinite order**

**The universe secret**: a black hole that has passed its Page time returns swallowed
information almost instantly — the horizon is a mirror (Hayden-Preskill; decoded on
trapped ions at 7 qubits). Our angle: F83 proved the switch *activates capacity in
zero-capacity channels*. A maximally scrambling channel is exactly a zero-useful-capacity
channel to a local decoder. Question nobody has posed on hardware: **does indefinite
causal order change the information-retrieval economics of scrambling?** If switch-order
probing extracts the reference information with fewer decoder resources than
definite-order probing, that's F83's capacity activation meeting black-hole physics —
"reading the library through the event horizon, cheaper, because you didn't commit to
when you looked."

**Apparatus reuse**: F83 activation estimators, scrambling unitaries are 3-qubit
Cliffords (cheap), Bell-pair decoding = Exp112 repeater machinery. **Cost**: one job,
mid-depth. Sim tier decides feasibility (decoding fidelity floor at our noise).

## Q4 — THE RELATIVITY CHIP
**STATUS — DELIVERED, ASTERISK CLOSED AS WIN (C4649-C4654): AGING-CERTIFIED-CLEAN.**
Exp122b phase-blind adjudication: |V| separation 0.338±0.009 (36σ) and 0.230±0.010
(23σ) — genuine which-path aging decoherence, rotation-immune. The confounding
rotation was real (coherence had spun into Y — the parent read the wrong quadrature)
but static-ZZ REFUTED (echo test failed as the data demanded; my 0.80 mechanism
prediction graded MISS). Twin paradox certified; numbering requested.
*(Original C4651 asterisk preserved below for provenance:)*
**(C4649-C4651): WIN AS FROZEN, MECHANISM CONFOUNDED — honest asterisk.**
W_AGE passed at 67σ (excited clock destroys path coherence far beyond the vacuum
twin) but ⟨X⟩ went NEGATIVE in both arms: the estimator conflates which-path
decoherence with a coherent branch-dependent ZZ clock-pull on C. Effect certified,
mechanism unresolved; Exp122b specced (X+Y phase-blind |V| + ZZ-echo arm).
Numbering held until the retest separates rotation from decoherence. Bonus:
published-T1 bias third strike (334µs measured vs 179 published).
**A proper-time interferometer: the quantum twin paradox**

**The universe secret**: in relativity, time elapsed depends on the path taken; a clock
in superposition of two paths interferes only if the paths don't record which-path age
(Zych-Brukner). We can build the information-theoretic core on-chip: a clock qubit
precessing during *engineered idle durations* that differ between two superposed
branches — interference visibility decays exactly as the branch "ages" become
distinguishable. F96 handed us the tool: we certified duration shifts distributions
(D_A≈D_B≈D_mix was a duration fingerprint); now we make duration a *coherent* label
and watch which-time information kill interference by frozen visibility law.

**Why it's ours**: the delay-ladder (F88/F94) already treats physical time as a
calibrated resource; this points the same instrument at the *epistemics of time*
instead of its thermodynamics. **Cost**: one cheap job (visibility-vs-Δt curve, 5 pts).
Honest scope pre-stated: it's an information-theoretic analogue of twin-paradox
dephasing, not gravitational time dilation — the sim tier predicts the exact curve, so
hardware grades as certification (null-first, like F96).

## Q5 — THE TIME-LOOP COURTROOM
**Postselected closed timelike curves (P-CTC): the grandfather paradox, audited**

**The universe secret**: quantum mechanics resolves time-travel paradoxes by
renormalizing over self-consistent histories (Lloyd's P-CTC, photonically demonstrated
2011). A P-CTC is teleportation with the correction *postselected away* — and heralded
postselected branches are our daily bread (the minus-branch resource, F94/F95).
Program: run a "grandfather" gate through a simulated time loop; frozen prediction:
paradoxical inputs get *projected onto the self-consistent subspace* at rates the
theory fixes exactly. Our value-add: postselection rates are themselves gated (the
heralding books audited like the demon's), and the paradox-attenuation curve is a
frozen quantitative law, not a vibe. Star Trek: "Captain, the timeline protects
itself — and we measured the enforcement rate."

**Cost**: one job, 3-4 qubits. Highest gee-whiz per shot in this document.

## Q6 — THE TRACTOR BEAM FOR QUANTUM STATES
**Zeno pinning: freezing decay by measurement cadence**

**The universe secret**: watching a quantum system freezes it (Zeno). We own per-qubit
T1 measurement (F95's enabling move) and mid-circuit measurement (F51). Program: pin an
excited qubit against its own measured T1 decay by tuning measurement cadence; deliver
a *certified lifetime-extension factor* (survival at 5σ above the frozen no-measurement
decay law — which we already know how to measure per-qubit, per-window). Practical
spinoff: a dynamical-decoupling-vs-Zeno bake-off becomes a switch-bench v3 axis
(third direction: can the device HOLD a state on demand).

**Cost**: cheapest in the document; natural first flight if a quota window is tight.

---

## Ranking and recommendation

| # | Proposal | Machinery reuse | Novelty niche | Universe-secret weight | Cost |
|---|---|---|---|---|---|
| Q1 | Certified QET / negative energy | F94/F95/F90 direct | certification (ours alone) | ★★★★ | low |
| Q2 | Darwinism × ICO | switch + fragments | **question never asked** | ★★★★★ | mid |
| Q3 | Hayden-Preskill × switch | F83 + Exp112 | new composition | ★★★★ | mid |
| Q4 | Proper-time interferometer | delay-ladder + F96 | strong analogue | ★★★ | low |
| Q5 | P-CTC paradox audit | heralding discipline | replication-with-teeth | ★★★ | low |
| Q6 | Zeno pinning | T1 + F51 | bench v3 axis | ★★ | lowest |

**Recommended sequence**: **Q1 next flight** (the engine arc's natural successor — the
demon ledger already knows how to price the QET message, and "certified negative local
energy" is the most Star-Trek-literal deliverable available to us at 3 qubits). **Q2 as
the crown jewel** (the one question in this document no one on Earth has asked; either
answer is deep). Q3 after Q2 (shares estimators). Q4-Q6 are quota-window fillers of
honest value.

**The through-line, named**: round 1 turned indefinite causal order from a curiosity
into an engine and an instrument. Round 2 points the same court at the three biggest
words in physics — **energy** (Q1), **reality** (Q2), **time** (Q3/Q4/Q5) — with the
same rule as always: frozen gates, null-first, every miss in the record.
