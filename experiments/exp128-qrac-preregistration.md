# Exp128 Pre-Registration — THE POCKET DICTIONARY: 2→1 Quantum Random Access Code

**Author**: Whisper (DC15W), C4667 (2026-07-13)
**Status**: FROZEN before hardware submission
**Directive**: Creator ("Ember numbered — run the next one!") — next item in the audit's advantage
sequence (`docs/quantum-advantage-audit-whisper-c4666.md`, item b), after F106's triptych completion.

## Scope, stated first

- **What this is**: the communication-resource advantage at its absolute cheapest — **two bits
  stored in one qubit, either retrievable on demand**. Referee asks for bit b (uniform); one
  classical bit caps the average success at **0.75 exactly** (enumerated in-code over all 256
  deterministic strategy pairs; shared randomness is convex); one qubit achieves
  **cos²(π/8) = 0.8536** on every one of the 8 (message, query) cases — and 0.8536 is *also*
  the quantum optimum for this protocol, so the measurement is a **two-sided law test**: above
  the classical law, at-or-below the quantum law.
- **What this is NOT**: not a channel-capacity violation (Holevo forbids >1 bit *retrieved*;
  only either bit is retrievable, not both — that's the whole point), not spatially separated,
  not a computational claim. Prior art credited plainly: ANTV QRAC is textbook; hardware demos
  exist on multiple platforms. **Ours is the pre-registered, enumerated-bound, two-sided-band,
  classical-arm-executed gate-model certification** — and the first zero-two-qubit-gate
  *advantage* flight of the campaign (F102 was zero-2q but a law match, not a bound beat).
- Protocol: encode (x0,x1) at Bloch r = ((−1)^x1, 0, (−1)^x0)/√2 via Ry(θ),
  θ ∈ {π/4, −π/4, 3π/4, −3π/4}; decode x0 by Z measurement, x1 by X measurement (H + measure).

## Apparatus

1 qubit (calibration-gated: min readout + 1q error), **zero two-qubit gates** (audited: any
pub with 2q count > 0 aborts). Arms:
- `main_{x0x1}_{q}`: 8 pubs × 20k shots = 160k.
- `class_{x0}_q0`: optimal classical strategy executed (send x0 as basis state; hardware
  measures the query-0 leg; the query-1 leg is **0.5 exactly by construction** under uniform
  messages — this arm's ideal pooled value is exactly the classical optimum 0.75). 2 pubs × 20k.
  These pubs double as readout sentinels (basis-state prep + measure).
- Shuffled (seed 4667), co-batched in one job (same-window by construction).

## Frozen gates

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_QRAC** (primary) | pooled success over 8 uniform cases beats one classical bit | p̂ > 0.75 + 5·SE |
| **W2_MIN** | worst single case beats the ceiling (min ≤ avg ≤ 0.75 classically, mixtures incl.) | min p̂_case > 0.75 + 5·SE_case |
| **G_QBAND** | quantum law respected — a value above cos²(π/8) means apparatus/grading error | p̂ ≤ 0.8536 + 5·SE (violation ⇒ NO-TEST, not win) |
| **G_CLASS** | executed optimal-classical arm stays at/below its own law | (mean measured q0 + 0.5)/2 ≤ 0.75 |
| **G_SENT** | readout integrity (class q0 pubs) | both ≥ 0.95 |

**Figures of merit**: pooled p̂ with σ-clearance over 0.75; distance below the quantum optimum
(procedure–theory residual); min-case value. **Fake preview** (FakeMarrakesh): pooled 0.8453
(clearance +0.095, ≈105σ at budget), min 0.8410, class 0.7447. Noiseless: 0.8533 = optimum ✓.

**Pre-filed predictions**: W1 HIT conf 0.95 (single-qubit circuits are the substrate's best
regime); W2 HIT conf 0.90; G_QBAND respected conf 0.93; G_CLASS conf 0.92.

**NO-TEST conditions**: G_SENT failure → window NO-TEST; any pub transpiling to >0 two-qubit
gates → abort pre-submit; G_QBAND violation → apparatus audit, no grading.

## Relation to the campaign

Adds the **storage/communication-resource column** at the opposite depth extreme from F98
(63 CZ): a bound-beat with zero entangling gates. Together with F87 (superdense: entanglement
doubles a channel) and F106 (contextuality: entangled measurements win a game), the comms
white space now spans assisted-capacity, nonlocal-games, and random-access storage.
