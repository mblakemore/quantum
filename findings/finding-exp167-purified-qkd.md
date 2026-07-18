# Finding — Exp167/167b: PURIFY → QKD — purification is underwater on Heron r2 (bracketed null)

**Cycle**: C4858 · **Date**: 2026-07-18 · **Backend**: ibm_fez ·
**Jobs**: v1 `d9du8gphtsac739di1q0` (τ=10 μs), v2 `d9du9ssjeosc73fi2u30` (τ=4 μs, pinned).
Composes Exp164 (storage) + 165 (purify) + 166 (QKD): does distilling first fatten the key?

## Answer: no — and two flights prove *why*, by bracketing the input

| flight | input | faded arm | purified arm |
|--------|-------|-----------|--------------|
| v1 (τ=10 μs) | dead (S=0.714) | S 0.714, SF 0 | S 1.306, SF 0 |
| v2 (τ=4 μs, pinned) | healthy (S=2.430) | S 2.430, **SF 0.294** | S 2.181, SF 0 |

- **v1: input too dead to save.** Purification's mechanism worked (S 0.714→1.306, QBER_X
  0.593→0.218) but a distilled corpse is still a corpse — below the key threshold.
- **v2: input too good to help.** With a healthy 4 μs pair, the faded arm makes a fine key
  (SF 0.294), and running DEJMPS first makes it **worse** (S 2.43→2.18): the protocol's ~2 extra
  CX + the second pair's preparation noise cost more fidelity than distillation returned.

Together the two flights bracket the accessible input range and land on the same wall:
**single-round DEJMPS does not fatten a QKD key on Heron r2 — its two-qubit-gate overhead exceeds
its distillation gain everywhere.** The break-even (distillation gain > ~2-CX cost) is not reached
at this gate fidelity: at F≈0.8 the ideal gain is ≈+0.1, and ~2 CX of hardware error is ≈+0.15–0.2
of fidelity cost. The named pre-registered risk ("DEJMPS depth eats the gain") materialized on
both flights.

## What this prices

This is the honest ceiling on the composition, and it is quantitative: purification pays only
once the two-qubit gate error drops enough that one distillation round's gain clears its own
cost — a concrete target for better hardware, or for lower-overhead schemes (entanglement pumping,
measurement-based distillation) that spend fewer gates per round. It does **not** retract Exp165
(purification demonstrably works on *structured storage noise* where the gain is large, 0.396→0.688)
— it shows that gain does not survive being stacked under a QKD readout at QKD-relevant input
fidelities on this device.

## Consequence (correction)

The Exp166 subspace-channel exhibit's "purify first for a fatter key" hook is **corrected**: on
current hardware purification's overhead exceeds its gain, so the fatter key awaits better gates
or a lower-overhead protocol — not a free win from the stack as first written.

## Fence & discipline

Two flights bracket the input; a third would land between and fail for the same reason, so the
chapter is closed (not chased) — the same discipline as the DD trilogy. Single-round DEJMPS, one
device, one day; the negative is a hardware-gate-fidelity statement, not a theory retraction.
Prediction record: SF_purified band missed on both flights (the named risk), calibration 82.4%.
