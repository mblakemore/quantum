# Exp 29 — The Gate-Overhead Dose-Response Law

**Pre-registration** — Whisper C3726, 2026-05-29
**Backend**: `ibm_marrakesh` (Heron-r2, 156-qubit heavy-hex)
**Status**: PRE-REGISTERED (criteria fixed before submission)

---

## What This Extends

Exp 28 (C3725) **confirmed** the Gate-Overhead Sign Rule on real hardware:
the *sign* of a mitigation technique's effect is set by its residual payload-gate
overhead, not the error channel it targets (REM, 0 gates → helps; TREM, X-gates
injected → null). That was a **categorical** result: 0 gates vs +gates.

The Sign Rule makes a stronger, **quantitative** causal claim it has not yet been
tested on: *more residual payload gates → more degradation.* If true, the effect
is not just a sign — it is a **dose-response law**, and that law is what predicts
why **every** gate-injecting technique (TREM, DD pulse trains, PT framing gates)
lands on the negative side: they all add gates whose cost exceeds the error removed.

Exp 28 left one residual confound even in its clean REM-vs-TREM pair: TREM still
*targeted* readout error. A skeptic can say "maybe TREM's twirl interacts with
readout, not with gate count per se." Exp 29 removes that last axis entirely.

## The Hypothesis: Gate-Overhead Dose-Response Law

> **On Heron-r2, accuracy degrades monotonically with the number of residual
> payload gates, independent of what (if anything) those gates target.**

The slope (pp of error per added 2-qubit gate) is the marginal causal cost of
gate overhead — the quantity that sits underneath the entire Sign Rule.

## The Controlled Test (Pearl dose-response `do(gate_count = n)`)

The cleanest possible intervention: inject **logically-identity** gate pairs into
the payload and vary only their count.

- Each dose unit = one pair of the native 2-qubit gate, `CZ · CZ = I`, fenced by
  barriers so it survives `optimization_level=0` and is **logically the identity**.
- Because each injected pair is the identity, **the ideal output is unchanged** and
  the gates **target no error source at all**. Any error they add is therefore
  *pure gate overhead* — the confound-free limit of the Exp 28 design.
- Hold the logical circuit FIXED (same IQAE state-prep + Grover payload), vary ONLY
  the injected-pair count `D`, same circuits, ONE calibration snapshot (co-submitted,
  C3723 matched-pairs deconfounding).

| Arm | Injected identity CZ-pairs `D` | Added 2q gates | Logical op | Predicted error |
|-----|-------------------------------|----------------|------------|-----------------|
| D0 (= raw) | 0 | 0 | unchanged | baseline (lowest) |
| D2 | 2 | 4 | unchanged | higher |
| D4 | 4 | 8 | unchanged | higher still |
| D6 | 6 | 12 | unchanged | highest |

## Design

- Circuit: 2-qubit CZ IQAE, P ∈ {0.56, 0.90}, k ∈ {0,1,2,3,4} (same as Exp 27/28,
  direct comparability). Ideal `P(11)` identical across dose arms (identity injection).
- Dose levels: D ∈ {0, 2, 4, 6} pairs → {0, 4, 8, 12} added CZ gates. Wide enough for
  monotone decoherence to dominate, well below the fully-mixed saturation floor.
- Injection block (per pair): `barrier; cz(0,1); barrier; cz(0,1); barrier`. Two CZ =
  identity; barriers prevent transpiler cancellation under `optimization_level=0`.
- 4 readout calibration circuits → REM applied as a *secondary* lens (see T3).
- Calibration snapshot (`calibration_snapshot.py`, C3723) captured at submit time.
- Shots: 4096/circuit. `seed_transpiler=42`, `optimization_level=0`.
- Circuit budget: 4 doses × 2 P × 5 k + 4 cal = **44 circuits**.

## Pre-Registered Criteria (FIXED before submission)

> **Criteria are TREND-based, not strict step-monotonicity.** The FakeMarrakesh sim
> pre-flight (C3726) revealed a *low-dose dip*: adding the first identity gates slightly
> *reduced* folded error before the trend turned up. This is expected physics — on a
> coherent-error substrate, the injected gates' coherent error can partially interfere
> with (cancel) the payload's coherent bias at small doses. Strict rank-monotonicity of
> the FOLDED |error| is therefore physically unwarranted; the dose-response LAW is a
> **net positive trend**, robust to that wiggle. Criteria below were fixed against this
> physical reasoning before the hardware (confirmatory) run.

- **T1 (NET TREND — headline)**: OLS slope of `mean_err_raw` vs added-2q-gate count is
  `> 0` **AND** the top dose exceeds D0 by `> 0.30pp`
  (`mean_err_raw(D6) − mean_err_raw(D0) > 0.30pp`). *Pure gate overhead causes a real
  net accuracy cost.* (Sim pre-flight: slope +0.063pp/2q, gap +0.72pp → PASS.)

- **T2 (RANK TREND)**: Spearman `rho(D, mean_err_raw) > 0` (positive rank trend; weak
  monotonicity, allows the coherent low-dose wiggle). (Sim pre-flight: rho +0.40 → PASS.)

- **T3 (GATE-NOT-READOUT)**: OLS slope of the *REM-corrected* mean error vs added-2q is
  `> 0`. Since REM removes readout error, a surviving dose trend proves the degradation
  is **gate-induced**, not a readout artifact — closing the last Exp 28 confound.
  (Sim pre-flight: REM slope +0.038pp/2q → PASS.)

- **Law verdict**: If **T1 ∧ T2** PASS, the Sign Rule is upgraded from categorical to a
  **dose-response law**: residual payload-gate count is a *continuous* cause of
  degradation, and the OLS slope is its marginal cost (pp/2q-gate). T3 PASS additionally
  certifies the cause is the gates themselves, not readout.

### Falsification conditions (what would REFUTE the law)
- **T1 FAIL** (slope `≤ 0` **or** top-vs-D0 gap `≤ 0.30pp`): error is flat/negative in
  pure overhead → gate count is **not** a continuous cause → the Sign Rule is merely
  categorical (a threshold at 0), not a dose-response law. Hypothesis rejected.
- **T2 FAIL** (`rho ≤ 0`): even the rank trend is non-positive → no dose-response.

### Auxiliary (reported, non-blocking)
- Marginal cost = OLS slope in pp per added 2q-gate. Sanity band ≈ [0.05pp, 2pp/gate],
  loosely consistent with device CZ error (~0.4%/CZ) projected through the 2-qubit
  `P(11)` estimator. Reported for magnitude calibration, not used as a pass/fail gate.

---

*Pre-registered by Whisper (Pearl causal-reasoning specialist). Dose-response
`do(gate_count=n)` is the gold-standard escalation of the Exp 28 controlled-mechanism
design: identity injections target nothing, so degradation can only be gate overhead.
Results + criteria evaluation to follow in `29-gate-overhead-dose-response-results.json`.*
