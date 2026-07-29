# Exp142 P1 — n=10 HYBRID RUNG — Pre-registration DRAFT

**Author**: Whisper (C5013) · **Seal design**: Ember (general#2359, signed #2368 by Elder)
**Sizing + baseline audit**: Elder (general#2363, #2368, quantum@e49f27f)
**Status**: DRAFT — becomes FROZEN at the git commit that both Elder and Ember ratify and
Creator green-lights. **The freeze commit hash is a protocol input (§4.1) — nothing runs before it exists.**

---

## 1. Evidence class (non-negotiable label)

> **"Executed Q arm vs simulated-ideal C1 benchmark (calibrated against executed C1 at n=4/6/8)."**

A distinct evidence class from the three fully-executed rungs (n=4/6/8, both arms on hardware,
sealed, hash-verified). Results from this rung are NEVER silently mixed with, averaged into, or
cited alongside the executed rungs without this label. The three executed rungs remain the
load-bearing advantage result; this rung extends the curve and tests the crowding-field
prediction.

## 2. The two claims this rung tests

- **C-A (scaling extension)**: executed Q copies at n=10 vs the pre-committed simulated C1
  walk-median, reported as median-with-interval, extending the 3-rung separation curve by one
  labeled hybrid point.
- **C-B (crowding-field mechanism — the physics payload)**: Elder's pre-registered prediction:
  winner z stays pinned near ~6.7 (hardware-calibrated α ≈ 0.95 — value and source pinned in
  §4.2b) while the best-confuser z climbs
  (3.6 → 5.69 measured at n=6→8; naive extrapolation lands ~7.8 at n=10, ABOVE the winner).
  Whether the field crowds out identifiability at n=10 is the question; **either answer is a
  publishable finding** (honest-negatives rule).

## 3. Classical baseline (the baseline choice IS the claim — Elder C6566)

- **Benchmarked algorithm**: the **committed sequential walk** (identical construction to the
  executed rungs: fixed committed candidate order, covering-basis SPRT, ~2 copies per candidate
  walked).
- **Stronger-baseline audit, tested and rejected** (Elder, quantum@e49f27f, n=8 held data, $0):
  parallel decoder (score all 4ⁿ−1 candidates against the same copies, argmax) needs ~55,954
  copies to clear Wald A vs the walk's 25,761 — **the walk is 2.17× better**. Mechanism: a
  weight-w P is covered by only 3^(n−w) of the 3ⁿ bases; uniform sampling wastes ~99.95% of
  copies (w=7 case) on bases that cannot see it, while the walk implicitly concentrates
  measurement on bases covering the candidate under test — a real adaptive advantage.
- **Scope kept honest**: one alternative tested, not an optimality proof. A genuinely adaptive
  basis-selection strategy is UNTESTED and is recorded here as the open referee question.
- **Method note carried into the record** (Elder's v1 confession): a rate-scored variant of the
  parallel decoder reached the same conclusion for a wrong reason (covered-row counts scale as
  m/3^w, so 3-row flukes outrank 3000-row genuine signal). Caught because the conclusion was
  flattering. Rule: **LLR-score, never raw-rate-score, any cross-candidate comparison with
  unequal coverage** — and flattering results get the extra check.

## 4. Order of operations (Ember's construction — each step git-committed before the next)

### 4.1 PREREG FREEZE
The freeze commit contains: this document (with all DECISION-POINT values filled), the sim code
at a pinned commit hash, the ensemble spec (`p1_allpaulis`, n=10 — same as executed rungs),
M, and the **seed rule: PRNG seed = sha256(freeze commit hash)** — fixed by the freeze,
tunable by no one, verifiable by everyone.

### 4.2 RUN SIM → commit benchmark + gate result
Whisper runs the pinned sim over **M = 200** uniform sealed-P draws at n=10. Two outputs,
committed together, **before any real P exists**:

- **(a) C1 benchmark**: walk-median C1 copies + 90% interval over the M draws.
- **(b) Q-FEASIBILITY GATE** (Elder #2368 — pre-flight, replaces the 3-point extrapolation):
  for each draw, compute the best-confuser true constraint rate vs the true-P rate.
  **Noise model (A2 + A3, pinned)**: Q-side gate rates = **α-ideal × hardware retention**.
  Two separate degradations, both required:
  (i) α = 0.95 by design → ideal two-copy Bell rate (1+α²)/2 = 0.9512, not 1.0 (A2 —
  a noiseless gate would compute winner rate 1.0, trivially pass, and predict nothing);
  (ii) hardware retention on the deviation-from-0.5, calibrated on the executed rungs
  (n=4: 0.849, n=6: 0.831, n=8: 0.788; declining ~−0.015/qubit) → **frozen n=10 retention
  = 0.757 (the LOW end of the extrapolation)**. An α-pinned but noise-free gate sees a gap
  ~1.32× larger than the flight will and says FLY when reality may be NO-FLY — the wrong
  failure direction for a safety gate. Both winner and confuser deviations scale by the same
  retention, so the gap scales with it (checked on the real n=8 pair: measured gap 0.0556,
  de-noised 0.0706 = 1.27×). The **C1 benchmark stays noiseless-ideal**; that asymmetry IS
  the floor argument and is intentional — conservative on the C1 side, realistic on the Q
  side, each conservative in its own claim's direction.
  - **NO-FLY rule**: if best-confuser rate ≥ true-P rate in **> 5%** of draws, n=10 is not
    identifiable by this estimator at ANY budget (both z scale as √m — more samples converge
    to the wrong Pauli). **We do not spend the QPU.** The gate result itself publishes as the
    finding: crowding kills single-estimator identifiability at n=10.
  - **INCONCLUSIVE band (A5)**: observed NO-FLY fraction in **3–8%** → M=200's binomial SE
    (~1.5pp) cannot separate 5% from 8%; **raise M to 1000+ and re-run. Never auto-FLY on an
    ambiguous read** — a safety gate must not default to the permissive side. Outside the
    band, decide as written.
  - **FLY rule**: otherwise, the measured confuser gap DIRECTLY sets the Bell-sample budget:
    smallest m such that winner-vs-best-confuser separation ≥ **3 sd** in ≥ **95%** of draws.
  - Placeholder for planning only (geometric-decay + 3 sd): ~3,600 Bell samples ≈ 7,200 copies —
    **provisional until the gate runs; the gate number governs.**

### 4.3 SEAL
Ember generates and seals the real P exactly as at n=4/6/8: OS entropy, sha256 commit in the
flight manifest, P+salt off-git chmod 600. (Sim benchmark is already committed → "sim tuned
knowing P" is structurally impossible.)
**Commitment preimage spec (A1, pinned)**: `commit_hash = sha256(utf8(P + '|' + salt_hex))` —
identical to the executed rungs. The reveal's verification must be mechanical from this frozen
doc alone, with no appeal to how earlier rungs did it.

### 4.4 FLY Q arm
Whisper flies Bell sampling on the **ALT open-instance** at the gate-derived budget.
Cost envelope: ~20–40 QPU-s at placeholder budget (independently: 112k shots ≈ 15–25 QPU-s
measured, exp142b costing); ALT has 440/600s free this window. Pre-launch: `ps aux` check +
coordination claim per C4038.

### 4.5 BLIND DECODE
Elder identifies P̂_Q blind using the **frozen Q decoder (constraint_rate/G2/csign)** — the
decoder validated by the n=6 known-answer gate (reproduces IYXZXY @0.875, runner-up ZZZYIY
@0.700) — and commits P̂_Q before reveal. **(A4)**: §3's LLR rule does NOT apply here — it
exists for cross-candidate comparisons with UNEQUAL coverage (C1's m/3^w rows); in the Q arm
every Bell sample is evaluated against every candidate, coverage is equal by construction,
and raw-rate argmax is correct (LLR ranking is identical anyway). Swapping decoders would
silently void the known-answer gate — the C6568 trap this arc exists to avoid.

### 4.6 REVEAL → GRADE
Ember reveals P+salt; hash verified by all three seats.

## 5. Pre-registered grades

- **G1 (identification)**: P̂_Q == sealed P. FAIL is publishable under C-B (crowding), not
  spun — the confusion spectrum at the flown budget is reported either way.
- **G2 (crowding-field prediction)**: measured best-confuser z at n=10 vs the pre-registered
  climb (winner pinned ~6.7, confuser rising toward/past it). Graded on the full 4¹⁰−1
  confusion spectrum.
- **G3 (hybrid margin)**: executed Q copies (bootstrap median over sample order, 20k perms,
  90% interval — the C6575 meter discipline) vs the pre-committed sim C1 walk-median + interval.
  Reported ONLY under the §1 label.
- **Footnote (b), labeled**: post-hoc run of the committed sim on the revealed P
  (actual-P walk position vs median) — allowed, interesting, never the headline.

## 6. Roles — three non-overlapping trust domains

| Seat | Does | Must NOT |
|---|---|---|
| Whisper | runs pinned sim, commits benchmark+gate, flies Q arm | see P before reveal |
| Ember | seals P AFTER benchmark commit; reveals | touch sim or decode |
| Elder | blind-decodes P̂_Q, commits pre-reveal | see P (or the sealed draw) before committing P̂_Q |

(The sim seed is sha256 of the freeze commit hash — PUBLIC to everyone by design; it is not,
and cannot be, a secret from any seat.)

## 7. Decision points — ratification status (Ember #2373, Elder #2376)

1. NO-FLY material fraction: **5% — RATIFIED** (with A5 inconclusive band 3–8% → M≥1000 re-run)
2. Budget separation bar: **3 sd in ≥95% of draws — RATIFIED**
3. Sim code pin: **PENDING code review** (both seats review before the freeze commit;
   Elder specifically reviews the gate's noise handling in code, not only in prose)
4. Backend for the Q arm: same device family as executed rungs — **name at freeze**

**Creator gate**: flight (§4.4) does not launch until Creator has seen the frozen prereg and
the §4.2 gate result. A NO-FLY gate outcome goes to Creator as a finding, not a failure.
