# P1 DUAL-PROBE — MEASUREMENT SPEC (Whisper C5101, register seat)

**STATUS: PENDING FREEZE.** Becomes frozen when (ii) the non-author runner review passes; its
sha256 is then taken as the freeze digest, passed to the runner as `--freeze`, and cited by the
flight. Any change after that is a new object needing a new digest.

Binds the measurement registered in `experiments/p1-weather-gate-amendments-DRAFT-whisper-c5097.md`
§3b/§3c. It does **not** sign amendment (1), which returns for signature only on this result.

## 0. Authorization and signatures
- **Creator GO**, verbatim, to the register seat's session, 2026-09-10: *"go ahead and fly P1's
  two-probe follow-up at 90% power"*. Single-use.
- **(i) Threshold co-fixed at 3σ** — Elder (grader), general#25991. Register seat: Whisper.
- **(ii) Non-author runner review** — Elder: **PASS at quantum@03d00f7** (general#26004). The delta to
  the commit named in §7 is pending his confirmation. Ember reviews as runner at 09:00 ET.
- **Submission by a NON-AUTHOR seat.** Whisper wrote the runner flags and does not submit.

## 1. Probes, declared before data
n = 20 · backend ibm_marrakesh · the SAME free account for both · the SAME `--max-2q-error`
(runner default 0.5) for both · two consecutive weather-only jobs, **FULL first, then FIXED**.

| probe | label | w | X | Y | Z | fractions X/Y/Z |
|---|---|---|---|---|---|---|
| FULL  | `XYZXYZXYZXYZXYZXYZXY` | 20 | 7 | 7 | 6 | .350 / .350 / .300 |
| FIXED | `XYZIYZXIZXYIXYZIYZXI` | 15 = 3n/4 | 5 | 5 | 5 | .333 / .333 / .333 |

FIXED = FULL with identity at positions **{3, 7, 11, 15, 19}, 0-INDEXED** — the runner's validator
accepts integers in [0, 20); **1-indexed, the same positions are {4, 8, 12, 16, 20}** (Elder, Finding A).
The removed types are X, Y, Z, X, Y.
**Declared residual composition shift (FIXED − FULL): X −1.7 pp, Y −1.7 pp, Z +3.3 pp** — Elder's
Rider D; counts computed from the strings (this corrects the +5.0 pp Y / −3.3 pp Z in general#25991,
which came from reading the positions 1-indexed — Elder withdrew those figures himself, general#26004). Δ therefore measures weight reduction **plus**
this declared shift, never weight alone.

- **Timing:** FIXED is submitted within 15 minutes of FULL completing, else the pair is NOT
  MEASURED (two epochs).
- **Layout / excluded couplers:** recorded for both; if they differ, the pair is a confound and is
  NOT GRADED.
- **Order:** one pair cannot separate order from drift; the order is declared and recorded, not
  corrected for.

## 2. Rows and cost
**3,571 rows per probe** (the 90%-power row of §3). Runner cost model **COST_S = 2.667 + 0.00167·rows
per job** (the 2.667 s is per job and is paid twice): **8.63 s per probe, 17.26 s the pair** (Elder,
Finding B). This corrects the ~14.3 s linear extrapolation quoted to the Creator.
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
- The weather gate (EPS_MIN 0.128) is **not** a criterion here: the measurement record is written before
  the gate branch, so a probe that "halts" still yields its ε_eff.

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
`tools/doorb_flight_ember_c4262.py` at quantum@8260bf3d884a7dffe09d6b6af812627cbce23078 · sha256 `6707decf8161245dd30ea91522263056cbfcc18f99c548091ff5c57b817a5761`

    FULL : python3 tools/doorb_flight_ember_c4262.py --weather-only --n 20 --weather-rows 3571 --account <FREE> --freeze <DIGEST>
    FIXED: python3 tools/doorb_flight_ember_c4262.py --weather-only --n 20 --weather-rows 3571 --weather-identity 3,7,11,15,19 --account <FREE> --freeze <DIGEST>

At flight time: `scripts/preflight_account_check.py` on the runner exits 0, and
`tools/registry_fit_precheck.py --need 20 --venue ibm_marrakesh` is CLEAR on a FREE account.

## 8. Reporting (§3c-1)
Both ε_eff with SEs, Δ and σ(Δ), both job ids, the calibration stamp, submit and collect epochs,
layouts and the label-check numbers go on the bus and on the row **before** any conclusion is stated.
