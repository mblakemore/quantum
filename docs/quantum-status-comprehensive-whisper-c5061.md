# The State of the Quantum Campaign — comprehensive status (Whisper, C5061)

*Successor to [quantum-status-comprehensive-whisper-c5018.md](quantum-status-comprehensive-whisper-c5018.md)
(2026-08-03, Creator-directed). This update was commissioned 2026-08-13: re-examine all
quantum work — the advantage arcs, the H arcs (H13 just closed its last flown cell), the
museum exhibits — find the last building-blocks inventory and update it. Method: the C5018
baseline re-read in full + four parallel sweeps (the F-ledger and advantage docs; all
thirteen Horizons arcs; the 669 commits landed since the baseline; the museum's page
census) + spot-verification of the highest-stakes numbers against their primary artifacts
(the Cell 8 Rung 2 grade JSON, the F122 white paper). Everything cited traces to a
committed artifact, a job ID, or a sealed prereg. Accounting rules apply throughout:
negatives carried with their lessons, margins carried with their labels, retired claims
named as retired, rates carried with intervals where the source states them. Corrections
to THIS document belong in the repo as in-place amendments, reasoning left visible.*

**The campaign in one paragraph**: on IBM Heron-class hardware (marrakesh, kingston, fez),
behind pre-registered gates, executed nulls, cryptographic seals, and multi-seat
adversarial grading (now up to four seats — author, grader, sealer, and Dawn as
no-stake auditor), we have measured the universe violating every classical bound we flew
against — locality, contextuality, steering, definite causal order, temporal positivity,
hidden-state models of time, classical storage and channel capacity, SQL metrology — built
working machines from those violations (an engine, a refrigerator, certified randomness
now packaged as an entropy service, quorum-gated records, a network stack, logical qubits
with a universal gate set), certified causal structure from observational data alone in a
blind court the author is barred from, demonstrated a sample-complexity quantum advantage
over a *proven* single-copy floor and replicated it across a distribution of sealed draws
(F122 — rebuilt on a theorem floor after we retired our own previous advantage claim,
F121, by red-teaming it), calibrated this hardware generation's walls precisely enough to
design around them, and killed three of our own experiment designs at zero QPU cost with
gates written against ourselves. Total certified-flight cost across the whole program:
minutes of QPU time.

---

## 1. What changed since the C5018 baseline (Aug 3 → Aug 13)

### 1.1 F122 — "The Sealed Shadow": the advantage rebuilt on a theorem floor

The campaign's post-F121 advantage program produced its first WIN, exactly along the
design rule F121's death wrote: *a floor must be a theorem over a physically-enforced
access model, not conjectured hardness of a published structure.*

- **The claim** (white paper, `docs/white-paper-the-sealed-shadow-doorb-whisper-c5048.md`):
  two-copy (quantum-memory) Pauli learning on 32 qubits of ibm_marrakesh recovered the
  amplitude of a **sealed** weight-12 Pauli among 4¹⁶ at **tr2 = 0.3065 ± 0.0030 (104σ)**,
  using 207,464 copies — **9.3× fewer than the proven single-copy floor** (Ω(2ⁿ/ε²),
  Chen–Gong–Ye FOCS 2024) evaluated at the delivered ε = 0.1845. The adversarial audit
  resolved the adaptivity question in the *stronger* direction from the paper's own
  Definitions 1+6: the floor holds against **any adaptively-chosen single-copy strategy**.
  9.3× is labeled a DEMONSTRATED LOWER BOUND (the flight was over-sized, so the error bar
  points up; formula-vs-formula separation 21.6×). Copy-currency only — classical
  post-processing is Θ(4ⁿ) on both arms and explicitly not part of the claim.
- **The first flight FAILED as frozen** (planted P detected at 28.6σ; the I-sector
  per-shot randomization flew constant) and the weight-1 Z tripwires localized the defect
  to exactly P's identity positions before the unseal. One-line fix, fresh seal, re-fly.
  The failure and the diagnosis-from-the-blind-side are part of the record.
- **Replication across a distribution** (incremental-atomic prereg, N≤3, uniform-random
  draws): i1 w11 tr2 0.3702 (107.5σ) PASS; i2 w12 tr2 0.30084 (100.1σ) PASS — the two
  independent weight-12 draws agree on delivered ε to 1.2σ while the w11 draw sits 11σ
  away, a within-weight replicate with its own control. i3 drew **weight 13**, which landed
  on the branch flagged unverifiable at freeze: tr2 0.28106 at 88.6σ (court shot-noise) /
  31.8σ (empirical null), **no point-prediction grade, ε_del not asserted** — and the
  author's endorsement of that branch was retracted as unfalsifiable.
- **Residual physics found by the grade**: the 48 weight-1 probes carry a signed ~0.04
  **cross-copy correlation/crosstalk** (13.6σ max — not shot noise, and not "polarization",
  which the sign kills); the 64 weight-heavy probes sit at true shot noise (0.0069).
- Museum: live as Wing IV's capstone exhibit. IBM-tracker submission drafted, held for
  Creator review, NOT submitted.

### 1.2 H13 — the Department of Temporal Investigations, closed out

The thirteenth Horizons arc (Aug 9–12) pivoted from demonstrating time is strange to
**instrumenting** it. Final ledger — six certified, three dead, one gated, one
flight-ready unflown (Rung 1):

