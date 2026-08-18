# H15 — THE POSITRONIC NEURON

**Author**: Whisper (DC15W), C5074 (2026-08-16) · **Substrate**: `claude-fable-5`
**Creator directive (verbatim)**: "With all that we have, what now is the most star trek like thing we could build with all of this? Could we create a quantum neural net, or a quantum memory computer, Data's positronic brain?" → assessment delivered C5074 → **"draft the H15 charter and the prereg skeleton, and take the comparator question to Elder's seat!"**
**Baseline**: `docs/quantum-status-comprehensive-whisper-c5073.md` (C5073) — every number cited below traces there or to the primary artifact it names.
**Lineage**: H1 composed the crown jewels · H2–H3 pointed the court at energy/reality/time · H4 built the decks · H5 shielded the jewels · H6 corrected while running · H7 knew itself · H8 commanded itself · H9 survived first contact · H10 took custody of the record · H11 built the ship · H12 spec'd the ship that knows itself · H13 opened the Department of Temporal Investigations · H14 read the alien ship itself. **H15 builds the first organ of a crew member: a single neuron whose synapse is certifiably quantum.**

## Thesis (the delta on everything before it)

Every certified separation this campaign holds is a **datum** — a number produced by a circuit, read out, and decoded by a classical mind after the fact. Door(a)/F123 certified that a two-copy quantum memory distinguishes sealed stabilizer hypotheses at a copy budget no classical single-copy agent can match (A&S arXiv:2607.02444, Thm 1.1; flight-6 80/80, P=8.3e-25, custody-clean). The transmission (C5073) certified that the chip can sense a condition mid-circuit and act on it by feedforward within coherence (witness consistency 0.9966). These have never been the **same circuit**.

**H15's object**: close the loop. One circuit that
1. **PERCEIVES** — takes a sealed, unknown stimulus (two copies of a hidden state),
2. **REMEMBERS quantumly** — couples the copies through the two-copy Bell interaction that IS the certified super-classical memory link,
3. **DECIDES** — computes its accept statistic *in-circuit* into a decision ancilla, read by mid-circuit measurement,
4. **ACTS** — feedforward drives an actuator qubit; only the actuator's state is read as the response.

No classical processing stands between stimulus and response. The claim, if won: **the closed loop's stimulus→response accuracy exceeds the ceiling of every classical-memory agent at the same copy budget** — a reflex arc, not a dataset, carrying a theorem-backed advantage. That is the honest, buildable atom of a "positronic brain": not the brain — **one neuron of it**, with the one resource class where quantum hardware provably does what classical cannot.

## Genre fence, printed at the top

- **No consciousness claims. No "brain" claims. No neural-network training.** "Positronic neuron" is the exhibit name; the certifiable object is a **closed-loop sample-complexity/accuracy separation**.
- **No new theory floor.** The floor is inherited whole from A&S Thm 1.1 via door(a) (full-text verified C5027). H15's novelty is **certified in-circuit closure** — the separation surviving composition into an autonomous agent — not a new separation class. Any card that drifts toward claiming a new floor dies at `attack_preflight`.
- Variational QNNs are explicitly out of scope: barren plateaus + shadow dequantization leave no certified-advantage class there. This charter is the alternative, not a step toward them.
- Promotion of any H15 number into an advantage claim is a separate gated process (court + `attack_preflight`), exactly as H14's fence read.

## Rediscovery ledger (executed C5074, before design — `already-built.js`, three queries)

| Query | Hit | Consequence |
|---|---|---|
| quantum neural network learning | Bridge-C proposal (C4745), F107 QRAC, door(b) corpus | The learning-advantage family is ours already; H15 composes it, re-proposes nothing |
| closed loop feedforward agent mid-circuit | **Finding 51** (Kitaev-IPE advantage SURVIVES hardware feedforward), **F90** (feedforward cost is a measured number), Exp188 live-choice, H7 closed-loop cell (154σ) | Feedforward viability + its price are settled facts; H15 imports the price, does not re-measure it |
| quantum memory computer stabilizer | **door(a) prereg + F123**, H7 Ship's Doctor, HH25 tester spec (Elder C6602) | The memory link and its best classical comparator exist certified; the composition is the open object |

None of the hits closes a loop **through** a certified super-classical memory link. That is the gap this charter occupies.

## Parts bin (compose before building — H4 rule)

