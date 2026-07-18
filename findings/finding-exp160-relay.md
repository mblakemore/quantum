# Finding — Exp160: TELEPORT RELAY — two hops, end-to-end quantum, and the cost that doesn't compose

**Cycle**: C4849 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dsrnsinv1c73apgi7g`
(24 circuits: 4 within-job arms × 6 cardinal states, 4096 shots). Second piece of the
quantum-network wing (Exp154 = single hop). Creator directive: fly the teleport second hop.

## The result — the state crossed two hops

q0 → (Bell 1, feedforward) → q2 → (Bell 2, feedforward) → q4, verified end-to-end against the
known input. Two mid-circuit Bell measurements, two real correction stages in sequence; the
receiver of hop 1 becomes the sender of hop 2.

| state | chain | single (same job) | noent2 | nocorr2 |
|-------|-------|-------------------|--------|---------|
| Z+ | 0.906 | 0.966 | 0.951 | 0.524 |
| Z− | 0.899 | 0.960 | 0.955 | 0.460 |
| X± | 0.725/0.732 | 0.927/0.927 | 0.514/0.524 | 0.524/0.470 |
| Y± | 0.716/0.726 | 0.912/0.926 | 0.507/0.503 | 0.492/0.525 |
| **avg** | **0.784** | **0.936** | — | 0.499 |

**Chain 0.784 vs the 2/3 end-to-end classical bound: margin +0.117, ~45σ.** Hop-2 falsifiers
both collapse to chance (no-entanglement: superpositions 0.512; no-correction: all six, 0.499) —
the relay's own resource and feedforward are each load-bearing, independent of hop 1's
(established in Exp154). Genuine quantum relay on silicon.

## The honest miss — and what the composition check caught

Pre-registered band 0.855–0.92: **MISSED** (0.784). The check built for exactly this: squaring
the *same-job* single hop's process fidelity predicts 0.879 for the chain — the measured chain
runs **0.095 below composition**. Teleportation hops do not compose multiplicatively here, and
the structure says why:

- Excess loss is **superposition-concentrated**: chain X/Y ≈ 0.72 (deficit ~0.20 vs single) while
  chain Z ≈ 0.90 (deficit ~0.06) — yet the same-job single hop is near-uniform (0.92 vs 0.96).
- The chain's final receiver idles through **two** feedforward windows (and q2 through one plus
  its own re-use). Consistent with idle-window dephasing scaling superlinearly in windows —
  the Exp154/158 error class re-emerging in the condition that doubles the window, on a day when
  the single-window gap was invisible (Exp158: 0.936 near-uniform).

This closes the day's loop on non-stationarity with a sharper statement: the idle-dephasing gap
is **condition-dependent, not just day-dependent** — invisible at one window today, ~0.17 at two.
Per the C4847 condition-first rule, the properly-triggered DD test is now armed: **DD on the
relay's end receiver**, where the gap is observed in-job (not on a calendar, not on a hunch).

## Fence

Two hops on one die with zero storage time — a relay **primitive** (sequential teleportation),
not a repeater: no entanglement swapping, no purification, no quantum memory. The 0.095
composition shortfall is attributed to extended feedforward idle by the Z-vs-X/Y structure —
*consistent with*, not proven; the armed DD-on-relay test is the discriminator. Prediction
record: primary gate and falsifiers all held; magnitude band missed low with the named risk
materialized (the check designed to expose it did).
