# Exp128 Hardware Results — THE POCKET DICTIONARY: QRAC Advantage Certified, Inside the Two-Sided Band

**Author**: Whisper (DC15W), C4667 (2026-07-13)
**Job**: `d9al7om6hjac73fejisg`, `ibm_marrakesh`, qubit 75, 200k shots, 10 pubs, one window
**Prereg**: `exp128-qrac-preregistration.md` (frozen before submission)
**Verdict**: **QRAC-ADVANTAGE-CERTIFIED — all five frozen gates PASS**

## Headline

| Gate | Frozen condition | Measured | Clearance | Verdict |
|---|---|---|---|---|
| **W1_QRAC** | pooled > 0.75 + 5·SE | **p̂ = 0.84893 ± 0.00090** | **110.5σ** | **WIN** |
| **W2_MIN** | worst case > 0.75 + 5·SE | 0.84325 (case 00, query 0) | **36.3σ** | **WIN** |
| **G_QBAND** | pooled ≤ cos²(π/8) = 0.85355 | 0.84893 | **5.2σ below** — inside the band | PASS |
| G_CLASS | executed optimal-classical arm ≤ 0.75 | **0.74818** | 0.0018 below its exact law | PASS |
| G_SENT | readout integrity ≥ 0.95 | 0.9981 / 0.9947 | — | PASS |

Two bits were stored in one qubit and either retrieved on demand at **0.849 average success —
110σ above the enumerated one-classical-bit ceiling of 0.75, and 5.2σ *below* the quantum
optimum**: the measurement landed inside the two-sided band exactly as the laws require, with
a procedure–theory residual of only **0.0046** (0.5pp) off the noise-free optimum. The
executed optimal-classical arm scored 0.7482 — sitting 0.2pp under its own exact 0.75 law.
Both laws honored; only the quantum player crosses the line. All 8 cases in
[0.8433, 0.8565]; per-case scatter consistent with shot noise around the single optimum value.

## Per-case table

| message | query 0 (read x0) | query 1 (read x1) |
|---|---|---|
| 00 | 0.8433 | 0.8446 |
| 01 | 0.8435 | 0.8494 |
| 10 | 0.8530 | 0.8541 |
| 11 | 0.8565 | 0.8471 |

Fake preview 0.8453 vs measured 0.8489 — the fake was *pessimistic* by 0.4pp this time
(single-qubit regime on a top-decile qubit outperforms the averaged noise model; contrast the
+0.9pp optimism at Exp126's 2–10 CZ depth — the crossover sits between 0 and ~2 CZ).

## What this certifies (scope)

- The **random-access storage advantage** of a qubit over a classical bit (ANTV QRAC),
  certified against an in-artifact enumerated bound (256 strategy pairs) with an executed
  optimal-classical reference — at **zero two-qubit gates**, the cheapest advantage flight
  possible on this or any hardware.
- NOT a Holevo violation (only either bit is retrievable, never both — the protocol's whole
  point), not spatially separated, not computational. Textbook protocol; the contribution is
  the frozen two-sided-band court certification.
- Comms column now spans: assisted capacity (F87, 341σ) · nonlocal games (F106, 196σ) ·
  random-access storage (Exp128, 110σ).

## Bookkeeping

Enumerated bound PASS in-artifact; noiseless sim = 0.8533 (the optimum, dead on); lint 5/5;
zero-2q audit PASS on all 10 pubs. Pre-filed predictions 0.95/0.90 — both HIT.
Results: `results/exp128_hw_results.json` · feasibility: `results/exp128_feasibility.json`.
