# The State of the Quantum Campaign — comprehensive status update (Whisper, C5073)

*Successor to [quantum-status-comprehensive-whisper-c5061.md](quantum-status-comprehensive-whisper-c5061.md)
(2026-08-13). That baseline is ONE DAY OLD and remains the deep inventory; this volume is the
comprehensive delta for C5062–C5073 (2026-08-13 → 08-14) — an unusually dense ~36 hours:
the H14 arc closed, six lock-hunt protocols ran, a 238-job custody corpus was rescued at the
retention edge, the 512 wall was measured, an evening Creator-directed program built and
tested three machines on the chip's own mechanics, the campaign flew its first jobs on a
fourth die, and one spend-gate incident occurred and was disclosed same-hour. Accounting
rules carried unchanged: negatives with their lessons, margins with their labels, retractions
named, rates with intervals, every claim traced to a committed artifact or job ID.*

**What the day added in one paragraph**: the F122 ghost was chased to ground (measurement-
quality-linked on marrakesh, absent on fez — mechanism-consistent opposite readings on two
dies); the sentinels riding unread in every kit job became a free drift instrument and
certified that populations are QUIET within jobs while a dedicated survey showed phases are
TURBULENT within jobs (z=79/92 on two dies) — the chip's currencies mapped; a natural-stream
turbine was designed, gated, and correctly NOT built (two mirages killed by two splitters);
the certified QET borrow was made a WHEEL (six back-to-back information-driven extraction
rounds, zero wear); the compiled switch earned a second career as an INSTRUMENT and its
first pointing found a 33σ coherent non-commutation — which a one-night program then
resolved into engineering doctrine (a LAYOUT property with per-die safe-score thresholds,
not a die defect); a compound machine (sensor→feedforward, the "automatic transmission")
demonstrated in-hardware self-shifting at 99.7% witness consistency; the 512 symmetric-
access wall came in at 0.9067 with Elder's four-edge promotion gate specced and the dual
certificate grinding; and the fleet grew by three never-measured Herons plus a live (paid,
spend-gated) AWS Braket path to trapped-ion hardware.

---

## 1. The H14 arc and the lock hunt (C5062–C5071)

- **H14 "The Alien Ship" executed end-to-end** (charter → A1 census, A2 ghost autopsy,
  A3 flight, A4 arithmetic closure, A5 power law, A6 field design-order audit; six Deck-B
  controls certified). Highlights already partially in c5061; completions since:
  - **A2/S4 chain closed (Locks 3, C5070)**: the F122 cross-copy ghost is
    **MEASUREMENT-QUALITY-LINKED** on the healthy stratum — per-qubit |m| tracks per-pair
    calibration deficit (four healthy flights ρ ∈ [+0.59,+0.70], Fisher ≈ 1e-5; first_FAIL
    null exactly as its a-priori defect ruling predicts). Route to the verdict included
    three self-caught comparator errors, a quarantine, and a v1 retraction — all on the
    record (`results/h14_lock3_s4_FINAL_v2.json`).
  - **Lock 1 (C5070)**: the causal compass certifies its own mechanism per-set; its CE leg
    failed as frozen at exactly the **V=1/3 negativity horizon** — temporal negativity dies
    at c=1/3 while the compass reads sign structure PAST the horizon (the court's
    instrument is strictly stronger than the PDM certificate). Failure reported as failure;
    the horizon is the yield.
  - **Lock 2 (C5070)**: the drift clock's AXIS is weather — 18–75° axis swings across
    epochs on the same drifters (rates 4–15×). In-window compensation categorical; B7
    riders are the carrier.
  - **Lock 4 (C5070)**: wiring-map NO-TEST, self-caught — raw-Z pairwise correlation is
    BLIND to Bell-rotated cross-copy structure (partner control caught the instrument
    blindness before a vacuous CLEAN-WIRING verdict stood).
  - **Locks 5a/5b/5c (C5071)**: ghost generality tested. 5a NO-TEST (my freeze assumed
    two-copy cal plants; rescued records showed single-copy — premise death). 5b NO-TEST
    (my fitted mapping pin was provably invariant under half its own search group —
    margins exactly 1.00×). 5c executed clean with the pin IMPORTED from the flown-matched
    decoder (all 5 fez rungs reproduce banked graded rates to 12 decimals): **NO
    distributed cross-copy negativity on fez** (p=0.96) — the ghost is marrakesh-local at
    the resolved scale, exactly what the measurement-quality ruling predicts.
    (`docs/h14-lock5c-*-c5071.md`, `results/h14_lock5c_verdict.json`)
  - **Lock 6 (C5072)**: the sentinel siphon — the parameterless Bell probe (H·CX, 400
    shots) bracketing every kit job, never read as an instrument, decoded across 49
    kingston jobs: **within-job population drift INVISIBLE** (overdispersion z=0.54, mean
    +0.13pp ± 0.19pp) while cross-job ε spans 1.0–7.25% — drift lives BETWEEN jobs.
    (`results/h14_lock6_verdict.json`)

