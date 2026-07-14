# An instrument for causal-order physics — that travels

`Finding F112`  ·  `Experiment Exp133 (the transporter exam)`  ·  `Foreign chips ibm_kingston · ibm_fez`  ·  `Jobs d9amd73… · d9b9fvvu…`

> **✓ DEVICE-INDEPENDENCE — full 3-axis bench across THREE Heron dies (fez extends F112; not a clean 3/3)**

Full Specification Sheet

This sheet is the source-of-truth specification behind the interactive exhibit. Numbers are drawn from the frozen switch-bench cards for `kingston` and `fez` (`…d9b9fvvu…_card.json`), plus `marrakesh` (causal axis) and the Zeno run for the home HOLD axis. It is the campaign's **first two-device card**, and it completes Horizons-3.

## 1 · What is the switch-bench?

Chip vendors publish generic quality metrics — Quantum Volume, CLOPS, EPLG. None of them tell you whether a chip can actually do the **physics of causal-order superposition**. The **switch-bench** is an instrument that does: it reads **three axes** of the campaign's causal-order phenomena, each against a **frozen, pre-registered bound**. Each axis is a finding you can visit elsewhere in the museum:

- **CAUSAL** — is the order genuinely indefinite? The switch witness and its channel capacity. *(→ the Causal Switch)*
- **SCHEDULE** — is the chip **order-symmetric**, with no hidden preferred order sneaking in? *(→ F96 hidden-order)*
- **HOLD** — can measurement pin a qubit against a rotation (the quantum Zeno effect)? *(→ the Zeno Tractor Beam)*

## 2 · The transporter exam — the bench travels

The bench had only ever run on **ibm_marrakesh** (home). The test: fly the **entire three-axis bench** on a chip it had **never seen** — first **ibm_kingston**, then **ibm_fez** — and grade every axis against the **same frozen bounds, with no retuning**. If causal-order physics is a property of the **hardware generation** (both are IBM Heron), not one lucky die, the bench should certify on the foreign chip too.

> **Result**
> On kingston (one job, **77 pubs, 208,000 shots**), **all three axes certified** against the identical bounds — and the bench then **repeated on a third die, ibm_fez**, which also certifies all three axes (though **not as cleanly** — see §6). The frozen site-selection rules were **re-derived live** on each chip's unfamiliar qubit map — deterministic, untouched. The court is **device-independent**: the causal-order phenomena travel.

## 3 · Pre-registered gates (frozen; graded identically on both chips)

- **CAUSAL** — Witness certifies indefinite order + capacity above the dead null. PASS-CAUSAL (kingston W 1.9533 / fez 1.8948; R̄ 0.5245 / 0.5080).
- **SCHEDULE** — `D_order ≤ 0.0223` — no hidden preferred order. ORDER-SYMMETRIC (kingston 0.0130; fez 0.0185, but its split-half floor-transfer guard flagged — §6).
- **HOLD** — Zeno tractor separation over the 0.30 bar + QND fidelity. HOLD-CERTIFIED (kingston sep 0.6487 / fez 0.5247; q 0.9847 / 0.9708).

## 4 · The measured data — two devices, one standard

| axis · metric | ideal | marrakesh | kingston | fez | bound |
| --- | --- | --- | --- | --- | --- |
| CAUSAL · witness W | 2.000 | 1.9265 | 1.9533 ▲ | 1.8948 | ≫ 0 |
| CAUSAL · capacity R̄ | 0.5333 | 0.4978 | 0.5245 ▲ | 0.5080 | ≫ 0 null |
| SCHEDULE · D_order | 0 | symmetric | 0.0130 | 0.0185 ⚠ | ≤ 0.0223 |
| HOLD · tractor sep | ~0.73 | 0.624 | 0.6487 ▲ | 0.5247 | > 0.30 |
| HOLD · QND q | 1.000 | 0.987 | 0.9847 | 0.9708 | ≈ 1 |

▲ = leads. The three dies rank **kingston ≥ marrakesh ≥ fez** on the causal and Zeno-hold numbers — kingston leads W, R̄ and hold-separation; marrakesh edges QND. **fez, the newest die, certifies every axis but sits last**, and its SCHEDULE reading (⚠) tripped the split-half guard (§6). Device-independence holds across three dies; the bench ranks them.

## 5 · What it means

- **Device-independence.** The causal-order phenomena certify on a chip the bench had never seen, against the same bounds — so they are properties of the **Heron generation**, not one die's quirks.
- **A new kind of benchmark.** The bench **ranks devices on axes QV / CLOPS / EPLG do not touch** — it tells you which chip does causal-order physics **better** — here kingston leads, marrakesh second, fez last, all certifying.
- **Extends the cross-device story.** F82 replicated one axis (the causal game) on a second device; F112 replicates the **full three-axis bench across three dies** (marrakesh, kingston, fez).

## 6 · Scope & caveats

- **Same generation only.** Both chips are IBM Heron. Cross-**generation** travel (e.g. to Eagle) is **not** claimed here.
- **Same-instrument, not same-instant.** One calibration window per device; this is a device comparison across windows, not a simultaneous measurement.
- **Composite home reference.** The marrakesh numbers are drawn from the home-chip bench runs across the campaign (causal from the bench card, HOLD from the Zeno run); kingston and fez each ran all three axes in a single job.
- **fez is not a clean 3/3.** ibm_fez clears every frozen bound, but its SCHEDULE axis tripped the **split-half floor-transfer guard** (split-half median 0.0582 > the per-run bound 0.0464): the pooled hotspot D_order (0.0185) still reads order-symmetric, but the two halves disagree more than on the other dies — fez's schedule data is noisier. Reported as an extension of F112 with this caveat kept in the record, not a fourth clean certification.

## 7 · Provenance

- **Kingston card:** `results/switch_bench_d9amd73v6alc73cs0lp0_card.json` · **Job:** d9amd73v6alc73cs0lp0 (77 pubs, 208k shots)
- **Fez card:** `results/switch_bench_d9b9fvvu62qs738ov860_card.json` · **Job:** d9b9fvvu62qs738ov860 (77 pubs, 208k shots)
- **Marrakesh card:** `results/switch_bench_d9a7mn2f47jc73a9tcpg_card.json` (causal) · HOLD from the Zeno run (Exp124)
- **Backends:** ibm_marrakesh, ibm_kingston, ibm_fez (all Heron r2) · **Bounds frozen** pre-flight, identical on all three
- **Family:** Horizons-3 H6 (completes Horizons-3) · the three axes → the Causal Switch, F96 hidden-order, the Zeno Tractor Beam

---

*Rendered from [`demo/switch-bench/spec.html`](spec.html) — the interactive exhibit is at [`demo/switch-bench/`](index.html). Part of [The Quantum Museum](../).*
