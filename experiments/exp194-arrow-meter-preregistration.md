# Exp194 Pre-registration — THE ARROW METER: how much of the past can be rewound?

**Cycle**: C4886 · **Backend**: ibm_fez · **Shots**: 8000 × 9 · Creator go: "fly the 3".
**Class**: the composition arc's toolkit turned into a thermodynamic instrument.

## The question
Decoherence splits into a **recoverable** share (coherent/quasi-static — the echo rewinds it)
and an **irreversible** remainder — the part of the past no operation gets back. Measure both
vs time: C(T) = ⟨X⟩ of |+⟩ after idle T, echoed (quarter-point pairs) and raw.
**A(T) = 1 − C_echo(T)** = the irreversibility fraction (the arrow, at the echo's reach);
**R(T) = (C_echo − C_raw)/(1 − C_raw)** = the rewindable share of what was lost.
The arrow-of-time statement: A grows and R falls with timescale — the longer you wait, the
smaller the fraction of the past that can be rewound.

## Circuits (9): {echo, raw} × T ∈ {1, 2, 4, 8 μs} + T0 reference. Two qubits per circuit
(independent, averaged); X-basis prep/readout.

## Criteria (formulas; se_C ≈ 1/√16000 ≈ 0.008)
- **Primary**: A(T) strictly increasing across all three steps (each step ≥ 2σ) AND R(T)
  non-increasing on ≥ 2 of 3 steps. Bands (priced from recent condition data): A(1μs)
  0.01–0.08 · A(2μs) 0.02–0.12 · A(4μs) 0.06–0.25 · A(8μs) 0.15–0.45. R(1μs) 0.45–0.90.
- **Reported deliverable**: τ_arrow — the interpolated time where A crosses ½ (extrapolated if
  outside the sweep, labeled).
- **Gauge**: C(T0) ≥ 0.97 (prep/readout floor).
## Fences
This measures THIS device-environment's arrow (decoherence irreversibility at the single-X-echo
reach), not cosmology; deeper echo ladders (XY4/CPMG) would shift the split point — the
instrument is defined BY its rewind protocol, stated openly. Selftest: noiseless A = 0, R
undefined-clean, C = 1 everywhere.
