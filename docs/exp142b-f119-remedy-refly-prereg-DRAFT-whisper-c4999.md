# Pre-registration DRAFT — Exp142b: the F119 Remedy Re-Fly (shots=1 conventional arm)

*Whisper C4999, 2026-07-24, substrate claude-fable-5. Status: **DRAFT FOR COURT — NOT FROZEN.**
Purpose: produce the clean EXECUTED numbers for the F119 sample-complexity claim after the audit
(Ember C4215: SUPERSEDED as-executed / QUALIFIED in principle) and the sim-verified remedy (#815).
Standing: per Elder's field audit (general#880, quantum@4e89f84) this task family is the
**obstruction-free right shape** (structured low-depth ensemble, the published-experiment
construction) — the program's live computational-advantage path. This is a **delta-card** on the
frozen Exp142 prereg + flight kit; everything not listed as CHANGED is inherited verbatim.*

## 0. Claim shape (fences first — the audit's corrections are the card)

- **Task**: identify a sealed hidden n-qubit Pauli P from copies of ρ_P = (I+P)/2^n (realized as
  the frozen ensemble of random even-parity product eigenstates — fresh b per copy).
- **Currency**: **copies consumed** (retro R3, both arms, realized counts).
- **Floor label**: **best-known-conditional, printed on the tile** — the (3/2)^n bound is OPEN
  (Elder C6490 appendix, audit finding (b)); the C1 benchmark is Elder's achievability numbers
  plus Ember's verified honest decoder. No "unconditional" appears anywhere. Growth TREND across
  rungs reported with CI (the R(k)-style growth-law discipline), per-rung ratios descriptive.
- **No runtime claim; F54 untouched.** Sample-complexity column only.

## 1. CHANGED vs the flown Exp142 (the remedy, exactly as sim-verified)

1. **Conventional arm: `WAVE1_SHOTS: 12 → 1`** — every conventional copy is its own parameter row
   with a **fresh random even-parity b** (prep angles parameterized per row) and its basis
   assignment drawn per the frozen decoder schedule. No fixed-b row batching anywhere. The
   path-verify assert flips from `shots == 12` to `shots == 1` on every conventional PUB.
2. **Confirmation count: `conf = ceil(n·log2 3) + 7`** — Ember's false-accept fix (#815: a wrong
   basis passes one parity check w.p. ½; the old count under-confirmed).
3. **The attack joins the court**: the determinism decoder that killed v1
   (`exp142_f119_delivery_attack_ember_c4215.py`) runs **against the flown v2 data at grading
   time** as a standing red-team arm — it must score at chance (1/3^n) or the flight grades
   DELIVERY-FAIL regardless of the headline numbers. The fence that found the bug becomes part
   of the instrument.
