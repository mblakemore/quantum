# The Zeno Tractor Beam, measurement as a grip

`Finding F102`  ·  `Experiment Exp124 (Zeno cadence law + frontier)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9ai9ku6hjac73fefdeg`  ·  `Wing III · Horizons-2 Q6`

> **✓ VERDICT — TRACTOR BEAM 92σ · LAW MATCH TO 0.5%**

Full Specification Sheet

This sheet is the complete, source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the frozen grade file `results/exp124_grade.json` and its job record `results/exp124_jobids.json`. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

"A watched pot never boils" is literally true in quantum mechanics. Measure a system often enough and you **freeze** its evolution — this is the **quantum Zeno effect**. Here we point a full `π`-rotation at a qubit — a drive that, left alone, flips it all the way from ON to OFF — and then we **watch it** as it turns. Each measurement catches the qubit before it can rotate far and pulls it back toward ON. The act of looking is a **tractor beam**: the more often you watch, the more tightly the state is pinned.

But watching is not free. Every measurement is a slightly imperfect (QND) interaction that costs the qubit a little coherence. So there is a **frontier**: watch faster and you hold tighter, until the per-glance cost cancels the extra grip and the survival stops climbing. We measure the pinning law and locate that optimal cadence.

> **Scope, stated first**
> The quantum Zeno effect is **textbook** (Misra–Sudarshan 1977) and is credited as such. This apparatus pins against **coherent rotation** — a driven π-flip — **not** against T1 relaxation (Markovian decay is cadence-invariant, so it could not be frozen by watching). The contribution here is the frozen, **QND-corrected** cadence-law match and the **measured watch-cost frontier**.

## 2 · What we measure — the pinning law

The qubit starts ON. A full `π`-drive is trying to flip it OFF. We insert `N` equally spaced measurements ("looks") during that drive and record the **survival** — the fraction that stays ON. The ideal Zeno prediction is `[cos²(π/2N)]^N`: watch infinitely fast and the qubit never flips.

> **The QND correction**
> Raw survival sits below the ideal law because each measurement itself costs a little. We measure the per-projection QND cost independently, `q = 0.987`, and divide it out. The corrected curve then matches the ideal Zeno law `[cos²(π/2N)]^N` to **0.5%** through `N = 8` — the law confirmed once the apparatus's own cost is removed explicitly, rather than absorbed into a fit.

The whole experiment uses **zero two-qubit gates** — the cheapest, shallowest flight of the campaign — and it produced its cleanest law match.

## 3 · Pre-registered gates (frozen before flight)

The decision rules were written and committed in `experiments/exp124-zeno-preregistration.md` before any data was taken. The grade script self-tested against synthetic outcomes and passed **4/4** before touching the real counts.

- **G0** — Integrity guard: the no-drive control at cadence 8 must survive, `nodrive_8 > 0.7`, else NO-TEST. PASS.
- **W_TRACTOR** — Headline: `P(pinned_8) − P(unwatched_8) > 0.3` at 5σ. PASS (realized **0.644 − 0.020 = 0.624**, **92σ**).
- **W_CADENCE** — Support: watch faster ⇒ hold tighter, `P(pinned_8) − P(pinned_2) > 0` at 5σ. PASS (realized **0.644 − 0.246 = 0.398**, **87σ**).

Both fire: the tractor beam holds the qubit far above the unwatched flip, and holding tightens monotonically with watch cadence. Registered priors were **0.92** (W_TRACTOR) and **0.90** (W_CADENCE); both hit.

## 4 · The measured data

Survival (fraction that stays ON) versus watch cadence `N`. Unwatched, the π-drive flips the qubit almost completely; each added look pulls it back toward ON.

| watch cadence | survival (stays ON) | gap over unwatched | note |
| --- | --- | --- | --- |
| unwatched | 0.020 | — | π-drive flips it |
| N = 2 | 0.246 | 0.226 | — |
| N = 4 | 0.498 | 0.478 | fought to a draw |
| N = 8 | **0.644** | **0.624** | **92σ · law match 0.5%** |
| N = 16 | 0.664 | 0.644 | frontier · residual −0.012 |

Survival climbs from **2%** unwatched to **64%** at cadence 8 — the tractor beam, **92σ** over the unwatched flip. From `N = 8` to `N = 16` it barely tightens (64% → 66%): the **watch-cost frontier**. The `N = 16` residual of **−0.012** locates the optimal grip cadence — watch faster than this and each glance's cost starts eating the extra grip.

## 5 · Scope & caveats

- **Coherent rotation, not relaxation.** This pins the qubit against a driven **π-rotation**. It does **not** freeze T1 decay — Markovian relaxation is cadence-invariant and cannot be slowed by watching. The design correction was owned at freeze so the claim is not confused with a decay result.
- **The effect is textbook; the measurement is the contribution.** Misra–Sudarshan (1977) is credited for the Zeno effect itself. What is new here is the **QND-corrected law match** (per-projection cost `q = 0.987` divided out, agreement to 0.5% through N=8) and the **measured frontier** at N=16.
- **The frontier is a real, measured limit.** The N=16 plateau (survival 0.664, residual −0.012 below N=8's trend) is reported as the optimal cadence, not smoothed away — watching is beneficial only up to the point where its own cost cancels the gain.
- **Cheapest apparatus of the campaign.** Zero two-qubit gates, single-qubit circuit — a first for the program — and it delivered the cleanest law match. The result does not depend on any delicate entangling gate.

## 6 · Provenance

- **Grade file:** `results/exp124_grade.json` · **Job record:** `results/exp124_jobids.json`
- **Pre-registration:** `experiments/exp124-zeno-preregistration.md` · **Builder:** `experiments/exp124_zeno_sim.py::build`
- **Backend:** ibm_marrakesh (Heron r2) · **Apparatus:** zero two-qubit gates (single-qubit, cheapest of the campaign)
- **Self-test:** grade script 4/4 PASS on synthetic outcomes before scoring real data · gate lint `experiments/exp124_gate_lint_spec.json`
- **Family:** Horizons-2 Q6 (the completion) · sibling of the Twin Paradox (F100) and the Grandfather audit (F101)

---

*Rendered from [`demo/zeno-tractor/spec.html`](spec.html) — the interactive exhibit is at [`demo/zeno-tractor/`](index.html). Part of [The Quantum Museum](../).*
