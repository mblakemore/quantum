# Finding — Exp165: PURIFICATION — two pairs below the witness, one certified pair out

**Cycle**: C4855 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dtr24inv1c73aphomg`
(9 circuits: {input, purify, fresh} × 3 settings, 8000 shots; DEJMPS on pairs faded by 10 μs of
plain storage — the wing's own memory decay as the noise source). Completes the repeater
primitive set: swap (162), memory (163), echo (164), **purification (165)**.

## Result

| arm | F(Φ+) | p_success | discard pile |
|-----|-------|-----------|--------------|
| input (one stored pair) | 0.396 | — | — |
| **purify (DEJMPS, kept)** | **0.688** | 0.50 | **−0.171** |
| fresh purify (τ=0 overhead) | 0.905 | 0.94 | 0.284 |

**Gain +0.292 at 20σ.** Half the shots are spent (the sacrificial pair's coincidence
postselection), and the survivors jump from 0.396 to 0.688. The free falsifier is emphatic: the
anti-coincident discard pile reads −0.171 — the protocol demonstrably sorts good from garbage
within the same shots, not merely "improves on average."

## The headline beyond the textbook

This run's input had faded **below the 1/2 witness** (0.396 — not certifiably entangled), yet
the distilled output (0.688) **is certified**. The textbook F > 1/2 purification threshold is a
*Werner-state* statement (depolarizing noise); our storage noise is **structured** — coherent
quasi-static dephasing (Exp163/164 diagnosis) — which DEJMPS is specifically built to filter,
and which the sim truth-gate proved pre-flight (injected Rz: 0.877 → 0.982). Distillation
below the Werner threshold is expected physics for this noise class, and the discard-pile split
(−0.171 vs +0.688) is what the filtering looks like. Fence on the claim: this does **not**
violate any bound — witness-F understates entanglement for coherently-rotated states; the
protocol exploits structure, and would not work at 0.396 Werner fidelity.

## Ledger

- Input band missed low (0.396 vs 0.55–0.68): the pair faded far more than yesterday-evening's
  memory curve — unpinned layout this flight plus the day's condition volatility (C4850 record).
  Gain correspondingly above band (+0.292 vs +0.03–0.12): bigger fade, bigger gain. Mechanism,
  falsifier, and p_success all held.
- The named routing risk did not bite: the router embedded the bilateral CNOTs at 2q-depth 5
  (vs 3 for the input arm) — purification is cheap on heavy-hex at this scale.
- Fresh-pair arm prices the protocol overhead at high F: 0.905 kept vs ~0.93 direct.

## Fence

One die, one round of distillation, structured noise, postselected (p=0.50); a purification
primitive, not a repeater stack. Museum panel queued.
