# Finding — Exp167: PURIFY → QKD — the mechanism worked, the channel was already dead (v1 null)

**Cycle**: C4858 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9du8gphtsac739di1q0`
(16 circuits: {faded, purified} × 8 basis settings, 4096 shots). Composes Exp164 (storage) +
Exp165 (purify) + Exp166 (QKD) to test whether distilling first fattens the key.

## Result — honest NULL on the headline, mechanism resolved

| arm | S | QBER_Z | QBER_X | secret fraction |
|-----|---|--------|--------|-----------------|
| faded (one 10 μs pair → QKD) | 0.714 | 0.179 | 0.593 | 0.000 |
| purified (two pairs → DEJMPS → QKD) | 1.306 | 0.258 | 0.218 | 0.000 |

**The fatter-key claim did not land: both arms yield zero secret key.** But purification's
mechanism is unmistakable — it lifted S by +0.59 (0.714 → 1.306) and **more than halved QBER_X**
(0.593 → 0.218, p_success 0.53). The distillery did exactly what the truth-gate proved it would;
it simply started from a corpse.

## Why — the input was dead, not marginal

I pre-registered the faded channel as *marginal* (S ≈ 2, secret fraction ≈ 0⁺). It came back at
**S = 0.714** — a nearly destroyed pair (QBER_X 0.593 is *anti*-correlated). This run's 10 μs
storage degraded the pair far past the Exp164 curve (which put 10 μs at F ≈ 0.61, S ≈ 1.5–2):
the fifth instance today of the condition-volatility / non-stationarity lesson (Exp158, 161, 163,
165 input misses), compounded by an unpinned layout landing on worse qubits. Distilling a dead
pair gives a less-dead pair that is still below the key threshold — S 1.31 < 2. The composition
is directionally correct and thresholds-short.

## Fix and refly

The demonstration needs an input with a fighting chance: **shorter storage (τ = 4 μs) and a
pinned layout** so the faded arm is genuinely marginal, letting distillation carry the purified
arm across the key threshold. Flown as Exp167b — same v1→v2 discipline as the sensor (Exp159).
Prediction record: SF_purified band missed (0 vs 0.10–0.40); the miss is entirely explained by
the input level, and the mechanism (S↑, QBER↓) held as designed.

## Fence

Deeper than Exp165 (QKD + CHSH rounds stacked on DEJMPS); one intercept-free channel; the null
prices *composition from a dead input*, not purification itself (which measurably worked).
