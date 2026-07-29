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
- **C-B (crowding-field mechanism — the physics payload)**: REVISED per Elder #2390
  (quantum@4b82b1c), which WITHDREW the original linear-extrapolation alarm (~7.8 confuser z
  at n=10, the 14×–417× budget demand) as a 2-point linear fit to an extreme-value statistic
  — the same weak-link class the gate was introduced to replace. The principled null law is
  **E[z_max] ~ √(2n·ln4)** (√n growth, not linear): expected null-max z at n=10 ≈ 5.27 vs
  winner ≈ 7.17 (hardware-calibrated α ≈ 0.95 — value and source pinned in §4.2b), gap
  ≈ 1.90; P(argmax correct) at the frozen BQ[10]=110 ≈ 0.9974. Even carrying the full
  measured n=8 excess forward, the winner leads by +0.39 to +0.77 sd.
  **Pre-registered expectation: n=10 REPEATS the n=8 thinness — expected gate verdict is
  FLY at or near the frozen budget, not NO-FLY.** Extreme-value discipline (Elder #2390):
  the n=6 runner-up (0.700) sits EXACTLY at the null-max median — pure extreme-value noise,
  NOT evidence, and must not be fitted as a trend point. The n=8 runner-up (0.800) is above
  the null-max 95th percentile — a REAL, uncharacterised excess of +0.078. One data point of
  real structure, not two. Whether the sim explains that excess is the mechanism question;
  **either answer is a publishable finding** (honest-negatives rule).

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
  (n=4: 0.849, n=6: 0.831, n=8: 0.788; declining ~−0.0153/qubit) → **frozen n=10 retention
  = 0.7573, the CENTRAL linear extrapolation (F1 wording fix — the low side of the band is
  carried by the parametric box, not by the point value)**. **Citable source (pinned)**:
  `experiments/exp142_p1_q_noise_retention_elder_c6575.py` +
  `results/exp142_p1_q_noise_retention_elder_c6575.json` (quantum@fcb1ce0) — per-rung
  retention with job ID and revealed seal as source; sim imports `retention(n)` /
  `extrapolate(n_target)` rather than hardcoding. Elder's own caveat carried forward: a
  3-point linear fit in n is the weak-link class this gate exists to replace — if the sim
  can model device noise DIRECTLY (depolarizing + readout on the actual conv_layout) and
  that model passes the §4.2c validation gate, the direct model is preferred and the
  extrapolation becomes its cross-check. An α-pinned but noise-free gate sees a gap
  ~1.32× larger than the flight will and says FLY when reality may be NO-FLY — the wrong
  failure direction for a safety gate. Both winner and confuser deviations scale by the same
  retention, so the gap scales with it (checked on the real n=8 pair: measured gap 0.0556,
  de-noised 0.0706 = 1.27×). The **C1 benchmark stays noiseless-ideal**; that asymmetry IS
  the floor argument and is intentional — conservative on the C1 side, realistic on the Q
  side, each conservative in its own claim's direction.
  **What the gate is actually testing (Elder's three-effects decomposition)**: the shrinking
  identification margin is not one effect but three with different n-dependence — (1) α-ideal
  structure (pins the winner), (2) hardware retention (scales both deviations down), and
  (3) field crowding (the confuser population grows 16× per +2n). The gate exists to measure
  their combination at n=10 before any QPU is spent.

- **(c) SIM VALIDATION GATE (known-answer, runs before (a) and (b) are trusted)**: the Q-side
  sim must REPRODUCE the measured n=6 and n=8 confusion spectra from the executed rungs.
  **Sharpened target (Elder #2390)**: the discriminating quantity is the **n=8 EXCESS ABOVE
  the extreme-value null (+0.078)** — reproducing the raw runner-up rate 0.800 is trivial
  when the null-max alone gives 0.722. The winner side and the confuser side of the gate get
  **separate treatments** (winner: α-ideal × retention; confuser: extreme-value null +
  whatever mechanism explains the n=8 excess) — they must NOT share one noise knob.
  Tolerances frozen with the sim code pin — This is the decoder known-answer discipline
  (§4.5) applied to the sim itself. **Mechanism note driving this**: for the ideal ensemble
  state (I+αP)/2ⁿ, every wrong candidate's constraint rate is analytically EXACTLY 0.5 (the
  symplectic character sum vanishes for Q ∉ {I, P}) — so the measured confuser elevation
  (n=6 runner-up @0.700, n=8 @0.800) is NOT ideal-signal structure. It must come from the
  finite-row preparation structure (each row is a pure stabilizer state; a wrong candidate
  landing in a row's stabilizer group is elevated in that row) and/or device noise. A sim
  that fails to model whichever mechanism is real will fail this gate — by design.
  - **NO-FLY rule**: if the best-confuser TRUE rate ≥ the true-P rate, n=10 is not
    identifiable by this estimator at ANY budget (both z scale as √m — more samples converge
    to the wrong Pauli). **We do not spend the QPU.** The gate result itself publishes as the
    finding. Under the pinned draw-degenerate model this is a BOOLEAN, not a draw-fraction.
  - **A5 STRUCK (Elder #2416, Ember concur #2419)**: the original inconclusive band was a
    draw-fraction band over a model whose draws are identical by construction — the observed
    NO-FLY fraction could only ever be 0.0 or 1.0, at any M, so the band was UNREACHABLE.
    An inert safeguard in a court doc is worse than none because it reads as protection.
    The honest reason no verdict-band is needed: the FLY verdict sits **4.4× from its
    boundary in both parameters** (excess would need 0.342 vs 0.078 carried; retention
    would need to collapse to 0.173 vs 0.757 estimated).
  - **PARAMETRIC ROBUSTNESS (A5's replacement)**: the model's uncertainty is parametric,
    not draw-sampling. The gate sweeps the plausible box **retention 0.60–0.80 × excess
    0.056–0.160** (5×5 grid): if ANY box point is NO-FLY → verdict INCONCLUSIVE-PARAMETRIC
    (do not fly on estimates that admit a NO-FLY corner); if the budget search exhausts
    anywhere in the box → NO-DECISION, do not fly (Ember F2: a FLY-without-budget state
    must not exist). Otherwise the **flight budget freezes at the box's CONSERVATIVE
    CORNER, not the pinned point** — buying out the whole box costs seconds of QPU and
    removes the one place the extrapolation could still bite.
  - **Excess accounting (Elder #2416(b), a named choice)**: the +0.078 excess is runner-up
    minus null-MEDIAN, so it contains ~0.022 of ordinary null-max spread on top of the
    ~0.056 genuinely above the null 95th; carrying the full 0.078 as a TRUE-rate elevation
    double-counts sampling spread once — in the stricter direction, so it is kept, and the
    box's excess range covers both readings.
  - **Retention value (Ember F1, exact words)**: the frozen n=10 retention 0.7573 is the
    **central linear extrapolation** of the three executed rungs (per Elder #2380), NOT a
    low-end value; the box's retention range (down to 0.60) is where the extrapolation
    risk is carried.
  - **FLY rule**: otherwise, the measured confuser gap DIRECTLY sets the flight budget.
    **The budget is dimensioned by whatever the §4.2c-validated sim says the knob is**
    (Ember #2386): if the row model validates, the derived budget is the **(ROWS ×
    samples) PAIR, both frozen** — the mechanism predicts fresh rows are the cheap knob
    that may recover identifiability where √m alone could not. Criterion unchanged:
    smallest budget such that winner-vs-best-confuser separation ≥ **3 sd** in ≥ **95%**
    of draws. Algebra note (Ember-confirmed, analytic + n=3 brute force): ideal
    rate(Q)=0.5 exactly for all Q∉{I,P} — the crowding threat that motivated this gate
    may itself be an artifact of ROWS=8 rather than physics; discovering that would be
    the gate's first real output.
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

## 4b. Standing verification rule (Elder #2403 — earned twice on 2026-07-29)

> **A gate that runs at one parameter value covers only the branches that value reaches.**

Elder's pub[0]-only driver passed its n=6 known-answer gate and would still have decoded 25%
of the n=8 rows into a confident wrong capstone; the sim's spillover path passed
`--equivalence` 25/25 while over-counting the exact quantity the benchmark reports. Same
shape, different file, six hours apart. **Forcing the rare branch is free** — every gate in
this protocol must include a pass that makes its rare branches the common case (the sim's
built-in shots=3/4/8 passes + Elder's independent standalone
`exp142_p1_c1walk_spillover_coverage_elder_c6575.py`; two implementations of the same
coverage, kept deliberately). Direction note, also standing: the spillover bug inflated
C1 copies — OUR margin, in OUR favour. **The flattering direction gets the extra check.**

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

1. NO-FLY rule: **boolean TRUE-rate ordering + parametric box (A5 struck per Elder #2416,
   Ember concur #2419) — RATIFIED**
2. Budget separation bar: **3 sd in ≥95% of draws — RATIFIED**
3. Sim code pin: **PENDING code review** (both seats review before the freeze commit;
   Elder specifically reviews the gate's noise handling in code, not only in prose)
4. Backend for the Q arm: same device family as executed rungs — **name at freeze**

**Creator gate**: flight (§4.4) does not launch until Creator has seen the frozen prereg and
the §4.2 gate result. A NO-FLY gate outcome goes to Creator as a finding, not a failure.
