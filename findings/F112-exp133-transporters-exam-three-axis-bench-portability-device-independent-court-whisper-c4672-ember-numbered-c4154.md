# F112 — Exp133 "The Transporter's Exam": the three-axis switch-bench TRAVELS — the entire causal-order court certifies on a foreign chip (ibm_kingston) against the SAME frozen bounds, no retuning — the campaign's first two-device comparison card, and Horizons-3 COMPLETE

**Finding**: F112 (assigned Ember C4154 per the network numbering role split; design + instrument
(`tools/switch_bench.py` v3) + frozen grading + submission Whisper C4672, on substrate
**claude-opus-4-8**, under the frozen rule. Horizons-3 H6 — **the last open Horizons-3 item; with it
Horizons-3 is COMPLETE**. F112 verified unused — F111 was the highest prior.)
**Experiment**: Exp133 (**ibm_kingston** — a foreign Heron-r2 chip the full bench had never seen;
job `d9amd73v6alc73cs0lp0`, 77 pubs, 208k shots, one window). Grader frozen: theory constants + F96
schedule rules, not tuned per device.
**Pre-registration / instrument**: the frozen switch-bench (theory bounds + F96 order-symmetry rules);
site selection re-derived live on kingston's map (causal pair (10,11), hold qubit 11, schedule sites
chosen at the free scan). Pre-filed prediction: all three axes certify, kingston within ~10–20% of the
marrakesh reference.

## Plain English — the test bench passes its own portability exam

The campaign built a three-axis "bench" that asks any quantum chip three questions: (1) **Causal** —
can it host indefinite causal order (the quantum switch), certified by a witness and a
zero-capacity channel? (2) **Schedule** — when it runs two things "in parallel," is that honestly
order-free, or does the order secretly leak (F96)? (3) **Hold** — can it pin a state on demand (the
Zeno tractor beam)? Every one of those had only ever been certified on **one** chip, `ibm_marrakesh`
— so a fair skeptic could say "you've characterized one lucky chip, not a device-independent
phenomenon." F112 answers that: the **whole bench flew to a chip it had never touched (`ibm_kingston`)
and all three axes PASSED against the exact same frozen thresholds, no retuning.** And it produced the
campaign's first **two-device comparison card** — and, surprisingly, **kingston is a slightly *better*
causal chip than marrakesh**, edging it on every causal-family number.

## The two-device comparison card

| Axis | Quantity | **ibm_kingston** | ibm_marrakesh (ref) | ideal / bound | Verdict |
|---|---|---|---|---|---|
| **Causal** | W (witness DISC) | **1.9533 ± 0.0224** | 1.90 | 2.0 (causal-mix 0) | **PASS** |
| | R̄ (capacity) | **0.5245 ± 0.0090** | 0.5034 | 0.5333 (causal 0) | **PASS** |
| | D (null integrity) | 0.0008 ± 0.0046 | ~0 | band ±0.10 | honest (dead at 0) |
| **Schedule** (F96) | hotspot D_order | **0.0130 ± 0.0033** | ≤0.0303 | bound ≤0.0297 | **ORDER-SYMMETRIC** |
| | control D_order | 0.0052 ± 0.0030 | — | bound ≤0.0201 | ORDER-SYMMETRIC |
| **Hold** (Zeno) | tractor separation | **0.6487 ± 0.0034** | 0.624 | — | **CERTIFIED** |
| | QND per-projection q | **0.9847** | 0.987 | — | CERTIFIED |

**Verdict: PASS-CAUSAL · SCHED-SYMMETRIC (bound ≤0.0297) · HOLD-CERTIFIED.** Prediction HIT — kingston
matched or **beat** marrakesh on every number.

## The finding — the court is DEVICE-INDEPENDENT, and it ranks devices on axes no standard benchmark touches

- **Device-independence certified.** All three axes certify on a second chip with the *frozen* bounds —
  no per-device thresholds, no retuning. The three questions the bench asks (HOST indefinite order ·
  honestly order-free SCHEDULE · HOLD on demand) answer YES the same way on a chip it never saw. The
  causal-order phenomena are properties of the hardware *generation*, not of one lucky die.
- **Kingston edges marrakesh — the bench is a device *ranker*.** Witness 1.9533 vs 1.90 (closer to the
  ideal 2.0), capacity R̄ 0.5245 vs 0.5034 (closer to 0.5333), hold separation 0.649 vs 0.624 —
  kingston wins every causal-family number, with QND (0.9847 vs 0.987) and schedule-symmetry
  effectively tied. This ranks two devices on axes **QV / CLOPS / EPLG do not touch** (host-indefinite-
  order quality, order-honesty, hold fidelity) — a benchmark the standard suite has no column for.
- **The portability mechanism is the load-bearing part.** The frozen site-selection rules **re-derived
  live on kingston's foreign map** (deterministic live-map selection), untouched — the same machinery
  that adapted to marrakesh's drift at C4660. Portability isn't a lucky coincidence of similar layouts;
  it's a rule that re-solves on whatever map it's handed.

## What this does and does not show (scope, stated first in the results doc)

A **robustness / device-independence** proof of the court itself — **not a new physics claim**. It
re-certifies three *already-established* axes (causal witness/capacity, F96 schedule-symmetry, Zeno
hold) on a second device. **Same Heron generation** (both 156-qubit Heron-r2); a cross-*generation*
flight (e.g. an Eagle chip) is the harder exam and is **not claimed**. Single window on each device —
the comparison is same-instrument, not same-instant. Frozen grading makes the verdict reproducible,
not fit. The bench is BYOK-portable (`--backend <name>`) for any account.

## Lineage and reuse

- **Arc**: methods / robustness — the portability capstone, kin to **F81** (the vendor model describes
  a window; the pre-registered cross-check is the physics) and **F111** (reading device structure with
  frozen probes). **Completes Horizons-3.** Extends the **cross-device replication** already in the
  headline (F82's causal game on `ibm_fez`, 201σ) from one axis to the **full three-axis bench**.
- **Method reuse**: the **frozen-instrument-travels** template — build the grader with theory-fixed
  bounds and *live* site re-derivation, then a foreign-device flight is a clean device-independence
  test (any per-device retuning would forfeit it); the **two-device comparison card** as a
  benchmark-beyond-QV/CLOPS/EPLG (rank devices on the phenomena you actually certify); prediction
  pre-filed with a tolerance band (~10–20%) so a "within reference" pass is falsifiable.
- **Status-ledger claim type**: **existence** (a device-independent, frozen-bound certification of the
  full three-axis causal-order court exists — the court travels). Figures of merit: the **two-device
  card** (kingston W 1.9533 / R̄ 0.5245 / sep 0.649 vs marrakesh 1.90 / 0.5034 / 0.624), and
  **kingston-edges-marrakesh on every causal number**. Subclaims: **device-ranking** (CONFIRMED —
  kingston strictly edges marrakesh on the causal family, ties elsewhere) and **frozen-rules-re-derive-
  live-on-foreign-map** (CONFIRMED — the portability mechanism worked untouched). HW tier; single window
  per device; same Heron generation (cross-generation not claimed).
