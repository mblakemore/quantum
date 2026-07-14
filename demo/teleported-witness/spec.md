# Indefinite causal order, teleported one hop

`Finding F92`  ·  `Experiment Exp113 (teleported-control witness)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9a36352su3c739l3kf0`  ·  `Graded C4604 · Whisper`

> **✓ DOUBLE WIN — survives quantum (90σ) · dies classical (33σ separation)**

This sheet is the source-of-truth specification behind the interactive exhibit. Every number is drawn from the frozen grade file `results/exp113_grade.json` and its job record. This was the **first experiment born under the R5 grader-selftest rule** — the grader passed its synthetic self-test before it was allowed to touch hardware counts.

## 1 · The idea, in plain language

A **quantum switch** puts the **order** of two operations into superposition — A-then-B **and** B-then-A at once. A **causal witness** is a single number, `DISC`, that measures this indefiniteness: `DISC = 0` for any definite order (or any classical coin-flip between orders), and `DISC → 2` for perfect indefiniteness. The switch's indefiniteness is physically carried by one **control qubit**.

> **The question**
> **Can you teleport the indefiniteness?** Quantum teleportation moves a qubit's state from one place to another using a shared entangled pair and two classical bits — no wire carries the qubit itself. So: move the switch's control qubit one hop **before** reading its witness. Does the indefinite causal order arrive intact — or does teleportation destroy it? And crucially, does it ride on the **entanglement**, or would any channel do?

## 2 · Four channels, one job, one window

The control qubit's witness is read under four conditions, all in the same calibration window so they are directly comparable:

- **direct** — no teleportation; the same-window baseline (`DISC = 1.8805`).
- **tele · quantum** — teleported over a genuine entangled Bell resource, frame-tracked.
- **tele · quantum + feedforward** — same, but with active if-test correction (a third observable family, the F90/F91 cost comparison).
- **tele · classical** — the **identical** teleport, but over a **dephased** (decohered) Bell resource. The protocol still runs; the resource is no longer quantum.

## 3 · Pre-registered gates (frozen; R5 self-test passed first)

- **G1** — Readout sentinels ≥ 0.95, else NO-TEST. PASS (0.9995 / 0.99 / 0.9985 / 0.9935).
- **G2** — Anchor: `DISC_direct − 5·SE > 1.60` (a live F75-class witness this window). PASS (1.8805).
- **W1** — **survival:** `DISC_tele_quantum − 5·SE > 1.0`. PASS (1.825, 90σ over the bar).
- **W2** — **channel discrimination:** `(DISC_quantum − DISC_classical) − 5·SE > 1.0`. PASS (separation 1.8075, 33σ).
- **G3** — **null integrity:** `|DISC_classical| + 5·SE < 0.15` — the classical channel must be genuinely dead, not merely leaky. PASS (0.0175, band 0.13).

## 4 · The measured data

Witness `DISC = ⟨X⟩_comm − ⟨X⟩_anti`. `0` = classical / definite-order value; `2` = noiseless indefinite maximum; `1.0` = the pre-registered WIN bar.

| channel | DISC | vs WIN bar (1.0) | % of direct | survives? |
| --- | --- | --- | --- | --- |
| direct (no teleport) | 1.8805 ± 0.008 | +116σ | 100% | anchor |
| tele · quantum | **1.8250 ± 0.009** | **+90σ** | **97.0%** | ✓ survives |
| tele · quantum + feedforward | 1.7660 ± 0.010 | +73σ | 93.9% | ✓ survives |
| tele · classical (dephased) | **0.0175 ± 0.022** | below — dead | 0.9% | ✗ dies |

## 5 · Survives quantum, dies classical — why the null matters

> **The double win**
> The control qubit — the carrier of indefinite causal order — was moved across the chip and arrived **still causally indefinite**: `DISC = 1.825`, 97% of the un-teleported anchor, 90σ over the WIN bar. Indefinite causal order is a **transmissible resource**.

> **The executed classical null — this is what makes it a claim**
> The **identical** teleport over a dephased Bell resource kills the witness dead: `0.0175 ≈ 0`. That executed null is the whole point. Without it, "the witness survived teleportation" could just mean "the witness survived some noise." With it, the meaning is exact: the indefiniteness **rides on the entanglement** — kill the quantum resource and the indefiniteness does not arrive. **Transmission by entanglement, not decoherence survival.**

**A sub-result kept on the record.** Active feedforward correction costs a little: `tele_active = 1.766 <
  tele_frame = 1.825` — the F90 feedforward penalty appearing in a **fourth** observable family. The noise-model preview had guessed the **opposite** ordering; the hardware corrected it, and the miss is reported, not hidden. All four pre-filed predictions hit, including this one.

## 6 · Scope & caveats

- **A causal witness, not spacetime.** "Indefinite causal order" here is the switch-control coherence that no definite ordering (or classical mixture) can fake — a laboratory resource, not a claim about the order of events in spacetime.
- **Standard teleportation.** The transport is ordinary quantum teleportation (Bell pair + classical bits). The novelty is **what** is teleported — the carrier of causal indefiniteness — and the executed classical control that isolates the entanglement as the cause.
- **Survival is near-complete but not exact.** 97% of the anchor, not 100%; the noiseless expectation is exact survival (DISC 2.0). The 3% and the feedforward cost are reported.
- **Same F75/F82 witness apparatus.** The teleported witness is the same certified causal-witness machinery that fires on this chip un-teleported.

## 7 · Provenance

- **Grade file:** `results/exp113_grade.json` · **Job:** d9a36352su3c739l3kf0
- **Pre-registration:** `experiments/exp113-teleported-witness-preregistration.md` · **WIN bar:** 1.0 · **survival band:** [0.90, 1.00]
- **Backend:** ibm_marrakesh (Heron r2) · **Sentinels:** 0.9935–0.9995 (start/end)
- **First flight under R5:** grader synthetic self-test passed before hardware grading (frozen rule C4603)
- **Family:** the Causal Switch arc (F73–F95) · same witness as F75 (first hardware fire) and F82 (the causal game)

---

*Rendered from [`demo/teleported-witness/spec.html`](spec.html) — the interactive exhibit is at [`demo/teleported-witness/`](index.html). Part of [The Quantum Museum](../).*
