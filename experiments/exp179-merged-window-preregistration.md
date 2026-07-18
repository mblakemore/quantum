# Exp179 Pre-registration — THE MERGED WINDOW: window-count architecture + engineered Hahn

**Cycle**: C4866 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 15 circuits
**Attacks**: the Exp178 residual (0.10 gap from best stack 0.782 to no-window ceiling 0.885) —
specifically the un-echoable middle-qubit window share and the ends' remaining window dose.

## The architectural insight

With Pauli-frame tracking (Exp177), the second swap's *gates* never depend on the first swap's
*outcomes* — sequencing was only ever forced by live feedforward. So the chain can be
restructured at circuit level, no pulse access needed:

1. **Merge the windows**: run both Bell-basis rotations first, then measure ALL FOUR middles in
   one simultaneous window. Window count 2 → 1, and the middles never idle through a measurement
   window at all (they are measured *in* it). Statistically identical to the sequential deferred
   chain (deferred-measurement principle — measured qubits touch nothing afterwards); only the
   *schedule* differs. Hardware, not simulation, decides what that schedule is worth.
2. **Engineered Hahn on the single window**: one window has no "between-windows midpoint," so
   build the symmetric arm explicitly: after the merged window, X(ends) → delay(≈ measurement
   duration, from backend timing, granularity-rounded) → X(ends). Ends' window phase φ_w is then
   cancelled by the matched delay (quasi-static coherence proven in Exp178). XX = I: no state or
   frame change.

## Arms (one job, frame-tracked throughout, ZZ/XX/YY; roles as Exp177/178)

| arm | windows | echo | purpose |
|-----|---------|------|---------|
| seq | 2 (sequential) | no | Exp177-deferred replica — baseline |
| seqecho | 2 | midpoint X pair | Exp178-defecho replica — current best stack |
| **merged** | **1 (merged)** | no | the architecture claim |
| **mergedecho** | 1 | X–delay(w)–X | the new candidate best stack |
| direct | 0 | — | floor |

Frame algebra identical to Exp177 for all arms (same gates, same measured bits, same
x=c3⊕c1 / z=c2⊕c0 on D) — selftest must prove all arms exact noiseless.

## Pre-registered predictions

- **Primary**: F(merged) − F(seq) > 0 at ≥3σ — halving the window count pays (Exp176
  dose-response, applied as architecture).
- **Secondary**: F(mergedecho) − F(seqecho) > 0 at ≥3σ — new best stack, approaching the 0.885
  ceiling.
- **Bands**: seq 0.50–0.62 · seqecho 0.70–0.82 · merged 0.68–0.82 · mergedecho 0.75–0.88 ·
  direct 0.95–0.99.
- **Open comparison, no confident prediction** (stated as genuine uncertainty): merged vs
  seqecho — window-halving+middle-sparing vs end-refocusing-across-both-windows. Either ranking
  is informative about where the residual actually sits (middles vs ends).
- **Fingerprint**: gains XX/YY-concentrated, ZZ flat (the arc's signature).
- **Named risk**: the engineered delay may be reflowed/mismatched by the transpiler; if
  F(mergedecho) ≈ F(merged), first suspect delay placement (check scheduled durations), not
  decoherence class — Exp178 already proved the coherence.

## Discipline

ps aux: clean. Coordination claimed exp179 (whisper C4866). Prereg committed before decode.
DECIDE-time prediction logged to the ledger BEFORE submission this cycle (closing the
C4864/C4865 fast-cycle gap).
