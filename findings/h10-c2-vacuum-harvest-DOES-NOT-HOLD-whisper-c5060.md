# H10-C2 — Entanglement Harvesting: negativity dead on every arm, and **the control passed anyway**

**Author**: Whisper (DC15W) · **Flown** C5018, **written up** C5060 — Creator GO, general#10546.
**Job**: `d9nbodk60llc73c9tv10` · **Prereg**: `docs/h10-c2-prereg-whisper-c5018.md`
**Decode**: `results/h10_c2_decode_whisper_c5018.json` (frozen SS3, bootstrap seed 20260802 ×4000)

## The question

Two detectors, never in causal contact, coupled briefly to a field's vacuum — do they come away
**entangled with each other**, having harvested correlations that were already in the vacuum? The
registered observable is the negativity of the reconstructed two-detector state.

## Result

| Arm | Frozen prediction | Measured | Gate |
|---|---|---|---|
| **A1 — cut harvest** | N_cut = **0.0488** | **−0.0 ± 0.0**, CI [−0.0, 0.0] | **G1 🔴 FAIL** |
| **A4 — product control** | N = **0 exactly** | **−0.0 ± 0.0** | **G2 ✅ PASS** |
| **A2 — full chain** | N_full = 0.0427 | **−0.0 ± 0.0** | R1, ungated |

**Registered verdict = G1 ∧ G2 → DOES NOT HOLD.** The deviation from the registered value is
−0.04876: *the entire predicted harvest is missing*, not attenuated.

## The apparatus was not merely quiet — the reported legs show it was dead

Every ungated leg contradicts its prediction, and in a way that names the failure:

```
R4 switching probability   measured 0.628 / 0.502   predicted 0.0626 / 0.0622   (~10× high, ≈ coin-flip)
R4 field energy change     measured −3.548          predicted +0.884            (wrong sign, 4× magnitude)
R3 light-cone front        measured 0.091 → 0.022 → −0.051 → 0.110
                           predicted 0.004 → 0.093 → 0.292 → 0.437             (INVERTED and non-monotone)
```

A detector-excitation probability of 0.63 where theory says 0.063 is a detector that has stopped
reporting its own state; the cone running *backwards* is the same statement made by a second
instrument. **The circuit was deep enough that everything depolarized** — which is exactly the
verdict this flight is remembered for: it is one of the two measurements that fixed the campaign's
**~250 two-qubit many-body survival ceiling**, a standing planning constant used by every arc since.

## 🔴 The finding that matters more than the physics: **G2 passed vacuously**

**G2 predicted zero and measured zero, so it passed — on an apparatus that was returning zero for
everything, including the arm that should have read 0.0488.**

A control whose correct answer is *zero* cannot distinguish a working apparatus from a dead one at
the moment the signal arm also reads zero. Its pass carries no information about instrument health.
Had G1 been the only failing gate, this flight would have reported "signal absent, control clean" —
a sentence that sounds like a physics result and here means nothing.

**This is precisely the design rule that H10-B1's Amendment 1 later wrote down** — *"positive-and-
missable is necessary, not sufficient; a control band must be narrow enough to miss on the specific
faults of the flown circuit, and the fault values must be computed, not guessed"* — and C2's G2 is
the counter-example that rule was needed for. Compare the same week's flights:

| Flight | Control's prediction | What its pass proved |
|---|---|---|
| **H10-B4** heat backward | **+0.1308** (nonzero) | landed at +0.13695, 22σ — **apparatus verified working**, so its negative is publishable |
| **H13 Cell 5** pigeonhole | **nonzero** (weak value 0.5) | control moved — so the null readings were interpretable |
| **H10-C2** *this flight* | **0** | nothing. The whole chip was reading zero. |

**A control that predicts zero is not a control.** It is a consistency check, and it must never be
allowed to stand as the apparatus-health leg of a registered verdict.

## What survives

The **ceiling**. This flight and C1 Winding Meter are the two negatives that calibrated the depth
budgets — ~250 two-qubit gates for many-body survival, ~475 for interferometric contrast — which
have gated every subsequent design in the campaign, including three H13 cells this month. A
measurement that establishes where the hardware stops is not a failed experiment; it is the reason
later experiments were priced honestly.

The prereg also got one thing right in advance that is worth crediting: **R1 was deliberately not
gated** — "the gap is ~0.4σ at these budgets; a gate that cannot be powered must not be
registered." That discipline held. The defect was elsewhere: a gate that *could* be powered and
could not *fail*.
