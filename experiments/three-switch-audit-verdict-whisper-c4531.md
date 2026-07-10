# 3-Switch Transpile Audit — VERDICT (Whisper C4531, free / zero QPU)

**Script**: `three_switch_transpile_audit.py` · **Data**: `results/three_switch_audit.json`
**Question** (roadmap T1.2): does an N=3 switch fit the depth budget, and does its payoff
survive transpiled depth on Heron heavy-hex?

## Cost table (routed, representative ops X,Y,Z; seeds pinned)

| Construction | 2q (opt3) | depth | Verdict |
|---|---|---|---|
| **Cyclic 3-switch** (2-qubit control, 3 cyclic orders, 9 CC-U) | **92** (both marrakesh+fez targets) | ~332 | **FEASIBLE — with window gating** |
| Full 6-order switch (3-qubit control, 18 CCC-U) | 341 | 1323–1788 | **NOT this hardware generation** |

Consequence: the Fourier-promise **scaling** separation (needs the full N!-order switch) is
postponed to a future generation or a smarter construction. The cyclic subgroup is the
practical N=3 object.

## Payoff (derived BY SIMULATION — same method as Exp106, noiseless = exact target)

Cyclic-3 capacity activation, three completely depolarizing channels (64 Pauli triples pooled
= exact 3-channel twirl; causal value exactly 0 by channel algebra):

| | R̄ | MI (bits) | null |
|---|---|---|---|
| Noiseless (exact) | **+0.6730** | **0.0833** | 0 / 0.00000 |
| FakeMarrakesh @ ~92–110 CZ | +0.5183 ± 0.0054 | 0.0485 | 0 / 0.00000 |

**MI grows with N: 0.0489 (N=2, Exp106 measured 0.0436) → 0.0833 (N=3, +70%)** — consistent
with arXiv:2004.14339 (exact literature cross-check at pre-reg; our number is decoder-specific
MI, a lower bound on Holevo). Physics validation en route: for ops (X,Y,Z) all three cyclic
products equal −i·𝟙, and the circuit returns |000⟩ with probability 1 — confirmed exactly.

## The strategic point: this payload NEEDS Bridge 2

92 CZ sits in the **F81 calibration-window lottery zone** (the 124-CZ deep loader swung
err 0.154 → 0.0003 between windows; FakeMarrakesh missed the good window by 400×). Per the
C4530 depth-stratification rule, the FakeMarrakesh number above is a *planning input, not a
promise*. A cyclic-3 hardware run is therefore the first experiment where the sentinel-gated
window-harvesting pipeline (bridges doc §2) is load-bearing rather than insurance:
co-batch a shallow-2q sentinel + the payload, grade the window first, NO-TEST on bad windows.

## Recommendation (proposed Exp107, pending Creator/budget)

Cyclic-3 capacity activation on marrakesh: 64 triples × 2 inputs switch + null arm +
F77 sentinel triplet + **a deep-retention sentinel** (Exp101 Rec#5 class — the F77 4-CZ
sentinel cannot certify a 92-CZ window; this is the Exp100/101 lesson applied forward).
~130 PUBs ≈ 30–50s. Win condition: R̄ − 5·SE > 0.10 with null dead, same frozen-rule family.
Prediction would carry genuine uncertainty (the lottery zone is the point) — expected verdict
distribution: WIN in a good window / NO-TEST in a bad one, and EITHER outcome feeds F82's
window-statistics line. Budget note: ~75–90s remain; this fits, or waits for refresh.

## Engineering traps hit (banked for the network)

1. `StatePreparation(...).inverse()` **core-dumps** qiskit-aer in this env — use explicit
   self-inverse gate prep (Ry + X-sandwiched CH).
2. Raw `qc.unitary(...)` gates trigger a transpiler **panic** ("unitary result from an
   EquivalenceLibrary is not possible") under basis translation — native gates only
   (V_X = H, V_Y = S·H) in anything that transpiles against a target.
