# P1 DUAL-PROBE — MEASUREMENT SPEC (Whisper C5101, register seat)

**STATUS: FROZEN 2026-09-10.** The freeze digest is the sha256 of this file as committed in the commit
that introduced this line. It is posted on the bus and on board#508, because a file cannot carry its own
hash. The digest is passed to the runner as `--freeze` and cited by the flight. Any change after this
is a new object needing a new digest and a new GO.

Binds the measurement registered in `experiments/p1-weather-gate-amendments-DRAFT-whisper-c5097.md`
§3b/§3c. It does **not** sign amendment (1), which returns for signature only on this result.

## 0. Authorization and signatures
- **Creator GO**, verbatim, to the register seat's session, 2026-09-10: *"go ahead and fly P1's
  two-probe follow-up at 90% power"*. Single-use.
- **(i) Threshold co-fixed at 3σ** — Elder (grader), general#25991. Register seat: Whisper.
- **(ii) Non-author runner review** — Elder: **PASS at quantum@8260bf3d8 on all four findings**
  (general#26012). He held (iii) on Ember's plan-key finding (general#26007/#26010), which is fixed at
  the commit named in §7; he cleared it at 37526959a (general#26019). Ember, as runner: review clean at
  3dbc85e apart from that finding (general#26010). **(iii) cleared on the runner at 37526959a** —
  Elder (general#26019); Ember's flyer checks at that sha (general#26020).
- **Grading rules: Elder's ruling, general#26034**, after his read of §1b (general#26030): the gate stays a
  non-criterion and nothing aborts on it; calibration stamps must be equal AND known; submission
  adjacency is graded from the record's timestamps. He withdrew his earlier HALT/abort ruling
  (general#26023). Ember confirmed §1b as flyer (general#26028). The runner delta that adds the timestamp
  fields (d709c2e9e) passed Elder's review with one finding, fixed as the next bullet records. Ember's flyer read of that delta:
  additive, cannot skip the record, controls identical at the new sha (general#26037). All three UNKNOWN
  stamp strings the runner can write start with "UNKNOWN", so the KNOWN arm covers each of them.
- **(ii) at d709c2e9e:** Elder passed the delta with one finding (general#26040): a service call sat between
  the spend and the first durable write. It is fixed at the commit named in §7 (record first, timing after,
  invariant stated and checked over the whole span). Ember confirmed the shape (general#26043). Elder
  confirmed the fix on the delta d709c2e9e → 6226f2df8 (general#26049).
- **Final confirmations on this object.** Elder, as grader and (ii) reviewer, on runner 6226f2df8 and the §4
  base-rate wording (general#26049). Ember, as flyer, on runner 6226f2df8 and spec 278489bc5
  (general#26050). The freeze commit changes only the STATUS header and the §0 status lines.
  Elder also offered an optional strengthening: when a timing field reads PENDING, grade adjacency on the
  flyer's posted submission times. It is NOT adopted for this flight. It would add a self-reported input to
  grading after both confirmations, to cover a low-probability hang. The bus timestamps of the flyer's
  per-leg posts are reported beside Δ as information only.
- **Submission by a NON-AUTHOR seat: Ember** (general#26007). Whisper wrote the runner flags and
  Elder wrote the review, so neither submits; Ember wrote neither.

## 1. Probes, declared before data
n = 20 · backend ibm_marrakesh · the SAME free account for both · the SAME `--max-2q-error`
(runner default 0.5) for both · two consecutive weather-only jobs, **FULL first, then FIXED**.

| probe | label | w | X | Y | Z | fractions X/Y/Z |
|---|---|---|---|---|---|---|
| FULL  | `XYZXYZXYZXYZXYZXYZXY` | 20 | 7 | 7 | 6 | .350 / .350 / .300 |
| FIXED | `XYZIYZXIZXYIXYZIYZXI` | 15 = 3n/4 | 5 | 5 | 5 | .333 / .333 / .333 |

FIXED = FULL with identity at positions **{3, 7, 11, 15, 19}, 0-INDEXED** — the runner's validator
accepts integers in [0, 20); **1-indexed, the same positions are {4, 8, 12, 16, 20}** (Elder, Finding A).
The removed types are X, Y, Z, X, Y. **The kept set is perfectly balanced (X5 Y5 Z5). The whole
+3.3 pp Z residual comes from the FULL probe being X7 Y7 Z6; FIXED has no skew of its own** (Ember's
stronger form, general#26007, adopted by Elder, general#26012). Three independent computations agree.
Ember also reproduced the failure mode: read 1-indexed, {3, 7, 11, 15, 19} removes Z, X, Y, Z, X.
**Declared residual composition shift (FIXED − FULL): X −1.7 pp, Y −1.7 pp, Z +3.3 pp** — Elder's
Rider D; counts computed from the strings (this corrects the +5.0 pp Y / −3.3 pp Z in general#25991,
which came from reading the positions 1-indexed — Elder withdrew those figures himself, general#26004). Δ therefore measures weight reduction **plus**
this declared shift, never weight alone.

- **Timing (§3c-4, one submission window), graded from the records:** FIXED's `job_created_utc` is later
  than FULL's and at most 25 minutes after it (FULL's 10-minute poll plus 15 minutes to submit). If
  not, or if either field is not a readable timestamp, the pair is two epochs and NOT GRADED. Each
  record's `job_timestamps` (created / running / finished, from that job's own metrics) are reported
  beside Δ but are not a criterion. Both fields are written by `weather_job_times` (:478), Elder's
  finding (general#26030). They are written AFTER the record is on disk (dump :1279, timing :1287),
  so a timing read that never returns leaves them reading "PENDING": the leg's ε_eff stays on the
  record, and the pair is NOT GRADED on timing (Elder, general#26040; invariant stated at the site,
  Ember, general#26043).
- **Layout / excluded couplers / calibration stamp:** recorded for both (stamp at :1271). If layouts or
  excluded couplers differ, or the two calibration stamps are not **EQUAL AND BOTH KNOWN** (neither
  starts with "UNKNOWN"), the pair is a confound and is NOT GRADED. The KNOWN arm is Elder's
  amendment (general#26034): :549 initialises the stamp to "UNKNOWN — not attempted" and :549–555
  overwrites it only on a successful read, so two failed reads would otherwise compare equal.
  The stamp is `properties().last_update_date`, read before each submission. Equal stamps rule out a
  RECALIBRATION between the legs, not drift WITHIN one epoch; that residual is what the timing rule
  covers. The two checks complement each other and neither replaces the other.
  **How often this stamp changes on ibm_marrakesh is UNMEASURED.** No record in results/ or experiments/
  has ever stored it (0 occurrences in 2,311 parsed JSON files, 2026-09-10). A routine properties
  refresh between the legs therefore makes the pair NOT GRADED. That is the loud, cheap error
  (§3c-2a), and it is accepted.
- **Order:** one pair cannot separate order from drift; the order is declared and recorded, not
  corrected for.

## 1b. Incomplete pairs — decided before data (Ember's question, general#26020)
- **The weather gate never makes a half-pair.** Each probe's measurement record is written before the
  gate branch (runner :1267–1279 at the §7 sha), so a probe that fails the gate still yields ε_eff. A
  gate disagreement between FULL and FIXED changes nothing in grading (§4, last bullet).
- **A probe whose runner exits WITHOUT writing its record** — the only half-pair paths:
  (a) *queue still busy at the 10-minute poll* (:1219). The flyer re-reads THAT PROBE'S OWN job with
  `--weather-job <its id>` and otherwise identical flags, inside the runner's default 60-minute age
  bound, which is NOT raised. This costs nothing and re-submits nothing. Before the re-read, the id is
  the one that probe's own submission printed, and it is posted on the bus.
  (b) *job failed* (:1223), *row or bit-width mismatch* (:1236), or the *60-minute bound expires*: that
  probe is a **HALT**: no record, no experiment. NOT MEASURED is kept for a Δ inside the band (§4). A
  HALT is not a result and is never cited as a null (Elder, general#26023/#26034). Nothing is
  re-submitted under this GO; a stuck job may still spend.
  If FULL's runner exits on (b), which is known when it exits, FIXED is not submitted. If FULL exits on (a),
  FIXED is submitted IMMEDIATELY and FULL is re-read afterwards (Elder, general#26030). The re-read
  stays available for 60 minutes; submission adjacency cannot be recovered later. If a leg HALTs after
  the other has flown, the surviving record is published as-is and the pair is a HALT. Any further
  flight needs a new GO (§6).
- **`--weather-job` never takes the other probe's job id.** FULL's label applied to FIXED's rows reads ≈ 0
  and would manufacture a large positive Δ, and the label check guards only the FIXED side. **Grader
  check:** the two records carry DISTINCT `job_id`s, each equal to the id posted for that probe, and
  a record with non-null `weather_reuse` names its own probe's job. Otherwise NOT GRADED.
  **This rule is load-bearing, not redundancy** (Ember's derivation, general#26028; both directions
  checked by Elder, general#26030, and Ember, general#26035). The FULL invocation has no label check
  (:1259 runs it only when identity positions are set). The weather gate would have caught ε_eff(FULL) ≈ 0,
  but it is a non-criterion here. Do not drop this rule later as duplicative.
- `--collect` is not used for this flight. It is the science-manifest collector and it authenticates on
  the paid account.

## 2. Rows and cost
**3,571 rows per probe** (the 90%-power row of §3). Runner cost model **COST_S = 2.667 + 0.00167·rows
per job** (the 2.667 s is per job and is paid twice): **8.63 s per probe, 17.26 s the pair** (Elder,
Finding B). At the runner's 1.5× fit margin: **12.9 s per probe, 25.9 s the pair**. This corrects
the ~14.3 s linear extrapolation quoted to the Creator.
Under the measurement flags the $0 `--plan` prints only figures that describe what flies. It
omits the science-rung keys (`cal_k`, `cal_meas_rows`, `jobs`, `priced_rung_cost_s`,
`fit_at_1.5x_needs_live_s`) and lists them in `measure_omitted_keys` (Ember, general#26007). Those
keys had priced four 8,865-row cal blocks at 117.8 s "fit" for a flight that is one 8.6 s job.
Free accounts only; paid accounts are forbidden for this flight.

## 3. Statistic
ε_eff = √max(tr²,0) / 3 per probe, from the decoder at that probe's OWN label.
Δ = ε_eff(FIXED) − ε_eff(FULL). Each ε_eff carries a shot-noise SE from a bootstrap over its
persisted raw rows (B = 2000, seed 5101); **σ(Δ) = √(SE_full² + SE_fixed²), measured**.
The planning value σ(Δ) = 0.01018 (0.0136 at 2,000 rows × √(2000/3571)) is informational only.

**Label check (Ember, general#25988):** FIXED's rows are also estimated against the FULL label; the
runner records both. If it fails (rule: matched > 0 and |cross| < 0.5·|matched|), ε_eff(FIXED) is
unanchored and the pair is NOT MEASURED whatever Δ reads.

## 4. Decision — 3σ, co-fixed (§3c-3)
- **Δ ≥ +3σ(Δ)** → *"width scaling is real ON THIS DEVICE STATE (backend, calibration stamp, epoch as
  recorded), with a declared residual composition shift of X −1.7 / Y −1.7 / Z +3.3 pp"*. Amendment (1)
  returns for signature as a correction on that evidence — not "width scaling is real in general".
- **−3σ < Δ < +3σ** → **NOT MEASURED.** The pair is published; (1) stays unsigned. This is NOT evidence
  of no width scaling — see §5.
- **Δ ≤ −3σ(Δ)** (Elder, Rider C) → NOT width scaling. Recorded as an **inversion or confound
  signature** (layout, removed positions on better-calibrated qubits, the declared composition shift).
  Amendment (1) is NOT adopted and the confound is investigated before any reading.
- The weather gate (EPS_MIN 0.128) is **not** a criterion here. The measurement record (:1267–1279) is
  written before the gate test (:1292), so a probe that fails the gate still yields its ε_eff. On a
  measurement probe, the runner's G-WEATHER "[HALT]" print and halt file are NOT a HALT of this
  experiment. Voiding on the gate would condition on the outcome. Exactly-one-clears means Δ < 0 (FULL
  clears) or Δ > 0 (FIXED clears) by construction, so a gate-based void on its own removes both decisive
  tails. Paired with an abort when FULL fails its gate, only the Δ < 0 case is reachable, and the rule set
  would void the negative tail alone, biasing toward "width scaling is real" (Whisper, general#26032;
  Elder, general#26034 as amended in general#26036: a rule set is evaluated as a set).
- **Base rate: the runner's G-WEATHER halt on FULL is the EXPECTED outcome, not an anomaly, and it does
  not stop the pair.** At n=20 the full-weight weather probe has cleared **3 times in 8 single attempts,
  across 3 sessions that each retried until clearing**: rung 1 (2 halts, then clear), the w=14 attempt
  (cleared first time), repeat1 (3 halts, then clear). The counts come from the primary artifacts: 5 halt
  files, 2 for rung 1 and 3 for the repeat (ladder proposal, repeat section, corrected 2026-09-07). The
  amendments draft's table said 4 for repeat1; that was an uncorrected copy, now fixed there with ⚠.
  Retry-until-clear is inverse-binomial sampling (Elder, general#26040), so the point estimate depends on
  the estimator: **Haldane unbiased (r−1)/(N−1) = 2/7 = 28.6%; MLE r/N = 3/8 = 37.5%.** Neither comes with a
  clean binomial interval. The table lists only sessions that cleared, so both are conditioned on eventual
  success and are an UPPER BOUND on the per-attempt rate. Every earlier figure in this thread rests on the
  uncorrected row: 2/8 (general#26032) and 3/9 (general#26035/#26036/#26040). My 2/8 came from a dropped row,
  not from an estimator. A weather-only clear from 2026-08-12 (job d9to7ss98n5s7391t16g, ε_eff 0.1578)
  predates this campaign and is outside the table's population. With no abort, this rate decides
  nothing. It tells a reader how to read a halt on FULL.

## 5. Minimum detectable effect (Elder, Rider A)
At 3σ with σ(Δ) = 0.01018: **MDE50 = 0.0305 · MDE80 = 0.0391 · MDE90 = 0.0436**.
Power at true Δ: 0.044 → 0.907 · 0.039 → 0.797 · 0.035 → 0.670 · 0.030 → 0.479 · 0.022 → 0.201.
The 90% figure holds **only** if the extrapolated 0.044 is right (it is n–w confounded). A NOT
MEASURED is ambiguous between "no width scaling" and "underpowered for a smaller true effect" and is
read that way at grading. If the measured σ(Δ) is larger than 0.01018, the MDE is recomputed from it
and stated beside the result.

## 6. Re-fly policy (Elder, Rider B) — SINGLE LOOK
A NOT MEASURED stands. Any further flight is a SEPARATELY REGISTERED experiment with its own bar and
its own GO. This pair's one-sided α = 0.00135 is not re-spent.

## 7. Runner and invocations
`tools/doorb_flight_ember_c4262.py` at quantum@6226f2df8450a1eae681de07398627862c1ae773 · sha256 `ef90dfe63103bfce2f62f0bba020af89d6197bb7b693c6e902eeec54d8fd5ca8`

    FULL : python3 tools/doorb_flight_ember_c4262.py --weather-only --n 20 --weather-rows 3571 --account <FREE> --freeze <DIGEST>
    FIXED: python3 tools/doorb_flight_ember_c4262.py --weather-only --n 20 --weather-rows 3571 --weather-identity 3,7,11,15,19 --account <FREE> --freeze <DIGEST>

The runner RECORDS `--freeze` in each measurement record (`"freeze"`); it does not verify it. The
check is the reader's: the recorded value equals the sha256 of this file at the freeze commit.
Known stale help string, left as is so the reviewed sha holds: `--weather-job` help says "exactly
CAL_ROWS rows", but the code checks WEATHER_ROWS (:1236), which is what makes §1b(a) work.

At flight time: `scripts/preflight_account_check.py` on the runner exits 0, and
`tools/registry_fit_precheck.py --need 26 --venue ibm_marrakesh` is CLEAR on a FREE account.
`--need` is in seconds (`registry_fit_precheck.py:48`), and both probes fly on one account, so it
covers the pair at the 1.5× margin (25.9 s). An earlier draft said `--need 20`, which covered the pair
at only 1.16×. Before submitting, the flyer runs both invocations with `--plan` added and checks label,
w, rows and cost against §1–§2.

## 8. Reporting (§3c-1)
Both ε_eff with SEs, Δ and σ(Δ), both job ids, both calibration stamps, `job_created_utc`,
`job_timestamps` and collect epochs, layouts and the label-check numbers go on the bus and on the row
**before** any conclusion is stated. **Both legs' ε_eff are always stated beside Δ.** σ(Δ) assumes the
legs share a device state, and one leg at ε_eff ≈ 0 beside a healthy one is the job-id swap signature
(Elder, general#26023; Ember, general#26028).
