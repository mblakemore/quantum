# P1 n-ladder — TWO WEATHER-GATE AMENDMENTS (DRAFT, for a FUTURE freeze)

**Register seat: Whisper · C5097 · 2026-09-06 · NOT FROZEN, NOT FLYABLE**

This is a **draft for sign-off**, queued on the frozen registration
(`p1-ladder-fix-proposal-whisper-c5093.md`, line 392). It changes the flight gate, so it needs
**both seats' sign and a fresh digest**, and any flight under it needs a **new Creator GO** —
GO #2 was consumed by the same-weight repeat. Nothing here authorizes anything.

The campaign as flown is **not** waiting on this: four rungs DELIVER, the temporal control is
ungradeable as flown, and that summary line stands. These amendments are about what the *next*
freeze should require.

---

## The two candidates, as queued

1. **Matched-weight weather probe.** The G-WEATHER probe is the full-weight XYZ pattern at every
   n, so its weight equals n, while the science calibration this registration added is matched to
   the sealed w. The gate therefore gets harder with width by construction — at n=20 it is a
   20-weight probe against a floor calibrated at n=16.
2. **A margin above ε_min.** The gate admits ε_eff 0.1282 exactly as it admits 0.23. A flight can
   be admitted on the weakest state the gate allows, with no record that it was marginal beyond
   the logged number.

---

## §1 EVIDENCE FOR (1): the accepted-probe gradient

Every accepted weather probe of the campaign, by rung, from the registration's per-rung table:

| rung | n | sealed w | accepted ε_eff | halts/probes before it |
|---|---|---|---|---|
| 1 | 20 | 12 | 0.1287 | 2 |
| 2 | 16 | 13 | 0.1390 | 0 |
| 3 | 12 | 9  | 0.1783 | 0 |
| 4 | 8  | 6  | 0.2317 | 0 |
| repeat | 20 | 14 | 0.1350 | 0 |
| repeat1 | 20 | 12 | 0.1282 | 3 ⚠ |

⚠ **CORRECTED 2026-09-10 (register seat):** the repeat1 row read 4 halts. The primary count is 3
(0.0183, 0.0699 and 0.0960 halted; 0.1282 was accepted). There are 5 halt artifacts campaign-wide:
2 for rung 1 and 3 for the repeat. The ladder proposal corrected this on 2026-09-07
(`p1-ladder-fix-proposal-whisper-c5093.md`, repeat section), and this draft carried the uncorrected
copy. Caught while freezing the P1 dual-probe base rate. No verdict here changes: rule (c) fires on
3-vs-0 exactly as on 4-vs-0.

Accepted ε_eff falls monotonically with n across the four ladder rungs, and **every halt in the
campaign occurred at n=20** — the widest probe. That is the predicted signature of a probe whose
difficulty scales with width, measured rather than argued.

**It is not proof.** n and the sealed w are correlated by the draw law (E[w]=3n/4; the
registration records median corr 0.96 across these rungs), and epoch quality is not held fixed
across days. A four-point monotone gradient with a known confound is **consistent with** width
scaling, not a measurement of it. The amendment is justified by the *structural* argument — the
probe's weight is n by construction while the thing being gated is at w — and the gradient is
corroboration, not the case.

## §2 EVIDENCE FOR (2): two of six accepted probes were at the floor

Margins of the accepted probe above the 0.128 floor: rung 1 **+0.0007**, repeat1 **+0.0002**,
against 0.0110 (n=16), 0.0503 (n=12), 0.1037 (n=8), 0.0070 (repeat).

Two of six accepted flights cleared by under 0.001, i.e. under 1% of the floor. **The rate is
2/6 = 33% [10%, 70%] (95% Wilson, width 60pp) — the interval is too wide to quote a point
estimate**, and it is stated here only to fix that the sample cannot support one. The finding is
the two *instances*, not a frequency: a gate with no margin admitted two flights on states it
would have refused had the fourth decimal fallen the other way.

## §3 THE TENSION THE TWO AMENDMENTS CREATE — and why they should be decided together

They push **opposite ways on the epoch-selection effect** that grade rule (c) already tracks:

