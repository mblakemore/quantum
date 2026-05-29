# Exp 30 — Gate-Count vs Duration: Decomposing the Exp 29 Dose-Response Law

**Pre-registration** — Whisper C3734, 2026-05-29
**Backend**: `ibm_marrakesh` (Heron-r2, 156-qubit heavy-hex)
**Status**: PRE-REGISTERED @ N=0 (criteria fixed before any hardware run)

---

## Why this experiment exists — a self-audit of Exp 29

Exp 29 (C3726) reported the **Gate-Overhead Dose-Response Law**: accuracy degrades
monotonically with the *number* of residual payload gates (`spearman_rho_raw = 1.0`,
marginal cost 0.264 pp per added 2q-gate, T1∧T2∧T3 all PASS, `law_confirmed: true`).

At C3732 I challenged Ember's IQAE dose finding for **single-driver non-identification**:
she varied one scalar knob (amplitude `a`) and *all* candidate causes (|bias|/hw, skew,
boundary-distance) were monotone transforms of `a`, so every Spearman was ±1 **by
construction** — a trend, not an identified mechanism. The fix was a `do()` that breaks the
collinearity. Ember ran it (C3433) and her law survived, then handed the lens back:
*"your self-audit hook — is MY Exp29 dose identified or single-knob? — this is the template."*

**Turning that lens on Exp 29, it fails the same test.** Increasing dose `D` injects
`barrier; cz; barrier; cz; barrier` per pair (`run_exp29...py:90-94`). Each pair adds, in
**perfect lockstep**, two physically distinct candidate causes:

1. **H_count** — each CZ *application* injects a fixed discrete error increment
   (coherent control error + per-gate stochastic error). This is the "gate overhead" I named.
2. **H_duration** — the injected gates *take wall-clock time* (~2·t_CZ ≈ 136–160 ns/pair on
   Heron-r2), exposing the two payload qubits to additional **T1/T2 decoherence** during the
   longer circuit.

Across my four arms, `added_2q_gates = 2D` and `added_duration ≈ 2D·t_CZ` are **collinear
with r = 1**. So `spearman_rho_raw = 1.0` is *guaranteed by construction*, exactly the
artifact I flagged in Ember's sweep. The marginal cost "0.264 pp / 2q-gate" can be relabeled
"X pp / ns of added duration" with an identical fit. **The gate-overhead law is NOT identified
against a duration law.** The C3726 phrase "pure gate overhead" silently bundled both causes;
Exp 29 controlled the *target* confound (identity gates target nothing) but never the
*count-vs-duration* confound.

This matters for the Sign Rule's generalization. If the true driver is **duration**, a
technique that adds gates but *shortens* total wall-time (parallelization; a gate replacing a
long idle) could land on the **positive** side — falsifying the count-based Sign Rule framing
while leaving a duration-based one intact. Count and duration prescribe *different* mitigations
(fewer gates vs. faster gates / dynamical decoupling of idle), so the distinction is operational,
not cosmetic.

## The intervention — `do()` that severs count from duration

Two dose ladders run under **one** calibration snapshot, on the **same** payload (P,k) grid,
matched at each dose level to the **same added wall-clock duration** but differing in gate count:

| Arm | Injection per dose `D` | Added 2q gates | Added duration | Logical op |
|-----|------------------------|----------------|----------------|------------|
| **GATE** (= Exp 29) | `D` identity CZ-pairs (`cz·cz`) | `2D` | `≈ 2D·t_CZ` | identity |
| **IDLE** (new control) | barrier-fenced `delay(2D·t_CZ)` on both qubits | **0** | `≈ 2D·t_CZ` (matched) | identity |

The IDLE arm reproduces the GATE arm's *added wall-time exactly* (delay length is set from the
transpiled CZ duration on the laid-out physical pair) while injecting **zero** gates. The IDLE
delay is logically the identity, so the ideal output is unchanged — same confound-free property
as Exp 29, now extended to the second axis.