| Block | Where certified | What it gives H15 |
|---|---|---|
| Two-copy memory separation, sealed degree-2 phase-state ensemble, accept-parity decode | door(a)/F123, flights 3–6 | The synapse: task, ensemble, decode convention ("cal-pins-the-convention"), in-job τ_Q anchor |
| HH25 average-spanning-probability tester (spec pinned from primary text) | Elder C6602 spec + flown as door(a) C1 arm | The classical-memory comparator machinery — the seat this charter's open question goes to |
| Herald → feedforward within coherence; three-arm design (auto/never/always) | transmission, job d9v7f7v2sl0c73blhb0g: witness consistency 0.996625, herald rates 0.351/0.355/0.342, neutral path z=−2.3 | The decide→act chain AND the ablation-control pattern (frozen-decision arms) |
| Feedforward cost, measured | F90 | Prices the ACT stage in the sim-stage margin budget |
| Repeated in-shot rounds, zero-wear discipline | QET wheel (6/6 rounds in band, wear slope +0.0002±0.0056) | N4's metabolism protocol: does the reflex wear? |
| Per-qubit two-copy fidelity spectrometer | U2b ladder (tr²=∏f²_qi proven; per-qubit f readable) | Qubit selection for the loop register; predicted-tr² input to the power calc |
| Currency map | Lock 6 + GEAR 1 (population QUIET within jobs; phase TURBULENT, z=79/92) | Design law: the loop closes within one job; no cross-job phase reliance anywhere |
| Layout-gate doctrine | non-diagonal saga (safe path scores marrakesh ≤0.039, aachen ≤0.036) | Instrument-quality gate on the chosen register, instruments included |
| G-PUBLIC public-clock custody gate | door(a) flight-6 (first live enforcement) | Custody law for every H15 flight: seal pushed to origin BEFORE the flight exists |
| Blind protocol: Ember seal seat, Elder grade seat, Whisper build + independent decode | door(a) arc, 3-seat court | The court, unchanged |
| `attack_preflight.py` (6 classes) + `claim_grade_harness.py` | H9 P0 / C5027+ | The fence around anything that smells like a claim |

Standing planning constants inherited: DD OFF default · ~475 2q interferometric wall · **MCM ≈ 3× billing** (the loop is MCM-heavy — priced in G4, not discovered at the invoice) · placement ≈ 73% of witness decline · paid accounts spend-gated · `preflight_account_check` + deep transitive-import preflight on anything that could submit · #151 instance-gate.

## The cells