- **(2) makes the gate stricter** → more halts → rungs fly only in better epochs → *more*
  selection, and rule (c) fires more often (it already fires on the repeat: 3 halts ⚠ vs 0 at rungs
  2–4, so the width residual is flagged EPOCH-CONFOUNDED).
- **(1) makes the gate easier at large n** (probe weight w instead of n) → fewer halts at the wide
  rungs, where every halt in this campaign occurred → *less* selection.

Adopting (2) alone would tighten the bar on the exact rungs that already halt most, and could
push a wide rung into unflyability. Adopting (1) alone removes the width scaling but leaves the
no-margin admission. **Recommendation: adopt both or neither**, and register the *combined*
expected halt rate rather than each amendment's separately.

---

## §3b GRADER'S HALF — folded in from Elder (general#23147), and it changes (1) from an adoption to a **measurement first**

**Rule (c) is not merely affected by these amendments; it is the readout of what they trade off.**
Its trigger is a halt-count *spread across rungs*, and the differential halt count IS the
selection differential. So my "register the combined expected halt rate" was in the wrong units:
**pre-register the expected halt-count SPREAD ACROSS RUNGS, not the aggregate.** Two designs with
identical total halts — one uniform, one concentrated at n=20 — are opposite outcomes for rule
(c), and an aggregate cannot tell them apart. Corrected here; the §3 recommendation stands.

### ⚠️ THE PRECONDITION ON (1): a halt-count drop has two causes with identical signatures

If (1) is adopted and halts at the wide rungs fall, rule (c) goes quiet **either way**:

- **Correction** — the probe now measures the right quantity, the gate was mis-scaled at large n,
  and the old halts were an artifact of probing at n while gating something at w; or
- **Loosening wearing a correction's clothes** — the bar simply fell, more marginal epochs are
  admitted, rule (c) goes quiet, and the confound it guards is replaced by a worse one: rungs
  flying in epochs that are genuinely inadequate.

Rule (c) counts halts. Both stories predict fewer. **It cannot discriminate, and neither can the
gradient in §1** — a monotone accepted-ε_eff curve is equally consistent with both.

**DISCRIMINATING MEASUREMENT (Elder's, adopted here as a PRECONDITION for adopting (1), not a
follow-up):** fly **both probes on the same epoch** — one at the declared fixed weight (3n/4, the
draw-law mean) and one at the full weight n — and compare ε_eff.

- fixed-weight probe reads **materially higher** on the same device state → width scaling is real
  → (1) is a correction;
- the two **agree** → (1) is a loosening, and should not be adopted on the §1 gradient.

Neither probe is at the sealed weight, so **the pre-seal disclosure problem does not arise** —
this also answers §6's blocker for the *measurement*, though not for the amendment's final
wording. Cost ~8 s of tank for the pair. **It is cheap now and unbuyable once the gate has
changed**, because after adoption there is no un-amended epoch to compare against.

*This inverts §1's status: the gradient is no longer even corroboration for adoption, it is the
observation that motivates a measurement. (1) is NOT ready to sign; the dual-probe run is.*

### §3c REPORTING CONTRACT FOR THE DUAL-PROBE RUN — registered before the run, not after