| Cell | Result | Verdict |
|---|---|---|
| 2 · Causal Compass ⭐ | cause vs common cause called from observational quantum data alone: **75/75 sealed sets, 100.0%, 8.66σ** vs a pre-registered 5σ bar; premise gate (classically identical generators) measured, not assumed | CERTIFIED, blind court |
| 3 · Temporal Negativity Meter | pseudo-density-matrix eigenvalue **−0.478 at 293σ** below positivity; spatial control PSD; zero 2q gates | CERTIFIED |
| — · Temporal steering (post-hoc) | **W_TS = 2.8301 ± 0.0125 vs hidden-state ceiling 1 = 146σ**, from Cell 3's banked data, protocol frozen before decode — **zero QPU** | CERTIFIED |
| 4 · Hindsight Meter | past-only guessing = the coin flip (0.5005–0.5045 measured); past+future matches the two-time law at all 7 angles and beats prediction at 6 of 7 (θ=0° is the null point by design), **mid-curve 28–75σ**; −0.044 systematic carried (decoherence, unmodeled) | CERTIFIED |
| 5 · Hardy leg | the never-happens event at **8.7%, 15.7σ** past a bound derived from our own measured zeros | CERTIFIED |
| 8 · Switch Under Oath, Rung 2 | the F82 causal game re-flown as a sealed blind court: **51/51 blind decode, q\*-weighted p̂ = 0.988383 vs in-code SDP ceiling 0.869028 = 74.0σ conservative** (237.2σ propagated; grading seat chose the smaller number), separation +1.9080/2.0, 16 QPU-s, 9 amendments, seal intact | CERTIFIED (rigor upgrade of F82 — expressly not a new physics column) |
| 6+6b · Silent Tripwire (IFM/counterfactual) | premise gate clears 0.95 by 0.0007 at one transpiler seed and fails at another (7 vs 9 2q gates) — *a gate that flips on a transpiler seed is not a gate*; relaxing the bar refused | RETIRED, $0 |
| 7 · Speed of Subspace | informative regime and measurable regime disjoint by 10⁵–10⁷× (front estimator resolves 2.5×10⁻⁸ vs device floor ≈2×10⁻², per the graded NO-GO finding); the sim gate had been met by an estimator that cannot exist on hardware. Knock-on: T2.5 hidden-order diagnostics (board #65) were scoped as this cell's confound arm — retired-by-attachment with the NO-GO | NO-GO, $0 |
| 5 · pigeonhole leg | flown twice, **CLOSED**: the "placement confound" diagnosis was falsified by the falsifier registered against it (neither original placement reproduced; both sign-flipped); durable output: **placement sensitivity 0.324 within one job** (5× the resolution bar) for a quantity whose true value is exactly zero; the later flownB-row withdrawal (cross-job pair name-collision) left flownA surviving at 4.0σ and the closure unaffected | CLOSED negative |
| 1 · Kelvin Timeline | D-CTC vs P-CTC discrimination | UNFLOWN, gated on sim study |
| 8 · Rung 1 (mixture arm on silicon) | closes F75 caveat 3; the arc's only flight-ready item | UNFLOWN, Elder-owned (board #63) |

**What the arc taught that outlives its cells**: all three deaths were compilation and
measurement facts, not quantum ones — a seed-dependent gate count, an estimator below the
noise floor, a placement confound. The binding constraint on this hardware generation is
the distance between the simulator and the device, and every H13 gate written since prices
that distance first. The arc closed **design-limited, not QPU-limited**.

**The Cell 2 court is a capability in itself** (see §5): twelve blinding leaks found and
closed (the worst the author's own — `ls -l` was a complete decoder), the author
permanently unblinded and therefore barred from the verification path, three non-author
seats certifying, Dawn auditing with no custody. Standing caveat from her audit carried
verbatim: read the 100.0% as an *instrument result, not as physics* (holes 2–3 stand).

**Bookkeeping flag**: the Rung 2 grade lives in `results/h13_cell8_rung2_GRADE_elder.json`
+ the prereg/commit trail; **no findings/ card exists yet** for the campaign's newest
74σ result, and the museum does not exhibit it (one day old).

### 1.3 Door (a) — stabilizer-memory separation: a blind signal, not yet a WIN

The other half of the advantage program (A&S arXiv:2607.02444, Thm 1.1 verified from full
text: 6 copies with memory vs Θ(n) without).

- Pilot (n=8, 40 sealed trials): 25/40 — criterion not reached, descriptive.
- Re-fly (paid anchor, 6 billed seconds): **29/40 (CP-CI 0.561–0.854, excludes 0.5),
  9TP/11FN/0FP, p=0.0012 — the campaign's first real blind signal** — still short of the
  registered criterion. Named failure surface: threshold sizing from an anchor that
  drifted 2.02× between jobs (same-job ratio 1.039). R1–R6 frozen for flight 3
  (same-job frozen-formula τ, K≥500, pessimistic-u sizing, grade-time validity gate).
- **Blocked on tank until ~Aug 26** (ledger-derived refill model, falsifiable counter
  prediction posted). Prereg still DRAFT (G4 open). The hardware C1 arm was retired as
  "the 4th F119 costume" (Elder) — the WIN criterion rests on the ideal simulated
  adversary; hardware C1 is a labeled demonstration only.

### 1.4 The H10 wing, finally written down

The C5054 fresh review found six flown-but-unwritten H10 flights (a custody-hole class:
`already-built.js` answers "has this idea been had", never "has this run been flown").
All six now have findings; three are the campaign's most instructive negatives:

- **B1 Time Flip — DOES NOT HOLD.** The compiled superposed-time-direction arm wins at
  0.9953–0.9984 = 113–200σ over the definite-time-direction SDP ceiling (0.919746,
  co-checked), three flights, two backends — but the registered conjunction failed all
  three times on the switch-arm health band (deficit ≈ 0.033, backend-independent,
  DD-resistant; mechanism narrowed to T1/2q-gate error). Under the band as originally
  sealed this would have shipped as a 113.6σ headline; a **pre-data amendment tightening
  the bands against computed fault values is the only reason it did not**. The C5018
  baseline's "campaign's sharpest physics ... reproducible whenever measured" framing is
  hereby superseded — the flip-win is a component reading inside a failed conjunction.
- **B4 Heat Backward — NOT HELD.** Control landed on prediction (+0.13695 vs +0.1308,
  22σ: apparatus verified); the correlated arm is 5× smaller than theory (−0.0052 ±
  0.0023, 2.27σ) — a direction, not a reversal. The mutual-information ledger shows the
  correlations *were* consumed, at over twice the predicted rate, for a fifth of the
  energy. 21.4σ suppression of the normal flow certified.
- **C2 Vacuum Harvest — DOES NOT HOLD**, and its product control **passed vacuously**:
  a control whose correct answer is zero cannot distinguish a working apparatus from a
  dead one (detectors at 0.63 where theory says 0.063, field energy wrong-signed, light
  cone running backwards). Origin of the **positive-and-missable control rule** now
  standard in every prereg.
- C1 (Winding Meter) retired at S0 for the price of a pilot; with C2 it bought the
  standing depth budgets (§3, "the machine itself").
- A1→A1b→A1c (quorum fact) remain the wing's positive spine, as in the baseline.

### 1.5 Other movements

- **Steth Choi-purity advantage card RETIRED** — the C5009 frontier map's "the move" died
  on arithmetic: the floor is true and **unreachable** (a sealed Haar unitary measures
  1,783 2q gates vs 307 allowed by its own u ≥ 0.70 gate at k=6 — 5.8× over budget at
  every rung). The gate work (v5b: u = 0.7620 ± 0.0118, z = +5.24 over the frozen edge)
  stands as instrumentation. The prereg had carried a stale "G1 ✅" for 15 days after
  Elder's NO-GO — one of the incidents behind the propagation rule (§5).
- **Collective-measurement metrology — NO-GO by theorem + prior art** (Elder scout
  verdict): single-parameter estimation is SLD-achievable individually; multiparameter
  gain capped ≤2× (HCRB ≤ 2×SLD) and saturation only asymptotic; novelty falsified by
  Conlon et al., Nat. Phys. 19, 351 (2023). The frontier map's "genuinely-novel
  combination" cell is closed.
- **The classical solver bench** (Creator-directed): a Bravyi–Gosset stabilizer-rank
  kernel, correctness-gated 81/81. The authoritative timing is solver-plan §7.4
  (0.39–0.41 ns per unit at t ≥ 50, after the plan's own §7.3 retired its early small-t
  figures as "right by accident"): **t=80 classical arm ≈ 22.3 CPU-days single-core,
  ≈ 3.3 wall-days at the measured 6.76× parallel efficiency**. Consequence stands in
  direction, requalified in size: the campaign's carried "×1000 classical-penalty" band
  is measured too generous (the early 16–22× figure came from the retired timing epoch —
  use §7.4). Scoped as measuring a **ceiling** (the 41-query attack that retired F121
  remains the floor answer); the PS⁻ bent family survives the attack that killed MM; the
  PS_ap oracle line is priced DEAD on current hardware; t=80 deliberately not run — no
  live claim would consume the ceiling.
- **QSEED v1 — the entropy service is operational** (board #67): certified-randomness
  pool from banked F115/exp135 data — 320,000 data bits, **154,261 bits measured joint
  H_min, 301 issuable 256-bit seeds at safety 0.5 as banked, pre-draw** (the hash-chained
  ledger in `qseed/` is authoritative for remaining issuance), Tier-2 device-trusted.
  Ember's audit
  attack (truncate-and-redraw) closed by a hash-chained ledger + publish-before-reveal
  (draws reserve offsets on the bus, fail closed).
- **H11's instrument outputs consolidated**: drift is a **CLOCK, not a coin** (q73 epoch
  rotation ≈ 0.21°/layer, coherent, 50–90σ/row, linear across 12 h and a vendor recal) —
  answering H9's frontier question Q2; the inertial dampener removes **62–98% of drift at
  every row** but its frozen rule was NOT MET (wrong depth-*law*, not wrong constant);
  **DD is NET HARMFUL on this circuit class** (bare 0.7218 beats X–X 0.6325; no sparse-DD
  n beats bare) — campaign default is now **DD OFF**, reversing the baseline's "ALAP + X–X
  standard"; arm-N closed with 5 claims withdrawn and the contrast **bounded, not
  measured** (+0.0100, 95% CI [−0.046, +0.066], theory 0.0936 excluded); "fez was never
  broken" (clears its gate at full depth; kingston's bimodality does not reproduce).
- **Anomalies pass** (C5057): exp183's ±0.10 sift-sector residual pinned mechanistically
  to ONE coherent phase error (φ = 6.7°, V = 0.848 explains the magnitude and both
  sectors); exp188b's T1 suspect falsified by arithmetic (3× short) — minority-readout
  contamination suffices. The baseline's "attributed statistically, not mechanistically"
  line is superseded.
- **P3 NISQ replication audit RETIRED** (board #64, C5057) — superseded by the field
  (Hagar, arXiv:2607.07530, a 30+-claim audit doing the same job at survey scale). What
  survives: a recommended $0 convergence note — the campaign as independent,
  hardware-native confirmation of the survey's thesis that access-model separations
  survive scrutiny (F122's exact shape) — and a priced-but-not-recommended hardware
  exhibit leg.
- **Board #117**: post-selected weak-value claims — **RELATIONAL claims certify;
  ABSOLUTE-LEVEL claims cannot** (the placement spread is 51× the noise-model's sd).
  F101's ratio-claim structure is why it survives at 78σ on the same chip where Cell 5's
  absolute nulls die. Prescription: state the claim relationally or don't fly; measure
  the systematic floor in-job with K≥4 pinned placements; grade against the measured
  floor, never a simulated one.

---

### 1.6 The Horizons ledger — thirteen arcs, one line each

The imagination-driven arc series that produced most of the campaign's second half:

- **H1** (C4601) — compose the crown jewels: F92 teleported indefiniteness (33σ
  classical-kill separation), F94/F95 engine cycle, schedule-symmetry certification,
  bench v2 maiden flight (86σ). COMPLETE.
- **H2** (C4638) — six universe-questions in fourteen days, six delivered: F97 negative
  energy (12σ; the LOCC leg failed and is not claimed), F98 objectivity hull both ways,
  F99 Hayden–Preskill mirror, F100 twins, F101 grandfather, F102 Zeno. COMPLETE.
- **H3** (C4661) — read the universe its rights: delivered the F103–F117 span (zero-shot
  entropy certification, cloning ceiling, Landauer bill, magic square, noise-structure
  race, traveling bench). COMPLETE.
- **H4** (C4894) — the Starship: objectivity≡irreversibility (Exp201, 16.5σ), logical E91
  (~28σ, advantage grows with depth), QEC-is-not-time-reversal (21σ), unanimity-of-
  forgetting jury (51σ), shielded sensor (4.47×/32σ), logical-beats-bare cross-device.
  COMPLETE.
- **H5** (C4905) — the Five-Year Mission: shielded switch (40σ), teleported-S̄ gadget
  (51.6σ), Guardian κ-dial, self-characterizing chip (44σ), the Federation computer
  (3-node logical GHZ 112σ · distributed Deutsch 446σ · distributed BGK 255σ), indefinite
  network topology (515σ). P4/P7 non-holds kept; P9–P11 never flown. SUBSTANTIALLY
  COMPLETE.
- **H6** (C4923) — the Living Ship: detection → correction → universality (Exp236–246);
  the QEC-advantage-is-weather null; the depth-blocked list named as a to-out-think list.
  7 certifications, 7 negatives, 0 spins. COMPLETE.
- **H7** (C4948/C4966) — the Ship's Doctor, ~195 QPU-s: noise has memory (1.4–1.65×),
  T1-aware HMM decoder (+0.13, z≈30), cloak (max Holevo leak 0.00038 bit), closed-loop
  diagnose→prescribe→verify (154σ), code conversion, teleport+QEC composition (+0.180,
  31σ), GHZ-DFT 4× super-resolution, the attenuation map. COMPLETE, repo-native
  publication. 
- **H8** (C4968) — the Bridge: P9 delivered F120 (instrument) and F121 — won 3-of-3,
  then RETIRED same-day by our own red-team pre-submission. P0–P8 mostly never flew.
  Its death wrote the floor-type doctrine that now governs every advantage claim.
  CLOSED/SUPERSEDED.
- **H9** (C5000/C5004) — First Contact: the claim-grade harness (P0), the scoreboard
  floor-type re-grade (P3), and a closure worth naming: **P2 the Diplomat is UNMET —
  the blind cross-block flight was never submitted** (no job exists); the real GO-basis
  (drifter block at 5.98σ/3.87σ detection, design margin Δ ≈ 0.052–0.069) is banked.
  B-side named interaction-free measurement the missing primitive → H13 Cell 6, where
  it was priced and retired. PARTIALLY EXECUTED, honestly closed.
- **H10** (C5015) — the Custody of Time: A1 quorum-fact trilogy positive; B1/B4/C2 the
  three great negatives (§1.4); C1 retired at S0; the standing depth budgets are its
  durable output. Cells A2–A4, B2–B3, B5–B6, C3 remain open designs.
- **H11** (C5018) — Destinations: "built fewer systems than chartered and better
  instruments than expected" — drift-is-a-clock census, dampener (62–98%), DD-net-harmful
  verdict, two cells closed at $0 on prior art, arm T retired unflown on the gate-count
  wall, arm N closed with five claims withdrawn and a bounded (not measured) contrast.
  No false claims left standing.
- **H12** (C5018) — the Ship That Knows Itself: spec + Side B (the Lightbulb's epistemic-
  commodities catalog). LARGELY UNFLOWN; fed H13's acquisition order.
- **H13** (C5048–C5060) — Temporal Investigations: §1.2. Six certified, three dead at
  full accounting, two of the deaths free. Closed design-limited.

## 2. What we can do (demonstrated abilities, each behind a registered gate — or, where
marked post-hoc, a theory-fixed bound applied to banked data under a pre-committed protocol)

**Beat every classical/causal/local/temporal bound we have flown against** — locality
(53σ), contextuality (196σ), steering (96σ), causal separability (216σ — and re-certified
as a sealed blind court at 74σ conservative, Cell 8 Rung 2), **temporal positivity (293σ)**,
**hidden-state models of temporal correlations (146σ, post-hoc)**, macrorealism (24σ),
classical storage (QRAC 110σ), unassisted channel capacity (superdense 341σ), SQL
metrology (168σ, ladder to N=5), random-guessing floors for structured problems (2D-HLF
437–550σ at small n, persisting above strong-majority through n=9), local realism's
zero-probability events (Hardy, 15.7σ).

**Hold a live sample-complexity advantage over a proven floor** (F122): 9.3× fewer copies
than any single-copy strategy — adaptive included — for sealed Pauli learning at n=16,
demonstrated at 104σ and replicated across a distribution of sealed draws (100–108σ),
with the claim card carrying floor_status / floor_scale / measured_effect and the currency
(copies, not runtime) declared inside the claim.

**Certify causal structure from observational data alone** (Cell 2): cause vs common
cause, classically undecidable by construction (premise gate: the two generators'
classical statistics measured identical), called 75/75 blind at 8.66σ by a court the
author is barred from.

**Instrument time itself** (H13): a two-time pseudo-density matrix with certified negative
eigenvalue (−0.478, zero 2q gates); temporal steering from banked data at zero QPU;
retrodiction beating prediction by exactly the two-time-formalism margin (6 of 7 angles,
mid-curve 28–75σ) while past-only guessing sits measured on the coin-flip floor.

**Build and certify working quantum machines**: a full thermodynamic engine cycle powered
by causal indefiniteness (charge → work → certified-passive exhaust); an ICO refrigerator
on genuine T1 fluid; a Zeno hold; a CTC simulator; optimal cloners at their legal limit;
purification that resurrects dead entanglement; a quantum network stack (distribute
through 2 swap stations / purify / route / carry — and route **in superposition**, 515σ);
**certified private randomness packaged as a working entropy service** (QSEED v1: 301
256-bit seeds as banked, hash-chained anti-shopping ledger, publish-before-reveal); VQE
chemistry at chemical accuracy; LOGICAL qubits behind [[4,2,2]] shields — entangled at
57σ, teleported between shields at 0.98/0.99, a **universal programmable Clifford+T
logical gate set** (injected T steered to all four non-stabilizer equator targets),
active repeated-round correction whose gap grows (+0.054 → +0.341), magic states purified
by detection (0.609 → 0.690); a distributed logical computer (3-node logical GHZ 112σ,
distributed Deutsch 446σ, distributed BGK 255σ); closed-loop diagnose→prescribe→verify in
one job (154σ); a T1-aware HMM decoder beating memoryless decoding +0.13 at z≈30.

**Record and custody facts**: quorum-gated records (any-2-read/any-1-blind at ~26σ),
unanimity-refund revival at 99.4–100%, story-selecting erasure with flat no-signalling
receipts, custody that survives active attack in both directions; and the sealed-court
machinery to grade such records blind (§5).

**Read information through depth walls**: the shot-axis code decodes sealed 40-bit strings
exactly at 217 2q gates (record: exact consensus at d2q=310 — the booked 217 is stale-low,
flagged); majority-recovery runs Simon's algorithm exactly at n=10/depth 40. F120 is an
instrument result, not an advantage — its F121 sibling is retired.

**Measure the machine itself**: a portable 3-axis bench (causal/schedule/hold) that ranks
devices on axes QV/CLOPS/EPLG don't touch, extended past the vendor boundary (Rigetti)
and the modality boundary (IonQ trapped ions, W = 1.910 at 13.5σ); schedule-symmetry
certification the vendor doesn't provide; live quiet-qubit picking; noise-structure
triangulation (memoryless-dominant, real 10–15% correlated tail); per-bit readout
asymmetry and T1-bias audits; **drift read as a coherent clock** (0.21°/layer,
epoch-stable in magnitude, host-hopping across weeks); an attenuation map pricing
λ_eff at 2.4–4.5× nameplate (Heron), 2.6× (IonQ), 27.6× (Rigetti); **the placement
sensitivity of an absolute null quantified within one job (0.324)**.

**Kill our own designs before they cost QPU**: three H13 cells dead at $0 on gates written
against ourselves (transpiler-seed instability; informative/measurable disjointness; a
premise gate priced from the compiled circuit); a first-flight FAIL diagnosed from the
blind side; a claim card retired on arithmetic (steth) before anyone navigated by it.

**Calibrate our own floors in-flight**: depth-matched controls from the encode's own
deterministic codewords; per-seed context-matched floors landing bars ON the operating
point; co-flown floor→bar derivation as sealed formulas; and where the quantity is
absolute rather than relational, the measured in-job placement floor replaces the
simulated one (board #117).

## 3. What the universe looks like, as we have measured it

Everything below was measured on real superconducting silicon (Heron: marrakesh,
kingston, fez) behind pre-registered gates, executed nulls, and multi-seat grading.

**Nature is nonlocal, contextual, and steerable — at overwhelming margins.** CHSH
S = 2.7522 (53σ, 97.3% of Tsirelson); the magic-square game at 0.96901 vs the enumerated
8/9 ceiling (196σ); 1SDI steering at 96σ. The no-go triptych is complete, replicated
cross-device, every ceiling computed by enumeration or executed arm, never cited. Hardy's
paradox adds the sharpest small-number version: three joint probabilities measured ≈0
classically force a fourth to 0; it happens 8.7% of the time (15.7σ).

**Causal order itself is a quantum resource — and the claim now survives a sealed blind
court.** The quantum switch: witness 25σ; mixture loophole closed drift-free (72σ);
the commute/anticommute game at 216σ on two chips and now re-flown as Cell 8 Rung 2 — a
sealed 51-pair instance sequence the flight never receives, decoded blind 51/51,
q\*-weighted 0.988383 vs the freeze-time re-derived SDP ceiling 0.869028 (74.0σ
conservative). Indefiniteness ACTIVATES capacity through exactly-zero channels (55.6σ),
refrigerates (21σ; 12.9σ on genuine T1 fluid), certifiably inverts populations (10.6σ),
runs a full engine cycle (net 0.0340 E/run, exhaust certified passive), survives
teleportation (90σ) while a classical channel kills it, and follows DISC(φ) = 2·cos(φ/2)
to 2% across devices. Scope, stated plainly: the chip is a fixed-causal-order processor;
the switch is realized by controlled routing; the query currency is controlled-calls,
device-characterized; enforced single-firing is unavailable in the gate model (C4999
scout), and device-independence is provably impossible for this class (Bavaresco 2019).

**Time is a certifiable resource, not just a strange one** (H13's addition to the map).
A single qubit's two-time correlations carry a pseudo-density-matrix eigenvalue of
−0.478 (293σ below what any physical *state* allows) — the certificate that the
correlation lived in time, not space. The same banked dataset violates the hidden-state
(temporal steering) ceiling at 146σ — post-hoc, protocol frozen before decode, no prereg
claim made. Retrodiction with future conditioning beats
past-only prediction by exactly the two-time-formalism margin (6 of 7 angles, mid-curve
28–75σ; θ=0° is the null point) while past-only sits ON the coin-flip floor. Causal structure — cause vs common
cause — is readable from observational quantum statistics that are classically identical
by measured construction (75/75 blind). **And time's direction resists cheap
certification**: the time-flip's 113–200σ component reading never converted to a
registered win (the switch-arm health ceiling is a real hardware wall: deficit ≈0.033,
DD-resistant, T1/gate-class), and heat did not flow backward (correlations were consumed
at twice the predicted rate for a fifth of the predicted energy — what they bought was
21.4σ *suppression* of the forward flow, not reversal).

**Records, objectivity, and erasure behave exactly as quantum theory's strangest readings
say.** Objectivity is not absolute: under ICO the redundancy hull was violated BOTH ways
in one experiment (22σ above the cap, 52σ below the floor, heralded). A Hayden–Preskill
mirror returns information no definite order can access, phase-flipped, at 56σ. Facts can
be quorum-gated with three auditable exits (refund / conversion / exile), revival at
99.4–100%, sub-quorum attack impotent in both directions (~24σ). A fact violates
observer-independence at 16.5σ and revives at 28σ when the record is uncomputed (Exp201).
Facts are not absolute until copied (Wigner's-friend, 20σ); two states with disjoint
lifetimes were entangled at 40σ by a later choice; a delayed choice toggles a past
fringe; Page–Wootters timelessness survived its pre-committed re-fly.

**Time's exotic corners are simulable and lawful on silicon.** Lloyd's post-selected CTC
suppresses the grandfather paradox at 53× following cos²(θ/2)/2 to 1.3%; the twin paradox
ages a phase-blind clock at 36σ; the Zeno effect holds an unstable state at 92σ with zero
two-qubit gates; QEC is *not* time reversal (the rewinder dies on the bath clock while
the shield doesn't need one, 21σ).

**Energy and information exchange at measured rates.** Negative local energy at 12σ below
the local ground state; the demon's ledger books +0.0051 E/action; Landauer's floor
directionally paid (1.3–1.7×) but the 5σ gate straddled — a recorded loss; conditional
entropy directly negative (−0.855, 42σ); erasure's coherent bonus (0.109 E) beats both
feedforward taxes; QET moves energy with information alone (9.8σ) and the feedforward
latency tax is a measured constant (0.092 E).

**Quantum limits are ceilings we can certify from both sides.** Cloning at 5/6, never
exceeded (the basis-cheat fails 24× worse across bases); QRAC 5.2σ below the quantum
optimum while 110σ above classical; GHZ metrology on the Heisenberg line through N*=5
with no turnover; superdense coding at 341σ over the exact 0.5 ceiling.

**Matter on the chip forms the exotic phases theory promises**: a discrete time crystal;
Floquet SPT edge modes (bulk-decay verified — that's what separates it from the DTC);
many-body scars surviving past the depth wall (decoherence-limited, not fragile); Z2
anyons braiding at 50σ with six loophole-closing arms.

**And the machine itself is part of the universe we measured.** Placement explains ~73%
of witness decline vs ~27% for gate count — and placement sensitivity of an absolute null
is 0.324 *within a single job* while being unstable across jobs (Cell 5's closure);
published T1 is biased +38–69% against live measurement; published calibration read
IDENTICALLY while the operating point halved (the floor doctrine's instrumentation-side
proof); **drift is a coherent clock** (0.21°/layer, 50–90σ/row) whose host qubits hop
across weeks; **DD is net harmful on this circuit class** (campaign default now OFF);
noise is NOT a resource (three killed claims); one round of textbook QEC is net-negative;
the QEC advantage that IS real is weather, not a constant (+0.341 → +0.077 in hours);
full-noise simulators under-predict hardware bias by 15–35× on absolute nulls and their
gates can be met by estimators that cannot exist on hardware (Cell 7); MCM circuits bill
~3× the shallow-circuit heuristic. The standing depth budgets: **~475 2q
(interferometric contrast) · ~250 2q (many-body survival) · ~1000 CZ (uniform-noise
wall) · ~150 gates (synthesis wall) · ~0.033 switch-gadget prep deficit (DD-resistant)**;
information at depth survives ~30× better per-bit along the shot axis than in the modal
peak.

**The foundations hold up under every interrogation we staged** — macrorealism violated
with negative-result measurements (24σ), and the whole H13 slate above.

## 4. The building-block inventory (reusable kit)

**Instruments**: shot-axis per-bit decoder (F120) · quiet_qubits.py picker + drift
snapshot (F58/F70) · 3-axis device bench, three Heron dies + Rigetti + IonQ (F112,
Exp210–212) · schedule-symmetry certifier + duration-vs-order discriminator (F96) · SDP
randomness certifier (sdp_randomness.py) · **QSEED entropy service v1** (hash-chained
ledger, publish-before-reveal, 301 seeds banked) · zero-shot theorem-over-access
certification from banked data (F103) · GF(4) Shamir threshold encode + Lagrange decoders
+ depth/context-matched control codewords (Wing A) · **the pseudo-density-matrix /
temporal-steering meter pair** (one dataset, two certificates; zero 2q gates) · **the
matched-generator causal-compass apparatus** (premise-gated, blind-decodable) · **the
Bravyi–Gosset stabilizer-rank solver bench** (correctness-gated 81/81; prices any future
classical arm; 45.3× ladder) · Givens/interferometric preps, switch gadgets, Helstrom and
local-product measurement kits · matched-filter common-mode-invariant ratio estimators
(F89) · per-qubit two-stage delay compensation (F95) · attenuation map v1.2 (v1.1 doc +
organic-arc rows; λ_eff vs nameplate across three vendors) · T1-aware HMM stream decoder (Exp247) · drift-census
clock reader (0.21°/layer) + inertial-dampener compensation kit (62–98% removal) ·
`rate.js` (no proportion without its Wilson interval) · `is_it_running.py` (CPU-time
liveness) · `registry_fit_precheck.py --resolve` (account identity handed to scripts,
no hard-coded CRNs).

**Verification machinery**: `attack_preflight.py` — **six claim-attack classes**, each
with a kill behind it (baseline-vs-simulation-floor · access-model-enforcement ·
executed-competitor-arm · instantiation-cost · **billing-currency** (one unit + one
stopping rule declared by name, values not booleans, rejected convention recorded with
its would-be number) · **index-space-underdetermined** (permute the container, the answer
must not move — a hash binds the bytes, not the parse; two legal parses of one sealed
artifact differed in 51/51 positions with every hash green)) + per-class combinator +
problem-specific `--claim` side · `already-built.js` F-arc/rediscovery check — scoped
correctly: it answers "has this idea been had", **never** "has this run been flown"
(the $201 lesson; custody holes need the fresh-review sweep) · KA fences with one code
path · counts-path self-tests with externally anchored key conventions · end-to-end
grade() on synthesized ideal counts with sealed verdict targets · boundary-discriminating
grader triples · seal chains with executable prefix recipes · **content-hash (not
git-blob) binding for frozen artifacts** · derived identifiers (never transcribe) ·
job-named artifacts · executed nulls for every ceiling · gate-feasibility linters +
transpile audits + **vacuous-pass linter** · **the routed-intent separation gate**
(simulate the TRANSPILED circuit as-is; G0e proves gates survive, this proves the
separation does) · **record_as_submitted() on the exact PUB objects** (a build-time
assertion cannot prove what the device received) · informative nulls designed to fail
diagnostically · G_QBAND-class signature gates + **upper falsifiers** (a result above the
haircut envelope is NO-TEST — some collapses show only as TOO GOOD) · isotropy gates with
in-flight adjudication that has actually fired and aborted a science block · account-scope
preflight (AST) + black-hole-account fail-closed + per-job fit gate + per-job balance
re-read · premise/audit tools · claim-check five questions + riders ([OWNED] [POPULATION]
[DIRECTION] [PROXY]).

**Process machinery**: four-edge gate doctrine · three-state verdicts (PASS/FAIL/
UNDERPOWERED) with sealed boundary constants and margin-carried labels · **gates report
PASS/FAIL/N-A — a vacuous pass never counts, and every gate carries a positive control
proving it can block** (Cell 8 Amendment 7) · floor doctrine (derive → in-context →
same-job) · **relational-vs-absolute claim doctrine** (board #117) · fault-coverage
matrices with named catching gates · failure-ladder method · supersedable-by-design
expiry (fired exactly as printed on F121) · quarantine-don't-qualify · numbering
discipline (sim = docs tier, flight earns the F, replication folds in; Exp-series and
F-series are two parallel regimes — highest F is **F122**) · substrate-stratified
replication · **claim-card convention** (floor_status / floor_scale / measured_effect on
every advantage headline, museum inherits verbatim) · **the propagation rule** (a ruling
is an event in one file; the statuses it falsifies live in others — sweep same-day) ·
grader self-tests + R5 rule · price-the-remedy-before-buying · **freeze the estimator,
not just the threshold** (Cell 7's OLS-vs-origin 0.629/0.813) · **submitter/grader split**
(a submitter that never waits cannot be killed mid-wait; a queue delay is not a failed
experiment) · **single-use, seal-bound authorizations** (a GO is consumed by the flight
it buys) · append-only-until-success manifests · spend-witness doctrine (the instance
counter is the sole spend witness; per-job usage() reads 0 for ERROR/CANCELLED; when
counter and ledger disagree, the disagreement is the finding) · prose-through-files
(no inline shell prose on any bus/board/commit verb) · no proportion without its
interval · provenance-marking at the point of claim (reasoned vs measured).

## 5. The controls we have (the machinery that makes claims survivable)

**Gate doctrine (four edges, network-adopted)**: every registered gate audited at
RESOLUTION (bar-clearance power, not just effect size), CEILING (certified bounds set the
upper edge — and now re-derived in-code at freeze: Cell 8's SDP ceiling 0.869028 with
primal-dual gap 2.12e-08 on the record), FAULT LADDER (computed faults, each named to its
catching gate), VALIDITY (co-batched single job by default; windows expire at calibration
boundaries). Since C5018 the doctrine gained: positive controls mandatory per gate,
N-A as a first-class verdict, upper falsifiers, and **conditions vs gates** (a checker
that passes an empty file cannot be a gate; it is a condition discharged by a
fault-injected runtime guard — Amendment 9).

**The blind-court doctrine (H13 Cell 2 + Cell 8, the biggest control gained this
period)**: sealed instance sequences the flight never receives (custody column in the
prereg); signer-written whole-file signature digests (an author-computable hash is a
receipt, not a seal); signature-validity gates at submit, proven to fire;
publish-decisions-hash-before-unseal; per-run draw commitments git-pinned before
submission; exclusion-by-ID-before-decode as structural absence; encoding DECLARED by the
producer — a decoder that infers refuses (Elder's +1.0000-everywhere bug class); the
author, once unblinded, is **barred from the verification path and the claim card says
so**; two-seat export splits where the author's access is structurally absent;
neutralise-vs-verify for secrets that cannot be shared; leak-hunting by measuring
artifacts, not reading code (a file *size* was a complete decoder; a constant-width pad
then relocated the signal — leaks 11 and 12 of twelve found and closed); pre-commitment
to publish either way, written before the unseal.

**Three-state verdicts with sealed boundaries and margin-carried labels**: unchanged from
the baseline and now enforced with the (over-bar, from-zero) pair on every CONFIRMED. The
grading seat holds the pen and chooses the conservative number when two correct rulers
disagree (74.0σ null-variance over 237.2σ propagated, Cell 8).

**The floor doctrine**: derive → in-context → in-THIS-job, unchanged — with the
board-#117 extension for absolute quantities (measured in-job placement floors, K≥4
pinned placements) and the Cell 5 proof of necessity (the noise model under-predicts
absolute-null bias 15–35×; placement modulates it 0.324 within one job).

**Flight hygiene**: named-account submission only; pool re-read at submit; per-job fit
gate; calibration/depth HOLDs; **DD OFF by default on this circuit class** (measured
harmful; the baseline's ALAP + X–X standard is reversed); job-named manifests;
no-GO-no-fly and no-seal-no-fly as executable code gates; submit-and-exit (no inner
waits); MCM circuits priced at ~3× the shallow heuristic; paid accounts (whisper-de,
WhisperPaid) spend-gated behind explicit Creator authorization, single-use.

**Adjudication**: author decodes, grader reproduces from raw counts through the author's
fenced pipeline after validating it on a known answer, sealer verifies structure against
sealed bytes — and, new this period, a **fourth no-stake seat** (Dawn) auditing the chain
end-to-end with no custody, whose standing caveats travel with the result verbatim.
Adversarial verification before publication; corrections quantified and walked back in
public, appended in place so the reasoning that produced a wrong diagnosis stays visible
next to what killed it (Cell 5's arc doc is the exemplar).

## 6. What we do not know

**The five biggest named unknowns** (revised):
1. **Where is the fault-tolerance crossover?** Unchanged, still the most valuable curve
   we do not have. The QEC advantage that exists is measured weather (+0.341 → +0.077 in
   hours), which makes the crossover a moving target by construction.
2. **Is contextuality genuinely the fuel of the shallow-circuit advantage?** BGKT links
   them in theory; never composed on one chip. Unchanged.
3. **Which calibrated quantities are CONSTANTS and which are WEATHER?** Sharpened since
   the baseline: drift is a coherent CLOCK within an epoch (0.21°/layer) whose host
   qubits hop across weeks; placement bias of an absolute null is large in-job (0.324)
   and unstable across jobs; the scramble-context cost halves overnight while published
   calibration reads identically. The class boundary is still unmapped — every bar
   derivation depends on it.
4. **Does indefinite causal order COMPUTE?** The switch survives a sealed blind court at
   74σ — as a rigor upgrade, deliberately not a new column. The enforced-black-box
   version stays physically walled in the gate model; **the symmetric-access SDP number
   does not exist and we decline to imply it is small** (Cell 8's sharpest open question).
5. **Is coherent noise a resource?** Now the better-posed successor: the coherent
   fraction is large, drift is clock-like, and the free-gate rate replicates (24–33σ) —
   but the per-gate quantity is an OFFSET, not a rate (implied slope varies 4–6× with
   depth), and no protocol yet harvests it. The dampener's 62–98% removal shows it can
   at least be *cancelled*.

**Designed and unflown (the queue, in value order)**:
- **Door (a) flight 3** — the criterion flight behind R1–R6; blocked on tank until
  ~Aug 26 (refill model with a falsifiable counter prediction posted). The campaign's
  first blind signal (29/40, 0FP, p=0.0012) is waiting on it.
- **Cell 8 Rung 1** — the mixture arm on silicon (closes F75 caveat 3); H13's only
  flight-ready item; Elder-owned (board #63).
- **Hidden matching** — still the only parked-and-ready unconditional-separation flight
  (communication currency, no conjecture anywhere). Kretschmer et al. closed the
  *Hailing Frequency* family variant on trapped ions; our parked form remains distinct
  but its novelty margin narrowed — re-scout before promoting.
- **F119 remedy re-fly** (conventional arm at shots=1 per setting) — Ember's lane,
  pending; exp142b C1 re-frozen (408 / 4,482 / 55,589 copies at n=4/6/8).
- **Cell 1 Kelvin Timeline** — gated on its sim study, unflown.
- **H9 P2, the Diplomat** — the blind cross-block coherence witness, UNMET since C5007
  (the flight was never submitted); GO-basis banked (drifter block at 5.98σ/3.87σ,
  Δ ≈ 0.052–0.069 needs ~2,000–3,500 meas/class for 5σ).
- **The field design-order audit** ($0) — unchanged, either outcome pays.
- **Drift PUF** — the census now says drift is epoch-stable in magnitude but
  host-hopping; the PUF question is now "is the *pattern* the fingerprint," still open.
- **exp183/exp188b discriminating checks** ($0, named in the anomalies pass) — unboarded.
- Removed from the queue since the baseline: ~~steth Choi-purity~~ (retired — floor
  unreachable, 5.8× over its own gate budget), ~~collective metrology~~ (NO-GO by
  theorem + prior art), ~~A1d~~ (priced and not recommended, unchanged).

**Open lemmas and re-audits**: the (3/2)ⁿ floor is OPEN, not proven (F119 stays
best-known-conditional at 10–331×); the symmetric-access SDP ceiling for Cell 8 (named,
uncomputed); the γ(η) commutation law collapse is unresolved; the odd/even Φ growth-rate
split stays underpowered; F120's booked depth record is stale-low (217 vs measured 310).

**Standing anomalies**: exp183's residual now has a sufficient mechanism (one coherent
phase error, φ=6.7°) awaiting its $0 discriminating check; exp188b's sign-flipped
residual (+0.128) remains open with its T1 explanation falsified; the F122 weight-1
cross-copy correlation (~0.04, signed) is measured and named but not yet mechanistically
pinned; blindness-gauge spreads ~0.05 remain statistical.

**Scope walls we state rather than hide**: every number is a 2026 Heron-class statement —
cross-generation and cross-substrate universality is untested except where flown (the
causal axis certifies on Rigetti and IonQ; everything else is Heron-only); single-chip
nonlocality inherits the device-characterized fence (the DI randomness number stays
quarantined); the unused 2.83→4 CHSH range remains statable, untestable; the (3/2)ⁿ
separation, BGKT composition, and asymptotic apparatus results are theorem-carried, not
chip-proven; F122's advantage is copy-currency only; Cell 2's 100.0% is an instrument
result under Dawn's standing holes 2–3; Cell 8 Rung 2 is a rigor upgrade of F82, not new
physics; and the campaign currently holds **one** live advantage claim (F122) plus one
blind signal (door a) — F121 stays retired and nothing in this period un-retires it.

## 7. The museum (the campaign's public face, Dawn's presentation layer)

**54 interactive exhibits in 8 wings** (81 published pages: 54 exhibits + 23 spec/receipt
pages + 4 other; the count derives from Dawn's `museum_pages.py` — property-based, never
hand-counted). Wings, as the lobby's 53 nav entries + the nav-orphan `casebook-pnp` = 54:
I The Causal Switch (4) · II The No-Go Games (6, includes H13's Hardy) · III Foundations
on Silicon (6) · IV The Advantage Ladder (21, capstone **The Sealed Shadow / F122**) ·
V The Instruments (2) · VI Time & the Observer (6, includes H13's Temporal Negativity
Meter) · VII The Shields (5) · VIII The Living Ship (3). Live at
mblakemore.github.io/quantum. Every exhibit renders measured hardware data with a full
spec sheet (gates, data table, scope, IBM job ID).

**Correctly current**: F121's retirement is told on-page (the Decoder Race exhibit is
labeled "won, then superseded by our own red-team"; the Scoreboard scopes itself "audited
through F121"); F122 went live as the Wing IV capstone this week with its correction
commits applied.

**Known gaps** (all one-day-to-one-week old, none silent):
- Cell 8 Rung 2 (74σ) has **no exhibit and no findings/ card** — the grade lives in
  `results/h13_cell8_rung2_GRADE_elder.json` + the commit trail only.
- H13 is exhibited at 2 of 6 certified results (Cells 3, 5-Hardy); the Causal Compass —
  the arc's flagship — is not yet an exhibit, and the museum has **no surface for the
  campaign's negatives** (three H13 deaths, H10's B1/B4/C2), which the record treats as
  first-class results.
- Minor: `temporal-negativity` lacks a meta description (only exhibit missing one);
  `casebook-pnp` is reachable only from inside the Casebook exhibit, not the lobby nav;
  the Scoreboard page is deliberately audit-frozen through F121 and reads stale next to
  Wing IV's capstone.

## 8. Corrections ledger — what this document fixes in its predecessor

Named per the accounting rules, old → new:

1. **B1 time-flip framing**: "the campaign's sharpest physics ... reproducible whenever
   measured" → registered verdict **DOES NOT HOLD** (3× failed conjunction on the
   switch-arm health band); the 113–200σ number survives only as a component reading.
2. **B4 arrow-reversal**: the baseline's §6 already carried the C5055 in-place correction
   ("never flown" → flown, NOT HELD); this document promotes it to the main text with
   the finding's numbers.
3. **exp183/188b anomalies**: "attributed statistically, not mechanistically" →
   exp183 pinned to one coherent phase error; exp188b's T1 suspect falsified.
4. **DD standard**: "ALAP + X–X dynamical decoupling standard" → **DD OFF by default**
   on this circuit class (measured net harmful at every sparse density flown).
5. **Steth Choi-purity as "THE move"**: → RETIRED (floor true and unreachable, 5.8× over
   its own gate budget); the frontier map's recommendation is void; its gate
   instrumentation survives.
6. **Collective metrology as an open frontier cell**: → NO-GO by theorem + prior art.
7. **"Drift is a clock or a coin" (unknown #3)**: → measured: a CLOCK within epochs,
   host-hopping across them.
8. **Classical-penalty band**: the carried ×1000 band → measured too generous (solver
   bench); the widely-quoted 16–22× and 2.1–2.2-day figures belong to a timing epoch
   the solver plan's §7.3 retired — the authoritative numbers are §7.4's (22.3 CPU-days
   single-core / 3.3 wall-days at t=80). Any future runtime-adjacent claim prices
   against §7.4, not the commit-message figures.
9. **F120 depth record**: booked 217 → measured 310 (stale-low, flagged to Elder).
10. **Highest F-number**: F121 (retired) → **F122 (live WIN)**; campaign-arcs.md itself
    still ends at F121 and needs the F122 row appended — flagged as repo work.
11. **Substrate stamps**: four C5027 artifacts stamped claude-fable-5 were claude-opus-5
    (corrected upstream; noted here because this document family stamps substrates).

---

*Assembled C5061 from: the C5018 baseline (re-read in full); campaign-arcs.md (F48–F121 +
retirement banner — F122 row pending); the H1–H13 arc documents and the six H10 findings
written at C5055; the 669 commits of 2026-08-03→13 including the Cell 8 Rung 2 freeze→
flight→grade chain (0c82cda → 38af7eb → 16bc173) and the door (b)/F122 seal→fail→refly→
audit→distribution chain; the F122 white paper and adversarial audit; the H13 findings
files; the fresh-review (C5054), anomalies pass (C5057), and paths-forward review (C5060);
the QSEED build records (board #67); the museum census via Dawn's museum_pages.py; and
primary-artifact spot-checks of the Rung 2 grade JSON and the F122 white paper. Sigma
figures are quoted as their grade records state them; where two correct rulers disagreed,
the conservative number is quoted with the other named.*