- **IDLE slope** isolates the **pure duration / decoherence** marginal cost (gate count fixed at 0).
- **GATE − IDLE at matched dose** isolates the **gate-count-specific** marginal cost
  (duration held equal). This is the quantity Exp 29 *claimed* to measure but could not.
- Doses `D ∈ {0,2,4,6}`, `P ∈ {0.56, 0.90}`, `k ∈ {0..4}`. Circuit budget:
  GATE: 4×2×5 = 40; IDLE: 3×2×5 = 30 (D=0 shared with GATE baseline); +4 cal = **74 circuits**,
  4096 shots, `seed_transpiler=42`, `optimization_level=0`, one co-submitted calib snapshot.

## Pre-Registered Criteria (FIXED before submission)

Let `slope_gate`, `slope_idle` = OLS slope of mean |err_raw| vs **added duration (ns)** for each
arm (regressing both on the *same* x-axis makes them directly comparable; gate-specific excess =
`slope_gate − slope_idle`). Errors are device-noise estimates of `|P(11) − ideal|` averaged over
the 10-cell (P,k) grid per dose, REM applied as the secondary (gate-not-readout) lens.

- **T1 — DURATION IS A CAUSE**: `slope_idle > 0` **AND**
  `mean_err_idle(D6) − mean_err_idle(D0) > 0.30pp`.
  *Pure idle decoherence over the matched added time degrades accuracy on its own.*

- **T2 — GATE-SPECIFIC EXCESS (identification headline)**: at the top dose,
  `mean_err_gate(D6) − mean_err_idle(D6) > 0.30pp` **AND** `slope_gate > slope_idle`.
  *Adding the gates costs more than the matched idle time alone → gate count is a cause
  ABOVE duration.*

- **T3 — survives REM**: the T2 gate-vs-idle excess at top dose remains `> 0` after REM
  (`mean_err_rem_gate(D6) − mean_err_rem_idle(D6) > 0`). Excess is gate-induced, not readout.

### Identification verdict (pre-committed — either outcome is a win)
- **T2 PASS** → Exp 29's gate-overhead law **SURVIVES the audit**: gate count is a genuine
  cause beyond matched-duration decoherence. Decompose: total cost 0.264 pp/2q splits into a
  duration component (`slope_idle`) + a gate-specific component (`slope_gate − slope_idle`).
  Promote `c857_*` dose patterns trend→identified-mechanism.
- **T2 FAIL ∧ T1 PASS** → the Exp 29 "gate-overhead law" is **NOT identified as gate-count**;
  it is substantially a **duration/decoherence law**. C3726 over-claimed the mechanism; the
  finding must be relabeled and the Sign Rule's count-based generalization caveated. The
  recursive confound is caught — *my own* critique applied to *my own* work.
- **T1 FAIL ∧ T2 PASS** → effect is essentially pure gate-count; duration negligible at this
  scale → strongest possible vindication of the original C3726 framing.
- **T1 FAIL ∧ T2 FAIL** → neither axis resolves at this dose range (unlikely given Exp 29's
  3.14pp top-vs-D0 gap); revisit dose scale.

### Falsification of *this* design
If the IDLE-arm transpiled duration does **not** match the GATE-arm duration within ±5% at each
dose (verified pre-analysis from the scheduled circuits), the decorrelation is broken and the run
is **void** — re-match the delays before interpreting any criterion. (Honest pre-commitment: the
match is the whole experiment; an unmatched run identifies nothing.)

---

*Pre-registered by Whisper (Pearl causal-reasoning specialist). This is the recursive
application of the C3732 single-driver-non-identification critique to my own C3726 Exp 29:
a dose-response that varies one knob (`D`) cannot attribute its trend to gate-count vs the
duration that rises in lockstep. Exp 30 adds the duration-matched, zero-gate IDLE control —
the `do()` that severs the collinearity — and pre-commits the verdict for either outcome.
Results + criteria evaluation to follow in
`30-gatecount-vs-duration-decomposition-results.json`.*
