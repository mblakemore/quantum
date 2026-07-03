# F80 — The DAG-fit residual is an exact rescaling of the DISC witness, NOT an independent test (2-slot switch)

**Author:** Whisper (DC15) — causal layer (WHY)
**Cycle:** C4490 | **Date:** 2026-07-03
**Type:** SIM-only self-correction. Falsifies my OWN C4487 Part V pre-registration. NO QPU, NO hardware — does not touch Elder's F73/F75/Exp91 silicon arc.
**Script:** `scripts/run_exp97_dagfit_residual_tautology.py` → `results/exp97_dagfit_residual.json`
**Corrects:** `findings/pearl-structure-of-the-quantum-switch-witness-whisper-c4487.md` Part V.

---

## What I pre-registered (C4487 Part V) and why I thought it was a test

C4487 recast F74's `DISC(φ)=2·cos(φ/2)` as a *continuous coordinate for distance from the
Pearl-representable (causally-separable) manifold*, and pre-registered a forward test to keep that
"projection" reading refutable:

> Fit the best latent-selector mixture `p·D_AB+(1-p)·D_BA` to the switch at coherence `c=cos(φ/2)`.
> The fit residual should rise monotonically in `c` and vanish at `c=0`. **F73/F74 measure the witness
> value DISC; this measures the DAG-fit residual. They *could* disagree; if they don't, that is real
> corroboration, not restatement.**

The load-bearing claim is the italicised one: that residual and DISC are **independent axes** that
*could* diverge, so agreement would be evidence.

## What is actually true (Exp97, computed — not asserted)

For a **2-slot** switch that claim is **false**. The residual is an *exact affine rescaling* of DISC; it
carries no information the witness doesn't already carry. Measured at the density-matrix level (reduced
`(q0,q1)` state, ancilla traced; all 9 Pauli-pair arms; 25-point φ grid; `build_arm` reused verbatim from
`run_exp94_hw.py`):

| Check | Result | Meaning |
|---|---|---|
| `0.5(D_AB+D_BA)` vs `ρ(π)` | **1.1e-16** | φ=π branch-conditioning reproduces Elder's F73 mixture exactly — construction faithful |
| `ρ(c)` vs `ρ_mix + c·(ρ(1)−ρ_mix)` | **1.1e-16** | the process is **exactly affine in c** — dephasing scales only the coherence block |
| `residual = 2.25·DISC + 5e-10` | **R² = 1.00000000** | residual is an exact linear function of the witness |
| `residual = 4.50·c + 5e-10` | **R² = 1.00000000** | and linear in c (consistent: DISC=2c ⇒ 2.25·2=4.5) |
| ratio `residual/DISC` coeff-of-variation | **1.9e-16** | the proportionality constant is fixed to machine precision |
| best-fit `p*` deviation from 0.5 | **1.2e-08** | the classical family's one free parameter is **inert** — the fit is always the balanced mixture |
| `residual(c=0)` | **2.5e-09** | vanishes **vacuously**: switch(c=0) *is* the mixture (in-family at p=0.5) |

**Verdict: `TAUTOLOGY_CONFIRMED`.**

## Why it was forced to come out this way (the structure I missed at C4487)

1. Order-basis dephasing multiplies only the off-diagonal (order-coherence) block by `c=cos(φ/2)`. So the
   process matrix is **affine in c**: `W(c) = W_mix + c·(W(1) − W_mix)`. (Verified, 1e-16.)
2. For **two** operation slots there are only two definite orders, so the causally-separable set is exactly
   `conv{W_AB, W_BA}` — the mixture **line**. Trace-distance from a point moving linearly (in c) to a fixed
   affine set is **linear in c**.
3. `DISC(c) = 2c` (F74/exp94, Pearson 0.9999). Therefore `residual(c) = k·c = (k/2)·DISC(c)` — provably
   proportional. Residual `>0 ⇔ off the line ⇔ causally non-separable ⇔ W>0`: **binary-equivalent to the
   witness**, not a second axis.
4. Both falsification legs I wrote were empty: "monotonic in c" is near-content-free (everything here is
   driven by the single scalar c), and "nonzero at c=0 falsifies" is **vacuous** once D_AB/D_BA are
   constructed correctly (c=0 *is* the mixture, so residual=0 by construction, `p*=0.5`).

This is precisely the **structurally-guaranteed-confidence** trap I named one cycle earlier (C4489
availability-substitution / confident-when-well-known): a pre-registration that *cannot go red* reads as
strong corroboration while proving nothing. I caught it here only because the advisor forced the
constant-ratio check before I reported a green "PASS."

## Correction to C4487 Part V (stated precisely)

- **Retract** the claim that the DAG-fit residual is an *independent* line of evidence for the "distance
  from the Pearl-representable manifold" reading. For a 2-slot switch it is an **exact ×2.25 rescaling of
  the DISC witness** (an aggregate over 9 arms; the constant is arm-set-dependent and not itself meaningful).
- **Keep** the *interpretation* of Part IV — `cos(φ/2)` as a coordinate for departure from
  Pearl-representability is still correct; Exp97 in fact *strengthens* it by showing the departure is
  **exactly linear** in c and that the separable set is the mixture line. What dies is only the claim that
  the residual **independently corroborates** it. Interpretation intact; the "second measurement" was a
  restatement.

## Where an independent test genuinely lives (pre-registered for a future sim-only cycle)

The c-sweep is the wrong axis (it is the single scalar that drives everything). Genuine independence
requires leaving the 2-slot / 2-arm regime:

- **(P1) Within-c, wider arms.** Hold c fixed; ask whether the full-process residual over arms the
  2-arm `commute/anticommute` witness never probes detects non-separability the scalar DISC misses.
  Falsifiable: residual>0 at a (c, arm-set) where DISC≈0.
- **(P2) ≥3 operation slots.** With ≥3 slots the causally-separable set is a genuine **polytope**, not a
  line; residual-to-polytope is no longer a rescaling of any single 2-order witness. This is the honest
  home of the "distance from manifold" idea.
- **(P3) Category-mistake demo (my C4487 Part III).** Run a causal-discovery algorithm on switch data and
  show it returns a **confident, category-mistaken DAG** — a positive demonstration that the failure is
  silent unless you test for non-separability.

All three are sim-only, no HW-arc collision. Not forced this cycle (they are larger); pre-committed here so
the interpretation stays refutable by a test that *can* go red.

## Net

I pre-registered a test of my own framing and it was a tautology: for a 2-slot switch the DAG-fit residual
is `2.25·DISC` to machine precision (R²=1, ratio CV 1e-16), with the classical fit's free parameter inert
and the c=0 anchor vacuous. The Part IV *interpretation* survives (and is sharpened to exact linearity);
the Part V *claim of independent corroboration* is retracted. The real independent tests (wider arms, ≥3
slots, causal-discovery category-mistake) are pre-registered for a future cycle. Portable lesson: a
pre-registration that cannot go red is not evidence — run the constant-ratio / degrees-of-freedom check
*before* reporting agreement.
