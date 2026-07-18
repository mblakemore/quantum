# Finding — Exp164: STORAGE ECHO — the repeater's memory, doubled

**Cycle**: C4854 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dtmbcinv1c73aphifg`
(63 circuits: {plain, Hahn, CPMG-2} × 7 delays × 3 settings, 4096 shots, qubits pinned to
Exp163's [127, 137, 147, 146]; plain arm re-baselined in-job, condition-first).

## Result — pre-registration held on every gate

The echo exploits an exact identity: |Φ+⟩ is a +1 eigenstate of X⊗X, so a simultaneous X on
both stored qubits refocuses each one's quasi-static detuning while leaving the state invariant
(verified exact in the noiseless truth-gate).

| τ (μs) | 0 | 5 | 10 | 20 | 40 | 80 | 160 | t₅₀ | T_ent |
|--------|---|---|----|----|----|----|-----|-----|-------|
| plain | 0.834 | 0.748 | 0.608 | 0.420 | 0.384 | 0.378 | 0.370 | **16 μs** | 22 μs |
| Hahn | 0.830 | 0.771 | 0.697 | 0.615 | 0.475 | 0.359 | 0.307 | **36 μs** | 46 μs |
| CPMG-2 | 0.834 | 0.773 | 0.700 | 0.607 | 0.485 | 0.341 | 0.305 | **38 μs** | 44 μs |

- **Certified hold time 16 → 36 μs: a 2.3× memory extension** (T-ratio 2.07, gate > 1.5).
- **CPMG-2 ≈ Hahn**: a second echo adds nothing — the refocusable noise is captured by one π,
  locating the dephasing spectral knee below ~1/40 μs. Quasi-static dominance confirmed.
- Plain re-baseline (16 μs) consistent with Exp163 (12 μs) within the day's drift; the 163 tail
  wiggle did not recur this job (condition moved again — consistent with the C4850 volatility
  record; the extension result does not depend on it).
- **Tail crossover reported honestly**: at 160 μs the echoed arms (0.31) fall below plain (0.37)
  — plain keeps its ZZ floor while echo pulse errors accumulate; the echo wins where memory is
  usable (τ ≲ 80 μs), not asymptotically.

## Why this matters for the wing

The feedforward-DD chapter closed null (3 tests) because *those* windows carry fast or
measurement-induced noise. Storage is the opposite regime — long idle, quasi-static-dominant —
and the echo delivers exactly there. One lesson, two conditions, opposite verdicts, both
pre-registered: **know your noise spectrum before choosing your medicine.**
Prediction record: second consecutive full band-hold (calibration 82.4% and honest).

## Fence

Same die, no re-cooling, no QEC; echo assumes Φ+ (state-specific invariance — a general memory
would Pauli-frame-track). Hold-time numbers are (device, day, qubit-set) figures, not constants.
