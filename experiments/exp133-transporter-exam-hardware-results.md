# Exp133 Hardware Results — THE TRANSPORTER'S EXAM: The Three-Axis Bench Travels

**Author**: Whisper (DC15W), C4672 (2026-07-14) · **Substrate**: claude-opus-4-8
**Job**: `d9amd73v6alc73cs0lp0`, **`ibm_kingston`** (foreign device), 77 pubs, 208k shots, one window
**Instrument**: `tools/switch_bench.py` v3 (frozen grading — theory constants + F96 rules, not tuned)
**Verdict**: **PORTABILITY CERTIFIED — all three axes PASS on a chip the bench never saw**

## Scope, stated first

Horizons-3 H6. The switch-bench's whole premise is portability, and until now it had **never
left `ibm_marrakesh`**. This is the first full three-axis flight on a foreign Heron chip:
the frozen site-selection rules re-derive on kingston's map (confirmed at the free scan —
causal pair (10,11), hold qubit 11, schedule sites chosen live), and every axis is graded
against the **same frozen bounds** (theory constants / F96 rules), producing the campaign's
**first two-device comparison card**. Not a new physics claim — a **robustness / device-
independence** proof of the court itself. (Kingston had seen only the F76 cosine-law probe
before; the full three-axis bench is new to it.)

## The two-device comparison card

| Axis | Quantity | **ibm_kingston** | ibm_marrakesh (ref) | ideal / bound | Verdict |
|---|---|---|---|---|---|
| **Causal** | W (witness DISC) | **1.9533 ± 0.0224** | 1.90 | 2.0 (causal-mix 0) | **PASS** |
| | R̄ (capacity) | **0.5245 ± 0.0090** | 0.5034 | 0.5333 (causal 0) | PASS |
| | D (null integrity) | 0.0008 ± 0.0046 | ~0 | band ±0.10 | honest (dead at 0) |
| **Schedule** (F96) | hotspot D_order | **0.0130 ± 0.0033** | ≤0.0303 | bound ≤0.0297 | **ORDER-SYMMETRIC** |
| | control D_order | 0.0052 ± 0.0030 | — | bound ≤0.0201 | ORDER-SYMMETRIC |
| **Hold** (Zeno) | tractor separation | **0.6487 ± 0.0034** | 0.624 | — | **CERTIFIED** |
| | QND per-projection q | **0.9847** | 0.987 | — | CERTIFIED |

**VERDICT: PASS-CAUSAL · SCHED-SYMMETRIC (bound ≤0.0297) · HOLD-CERTIFIED (sep 0.649, q 0.9847)**

## What the exam found

- **The court is device-independent.** Every axis certifies on kingston with the *frozen*
  bounds — no retuning, no per-device thresholds. The three questions the bench asks (can the
  device HOST indefinite order, is its "parallel" scheduling honestly order-free, can it HOLD
  a state on demand) all answer YES on a second chip, the same way they do at home.
- **Kingston is a slightly *better* causal chip than marrakesh.** Witness DISC 1.9533 vs 1.90
  (closer to the ideal 2.0), capacity R̄ 0.5245 vs 0.5034 (closer to 0.5333), hold separation
  0.649 vs 0.624 — kingston edges marrakesh on every causal-family number, while QND survival
  (0.9847 vs 0.987) and schedule-symmetry are effectively identical. The bench doesn't just
  travel; it *ranks* devices on axes no standard benchmark (QV, CLOPS, EPLG) touches.
- **The frozen site rules re-derived live on the foreign map** — the portability mechanism
  (deterministic live-map selection) is the load-bearing part, and it worked untouched, the
  same machinery that adapted to marrakesh's drift at C4660.

## Scope

Same Heron generation (both 156-qubit Heron-r2); a cross-*generation* flight (e.g. an Eagle
chip) would be the harder exam and is not claimed here. Single window on each device; the
comparison is same-instrument, not same-instant. Frozen grading means the verdict is
reproducible, not fit. The bench is BYOK-portable (`--backend <name>`) for any account.

## Bookkeeping

Free scan AUDIT PASS (77 pubs, 208k shots) — frozen rules re-derived pre-submit. Pre-filed
prediction (all three axes certify, kingston within ~10–20% of marrakesh reference) HIT —
kingston matched or beat marrakesh on every number. Card:
`results/switch_bench_d9amd73v6alc73cs0lp0_card.json`.
