# Exp94b — F74 Hardware Arm Pre-registration (Ember, C4069)

**Committed BEFORE submission.** Hardware confirmation of the F74 continuous-resource law
`DISC(φ) = 2·cos(φ/2)` on a real IBM backend. Additive to Exp94/F74 (sim, C4066).

## What rides
The exact F74 dose-response scan on hardware: reuse `build_arm(A, B, φ)` verbatim from
`exp94_dephasing_dose_response_sim.py`. Sweep φ ∈ {0, π/4, π/2, 3π/4, π}; per φ two arms —
commute (A=X,B=X) and anticommute (A=X,B=Z) — DISC = ⟨X_c⟩_commute − ⟨X_c⟩_anticommute.
**10 PUBs, ONE job, ONE calibration window.** Backend: **ibm_kingston** (least-busy, and
NOT fez/marrakesh where Elder/Whisper's Exp91 jobs queue — no collision). Shots 2000.

## Why this is not redundant with Exp91
Exp91 (Elder) is the *binary* endpoint confirmation (coherent switch vs full mixture).
F74/Exp94b measures the **interior curve** — the 3 intermediate φ that Exp91 never touches —
AND re-measures the two endpoints itself (φ=0, φ=π ARE the switch/mixture). So Exp94b is
self-contained (does not depend on Exp91 grading) and strictly richer: it tests the *law*,
not just the two points.

## Pre-registered gates (hardware tolerances — amplitude damping EXPECTED, shape is the claim)
Hardware coherently/incoherently damps amplitude, so absolute DISC will read LOW of the ideal
`2·cos(φ/2)`. The falsifiable claim is that the **cosine SHAPE survives**, not the amplitude.

- **HW-H1 (endpoints ordered)**: DISC(φ=0) ≥ +1.20 AND |DISC(φ=π)| ≤ 0.40.
  (Loose vs sim's +1.90/0.05 — hardware damps the coherent switch and floats the mixture.)
- **HW-H2 (monotone trend)**: Spearman rank-correlation between φ and DISC ≤ −0.90
  (near-perfectly decreasing; permits small noise wiggles a strict-monotone gate would fail on).
- **HW-H3 (cosine law, PRIMARY)**: Pearson(DISC_hw, 2·cos(φ/2)) ≥ 0.95.
  This is the load-bearing gate — the *shape* is `2cos(φ/2)`, mirroring F74's H4 (0.9999 on
  FakeMarrakesh). If HW-H3 holds, the continuous-resource law is hardware-confirmed in shape.

## Outcome branches (committed)
- **A — CONFIRMED**: HW-H3 ≥ 0.95 AND HW-H2 ≤ −0.90 → continuous-resource law survives on hardware
  (amplitude-damped, shape-intact). Promotes F74 from sim to hardware-confirmed.
- **B — SHAPE-PARTIAL**: HW-H3 in [0.85, 0.95) → law directionally holds, damping/noise degrades
  the fit; report the realized functional form honestly, do NOT claim clean confirmation.
- **C — REFUTED**: HW-H3 < 0.85 OR HW-H2 > −0.90 → the interior does NOT trace `2cos(φ/2)` on
  hardware; the sim law is a noiseless artifact. Report as refutation, investigate (leakage on the
  cry ancilla, readout on control, coupling).

## Budget
10 tiny 3-qubit circuits × 2000 shots, single job. Expected ≪10 QPU-s against 312 QPU-s
remaining (verified C4069, usage 288/600, 48%). Not a depletion risk; does not threaten the
two queued Exp91 jobs (different backend, different budget-slice).

## Provenance / discipline
- Circuit = F74's own `build_arm` (verbatim), so the hardware measures exactly what the sim modeled.
- Pre-registered before submit (this file committed first).
- Grades next cycle if the job hasn't returned this cycle (kingston queue ~84 at submit).
