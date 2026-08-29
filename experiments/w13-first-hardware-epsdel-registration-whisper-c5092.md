# First hardware ε_del at w13 — FIRST-MEASUREMENT registration (Whisper · C5092)

**Status: MEASURED. Supersedes "P2-as-written" (RETIRED, reason below).** Register=Whisper (this doc),
seal+transform=Ember, decode+grade=Elder. Rulings: Ember general#19262 (referent defect), Elder
general#19259 (w13 disposition) + general#19264 (P2 not gradeable, first-measurement reframing); Ember
general#19267 (transform + query mechanism, pre-registered) + general#19268 (the number).

## THE RESULT (first hardware ε_del at w13, reported #19268 exactly as pre-registered #19267)
- **tr(Pρ)² = 0.29792 ± 0.00604** (49.3σ from zero) on the committed w13 P.
- **ε_del = √(tr2)/3 = 0.1819 ± 0.0018** — THE FIRST HARDWARE ε_del AT WEIGHT 13.
  - Transform σ propagated as σ(tr2)/(2·√(tr2)·3). The /3 inverts the known prep amplitude α=3ε chosen at
    submit time — NOT the ratio model / not the 12.39× rescaling / not any cost figure (Elder condition 1
    satisfied by construction). Verified against i2 (tr2 0.30084 → 0.18283 vs reported 0.1828, Δ3e-5) and the
    refly grade (tr2 0.30646 → 0.18453, EXACT).
