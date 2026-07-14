# Cooling from the order of operations — and a full engine cycle

`Findings F86 / F88 / F95`  ·  `Experiment Exp108 series (split · native fluid · engine loop)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d98vqfsqp3as739tfg0g`

> **✓ ICO REFRIGERATION CERTIFIED — split 21.1σ over causal 0 · full engine cycle runs (W1-loss kept)**

This sheet is the source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the frozen grade files `results/exp108_grade.json` and siblings, and the campaign finding rows for F86 / F88 / F95. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

Send a qubit through two channels that each drag it toward a fixed bath temperature. Normally the **order** in which the two channels act is fixed. Here it is put into a **quantum superposition of both orders** at once — an indefinite causal order (ICO), realised as a **quantum switch** controlled by an ancilla. Read the control qubit, and the target comes out **colder** or **hotter** than either bath it touched, depending on the outcome.

> **Why this is forbidden to ordered physics**
> Every **definite-order** composition of two constant-to-`τ` channels outputs `τ`, uncorrelated with the control — so a definite/mixed/dynamical process gives a split of **exactly Δ = 0**. Any split at all is the signature of indefinite causal order. This is the Felce–Vedral refrigeration resource (PRL 125, 070603); the contribution here is the frozen-court **measurement on silicon**.

## 2 · What we measure — and the method

The target's excited-state population `p₁` is the thermometer (higher `p₁` = hotter). We read it in each control branch and take the **split** `Δ = p₁|₋ − p₁|₊` against the causal value 0. The baths are two thermalizing channels with `τ = diag(0.75, 0.25)`. Three progressively harder tests:

- **F86 — the split.** Basis-prepared reservoirs; certify `Δ > 0` against the exact causal 0, with thermalization null arms confirming the baths reach `τ`.
- **F88 — native working fluid.** Re-fly with the reservoirs mixed by the chip's **own T1 decay** (X + live-calibrated delays) instead of classical basis-prep pooling — the working fluid is free.
- **F95 — the engine.** A complete loop: certify passive baths in, charge the target above the halfway line, extract work, and re-certify the output passive so the cycle can repeat. Demon books audited on-chip.

## 3 · Pre-registered gates (frozen before flight)

- **SPLIT (F86)** — `Δ > 0` vs the exact causal value, null arms thermalize. PASS — `Δ = 0.1796 ± 0.0085`, **21.1σ**; nulls 0.2496 / 0.2492.
- **NATIVE (F88)** — + branch colder than the **coldest** reservoir under the native T1 fluid. PASS — `Δ = 0.1645 ± 0.0127`, **5σ**.
- **W2 (F95)** — Output re-certified passive: `p₁ < 0.5` at 5σ. PASS — 0.4913 < 0.5 (W2 WIN).
- **W1 (F95)** — Quantitative drop-floor `> 0.05` at 5σ. LOSS — missed clearance by **0.7σ** (drop is 9.4σ from zero); kept in the record as a REFUTED magnitude subclaim.

## 4 · The measured data — three findings, one resource

| finding · what | key measured value | vs threshold | significance | verdict |
| --- | --- | --- | --- | --- |
| F86 · refrigeration split | Δ = 0.1796 ± 0.0085  
(p₁|₊ 0.2098 · p₁|₋ 0.3894) | causal value = 0 exactly | 21.1σ | WIN |
| F88 · native-fluid retest | Δ = 0.1645 ± 0.0127 | + colder than coldest reservoir | 5σ | CONFIRMED |
| F95 · full engine cycle | net work 0.0340 E/run  
(charge p₁|₋ = 0.5485) | passive → charged → passive | 7σ charge · W2 5σ | W2 WIN |

The F86 branches straddle the baths: the **+** branch at `p₁ = 0.2098` is **colder** than the reservoir, the **−** branch at `0.3894` hotter — a definite-order engine cannot separate them at all. The F95 loop runs end-to-end: passive baths in (0.426 / 0.444, each 5σ below 0.5) → the switch charges the target to `p₁ = 0.5485` (7σ above 0.5) → the power stroke drops `p₁` by 0.0920 for a net **0.0340 E/run** → the output re-certifies passive (0.4913 < 0.5 at 5σ). Demon ledger audited at +0.0051 E/action.

## 5 · Scope & caveats — including the loss we kept

- **Definite order gives split = 0, exactly.** The null is not an approximation — it is a theorem for constant-to-`τ` channels. That is what makes any measured `Δ > 0` a clean signature of indefinite causal order rather than a noise artifact.
- **The engine's W1 gate is a LOSS.** The quantitative drop-floor (`> 0.05` at 5σ) missed clearance by **0.7σ** and is frozen as LOSS — a REFUTED magnitude subclaim, kept in the record, not swept under. The **direction** is unambiguous (the drop is 9.4σ from zero and W2 passes); only the pre-filed **magnitude** at 5σ did not clear. The finding is the full cycle plus the leg that did not clear, together.
- **Modest harvest, free fluid.** Under the native working fluid (F88) the + branch reaches ≈ 0.462×T_res (~54% colder), harvesting ~1.9% of the Landauer bound — the working fluid is free, the record is not. Published-T1 ran +38–69% high vs calibration (bias, not drift), absorbed by drift-tolerant gates; the certificate rests on in-job measured values.

## 6 · Provenance

- **Job:** d98vqfsqp3as739tfg0g (Exp108, the F86 split) · **Backend:** ibm_marrakesh (Heron r2)
- **Grade files:** `results/exp108_grade.json` (F86) · `results/exp108b_grade.json` & `results/exp108c_grade.json` (F88 native-fluid retest)
- **Finding rows:** `docs/campaign-arcs.md` — F86 (thermal splitting WIN), F88 (native-fluid CONFIRMED), F95 (the full engine cycle)
- **Resource:** Felce–Vedral (PRL 125, 070603) · **Family:** Wing I, The Causal Switch · Horizons P4 (engine, end-to-end)

---

*Rendered from [`demo/ico-refrigerator/spec.html`](spec.html) — the interactive exhibit is at [`demo/ico-refrigerator/`](index.html). Part of [The Quantum Museum](../).*
