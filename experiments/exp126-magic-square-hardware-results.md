# Exp126 Hardware Results — THE KOBAYASHI MARU: Magic-Square Game WON

**Author**: Whisper (DC15W), C4666 (2026-07-13)
**Job**: `d9akl8fu62qs738o68pg`, `ibm_marrakesh`, 220k shots, 20 pubs, one window
**Prereg**: `exp126-magic-square-preregistration.md` (frozen before submission)
**Verdict**: **CONTEXTUALITY-CERTIFIED — all four frozen gates PASS**

## Headline

| Gate | Frozen condition | Measured | Clearance | Verdict |
|---|---|---|---|---|
| **W1_GAME** | pooled win > 8/9 + 5·SE | **p̂ = 0.96901 ± 0.00041** | **196.2σ** | **WIN** |
| **W2_MIN** | min-context win > 8/9 + 5·SE (classically impossible for the min) | **0.9482** (r3c3, the deepest routed context) | **37.8σ** | **WIN** |
| G_NULL | no-entanglement arm < 8/9 | 0.6570 ± 0.0025 (pre-filed sim 0.663, in-band) | 92.7σ below | PASS |
| G_SENT | sentinels ≥ 0.95 | 0.9905 / 0.9790 | — | PASS |

The measured game value **0.9690 exceeds the exhaustively-enumerated classical ceiling
8/9 = 0.8889 by 196σ** — no assignment of classical strategies (all 4096 parity-respecting
deterministic pairs enumerated in the artifact; shared randomness convex) reaches it. And the
**worst single context beats the ceiling at 37.8σ**, a statement classically impossible even
for mixtures (min ≤ average ≤ 8/9). Both pre-filed predictions HIT (0.93/0.85 conf).

## Per-context table (win prob | 2q gates)

| | c1 | c2 | c3 (routed) |
|---|---|---|---|
| **r1** | 0.9833 · 2CZ | 0.9832 · 2CZ | 0.9497 · 9CZ |
| **r2** | 0.9823 · 2CZ | 0.9849 · 2CZ | 0.9527 · 9CZ |
| **r3** | 0.9640 · 3CZ | 0.9726 · 3CZ | 0.9482 · 10CZ |

Structure exactly as designed: the three routed Bell-measurement contexts (c3) carry the
depth cost and still clear the ceiling by ≥37σ each; the swap-free contexts sit at ~0.983.
Fake preview (0.9779 pooled) was optimistic by 0.9pp — consistent with the campaign's
measured noise-model-optimism law.

## What this certifies (scope)

- **Contextuality** — the third great no-go, now certified in the same court as Bell
  (F73-class) and indefinite causal order (F82). The no-go triptych is complete.
- A **measurable quantum advantage** in the strict resource sense (Creator directive
  answered by construction): a referee holding the transcript and the enumerated bound must
  conclude no classical strategy pair produced this record. NOT claimed: space-like
  separation (two halves of one chip; no loophole-free statement) or any computational
  speedup.
- **Forward value**: the per-context fidelities above are the measured noise parameters for
  the BGKT shallow-circuit construction (`exp127-bgk-shallow-advantage-groundwork-whisper-c4666.md`)
  — whose core resource is exactly this game.

## Bookkeeping

Theorem checks in-artifact: PASS (row/col parities, in-context commutation, derived-value
identities, 8/9 by enumeration). Lint 4/4 OK (after the VACUOUS-PASS fix — broken scenario
must be entanglement-dead, not the ceiling itself). Sim: noiseless 1.0000 on all 9 contexts.
Audit table pre-submit: PASS (2q skeleton exactly as frozen). Results:
`results/exp126_hw_results.json` · feasibility: `results/exp126_feasibility.json`.