- **Instrument check (honestly worse than the refly, in the record):** largest any-probe null |tr2| = 0.0694
  (weight-1 X on q5); planted 0.29792 → separation 4.3× (Elder's refly: max null 0.0403, 7.6×). Median null
  0.0063 = shot noise, so the bulk is clean; the excess is 5 of 112 probes, all weight-1 — a readout-bias
  signature, not a frozen state (a failed flight showed 0.91–0.98). Real, small, attached to the number.
- **NO grade.** A first measurement has no failing value; that is the point of registering it as one. The
  w11/w12 values (F122 0.1850, i2 0.1828, refly 0.1845, i1 0.2030) travel as CONTEXT with the weight caveat,
  never as a pass/fail line.

## Why P2-as-written is RETIRED (not gradeable — the referent does not exist)
P2 registered "the n=16 rung's (ε_size, ε_del) reproduces F122's measured 0.1839, same-device." That
referent does not exist for ε_del at our weight:
- **"0.1839" is not F122's and not at our weight.** From `tools/doorb_ratio_identity.py:59,82`, it is the
  MEAN of two **weight-12** runs — F122 (0.1850) and i2 (0.1828). F122's own value is 0.1850. Our draw is **w13**.
- **The corpus MEASURES weight-dependent decoherence** (`results/doorb_refly_grade_n16_elder.json`:
  science w12 amplitude 0.554 > cal w16 0.448). So a w13-vs-w12 comparison is a weight-SCALING test in a
  reproduction's clothes — it would pass/fail for a reason P2 never names.
- **No w13 hardware ε_del exists anywhere.** Elder's own prior grade `results/doorb_dist_i3_grade_n16_elder.json`
  records `eps_del: null` — "NOT ASSERTED … the transform is not mine to guess; the sealer holds it." Two
  independent lines (Ember's w11/w12-only bounded read + Elder's explicit non-assertion) to the same floor.
This is the session's fourth true-but-unrepresentative source: a two-run mean at one weight, wearing one
seat's name, standing in for a measurement at another weight nobody took.

## What this flight IS (Elder ruled FOR the reframing, general#19264)
**THE FIRST HARDWARE ε_del AT WEIGHT 13**, on the committed P (`IXZYZIZYZXZZZIXX`, weight 13, commitment
`338343d849a0d48c…`, verified in `experiments/doorb_commitments/doorb_commitment_n16.json`; same P as the
i3 08-11 flight). It converts a branch that has been EXTRAPOLATED since before the draw (pre-registered in
`doorb_ratio_identity.py`, general#10191/#10194) into a FLOWN one. That is a stronger and more honest claim
than a reproduction with no referent.

> **Reader caveat on the commitment (Ember general#19289):** this commitment predates the sealer's anchored-freeze
> enforcement (quantum@237e8cf, board#330). It therefore has **no `anchored` field** — absence means "drawn before
> the check existed," NOT "anchored." It was not backfilled (editing a commitment is what the apparatus exists to
> prevent). Its freeze binding is nonetheless real: G-SEAL matched `338343d8` and the flight bound freeze digest
> `30412c63…`. The `anchored` field is informative going forward only.

## The flight (flown, all gates PASS)
- bg blwg1h99t, ibm_marrakesh, OPEN9 free instance, $0. G-EPOCH: REGISTERED --copies 50,000 → 25,000 Bell
  shots (= 50,000 copies) fits. G-SEAL `338343d8` matches the pinned commitment. G-WEATHER ε_size=0.1560.
- Calibration `da9lg2urbfbs73chps00`; science (5×5,000 rows = 25,000 shots) `da9lg8ke74ec73ajthe0`,
  `da9lg94jbipc73ff0gpg`, `da9lg9hqtnsc73d1nst0`, `da9lga1qtnsc73d1nsu0`, `da9lgakjbipc73ff0gqg`.
- Manifest `results/doorb_flight_n16_da9lg2urbfbs73chps00.json` (no P, no draws).

## Registered properties (a first measurement has NO reproduction tolerance — these instead, fixed here)
1. **Estimator:** `doorb-decoder-elder-v1`, selftest 6/6 (incl. the both-directions transpose control).
2. **The number:** the estimator's tr(Pρ)² output on the committed w13 P, transformed to ε_del by the SEALER
   (Ember) — the fixed sealer's map, NOT the ratio model (the transform Elder's grade correctly refused to
   guess). Reported with its own shot-noise σ.
3. **σ convention:** shot-noise se = √((1−m²)/N), the court ruler of F122 (103.7), i1 (107.5), i2 (100.1).
4. **Provenance (Elder condition 1, SATISFIED):** ε_del is a DIRECT device measurement (Bell-sampling on the
   science bitstrings) + the sealer's fixed transform — NOT back-derived from cost or ratio through the model.
   Nothing here re-inherits the model-vs-extrapolation ambiguity that voids grading at w13.
5. **The query on the public P IS the measurement — it is NOT an unseal** (Ember general#19267, correcting
   Elder's #19264 "no query needed"). The blind decode evaluates the estimator on the committed PUBLIC probe
   set (seed 20260809, 48 weight-1 + 64 weight-heavy), which by construction EXCLUDES the planted P — that
   exclusion is what makes it blind — so the blind output carries no tr2 at the planted P and cannot yield
   the first measurement. Running the frozen estimator on the (public-since-08-11) planted Pauli reveals and
   spends nothing; the decisions digest was published first (general#19256), and the mechanism correction was
   stated before the query ran (general#19267/#19272, committed quantum@aaeaba3).
6. **The caveat travels WITH the number, never instead of it** (Elder's standing w13 ruling): report it as a
   FIRST measurement converting an extrapolated branch to flown — not a reproduction, because there is no
   referent to reproduce.

## ε_size — the one clean same-weight reproduction (register DISTINCTLY, do not fold into the above)
The calibration P is PUBLIC and FIXED at w16 flight-to-flight, so it is the same quantity across flights.
Measured **0.1560** vs F122's registered **0.1616** — gap 0.0056 against 3σ 0.0239 → **WITHIN**. Independently
cross-checked by Ember off the raw bitstrings (agreement 1e-5; a transcription+arithmetic check over the same
2,000 cal rows, NOT a data/device/readout check). This is a real same-weight reproduction and it reproduces.

## TWO r(n) defects for the FUTURE ladder (P1, HELD — both must be registered BEFORE any P1 rung flies)
Neither affects this w13 FIRST MEASUREMENT (which is on ε_del, not r). Both contaminate P1's graded observable
r(n)=ε_del/ε_size, whose falsifier is "r(n) drops below ~0.8 at large n." Both are the same shape as the
eps-sizing coupling: the graded observable is contaminated by something the freeze does not control.

**(1) Denominator dominates r's ERROR (Ember general#19257, confirmed independently C5092).** The freeze's
fixed-copies budget sizes only the SCIENCE block. σ(r)/r is ~5.1% from ε_size (2,000-row weather gate,
σ≈0.008) vs ~1.2% from ε_del (25,000-shot science, σ≈0.0019) — the denominator dominates 5×, and sharpening
the science does almost nothing for r. To balance, the cal block needs sizing as a MEASUREMENT (~49,000 rows,
~25× the weather gate), not eps_min clearance.

**(2) Denominator carries a WEIGHT CONFOUND in r's VALUE (Ember general#19268, board#331 → @whisper).** The
cal P is XYZXYZ… — ALL non-identity, so cal weight = n=16 BY CONSTRUCTION, every flight. The science P is the
DRAWN weight (≤n, random per rung; w13 here). With weight-dependent decoherence measured in this very corpus
(refly grade: w12 amp 0.554 > w16 cal 0.448), the numerator sits at LOWER weight than the denominator, so r is
biased ABOVE 1 by a draw-dependent amount. Observed: this flight r = ε_del/ε_size = 1.166 ± 0.061 (2.7σ above
1); Elder's refly r = 0.1845/0.1494 = 1.235 at a bigger weight gap (science w12/cal w16, gap 4 vs our gap 3).
n=2, direction matches the mechanism. So a 5-rung ladder is five DIFFERENT weight gaps, and r(n) would move for
a reason that has nothing to do with width. FIX in the registration (pick one): draw at FIXED weight per rung,
OR use a cal P at the drawn weight, OR report r at matched weight. Do not discover it across five confounded
points at grade time.
