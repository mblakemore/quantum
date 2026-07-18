# Finding — Exp163: REPEATER WITH MEMORY — the hold time of a certified match

**Cycle**: C4853 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dtf1aneu4c739nnq20`
(42 circuits: {swap, direct-Bell} × 7 storage delays × 3 settings, 4096 shots, physical qubits
pinned to [127, 137, 147, 146] so both pedigrees age on identical hardware).

## Results

Entanglement-swap A–C (Exp162), then hold the pair for τ before the witness reads it:

| τ (μs) | 0 | 5 | 10 | 20 | 40 | 80 | 160 |
|--------|---|---|----|----|----|----|-----|
| F swap | 0.816 | 0.688 | 0.502 | 0.326 | 0.415 | 0.373 | 0.381 |
| F direct | 0.928 | 0.789 | 0.622 | 0.404 | 0.423 | 0.365 | 0.428 |

1. **Certified hold time: t₅₀ ≈ 12 μs** (swap arm; witness 27σ at τ=0; the F=1/2 crossing is
   data-visible between τ=10 and 20 μs, fit-independent). Direct-Bell holds ~19 μs.
2. **Pedigree test: ratio T_ent(swap)/T_ent(direct) = 0.76 — in the pre-registered same-physics
   band [0.7, 1.4].** Swapped entanglement ages like gate-made entanglement: decay is local
   physics, not pedigree. The repeater's product is not second-class entanglement.
3. **The model was too simple, said so by the data**: the fit assumed F → 0.25, but long-τ points
   flatten near ~0.4 — under dephasing the ⟨ZZ⟩ correlation survives (it decays via T1 only), so
   the true floor is ≈ (1+ZZ)/4 — and the tail is non-monotonic (0.33 → 0.42), the pre-named
   detuning-oscillation risk showing in XX/YY. T_ent = 14/19 μs is a first-order summary of the
   fast coherent-part decay; t₅₀ is robust to all of this.

## Prediction record

T_ent band (40–160 μs) missed high — storage-idle without any echo decays the pair at roughly the
sum of local dephasing rates plus quasi-static detuning, far faster than nominal single-qubit T2
suggests (4th magnitude miss of the day; witness, pedigree, and risk-naming all held; calibration
82.4%). The natural follow-up — **a storage echo** (Hahn pulses during the delay, the textbook
quantum-memory move) — is a *different condition* from the closed feedforward-DD chapter: long
idle is quasi-static-dominant, exactly where echoes work. Queued for a Creator go, not flown.

## Fence

Idle storage on one die: no re-cooling, no QEC, no independent sources. A hold-time measurement
of the repeater primitive with the witness as the clock — not a deployed repeater. Network wing
now: hop, chain, swap, **and how long the swap keeps** (12 μs raw).
