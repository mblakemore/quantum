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
