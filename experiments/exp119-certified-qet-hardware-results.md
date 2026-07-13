# Exp119 — Certified QET: HARDWARE RESULTS

**Whisper C4640.** Job `d9a9ma8tcv6s73do74r0` (C4639 freeze, 12 pubs, 340k shots,
ibm_marrakesh pair (3,4)), graded by the FROZEN grader `scripts/grade_exp119.py`.
Grade record: `results/exp119_grade.json`.

## VERDICT (as frozen, no softening): **FAIL-EXISTENCE** on the LOCC headline

The feedforward arm did not certify energy teleportation. Predictions P1 (0.75) and
P2c (0.65) graded **MISS**; P2 (0.50) resolved no; the record keeps the losses next
to what was won.

| Arm | E_B raw | E_B corrected | Theory |
|---|---|---|---|
| ground | +0.0979 ± 0.0096 | +0.0409 | 0 |
| **qet_ff** (LOCC headline) | **+0.1199 ± 0.0086** | +0.0602 | −0.1147 |
| qet_def (coherent, diagnostic) | **+0.0279 ± 0.0082** | **−0.0341** | −0.1147 |
| scrambled control (pooled fix±θ) | +0.2191 ± 0.0070 | — | +0.109 |

Gates: G0 clean (valid test). **W1a MISS** (ff sits +0.022 ± 0.013 ABOVE ground —
needed 5σ below). **W1b WIN** (ff is −0.0993 ± 0.0111 below the scrambled-message
control ≈ 9σ). W2/W2c MISS for the ff arm.

## What actually happened — the pre-registered D1 diagnostic isolates it

The prereg's "what would make this wrong" section named this exact failure mode at
freeze: *"If feedforward latency decoheres B before the conditional rotation fires,
qet_ff degrades toward the fixp/fixm arms — DETECTABLE as W1b shrinking while
qet_def stays deep."* That is the observed pattern, sharpened:

- **D1 = E_B(ff) − E_B(def) = +0.092**: the classical feedforward round-trip costs
  ~0.09 energy-units of decoherence at B — nearly the ENTIRE 0.115 extraction
  budget. The sim predicted the opposite ordering (def noisier by gate count);
  hardware inverted it because **FakeMarrakesh executes `if_else` at zero latency**
  → friction report 05 filed.
- **The message still did real thermodynamic work**: W1b at ~9σ means using Alice's
  actual bit beats ignoring it by 0.099 E — information-conditioned extraction is
  REAL on this hardware; it just doesn't overcome the latency tax in the LOCC arm.
- **The coherent arm nearly certifies the exotic-matter leg**: corrected
  E_B(def) = −0.0341 ± 0.0082 = 4.2σ below zero — and by the one-sided-safety
  argument (all noise pushes E_B UP), the measured value is an UPPER BOUND on the
  true local energy. It misses the frozen 5σ bar (upper bound crosses zero by
  +0.007) and qet_def was pre-registered as DIAGNOSTIC ONLY — so **no promotion,
  no certification**. It stands in the record as a 4.2σ near-miss on a
  non-headline arm.

## Books (demon ledger, reported)

E_A deposit confirmed: +0.7399 measured vs +0.7071 theory (ground E_A = −0.0004 —
the baseline is exquisite). LOCC extraction efficiency: **negative** (−0.16) — the
ff arm *cost* energy. Readout assignment: F ≈ 0.989–0.997; correction removes about
half the positive bias; the residual (+0.041 on corrected ground) is prep/gate
decoherence — the corrected-absolute path carries ~0.04 apparatus bias, stated.

## What this buys us

1. **A measured price for classical latency in energy units**: 0.092 E per
   feedforward round-trip on Heron r2 — the F90 feedforward-cost family gains a
   thermodynamic member. Nobody quotes this number; we just measured it.
2. **The information-thermodynamics core survived**: message-correlated vs
   message-scrambled = 9σ. The Maxwell-demon reading of QET is hardware-real.
3. **A power-calculated retest path — Exp119b proposal**: make the COHERENT
   extraction the headline with scope-honest framing ("certified negative local
   energy via coherent-controlled extraction" — NOT LOCC QET; different, weaker,
   still the exotic-matter deliverable). c4130_001 power calc: corrected dip
   −0.0341, need 5σ < 0.034 → SE ≤ 0.0068 → ~90k shots/pub gives SE ≈ 0.0047
   (margin 1.4×). 6 pubs, one cheap job. Freeze on a fresh cycle per rule.

**Prediction grades**: P1 MISS (0.75 → no), P2 no (0.50), P2c MISS (0.65 → no),
P3 correctly no. The overconfident leg was the LOCC arm's noise budget — the sim's
zero-latency feedforward was the bad prior, now instrumented (friction 05).
