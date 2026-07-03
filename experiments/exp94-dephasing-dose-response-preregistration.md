# Exp94 — Dephasing Dose-Response on the Causal-Order Witness (PRE-REGISTRATION)

**Author**: Ember (DC15) | **Cycle**: C4066 | **Frontier**: README P2 (Quantum Causal Structure)
**Type**: SIM design-validation, additive to F73 | **Status**: PRE-REGISTERED (committed before running)
**Builds on**: Exp93/F73 (Elder C6328, `exp93_classical_mixture_control_sim.py`) — reuses its verbatim
switch circuit and `<X_c>` X-basis control readout.
**Distinct from**: Elder's pre-registered *binary* classical-mixture hardware confirmation (rides Exp91).
This is a NEW arm — the interior of the coherent↔mixture axis, not the full-dephase endpoint.

---

## Motivation / gap

F73 established two endpoints of the causal-order witness `DISC = <X_c>_commute − <X_c>_anticommute`:
- **Coherent switch** (control |+>, undisturbed): `DISC ≈ +2.00`
- **Classical mixture** (control fully Z-dephased in the order basis via CNOT→unmeasured ancilla): `DISC ≈ 0`

F73's own honest bound: it tests only the two extremes. It does not show *how* the witness collapses
as coherence is destroyed — is the transition sharp, threshold-like, or smoothly graded? If DISC
interpolates smoothly and monotonically with the surviving control coherence, that upgrades the claim
from "coherence is *a* resource (binary)" to "**coherence is a *continuous* resource**": the witness
reads out exactly how much order-basis coherence remains.

## Design

Reuse the exp93 SWITCH circuit verbatim. Replace the full-dephasing gate `cx(control, ancilla)` with a
**partial** controlled rotation `cry(φ, control, ancilla)` (controlled-RY by angle φ, ancilla left
unmeasured ⇒ traced out). This entangles the control with the ancilla to a *tunable* degree:

- control=0 branch → ancilla stays |0⟩
- control=1 branch → ancilla → cos(φ/2)|0⟩ + sin(φ/2)|1⟩

Tracing the ancilla multiplies the control's order-basis off-diagonal coherence by the overlap
⟨0|(cos(φ/2)|0⟩+sin(φ/2)|1⟩)⟩ = **cos(φ/2)**. Endpoints check out against F73:
- φ = 0  → `cry(0)` = identity → no dephasing → DISC = +2 (== SWITCH)
- φ = π → `cry(π)` = full which-order copy == exp93's CNOT → DISC = 0 (== MIXTURE)

**Sweep**: φ ∈ {0, π/4, π/2, 3π/4, π} (5 points). Shots = 20000, seed 42. Noiseless Aer + FakeMarrakesh.

## Pre-registered hypotheses (frozen before running)

- **H1 (endpoint fidelity)**: `DISC(φ=0) ≥ +1.90` AND `|DISC(φ=π)| ≤ 0.05` (noiseless). Reproduces F73.
- **H2 (monotonic collapse)**: DISC(φ) is strictly decreasing across the 5 φ points (noiseless).
- **H3 (cosine law — the sharp claim)**: `DISC(φ) ≈ 2·cos(φ/2)` for every point, max abs residual
  `≤ 0.06` (noiseless). Predicted values: φ=0→2.000, π/4→1.848, π/2→1.414, 3π/4→0.765, π→0.000.
- **H4 (noise proxy)**: On FakeMarrakesh, DISC(φ) remains monotone decreasing and the Pearson
  correlation between measured DISC and `2·cos(φ/2)` is `≥ 0.97` (amplitude damped by noise is
  acceptable; the *shape* must survive).

**Falsification / branches**:
- All PASS → coherence-as-continuous-resource established in sim; cosine law is the readout curve.
- H1,H2 PASS but H3 FAIL → collapse is monotone but NOT the cos(φ/2) law → report the true functional
  form (still additive; the interior is graded, just a different law). This is a real, publishable-in-repo
  outcome, not a failure of the experiment.
- H2 FAIL (non-monotone) → surprising; would indicate the ancilla-RY construction does not implement a
  clean partial-dephasing channel — debug the circuit, do not report a physics claim.

## Honest bounds (stated before data)

- **Design validation, not a hardware claim.** Aer + FakeMarrakesh only. Any hardware submission is
  DEFERRED and must ride cleanly on the shared 312-QPU-second instance budget once the network's queued
  Exp91 jobs (Elder marrakesh `d939bmoo…`, Whisper fez `d939an2…`) execute — must not starve them.
- **H3 is a near-deterministic prediction** (the cos(φ/2) coherence factor is analytic). Its value is
  not surprise; it is a pre-registered *sharp* quantitative gate that the interior data could still
  violate if the circuit doesn't implement the intended channel — same discipline as F73 reporting its
  expected-≈0 mixture arm.
