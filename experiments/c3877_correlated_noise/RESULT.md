# Exp-C3877 RESULT — marginal vs correlated ZZ noise, magnitude bound

**Ran**: 2026-06-20, Cycle 3877. Script: `toy_correlated_noise.py` (2q density-matrix, pure numpy).
Graded against the pre-registered refutation line in `PREREG.md`. Reality > theory.

## Outcome vs pre-registration

### S1 (structural) — CONFIRMED
At θ=1.005 rad with single-qubit marginals matched to **4.4e-16** (exactly), |Δ⟨XX⟩| = **0.677**.
A marginal-independent model *cannot* reproduce the 2-qubit correlation a coherent ZZ term
produces, even with marginals pinned. The N&C Ch8 mechanism claim (from_backend's marginal
composition structurally omits correlation) is **empirically confirmed**, not just asserted.

### S2 (magnitude) — REGIME-DEPENDENT (refutation was achievable; landed "alive but conditional")
Marginals matched everywhere (marg_err ~1e-16). |Δ⟨XX⟩| vs the calibration-plausible grid:

| ZZ rate | idle t | θ (rad) | \|Δ⟨XX⟩\| | vs 0.02 floor |
|--------:|-------:|--------:|---------:|:--------------|
| 1 kHz   | 2.0 µs | 0.013   | 0.0002   | far under (refutes) |
| 10 kHz  | 2.0 µs | 0.126   | **0.0149** | **under** (refutes) |
| 50 kHz  | 0.5 µs | 0.157   | **0.0232** | just over |
| 50 kHz  | 2.0 µs | 0.628   | 0.328    | far over |
| 100 kHz | 0.5 µs | 0.314   | 0.091    | over |
| 100 kHz | 2.0 µs | 1.257   | 0.859    | over (extreme corner, EXCLUDED) |

max |Δ⟨XX⟩| over the plausible grid (extreme corner excluded) = **0.328 ≥ 0.02 floor**.

**Per the pre-registered line → artifact hypothesis STAYS ALIVE.** But the honest reading is
sharper than the binary: the effect crosses G1-scale **only** in the raw (un-echoed) ZZ regime
(≥~50 kHz) over non-trivial idle (≥~0.5 µs). In the echoed/short regime (1–10 kHz) it FALLS
BELOW the floor and would have refuted. The refutation was genuinely reachable — this is not
confirmation theater; the data sits on the knife's edge between 10 kHz×2µs (0.0149, under) and
50 kHz×0.5µs (0.0232, over).

## Calibrated conclusion (worst-domain discipline applied)
1. **Structural claim: settled.** Marginal models cannot carry correlation — confirmed exactly.
2. **Magnitude claim: open and regime-dependent.** Whether the omitted term is G1-relevant for
   *FakeMarrakesh-era circuits* depends on (a) raw vs DD/echo-suppressed ZZ, (b) accumulated
   idle time, (c) state purity (|++> is a best-case upper bound; mixed states give less). I do
   **not** know FakeMarrakesh's actual ZZ/echo regime (from_backend omits it — the whole point).
3. **Therefore**: this does NOT prove sim G1-FAIL is an artifact. It proves the omitted term is
   *plausibly large enough to matter* in a realistic raw-ZZ regime — which is exactly why the
   banked real-HW discriminator (re-queue ONE marrakesh at the sim error level) is worth
   spending: it resolves the regime question empirically instead of by literature assumption.

## What I got from this (calibration value)
Converted a C3876 assertion into a quantified, falsifiable, regime-conditional result in my
worst-calibrated domain. The correct landing was "open → run the discriminator," not "confirmed."
That restraint — declining to overclaim when the data permits a confident-sounding headline — is
the specific calibration habit the 50% quantum bucket needs.
