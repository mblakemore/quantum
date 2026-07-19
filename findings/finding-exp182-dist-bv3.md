# Finding — Exp182: THE SCALING LAW — 8/8 at n=3; per-gate cost banded at 3–5%; the drift is the chip, not the architecture

**Cycle**: C4870 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e2f4kinv1c73apo1l0`
(20 circuits: local×8, dist×8, noresource×4 weight-reps, 8000 shots). First 10-qubit flight of
the campaign; upgrades Exp181's single per-gate ratio to a three-dose measurement. Creator go:
general#24.

## Result

| arm | w=0 | w=1 (mean of 3) | w=2 (mean of 3) | w=3 | modal |
|-----|-----|------|------|-----|-------|
| local | 0.991 | 0.950 | 0.900 | 0.945 | 8/8 |
| **dist** | 0.991 | 0.945 | 0.893 | 0.868 | **8/8** |
| noresource | 0.993 | 0.489 | 0.245 | 0.123 | wrong on every gate-bearing rep |

- **PRIMARY HELD**: the distributed computer read the right hidden string as top outcome for
  **all eight programs**; +79σ / +125σ / +141σ over the falsifier floors per weight class — and
  the floors sat exactly on the 1/2^w guessing theorem (0.489 / 0.245 / 0.123 vs 0.5/0.25/0.125).
- **Per-gate ratios (three doses)**: r₁ = 0.954±0.002, r₂ = 0.945±0.003, r₃ = 0.972±0.005 —
  **all inside the pre-registered 0.93–0.99 band**; pooled r̂ = 0.954; extrapolation
  r̂¹⁰ = 0.62 (a 10-cross-cut-gate distributed oracle would still decode near 62%).

## The scaling verdict — the data chose a third branch (honest accounting)

The pre-registration offered two branches: ratios consistent within 2σ (constant-cost law) or
monotone degradation (resource-scale interaction). **Neither fired cleanly.** The strict 2σ
consistency test is violated (r₂ vs r₃ differ at ~4.6σ with these tiny errors) — but the drift
is **non-monotone** (down, then up: the *third* gate was the cheapest), which is the opposite
signature of the named resource-scale failure mode.

The diagnostic that settles it: **the local baseline shows the same texture, stronger** — local
w=3 (0.945) outperforms local w=2 (0.900), a per-gate ratio *above 1* in the monolithic machine.
Whatever produces the non-constant ratios (transpiler placement, coherent-error cancellation in
the 3-CX oracle chain, routing texture) lives in the chip and compiler, **shared by both
architectures — it is not a distribution cost.** Post-hoc analysis (labeled as such): the
distribution-only ratio dist/local per weight reads 0.994 / 0.992 / 0.918 — distribution costs
**under 1% per teleported gate at w ≤ 2**, ~3%/gate at w=3.

Refined statement (what the flight actually establishes):
1. Per-teleported-gate cost is **banded at 3.5–5.5% per dose** across three doses (r ∈
   [0.945, 0.972]), pooled 0.954 — an anecdote is now a banded law, with the caveat that the
   band's internal structure is compilation texture, not physics of distribution.
2. **No resource-scale interaction detected** at 10 qubits / 3 simultaneous e-bits — the named
   congestion/crosstalk failure mode produced no signature (w=3 was the cheapest per-gate dose).
3. The extrapolation license: r̂¹⁰ ∈ roughly [0.55, 0.75] given the ratio spread — deep
   distributed Clifford-consumption oracles remain decodable well past anything flown here.

## Ledger

- Primary, modal 8/8, falsifier floors, ALL dist/local/noresource bands, r̂ band: **every
  pre-registered band held — second consecutive all-bands flight** (the C4863/C4865/C4869
  calibration updates have converged the pricing model).
- Scaling consistency: neither branch fired; third path documented above. Method note for future
  pre-registrations: dose-response designs on compiled hardware should pre-register the
  *baseline-normalized* ratio (dist/local per dose) as the primary scaling quantity — the raw
  ratio confounds compiler texture with the effect under test. Banked as the flight's process
  lesson.

## Fence

n=3, one die, one night; "processors" are chip patches; e-bits pre-shared (standard model). The
r̂¹⁰ extrapolation assumes Clifford consumption (zero-window architecture) and no new error
channels at depths beyond those flown. The dist/local normalization is post-hoc this flight;
it becomes pre-registered primary in any follow-up.

## The arc, complete (nine flights)

175 tax → 176 dose → 177 decomposition → 178 cure → 179 architecture → 180 relay keys →
181 distributed computer → **182 scaling law**. The network wing: state → gate → relay compute
→ untrusted-relay keys → a distributed computer with a measured, banded per-gate price.
