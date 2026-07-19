# Finding — Exp194: THE ARROW METER — the irreversible fraction of the past, measured vs time

**Cycle**: C4886 · **Backend**: ibm_fez · **Job**: `d9e6q6ineu4c739o3gjg` (9 circuits, 8000 shots).
The composition arc's echo toolkit turned into a thermodynamic instrument. **All criteria HELD.**

## Result

| T | C_echo | C_raw | A = irreversibility (1−C_echo) | R = rewindable share |
|---|--------|-------|--------------------------------|----------------------|
| 1 μs | 0.889 | 0.728 | 0.111 | 0.593 |
| 2 μs | 0.802 | 0.425 | 0.198 | 0.655 |
| 4 μs | 0.657 | 0.065 | 0.343 | 0.634 |
| 8 μs | 0.457 | −0.037 | **0.543** | 0.477 |

**The arrow of time, on a dial**: A(T) — the fraction of coherence the echo *cannot* rewind —
rises monotonically 0.111 → 0.198 → 0.343 → 0.543 (each step ≥ 2σ). The rewindable share R(T)
holds ~0.6 early and falls at the last step: **the longer you wait, the smaller the fraction of
the past that can be undone.** Deliverable: **τ_arrow ≈ 7.1 μs** — the timescale where half the
coherence has become irreversibly lost (interpolated within the sweep).

This grounds the composition-arc discovery (Exp177/178: decoherence splits into a coherent,
echo-recoverable share and an irreversible remainder) as a *quantitative thermodynamic
statement*: the split point moves with time, and we measured its trajectory. The engineering
law became a meter for the arrow of time.

## Ledger
A-monotonicity held (all steps up, ≥2σ). R-decline held (2 of 3 steps non-increasing —
the early rise is the raw baseline collapsing faster than echo, expected). C(T0) = 0.994 ≥ 0.97.
A-bands all held (0.111/0.198/0.343/0.543 inside their priced ranges).

## Fence
This is THIS device-environment's arrow at the single-X-echo reach — the instrument is defined
by its rewind protocol (a deeper XY4/CPMG ladder would shift the recoverable/irreversible split
and lengthen τ_arrow); not a cosmological statement. Two qubits averaged; one die; one day's
conditions. The *existence* of a rising irreversibility fraction and a finite τ_arrow are the
durable results; the numbers are condition-dependent.
