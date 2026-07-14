# A sextant made of entanglement — and the ladder it climbs

`Findings F108 / F109`  ·  `Experiment Exp129 (N=3, F108) + Exp130 (the N=2→5 ladder, F109)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9alnju6hjac73fek980`

> **✓ HEISENBERG ADVANTAGE CERTIFIED — vs an executed separable reference · persists to N=5**

Full Specification Sheet

This sheet is the source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the hardware records `results/exp130_hw_results.json` (the ladder) and `results/exp129_hw_results.json` (the N=3 certification), and the campaign finding rows for F108 / F109. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

To measure a tiny phase, you watch an interference **fringe** — a wave whose position shifts with the phase. If you use N **separate** probes, averaging their independent readings only sharpens your estimate as `√N` (the standard quantum limit). Tie the N probes into a single entangled **GHZ state** and the whole fringe oscillates **N times faster** with the phase — **super-resolution** — so its sensitivity grows as `N²`, and your precision scales as `N` instead of `√N`. That is the Heisenberg limit.

> **The textbook reference**
> GHZ super-resolution is textbook (Bollinger 1996). The contribution here is not the idea but the **measurement discipline**: the entangled probe is certified against a **separable reference actually executed on the same qubits** — not against a theoretical ideal you could always beat on paper. The classical arm ran at its own best case (`F_sep = 2.912 / 3.0`, `V₁ = 0.985`) and was beaten anyway.

## 2 · What we measure — and the method

The quantity is the **Fisher advantage** `R`: how much more phase information the GHZ probe carries per use than the executed separable reference, with `R = N` the ideal Heisenberg line. We also read the **visibility** `V` (fringe contrast, 1 = perfect) of each GHZ state — it decays a little as N grows, which is why the measured ladder tracks just **below** the ideal line rather than on it. The super-resolution is directly visible as structure: the GHZ fringe's frequency-scan peaks at exactly `k = N`.

- **GHZ arm:** N entangled probes, `2(N−1)` two-qubit gates of prep (4 CX at N=3) — cheap-prep metrology.
- **Separable arm:** N independent single-qubit probes, **zero** two-qubit gates — the classical best case, executed.
- **Readout:** the phase Fisher information of each arm; `R` is their ratio.

## 3 · Pre-registered gates (frozen before flight)

- **R-ADV** — GHZ Fisher information beats the **executed** separable reference at N=3. PASS — `R = 2.848 ± 0.011` (95% of the max 3.0), **168σ**.
- **BEAT-IDEAL** — GHZ beats even a **perfect** separable probe: `F_GHZ > 3`. PASS — `F_GHZ = 8.293`, **239.5σ**.
- **SUPER-RES** — Visibility over the `1/√3` threshold + fringe peak at `k = 3`. PASS — `V₃ = 0.9599`, **299σ**; free-scan peak k=3, 122.9× amp ratio.
- **LADDER** — Every rung N=2→5 beats the executed reference; `F_GHZ` grows monotonically ⇒ turnover point `N*`. PASS — **N* = 5, no turnover**.

## 4 · The measured data — the Heisenberg ladder

Each rung is the measured Fisher advantage `R` against the ideal Heisenberg line `R = N`, with the GHZ state's measured visibility `VN`. The separable single-qubit reference visibility is `V₁ = 0.9853`.

| N (probes) | Fisher advantage R | ideal (Heisenberg) | significance | GHZ visibility VN |
| --- | --- | --- | --- | --- |
| 2 | 1.944× | 2 | 66σ | 0.9781 |
| 3 | 2.859× | 3 | 91σ | 0.9672 |
| 4 | 3.643× | 4 | 147σ | 0.9445 |
| 5 | 4.411× ▲ | 5 | 101σ | 0.9286 |

▲ = the advantage is **still climbing at N=5** — no turnover. `R` tracks the Heisenberg line and bends gently below it as visibility decays (`R/N`: 0.97 → 0.88). The N=3 rung (`R = 2.859`, `F_GHZ = 8.42`) reproduces the F108 certification (`2.848`, `8.29`) across a different job, window, and substrate — a cross-validated replication.

## 5 · Scope & caveats — where the advantage is, and isn't

- **N=3 metrology advantage, textbook idea.** GHZ phase super-resolution is Bollinger (1996). The claim is the **executed-reference** certification and the ladder's persistence, not novelty of the physics.
- **Scaling is task-dependent — this is the headline.** Cheap-prep metrology (`2(N−1)` CX) keeps climbing through N=5, but the companion finding **F85** — expensive-prep capacity activation (110-CX) — **INVERTS at N=3 on the same silicon**. Same hardware, opposite scaling: the inversion is a property of the task's **depth cost**, not a hardware verdict. "NISQ scaling" is not one number; it depends on what you ask.
- **A local sensitivity, not unconditional superiority.** Advisor-audited scope: `R` is the local per-shot Fisher sensitivity given fringe confinement — not a claim of unconditional superiority over all separable strategies. `N*` is a turnover **location**, not a power-law exponent.

## 6 · Provenance

- **Job:** d9alnju6hjac73fek980 (the F109 ladder, Exp130) · **Backend:** ibm_marrakesh (Heron r2)
- **Records:** `results/exp130_hw_results.json` (ladder N=2→5) · `results/exp129_hw_results.json` (N=3 executed-reference certification, F108)
- **Finding rows:** `docs/campaign-arcs.md` — F108 (N=3 vs executed SQL reference) & F109 (the Heisenberg ladder)
- **Family:** Horizons-3 · Wing IV, The Advantage Ladder · companion to F85 (capacity-activation, the inverting task)

---

*Rendered from [`demo/ghz-sextant/spec.html`](spec.html) — the interactive exhibit is at [`demo/ghz-sextant/`](index.html). Part of [The Quantum Museum](../).*
