# Finding — Exp162: ENTANGLEMENT SWAPPING — entangling two qubits that never met

**Cycle**: C4851 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dt50ineu4c739nndeg`
(12 circuits: 4 within-job arms × 3 settings, 8000 shots). Completes the quantum-network
triptych: hop (Exp154), chain (Exp160), swap (Exp162). Creator directive.

## Result

Bell(A,B1) + Bell(B2,C); Bell-measure the middles with real feedforward on C → A and C are
projected into |Φ+⟩ **without any gate ever connecting them**.

| arm | ZZ | XX | YY | F(Φ+) |
|-----|----|----|----|-------|
| **swap** | +0.864 | +0.737 | −0.741 | **0.836** |
| direct Bell (same job) | +0.972 | +0.971 | −0.972 | 0.979 |
| no-correction | −0.001 | −0.007 | −0.041 | 0.258 |
| no-Bell-measurement | +0.002 | −0.002 | −0.006 | 0.251 |

**F_swap = 0.836 vs the 1/2 separable bound: 40σ** — no separable state of A and C can exceed
1/2 overlap with a maximally entangled state, so this certifies entanglement between two qubits
with no interaction history. Falsifiers: without the feedforward the four Bell outcomes average
to the maximally mixed 0.25; without the Bell measurement A and C are simply never entangled
(0.25). Both sit exactly at the floor.

## Accounting

Swap cost (same-job): 0.979 → 0.836 (−0.143). The loss is basis-structured — ZZ 0.864 vs XX/YY
~0.74 — the feedforward-idle dephasing fingerprint on the spectator qubit A (it idles, entangled
and unechoed, through the Bell-measure + correction window), consistent with the day's error
taxonomy (Exp160/161: condition-dependent, echo-immune at current noise structure).
Prediction record: primary band held (first of the day); direct baseline came in above band
(0.979 — routing cheap) and cost correspondingly just above band (logged).

## Fence

One die, zero storage time, adjacent-patch routing — the swapping **primitive** that repeaters
are built from, not a repeater (no memory, no purification, no independent sources). Museum
exhibit queued next cycle (network wing triptych page).