## 2. Custody: the retention-edge rescue (C5071)

- Enumeration found **~250 exp142/exp144 job IDs manifest-only on disk** — shot records
  living solely at IBM with the mid-July era ~2 days from the retention edge; Ember's
  cross-seat flag added the **exp_hss race family (the F120/F121 substrate)**, also
  manifest-only. Verbatim banking (computes nothing, A2 stage-0 precedent):
  **238 jobs banked, definitive retry ledger shows ZERO retention losses** (all 45
  unbanked IDs were CANCELLED/ERROR — no data ever existed). Corpus pushed durable to
  GitHub (~0.5 GB). Standing rule banked: manifest-on-disk ≠ data-on-disk; a custody
  ledger is only definitive after a retry pass classifies every failure.

## 3. The 512 wall and its promotion gate (C5069–C5073, open)

- **B1 symmetric-access ceiling at dims [4,4,4,4,2]: 0.90667427** (SCS optimal, eps 1e-7,
  25,091s; exchange-only invariance after the measured sign obstruction retired the C1
  reduction — the wall characterized as STRUCTURAL). Charter's pre-committed <0.988 branch
  fires: dim32 0.8690 → 512 0.9067, and **F82 hardware (0.9769) exceeds the 512 ceiling by
  ~0.07**. Promotion is its own gated process: **Elder specced the four-edge gate**
  (`docs/h14-b1-promotion-gate-SPEC-elder-c6618.md`) — G1 exchange-WLOG lemma in writing,
  G3 DUAL certificate (approx-primal understates a max — the dangerous direction), G4a
  embed regression at [2,2,2,2,2] to 0.8690277, G4b billing row at frozen q*. **Producer
  packet = board #150**; the dual-capture re-solve is grinding as this document is
  written; lemma/regressions/rounding land in a fresh block. The number stays banked, not
  promoted.

## 4. The Creator's machine-shop night (C5072–C5073): siphon → turbine → gears → wheel → transmission

A live Creator-directed program: *"is there anything moving through the system on its own
that we could siphon work from... a turbine in a natural quantum stream... quantum gears we
can connect to... build the automatic transmission."* Every flight seal-bound (staged digest
→ Creator GO citing it → fly → decode at the frozen gate). Total ~180s of free tank plus
one authorized paid flight (see §7).

- **The turbine arc — the wheel correctly NOT built.** Scout: LIVE-REVIVAL, 7 revivers on
  marrakesh this epoch (q34 amplitude 0.382, a full depth-oscillation). Splitter 1
  (mechanism-split, idle ladder at fixed depth): **q34 is GATE-clock** — interference, not
  an energy stream (the showpiece killed); **q45 is a real TIME-clock** (0.200→0.034→0.248
  on pure idle, turning 0.213 vs 0.057 noise). Splitter 2 (the stroke, clean population
  prep): **q45 is coherence-frame only** — bare population monotone (the chip's lossiest
  qubit; the TLS drains, it does not store). NO-TEST branch fired as frozen; no borrowable
  energy stream this window. Two mirages, two pre-registered splitters, zero wheels on
  either. Lesson banked: split the CLOCK and the CURRENCY before designing extraction.
- **GEAR 1 — the coherent error field: real, huge, and LURCHING.** Rider survey (self-
  inverse CZ trains, 16 calibration-picked edges): conditional riders tens-to-hundreds of
  mrad/CZ at 30–100× se — but the unwrap-free within-job repeats moved **z=79**: the phase
  currency wanders O(1 rad) in minutes. Unmeshable by static calibration; fold-in demo
  dead as designed. Two decode-design lessons on the record (verdict taxonomies must name
  large-but-unstable; unwrap breaks past π). (`results/exp_gear1_rider_decoded_c5073.json`)
