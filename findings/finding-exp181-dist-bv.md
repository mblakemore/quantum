# Finding — Exp181: THE DISTRIBUTED COMPUTER — BV across a cut at 0.914, and the tax vanishes without windows

**Cycle**: C4869 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e28tcjeosc73fi8fi0`
(12 circuits: {local, dist, noresource} × 4 hidden strings, 8000 shots). The campaign's first
**distributed computation**: Bernstein–Vazirani with Alice's data register and Bob's oracle
ancilla never touching — every oracle CNOT teleported (EJS) over pre-shared e-bits.

## Result

| arm | s=00 | 01 | 10 | 11 | avg(01,10,11) | modal |
|-----|------|----|----|----|----------------|-------|
| local (monolithic ceiling) | 0.995 | 0.970 | 0.964 | 0.912 | 0.949 | 4/4 |
| **dist (teleported oracle)** | 0.992 | 0.923 | 0.920 | 0.897 | **0.914** | **4/4** |
| noresource (falsifier) | 0.993 | 0.502 | 0.486 | 0.244 | 0.411 | wrong on 10, 11 |

- **PRIMARY HELD at absurd margins**: dist beats the falsifier +67σ / +68σ / +111σ per string,
  **+141σ** on the average; the distributed computer read the right hidden string as the top
  outcome for **all four programs**. One query each, as BV requires.
- **Distribution cost: 0.035** — the fully-distributed algorithm (2 cross-cut teleported gates
  at worst) runs within 3.5 points of the monolithic machine.
- **Falsifier = the classical guessing bound, exactly**: without e-bits every gate-bearing
  readout bit is a coin flip — measured 0.502 / 0.486 / 0.244 against theory 0.5 / 0.5 / 0.25.
  The floor of the "no quantum resource" impostor is a theorem, and the data sat on it.

## The architecture (why this worked so well) — and the tax closing its loop

Design discovery, selftest-proven before flight: for BV the **entire EJS correction structure
defers out of the circuit**. The X^x correction lands on Bob's ancilla in |−⟩ — an X eigenstate —
so it is a global phase, dropped entirely (phase kickback absorbs it). The Z^z correction
commutes through Alice's final H into a classical XOR at decode (s_i = m_i ⊕ z_i). Net: **zero
live feedforward, zero mid-circuit measurement** — one merged final layer (Exp179's architecture
applied to computation). No gate ever waits on a cross-cut message; classical communication
exists only in post-processing.

The payoff shows in the arc's sharpest cross-check: **P(11)/P(10 or 01) = 0.971 — the second
teleported gate costs ~3%.** Compare the window-laden compositions: Exp176's second swap cost
~45% (per-stage ratio 0.55), Exp175's stack paid a −3.4σ super-multiplicative tax. Here, with
no windows anywhere, teleported gates compose almost freely. **The composition tax was never
about stacking quantum operations — it was entirely the feedforward/measurement windows** —
confirmed now from both sides: dose-response when windows are present (176), near-free
composition when they are absent (181).

## Ledger (honest accounting)

- Primary, modal 4/4, falsifier bands, local bands, noresource bands: all HELD.
- **dist beat its band HIGH** (avg 0.914 vs 0.68–0.88; s=11 0.897 vs 0.62–0.85) — third
  high-miss of the campaign, same direction, same lesson (C4865): I persistently underprice
  window-free architectures. Calibration note: for zero-window designs, price from per-CX gate
  error alone (~1–2% per teleported gate + routing), not from any window-bearing precedent.
- Per-gate truth-table comparison: Exp170's live EJS gate read 0.870; here each deferred gate
  effectively contributes ≥0.95 — the windows were most of Exp170's gate cost too.

## Fence

n=2 BV (4 hidden strings) on one die — patches, not physically separated processors; e-bits are
pre-shared resources (the standard distributed model, stated openly). The zero-communication
property is BV-specific in its strongest form (target = phase-kickback eigenstate ⇒ X-corrections
free; Clifford consumption ⇒ Z-corrections defer): algorithms with non-Clifford post-oracle
structure need live corrections and would re-enter window territory (priced by Exp177/178).
The one-query advantage claim is about the oracle-query count, not wall-clock speedup.

## Where this leaves the wing

The network wing now demonstrates, end-to-end and certified: state teleportation → gate
teleportation → computing over a relay → keys through untrusted relays → **a distributed
algorithm at 96% of monolithic performance**. Eight flights this campaign arc (175–181), every
one pre-registered, every falsifier on script.
