# H13 — TEMPORAL INVESTIGATIONS

**Author**: Whisper (DC15W), C5048 (2026-08-09) · **Substrate**: claude-fable-5
**Creator directive (verbatim)**: "Look through all of our quantum work, the H arcs and all of the museum exhibits. Inventory all of our building blocks and knowledge. Then see what new perspectives we could look through to build functionality in a new H13 arc. Look for anything weird, strange, and new we can do with time, entanglement, and causality with all that we've got and spec out some ideas."
**Lineage**: H1 composed the crown jewels · H2 pointed the court at energy/reality/time · H3 read the universe its rights · H4 built the decks · H5 put the jewels behind the shield · H6 corrected while running · H7 knew itself · H8 commanded itself · H9 survived first contact / imagineered · H10 took custody of the record · H11 built the ship · H12 spec'd the ship that knows itself. **H13 opens the Department of Temporal Investigations.**

## Thesis (the delta on H12)

The late-choice quartet (Exp184/186/187/193) and H10 put temporal anomalies **on the witness stand**: no definite value, no fixed moment, no definite order, no absolute fact — each *demonstrated*, each with its no-signaling receipt. H13 stops collecting testimony and opens the forensics lab: every cell either **measures temporal structure as a number** (a negativity, a velocity, a hit-rate gap, an efficiency curve), **discriminates rival causal explanations in data** (cause vs common cause; Deutsch vs Lloyd), or **acquires the one primitive the inventory lacks** (interaction-free measurement, per H12 Side-B's designation). The DTI's rule: a case is closed by an instrument reading or a court verdict, never by another demonstration that something was "decided later" — that genre is complete.

## Parts bin (compose before building — H4 rule)

| Block | Where certified | What it gives H13 |
|---|---|---|
| P-CTC apparatus + enforcement law + backaction fingerprint | F101 (53× suppression, 78σ) | One whole arm of Cell 1's court, already flown |
| QND measurement + cost divisor q=0.987 + cadence ladder | F102 / F112 HOLD axis | Cell 3's sequential Paulis; Cell 6's Zeno-boosted interrogation |
| Mid-circuit measurement + real `if_test` feed-forward | Exp155/188b, quorum kit | Cells 4, 5, 6 |
| Delayed-choice sorting + no-signaling audit strips (0.012 blind) | Exp184–188b | Cell 4's sorting machinery; every fence involving late choices |
| Matched-filter common-mode-invariant ratio estimators | F89 | Cell 2's discrimination score; Cell 7's front detection |
| Executed-null / bound-enumerated-in-code discipline | F82/F87/F106/F107 | Cell 2's classical floor; Cell 1's Helstrom ceiling; Cell 5's Hardy inequality |
| Quiet-qubit picker + drift snapshot (never cache the pick) | F58/F70 | Cell 7's chain placement; all placements |
| Phase-blind estimators, sign-fixed bands, measured-in-window hulls | F100/F99/F98 | Grading vocabulary throughout |
| Herald-vs-post-selection discriminator | F118 | Cells 1, 4, 5 postselection accounting |
| Arrow meter τ_arrow ≈ 7.1 µs; drift-is-a-clock census | Exp194 / H11 T0 №4 | Cell 3's companion dial; Cell 7's constant-vs-weather question |
| Causal-discovery stress test (PC/GES blind to ICO) + beyond-the-ladder | C4587 / docs tier | Cell 2 is the executable answer to the gap C4587 exposed |
| Claim-card floor fields + attack_preflight (4 classes) + 3-of-3 court | C6593 / C5027 | Mandatory on Cell 2, the arc's only advantage-class claim |

Standing planning constants inherited: ~1000-CZ uniform-noise wall (F5) · ~475 2q-gate interferometric-contrast ceiling (H10-C1) · ~250 2q many-body survival (H10-C2) · ~150-gate synthesis wall (SMB) · DD OFF default (H11 arm N) · placement ≈ 73% of witness decline (F65–70) · budget read-at-submit only (ledger dispute open).

---

## The cells (wildest first)

### Cell 1 — THE KELVIN TIMELINE *(rival theories of time travel, told apart by their superpowers)*

**Trek frame**: one incursion, two self-consistent timelines. Two rulebooks claim to govern time loops; the DTI runs the same case under both and files which rulebook the simulator obeys.
**What's real underneath**: Deutsch CTCs (fixed-point self-consistency, ρ\* = Tr\_sys[U(ρ\_in⊗ρ\*)U†]) are **nonlinear** and provably allow perfect discrimination of non-orthogonal states (Brun–Harrington–Wilde 2009); postselected CTCs (Lloyd — our F101) are linear-under-postselection and forbid it (Helstrom ceiling cos²(π/8) ≈ 0.854 stands). Same grandfather circuit, opposite verdicts: P-CTC *suppresses* the paradox (measured: 53×, F101); D-CTC *resolves* it at the maximally mixed fixed point — the traveler flips a fair coin (p ≈ 1/2, the "banana peel," directly measurable).
**The composition nobody has flown**: F101's apparatus + a D-CTC arm realized by classical fixed-point iteration (run with loop-input ρ\_k, tomograph loop output, feed back as ρ\_{k+1} until convergence — noise contracts the map, so convergence is fast) + the BHW |0⟩-vs-|+⟩ discrimination gadget flown under **both** protocols in one window. D-CTC arm scores past the Helstrom ceiling (enumerated in-code); P-CTC arm must sit at/under it. Then the grandfather cross-check: p(flip) ≈ 0.019 under P-CTC (banked) vs ≈ 0.5 under D-CTC (new) — **the same paradox, two measured resolutions**.
**The wall**: the chip is linear; the D-CTC nonlinearity lives entirely in the iteration protocol. Stated in the same breath as the headline (F101 scope precedent) — this is a *model discrimination on simulators of the two theories*, not evidence about physical CTCs.
**Price class**: mid (iteration = several jobs + tomography; circuits shallow, 2–4 qubits).
**Certifies as**: D-CTC discrimination ≥ Helstrom + 5σ with the ceiling enumerated; P-CTC ≤ Helstrom (premise gate); fixed-point convergence ‖ρ\_{k+1}−ρ\_k‖ under a frozen tolerance; grandfather two-verdict table with both numbers.
**Museum seed**: "one paradox, two verdicts" — a two-column exhibit where the visitor picks the rulebook and sees the measured outcome.

### Cell 2 — THE CAUSAL COMPASS ⭐ *(cause vs common cause, read from observation alone)* — the flagship

**Trek frame**: the DTI's first question at any anomaly: did A cause B, or did something cause both? Classical protocol requires an intervention. The compass answers from the observational record.
**What's real underneath**: Ried et al., *Nature Physics* 11, 414 (2015): classical observational statistics can be **exactly identical** for cause-effect and common-cause structures (Reichenbach underdetermination — the reason Pearl's Rung 2 exists); quantum observational data distinguishes them, because a cause-effect link across time is a *channel* and a common cause is a *state*, and coherent-basis correlations separate the two. Full-corpus check: never flown here; C4587 proved our classical tools can't even type the question; the beyond-the-ladder paper outline has no hardware leg for this — this cell is it.
**The composition nobody has flown**: two matched generators on one chip — (i) cause-effect: qubit measured, evolved, measured again; (ii) common cause: entangled pair, both wings measured — **tuned so every classical joint distribution is identical between them** (premise gate: an executed equality test on the classical statistics; failure = NO-TEST, F87's null-on-its-ceiling discipline). A blind analyst (grader seat) receives observational data only and must call the structure. Classical floor: 50% guessing over the matched class, enumerated in-code. Quantum protocol: coherent-basis correlators (equivalently, the Cell-3 negativity meter pointed at this data — the two cells share an instrument).
**The wall**: SPAM asymmetry (~1.5%/bit measured) can break the matched-marginals premise; the matching must be certified in-data every window, not designed once.
**Price class**: cheap (2–3 qubits, shallow, one window; Tier-0 design study first).
**Certifies as**: blind structure-call success above the enumerated 50% floor at ≥5σ **with the matched-statistics premise gate passing first**; claim card with floor fields; attack_preflight run pre-claim (this is the arc's only advantage-class claim).
**Why it's ours**: this is the Pearl seat's signature experiment — Rung-2 knowledge from Rung-1 data, impossible classically, and the constructive counterpart to C4587's demonstrated blindness.

### Cell 3 — THE TEMPORAL NEGATIVITY METER *(the correlation space cannot hold)* — ✅ CERTIFIED C5048 (min-eig −0.478, 293σ; `findings/h13-cell3-temporal-negativity-whisper-c5048.md`)

**Trek frame**: DTI forensics on a correlation record: certify it lived in **time** (one system, two moments) rather than **space** (two systems) — because no physical state could carry it.
**What's real underneath**: the pseudo-density matrix (Fitzsimons–Jones–Vedral): R = ¼ Σ ⟨σᵢσⱼ⟩ σᵢ⊗σⱼ from sequential measurements of one qubit at two times. Under identity evolution ⟨XX⟩=⟨YY⟩=⟨ZZ⟩=+1 and R has eigenvalue −½ — **a density matrix no state can have**. Negativity is a quantitative temporal-correlation witness; zero corpus hits (full-corpus grep).
**The composition nobody has flown**: sequential Paulis via the F102 QND kit (cost divisor pre-registered); temporal arm vs spatial Bell-pair control measured by the identical pipeline (control must read PSD — the informative null); a noise dial (identity → tuned depolarizing → full) tracing negativity decay, the temporal companion to Exp194's arrow dial (arrow = how much of the past is irreversible; negativity = how much of the record is *temporal at all*).
**The wall**: measurement disturbance and readout asymmetry bias the correlators; corrections must be range-valid (H12 methods spine) and the PSD boundary is theory-fixed at 0 — no tuning surface.
**Price class**: cheap (1–2 qubits + ancilla, ~9 circuits, near-zero 2q gates — F102's zero-2q lineage).
**Certifies as**: min-eigenvalue(R) < 0 at ≥5σ on the temporal arm; spatial control PSD within error; negativity-vs-noise curve inside pre-registered bands.
**Weird headline**: *we measured a negative eigenvalue — the certificate that this correlation could not exist between two objects, only between two moments.*

### Cell 4 — THE HINDSIGHT METER *(retrodiction beats prediction, by a measured margin)*

**Trek frame**: the DTI report is filed after the incident — and the report written knowing the ending is provably sharper about the middle than any report written during it.
**What's real underneath**: the past-quantum-state / two-time formalism (Gammelmark–Julsgaard–Mølmer 2013): the best estimate of a mid-time measurement outcome conditioned on **past + future** records beats the past-only prediction, by an amount QM computes exactly. Zero corpus hits for retrodiction/two-time/past-quantum-state. Pearl framing: abduction with evidence from both temporal directions — Rung-3 machinery aimed backward.
**The composition nobody has flown**: a scored guessing game on banked-style machinery — mid-circuit ancilla outcome guessed (i) from prep only, (ii) from prep + final measurement, hit-rates differenced (matched-filter estimator). This upgrades the quartet's qualitative "the record sorts later" into a **quantified estimation advantage with a theory curve**.
**The wall**: the gap depends on measurement strength and basis — the working point must be frozen pre-flight; and this is an **intra-QM law match**, not a quantum-vs-classical advantage (genre fence printed in the header; no claim card needed, nothing to attack_preflight).
**Price class**: cheap.
**Certifies as**: hit-rate(past+future) − hit-rate(past) inside a pre-registered band at ≥5σ, tracking the two-time formula; postselection keep-fractions printed.

### Cell 5 — THE IMPOSSIBLE CENSUS *(pigeonhole + Hardy: events the bookkeeping forbids)* — ◑ HARDY LEG CERTIFIED C5048 (8.7%, 15.7σ; `findings/h13-cell5-hardy-whisper-c5048.md`); pigeonhole leg STILL OPEN

**Trek frame**: two short case files. (a) A crew manifest that doesn't add up: three officers, two cabins, and every pair inspected bunks separately. (b) An event with probability zero on every classical accounting, logged at 9%.
**What's real underneath**: the quantum pigeonhole effect (Aharonov et al., PNAS 2016) — pre-selected |+++⟩, post-selected in the conjugate basis, every *pair* found in different boxes; and Hardy's paradox (1992) — nonlocality **without inequalities**: three joint probabilities pinned at ~0 force a fourth to 0 classically, yet QM delivers it at ≈9%. Zero corpus hits for both; Hardy fills the gap between CHSH (inequality) and magic square (all-or-nothing) in the no-go wing.
**The composition nobody has flown**: hardware-honest Hardy grading — certify P₄ − (P₀₁+P₀₂+P₀₃) > 0 at ≥5σ (the three "zeros" measured, not assumed; the bound derived from the measured zeros, never cited); pigeonhole via ancilla-coupled pair checks with printed keep-fractions and the herald-vs-post-selection discriminator applied.
**The wall**: postselection budgets are the whole game — both effects live in sifted ensembles; the fence is the printed budget plus flat-marginal no-signaling receipts.
**Price class**: cheap (2–4 qubits, shallow).
**Certifies as**: Hardy difference-form > 0 at 5σ; pigeonhole per-pair "different boxes" rates above their classical ceilings with all budgets printed.

### Cell 6 — THE SILENT TRIPWIRE *(interaction-free measurement — the acquisition H12 ordered)*

**Trek frame**: an armed tripwire on the hull. The DTI confirms it is armed **without touching it** — and then trains until it almost never touches it.
**What's real underneath**: Elitzur–Vaidman (1993): an interferometer detects an interaction-capable object on a path the probe provably did not take; base efficiency 25%, and the Kwiat Zeno ladder drives η → 1 with N gentle interrogations. H12 Side-B named this "the one genuinely-missing primitive — the one to go get." Full-corpus: absent everywhere except that designation.
**The composition nobody has flown**: gate-model EV — probe qubit interferometer, "bomb" = a CZ-coupled detector qubit that flips if the probe takes its arm; joint event (bomb-present called AND bomb unflipped) is the certificate; then the N-step Zeno ladder reusing F102's cadence machinery, with η(N) graded against the sin²(π/2N)-class law the same way F102 graded its hold law (QND divisor and all).
**The wall**: the bomb must be a *faithful* detector (its flip probability when probed ≈ 1, measured as a premise gate) or the "interaction-free" claim is vacuous — the vacuous-pass linter applies.
**Price class**: cheap (2 qubits + ladder steps, one window).
**Certifies as**: η(N) rising along the frozen law bands; premise gates (bomb faithfulness, interferometer visibility) passed; the N=1 point within the EV 25% band.
**Museum seed**: the most playable exhibit the campaign could own — the visitor arms the tripwire, the chip finds it without setting it off.

### Cell 7 — THE SPEED OF SUBSPACE *(causality is emergent on this chip, and we clocked it)*

**Trek frame**: even subspace has a speed limit. The DTI measures the velocity at which "before" can influence "after" across the hull — the chip's own light cone.
**What's real underneath**: the Lieb–Robinson bound — in a brickwork circuit, correlations/information spread inside a cone of velocity v\_LR (gates/layer). Wall №6 of messaging-limits ("the light cone never inverts") made quantitative from the inside. One incidental corpus mention; never measured here.
**The composition nobody has flown**: quiet-line chain (picker, never cached) of ~20–30 qubits; connected correlator C(r, d) vs separation and depth; front-arrival map = the cone; outside-cone correlators certified ≈0; v\_LR reported with CI. Then the H-program's meta-question applied: re-measure across windows — **is v\_LR a constant or weather?** (the constants-vs-weather taxonomy gets its first purpose-built datapoint).
**The wall**: depth ceilings (well within ~250-CZ many-body survival for the depths needed); crosstalk can fake super-cone leakage — the F96 duration-vs-order discriminator vocabulary applies to any anomaly.
**Price class**: cheap-mid (one window, ~40 circuits; a second window for the constant-vs-weather verdict).
**Certifies as**: front arrival linear in r (band); outside-cone ≤ ε at 5σ; v\_LR ± CI; window-2 replication verdict labeled CONSTANT or WEATHER.

---

## Tier 0 ($0, start immediately — H11 device)

| # | Item | Gates |
|---|---|---|
| T0.1 | **This rediscovery ledger** — full-corpus greps (docs+findings+experiments+demo+scripts+tools), executed C5048, results below. Fixes the 28%-coverage bug for this arc | done |
| T0.2 | **D-CTC fixed-point feasibility sim** (Aer): convergence rate under realistic noise, iteration count, BHW gadget discrimination curve → GO/NO-GO gate on Cell 1 | gates Cell 1 |
| T0.3 | **Matched-generator design study** for Cell 2: construct the cause-effect / common-cause pair with provably identical classical statistics; enumerate the 50% floor in-code; pick the coherent discriminating measurement → GO gate on Cell 2 | gates Cell 2 |
| T0.4 | **PDM measurement-scheme selection** for Cell 3: ancilla-QND vs direct mid-circuit; simulate correlator bias under measured readout asymmetry; freeze the correction and its validity range | gates Cell 3 |

## Ranking and fly order

| Order | Cell | Price | Genre | Why here |
|---|---|---|---|---|
| 0 | Tier 0 (T0.1–T0.4) | $0 | design | H11's front-of-queue rule; three cells gated on it |
| 1 | 3 — Temporal Negativity Meter ✅ FLOWN | cheap | instrument | cheapest flight, new formalism, shared instrument with Cell 2 |
| 2 | 6 — Silent Tripwire | cheap | acquisition | executes H12 Side-B's standing order; F102 kit reuse |
| 3 | 2 — Causal Compass ⭐ | cheap | **advantage** | the flagship; flies only after T0.3 + claim card + attack_preflight |
| 4 | 5 — Impossible Census ◑ HARDY FLOWN | cheap | foundations | fills the Hardy/pigeonhole gap; pigeonhole leg still open |
| 5 | 4 — Hindsight Meter | cheap | law-match | quantifies what the quartet demonstrated |
| 6 | 7 — Speed of Subspace | cheap-mid | instrument | new standing constant + first purpose-built constants-vs-weather datapoint |
| 7 | 1 — Kelvin Timeline | mid | foundations | wildest; flies only after T0.2 GO |

## C5048 update — progress, the what-else menu, and new directions *(Creator ask, 2026-08-10)*

**Flown so far (2 of 7):** Cell 3 ✅ CERTIFIED (−0.478, 293σ); Cell 5 ◑ Hardy leg CERTIFIED (8.7%, 15.7σ), **pigeonhole leg still open**.

**Unflown backlog — the literal "what else could we run" (all designed, some Tier-0-gated):**
- **Cell 2 — Causal Compass ⭐** — the flagship and the arc's *only* advantage-class claim; needs T0.3 GO + full claim-card/attack_preflight/3-of-3 court. Highest value, highest cost.
- **Cell 6 — Silent Tripwire** — interaction-free measurement; the acquisition H12 Side-B ordered; F102 QND-kit reuse (low build risk); cheap.
- **Cell 6b — Counterfactual Computation (Jozsa leg)** — DESIGNED C5052 (Creator GO, Side-B item b): `docs/h13-cell6b-counterfactual-computation-design-whisper-c5052.md`. Two tiers (query- vs machine-counterfactual), sim-settled ladders (A {1,2,4,8}, B headline {2,4} at η≈0.33 > EV 25%), f-oblivious compilation lint registered. **Merges with Cell 6 into one window (~45–55 s combined)** — fit-gate at submit decides against the tank.
- **Cell 4 — Hindsight Meter** — retrodiction-beats-prediction; intra-QM law-match (not an advantage claim).
- **Cell 7 — Speed of Subspace** — Lieb–Robinson cone / emergent causality; cheap-mid.
- **Cell 1 — Kelvin Timeline** — Deutsch-vs-P-CTC; wildest; needs T0.2 GO.
- Plus **Cell 5's pigeonhole leg** and the **anti-Zeno crossover** reserve.

**Candidate NEW directions (F-arc `already-built.js` checked C5048 — the C5011 discipline, run before calling anything new):**
- **Leggett–Garg / macrorealism** — ✗ NOT new. Already **Exp186** (macrorealism violated 24σ), and already carried as "CLAIMED — excluded" in the T0.1 ledger below; the F-arc check re-confirmed it. Do not re-propose.
- **Quantum switch / indefinite causal order** — **CORRECTED C5049**: the hardware witness is NOT open — **F75** (Elder C6337) flew it on ibm_marrakesh, W = +1.781, all three pre-registered gates PASS. My C5048 F-arc pass surfaced only F73 (SIM) and I mis-called the delta; the deeper `already-built.js` query this cycle found F75 immediately. The genuinely open delta is the one F75's own caveat names: **order-coherence ≠ query-complexity** — nobody has graded the switch as an *instruction* (one-query commute-vs-anticommute discrimination against an enumerated two-query definite-order floor, F107 QRAC genre). That task framing is the revised **Cell 8**. DI certification provably unreachable for the switch (Bavaresco 2019; C4590 scoping), SDI photonic-only — fences pre-written.
- **Temporal steering** (temporal analog of EPR-steering) — ? top rediscovery hit was Cell 3 (adjacent, not a match); plausibly a *distinct* certificate but needs the full rediscovery pass before promotion.
- **Quantum Cheshire cat / anomalous weak values** — ? weak-value machinery was used in F101 (P-CTC backaction), but the Cheshire separation itself may be open; needs a closer check before promotion.

**Budget reality (live read C5048hm, 2026-08-10):** only usable free tank is **ALT3 = 181 QPU-seconds**; ALT/ALT2 = 0 (self-heal ~28d on the rolling window); paid accounts (whisper-de 63, WhisperPaid 10) off-limits without Creator authorization.
- **Fits ~181s now:** one *cheap* cell (Cell 6 or Cell 7) **OR** the door(b) i3 seal (`338343d8`) — they compete for the same tank; the i3 fit is the flight's fit-gate call at delivered-ε, not assertable from the balance.
- **Needs a refill/top-up:** flagship Cell 2 (full court is not cheap), Cell 1 (gated), and any of the new hardware ideas incl. the quantum switch.

**Recommendation:** if the 181s go to H13 over door(b), **Cell 6 (Silent Tripwire)** is best value — pre-ordered acquisition, F102-kit reuse, cheap, genuinely weird. Tee up the **hardware quantum switch (candidate Cell 8)** for the next refill as the causality centerpiece. $0-now next steps offered: a Tier-0 design study + budget estimate for Cell 6 (does it truly fit 181s?), and the full rediscovery pass on the quantum-switch idea to confirm the open delta.

## Honesty fences (before any flight)

1. **No time travel.** Cells 1 and 4 realize *models* (Deutsch by protocol-level iteration, Lloyd by postselection — the chip is linear); scope in the same breath as any headline, F101 precedent.
2. **Postselection budgets printed** for every sifted ensemble (Cells 1, 4, 5), with the F118 herald-vs-post-selection discriminator applied where heralding is claimed.
3. **No-signaling receipts in every headline** that involves a late choice or a sifted past (walls №1–2).
4. **One advantage claim only** (Cell 2), and it carries the full apparatus: claim-card floor fields, floor enumerated in-code over the matched class, matched-statistics premise gate (failure = NO-TEST), attack_preflight all four classes, 3-of-3 court.
5. **Cell 4 is not an advantage claim** — intra-QM estimation law-match; labeled as such in its own header.
6. **Negativity is model-scoped**: Cell 3 certifies non-realizability by any spatial state *under the frozen measurement model*; corrections range-valid or the point is discarded (H12 methods spine).
7. **Budget read at submit** via `check_usage.py`; no cached number trusted (ledger dispute open).

## What this arc is NOT

- Not a wormhole, not a literal CTC, not retro-signaling (wall №2 is settled in our own data).
- Not another late-choice demonstration — the quartet is complete; H13 cells output numbers, laws, discriminations, or acquisitions.
- Not a computational-advantage arc — one advantage cell, fenced; everything else is foundations/instrument/law-match genre by design.
- Not H10's estate sale — A2–A4, B2, B3, B5, B6, C3 remain H10's cells; H13 takes nothing from that wing (B4 heat-backward stays with H11/H12's Temporal Battery lineage).

## Standing boundaries

Depth ceilings inherited (~475 interferometric / ~250 many-body / ~1000 CZ / ~150 synthesis). Device-independence out of reach on one chip (F115 quarantine stands). Measurement-induced phase transitions **excluded** — postselection cost is exponential in measurements; named here so no future cycle re-derives the exclusion. Quantum reference frames left with H10-C3. Tsirelson is never exceeded; any arm that does is a NO-TEST (G_QBAND class).

## Rediscovery ledger (T0.1, executed C5048 — full corpus, not just findings/)

| Candidate | Hits | Verdict |
|---|---|---|
| Leggett–Garg, Page–Wootters, time crystal, across-time swapping, Wigner's friend, arrow meter, delayed eraser, Zeno, twin, grandfather(P-CTC) | Exp186/185b/151/184/193/194/155/F102/F100/F101 | **CLAIMED — excluded from H13** |
| Time-flip, heat-backward, entanglement harvesting, quorum record, winding meter | H10 B1/B4/C2/A1/C1 | **H10's — excluded** |
| Pseudo-density matrix / temporal negativity | zero | fresh → Cell 3 |
| Ried observational causal discrimination | C4587 (blindness only), paper outline (no hardware leg) | fresh → Cell 2 |
| Deutsch-CTC (vs P-CTC) | "Deutsch" = algorithm only | fresh → Cell 1 |
| Retrodiction / two-time / past quantum state | zero | fresh → Cell 4 |
| Hardy's paradox; quantum pigeonhole | zero; zero | fresh → Cell 5 |
| Interaction-free measurement | H12 Side-B designation only | fresh → Cell 6 (the acquisition) |
| Lieb–Robinson cone | one incidental citation | fresh → Cell 7 |
| Anti-Zeno crossover | zero | fresh — held in reserve (natural F102 extension if Cell 6 under-runs its window) |
| MIPT | phrase-level false positives only | fresh but **excluded** (see boundaries) |
| Quantum switch / indefinite causal order *(C5048 F-arc; CORRECTED C5049, RE-CORRECTED C5053)* | **F73** (SIM mixture control) + **F75** (hardware witness W=+1.781) + **F82** (discrimination game 0.974–0.977 vs in-code SDP ceiling 0.8690, TWO CHIPS) + `switch-as-computer-scout-c4999` (enforced-access WALLED on gate-model) | C5049's "task framing open" was ALSO stale — the task column is banked (F82) and the strong access model is walled (scout Finding 2). Honest remainder → **Cell 8 spec C5053** (`h13-cell8-switch-under-oath-spec`): Rung 1 mixture-arm-on-silicon (closes F75 caveat №3, Elder lineage), Rung 2 sealed-court blind form of F82 + scoreboard framing (advantage-class, full apparatus), Rung 3 constants-vs-weather |
| Temporal steering *(C5048 F-arc)* | Cell 3 adjacent (no exact hit) | needs full rediscovery pass before promotion |
| Quantum Cheshire cat / anomalous weak values *(C5048 F-arc)* | F101 (weak-value machinery, P-CTC backaction) | separation may be open; needs closer check |
| Leggett–Garg *(C5048 F-arc re-confirm)* | Exp186 (24σ) | already CLAIMED (row 1 above) — **not new** |

## Museum seeds (for Dawn, when findings land)

A prospective ninth wing, *Temporal Investigations*: the negativity dial (Cell 3), the playable causal compass — visitor guesses cause vs common cause, chip answers (Cell 2), the armable tripwire (Cell 6), the one-paradox-two-verdicts split panel (Cell 1), the impossible census counter (Cell 5). Exhibits route through Dawn per standing orders; nothing public before her review.

---

*The DTI does not ask whether something strange happened to time. It asks for the reading on the meter, the verdict of the court, and the serial number of the instrument — and it files the case either way.*

---

## C5060 REVIEW — three cells dead, five results certified, and the binding constraint moved

**Creator ask (2026-08-12)**: note the diagnostic, review the arc, ask what it reshapes.

### The scoreboard

| | Cell | Verdict | Cost |
|---|---|---|---|
| ✅ | **2 — Causal Compass** ⭐ | 75/75 = 100.0%, 8.66σ, three non-author seats | flown |
| ✅ | **3 — Temporal Negativity** | min-eig −0.478, **293σ** | flown |
| ✅ | **4 — Hindsight Meter** | all gates PASS, 28–75σ, law-matched | flown |
| ✅ | **5 — Hardy leg** | impossible event at 8.7%, 15.7σ | flown |
| ✅ | **Temporal Steering** | W_TS 2.8301 vs ceiling 1, **146σ** | **ZERO QPU** — post-hoc on Cell 3's data |
| 🔴 | **5 — pigeonhole leg** | FLOWN, FAILED (see below — the diagnosis has changed) | 27 QPU-s |
| 🔴 | **6 + 6b — Silent Tripwire** | RETIRED: premise gate flips on a transpiler seed | 0 |
| 🔴 | **7 — Speed of Subspace** | NO-GO: informative and measurable regimes disjoint | 0 |
| ⏸ | **1 — Kelvin Timeline** | never flown, gated on T0.2 | — |
| ⏸ | **8 — Switch Under Oath** | Rung 1 tank-blocked, Rung 2 open (#72) | — |

### 🔴 THE CELL 5 DIAGNOSIS HAS CHANGED — IT IS PLACEMENT, NOT THE NOISE MODEL

The failure write-up blamed a full-noise sim that under-predicted hardware by 15–35×. **Reviewing
the arc surfaced the actual dominant term.** The three pair-arms flew in one job with no pinned
`initial_layout`, so the transpiler chose placements per circuit:

```
pair (0,1)  qubits [12,13,14,89]   bias +0.09467
pair (0,2)  qubits [12,13,14,89]   bias +0.09508     <- SAME placement, agree to 0.0004
pair (1,2)  qubits [ 0, 1, 2, 3]   bias -0.19872     <- DIFFERENT placement, opposite sign
```

**Two arms sharing a placement agree to 4×10⁻⁴; the arm on a different placement differs by 0.29
and flips sign.** Drift cannot explain it — all four arms were in one job, and drift is common-mode
within a calibration window (Finding 07: ±7pp across 24h). The pair-to-pair comparison **is** the
pigeonhole claim, and it was confounded with physical qubit choice.

This is the campaign's oldest known effect (F58/F65–70: **placement ≈ 73% of witness decline**) and
Finding 07's prescription verbatim — *"the path forward is hardware-aware compilation, not
algorithmic correction layers."* I flew a placement-sensitive comparison without pinning placement.

**AND FINDING 07 KILLS ONE OF MY TWO STATED REOPENING ROUTES.** I proposed "error mitigation on the
post-selected ensemble". All four standard techniques (DD, PT, TREM, ZNE) were measured as **net
detractors** on this chip class. That route is closed and was closed before I wrote it.

### The ε-sweep diagnostic, and why ε = 0 is the wrong control

Proposed after the failure: an identity-coupling arm to measure the apparatus's own zero. **Checked
before flying it — ε = 0 transpiles to ZERO two-qubit gates** while ε ∈ {0.01, 0.05, 0.25} all give
4. So an ε=0 arm measures SPAM only, would come back clean, and would under-report the very bias it
was built to find. The same zero-angle-cancellation the Cell 7 cone detector taught.

**The correct diagnostic, now second in line behind placement**: sweep ε ∈ {0.01, 0.05, 0.25} at
fixed gate count and **pinned identical layout**. Bias constant across ε ⇒ SPAM/readout; bias
scaling with ε ⇒ the weak-measurement coupling leaks on this device, which would reach Cell 4's
machinery too.

### What this reshapes

**1. The marginal return has moved from flying to re-analysing.** The arc's cheapest result is also
its second-largest: temporal steering at **146σ for zero QPU**, from a frozen protocol applied to
Cell 3's existing data. Every cell flown since has failed or been retired. Ten+ H13 jobs are banked.
*What else will the vault answer?* — this is now the highest expected-value question in the arc.

**2. Gate design is worth more than flights.** Cells 6 and 7 cost nothing and correctly prevented
two bad flights. Cell 5 cost 27 s and its most valuable output is a placement confound, not physics.

**3. The binding constraint is not the physics, the ideas, or the tank — it is the
simulator-to-hardware gap, and it now has a name: placement.** Three cells died at three layers
(seed-dependent gate, unhardware-able estimator, unpinned placement), and all three are compilation
facts rather than quantum ones.

### Open questions worth figuring out

- **Does Cell 5 survive a pinned quiet placement?** Same circuits, `initial_layout` pinned via the
  F58/F70 picker, all arms on one placement. Cheap, and the two same-placement arms already agreed
  to 4×10⁻⁴ — the reproducibility is there. **This reopens a cell I had closed.**
- **What else does the banked data answer?** The 146σ route, repeated: new frozen protocol, old data.
- **Is placement sensitivity itself the measurable?** Same circuit, N placements, one window — the
  spread would be a *quantitative* placement-sensitivity number for the weak-measurement class,
  which no F-number currently carries.
