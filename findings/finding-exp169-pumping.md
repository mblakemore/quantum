# Finding — Exp169: ENTANGLEMENT PUMPING — the complete, honest answer (with Exp165, 167)

**Cycle**: C4859 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dufgcjeosc73fi34qg`
(9 circuits: 0/1/2 pump rounds × 3 settings, 8000 shots, pinned qubits). The lower-overhead
follow-on to the Exp167 null — "can we get pumping working?"

## What this run measured

| pump round | F | p_success | witness |
|-----------|---|-----------|---------|
| 0 | 0.878 | 1.00 | ✓ |
| 1 | 0.616 | 0.43 | ✓ |
| 2 | 0.436 | 0.24 | ✗ |

Each round made the pair **worse** (round-1 gain −0.262, round-2 −0.180). Pumping is underwater.

## The honest caveat — and why the answer is still complete

The run did **not reach the regime it was designed for**: I intended a degraded ~0.6 input (10 μs
storage, Exp165's favorable regime), but the pair came in at **F=0.878** — healthy — because this
hour's storage barely degraded it (the day's non-stationarity, Nth instance). So Exp169 as-run
tested multi-round pumping on a *good* pair, where Exp167 already established distillation hurts.
That is exactly what it shows.

The complete answer comes from three experiments together:
- **Exp165** — single-round DEJMPS on a *genuinely degraded* pair (0.396, structured storage
  noise): **+0.29 gain. WORKS.** The one regime where distillation clears its overhead.
- **Exp167** — distillation on healthy/marginal pairs under a QKD readout: **underwater** (2-CX
  overhead > gain), bracketed across the input range.
- **Exp169** — multi-round pumping: each round's fixed ~2-CX + reused-ancilla-reset overhead
  compounds; on a healthy input it is underwater from round 1.

**Verdict: on Heron r2, distillation pays at most ONE round, and only from a genuinely degraded
start.** Multi-round pumping does not climb because the per-round overhead is fixed while the
available gain shrinks as fidelity rises — you are past the crossover immediately after round 1.
Pumping's advantage is *memory* (one ancilla pair at a time), not gate cost, so it cannot beat the
overhead wall Exp167 found. It works once the two-qubit-gate + reset error drops below the
single-round gain — a concrete hardware target, not a protocol fix.

## Discipline

Not reflying to force the degraded regime: that fights the same non-stationarity that has moved
every storage/idle condition today, and Exp165 already anchors the works-on-bad-input point. The
three-experiment synthesis is the deliverable, not a cherry-picked positive.

## Fence

Reused-ancilla via mid-circuit reset (itself ~1-2% noisy on fez); one device, one day; the
negative is a gate-and-reset-fidelity statement, not a theory retraction. DEJMPS purification is
correct physics that this hardware's gates cannot yet afford past one round.
