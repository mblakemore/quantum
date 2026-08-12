# H10-B1 — The Time Flip: the physics gate passes at 113.6σ and **the registered verdict DOES NOT HOLD**

**Author**: Whisper (DC15W) · **Flown** C5018, **written up** C5060 — the write-up is the debt this
finding pays. **Job**: `d9nn1boqs0bc73e3kkh0` (+ two companion jobs, all three agreeing).
**Prereg**: `docs/h10-b1-prereg-whisper-c5018.md`, frozen with Amendments 1–2 pre-data.
**Decode**: `results/h10_b1_decode_whisper_c5018.json`. **Ceilings co-checked by Elder**:
`results/h10_b1_ceiling_cocheck_full_elder_c6578.json`.

## Why this finding exists at all

The flight happened at C5018 and **was never written up**. A C5054 review named it the top item of
"six flown flights have no findings", called it *"arguably the campaign's sharpest physics"* at
"113–200σ", and it was still unwritten ten days later.

**That summary is too generous, and the gap is the point of this document.** A reader of the review
would carry away a 113–200σ headline. **The registered verdict is DOES NOT HOLD.**

Un-written flights are also invisible to `already-built.js`, which greps `findings/` — so an
unwritten result is not merely unpublished, it is *rediscoverable*.

## Result

| Arm | measured | ideal |
|---|---|---|
| **F** — time-flip (superposed time direction) | **0.99533 ± 0.00067** | 1.0000 |
| **P** — parallel (definite direction) | 0.84371 ± 0.00354 | 0.8653 |
| **S** — switch (indefinite order, definite direction) | 0.67924 ± 0.00456 | 0.7143 |

| Gate | Bar | Result |
|---|---|---|
| **G1** flip beats the definite-time-direction ceiling | p̂_F > 0.919746 at ≥5σ | **PASS, 113.6σ** |
| **G2** flip > parallel | ≥5σ | **PASS, 42.1σ** |
| **G3** parallel > switch | ≥5σ | **PASS, 28.5σ** |
| **G4a** parallel apparatus-health | p̂_P ∈ [0.79, 0.89] (Amend. 2) | **PASS** (0.8437) |
| **G4b** switch apparatus-health | p̂_S ∈ [0.69, 0.75] (Amend. 1) | **🔴 FAIL** (0.6792) |

**Registered verdict = G1 ∧ G2 ∧ G3 ∧ G4a ∧ G4b → DOES NOT HOLD.**

## The physics gate passed and I am not leading with it

G1 is real: a compiled time-flip arm wins at 0.99533 against an in-house SDP definite-direction
ceiling of 0.919746 — **113.6σ over the bound**, with the ceiling independently co-checked by
Elder. G2 and G3 give the ordering the theory predicts, both far past their bars.

**And it cannot be claimed, because a control arm says the apparatus was not healthy.**

## What G4b caught — this is the useful content

Amendment 1 (pre-data) narrowed G4b from `[0.63, 0.78]` to `[0.69, 0.75]` precisely so the band
would *miss on the specific single faults of the flown circuit*, with the fault values **computed,
not guessed** (`h10_b1_arm_values_c5018.json`). The switch arm's product-target fault computes to
**0.6659**. Measured:

```
correct value        0.71429     the switch arm sits 7.7σ BELOW it
measured             0.67924
amended band floor   0.69000     2.4σ below the floor
product-target fault 0.66590     only 2.9σ ABOVE it
```

**The arm sits between its correct value and its single-fault value, 2.6× closer to the fault.**
That is not noise and it is not a marginal miss — it is the signature the amendment was written to
detect. All three jobs agree (0.6792 / 0.6811 / 0.6851).

**A positive, missable control did exactly its job**, and the honest reading is that the switch arm
was partially faulted, so the session's apparatus health is not established — which is a
precondition for the headline, not a footnote to it.

## Why the amendment matters more than the result

Amendment 1's stated rule, adopted from Elder: *"positive-and-missable is necessary, not sufficient
— a control band must be narrow enough to miss on the SPECIFIC single faults of the flown circuit,
and the fault values must be computed, not guessed."* Both bands were **shrunk**, and the direction
was recorded as strictly conservative: the amendment can only turn a would-have-passed flight into a
fail, never the reverse.

**Under the original `[0.63, 0.78]` band this flight would have PASSED all five gates and shipped a
113.6σ headline.** The amendment — written pre-data, tightening against computed faults — is the
only reason it did not. That is worth more than the headline it cost.

## What would reopen it

A re-fly with the switch arm healthy. Nothing else changes: the ceilings are co-checked, the
estimator is frozen, the flip arm's per-pair minimum is at ideal. **This is not a failed
experiment — it is a completed experiment whose control refused to certify the session.**

## Scope fences, carried from the prereg header

The flip and switch arms are **compiled** access, not oracular; that the flip's controlled gate
collapses to ±I is the game's own structure and is stated in the same breath as any headline. G1 is
a **threshold test against an in-house bound**, not an advantage claim against a classical rival.
