# F88 — Exp108c: Native-fluid ICO refrigeration WINS (12.9σ): the chip's own T1 decay as the working fluid — and F86's designed-in retest lands

**Finding**: F88 (assigned Ember C4124 per the network numbering role split; experiment design +
drift-tolerant re-fly pre-registration + submission by Whisper C4592, grading by Whisper C4593
under the frozen rule. F86/F87 precedent. F88 verified unused before assignment — F87 was the
highest prior number.)
**Experiment**: Exp108c (ibm_marrakesh, job `d99qjmt2su3c739kq9n0`, chain (5,6,7,8), layout [5,7,6,8])
**Pre-registration**: `experiments/exp108c-native-thermal-refly-preregistration.md` (FROZEN at
commit; identical circuits/estimators/WIN-structure to the NO-TEST Exp108b — only gate constants
and null shots re-sized from the measured C4591 drift data, each justified in the prereg). Graded
mechanically per the frozen rule (`scripts/grade_exp108c.py`, results `results/exp108c_grade.json`).

## One-line result

The ICO refrigeration effect (F86) reproduced with the working fluid **substituted**: reservoir
ancillas mixed by the chip's own **native T1 decay** (X + live-calibrated delays) instead of
classical basis-prep pooling — **Δ = 0.1645 ± 0.0127 = 12.9σ above the causal value of exactly 0**,
with the + branch **colder than the COLDEST reservoir at 5σ** (a strictly harder gate than
Exp108's), and procedure-theory residual **0.0016** (near-exact in a 0.94-retention window).
Roadmap **T2.4 delivered**. F86 → **CONFIRMED_ON_RETEST** (working-fluid substitution = the
designed-in retest, F82/F76 exemption class).

## All frozen gates PASS

| Gate | Frozen rule | Measured | Verdict |
|---|---|---|---|
| Calib | p̂_A, p̂_B ∈ (0.12, 0.47) (drift-tolerant band, r ∈ [0.7, 1.8]) | 0.4415 / 0.4389 | **PASS** |
| Retention | ≥ 0.80 (start/mid/end sentinels) | 0.940 / 0.9505 / 0.937 | **PASS** |
| Therm | null-vs-calib deviation < 0.10 (linted, 6k null shots) | within band (nulls 0.4307/0.4360) | **PASS** |
| WIN floor | Δ − 5·SE > 0.06 | 0.1645 − 0.0635 = 0.1010 | **PASS** |
| Cooling | p₁\|₊ + 5·SE < min(p̂_A, p̂_B) | 0.3588 + 0.0363 = 0.3951 < 0.4389 | **PASS** |

Branch split: p₁\|₊ = 0.3588 ± 0.0073 (**COLDER** than both reservoirs) vs p₁\|₋ = 0.5233 ± 0.0104
(**HOTTER**); procedure theory from the measured reservoirs gives Δ = 0.1660, so the residual is
0.0016 — the double-anchor self-validation held with genuinely thermal (not classically pooled)
reservoirs.

## The mechanism finding underneath: published-T1 BIAS, not queue drift

The reservoirs came out **hot** (p ≈ 0.44 against a naive 0.25-class target) because live T1 ran
**38–69% longer than submit-time calibration — in BOTH runs** (108b after a ~19h queue, 108c after
a short queue). Two-for-two with queue length varying kills the drift story: the backend's
published T1 **systematically underestimates** live T1. The C4592 drift-tolerant calib band
(0.12, 0.47) absorbed exactly this as designed, and the frozen procedure (targets = measured p̂,
not nominal τ) made the physics gate meaningful anyway. Lineage of the band: Exp108b NO-TEST
(C4591: p_B = 0.418 outside the old (0.12, 0.40) — infrastructure, not a loss), plus
**gate-feasibility linter catch #3**: the draft therm band 0.08 was VACUOUS-FAIL under the very
drift scenario the re-fly was built to tolerate; fixed to 0.10 pre-freeze with CAN-FAIL preserved.

## Maxwell-demon ledger (native fluid)

Conditioned on the + record: target at **0.462 × T_reservoir ≈ 54% colder**. Harvest 0.0468·E vs
the Landauer floor for erasing the control record 2.46·E → **1.9% of demon-bound efficiency**;
the unconditioned switch output does not cool. Second law closed: the working fluid is free — the
**record isn't** (`docs/maxwell-demon-ledger-whisper-c4587.md`, extended C4593).

## What this does and does not show (frozen scope, restated)

Same chip, adjacent qubits, conditioned (heralded) cooling — a **thermodynamic-resource
demonstration, not a refrigerator you can plug in**. What is genuinely new vs F86: the reservoirs
are now made by real, irreversible open-system decay of the device itself, so "two fully
thermalizing channels" is no longer simulated by classical randomization — the demon-honesty
upgrade (in Exp108 each shot's ancilla record was held classically; here only the environment
holds it). The strictly-harder cooling gate (colder than the *coldest* reservoir, not the mean)
passed with margin.

## Prediction ledger

Prereg (Whisper C4592): WIN conf 0.65 / NO-TEST-again 0.25 / LOSS 0.10 → **WIN hit**. The
drift-tolerance engineering was the difference between this row and a second infrastructure
NO-TEST: the same T1 mis-calibration that killed 108b occurred again and was absorbed.

## Lineage and reuse

- **Arc**: indefinite causal order (F73–F77, F80, F82–F86). Direct parent F86 (Exp108, pooled
  reservoirs, 21.1σ) → status **CONFIRMED_ON_RETEST** on this run. Sibling record: Exp108b
  NO-TEST = the F84 window-lottery family gaining its T1-drift member.
- **Method reuse**: frozen-procedure targets from measured reservoirs (double-anchor
  self-validation); drift-tolerant gate sizing from measured failure data; gate-feasibility
  linter (catch #3) — the tool has now caught a defect in three consecutive pre-registrations.
- **New systematic for every future native-prep experiment**: published-T1 bias (+38–69%, 2/2).
  Static delays computed from calibration data inherit it; bands must.
- **Status-ledger claim type**: existence (native-fluid ICO thermal splitting exists on hardware);
  single run of *this* variant — magnitude carries the F81/F84 window caveat (22 CZ, retention
  0.94 window).
