# ZNE cannot rescue the deep scar — a 0-QPU viability boundary (Ember, C4204)

**Creator directive (2026-07-18):** *"fly ZNE on the coherent residual"* — the lever I named in Exp173
for the ~40% residual signal loss on the N=8 scar. **The design-time viability check (0 QPU) is the
deliverable: zero-noise extrapolation cannot clear that residual at the scar's depth, and here is the
quantitative boundary and why.** No QPU was spent — running it would only reproduce a proven null.

---

## Why ZNE fails here — depth, quantified

ZNE amplifies hardware noise by a factor λ (gate folding), measures the observable at λ = 1, 2, 3…, and
extrapolates to λ = 0. It needs the λ = 1 point to sit at *high* fidelity so the extrapolation spans a
short, well-conditioned range. The scar circuits are the opposite regime:

| operating point | base CZ | per-λ survival f | anomaly λ=1 / 2 / 3 | exp-fit recovery (true) |
|---|---|---|---|---|
| **N=8** | 433 | 0.22 | 0.063 / 0.014 / 0.003 | 0.35 ± **0.20** (0.285) |
| **N=6** | 260 | 0.33 | 0.129 / 0.043 / 0.014 | 0.44 ± **0.21** (0.391) |
| **N=4** | 146 | 0.45 | 0.284 / 0.128 / 0.058 | 0.63 ± **0.04** (0.632) |

At N=6/N=8 the λ = 1 point is already at 22–33 % of ideal, and the λ = 2/3 points collapse into shot
noise (0.003–0.043). The exponential extrapolation is then unbiased but **useless** (SE ≈ 0.20 on a
~0.3 target — a 60–70 % error bar), and a linear fit is precise but **badly biased** (it cannot fit an
exponential decay). **No folding-based method escapes this — folding only makes the base circuit
deeper.** The boundary: reliable ZNE needs f ≳ 0.45, i.e. a base circuit ≲ ~150 CZ. The deep scar
(≥260 CZ) is past the mitigation-rescuable depth, full stop.

## The one viable version answers a *different* question

**N=4** PXP has a resolvable scar (noiseless anomaly +0.632 — the tiny ~7-state Hilbert space makes
|Z₂⟩ maximally distinct) at 146 CZ, where exponential ZNE recovers the noiseless value accurately
(0.63 ± 0.04). So an N=4 ZNE flight is a legitimate **method-reach** demonstration — "ZNE clears the
residual at shallow depth" — but it is **not** "ZNE rescued the N=8 scar." It characterizes where
mitigation works, not the deep residual Creator asked about. Flagged for Creator's call, not
auto-flown.

## Corrections to the Exp173 finding (advisor C4204 — before they propagate)

Two claims in `finding-exp173-scars-n8-defog-ember-c4203.md` were wrong and are corrected here:

1. **"Finer Trotter" is backwards.** The residual R = measured / (noiseless × s) uses the *same*
   Trotterized circuit in the numerator and the noiseless baseline, so **Trotter error cancels in R —
   it is not in the residual.** Finer Trotter adds gates → deeper → *lower* R. If any Trotter knob
   helps, it is *coarser* (shallower, which the ratio tolerates because the noiseless baseline moves
   with it). The residual is **hardware error beyond the 2q-depolarizing model: 1q gates, idle T1/T2,
   coherent gate miscalibration, crosstalk** — not "Trotter."

2. **"The residual is coherent" is unproven.** Exp173 established *not readout* (readout fidelity 0.99,
   mitigation barely moved the signal), **not** *coherent*. Coherent-vs-stochastic was never
   decomposed. The supported statement is: the residual is **hardware error beyond 2q-depolarizing and
   beyond readout**. And ZNE fails here **because of depth** (it suppresses stochastic and coherent
   error alike once the base circuit is deep) — not "because the residual is coherent."

## What the universe answered

Asked to clear the residual with ZNE: at the scar's depth, it can't — the base circuit is already so
deep that noise amplification drowns the extrapolation (N=6/N=8 recover with 60–70 % error bars). ZNE
is viable only at ≲ 150 CZ (N=4), where it recovers cleanly but answers the shallow-depth method
question, not the deep-scar one. The residual on the deep scar is **hardware error beyond
2q-depolarizing and beyond readout** (1q/idle/coherent-gate/crosstalk), and it is **past the
mitigation-rescuable depth**. The scar itself is now characterized four ways — survives the wall
(Exp172), decoherence-limited (Exp172), not fragile (Exp173), and its residual is not readout and not
ZNE-removable at depth (here). The mitigation wall, mapped.

**Numbering:** Exp174, 0-QPU viability analysis (no hardware job); companion boundary to Exp172/173.
