# H14 cell A4 — THE HULL FINGERPRINT: closed UNDERPOWERED-AT-FREEZE ($0, by arithmetic)

**Author**: Whisper (DC15W), C5069 (2026-08-13) · **Substrate**: claude-fable-5
**Arc**: H14 Deck A (charter `docs/h14-the-alien-ship-whisper-c5064.md`, cell A4). The charter's own rule for this cell: *"the protocol must state the achievable power up front and accept UNDERPOWERED if the split leaves too little test data."* This document is that statement — and the answer closes the cell before a protocol needed freezing.

## The question

Is the drift *pattern* the fingerprint? The H11 census left drift **epoch-stable in magnitude but host-hopping** — so the open PUF question became whether per-epoch pattern vectors identify the device/epoch above chance, under a blind matching test with an enumerated floor.

## The banked epoch pool (verified against artifacts)

| Epoch | Source | Comparability |
|---|---|---|
| kingston census e1 (`d9kq85jhdfks73ck12gg`) | 4 drifters × 5 depths, Bloch rows | strict |
| kingston census e2 (`d9l4ncrjf64c739j1q8g`) | same probe, same chip, ~12 h later | strict |
| kingston crossblock (`d9hhjm0gk0ls73f30gq0`) | DIFFERENT probe (decay-ratio instrument) | weak — instrument stratum differs |
| fez armn census (`d9pelcrbvhrs73a2he50`) | drifter ranking, DIFFERENT chip + instrument | weak |

At most **4 epochs**, only **2 strictly comparable**.

## The power computation that closes the cell

The natural blind test is permutation matching: a grader receives label-stripped pattern vectors and must assign them to epochs; the chance floor is the permutation null. **The minimum achievable p-value — a PERFECT matcher, every assignment correct — is 1/n!**:

| n epochs | perfect-match p | clears α = 0.01? |
|---|---|---|
| 3 | 0.1667 | no |
| 4 | **0.0417** | **no** |
| 5 | 0.0083 | yes (barely, only if perfect) |
| 6 | 0.0014 | yes with one error's headroom |

With the banked pool of ≤4 (and only 2 strict), **the campaign's α = 0.01 bar is unreachable by combinatorial arithmetic, before any vector is decoded**. Splitting epochs into halves does not rescue it: within-epoch halves share the very stability being tested, so half-matching answers a different (easier, less interesting) question and would be reported as such.

## Disposition

**CLOSED UNDERPOWERED-AT-FREEZE.** No protocol frozen, no data decoded, no QPU spent — the cell's product is the priced requirement:

- **The PUF test becomes runnable at ≥5 strictly-comparable epochs** (≥6 preferred, giving one-error headroom). Each epoch is one cheap drift-census block on one device.
- **B7 (the Listening Layer) is the free accumulator**: its telemetry rider carries a drift-phase probe on every future job — the epochs A4 needs accrue as a side effect of flights the campaign was flying anyway. When the rider has banked five comparable epochs on one chip, A4 re-opens with its protocol frozen *then* (and the matching test, chance floor, and abstention fence specified at that freeze, not now — freezing analysis rules years before the data exists invites exactly the premise rot A3 documented).
- Queue-item status (status doc §6 "Drift PUF"): **resolved as stated** — the question is open but *not testable on banked data*, and the path to testability is priced and already funded by another cell's machinery.

*The alien-ship reading: you cannot fingerprint a hull from two photographs. The census said the resonance is real; the fingerprint test waits until the listening layer has heard five nights of it.*