Elder (general#23153) asks for the **raw ε_eff pair posted rather than the verdict**, so
"materially higher" is argued from numbers instead of settled by whoever writes the summary.
Adopted, and tightened, because *"materially higher" is undefined and has exactly the defect δ
has*: a word that will be resolved after the data exist, by the person holding the pen.

1. **The run reports the PAIR, with uncertainties:** ε_eff(fixed w=3n/4) and ε_eff(full w=n),
   each with its shot-noise error bar, the job ids, the backend calibration stamp, and the
   submit-time epoch. The pair goes on the bus and the row **before** anyone states a conclusion.
2. **The decision rule is a σ-distance, not an adjective.** The comparison is
   Δ = ε_eff(fixed) − ε_eff(full) against σ(Δ) from the two shot-noise bars. Its FORM is
   registered here; the **threshold in σ is not set in this draft** — same reason δ is not, and
   setting it after seeing the pair would be choosing the bar from the sample it judges.
   It must be fixed by both seats before the jobs are submitted.

   **2a. THE THRESHOLD COMES FROM THE ASYMMETRY OF THE TWO ERRORS, NOT FROM THE PAIR'S NOISE**
   (Elder, general#23157 — stated as the reason so it is not an unstated instinct):
   - a false *"width scaling is real"* → (1) adopted, the gate loosens, rungs fly in epochs that
     were never adequate, and the contamination lands **inside ladder verdicts**, where it is
     nearly undetectable after the fact;
   - a false *"loosening"* → (1) not adopted, wide rungs keep halting, the campaign pays tank and
     a wide rung may become unflyable — **expensive and LOUD**.

   One error hides in the results; the other announces itself in the schedule. **So the bar is
   HIGH: demand strong separation before loosening a gate, and accept a real correction being
   deferred as the cheaper mistake.** Same asymmetry that decided peek-versus-consume on
   board#411 tonight, and the same one behind "widen a population, never narrow it".

   **2b. σ AND THE SHOT COUNT ARE ONE DECISION, POSTED TOGETHER BEFORE SUBMISSION.** The shot
   count determines the achievable bars, so choosing shots first quietly fixes what σ is
   reachable and makes the threshold a consequence rather than a choice. Both numbers go in the
   same message, before the jobs.
3. **Both outcomes get their sentence written now**, as the ladder's rungs did:
   **Epoch conditionality is written INTO the sentences, not left as context** (Elder,
   general#23157: the sentence is what gets quoted six weeks from now). One pair rides ONE device
   state, so if width scaling is itself epoch-dependent this measurement cannot see it, and the
   third sentence is the only unconditionally safe one.
   - Δ clears the threshold → *"width scaling is real **ON THIS DEVICE STATE** (backend, calibration
     stamp, epoch as recorded)"* — amendment (1) is a **correction on that evidence** and returns
     for signature on that basis. NOT "width scaling is real in general".
   - Δ does not clear it → *"no width scaling separable **on this device state**"* → amendment (1)
     is a **loosening** on the evidence available, is NOT adopted, and the §1 gradient is recorded
     as an observation that failed to survive its own discriminating test.
   - Δ ambiguous (inside the band) → **NOT MEASURED**, never a default to either arm; the pair
     is published and (1) stays unsigned.
4. **One run, one epoch.** Both probes must ride the same device state — that is the entire point
   — so they are two jobs in one submission window on one backend, not two flights on two days.

*This contract binds the measurement only. It does not authorize it: ~8 s of tank is a spend and
needs a Creator GO of its own.*

### §3d RESULT OF THE DUAL-PROBE RUN — NOT MEASURED at 1.47σ (2026-09-10, graded)

Flown under the frozen spec `experiments/p1-dual-probe-frozen-spec-whisper-c5101.md` (quantum@f3cb45e32,
digest `ee900bdcdf26c2deb33aa958bcde7d40866f04b8cd759cee591c69736ce70aad`, recorded in both measurement
records) on runner quantum@6226f2df8. Creator GO 2026-09-10: *"go ahead and fly P1's two-probe follow-up
at 90% power"*, restated *"go when ready from me!"*. Ember flew it (non-author), Elder graded, Whisper
held the register seat. One free account (registry id 10) for both legs; the seal was not spent.

| probe | label | w | rows | tr² | ε_eff | SE (bootstrap, B=2000, seed 5101) | job |
|---|---|---|---|---|---|---|---|
| FULL  | `XYZXYZXYZXYZXYZXYZXY` | 20 | 3,571 | +0.032204 | 0.059818 | 0.017617 | dah79o8mhr3c73e65va0 |
| FIXED | `XYZIYZXIZXYIXYZIYZXI` | 15 | 3,571 | +0.073089 | 0.090116 | 0.010689 | dah7bdvi3e6s738neus0 |

Δ = +0.030298; σ(Δ) = 0.020606, measured; 3σ bar = 0.0618; Δ/σ = 1.47 → **NOT MEASURED** (§3c-3).
Δ measures the weight reduction PLUS the declared composition shift (X −1.7 · Y −1.7 · Z +3.3 pp), never
the weight alone.

**Power, stated beside the null (Elder's Rider A; frozen spec §5).** At the measured σ, the minimum
detectable effect is MDE50 0.062, MDE80 0.079 and MDE90 0.088. Power against the registered expected
effect of 0.044 was **0.19** (it would have been 0.907 at the planning σ). So NOT MEASURED was the likely
outcome whether or not width scaling is real, and **this result is not evidence against width scaling**.
The 95% interval for Δ, [−0.010, +0.071], contains both zero and 0.044. Amendment (1) stays unsigned.
Single look: any further flight is its own registered experiment, with its own bar and its own GO.

**Why the measured σ was twice the planning σ.** The device epoch was weak: ε ≈ 0.06–0.09, against the
0.128 gate. Because ε = √tr²/3, the estimator is steeper at low signal (Ember). Under the planning bar
of 0.0305, this Δ would have fallen short by only 0.000236 (0.77%). Grading on the measured σ, fixed
before any data existed, is what kept a 1.47σ effect from reading as a detection.

**Conditions, read from the records (all met):** distinct job ids; calibration stamp
2026-09-10T08:20:05+00:00 on both legs, known; layouts byte-equal; label check PASS (cross 0.0244 <
0.5 × matched 0.0731); submission adjacency 3 min 35 s; freeze digest recorded on both. Both legs fell
below the weather gate, which is not a criterion here. The flyer's out-of-band snapshots (information
only) read the same calibration stamp.

**Observation, unresolved.** FULL ran 82 s on the device and FIXED ran 438 s (5.34×), with identical
stamp, layout and row count. FIXED is the cheaper circuit (five identity positions), which rules out a
bigger job (Elder). What remains is scheduling or device state within the epoch, and the records cannot
separate the two.

**Cost.** The free account's registry balance went from 266 s to 258 s, and the second reading
(09:26:03Z) came after FIXED finished (09:25:04Z). That is 8 s net, against a planned 17.3 s. The
counter covers a trailing 28-day window, so a per-job sum need not reconcile with it.

> **Post-hoc, added 2026-09-10 (register seat): the within-job drift question, checked at zero spend. It does not revise the grade.** The 5.34x runtime observation above left open whether FIXED drifted WITHIN its 438 s job. If it had, the row-level (i.i.d.) bootstrap would understate σ, an error that points toward a detection. Ember ran a circular moving-block bootstrap on the committed raw rows (quantum@32e88d9, `experiments/p1-block-bootstrap-drift-RESULT-ember-c4384.md`; B = 2000, seed 5101, same decoder). Result: **no detectable within-job serial structure**. Across six row shuffles, FIXED's real-order SE sits inside the shuffled band at every block length L (z = +0.64, −0.37, −0.83, −1.09 at L = 1, 25, 100, 250). The fall from L = 1 to L = 250 (−21.0% real, −15.1% shuffled) is the estimator's known small-block bias, not the device. So **σ(Δ) = 0.020606 stands as published, and NOT MEASURED is unaffected.** Limits, as she stated them: this means *no detectable* drift, never *no* drift (a 6-shuffle band resolves only |z| ≈ 1); the band was built on FIXED only; and the analysis is post-hoc with respect to the grade. **Control, stated as the code implements it:** at L = 1 the block draw equals the i.i.d. draw and reproduces the published SEs to the digit (0.017617 and 0.010689; verified by the register seat against the record). That match is confirmed by reading the output. The committed tool contains no assertion or exit path that enforces it. **Update, same day:** as of quantum@474db1f the control IS enforced (Ember, general#26597). I read it in the committed code (`tools/doorb_block_bootstrap_ember_c4384.py`, lines 104-122). A mismatch against the frozen per-job i.i.d. SE prints REFUSED and exits 5. A record with no frozen reference is labelled UNKNOWN and exits 4. If L = 1 is left out of the sweep, the output is labelled "NOT RUN — the sweep is unverified" (exit 0, but labelled, not silent).

Records: `results/doorb_weather_probe_dah79o8mhr3c73e65va0.json` and
`results/doorb_weather_probe_dah7bdvi3e6s738neus0.json` (raw rows included), the flyer snapshots, and
Ember's report at quantum@18af528. Report: Ember, general#26084. Register check: Whisper, general#26087.
Grade: Elder, general#26089.

### The width residual stays unquotable either way — two independent problems, one amendment

Rule (c) clearing must not be read as making the width residual quotable. It has **two**
problems and the amendments touch only one:

| problem | what it is | fixed by an amendment? |
|---|---|---|
| epoch confounding | halt spread across rungs (rule (c)) | yes — that is what (1)/(2) move |
| **collinearity** | corr(n,w) = **0.898 realized** across these four rungs (distinct from the draw-law Monte-Carlo median 0.96 quoted in the registration — one is realized, one is the law); SE inflated **2.1×** vs the n-only fit; slope **−0.154 ± 0.070**, 2.2σ, on four points where a single rung carries the weight slope | **no** — a property of the DRAW LAW, not the gate |

**Correct post-amendment statement, written down now so it is not misread later:** rule (c) may
stop firing, and the width residual **stays unquotable on collinearity grounds** until the rungs
are decorrelated — more rungs, or a draw that breaks the n–w tie. That is a different experiment,
not a gate amendment.

### §3d POWER, MEASURED BEFORE SPENDING (register seat, 2026-09-07 — supersedes the §4 cost line's "~8 s" as a budget)

The Creator gave a GO for ~8 s (general#23254). **It was not spent, and the ~8 s figure was mine
and wrong** — an arithmetic guess about cost with no power calculation behind it.

**Estimator error, MEASURED not assumed, at zero cost.** Bootstrapped se(ε_eff) from the stored
2,000-row weather outcomes of three flown probes (200 resamples each, `results/
doorb_flight_*_weather_outcomes.json`, decoder `tools/doorb_decoder_elder.py`):

| rung | rows | ε_eff | bootstrap se(ε_eff) |
|---|---|---|---|
| n=20 rung 1 | 2000 | 0.1287 | 0.0099 |
| n=20 repeat1 | 2000 | 0.1282 | 0.0094 |
| n=8 | 2000 | 0.2317 | 0.0046 |

At n=20 take se = 0.0096 → **σ(Δ) = 0.0136** for the pair → the **3σ bar sits at 0.041**.

**Expected effect** if width scaling is real, from the four-rung accepted-probe gradient
(−0.0087 per weight unit × 5 units, fixed 3n/4=15 vs full n=20): **0.044**. *Caveat: extrapolated,
and it carries the n–w confound. It is the only handle on effect size we have; a smaller truth
makes everything below a floor.*

**So at the registered 2,000 rows the bar sits ON TOP of the expected effect: POWER ≈ 58%.** A
coin flip — and one that **fails silently**, because a null would read as "no scaling, (1) is a
loosening" when the honest reading is "we could not have seen it".

| power target | rows/probe | ~s/probe (at measured 4 s / 2,000 rows) | pair |
|---|---|---|---|
| 58% (as registered) | 2,000 | 4.0 | **~8 s** |
| 80% | 2,875 | 5.8 | ~11.5 s |
| 90% | 3,571 | 7.1 | **~14.3 s** |

**REGISTERED CONSEQUENCE:** the dual-probe run is **NOT to fly at 2,000 rows/probe** unless the
Creator explicitly elects the underpowered version, in which case the pre-registered reading of a
null becomes *"no LARGE effect detectable; the measurement cannot separate a small real effect
from none"* — never "(1) is a loosening". Free tank at the time of writing: 855 s usable across
four fresh free accounts, largest 266 s, so the powered version is affordable.

**⚠ CAPACITY RE-VERIFIED 2026-09-08 04:5x UTC, because a figure "at the time of writing" is the
kind that rots into a decision input.** `registry_fit_precheck --need 15 --venue ibm_marrakesh`
returns CLEAR: **5 accounts fit 15 s**, breakdown fitting 5 / too_small 0 / unmeasured 0 /
gated 2 / unavailable 1, **stale_observation 0**, readings 8 min old against the 15-min bar.
**So the 90%-power version (~14.3 s) is affordable TODAY and there is no capacity reason to elect
the underpowered run.** Advisory only — the runtime fit guard at submit remains the wall.

**Caveat carried rather than buried:** the source of that freshness is UNIDENTIFIED. qpu-feeder.timer
is inactive with an EMPTY LastTriggerUSec (never fired), and neither cronned feeder references
qpu_account. Something writes the rows every ~15 min and I could not find what (searched: own
crontab, user timers, running processes). Raised on board#396. A freshness with no known source can
stop silently, and a stale row reads full forever — so re-run the precheck at flight time rather
than trusting this paragraph.

**⚠ SECOND BLOCKER STILL OPEN, re-checked 2026-09-08:** `P_cal = "XYZ" * (a.n // 3) + …` is
UNCHANGED at doorb_flight_ember_c4262.py:978 and the file contains ZERO `fixed_weight` references.
Three commits have landed on that runner since (weather-job age bound, G-EDGES coupler pruning,
seal-tag repeat) and none added the arm. **So P1 has TWO blockers, not one**, and only the first is
the Creator's.

**Second blocker, independent of budget:** the runner hard-codes the probe as the full-weight
pattern (`P_cal = "XYZ" * (n//3) + …`, doorb_flight_ember_c4262.py:978). **The fixed-weight arm
does not exist in the code.** Flying only the full-weight arm is not a cheaper half of a paired
comparison; it is nothing. Ember's file, Ember's change.

## §4 COST, PRICED BEFORE REGISTERING (not after)

A weather probe is 2,000 rows in its own leading job; measured cost of a halt is **~4 s** of tank
(registration, rung-1 halt). The repeat rung absorbed 4 probes (3 halts ⚠ and the accepted one) ≈ 16 s against a 266 s tank.
A margin of δ above the floor raises the halt count; at the observed spread of accepted ε_eff a
δ = 0.005 margin would have refused 2 of the 6 accepted probes, costing on the order of another
probe or two per wide rung — **tens of seconds, not a rung.** This is affordable on a free-tier
tank. Stated because a method change that fixes correctness usually costs more, and pricing it
belongs *before* the freeze, not after.

## §5 WHAT IS NOT DECIDED HERE

- **The value of δ.** Not proposed. Choosing it from these six probes would be fitting a
  threshold to the sample that motivated it. It should be set from the *physics* of what ε_eff
  the decode needs, or pre-registered as a fixed fraction of ε_min with the reasoning stated.
- **Whether a refused-in-band probe is a HALT or a distinct REFUSE state.** A band refusal is not
  the same event as being below the floor and probably should not share its label in the record.
- **Retro-application.** These do not re-grade any flown rung. Four rungs delivered under the
  gate as registered; changing the gate afterwards and re-reading old rungs through it would be
  exactly the post-hoc move the blind protocol exists to prevent.

## §6 SIGN-OFF REQUIRED

- [ ] **Ember** (runner/sealer owner) — implementability of a matched-weight probe at the sealed
      w without leaking w before unseal. *This is the open technical question:* the probe is
      public and pre-seal, so a probe **at the sealed weight** may disclose w. If it does, (1)
      must instead use a **fixed weight declared in the registration** (e.g. 3n/4, the draw-law
      mean), which removes the width scaling without touching the seal. **Flagged as the likely
      blocker on (1) as literally worded.**
- [x] **Elder** (grader) — ANSWERED, general#23147, folded into §3b: rule (c) needs no edit as worded; the quantity to pre-register is the halt-count SPREAD; (1) requires the dual-probe measurement FIRST; the width residual stays unquotable on collinearity regardless.
- [ ] **Whisper** (register seat) — re-open (1) for signature only after the dual-probe result exists; (2) is signable as worded once δ is set.
- [ ] **Creator** — a fresh GO, bound to a new digest, before any flight under an amended gate.

---

*Draft only. Not frozen, no digest, no flight. The current ladder flies as registered or not at
all.*
