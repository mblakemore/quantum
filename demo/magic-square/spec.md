# The Magic Square, a no-win game won

`Finding F106`  ·  `Experiment Exp126 (Peres–Mermin contextuality certification)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9akl8fu62qs738o68pg`  ·  `Wing II · Horizons-3 H5`

> **✓ VERDICT — CONTEXTUALITY CERTIFIED · 96.9% · 196σ**

This sheet is the complete, source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the frozen results file `results/exp126_hw_results.json` and its job record `results/exp126_jobids.json`. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

The **Peres–Mermin magic square** is a no-win scenario. Fill a 3×3 grid with `+1` and `−1` so that every row multiplies to `+1` and the three columns multiply to `+1, +1, −1`. It cannot be done — the grid multiplies to `+1` across the rows but `−1` down the columns, a flat contradiction, so **one rule always breaks**. That single unavoidable break caps any classical team at **8 wins in 9** rounds.

Quantum mechanics wins it with certainty. Swap each `±1` for a compatible quantum measurement (Pauli observables like `XI`, `ZZ`, `YY`); within any row or column they commute and multiply to the required sign, so **all six rules hold at once**. The reason no consistent classical assignment exists is that quantum observables are **contextual** — an observable's outcome depends on which compatible set it is measured alongside. F106 wins the game on silicon and, in doing so, certifies contextuality, the third of quantum theory's great "no classical model can do this" theorems.

> **Scope, stated first**
> This is a **game-value / contextuality advantage**, **not** a computational speedup — no time-to-solution claim is made (it is the campaign's one un-won scoreboard). The classical ceiling `8/9` is **enumerated in code over all 4,096 parity-respecting strategy pairs** — a bound proved inside the grader, not cited. The demonstration is **device-characterised, not loophole-free**. Prior art (Mermin–Peres) is credited plainly; the contribution is the frozen-court, enumerated-bound, adversarially-controlled certification.

## 2 · What we measure — and the controls that fence it

We play all **nine contexts** (the six rows and columns, over their shared observables) and pool the per-context win rates into a single **game value**. Then we check it against a bound and two controls:

- **The enumerated ceiling.** The grader enumerates every classical strategy pair (4,096 of them) and finds the best scores exactly **8/9 = 88.9%**. A second frozen fact: for *any* classical strategy (mixtures included), the **minimum** over contexts is also ≤ 8/9 — so even the worst-context value beating 8/9 is classically impossible.
- **The no-entanglement null.** We execute the same circuit with the shared entanglement removed. Without it, even a quantum machine should fall to the classical regime — a real executed control, not an assumed one.
- **Sentinels.** Prep/readout integrity probes guard against a device artefact masquerading as a win.

## 3 · Pre-registered gates (frozen before flight)

The decision rules were written and committed in `experiments/exp126-magic-square-preregistration.md` before any data was taken; the theorem checks and enumerated bound were verified in `exp126_magic_square_sim.py` (PASS) pre-freeze.

- **W1_GAME** — Primary: pooled win over the 9 contexts beats the ceiling, `p̂ > 8/9 + 5·SE`. PASS (realized **0.96901 ± 0.00041 = 196σ**).
- **W2_MIN** — Secondary: even the WORST context beats the ceiling, `min_c p̂_c > 8/9 + 5·SE` (classically impossible for the min). PASS (realized **r3c3 = 0.9482, 37.8σ**).
- **G_NULL** — Executed no-entanglement arm must stay at/below the ceiling, `p̂_null < 8/9`. PASS (realized **0.657, 92.7σ below**).
- **G_SENT** — Prep/readout integrity: both sentinels `≥ 0.95`. PASS.

All four fire: the game is won past the enumerated bound, the win survives even at the worst context, and the entanglement-stripped control collapses to the classical regime exactly as it must.

## 4 · The measured data

Headline quantities, each versus the enumerated `8/9` classical ceiling.

| quantity | measured value | vs 8/9 ceiling |
| --- | --- | --- |
| game value (pooled, 9 contexts) | **0.96901 ± 0.00041** | **+196σ** |
| worst context (r3c3, 10-CZ) | 0.9482 | +37.8σ |
| classical ceiling (enumerated, 4,096 pairs) | 0.8889 = 8/9 | — |
| no-entanglement null (executed) | 0.657 | −92.7σ (below) |

The measured per-context win rates (row-major) are `r1: 0.9833, 0.9832, 0.9497` · `r2: 0.9823, 0.9849, 0.9527` · `r3: 0.9640, 0.9726, 0.9482`. The minimum is **r3c3 = 0.9482** — the routing-heaviest, 10-CZ context — and even it clears the ceiling by **37.8σ**. A min-over-contexts above 8/9 is classically impossible even for mixtures, so the worst-case result alone certifies contextuality.

## 5 · Scope & caveats

- **An advantage, not a speedup.** This certifies a **game-value / contextuality** advantage. It makes no time-to-solution claim and is **not** a computational speedup — the one advantage the campaign's scoreboard still leaves un-won.
- **The ceiling is enumerated, not asserted.** `8/9` is proved inside the grader by exhausting all **4,096** parity-respecting strategy pairs, and the secondary min-over-contexts bound (also ≤ 8/9 for any mixture) is frozen alongside — so a worst-context win above 8/9 is classically impossible.
- **Device-characterised, not loophole-free.** This is a gate-model certification on a characterised device, with an executed no-entanglement null (0.657) and sentinel integrity checks — not a loophole-free Bell-type test.
- **Textbook priors credited.** The Mermin–Peres magic square is textbook and hardware demonstrations exist on other platforms. The contribution is the pre-registered, enumerated-bound, adversarially-controlled certification — completing the no-go triptych (Bell/nonlocality F73 · indefinite causal order F82 · contextuality F106).

## 6 · Provenance

- **Results file:** `results/exp126_hw_results.json` · **Job record:** `results/exp126_jobids.json`
- **Pre-registration:** `experiments/exp126-magic-square-preregistration.md` · **Bound & theorem checks:** `experiments/exp126_magic_square_sim.py` (PASS)
- **Backend:** ibm_marrakesh (Heron r2) · **Worst context:** r3c3, 10 CZ (routing-heaviest)
- **Controls:** executed no-entanglement null 0.657 (92.7σ below ceiling) · sentinels for prep/readout integrity
- **Family:** Horizons-3 H5 ("Kobayashi Maru") · no-go triptych with Bell (F73) and indefinite causal order (F82)

---

*Rendered from [`demo/magic-square/spec.html`](spec.html) — the interactive exhibit is at [`demo/magic-square/`](index.html). Part of [The Quantum Museum](../).*
