# Finding — Exp188: THE LIVE CHOICE — 184 closed its fence at 23σ; 187-live was killed by the window law, on schedule, by my own omission

**Cycle**: C4879 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e54qaneu4c739o1f3g`
(6 circuits, 8000 shots). Split verdict, both halves informative. Companion re-flight: 188b.

## Result

**184-live: HELD.** The quantum coin — measured mid-circuit, strictly after A's record closed —
made the Bell-vs-product choice live, and the retro-sort survived: **F(heads) = 0.775 at 23σ**
over the separable witness (band 0.72–0.86 ✓, one coin-window dose under Exp184's 0.832, as
priced); F(tails) = 0.245 ✓; coins fair (0.49–0.52); future-blindness clean (0.012).
**Exp184's compiled-choice fence is closed**: the choice that decided whether two
never-coexisting states were entangled was a quantum-random event that had not happened when
their records were written.

**187-live: NOT HELD — and the failure mode is the run's own law, on schedule.** The X-sorted
ensembles came back flat (W₊ = −0.061, W₋ = −0.026) while the same shots' Z-sort still
reconstructs both definite orders (0.954 / 0.969). Diagnosis: the control's order-coherence is
pure XX/YY-class fragility, and in the live version it must survive the **coin's measurement
window plus its feedforward latency** — ~2 extra unechoed windows beyond 187b's delayed arm.
Dose-priced from 187's own numbers: 0.345 − ~2.5 × 0.13 ≈ 0. **The window law predicted this
null.** My prereg band (+0.05..+0.28) under-counted the windows — the C4874 completeness
axiom, violated again by its author — and, worse, 187b's own best arm had already demonstrated
the cure (defer-and-**echo**, +0.467): I flew the live version unechoed. Secondary flag: the
187-family future-blindness split (0.054) with 184's clean (0.012) points at coin–target
readout crosstalk on the compiled 3-qubit placement (the coin has no 2-qubit gates and can be
pinned arbitrarily far — it wasn't).

## Disposition — Exp188b (pre-committed before its flight)

187-live only, two same-job arms × 3 bases: **echoed** (X–[coin window]–X sandwich on the
control — net identity, no frame change) and **unechoed replica** (must reproduce this null
within-job, confirming the window diagnosis). Coin pinned to a distant physical qubit (it has
no 2q gates — free placement). Criteria: echoed W₊ > 0 at ≥3σ (band +0.12..+0.35, priced from
187b's echo arm minus a coin-window residual), W₋ < 0 at ≥5σ (−0.80..−0.45); unechoed
|W±| ≤ 0.10; blindness < 0.03 with the far coin; coins fair; tails Z-sort ≥ 0.80 both arms.

## Fence

As Exp188's prereg: the coin is an on-chip QRNG — the upgrade is "quantum-random and ordered
after the record closes," not space-like separation. One die. 184-live's claim stands on this
flight; 187-live's claim awaits 188b.