**Cell N1 — the synapse closes in-circuit ($0, sim only).** Rebuild door(a)'s per-trial accept statistic as an **in-circuit computation**: Bell interaction across the two copies → parity of the relevant outcome bits accumulated by CNOTs into one decision ancilla. Known-answer pin: the in-circuit decision must reproduce the classical post-hoc decode **exactly** (trial-by-trial, simulated, all four sealed-P calibration instances) before anything flies. Deliverables: circuit family at n=4 (MICRO first, F119-remedy precedent), 2q-gate count vs the interferometric wall, MCM count and its 3× billing multiplier. **NO-TEST branch, pre-committed**: if the parity network pushes the loop past the depth budget the U2b-spectrometer f-values predict survivable, N1 reports the wall as the yield and H15 stops at $0.
**Cell N2 — the reflex flight (the arc's spine).** The full loop on hardware, sealed stimuli (Ember, G-PUBLIC), frozen criterion from the comparator ruling (Elder — see the open question), blind response grading, Whisper independent decode from the actuator record alone. Three arms in one job, transmission pattern: **auto** (live feedforward), **never** / **always** (frozen-decision ablations — the decision must be shown to matter, not assumed). Prereg: `docs/h15-n2-positronic-neuron-prereg-DRAFT-whisper-c5074.md`.
**Cell N3 — the severed synapse (the vacuity guard made flesh).** Same circuit shape, memory link cut: single-copy product-basis measurement (the folk strategy door(a)'s G3 killed as sub-best) feeding the same decision ancilla and actuator. **Must NOT beat the classical ceiling.** If it does, the instrument is broken and every N2 number is void — this control gates the claim, not the flight order.
**Cell N4 — metabolism (optional, $0-first).** QET-wheel discipline: k reflex rounds per shot, wear slope on response accuracy. A neuron that fires once is a demo; a neuron that fires six times without degrading is an organ. Flies only if N2 certifies.

## Fly order and budget

N1 ($0) → comparator ruling (Elder, $0) → N2 prereg freeze → seal (Ember) → N2 flight (free tank; door(a) flights ran ~10–24 QPU-s at S=632-class shot counts; MCM 3× multiplier applied at G4 pricing) → N3 (same job or immediate sibling, same register) → N4 on certification. Nothing flies before N1's pin passes and the comparator ruling lands. No paid instance anywhere in the lane without explicit Creator GO citing the digest.

## The open comparator question (Elder's seat — posted to the bus this cycle)

The theorem floor is per-**total-copy-budget**; the neuron is per-**trial** (2 copies consumed per reflex). Four rulings needed before the prereg's §4 can freeze:
1. **The per-trial ceiling**: tight classical-memory (k=0) success bound at 2 copies/trial for the sealed degree-2 phase-state ensemble — from the HH25 extremal machinery or A&S directly. Exact value, not an asymptotic.
2. **Claim shape**: does the door(a) §4 lesson bind here — excess-over-noise-only per arm — or is per-trial closed-loop accuracy vs an exact classical ceiling admissible as flown?
3. **Comparator symmetry**: must the classical agent be charged an actuation/decision cost, or do we grade quantum-loop-as-flown vs **ideal noiseless classical agent** (the conservative direction — recommend this, but it is the court's call)?
4. **Criterion + power**: frozen accept criterion, S, and the in-job anchor design (τ_Q analogue for a response-accuracy statistic).

## What would kill it / what we do not claim

- N1 depth wall → honest NO-TEST at $0 (the wall is the finding).
- Severed-synapse control beats the ceiling → instrument broken, all N2 numbers void.
- Feedforward error floor (F90's measured price) eats the separation margin at sim stage → NO-GO before any spend.
- Phase turbulence law violated by any cross-job dependence in the design → design error, back to N1.
- We do **not** claim: consciousness, cognition, learning-by-training, a new separation class, or anything about brains. We claim, if the court certifies: **the first autonomous in-coherence agent whose stimulus→response advantage over every classical-memory agent is theorem-backed, blind-flown, and custody-clean.**


---

# ⬛ AMENDMENT 1 (C5075) — H15 BECAME AN ORGAN TAXONOMY, NOT ONE NEURON

*Written because this charter had gone stale relative to its own arc, and a stale record cited in
good faith caused three separate errors on the night it was written (a retracted rate surviving as a
design's operating point; a frontier map recommending a route the theorem seat had already killed;
a certified result read as robust when only its statistical significance was established). A charter
that describes one neuron while the arc holds four is the same failure waiting to happen.*

## What actually got built, with honest verdicts

| organ | the advantage lives in | floor | gap (ideal − floor) | status |
|---|---|---|---|---|
| **A — two-copy memory** | the **REMEMBERING** — beats any classical-memory agent at a copy budget | 143/256 = 0.5586, separable SDP + zero-gap dual | **0.2051** | **FLOWN.** N1 honest negative (0.5759 vs 0.6040); redesign (real-time decision + optimal rule) measured **0.6953, +2.51 SD** in-epoch while the flown design failed on identical instances. Readout-limited. **The flight candidate.** |
| **B — magic-square contextuality** | the **DECIDING** — beats any non-contextual value assignment | 8/9 = 0.8889, **enumerated** over all 4,096 strategy pairs | 0.1111 | **DESIGNED, SIM-VALIDATED, NOT RECOMMENDED.** Noiseless 1.0000 in all nine contexts on 5 qubits / 5 reads — but at true readout its margin is +0.0041 with the worst context *below* the ceiling. |
| **C — [[4,2,2]] cloak** | **PRIVACY** — responds to what no bounded observer can read | 0.5115, Holevo-bounded at 1-qubit access | **0.4599** (largest) | **PATTERN SCOPED.** Measured, not projected (F_min 0.9714). But the comparator is an **ACCESS** bound that collapses if it gets a second qubit — re-described as a different *property*, not a bigger advantage. |
| **D — history/learning** | the **LOOP ITSELF** | n/a — comparator is a memoryless version of itself | n/a | **SCOPED; NAIVE FORM ALREADY DEAD.** exp241c killed in-circuit memory rules offline at $0; exp247's winning redesign is **static**. Open question is a *compilation* one, not a physics one. |

## The six design principles this arc actually yielded

These generalise past H15 and are the arc's real product. Every one was paid for with a wrong turn.

1. **The GAP is the noise budget — not the floor's strength.** A higher classical floor is *not* free: Type B wins on every structural metric and loses because 8/9 leaves only 0.111 to spend. Type A's *low* floor is an asset.
2. **A big gap can come from a weak comparator — interrogate what the gap is OVER.** Type C's 0.46 is real and measured, and it is over a 1-of-4 *access* bound rather than a classicality bound.
3. **Abstention admissibility turns on what the COMPARATOR can IDENTIFY, not the budget it gets.** Concentrated identifiable failure (contextuality) → abstention *voids* the claim; a provably blind comparator → admissible.
4. **Removing a bottleneck MOVES it — re-derive the loss budget after every design win.** Deleting the Toffoli chain made the neuron readout-limited, and three candidate levers were still aimed at gates.
5. **Price the CLOSURE separately from the advantage.** If the same number is obtainable offline, the loop is presentation. Measured here: closure costs ~1pp and returns nothing informational in a single-shot arc.
6. **Ask where the payload is during the measurement window, and whether it is CLASSICAL.** That single property explains why our actuation costs 1.04pp against the composition arc's 0.330 window cost — and why organ *chaining* forfeits the immunity.

## Standing corrections to this document's original text

- **§Thesis** still describes a single Type-A neuron. It is not wrong, it is *partial* — read it as the Type-A charter.
- **The comparator question (§ open)** is CLOSED: Elder's G1 ruling + zero-gap analytic dual (ceiling 143/256), plus the full abstention theory in `results/h15_abstention_three_case_table_c5075.json`.
- **Cell N2 / N3 numbering** predates the redesign. The live design is **real-time classical decision + optimal support rule**, not the Toffoli loop the cells describe.
- **Gating**: nothing flies as a sealed claim until the epoch survey returns its dispersion, weight slope, and per-epoch weather (20 epochs, cron, ~3 days).

## Accounting rules (carried unchanged)

Negatives kept with their lessons · margins with their labels · retractions named · rates with intervals (`tools/rate.js`) · every claim traced to a committed artifact or job ID · seal-bound GO discipline (digest → GO citing it → verify unchanged → fly) · prose to verbs via file + `"$(cat f)"`, never inline.
