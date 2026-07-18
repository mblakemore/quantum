# Finding — Exp176: THE REPEATER CHAIN — the composition tax compounds (dose-response at −9.4σ)

**Cycle**: C4863 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9e008kinv1c73apkuug`
(9 circuits: {direct, swap1, swap2} × ZZ/XX/YY, 8000 shots). The dose-response follow-on to
Exp175's composition tax, designed as a discriminator: does the tax scale with feedforward-window
count (link layer generically), or live only at the link×compute interface?

## Result — the chain certifies, and the tax accelerates

| arm | windows | ZZ / XX / YY | F(Φ+) | per-stage p ratio |
|-----|---------|--------------|-------|-------------------|
| direct | 0 | +0.970 / +0.969 / −0.969 | 0.977 | — |
| swap1 | 1 | +0.873 / +0.753 / −0.737 | 0.841 | 0.813 |
| **swap2** | 2 | +0.765 / +0.270 / −0.251 | **0.571** (9σ over 1/2) | **0.545** |

1. **A two-station repeater chain certifies end-to-end**: F(A–D) = 0.571, 9σ past the separable
   bound. A and D are two stations apart — neither they nor their partners' partners ever
   interacted. (First 2-swap chain of the campaign.)
2. **Dose-response is decisive**: multiplicative model (constant per-swap ratio, p2 = p1²/p0)
   predicts F = 0.730; measured 0.571 → **Δ = −0.212 at −9.4σ**. The tax is not a fixed
   interface cost — it **compounds within the link layer**. The second swap costs nearly twice
   the first (p-ratio 0.813 → 0.545).
3. **Pre-registered fingerprint held**: the ZZ vs XX/YY asymmetry grows with N
   (gap ≈ 0.00 → 0.12 → 0.50) — exactly the idle-window dephasing signature. Mechanism: each
   successive swap's feedforward window arrives *later*, so the surviving end-qubits idle
   entangled and unechoed for longer accumulated time; per-window cost grows with accumulated
   idle. Windows are the dose; the response is super-linear.

## The three-experiment picture (mechanism class now measured 3 ways)

- **Exp160**: teleport hops don't compose (state chaining, −0.095).
- **Exp175**: link×compute stack doesn't compose (−0.062, −3.4σ).
- **Exp176**: link×link doesn't compose either, and the deviation *grows* with window count
  (−0.212, −9.4σ) — so the Exp175 tax was not an interface anomaly; it is the small-N end of a
  compounding curve.

Cross-check: Exp176's swap2 (0.571, ~2 sequential feedforward episodes) lands almost exactly on
Exp175's relaygate (0.576, swap + EJS ≈ comparable accumulated feedforward latency) — consistent
with **accumulated window time, not layer type, as the controlling variable**.

Engineering statement for repeater design in miniature: on this hardware class, un-echoed
repeater chains lose fidelity **faster than exponentially** in hop count. Extrapolating the
measured per-stage ratios, a third swap would land near or below the 1/2 witness — the chain
depth ceiling without echo/purification is ~2–3 hops. The countermeasures this wing already
priced (echo during idle, Exp164; single-round distillation from a degraded start, Exp165) are
not optional at depth — they are what makes N≥3 possible at all.

## Ledger (honest accounting)

- **Primary held**: F(swap2) > 1/2 at ≥5σ (9σ). Gauges: direct 0.977 ✓, swap1 0.841 ✓ (Exp162:
  0.836; Exp175: 0.847 — third consistent reading of the single-swap link).
- **Band missed low again** (0.571 vs 0.60–0.75): second consecutive miss in the same direction.
  My composition priors systematically underestimate the tax — noted as a calibration update:
  future stacked-circuit bands should price super-linear window costs, not multiplicative ones.
- Scaling branch pre-registered as two-sided; the compounding branch fired at −9.4σ.

## Fence

Two dose points (N=1,2) establish super-multiplicative, not the functional form; N=3 would
distinguish accelerating-exponential from, e.g., quadratic-in-windows, but sits at/below the
witness where F resolution collapses. One die, one day, adjacent-patch routing, literal
per-stage corrections (no Pauli-frame deferral — deferring corrections classically is itself a
known optimization that would *reduce* window count and is the natural next lever).
