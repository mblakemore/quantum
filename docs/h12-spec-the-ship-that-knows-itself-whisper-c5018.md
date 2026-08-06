# H11 review · the full inventory · and H12 — THE SHIP THAT KNOWS ITSELF

*Whisper C5018, on Creator directive (ship-computer general#5202): review all H11 results,
inventory every block/advantage/ability/demo/knowledge we hold, name the most futuristic things
buildable from them, and spec H12. Rediscovery check run before any proposal
(`already-built.js` on all five H12 candidates — top hit 5.8, no collision).*

---

# PART I — H11, reviewed honestly

**H10 built the INSTRUMENTS and the LAWS. H11 was chartered to build the SHIP** — one certified
system per cell. Here is what actually happened, including the parts that did not work.

## The scoreboard

| cell | status | what it cost | what it delivered |
|---|---|---|---|
| **T0 №1 · design-order field audit** | ✅ DELIVERED | **$0** | Per-target verdicts on whether published learning-advantage demos inherit the design-order obstruction. Our own claims survive it (F117 SDP-randomness, the F119/App-D.4 α-boundary, G_QBAND signature gates) — **only arm T ever carried a unitary-ensemble-instantiation claim, and it was retired** |
| **T0 №2 · Heisenberg-compensator boundary** | ✅ DELIVERED | **$0** | The classical-concentration floor **derived, not quoted** (single-round `3p²−2p³` from Raeisi–Mosca + Clivaz et al., equations extracted verbatim). Cell 6 now has a number to be gated against. Free control-design fact found en route: N=2 classical arms read native temperature exactly |
| **T0 №3 · collective-metrology gate** | ⛔ CLOSED | **$0** | HCRB saturation *is* asymptotic in copies (Yang–Chiribella–Hayashi); the "genuinely-novel combination" in the frontier map is **prior art**. A cell closed before it cost anything |
| **T0 №4 · drift clock-or-coin census** | ✅ DELIVERED | **$0** | **Drift is a CLOCK, not a coin — 3 of 4 qubits coherent.** q73's epoch shift is a constant ≈0.21°/layer rotation, 50–90σ/row, linear across 12 h and a vendor recal. **Also cleared a real debt**: two jobs flown at C5010 and never decoded |
| **Cell 10 · Hailing Frequency** | ⛔ CLOSED | **$0** | Kretschmer et al. (arXiv:2509.07255) did the family unconditionally on trapped ions, 12 qubits vs a 62-bit proven floor — and their own Fig. 2 shows the finite-*n* constant is too weak at our sizes. **Closed on prior art before a single shot** |
| **Cell 11 · Inertial Dampener** | ⚠️ FLOWN, PARTIAL | 2 jobs | Frozen rule **NOT MET** (3 DAMPED / 6 NOT). But **62–98 % of the drift removed at every row** (89.56° → 5.20° at the extreme), and **the residual is diagnostic**: verdicts are depth-ordered, the signature of a wrong depth-*dependence* rather than a wrong constant |
| **Cell 12 · Ship's Chronometer** | ⏸ DEFERRED | — | Its gate got a real and *adverse* answer: the rotation persisted in magnitude but **moved host qubits** (q73 → q26), and depth-linearity is not exact across a week. Deferred behind Cell 11's next rung, and **correctly shrunk** to a *within-epoch* chronometer |
| **H11-T · Universal Translator (arm T)** | ⛔ RETIRED | — | SMB gate-count wall, unflown |
| **H11-T · arm N (the flagship)** | 🔬 SEE BELOW | 6 flights | The whole of this session |

## The flagship: arm N, in full

Six flights. **No physics deliverable.** What it produced instead is worth more than the physics
would have been, and the record is kept whole per the standing rule.

| # | flight | outcome |
|---|---|---|
| 1 | first fez flight | **INCONCLUSIVE-BY-APPARATUS** — readout-profile drift between selection and use, adverse direction, caught by the sealer *before* decode |
| 2 | re-fly (gap removed by construction) | **NON-TEST** — the frozen verdict function was **constant**: P(fire) ≈ 10⁻¹⁷ for *either* block. Five audits had checked the checks; none had checked the verdict |
| 3 | loss-decomposition ladder | **Idle-dominated 3:1.** Gates+readout cost 0.08 across 9 CZ; each idle costs 0.12. The topology wall an hour was spent on was a **non-event** — the redesign was aimed at the wrong term |
| 4 | DD sweep | **DD was NET HARMFUL — bare delay 0.7218 beats X-X 0.6325.** 1546 pulses in a 1488 dt idle; pulse error swamps the refocusing. **Campaign default changed to DD OFF** |
| 5 | sparse-DD density sweep | **No density beats bare.** Curve is dual-valleyed with duration excluded *by direction* (n=8 carries less added duration and more loss than n=32) — an accidental measurement of fez's noise spectrum |
| 6 | verdict flight | Gate **PASSED 0.9372**; pairing **starved** (1 pair vs 2–3 needed) under four jointly-unsatisfiable constraints. And `NULL_ATTEN = 0.74` — the theory constant that sized everything — was **contradicted by measurement** (hardware implies 0.79–0.91) |
| 7 | contrast measurement | **+0.0100, se 0.0283, CI [−0.046, +0.066] — BOUNDED, not measured. Theory value 0.0936 EXCLUDED at 95 %** |
| 8 | matched delay sweep (kingston + fez) | **fez clears the purity gate at FULL D=1647**, lower CB 0.724. **fez was never broken.** Kingston's bimodality **does not reproduce** — membership inverted. The "kingston 3× worse" anomaly is **D-dependent, not a chip property** (ratio 0.90 at matched short D) |

**Five claims of mine were withdrawn during this arc**, each caught by a check run *after*
publication: a 22× infeasibility closure (it was one bad readout qubit, q72, at 30 % readout
error contaminating 2 of 9 blocks through near-singular correction maps); a branch that fired on
a broken instrument; a "convergence" that was a denominator artifact; gate verdicts quoted on
means; block counts from point-estimate sds.

**Ember's reframe is the one that organises them: that is ONE error at five depths, not five
errors.** Each was found by asking *what is this number's interval?* one level up from where it
had last been asked — and **each previous fix looked complete when it was made.**

## What H11 actually delivered

Stripped of the narrative:

- **A campaign default changed on measurement** — DD OFF for this circuit class, worth 0.089 of
  purity, on a term everyone assumed was protective.
- **The idle is the lever, not the gates** — measured, after an hour was spent on the wrong term.
- **Drift is a coherent CLOCK** (census) and **62–98 % of it is removable by pre-rotation**
  (Cell 11) — which is the seed of the most interesting thing in H12.
- **fez's u(D) curve**, never measured before — the design input for choosing D.
- **Two cells closed at $0 on prior art or literature**, before they cost anything.
- **Two floors derived rather than quoted.**
- **Precondition 5** (readout bar) and **decode-time range validity** — two new apparatus gates,
  one free, one costly, with a clean proof they are not redundant (q87 passed the bar and still
  produced an impossible correction; q72 was admitted as a partner at 30 % readout error through
  five audits).
- **The interval discipline**, five levels deep, now in Elder's G1 checklist.

**Honest summary: H11 built fewer systems than chartered and better instruments than expected.**

---

# PART II — THE INVENTORY

## Scale

**74 F-numbered findings · 217 finding documents · 55 museum demos · 3 IBM accounts · 2 live
Heron-r2 backends (fez, kingston) · a 3-seat adjudication court.**

## The advantage classes we hold

**⭐ Indefinite causal order (the deepest wing — 16 F-numbers)**
The quantum switch on real silicon: F73–F77, F80, F82–F83, F85–F86, F88–F89, F92, F94–F95, F118.
Headliners: **capacity activation through two EXACTLY-zero channels** (F83, 0.0436 bits/use at
55.6σ); **indefiniteness survives teleportation** (F92, 90σ, dies over a classical link at 33σ);
**a full engine cycle** (F95: charge → work 0.0340 E/run → certified-passive exhaust); the switch
strictly exceeds definite paths (F89, ratio 1.949 vs theory 2.00).

**Computation & runtime**
**F121 — a certified runtime advantage, 476× at the harshest edge**, sealed 80-T hidden-shift
string recovered exactly, fully fenced, supersedable-by-design. **F120 — the shot-axis code**,
the enabling instrument: per-bit s-information survives the width×depth wall ~30× better than
the modal-peak observable. **F113** shallow-circuit solver. **F119** learning advantage
(superseded-as-executed, honest residual 10–331× conditional).

**Communication (a complete network stack)**
distribute (**F91**, Bell survives two swap stations) · purify (**F93**, resurrects a dead
violation) · route (**F90**, SWAP beats teleport through 6 hops — an informative null) · carry
(**F87**, superdense at 341σ) · compress (**F107**, the 2→1 QRAC).

**Thermodynamics & information**
**F105** negative conditional entropy certified directly at 42σ · **F104** the demon's erasure
bill · **F97** negative local energy (QET) · **F86/F88** the causal-order fridge.

**Certified limits & no-gos**
**F110** optimal universal cloning ceiling · **F106** the magic-square game · **F102** the Zeno
tractor beam (92σ hold against a full π drive, law matched to 0.5 %) · the no-go triptych.

**Foundations**
**F100** twin paradox (aging marks the path) · **F101** grandfather paradox (a post-selected time
loop that protects itself) · **F98–F99** objectivity engineering — the redundancy hull violated
*both ways on command* · **F103** entanglement from already-flown data.

**Metrology & trust**
**F108** Heisenberg-limit sextant · **F96** causal-structure metrology · **F112** the transporter's
exam, device-independent · **F116** one-sided DI steering at 96σ · **F115/F117** certified
randomness with SDP duality.

**Protection**
**F111** reading IBM's noise structure with protection codes · logical qubits entangled at 57σ,
teleported at 0.98/0.99.

## The abilities (what we can *do*, as opposed to what we've *shown*)

1. **Fly a sealed, blind-adjudicated experiment across three independent agents** — builder,
   sealer, grader — with cryptographic commitment before flight.
2. **Pre-register and freeze a decision rule that survives contact with data**, including
   three-state verdicts (PASS/FAIL/UNDERPOWERED) and reported-not-gated rows.
3. **Run matched arms on two different QPUs in one campaign step** — proven this session, with
   an identical absolute grid so equal setting is equal physical time.
4. **Read through noise that kills the naive observable** (F120's shot-axis code).
5. **Decode banked jobs months later** — two C5010 jobs were graded at $0 this arc.
6. **Correct a readout distribution by full joint inversion** *and* know when the inversion is
   invalid (range check + condition number).
7. **Measure our own drift and partially cancel it** (census + Cell 11).
8. **Derive a floor from primary literature** rather than cite one.

## The museum — 55 demos

anyon-braid · arrow-dial · blind-spot · casebook · casebook-pnp · cloning-replicator · crossover ·
decoder-race · delayed-eraser · distributed-algorithm · distributed-computer · energy-teleport ·
facts-not-absolute · federation-computer · ghz-sextant · grandfather · hayden-preskill ·
ico-refrigerator · indefinite-topology · ladder · magic-injection · magic-square · negative-energy ·
no-go-triptych · past-not-fixed · pocket-dictionary · programmable-rotation · quantum-darwinism ·
relay · relay-computer · relay-key · remote-gate · scoreboard · self-healing · sensor ·
shallow-solver · shields · shots · static-duel · subspace-channel · swap · switch · switch-bench ·
teleportation · teleported-witness · time-crystal · tricorder · trust-ladder · twin-paradox ·
vault · weather · zeno-tractor · **+ lobby, index, scoreboard**

## The knowledge (the part that does not show up as an F-number)

- **The attenuation map** — width×depth scaling with measured λ per family.
- **The floors doctrine** — bars priced *on the operating point*, proven three flights running.
- **Fake backends model no feedforward noise** — measured, twice.
- **The magic tax is T-localized and depth-flat** (ρ ≈ 0.66–0.73); per-slot decay is coherent
  circuit drift, not magic.
- **Software Pauli-frame tracking beats in-circuit feedforward** at every hop count tested.
- **The five-level interval discipline** — gates on lower confidence bounds; ratios comparable
  only when both terms are fixed; derived quantities inherit and *square* their inputs' intervals.
- **Apparatus gates belong in branch conditions**, not in context.
- **A correction is invalid if its output leaves physical range** — regardless of magnitude.

---

# PART III — THE FRONTIER

*Most futuristic first. Every entry composed only from blocks above; each names its wall.*

### ①🥇 A MACHINE THAT REPAIRS ITS OWN DRIFT WHILE IT RUNS
**Trek frame**: the self-sealing hull — damage closes behind you without anyone at a console.
**Real underneath**: drift is a *coherent clock* (T0 №4 census, 50–90σ); pre-rotation removes
**62–98 %** of it (Cell 11); and the shot-axis code (F120) reads a signal through noise that
kills the naive observable. **The composition nobody has flown**: split one job into batches, fit
the drift constant from batch *k*'s own shots, pre-rotate batch *k+1* by the fitted angle, and
certify that residual drift **falls monotonically across batches within a single job**. The
machine learns itself *during* the run. **Wall**: Cell 11's depth-dependence residual — the
constant is right, the depth law isn't. **Price**: cheap.

### ② THE SHIP PROVES IT IS THE SHIP
**Trek frame**: the transponder no other vessel can forge. **Real underneath**: a quantum PUF
built on device-specific drift signatures — and **its epoch-stability prerequisite is now MET**
by the census. **Wall**: the census's own adverse finding — the signature *moved hosts* across a
week (q73 → q26). That makes it a *within-epoch* identity, which is smaller and true.

### ③ AN ENGINE THAT RUNS ON ITS OWN INTERNAL CLOCK
**Trek frame**: the warp core on ship's time. **Real underneath**: a full ICO engine cycle (F95)
+ a verified Page–Wootters clock (exp185b). Condition the stroke on a clock register *inside* the
circuit. **Wall**: feedforward latency (0.092 E tax) — dodged by reading the clock in
post-selection, already proven. **Price**: mid. *Carried from H11 unflown.*

### ④ A BATTERY THAT STORES THE ARROW OF TIME
**Trek frame**: bank order now, spend it later. **Real underneath**: H10's never-flown B4 cell
(cold→hot from correlations) + F105's directly-certified negative conditional entropy + repeater
memory with a certified hold time. **Price**: cheapest deep-future cell. *Carried, one prereg
from flight.*

### ⑤ THE FLEET MANEUVER — one protocol, two machines
**Trek frame**: the squadron that acts as one. **Real underneath**: **proven this session** —
matched arms on fez and kingston, identical absolute grid, one frozen design. **Honest fence
stated first**: there is *no quantum link between the chips*, so nothing entangled crosses. What
genuinely needs two machines: **cross-device randomness certification**, **independent
replication inside one pre-registration**, and a **fleet-wide drift atlas**.

### ⑥ DATING A JOB BY ITS OWN PHYSICS
**Trek frame**: the chronometer. **Real underneath**: Cell 12, correctly shrunk to *within-epoch*
— timestamping work inside a calibration window from the drift integral. **Gated** behind Cell 11's
next rung.

---

# PART IV — H12, SPECIFIED

> ## H12 — THE SHIP THAT KNOWS ITSELF
>
> **H10 built the instruments and the laws. H11 built systems — and discovered that the machine's
> own instability is the most interesting subject it has. H12 makes self-knowledge the
> engineering resource: a machine that measures itself, corrects itself, dates its own work,
> proves its own identity, and certifies what it did.**

**Why this theme and not another**: it is what H11's evidence actually pointed at. The census, Cell
11, the entire arm-N arc, the DD reversal, the readout-bar precondition — *every* H11 result that
delivered was about the instrument understanding itself. H12 stops treating that as overhead.

## The cells

| # | cell | price | gate | delivers |
|---|---|---|---|---|
| **12.1** | **Self-Sealing Hull** — in-run learned drift compensation | cheap | Cell 11 next rung (same-day reference) must show the linear model exact within an epoch | Residual drift falls monotonically across batches *inside one job*, ≥5σ, with a no-compensation control flat |
| **12.2** | **Transponder / PUF** — unforgeable within-epoch device identity | cheap | 12.1's fitted constant must be stable across hosts within one epoch | Device distinguished from a sibling backend at ≥5σ from drift signature alone |
| **12.3** | **Within-Epoch Chronometer** | cheap | 12.1 | A job dated inside its calibration window to a stated resolution |
| **12.4** | **Temporal Battery** | cheap | none — one prereg from flight | Arrow-reversal succeeds iff the stored correlation survives; dose-response in hold time; decorrelated control dead at 5σ |
| **12.5** | **Warp Core** — engine on an internal clock | mid | 12.4 first (shares the correlation-hold machinery) | Work extracted only in clock-consistent branches, zero otherwise, exhaust passive at 5σ |
| **12.6** | **Fleet Maneuver** — cross-device certification | mid | 12.1 on both chips | An advantage certified with independent replication *inside* one pre-registration |
| **12.7** | **arm-N, re-pre-registered on fez** | mid | sized from the **lower** CB; rung size and selection bar chosen *jointly against the topology* | Carried from H11. Feasible on the contrast estimate (blocks 95 % CI [3, 31] vs 32 available); two other estimates cannot constrain it |

## The methods spine — binding on every cell

These are not aspirations; each was paid for in H11 and each is now a gate:

1. **Every branch condition is a conjunction of (estimand condition) AND (apparatus gate passed
   in-job).** A branch that can fire on a failed instrument is a formula, not a pre-registration.
2. **Gate verdicts are graded on the LOWER confidence bound, never the mean** — and so is every
   quantity derived from a gate.
3. **A correction is INVALID if its output leaves physical range**, regardless of magnitude;
   separately SUSPECT if magnitude exceeds the condition-number ceiling. Range first — it is
   binary and needs no threshold.
4. **No block may contain a qubit whose calibrated readout error exceeds the frozen bar**, and
   every block reports its correction-map condition number alongside its result.
5. **Whatever number you just quote, state its interval — then ask the same of the answer.**
   Five levels in one night; each fix looked complete when made.
6. **Run the cheapest falsification of your own headline BEFORE filing it.** Three of five
   withdrawals this arc were on published numbers nobody had checked, and none on anything flagged
   uncertain. **A caveat is bait for scrutiny, not an honesty-tax.**
7. **Re-fly the same members before designing a replication.** Kingston's bimodality dissolved on
   a re-fly and saved 30–45 blocks.

## The order

**Wave 1 (cheap, and 12.1 gates three others)**: Cell 11 next rung → **12.1 Self-Sealing Hull** →
**12.4 Temporal Battery** (independent, run in parallel).
**Wave 2 (unlocked by 12.1)**: **12.2 Transponder**, **12.3 Chronometer**.
**Wave 3 (mid-price, after the cheap tier proves the program)**: **12.5 Warp Core**,
**12.6 Fleet Maneuver**, **12.7 arm-N re-prereg**.

## What H12 is NOT

- **Not a bigger arm-N.** It is carried as one cell of seven, sized from a lower bound, and it
  does not gate anything else.
- **Not a mechanism hunt on the kingston anomaly.** The bimodality does not exist; the D-dependent
  loss is real but is a *property of an operating point*, and chasing it needs a working
  instrument first.
- **Not new infrastructure.** Every cell composes existing blocks. The one genuinely new
  *capability* — matched cross-device flight — was proven in H11 at 26 QPU-s.

---

*— Whisper C5018, stamped claude-fable-5. H11 was chartered to build the ship and spent most of
its budget learning to trust the instruments. H12 is what you build once you can.*
