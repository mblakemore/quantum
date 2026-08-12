# H13 Cell 5 — PINNED-PLACEMENT re-fly + PLACEMENT-SENSITIVITY sweep (FROZEN before submit)

**Author**: Whisper (DC15W), C5060 · **Boards**: #113 and #115, answered by ONE flight
**Creator GO**: "create board tasks for the 3 (both/and!) and run them"
**Supersedes**: the C5060 pigeonhole prereg `quantum@499cc2b`, which is spent and whose G4 was
defective (the control keeps 0.98 **by construction**; I registered a bound it could never satisfy).
**Genre**: foundations + instrument characterisation. **Not an advantage claim.**

## Why this is not a re-run of a failed experiment

The prior flight tested the physics on a **confounded apparatus**. Three pair-arms flew with no
pinned `initial_layout`:

```
pair (0,1)  qubits [12,13,14,89]   bias +0.09467
pair (0,2)  qubits [12,13,14,89]   bias +0.09508    <- same placement, agree to 4e-4
pair (1,2)  qubits [ 0, 1, 2, 3]   bias -0.19872    <- different placement, opposite sign
```

All four arms were in one job, so drift is common-mode (Finding 07: ±7pp is a *cross-window*
quantity). **The pair-to-pair comparison IS the pigeonhole claim, and it was confounded with
physical qubit choice.**

## The placements — picked live at flight time, never cached (F58/F70)

| label | qubits | picker score | why included |
|---|---|---|---|
| **BEST** | live `pick(mode='best')` | lowest | the unconfounded test for #113 |
| **WORST** | live `pick(mode='worst')` | highest | spans the picker's range for #115 |
| **flownA** | `[12,13,14,89]` | mean readout 0.01270 | reproduces the +0.095 reading |
| **flownB** | `[0,1,2,3]` | mean readout 0.00751 | reproduces the −0.199 reading |

**A prediction I am registering as likely FALSE, because it already looks false:** flownB has
*better* readout error than flownA (0.00751 vs 0.01270) and produced the *worse* bias. So I do
**not** expect the picker's readout-based ranking to predict weak-measurement bias. Registering
that in advance so a null correlation cannot be reported later as an expected result.

## Arms — 7 circuits, 20,000 shots each, ONE job

```
1  control @ BEST        4  pair12  @ BEST         6  pair01 @ flownA
2  pair01  @ BEST        5  pair01  @ WORST        7  pair01 @ flownB
3  pair02  @ BEST
```

Estimated cost **≈43 QPU-s** at the measured 0.31 ms/shot; ask under the G-EPOCH margin
`max(43×1.5, 43+20)` = **65 s**. Account `IBMQ_ALT4`, backend `ibm_marrakesh`, ε = 0.25 unchanged.

## Gates

**G1 — CONTROL MUST MOVE.** |shift| ≥ 0.15 on arm 1. Failure = **NO-TEST**, checked first, for the
same reason as last time: the pigeonhole prediction is zero, so a dead apparatus and a successful
detection read identically. **No keep-fraction bound is placed on the control this time** — it keeps
~0.98 by construction, and last flight I registered a bound it could not satisfy.

**G2 — KEEP FRACTIONS** on the six pigeonhole arms within **[0.09, 0.16]** (ideal 0.125).

**G3 — #113, THE PINNED TEST.** On BEST, all three pairs must read **|bias| ≤ 0.06** and their sum
of "same box" probabilities must be **< 0.50** against the in-code classical floor of 1.
**PASS reopens Cell 5. FAIL closes it on an unconfounded measurement.**

**G4 — #115, THE SENSITIVITY NUMBER.** Report per-placement bias for pair01 across BEST / WORST /
flownA / flownB, the **spread** (max − min), and whether the ordering matches the picker's score
ranking. This gate **cannot fail** — it is a measurement, not a test — and it is labelled as such so
no reader mistakes a reported number for a passed criterion.

## Falsifiers, stated in advance

- **Control does not move** → NO-TEST, nothing claimed, no placement conclusions drawn.
- **All three BEST pairs ≤ 0.06 and sum < 0.50** → the pigeonhole effect survives on an unconfounded
  apparatus, and the prior failure was placement. Cell 5 reopens.
- **BEST pairs still exceed 0.06** → placement was not the whole story; the effect does not survive
  on this device at this coupling, and Cell 5 closes on a clean measurement.
- **flownA/flownB do not reproduce ~+0.095 / ~−0.199** → the readings were not placement-stable
  either, which would make the original failure a *drift* result and would invalidate the entire
  placement diagnosis. **This is the falsifier for my own new hypothesis** and I am flying it
  deliberately.
- **Spread across placements < 0.05** → placement sensitivity is small for this class and the Cell 5
  diagnosis was wrong.

## What this cannot do

It cannot rescue the pigeonhole claim by itself: a PASS on BEST is one placement on one day and
would need replication before anything is claimed. And error mitigation is **not** a follow-up
route — Finding 07 measured all four standard techniques (DD/PT/TREM/ZNE) as net detractors on this
chip class.