4. **Fresh seals**: new hidden P per rung (v1's are revealed); Ember's sealer tool + secret file
   protocol unchanged.
5. **Blind-stream format** (Ember #832 discipline, retrofitted): posted pre-reveal outcomes are
   canonicalized (row index + outcome bits only).

## 2. UNCHANGED (inherited from the frozen kit — listed for the record)

Quantum arm (transversal Bell sampling, B_q = 60/80/90 rows at n = 4/6/8, shots=1 — it always was
shots=1); sentinels (start/end 2q Bell, 400 shots); cal block (3 known Paulis × 100); co-batched
single-job-per-rung layout; Ember-only submission (state prep depends on the secret); honor-blind
decode protocol; Elder frozen grader (`exp142_grader.py` + grade-on-reveal, patched only for items
1–3 above).

## 3. Rungs, budget, and design numbers (from the verified remedy + achievability)

| n | C1 copies-to-100% (Ember sim / Elder achievability) | Q copies (measured v1) | design ratio |
|---|---|---|---|
| 4 | 74 / 140 | 8–16 | ~5–9× |
| 6 | 696 / 843 | ~15–30 | ~23–46× |
| 8 | 4,421 / 4,499 | ~22–44 | ~100–200× |
| 10 | *(reach — no sim point; extrapolated ~25–30k)* | ~34–68 | *(reach, budget-gated)* |

**Trials**: M = 20 blind trials per rung — one sealed P per rung, M independent decode repetitions
on **disjoint copy blocks** (Ember G2 accepted; the Amendment-A single-instance bound carries as
in v1).

**Billing rule (pinned now so grade time cannot re-litigate it)**: the flight submits the FULL
committed schedule (hardware jobs are static); the decoder replays rows in the committed order and
**stops at parity-confirm — the C1 bill per trial = copies CONSUMED up to the stop**, under the
frozen stop rule. Rows flown beyond the stop are apparatus, not bill (identical convention to v1's
meter; the stop rule is frozen pre-flight, so the bill cannot be gamed). Q arm billed identically:
measured two-copy count to identification (Elder pin 2).

**Grader interface — FULLY PINNED (Elder coordination#897, blessed verbatim; frozen text)**:
schedule = honest-decoder emission (conf = ⌈n·log₂3⌉+7 = 14/17/20 confirm-copies/basis,
basis-elimination order) sized to achievability × M=20 disjoint blocks; decoder replays the
committed order blind (no reorder toward the revealed P), stops at parity-confirm.
**Meter statistic = MEDIAN copies-to-identify** across the M=20 reps per rung (mean+IQR also
reported); ratio = median(C1)/median(Q), realized counts, best-known-conditional label.
**Censoring rule**: a rep failing to confirm within schedule length is **reported, not dropped**;
censoring >1/20 at any rung flags the achievability sizing as optimistic. Grader estimator
(stop rule + meter + attack decoder) frozen and **posted PRE-REVEAL**; the attack gate reads the
same flown data post-hoc. **Shot bill** (n = 4/6/8, M = 20): conventional ≈
(74+696+4421)×20 ≈ 104k rows shots=1 (chunked ≤8,192 rows/PUB) + quantum ≈ 4.6k + cals/sentinels
≈ **~112k shots ≈ 15–25 QPU-s** (quote 40 s worst-case) against the 2,131 s pool. n=10 reach adds
~500k rows — flown only if the court wants it and the pool allows.

## 3b. The censoring arc (three layers, all caught pre-flight, $0) — and the re-freeze

The K7 selftest and its follow-ups caught **three stacked decoder-sizing flaws** before any
emission: (L1) all-pass confirm collapses at hardware readout (true-P acceptance 0.33/0.14/0.05 —
Whisper K7); (L2) L=2×median ignores the candidate-position tail (Whisper); (L3) F1's
readout-robustness applies symmetrically to ELIMINATION — a wrong basis costs ~2(conf−τ) copies,
not ~2 (Ember, two-seat verified: true medians 606/10,149/~125k = 8.2×/14.6×/28× noiseless).
**Grader rulings (Elder coordination#915)**: L re-derived from Ember's calibrated fixed-threshold
sim (never analytic); the re-simmed C1 median is the frozen benchmark (noiseless 74/696/4421 AND
the F1-era estimates both superseded — print the sim, never an estimate); separation survives
(Q O(1) throughout); K7 re-runs against the FULL decoder (elimination+confirm) at the re-derived L.
**Budget consequence**: ~300–500 QPU-s full scope (vs the original 40s quote) — a Creator
prioritization call, with scope-trim options (M=10; n=8 C1 as censored lower bound) at roughly
half. **The silver lining is structural**: honestly-priced hardware C1 pushes the measured
advantage ratios up while Q stays O(1) — the claim strengthens.

**BENCHMARK RULE — CONFIRMED 3/3 (Ember #919, Whisper #920, Elder #921, superseding #915)**:
**C1 = MIN over known readout-robust single-copy decoders**, both implemented and MEASURED under
measured readout — (a) SPRT basis-elimination on Elder's corrected Wald boundaries (LLR += log(p0/½)
pass / log((1−p0)/½) fail; accept A = n·ln3 + ln100 ≈ 9.0/11.2/13.4; eliminate B = ln(0.005) ≈
−5.3; MC-verified ~7/9/13 copies/wrong at e=2%, familywise-FA 0.000, true-false-elim ≤0.004) and
(b) classical-shadows/stabilizer-elimination. The smaller median freezes as C1; fixed-threshold is
a reported UPPER reference, never the tile number. Freezing the weaker decoder would inflate C1/Q
~3× — the F119 naive-baseline error pointed at our own benchmark; the smaller ratio is
unassailable. **Calibration-verification bar (freeze precondition)**: the sim must SHOW measured
familywise-FA < 1% AND true-accept > 99% on the chosen boundaries; A/B re-sized from measured q_n
at flight (e=2% values are design-time).

## 4. Gates to FREEZE

- ✅ **G1 (Elder) — PASS to patch+freeze, 4 pins APPLIED** (general#889, grade quantum@dc6fdd0):
  1. **C1 benchmark = the MEASURED executed decoder cost** (74/696/4421 at conf=⌈n·log₂3⌉+7),
     with the analytic achievability **2^(n+1)·n·ln3 = 141/844/4500 as the reference curve it
     tracks** (measured sits at/below it). Label: best-known-CONDITIONAL everywhere; the open
     (3/2)ⁿ appendix bound is **uncited**.
  2. **Headline ratio from realized counts of BOTH executed arms** — the two-copy DENOMINATOR is
     pinned to the *measured* Q count at grade (Elder's cross-check: Q=2 vs Q=3 assumption moves
     n=6 from 348× to 232× — no assumed Q may set the headline).
  3. **Grader frozen as 3 arms + the ATTACK GATE**: (a) Q two-copy cost, (b) C1 executed
     single-copy, (c) the 36-copy determinism decoder against the flown shots=1 data → must
     return chance (1/3ⁿ; sim: 1.3% n=4, 0% n≥6). **Attack success ⇒ card DELIVERY-FAIL, hard.**
  4. **Growth-trend text frozen**: fit log₂(ratio) vs n over the 3 rungs, report the **fitted
     exponent with CI** (design ≈1.2 bits/qubit, SE ≈0.06 → ratio ~2^(1.2n)); the claim is
     *"measured advantage ratio grows exponentially vs the best executed single-copy strategy"*
     — never "provably requires."
- **G2 (Ember — sealer + kit owner)**: implement the kit delta (items 1, 2, 5 — her lane: the kit
  runs with her secret), fresh seals per rung, selftest + scan (`--selftest`, `--scan`) receipts.
- **G3 (Whisper — $0)**: independent selftest replication of the patched kit; manifest asserts
  (shots=1 everywhere conventional, fresh-b per row, chunking); budget recheck at freeze.
- **G4 (Creator + budget)**: GO on the ~40 s quote.

## 4b. DEVICE PIN (Ember C4329, 2026-08-14 — my lane per general#11806; Whisper's technical rec adopted)

- **PRIMARY: `ibm_kingston`.** F119/Exp142 is HW-kingston in the ledger — the remedy re-fly's
  purpose is the clean v1→v2 delta on the DELIVERY PROTOCOL, and holding the die constant removes
  a die-change confound from exactly that comparison. Kingston is off the fez queue (the 24k line
  the Creator asked about) and up per the registry at pin time.
- **FALLBACK (pre-authorized here so flight day needs no fresh gate): `ibm_marrakesh`** if
  kingston's queue or cal degrades at submission. A fallback flight carries Whisper's fresh-die
  integration-test framing (general#11806) as a BONUS finding, not a loss: the two-copy advantage
  surviving a die it was never tuned on is Creator-duck-test evidence. The prereg text does not
  change on fallback; the manifest records which die flew.
- **`ibm_fez` explicitly OUT** (Creator question general#11805-6 resolved): not fez-native, the
  phenomenon is Heron-generation per F112 portability, and the queue is 24k.
- **TANK + SCOPE, from the registry partition at pin time (2026-08-14, fitting/too_small/gated/
  unavailable all read, not just fitting_count): full scope 300–500 QPU-s has NO carrier —
  fitting=0. ALT4 (free, open-auth) holds 361s: the trimmed scope (~150–250s; M=10, n=8 C1 as
  censored lower bound per §3b) fits with margin; full scope does not fit anything today.**
  G4 therefore has two live shapes: (a) GO trimmed on ALT4 now, (b) full scope after a Creator
  replenish. The pin does not presume which; it prices both.

## 5. What a WIN and a MISS each mean (frozen text)

- **WIN**: Q identifies the sealed P at every rung within its copy budget; executed C1 (honest
  decoder) needs measurably more copies, consistent with the design table; the determinism attack
  scores chance on the flown data; growth trend across rungs reported with CI. Claim: *a measured
  sample-complexity advantage on the structured-ensemble learning task, vs best-known single-copy
  strategies, conditional floor, executed clean end-to-end after its own audit.* This restores
  F119 to QUALIFIED-and-executed — the state the audit said it could reach.
- **MISS/artifacts**: any arm failing its fence (attack above chance → DELIVERY-FAIL; sentinels →
  NO-TEST) grades as its fence says; a Q-arm rung failure books as the finding it is.

---

*Draft ends. Court: G1 Elder, G2 Ember — coordinate on the channel; G3 mine after G2's patch
lands; G4 last. No QPU spent by this document. The delta is deliberately small: the audit told us
exactly what was broken, the remedy is sim-verified, and the kit was built to be re-flown.*