- **The QET wheel — the certified borrow made continuous.** Six back-to-back information-
  driven extraction rounds per shot (exp195c construction verbatim; a first-draft coin
  improvisation was caught against lineage pre-flight; selftest reproduced the exact
  −0.2001 gap in all six simulated rounds). Result: **6/6 rounds in band, falsifiers pay
  every round (+0.26..+0.32), wear slope +0.0002 ± 0.0056 — ZERO degradation**; frozen
  letter reads WHEEL-PARTIAL (round 3 brushed the strict fence by 0.005; pooled clears
  with room, labeled secondary). The self-primed engine runs continuously.
  (`results/exp_qet_wheel_decoded_c5073.json`)
- **GEAR 3 — the switch's second career as an instrument**, and its first pointing
  detected: on marrakesh auto-routed qubits, two native CZs sharing a qubit **fail to
  commute coherently at 33σ** (self-calibrating same-gate floor; polarity −0.95;
  depth-normalized comparison frozen pre-flight). This is the axis GEAR 1's diagonal
  riders are structurally blind to.
- **The automatic transmission — sensor drives drivetrain in one circuit.** Mid-circuit
  COMMUTE herald → feedforward shift + hardware witness: **mechanism demonstrated** —
  witness/herald consistency 0.9966, herald rate 0.35 reproducing GEAR 3's deficit class
  across a recalibration (the sensor is stable cross-epoch), neutral path undisturbed;
  first recovery candidate trended +2.81σ, below the exploratory bar, unclaimed.
- **The gear-ratio ladder — a clean null that graded the trend as noise.** Rz(θ)×7 +
  Rx(π) sweep: no candidate clears Bonferroni (best z=+1.4), tuning curve flat (r²=0.02),
  and the +2.81σ trend did NOT replicate (z=+1.1 same setting) — the unclaimed-trend
  discipline vindicated within hours. The grind branch is not correctable by any
  single-qubit rotation: the coherent error is entangling-class. Axis closed.

## 5. The non-diagonal saga: discovery → doctrine in one night (C5073)

- The 33σ grind was chased through a named confound (die-vs-layout: marrakesh-auto ground;
  aachen-auto was instrument-dead — an unmeasured cell, not a clean one) to a **one-cell
  resolution**: both dies' calibration-gated best paths COMMUTE (aachen z=−0.2; marrakesh
  z=−20 with science ABOVE floor — the anti-grind direction). **It was the layout, not the
  die**: real physics on weak silicon under the auto-router.
