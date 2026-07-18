# Finding — Exp178: THE ECHO THROUGH THE WINDOW — the tax is coherent; one X gate buys certification back

**Cycle**: C4865 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e0a4ineu4c739nrt50`
(15 circuits: 5 arms × ZZ/XX/YY, 8000 shots). The final flight of the composition-tax arc:
Exp175 (tax) → Exp176 (compounds with windows) → Exp177 (decomposed; measurement window dominant)
→ **Exp178: the dominant cost is coherent, and a single mid-point X recovers it.**

## Result

| arm | ZZ / XX / YY | F(Φ+) |
|-----|--------------|-------|
| live | +0.752 / +0.070 / −0.072 | 0.474 — **below the witness** |
| **liveecho** (one X on A and D, mid-point) | +0.751 / +0.653 / −0.664 | **0.767** |
| deferred (Pauli frame) | +0.787 / +0.237 / −0.236 | 0.565 |
| **defecho** (frame + echo) | +0.778 / +0.690 / −0.657 | **0.782** |
| direct | +0.972 / +0.968 / −0.972 | 0.978 |

- **Echo gain +0.293 at 24.8σ (live), +0.217 at 18.3σ (frame-tracked).** Primary and secondary
  both HELD; the pre-registered branch fired at **substantially coherent** (≥+0.10) — the
  measurement-window tax is common-mode quasi-static dephasing on the end qubits, refocused by a
  single simultaneous X at the between-windows midpoint (X⊗X leaves Φ+ invariant: no closing
  gates, no frame change — one gate per spectator, total).
- **Fingerprint textbook-perfect**: ZZ unmoved (0.752 → 0.751); the entire recovery is XX/YY
  (+0.070 → +0.653). Refocused dephasing, nothing else.
- **The headline in operational terms**: tonight's un-echoed live chain FAILED certification
  (0.474 < 1/2). With one echo X per end qubit it certifies at **0.767 — 22σ past the witness**.
  On this hardware, spectator echo through measurement windows is not an optimization; it is the
  difference between a dead link and a strong one.

## Second discovery — the countermeasures overlap (non-additive)

Exp177 priced frame-deferral at +0.093. On an **echoed** chain the frame adds only **+0.015**
(defecho − liveecho). The two fixes were attacking the same coherent noise pool: what the frame
"avoided" (dephasing during the feedforward wait) is largely the same common-mode phase the echo
refocuses anyway. Countermeasure stacks must be priced jointly — their gains do not add.
(Frame tracking remains worth taking: it is free, and it is the only fix for the latency slice
when echo timing is imperfect.)

## Where the arc lands (the night's ledger)

Deficit accounting, tonight's conditions: live 0.474 → +echo 0.767 → +frame 0.782 → ceiling
(no mid-circuit measurement, Exp177) 0.885 → direct 0.978. The remaining 0.10 gap to the ceiling
is the un-echoable share: the middle qubits' window-1 dephasing (their single window cannot be
split around a measurement instruction), non-common-mode components, and any true backaction
remnant. That residual — not latency, not end-qubit dephasing — is now the frontier.

## Ledger (honest accounting)

- Primary HELD (+18.3σ ≥ 3σ). Secondary HELD (+24.8σ). Branch: coherent.
- Bands: live 0.474 ✓ (0.42–0.58), deferred 0.565 ✓ (0.50–0.62), direct 0.978 ✓.
  **Echo gains missed HIGH**: liveecho +0.293 vs band +0.00–0.15; defecho 0.782 vs band
  0.55–0.75 (+0.03 over). After three low misses on window-bearing arms, the first high misses —
  both on echo efficacy. The echo works better than priced; the coherent fraction of the window
  tax is larger than my conservative prior.
- live replicated C4864's degraded conditions (0.474 vs 0.463) — the volatility record extends.

## Fence

One echo design (single mid-point X pair; no XY4/CPMG ladder), one die, one night's conditions —
the +0.29 magnitude is condition-dependent (bigger fade, bigger refocus). The middle-qubit
window-1 dephasing is structurally un-echoable in this circuit form; attacking it needs either
split-window scheduling (pulse-level) or readout hardware. Frame arms remain
verification-equivalent for non-Clifford consumption (Exp177 fence).
