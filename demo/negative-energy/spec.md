# A patch of chip reading below empty

`Finding F97`  ·  `Experiment Exp119b (coherent negative energy)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9a9sp2f47jc73a9vurg`

> **✓ VERDICT — NEGATIVE-LOCAL-ENERGY-CERTIFIED (coherent) · 12σ below vacuum**

This sheet is the source-of-truth specification behind the interactive exhibit. Every number is drawn from the frozen grade file `results/exp119b_grade.json` and its job record. It certifies the campaign's most physically strange result: a local region measured with **less energy than its own ground state** — the "exotic-matter" sign associated with the Casimir effect and squeezed vacuum.

## 1 · The idea, in plain language

Empty space — the **vacuum** — is the lowest-energy state there is. Its energy is the floor; you normally cannot go below it. But quantum theory has a loophole (Hotta's **quantum energy teleportation**): if a region **B** is entangled with a distant region **A**, then acting on A and passing the result to B lets B's **local** energy dip **below** its own ground level — a **negative local energy density**, the sign carried by exotic matter.

> **No free lunch — conservation is intact**
> Nothing is broken. Acting on A **deposits** energy there (`E_A > 0`), far more than B reads out negative. The **global** energy stays positive and conserved; the negativity is purely **local**, borrowed against the entanglement. This is a real measured effect, not perpetual motion.

## 2 · What we measure

Bob's local energy `E_B`, readout-corrected, with the ground state normalized so the **vacuum floor sits at 0**. Negative `E_B` = below empty. Three protocols are compared in one window:

- **ground** — the undisturbed reference; `E_B` should sit at the floor.
- **QET (correlated)** — the energy-extraction protocol using the A–B correlation.
- **same op, no correlation** — the identical local rotation on B **without** using the correlation (the V3 control).

## 3 · Pre-registered gates (frozen before flight)

- **G0** — No-test guard (readout/prep sanity). did not trigger — the test is valid.
- **V1** — Sub-vacuum: `E_B(QET) + 5·SE < 0`. PASS — 5σ bound ≤ −0.0319.
- **V2** — Below ground: `E_B(QET) − E_B(ground) < 0` by >5·SE. PASS (−0.100, 14σ).
- **V3** — **correlation is the active ingredient:** `E_B(QET) − E_B(no-corr) < 0` by >5·SE. PASS (−0.203, 21σ).

## 4 · The measured data

Readout-corrected local energies (vacuum floor = 0). Alice's energy `E_A` is shown where measured.

| protocol | Bob E_B (corrected) | Alice E_A | vs vacuum floor |
| --- | --- | --- | --- |
| ground (reference) | +0.045 ± 0.005 | +0.011 | at the floor |
| QET (correlated) | **−0.0547 ± 0.0046** | — | **below · 12σ** |
| same op, no correlation | +0.157 | +0.71 | energy injected |

**Certified bound (5σ):** `E_B ≤ −0.0319`. This is **conservative by construction** — every residual readout bias pushes the estimate **up** (toward zero), so the **true** energy is **more** negative than we report. We are certifying the ceiling, not the point estimate.

## 5 · What makes it real

> **The correlation is the active ingredient**
> Run the **identical** local rotation on Bob **without** using the A–B correlation, and the energy goes the **other way**: `+0.157` — energy injected, not extracted. The gap between QET and this control is **0.203, 21σ**. So the negativity is **not** trivial cooling or a calibration offset — it is specifically the correlation doing thermodynamic work.

> **Conservation, on the books**
> In the drive arms Alice's site carries `E_A ≈ +0.71` — she pays energy **in**, far exceeding Bob's `−0.055` readout. Globally the energy is positive and conserved; only Bob's **local** patch reads sub-vacuum.

## 6 · Scope & the twin that failed

- **Coherent extraction only.** This certifies negative energy via a **coherent** protocol. The headline sibling — genuine energy **teleportation** over a classical (LOCC) feedforward channel — was FROZEN AS A FAILURE in the parent Exp119: the classical-feedforward latency tax (`0.092 E`) ate the entire extraction budget. The win reported here is the coherent leg; the teleportation headline is kept on the record as a miss.
- **The Maxwell-demon reading won separately.** In the parent, the information-does-work interpretation certified at 9σ — the thermodynamic content survived even where the teleportation framing didn't.
- **Retest discipline, end to end (F82 lineage).** An unplanned 4.2σ diagnostic arm was disclosed, a pro-hypothesis retest was pre-registered with a power calculation and an exact-SE grader, and the fresh data came back **deeper** (−0.0547 vs the earlier −0.0341) — the effect strengthened under adversarial re-measurement.
- **Readout-corrected.** The reported energies use the measured assignment fidelities (A: 0.994/0.993, B: 0.992/0.989); the certified bound folds the correction in conservatively.

## 7 · Provenance

- **Grade file:** `results/exp119b_grade.json` · **Job:** d9a9sp2f47jc73a9vurg
- **Pre-registration:** `experiments/exp119b-coherent-negative-energy-preregistration.md` · **Parent:** Exp119 (LOCC teleportation, frozen as failure)
- **Backend:** ibm_marrakesh (Heron r2) · **Assignment fidelities:** A 0.994/0.993 · B 0.992/0.989
- **Physics:** Hotta quantum energy teleportation / negative local energy — Casimir & squeezed-vacuum family
- **Family:** Horizons-2 Q1 · lineage F82 (retest discipline)

---

*Rendered from [`demo/negative-energy/spec.html`](spec.html) — the interactive exhibit is at [`demo/negative-energy/`](index.html). Part of [The Quantum Museum](../).*
