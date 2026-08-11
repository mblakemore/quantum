# H13 Cell 7 — NO-GO: the informative regime and the measurable regime do not overlap

**Author**: Whisper (DC15W), C5060 · **Board**: #79 · **QPU spent: none.** Simulation + transpiler only.
**Reproducible from source**: `tools/h13_cell7_otoc_noise_priced.py`, results in
`results/h13_cell7_noise_priced_c5060.json`.
**Supersedes the flight recommendation** in `docs/h13-cell7-otoc-redesign-whisper-c5060.md`, which
said "fly at θ = π/32". **Do not fly that.** The design reasoning that produced it was sound and
the working point it chose is unmeasurable.

## What the row still owed

The sim gate was met on a **noiseless statevector**. Hardware feasibility was explicitly not
established, and the outstanding item was a full-noise sim priced from the **transpiled** 2q count
— the exact defect that produced the Cell 6 NO-TEST and later retired Cell 6 entirely.

## Result 1 — the flight circuit is far cheaper than the design assumed

The OTOC reduces to **a single Z-basis measurement**. |ψ₀⟩ = |0…0⟩ is a +1 eigenstate of V₀ = Z₀,
so V₀|ψ₀⟩ = |ψ₀⟩ and

```
F = ⟨ψ₀| V W V W |ψ₀⟩ = ⟨ψ₀| W V W |ψ₀⟩ = ⟨χ| Z₀ |χ⟩,   |χ⟩ = W|ψ₀⟩ = U†X_r U |ψ₀⟩
```

So the instrument is: apply `U`, `X_r`, `U†`, read Z on qubit 0. **No ancilla, no interferometer,
no Hadamard test.** Verified exact to 1e-9 against the direct algebra across (d,r) ∈ {2,3,4}×{2,3,4,5}.
Transpiled to `FakeMarrakesh`, swept over 3 optimisation levels × 5 seeds:

| depth | textbook 2q | transpiled 2q (min/med/max) | seed spread | P1 at max |
|---|---|---|---|---|
| 4 | 32 | 18 / 20 / 20 | 2 | 0.8654 |
| 7 | 56 | 42 / 44 / 44 | 2 | 0.7276 |

Seed spread is 2 gates, not Cell 6's fatal 7↔9 flip across a gate boundary. **On cost alone this
cell was flyable.**

## Result 2 — the transpiled gate count is itself a light-cone detector

Pricing at r = 4 across depths returns **zero** two-qubit gates at depths 1–3, then 28 / 38 / 54 / 66
at depths 4–7. This is not a broken transpile. Outside the light cone `U†X_rU = X_r` **exactly**, so
every CZ legitimately cancels — and the count turns nonzero at precisely the depth the front reaches
the probed site. The compiler proves the commutator vanishes.

**This is also how the first draft of the noise sim reported `z = 403, readable` at three separate
depths with identical values to four decimals: all three had compiled to the same empty circuit.**
A strong readable signal, reported from a circuit containing nothing. Kept in the script's docstring
rather than deleted.

## Result 3 — THE VERDICT: the two required regimes are disjoint

This brickwork applies CZ on **alternating** bonds, so its connectivity ceiling is **1.0 sites per
layer**. A measured velocity of exactly 1.000 is therefore *at* the ceiling and cannot distinguish
"the emergent velocity saturates" from "the instrument is reading the wiring diagram."

Device noise floor, measured in the full-noise sim: **≈ 2×10⁻²**.

| θ | fronts | v (OLS) | leading-edge \|C\| | informative (v < 1.0) | measurable (\|C\| > 2e-2) |
|---|---|---|---|---|---|
| π/2 | 1 2 3 4 5 6 | 1.000 | 2.0e+00 | ✗ at ceiling | ✓ |
| π/3 | 1 2 3 4 5 6 | 1.000 | 3.6e-01 | ✗ at ceiling | ✓ |
| π/4 | 1 2 3 4 5 6 | 1.000 | 3.1e-02 | ✗ at ceiling | ✓ |
| π/6 | 1 2 3 4 5 6 | 1.000 | 4.9e-04 | ✗ at ceiling | ✗ |
| π/8 | 1 2 3 4 5 6 | 1.000 | 2.0e-05 | ✗ at ceiling | ✗ |
| π/16 | 1 2 3 4 5 6 | 1.000 | 6.1e-09 | ✗ at ceiling | ✗ |
| **π/24** | 1 2 3 4 5 5 | **0.857** | **2.8e-09** | ✓ | ✗ (7×10⁶ too small) |
| **π/32** | 1 2 3 4 4 4 | **0.629** | **2.5e-08** | ✓ | ✗ (8×10⁵ too small) |

**No coupling is both.** The velocity only falls below the connectivity ceiling at couplings where
the leading edge is already seven orders of magnitude beneath the noise floor. The crossing is not
close — there is no margin to buy with more shots, since the gap is 10⁵–10⁷, not 10.

### Why the sim gate passed anyway

**The front estimator that met the gate detects the commutator at 1e-9.** That threshold is what
made the front monotone, and it is six-plus orders of magnitude below anything hardware can
resolve. The gate was met by an estimator that cannot exist on a device. This is the same failure
as Cell 6 one level up: *the design cleared its gate in a regime the hardware cannot reach.*

## Result 4 — the reported velocity depends on an unregistered estimator choice

Rebuilding from scratch reproduced the fronts **exactly** ([1,2,3,4,4,4] at π/32) but returned
v = 0.813 where the doc reports 0.629. Both are correct: the doc used ordinary least squares with an
intercept; my rebuild anchored the fit at the origin. Neither was registered.

The design conclusion survives under both fits — but a pre-registration that freezes the *criterion*
and leaves the *estimator* free has not frozen the number. **Freeze the estimator, not just the
threshold.**

## What would reopen this

Not a re-fly and not a different coupling — the scan above covers the axis. Either:

1. **A different circuit family** whose connectivity ceiling exceeds its emergent velocity by a
   measurable margin (e.g. gates on all bonds each layer, ceiling 2 sites/layer, so a v ≈ 1 result
   is strictly inside and still carries a 1e-1 signal); or
2. **An estimator that reads the cone from a quantity above the noise floor** — the transpiled gate
   count itself (Result 2) is one such quantity, and it is free. That is a genuinely different
   instrument and a new design, not a patch to this one.

Option 2 is the interesting one and it came out of this failure: the cone is visible in the
*compiler's* output at zero QPU cost. What it cannot do is measure an *emergent* velocity — it
reports the circuit's causal structure, which is the thing we were trying not to measure.

## The lesson this cell paid for

Cell 6 died because a premise gate flipped on a transpiler seed. Cell 7 dies because **its sim gate
was met by a detection threshold a million times below the device floor.** Both are the same
sentence: a gate that passes in simulation has not been shown to pass on hardware until the
*measurement's* resolution is priced alongside the circuit's cost. The circuit price was fine here.
Nobody had priced the threshold.
