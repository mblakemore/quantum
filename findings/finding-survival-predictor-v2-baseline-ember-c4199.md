# The survival predictor's "structured protection" was a borrowed-baseline artifact (Ember, C4199)

**Creator directive:** *"fly the two-term predictor"* — the 0-QPU upgrade flagged in the C4196 frontier
doc: fit a two-term model (generic decay × structured-protection factor) on the DTC data, turning
Exp151b's *favorable* scope-limit into a standing instrument. **The fit killed the premise.** There is
no protection term to add — the apparent protection was the generic model using a baseline error rate
**borrowed from the wrong qubits**. The real, better upgrade is per-qubit baselining.

---

## What I set out to fit, and what the data said

The v1 predictor used one hard-coded `E_CX = 0.0106` for every circuit. Fitting
`A_hw = A_ideal · (1−E_CX)^n2q · exp(β·n2q)` on the Exp151b DTC amplitudes gave a clean
`β = 0.0077/gate` — a 3.6× "structured-protection factor," reproducing the C4196 twin-finding's
"interactions beat generic decay by ~2.9×." It even had believable curvature.

**Then the advisor flagged the arithmetic coincidence:** `(1−0.003)/(1−0.0106) = 1.00768`, whose log
is 0.00765/gate — my entire β to three sig figs. β could be "protection," or it could be a DTC chain
on **better qubits than the reader**, divided by a baseline that never belonged to it. `E_CX = 0.0106`
was validated on the Exp148b *reader* qubits — a different circuit, different physical qubits,
different calibration epoch — and then applied to the L=6 DTC chain it was never measured on.

## The discriminating check (0 QPU) — decisive

I pulled the mean CZ error on the **actual** qubits job `d9di5mkjeosc73fhkf6g` ran on
(123,124,125,136,140–143) from backend properties:

| quantity | value |
|---|---|
| **measured CZ on the actual DTC qubits** | **0.00209** (median 0.00199) |
| borrowed reader baseline (v1) | 0.0106 (≈5× too high) |
| two-param fit `A_hw/A_ideal = B·(1−E_eff)^n2q`, **E_eff** | **0.00214** |
| SPAM/front-end offset **B** | 0.934 |
| **E_eff / measured CZ** | **≈ 0.99 — the observable decays at ≈ the bare gate-error rate** |
| protection vs the **correct** baseline | **≈ 1× — no evidence of the large protection claimed** |
| protection vs the **borrowed** baseline | 0.36× (the 2.9× artifact) |

n2q = 10/period confirmed against the transpiled circuit (5 edges × 2 CZ/bond × 12 periods = 120).
The SPAM offset B=0.934 also explains the front-end drop (0.996→0.885 in one period) I'd mistaken for
super-exponential protection — it's readout/prep, not dynamics.

**Verdict: no evidence of structured protection.** The DTC subharmonic observable decays at ≈ the CZ
error rate of the qubits it ran on; the "interactions protect ~2.9× over generic" claim (Exp151b
secondary / C4196 twin-finding) was a **baseline-mismatch confound** — good qubits scored against a
borrowed worse-qubit rate. *Honesty caveat (the same C4198 discipline this finding stores as a
pattern):* I put no error bar on E_eff (the 0.062 backtest residual says it is non-trivial), and a
*purely* generic observable should decay slightly **faster** than the bare 2q rate once 1q rotations
(~12/period), idle, and readout are budgeted on top of the 10 CZ. So E_eff ≈ E_CX is not proof of
*exactly* zero protection — a small real effect could hide within fit + error-budget uncertainty. The
airtight claim is the falsification: **the 2.9× was a borrowed-baseline artifact; against the correct
per-qubit baseline any residual protection is small and unresolved, not the large factor originally
claimed.**

## What this corrects, and what still stands

- **Corrected:** the C4196 twin-finding's *secondary* claim that structured Ising interactions confer
  ~2.9× noise protection over generic decay. They do not; that number was `0.0106/0.0021`.
- **Untouched:** Exp151b's *primary* result — disorder adds **no differential** protection over
  interactions (P_hw/P_ideal ≈ 1.00). That is a DTC/MATCH ratio on the **same** qubits, so the baseline
  cancels exactly. Ratios were safe; the "vs generic" absolute comparison was not.
- **Untouched:** the genuine G1 blind spot — the model cannot predict a coherent sign inversion
  (Exp148 copy arm; Exp149b showed it isn't purely coherent either). That remains echo/leakage
  territory, not this gate's.

## The actual upgrade (v2)

Not "generic × protection." The honest, better model is: **use the per-qubit mean CZ error of the
qubits the circuit ran on, not a global constant.**

- `E_CX` is now a **required per-qubit input**; `measured_cz(job_id)` pulls it from backend properties.
- Backtest on the DTC amplitude: max|err| **0.266 (borrowed v1) → 0.094 (per-qubit) → 0.062 (+SPAM B)**.
- The "favorable structured-protection" scope-limit is **removed** (it wasn't real). One genuine
  blind spot remains (G1, coherent inversion). A predictor with one fewer false scope-limit is a
  better instrument.

## The lesson (third recurrence)

This is the C4196 match-the-axis discipline again, in a new disguise: **a decay baseline must be
measured on the same qubits the circuit ran on.** C4196 matched the control on scheduled *duration*;
C4198 chose the *estimator* before the gate; here, match the *baseline* to the *qubits*. Each time, a
borrowed/biased reference invented a physics story (overhead-as-coherence, estimator-bias-as-idle-cost,
better-qubits-as-protection) that dissolved once the reference was matched to the thing measured.
Forward prediction: structured-circuit observables will keep decaying at their qubits' gate-error rate;
future flights test v2 by comparing E_eff to the job's measured CZ.

**Numbering:** predictor upgrade (v2), 0 QPU; supersedes v1. Corrects the C4196 twin-finding secondary
claim; resolves the "two-term predictor" item in the frontier doc (as a falsification of its premise).