- **Dose-response on both dies** (band-filling rungs under an alive-band guard that
  pre-predicts floor survival — the guard itself measured marrakesh's instrument-hosting
  band as razor-thin vs aachen's roomy one): **ALL-CLEAN inside both alive bands**, with
  matching sub-significance upward tilts at the outer edges (+2.5σ / +2.8σ, claimed on
  neither) — the grind threshold sits just past instrument-hosting quality on both dies.
- **Standing doctrine with numbers**: layout-gate everything, instruments included; safe
  path scores **marrakesh ≤ 0.039, aachen ≤ 0.036**. Instrument note banked: the same-gate
  switch floor accumulates repeated-pair error and should be repetition-structure matched
  in future pointings.

## 6. The currency map — the day's synthesis, now three dies

| Currency | Verdict | Evidence |
|---|---|---|
| **Population** | QUIET within jobs, everywhere measured | Lock 6 (kingston, N=49, z=0.54); aachen paired sentinels (z=1.3, ε 0.75–1.75%) |
| **Phase** | TURBULENT within jobs, everywhere measured | GEAR 1 repeats z=79 (marrakesh); replication z=92 (aachen); field present 15/16 edges |
| **Energy streams** | ABSENT / mirage | turbine arc: gate-clock interference; coherence-frame TLS; no population return |
| **Non-diagonal grind** | LAYOUT property with a threshold, not a die property | 2×2 + two dose-response curves; safe-score doctrine per die |

*Stability lives only in the currency you cannot extract from; turbulence rules the one
computation uses; nothing flows free in energy; and the dramatic anomaly was bad
neighborhoods, not bad chips.*

## 7. Fleet, venues, and the spend-gate incident

- **The fleet grew — AMENDED IN PLACE (C5073, post-#151 gate)**: aachen/boston/pittsburgh
  are reachable ONLY through the PAID instances — the enumeration that "found" them was
  itself the unpinned service leaking paid-instance visibility (the same mechanism as the
  billing incident). Under the pinned free instance the fleet is exactly the usual trio.
  **There are no free virgin dies.** All six devices remain 156q CZ-native Herons and **no
  Eagle exists on any reachable account** (Gear 0 fleet-verified unreachable). Aachen has
  been measured (this doc §5–6, paid-annotated); boston/pittsburgh would be paid flights.
- **AWS Braket is live**: 25 devices visible including IonQ Forte (trapped-ion), Rigetti
  Cepheus-108Q, IQM Garnet/Emerald. Real dollars per task+shot (Rigetti/IQM ≈ $3–30 per
  8k-shot job; IonQ ≈ $100+): spend-gated like the paid tanks. Highest-value first flight
  if funded: the currency map cross-ARCHITECTURE on trapped ions.
- **SPEND-GATE INCIDENT (C5073, disclosed same-hour, general#11539)**: three aachen
  flights billed **whisper-de (paid eu-de instance) 61 of 63s without authorization** —
  the shared IBMQ_TOKEN credential carries free us-east AND paid eu-de instances, and the
  runtime resolves by device region; the name-level preflight (c4217_018) cannot see
  instance routing. Halted, disclosed with exact figures, fix boarded (**#151**: CRN
  allowlist that refuses-loudly + preflight upgrade). The Creator subsequently issued
  explicit post-disclosure authorization and the aachen gradient re-flew as an
  **authorized** paid flight (+18s). Books: 79s against the 63s trailing window, aging out
  over 28 days. The aachen science is valid; its billing annotation is in every artifact.

## 8. Open lanes and standing waits (as of this writing)

| Item | State |
|---|---|
| **#150 B1 promotion packet** | dual-capture re-solve grinding (~hours); G1 lemma + G4a/G4b + rigorous dual rounding owed in a fresh block; Elder grades |
| **#151 instance-pinning fix** | owed before any unauthorized eu-de submission is possible; cross-seat review specced |
| **Exp183b (permutation court)** | queued on fez (~97k pending at submit); watch armed; days-scale wait |
| **#141 threshold vitality** | boarded (split from #112; RV-drift discriminator per elder's correction) |
| **#143 thermal head gauge** | boarded (turbine step 1, $0-first) |
| **#145 clock-spend design** | boarded; feasibility now directly informed by measured phase turbulence (the single-qubit clock lurches too) |
| **Two-qubit / tracking recovery for the grind branch** | named residual of the ladder null; not boarded (needs a design with a real prior) |
| ** PAID-only per the #151 gate finding — flights need explicit authorization | currency-map replication available, us-east (likely free-route — verify against #151 first) |

## 9. Method scoreboard for the delta period

Nine frozen protocols executed; **five NO-TESTs self-caught at their own gates** (5a
premise, 5b degenerate pin, stroke currency, plus two carried from C5070's locks); two
honest-negative locks opened (5c, Lock 6's stability certificate); one mirage pair killed
pre-build; one 33σ detection resolved to doctrine; one trend correctly left unclaimed and
then graded noise by replication within hours; one spend-gate breach disclosed same-hour
with exact books. Seal-bound GO discipline held on every flight (digest → GO citing it →
verify unchanged → fly). The cwd-trap compound-command failure mode fired four times and
is now a stored rule (validated_times=4). Every number in this document traces to a
committed artifact or job ID in this repo.

---

## 10. Since §1–9 (same C5073 session, later): B1 to the floor, F119 relaunched, and the perturbation-mining arc

This volume was written mid-session; the run continued. Appended here so the inventory stays whole.

### 10.1 B1 512 promotion — court-certified and PUBLIC
The producer packet completed all four edges (G1 exchange-WLOG lemma with machine-checked
premises; G4a mixed-dim regression, byte-identical grader re-run; **G3 dual certificate — two
independent blind computations agreeing to 15 digits, U′ = 0.9066741104, tighter-than-primal**;
G4b billing row). Court-certified **3-of-3** (Elder compile, Whisper + Ember independent
re-derivations), G6 attack-preflight clear. Posted as an **F82 card update** and **published to
the public museum floor** (Dawn, verified live), with the sigma-pairing rule adopted binding
(216.8σ↔0.8690 dim-32, 134σ↔0.9067 512) and the q*-table 1.000008 caveat named. The honest
fence: the separable class, given 16× the ancilla, closes barely a third of the gap to hardware;
dims>512 stays OPEN.

### 10.2 F119 remedy re-fly — relaunched (delivery-fix, honest-delivery)
G3 (Whisper) verified the patched kit independently (delivery fix confirmed: conv+quantum
shots==1, fresh-basis-per-row, P-independent manifest); court G1/G2/G3 green. Creator GO trimmed
→ preflight caught the registry tank stale (my C5060 probe 361s vs live 56s) → re-authorized
**MICRO n=4**, flown blind by Ember (EMBER-ONLY, secret P) on kingston/ALT4, bill 40% under via
measured-q_n resize. The grade-time determinism-attack gate must score chance or it grades
DELIVERY-FAIL. n=6 waits free on 28-day window aging. Device pin: kingston primary (holds the die
constant to isolate the v1→v2 delivery delta — Ember's refinement of the cross-die recommendation).

### 10.3 The perturbation-mining arc — five $0 extractions off banked collision data (F103-lineage)
Creator prompt: "throw perturbations at existing data to extract info from our own collisions."
Proof-of-concept was F103 (entanglement from negative conditional entropy, zero shots). Five
extractions on the F122 door-b two-copy corpus, **each frozen before compute**, each importing the
validated F122/A2 decoder:
- **Purity (naive) → NO-TEST**: the symmetric two-copy SWAP purity came out ~0 (maximally-mixed),
  failed the physical bound — the freeze caught a wrong physics assumption (the signal lives in the
  P-selected cross-pair correlation, not a symmetric observable). No fabricated number.
- **Calibrated spectrum → SHARP SEAL**: the calibrated estimator reproduced all graded tr2 to
  **machine precision (1e-16)**, then the leakage ring (planted-weight ±1) sat at the shot-noise
  floor → the F122 amplitude loss is **incoherent decoherence, not coherent leakage**.
- **Weight-spectrum → WEIGHT-1-EXCLUSIVE ghost**: a broad blind search found off-planted structure
  at **weight 1 only** (weights 2–16 flat at floor) — independently rediscovering the A2 ghost and
  **bounding** it (weight-1-exclusive, a ceiling A2's targeted probes couldn't give).
- **Ghost-power jackknife → blind rediscovery of the first_FAIL stratum**: the all-5 jackknife came
  back 100% systematic — entirely from the one a-priori-defective flight (W1 6.49 vs healthy ~0.05),
  which the blind statistic flagged without knowing the stratum ruling; healthy-4 (inherited
  exclusion) show a small cal-linked systematic. (Label correction on record: "original" =
  first_FAIL, not WIN.)
- **Sign test → MEASUREMENT-QUALITY (the decider)**: four healthy draws with four DIFFERENT sealed
  P; the per-qubit ghost pattern is **P-independent** (cross-draw r = +0.809, P-tracking +0.003) →
  same qubits regardless of the secret → apparatus, not state. **A2/S4's measurement-quality ruling
  DEMONSTRATED, not just supported.** (Ember: this design beat her readout-asymmetry sketch — the
  four-different-seals corpus discriminates for free.)

### 10.4 The ghost's home — found in three senses
- **Spectral**: weight-1-exclusive.
- **Mechanism**: P-independent measurement-quality (leaning S3 backaction per A2's flat-class shape).
- **Spatial**: hot pairs 8/6/10/12 = physical qubits 17-27, 24-25, 37-45, 28-29; cold at 2/4/15;
  consistent across draws (the consistency IS the apparatus signature).
- **S1-vs-S3 fine split: UNDETERMINABLE at $0** — inherited from A2's S1_declaration (no
  readout-multiplex data on any read path; proxying disallowed) and confirmed (cal blocks 2000-shot
  SE 0.022 > the 0.01 ghost). Needs a targeted readout-crosstalk flight; **named, not proxied**.

### 10.5 Method note for the delta-delta
The perturbation arc is the re-analysis discipline at its cleanest: measure-once-ask-many is real
**when you ask with the calibrated question and let existing experimental design (4 different
sealed P) do the discriminating**; freeze-before-compute turned a wrong estimator into an honest
null; every new number pinned to a machine-precision known-answer before it was trusted; and the
analysis floor (S1-vs-S3) was named rather than papered with a proxy. Total new QPU this section:
zero (the perturbation arc) + one MICRO n=4 remedy flight (~10s free ALT4).

### 10.6 Collision-scan resolution map + digs A/B — the $0 re-analysis at its TRUE floor
Creator prompt: "do another collision scan" → "both/and A and B".
- **The scan produced a RESOLUTION MAP of our own corpus** (`results/collision_scan_resolution_map_c5073.json`):
  the two-copy ghost (~0.01, needs SE~0.003 ≈ 100k shots) is resolvable **only on the door-b data**.
  Every *other* two-copy arm is shot-starved **by design** — the few-copy advantage means few shots
  (fez p1 528-3878, wave ~110/rung, cal 2000), all below the ghost scale. So "does the ghost appear
  on other devices" is a **$0 floor**, same class as S1-vs-S3. The scan's real find: the
  **conventional (classical-baseline) arms carry 100k-700k shots each** (wave1 conv = 707k) =
  single-copy randomized-basis data = a **classical-shadows dataset never mined for state structure**,
  only ever used to count classical-learner queries.
- **Dig A (recover the signed phase the two-copy squares away, via conv-arm classical shadows):
  FUNDAMENTALLY INFEASIBLE — and the wall IS the two-copy advantage.** Signed tr(P·ρ) of a
  **high-weight** sealed Pauli from single-copy data has classical-shadow variance **~3^weight**.
  The sealed P's are weight 11-13 → 3^11–3^13 = 177k–1.6M → ~2e8–2e9 single-copy shots for SE 0.03;
  we have 707k (**90×–2500× short**). Not a data limit — **precisely why F122 measures two copies**.
  The phase the two-copy squares away is classically un-recoverable at high weight, and *that
  un-recoverability is the separation itself*. The re-analysis re-derived the advantage's foundation
  from the opposite side. (`results/collision_scan_digs_AB_c5073.json`)
- **Dig B (single-copy readout to split S1 readout-crosstalk vs S3 backaction): NOT feasible on
  banked data.** The door-b cal is **two-copy** (32-bit Bell), not single-copy readout; the only
  high-shot single-copy we hold (wave conv) is on **kingston with zero qubit overlap** with the
  marrakesh ghost qubits {17,24,25,27,28,29,37,45}. The single-copy angle re-confirms the A2 S1/S3
  floor from a new direction; splitting them still needs a targeted new flight.
- **Weight matters — the one twinkling dig A does NOT wall:** the *ghost* is **weight-1**, where
  shadow variance is 3^1 = 3 (trivially resolvable). So the ghost's **signed per-qubit direction**
  (the phase/readout-asymmetry sign) *is* recoverable from low-weight measurement even where the
  high-weight sealed-P phase is not — a real dig-A-immune next step (needs Elder's signed reading).

### 10.7 The unfold/fold campaign + F119 n=4 remedy + ALT5 (C5073 continued)
**Unfold/fold campaign** (`docs/unfold-fold-campaign-whisper-c5073.md`): thesis = Pauli weight is the
radial/holographic coordinate (single-copy shadow cost ~3^weight); unfold at the boundary, fold when
algebras match. Runs (all $0 except the U2b-family flights):
- **U0 ghost-mitigation (the build-upon run)**: a uniform per-qubit fidelity model f=0.9528±0.0018
  reproduces all 4 door-b sealed-P tr² to 0.2% (tr²=f^(2w)) — the duck. The ghost's hot-qubit pattern
  does NOT predict the tr² deficit (LOO 143% worse than weight) → the ghost is a localized side
  channel, NOT the advantage limiter; the loss is uniform. Both offered to the F122 lane.
- **U1 ghost-phase**: PREMISE-CORRECTED at pin — two-copy tr² is sign-free at all weights (D.estimate
  reproduces the grade exactly); the signed direction is single-copy-only (dig B wall). Delivered the
  P-independent per-qubit ghost map (cross-draw r +0.809).
- **U2a boundary-purity**: the boundary carries only the w=1 ghost, w≥2 at floor — weight-1-exclusive
  ghost confirmed from the purity angle.
- **U3 conv-arm boundary (the deepest result)**: the conv arm is a structured honest-oracle (fresh
  random even-parity b per row). Single-copy ensemble low-weight marginals are maximally mixed BY
  DESIGN (uncond w1 |tr|~0.07); conditioning on b recovers the eigenvalue (~0.99). **The sign the
  two-copy squares away IS the oracle's per-row b** — dig A's wall AND the two-copy advantage,
  mechanistically explained from the construction. PIN confirmed on flown kingston (true-basis odd
  0.083 vs wrong 0.500).
- **U4 dual-orbit**: 512-wall optimum near-full-rank (456/512) → generic, not compressible (weakens
  F2). **U5 epoch-drift**: low-power (needs abs timestamps). **U6 sentinel timeline**: device-health
  series across 61 flights, sentinel fidelity 0.960±0.015 (exp142 0.974 > exp144 0.956).
- **F1 degree-2 manifest** emitted (which functionals fold through the two-copy envelope).

**U2b flight family (ALT5/marrakesh, Creator GO)** — testing the U0 build-upon result on-device:
- **U2b (single w=4, job da0g727)**: tr²=0.873, implied f=0.983 — the U0 FORM transfers but the f
  VALUE is qubit/prep-local (0.983 vs door-b 0.953: different marrakesh qubits + fixed-b vs fresh-b
  ensemble). Honest partial.
- **U2b weight-ladder (w=1–4, job da0gol0)**: **the per-qubit fidelity spectrometer**. tr²
  0.957/0.912/0.902/0.865 → per-qubit f q0=0.978, q1=0.976, q2=0.995, q3=0.979. The U0 PRODUCT
  structure (tr²=∏ f_qi²) is proven and portable; the UNIFORM-f simplification is resolvably rejected
  at low-weight/8192-shot precision (χ²/dof=6.7) — it is the many-qubit AVERAGE of per-qubit f, valid
  only at high weight. **Structure universal, uniform is a scale-dependent coarse-graining.**
- **Spectrometer N=10 (job da0gvsno, in flight)**: extends the ladder to 10 qubits — reads 10
  per-qubit two-copy fidelities from the tr² ratios. A reusable on-device calibration instrument the
  vendor numbers do not give at the two-copy level.

**F119 n=4 remedy (EXP142B, Whisper's prereg deliverables — GRADED CLEAN)**: (1) determinism-attack
gate PASS (flown v2 per-qubit determinism 0.49 aggregate / 0.85 per-basis at the 73rd null percentile
= chance; the v1 delivery flaw gone via shots=1 + fresh-b); (2) independent blind SPRT decode
recovered **ZYYZ 20/20** = the TRUE sealed Pauli (committed 3 weeks pre-flight, hash-verified).
Elder's meter concurred (both arms ZYYZ, ratio 105× best-known-conditional). Rung STANDS.

**Infrastructure**: added **IBMQ_ALT5** to the ship computer (fresh 600s open-instance) by fixing the
registry feeder's hardcoded token list to discover all IBMQ_* (board #154 closed). Fixed board #128
(quality gate scored evidence by vocabulary, not by whether a measurement happened) and the cwd-trap
on the memory-write tools (script-relative paths). All U2b-family flights cleared every spend-gate
(sim-verify, preflight, #151 instance-gate blocking the us-east paid-misroute) before submission.

**Recurring method lesson (3× this session)**: a threshold must be calibrated to the sample size /
noise of the statistic it judges — a flat band false-fires in both directions (σ-test on 43k rows;
0.65 band on 27-row determinism; R² on a 4-point small-range ladder). Null-calibrate; the per-qubit
decomposition, not the R², was the honest read of the ladder.

### 10.8 door(a) CERTIFIED WIN — the stabilizer-memory separation, flights 4→6 (C5073)
Creator directive: "fly door-a flight-4" → "fly flight-5" → "fly flight-6". The campaign's **first
certified stabilizer-memory separation WIN** (A&S arXiv:2607.02444 class; single-copy hardness via
the HH25 tester as the simulated C1 comparator). **Certifying flight = flight-6, custody-clean.**

**The result (Elder graded, Whisper cross-check 80/80 vs sealed truth, Ember integrity-gated reveal):**
- **flight-6 (certifying): 80/80 = 100.0%**, frozen criterion **76/80 CLEARED by four**, P(chance)
  = **8.3e-25**. Zero errors; sensitivity **80/80 under τ±1SE in BOTH directions** (the zero-flip
  signature seen blind, realized as perfection). Ran on the best epoch of the campaign (u_hat
  **0.2166**), which the in-flight τ_Q rode automatically. Powered prediction E[correct]~79 landed
  within one trial. **The pre-commitment is on the PUBLIC CLOCK, not attestation:** commitment
  72b8f60e was public on origin (commit 9358235) BEFORE the flight existed — **G-PUBLIC's first live
  enforcement**. Both blind decodes (Whisper + Elder) hashed pre-unseal, both 40 ALT/40 NULL.
- **flight-5: 78/80 = 97.5%** (P=2.7e-21, TP39/TN39/FP1/FN1) — a real result but rebadged **honestly
  descriptive-with-attestation**: its commitment published ~24s AFTER the job (seal+flight bundled in
  one post-flight commit), so "commitment older than its flight" was FALSE for the win flight. Ember
  caught the custody gap (general#12351); Elder ruled a **re-fly for integrity, not for results** —
  and the flight that flew on the public clock flew perfect.
- **The arc, every rung diagnosed then fixed:** pilot 62.5% → refly 72.5% → flight-3 90.0% →
  flight-4 92.5% → flight-5 97.5% (attested) → **flight-6 100.0% custody-clean**. Diagnosis chain,
  each validated by the next flight's gain: anchor-vs-science drift → **in-job τ_Q** (flight-3, fixed
  the drift, symmetric errors appeared) → **shot noise** (flights 3+4 both ~2 short at S=316; 6/6
  errored trials NOISE-CLASS, ≤1.4 SD from τ) → **S-doubling** (flight-5 S=316→632 halved per-trial
  variance → ~1%/side error) → **custody re-fly** (flight-6, same powered S=632 design, public
  pre-commit → zero errors).

**Why it is a real WIN, not a lucky draw:** blind (decoder never sees labels), **pre-committed on the
public clock** (72b8f60e on origin before the flight, G-PUBLIC-verified — the property flight-5 could
only attest to), commitment-verified from the frozen preimage, threshold traveling IN-JOB (the
in-flight cal rows give the true u_anchor, killing the drift that lost flights 1&2), two independent
decodes (Whisper + Elder) agreeing 80/80 with independently re-derived accept-parity, and the winning
power stated in advance (E[correct]~79, P(win)~99%; observed 80). **The 100% earns the scrutiny a
100% demands** (the Cell-2 rule): every safeguard fired BEFORE the number existed.

**Whisper's role across the arc:**
- Built the **HH25 single-copy tester** from Elder's spec — sim-verify caught two court-critical
  errors before any tank: a **gf2_rank bug** (pivot reuse) and the **extremal-MIN direction** the
  spec paraphrased as "max" (confirmed against the primary text; the grader fixture was already
  right, the spec's paraphrase was not).
- Built + verified the public manifest for all five flights (τ_Q wired verbatim, K-sizing —
  **caught Elder's 8-vs-6 formula typo** and his **row-vs-sample units error**; A_cal seed lineage
  30000/30032/30064; interleave maps), with **byte-identical two-seat cross-hashes** every flight.
- Ran the **independent blind decode** each flight, matching the grader **80/80** via a from-scratch
  accept-parity re-derivation, **cal-PINNED** (the calibration data selects the decode convention:
  halves 0.61 vs interleaved 0.51 — "cal-pins-the-convention", Elder's method-note-of-the-night);
  on flight-6 self-verified 80/80 against the opened seal by his own hand, not on the announcement.
- **Honestly reversed his own wrong call:** after flight-4 recommended STOPPING (misread shot noise
  as a true-rate ceiling); Elder's noise-class fit corrected it; the powered S flew and won. The
  reversal is on the record next to the win.
- **Owned the propagated custody error:** the flight-5 claim-card (Whisper-drafted, Elder-ratified)
  asserted "every commitment older than its flight" — false for flight-5. When Ember surfaced it,
  Whisper corrected his own state and the card rather than defending the number, and flew the re-fly.

**Seven pre-spend catches across three seats, every one by re-deriving not re-reading** (HH25
direction, HH25 rank, K-formula, binder-premise, cal-row doc-vs-code, row-vs-sample units, custody
timeline), plus the shot-noise diagnosis itself — ~zero wasted QPU-s across six flights.

**Standing lesson banked:** a pre-commitment that can only be *attested* (seal + flight in one
post-flight commit) is not the same integrity object as one on the *public clock* (seal pushed to
origin before the flight exists). The re-fly cost was small; the distinction is the whole point of a
commitment. G-PUBLIC now enforces it at submit — its first live catch was this arc.

**Fences / open:** door(a) is **WON and CLOSED, custody-clean**; the claim-card ratification is
RESTORED with flight-6 as the certifying flight (`docs/doora-claim-card-RATIFIED-c6625.md`), and
**F123** is assigned (Ember's numbering seat — sibling of F122 door(b)). F119 n=8 remains the last
tank-gated frontier
(~5,850 QPU-s, ~30× the free tank — a paid-allocation call for the Creator).
