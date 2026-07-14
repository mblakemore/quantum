# The Grandfather Paradox, forbidden on silicon

`Finding F101`  ·  `Experiment Exp123 (P-CTC enforcement + backaction audit)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9ahnee6hjac73feegfg`  ·  `Wing III · Horizons-2 Q5`

> **✓ VERDICT — PARADOX SUPPRESSED 53× · FINGERPRINT 78σ**

This sheet is the complete, source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the frozen grade file `results/exp123_grade.json` and its job record `results/exp123_jobids.json`. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

The grandfather paradox is the oldest objection to time travel: go back, prevent your own grandfather from meeting your grandmother, and you are never born to make the trip — a story that cannot be consistent with itself. Physicist **Seth Lloyd** proposed a resolution. If a quantum time loop existed, it would only permit stories that are **self-consistent**; the universe effectively **post-selects** for consistency, and the paradoxical branches are simply pruned away. The grandfather kill cannot happen because there is **no self-consistent amplitude** for it.

We do not build a real closed timelike curve. We build the **model** Lloyd wrote down: a **post-selected CTC** (P-CTC), where a post-selection stands in for the loop closing on itself. Then we ask the chip two questions. First — **how hard does the timeline work to forbid a paradox?** We turn up the strength of the grandfather kill and measure the fraction of runs that survive as self-consistent. Second — **can the rate be faked?** A bystander who merely knew what the traveller did, before the loop closed, should carry a fingerprint that ordinary post-selection cannot leave.

> **Scope, stated first**
> This is **Lloyd's post-selection model** (P-CTC, 2011): **the post-selection IS the timeline**. It is **not** literal time travel and **not** a physical closed timelike curve — no signal is sent to the past. What is real is the measured hardware behaviour of that model: the enforcement rate and the nonlinear backaction fingerprint.

## 2 · What we measure — the rate and the fingerprint

Two observables carry the finding, on the shallowest apparatus of the whole campaign — **three CX gates**.

### The enforcement rate

A knob `θ` sets how hard the traveller tries to flip the grandfather bit: `θ = 0` is "leave him alone," `θ = π` is a full kill. We measure the **survival** — the fraction of runs that close self-consistently — down the ladder. The prediction of the model is the enforcement law `p(θ) = cos²(θ/2)` (normalised to the baseline): survival should fall to **zero** at a full kill.

### The fingerprint the rate cannot fake

A chronology-respecting **bystander** is correlated with the traveller *before* the loop closes, writing a plain **classical record** (a value along the Z axis). If this were trivial post-selection, that record would stay classical. Instead, closing the self-consistent loop **rotates the record into quantum coherence** — it appears along the X axis. That rotation is the nonlinear CTC backaction; a trivial post-selection cannot produce it.

## 3 · Pre-registered gates (frozen before flight)

The decision rules were written and committed in `experiments/exp123-pctc-preregistration.md` before any data was taken. The grade script self-tested against synthetic outcomes and passed **4/4** before touching the real counts.

- **G0** — Both arms must start balanced: baseline `p(0) ∈ [0.40, 0.60]`, else NO-TEST. PASS.
- **N1** — Miswire guard: broken-loop bystander stays classical, `X_S(broken,0) < 0.25`, else NO-TEST. PASS.
- **W_PARADOX** — Enforcement headline: `p(π)/p(0) < 0.1` at 5σ. PASS (realized **0.0188** — a **53× suppression**).
- **W_LOOP** — Backaction headline: `X_S(loop,0) − X_S(broken,0) > 0.5` at 5σ. PASS (realized **0.9415 ± 0.0120 = 78σ**).

Both headline gates fire and both NO-TEST guards stay clean ⇒ the timeline genuinely forbids the paradox **and** leaves the un-fakeable fingerprint. Registered prior on each headline was **0.90**; both hit.

## 4 · The measured data

Survival down the kill-strength ladder, normalised to the `θ=0` baseline (measured on the chip), with the model enforcement law `cos²(θ/2)` for comparison.

| kill strength θ | measured survival | law cos²(θ/2) | note |
| --- | --- | --- | --- |
| 0 · leave alone | 100% | 100% | baseline |
| π/4 · a nudge | 85.7% | 85.4% | — |
| π/2 · half | 51.8% | 50.0% | half pruned |
| 3π/4 · most | 17.1% | 14.6% | — |
| π · full kill | **1.9%** | 0% | **53× suppressed** |

The survival collapses along the model's `cos²(θ/2)` curve, and at a full kill only **1.9%** remains — a **53× suppression** of the paradox. Theory says the self-consistent amplitude is **exactly zero**; the 1.9% residue is readout noise, confirmed by a herald autopsy (the survivors show scrambled bystander statistics, not un-suppressed paradox). The full enforcement curve tracks to residuals below **0.013** — the timeline's law measured to about a percent.

> **The loop's fingerprint**
> Before the loop closes, the bystander's record is **classical**: `Z_S = 0.978` (a plain Z-axis value). After the self-consistent loop closes, the same record has rotated into **quantum coherence**: `X_S = 0.966` (an X-axis value). The certified quantity is the X-basis separation between loop-closed and loop-broken, `X_S(loop) − X_S(broken) = 0.9415 ± 0.0120 = 78σ` — the nonlinear backaction a trivial post-selection cannot fake.

## 5 · Scope & caveats

- **A model, not literal time travel.** This is **Lloyd's P-CTC (2011) post-selection model** — **the post-selection IS the timeline**. It is not a physical closed timelike curve and sends no signal to the past. The claim is about the measured behaviour of that model on hardware.
- **The residue is noise, not physics.** The model predicts **exactly zero** self-consistent amplitude at a full kill; the measured 1.9% survival is readout floor, confirmed by the herald autopsy (scrambled bystander statistics among the survivors). We report the residue openly rather than rounding it to the theoretical zero.
- **The fingerprint is the load-bearing claim.** A suppression rate alone could, in principle, be mimicked by an ordinary post-selection. The **78σ** rotation of a classical record into coherence is the observable a trivial post-selection cannot produce — that is what distinguishes genuine (modelled) CTC backaction.
- **Shallowest apparatus of the campaign.** Three CX gates — deliberately the opposite of the campaign's deepest circuits. The result rests on a very shallow, well-characterised device, not on a delicate deep circuit.

## 6 · Provenance

- **Grade file:** `results/exp123_grade.json` · **Job record:** `results/exp123_jobids.json`
- **Pre-registration:** `experiments/exp123-pctc-preregistration.md` · **Builder:** `experiments/exp123_pctc_sim.py::build`
- **Backend:** ibm_marrakesh (Heron r2) · **Apparatus:** 3 CX gates (shallowest of the campaign)
- **Self-test:** grade script 4/4 PASS on synthetic outcomes before scoring real data · gate lint `experiments/exp123_gate_lint_spec.json`
- **Family:** Horizons-2 Q5 · sibling of the Twin Paradox (F100) and the Zeno tractor beam (F102)

---

*Rendered from [`demo/grandfather/spec.html`](spec.html) — the interactive exhibit is at [`demo/grandfather/`](index.html). Part of [The Quantum Museum](../).*
