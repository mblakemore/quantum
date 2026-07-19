# Exp197 THE FEDERATION — CERTIFIED: entanglement swapped between shields, 22σ (C4889)

Job `d9e7ffkjeosc73fiekc0`, ibm_fez, 8000 shots × 12 circuits. All six pre-registered gates held.

## Result

| arm | Z̄Z̄ | Z̄X̄ | X̄Z̄ | X̄X̄ | S_L1 | S_L2 |
|---|---|---|---|---|---|---|
| federation (corrected) | +0.865 | +0.006 | +0.015 | +0.977 | **2.6046** | 1.385 |
| federation (relay bits ignored) | — | — | — | — | −0.018 | — |
| norelay | −0.001 | −0.013 | +0.006 | −0.024 | −0.036 | 1.378 |
| bare swap | +0.878 | +0.009 | +0.022 | +0.794 | 2.3646 | — |

- **PRIMARY**: S(A,C | relay bits) = 2.6046 vs classical bound 2 → **22σ**, band [2.10, 2.85];
  the C4887 budget rule predicted 2.4–2.6 pre-flight — landed at the top of the band. Ships A
  and C share no gate anywhere in the circuit.
- **IN-DECODE FALSIFIER**: the same shots decoded with the relay's two bits ignored → S = −0.018.
  **The weld IS the two classical bits.** ✓
- **HW FALSIFIER**: relay measured without the Bell rotation → S = −0.036. The measurement
  *basis*, not the measurement, does the welding. ✓
- **IN-SHOT CONTROL**: ride-along product pair at 1.385 ≈ √2, below the bound, same shots. ✓
- **NULLS**: +0.006 / +0.015. ✓
- **REFERENCE**: bare 4-qubit swap 2.3646 → **shielded beats bare by +0.240** — the largest
  shield advantage measured yet (Exp191 +0.07, Exp196 +0.06). Error detection pays more as
  protocol depth grows: exactly the fault-tolerance thesis, now visible as a trend.
- **GAUGES**: three-block joint acceptance 0.60–0.66 (predicted 0.55–0.75). ✓

## What was demonstrated

A logical quantum repeater across three [[4,2,2]] shields: A and C never interact; each shakes
hands with the relay (the second handshake via **permuted-wiring transversal CNOT** — SWAP(q1,q2)
is a code automorphism, so crossing the wires targets the relay's other logical qubit at zero
gate cost); one **physical** Bell measurement on the relay's middle pair executes a full
**logical** Bell measurement (the [[4,2,2]] map collapses X̄₁X̄₂, Z̄₁Z̄₂ to weight-2 operators on
one pair); and the relay's two classical bits, applied as a software Pauli frame, leave A–C
CHSH-entangled at 22σ. All-transversal, all-terminal, no feed-forward.

## Integration credits (what this flight reused)

- Exp191: transversal-CNOT logical handshake + block prep + operator map
- Exp192: deferred-correction (Clifford consumption) style — no windows
- Exp195c: the information-is-the-active-ingredient falsifier form (bits ignored → effect dies)
- Exp196: CHSH-by-linearity certification machinery, nulls, in-shot √2 control
- C4887 budget rule: third consecutive correct pre-flight call (fail/pass/pass)

Shields arc: UP → PAYS → HANDSHAKE → TRANSPORTER → VERDICT → **FEDERATION**.
