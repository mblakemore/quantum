# Exp 28 — The Gate-Overhead Sign Rule for NISQ Error Mitigation

**Pre-registration** — Whisper C3724, 2026-05-29
**Backend**: `ibm_marrakesh` (Heron-r2, 156-qubit heavy-hex)
**Status**: PRE-REGISTERED (criteria fixed before submission)

---

## The Tension This Resolves

The campaign holds two results that appear to contradict:

- **Finding 7** ("Software Error Mitigation Is Largely Futile"): DD, Pauli Twirling, TREM,
  and ZNE-at-N=4 all **degraded** signal on `ibm_marrakesh`. The finding's own caveat:
  these measurements were taken **cross-day and cross-circuit** (DD on syndrome circuits
  C3666, PT/TREM C3668–69, ZNE on Bell/GHZ C3651), and *"±7pp daily calibration drift
  dwarfs any mitigation gain — you cannot honestly report a 2pp improvement without
  specifying the calibration day."* By its own standard, Finding 7's verdict is confounded.

- **Exp 25–27** (C3720–22): ZNE+REM delivered **59% error reduction** on the 2-qubit CZ
  IQAE circuit (2.49pp → 1.02pp, a new hardware record), measured in a **single
  co-submitted job** (all arms share one calibration snapshot → drift cancels in the
  relative comparison; the C3723 matched-pairs deconfounding design).

These do not actually contradict — they are confounded against each other along **two
uncontrolled axes**: (a) calibration day, (b) target circuit. Finding 7 could not isolate
*why* some techniques help and others hurt because it never varied a single mechanism while
holding everything else fixed.

## The Hypothesis: Gate-Overhead Sign Rule

> **On Heron-r2, the SIGN of a mitigation technique's effect on accuracy is governed by its
> residual payload-gate overhead, NOT by the error source it targets.**
>
> - Techniques that leave **zero residual gates** in the measured payload — pure
>   post-processing (M⁻¹ readout correction / REM), or fold-and-extrapolate-away (ZNE at
>   N where its scaling model holds) — extract net positive value.
> - Techniques that leave **residual injected gates** in the payload (TREM's pre-readout
>   X-gates, DD's pulse trains, PT's framing gates) are net negative or null, because on
>   this substrate active-gate error (~0.4%/CZ, microwave cross-talk) dominates the passive
>   error they were designed to suppress.

This reframes Finding 7's coarse "mitigation is futile" into a **predictive rule**: the
added-gate count predicts the sign.

## The Controlled Test (Pearl `do(mechanism)`)

To isolate gate-overhead as the cause, we **hold the target error source fixed** (readout
error) and vary **only the correction mechanism**, on the **same circuits** under the
**same calibration snapshot** (co-submitted):

| Arm | Mechanism | Residual payload gates | Predicted sign |
|-----|-----------|------------------------|----------------|
| **Raw** | none (same-day floor / fix #2 reference) | 0 | baseline |
| **REM** | M⁻¹ post-processing of counts | **0** (classical) | **net POSITIVE** |
| **TREM** | random X-twirl before readout, XOR-corrected | **+X gates/qubit** | **net NEGATIVE / null** |
| ZNE | unitary folding (λ=1,3), extrapolate to λ=0 | 0 (extrapolated away) | net positive |
| ZNE+REM | both | 0 | best (control, from Exp27) |

REM vs TREM is the headline: **identical target (readout), opposite gate-overhead.** Any
gap between them under one calibration snapshot is *mechanism*, not weather. This is exactly
the confound Finding 7 said it could not remove — removed here by co-submission.

## Design

- Circuit: 2-qubit CZ IQAE, P ∈ {0.56, 0.90}, k ∈ {0,1,2,3,4} (same as Exp 27, direct comparability)
- ZNE scale factors: λ ∈ {1, 3} (2-point, validated optimal C3722)
- **TREM arm (new)**: 2-mask symmetrization twirl per cell — mask `00` (identity) and mask
  `11` (X on both qubits before measure), each measured, classically XOR-corrected back,
  then averaged. Faithful minimal TREM; isolates the pre-readout gate injection.
- 4 readout calibration circuits (shared by REM and as TREM reference)
- Calibration snapshot (`calibration_snapshot.py`, C3723) captured at submit time → results
  tagged with the day's T1/T2/CZ-err/readout-err/calib-timestamp.
- Shots: 4096/circuit. `seed_transpiler=42`, `optimization_level=0` (preserve folding/twirl).
- Circuit budget: 20 ZNE main + 20 TREM (2 masks × 2P × 5k) + 4 cal = **44 circuits**.

## Pre-Registered Criteria (FIXED before submission)

- **T1 (REM helps)**: `mean_err(REM) < mean_err(Raw)`.
  Post-processing readout correction reduces error. *(Expected PASS.)*

- **T2 (THE SIGN RULE — headline)**: `mean_err(TREM) > mean_err(REM)`.
  Same target (readout), but the gate-injecting mechanism underperforms the post-processing
  one on the *same circuits under one calibration snapshot*. Isolates gate-injection — not
  the readout-correction goal — as the cause of TREM's degradation. *(Expected PASS.)*

- **T3 (TREM no net benefit)**: `mean_err(TREM) ≥ mean_err(Raw) − 0.3pp`.
  Consistent with Finding 7's −0.7pp TREM result, now under matched calibration so the
  ±7pp-drift excuse is removed. *(Expected PASS / borderline.)*

- **Reconciliation verdict**: If **T1 ∧ T2** PASS, Finding 7 is REFINED, not overturned:
  *"gate-injecting mitigation is futile on Heron-r2; zero-gate-overhead mitigation
  (post-processing REM, extrapolate-away ZNE) extracts genuine value"* — and the prior
  "futile" verdict is shown to have been an artifact of cross-day/cross-circuit confounding.

### Falsification conditions (what would REFUTE the rule)
- If `mean_err(TREM) ≤ mean_err(REM)` (T2 FAIL): the sign is **not** governed by gate
  overhead — the readout-correction goal matters more than the mechanism. Rule rejected.
- If `mean_err(REM) ≥ mean_err(Raw)` (T1 FAIL): even zero-gate post-processing fails →
  Finding 7's blanket "futile" stands, hypothesis rejected.

## Why DD and PT are excluded (scope discipline)
- **DD** targets idle-T₂ dephasing, which is ~20× below active gate error here (Finding 7) —
  designed-out for this circuit, and carries a silent-scheduling-failure hazard. Out of scope.
- **PT** converts coherent→stochastic error, but Heron-r2 noise is already stochastic
  (Finding 7) — null by construction. Out of scope.
- The **readout pair (REM vs TREM)** is the cleanest possible isolation: same error source,
  opposite gate overhead. One clean variable beats three noisy ones.

---

*Pre-registered by Whisper (Pearl causal-reasoning specialist). Matched-pairs co-submission
deconfounding design (C3723) applied to error-mitigation methodology. Results + criteria
evaluation to follow in `28-gate-overhead-sign-rule-results.json`.*
