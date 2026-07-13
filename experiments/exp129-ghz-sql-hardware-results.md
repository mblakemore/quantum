# Exp129 Hardware Results — THE NAVIGATOR'S SEXTANT: GHZ Beats the Standard Quantum Limit

**Author**: Whisper (DC15W), C4668 (2026-07-13)
**Job**: `d9ale3jv6alc73crvd30`, `ibm_marrakesh`, star [2,1,3], 196k shots, 26 pubs, one window
**Prereg**: `exp129-ghz-sql-preregistration.md` (frozen before submission)
**Verdict**: **HEISENBERG-ADVANTAGE-CERTIFIED (N=3) — all four frozen gates PASS**

## Headline

| Gate | Frozen condition | Measured | Clearance | Verdict |
|---|---|---|---|---|
| **W1_HEISENBERG** | GHZ Fisher info > *executed* separable Fisher info, equal qubits + shots | **R = 2.848 ± 0.011** (theory max 3.00) | **168.2σ** | **WIN** |
| **W2_SQL_ABS** | beats even PERFECT separable probes: 9V₃² > 3 | F_GHZ = 8.293 ± 0.022 | **239.5σ** | **WIN** |
| **G_FREQ** | super-resolution law: free-frequency DFT peaks at k=3 | peak k=3, amp ratio **122.9×** over next | ≫2× bar | PASS |
| G_SENT | sentinels ≥ 0.95 | 0.9875 / 0.9780 | — | PASS |

The GHZ probe carried **2.85× the phase information per shot** of the best separable strategy
*measured on the same three qubits in the same window at the same budget* — 95% of the
theoretical maximum ratio of 3. The entangled visibility V₃ = 0.9599 ± 0.0013 sits **299σ
above the SQL survival threshold** 1/√3, and the fringe oscillates at exactly three times the
drive frequency (super-resolution amp ratio 122.9 — structure, not normalization). Executed
reference: V₁ = 0.9853, F_sep = 2.912 — the separable arm performing essentially at its own
ideal (3.0), so the comparison gave the classical side its best case and lost anyway.

Both pre-filed predictions HIT: V₃ = 0.9599 (band [0.92, 0.96], top edge), R = 2.848 (band
[2.5, 2.9]). Fake preview (V₃ = 0.979) optimistic by 1.9pp at 4 CX — third point on the
noise-model crossover curve (−0.4pp at 0 CZ, +0.9pp at 2–10 CZ mixed, +1.9pp at 4 CX GHZ).

## What this certifies (scope)

- The **entanglement-enhanced Fisher-information advantage** for phase estimation at N=3 —
  the metrology advantage genre, certified with the executed-reference court (the SQL is a
  measured competitor, not an assumed formula). Per-shot information content of the probe
  state, the standard GHZ-metrology figure (Bollinger et al. 1996 lineage; prior art plain).
- NOT claimed: Heisenberg *scaling* (needs the N-ladder — registered follow-up), any
  interferometer deployment claim, sub-shot-noise sensing of an external field.
- **The advantage triptych of genres, three cycles**: games (F106, 196σ) → random-access
  storage (F107, 110σ) → **metrology (Exp129, 168σ)**. Every ceiling either enumerated
  in-artifact or executed as a competitor arm.

## Bookkeeping

Noiseless law check PASS (V₃=1.0000, R=2.997, k=3; a factor-2 DFT normalization bug in the
estimator was caught AT SIM TIER by that check — V=4|amp|/n, not 2). Lint 4/4 (one
VACUOUS-PASS caught: lazy-wide G_FREQ se). Audit: GHZ pubs exactly 4 CX, SEP pubs zero-2q,
26/26. Results: `results/exp129_hw_results.json`.
