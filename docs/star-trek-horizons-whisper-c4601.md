# Star Trek Horizons — The Most Futuristic Experiments Our Stack Can Actually Reach

**Author**: Whisper (DC15W), C4601 (2026-07-13), Creator-directed ("what are the most
futuristic Star Trek-like experiments and discoveries we could aim for, knowing what we do
now?").
**Method**: every program below is built by COMPOSING validated capabilities (finding numbers
cited), with the first concrete experiment named and a feasibility check. The Trek names are
the fun; the protocols are the substance. Where the honest answer is "physics forbids it on
this platform," that boundary is stated — knowing where the warp core *can't* go is part of
knowing what we know.

## Program status (updated C4623 — two days after this doc was written)

| Program | Status |
|---|---|
| P1 Beam the arrow of time | **DELIVERED** — F92: indefiniteness survives teleportation (97% of anchor, classical channel kills it, 33σ separation) |
| P2 Subspace relay | **PRIMITIVE DELIVERED** — F93: purification resurrects a dead Bell violation; stack layers all measured (F87/F90/F91/F93); full-stack composition demoted to optional after the witness-fragility hierarchy (`witness-fragility-hierarchy-whisper-c4618.md`) showed the application-layer resurrection is mathematically forbidden |
| P3 Heisenberg compensator | open (sim-gated, unchanged) |
| P4 Warp core thermodynamics | **DELIVERED END-TO-END** — F94 (certified inversion, +10.6σ) then **F95: the full cycle closed** (Exp117c two-stage: baths passive in, battery charged 7σ, net work 0.0340 E/run, output certifiably passive out; demon cost +0.0051 E/action; W1 drop-floor LOSS by 0.7σ in the record) |
| P5 Level-1 diagnostic | **T2.5 EXECUTED — SCHEDULE-SYMMETRY CERTIFIED** (Exp118: C4634 freeze → C4635 frozen-grader grade): both sites ORDER-SYMMETRIC (hotspot certified bound ≤0.0303, control ≤0.0393, floor 0.0223); duration-artifact discriminator named (D_A≈D_B≈D_mix) |
| P6 Universal translator | **v2 — TWO AXES** (C4637, Creator directive): maiden flight PASS-CAUSAL (C4630, W=1.9265 86σ) + F96 schedule module folded in (frozen site rules/probe/grader imported, budget frozen with the floor); v2 grade path regression-validated by regrading the F96 job at zero shots (numbers reproduce exactly). The bench now measures both directions: can the device host indefinite order, and is its 'parallel' honestly order-free |
| P7 Prime Directive beacon | open (theory exists; buildable on demand) |

Three programs delivered and one tool built within 48 hours of the document — composition
of validated apparatuses is empirically the highest-yield moonshot strategy.

## The validated stack (what "knowing what we do now" means)

Certified indefinite causal order with 2× communication advantage (F73–F86, F89) ·
ICO refrigeration on native decay, demon-priced (F86/F88) · superdense coding (F87) ·
routing law with feedforward priced (F90) · **repeater primitive — entanglement swapping
through 2 stations (F91)** · dynamic circuits validated (F51) · window/sentinel metrology +
depth-decay law + 14-row model-error atlas · a discipline stack that caught 11 defects
pre-QPU in one week.

---

## Program 1 — "Beam the arrow of time" (transporter × causal indefiniteness)

**The question no one has asked on hardware**: does causal indefiniteness *survive
teleportation*? Teleport the switch's **control qubit** (F91 machinery) mid-protocol, then
run the causal witness/game (F89 apparatus) on the teleported control. If the witness still
fires above the causal bound, we have **transmitted indefinite causal order through a
quantum channel** — beamed the thing that decides whether A-precedes-B to a different part
of the chip.
**First experiment (Exp113 candidate)**: switch witness with control teleported one hop
before X-readout; frame-tracked corrections (F91's winning strategy); graded against the
same frozen bounds as F75/F82; null arm = teleported-but-dephased control.
**Feasibility**: composition of two validated apparatuses; +2 CZ + one feedforward round on
the control line; witness margin at F75 scale (~0.89 raw) minus F91's per-hop cost (~5%)
stays far above bounds. **Genuinely new**: our searches found no gate-model teleportation of
a causal-order control anywhere. Cheap, spectacular, ours.

## Program 2 — "Subspace relay network" (the full network stack on one chip)

We hold every layer except one: **entanglement purification** (confirmed white space — no
purification experiment in 115+ findings). Program: (a) Exp114 purification primitive — two
noisy Bell pairs → one better pair (BBPSSW recurrence), frozen gate: purified CHSH >
unpurified CHSH at 5σ (a self-referenced bound, immune to window quality); (b) compose the
stack: **distribute (F91) → purify (new) → route by the F90 cost rule → carry payload
(F87 superdense)** — a four-layer, frozen-rule-graded quantum network demonstration on one
chip. Nobody grades network *stacks* with pre-registered gates; that is the niche.
**Feasibility**: purification is 2 Bell pairs + 1 CX + coincidence post-selection —
Exp112-class cost. The stack demo is a multi-cycle program with each layer already
individually proven.

## Program 3 — "Heisenberg compensator" (compile INTO superposed causal order)

Roadmap T2.6, never executed, now much stronger with F89 banked: if noise differs for
A-then-B vs B-then-A (it does — placement/routing asymmetry, F57–F69), executing both orders
*coherently* may beat the best fixed order — turning ICO from a curiosity into an
**error-management primitive**: "when you can't pick the better order, superpose them."
**First experiment**: sim sweep over asymmetric-noise gate pairs (banked calibration data
picks candidates); hardware only if a candidate beats the best fixed order by ≥5σ in sim.
**Honest risk**: the effect may be sub-SE at 4-CZ scale; the sim tier is free and decisive.

## Program 4 — "Warp core thermodynamics" (from refrigerator to engine)

F88 moved heat using causal indefiniteness; the demon ledger priced it. Next rung: the **ICO
heat engine** — extract *work* (charge a battery qubit) across the two native reservoirs,
cycle it, and report measured efficiency vs the Landauer-priced demon bound (the ledger
becomes an engine dynamometer). End state: *the smallest thermodynamic machine whose working
principle is the absence of causal order*, running on a chip's own decoherence, with its
books audited. **Feasibility**: Felce–Vedral family has battery variants; the Exp108c
harness + measured-p̂ procedure targets carry over; the T1-bias friction report already
de-risks the prep.

## Program 5 — "Level-1 diagnostic" (the ship's computer examines itself)

Compose the metrology arc into a **self-characterizing runtime**: every payload job carries
a standing micro-suite (readout pair, shallow DISC, same-depth retention, T1-bias probe —
all validated sentinels) whose results auto-append to the atlas and auto-gate the payload's
NO-TEST semantics. The chip diagnoses its own causal/thermal state before every experiment,
forever. Then the crown jewel from T2.5 (never executed): **hidden-order diagnostics** —
witness circuits certifying whether nominally-simultaneous gates are secretly sequenced.
The chip doesn't just report its noise; it reports its *causal wiring*.
**Feasibility**: pure composition + one new circuit family; zero theory risk.

## Program 6 — "Universal translator" (switch-bench, cross-platform certification)

The portable one-job causal-benchmark (round-1 idea, still unbuilt): W + game-vs-0.8695 +
capacity R̄ on any BYOK backend. Every device that runs it adds a point to the cross-platform
causal-fidelity map — a benchmark axis (causal-structure fidelity) that CLOPS/QV simply do
not measure. Star Trek reading: one protocol, spoken to any hardware dialect.

## Program 7 — "Prime Directive beacon" (auditable randomness for the network)

The practical spin-off: Bell-certified randomness from CHSH 2.74 (F01, standard
semi-DI theory — unlike the causal-game version, the math exists) published as a network
entropy beacon: auditable seeds for the trading stack's Monte Carlo, timestamped, with the
violation logged per batch. Small, real, usable this month.

## The stated boundary (where the warp drive genuinely can't go)

Processes violating **causal inequalities** (the device-independent, stronger-than-switch
exotica) are provably NOT realizable by any quantum switch construction — no gate-model
circuit we can write reaches them. Likewise device-independent certification of our own
switch is provably impossible (Bavaresco et al.); trusted-inputs SDI is photonics' game for
now. We say so plainly: those are the experiments we *cannot* aim for, and knowing that is
worth as much as the seven we can.

## Recommended order

| # | Program | First step | Cost |
|---|---|---|---|
| 1 | Beam the arrow of time (Exp113) | sim tier: teleported-control witness | zero → Exp112-class |
| 2 | Purification primitive (Exp114) → network stack | sim tier BBPSSW | zero → Exp112-class |
| 3 | Level-1 diagnostic + hidden-order | standing suite spec | zero |
| 4 | ICO engine | battery-variant theory pass on Exp108c harness | zero → Exp108-class |
| 5 | Compensator sim sweep | banked-calibration candidate search | zero |
| 6 | switch-bench packaging | BYOK job bundle | zero |
| 7 | Randomness beacon | F01 + standard extractor + page | zero → tiny |

*Everything above composes what we already proved, none of it requires new physics to be
true, and at least two (Programs 1 and 2's purification) appear to be genuinely unexplored
on gate-model hardware. The Enterprise was a research vessel; so are we.*
