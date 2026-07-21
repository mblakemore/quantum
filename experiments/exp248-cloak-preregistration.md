# Exp248 (H7-P2) — PRE-REGISTRATION: THE CLOAKING DEVICE — QEC-as-privacy on silicon

**FROZEN before submission. Whisper C4952, substrate claude-fable-5. Creator go: "A and B go" (2026-07-21).
Builder+grader frozen together: `experiments/exp248_cloak.py` (grader written before any data).**

## Claim
Every single physical qubit of a [[4,2,2]]-encoded logical state is information-free about the logical
bit (Holevo χ from reconstructed per-qubit tomograms, bounding EVERY single-qubit measurement), while
the owner reads the logical bit at high fidelity — and the cloak measurably breaks at the pre-identified
two-qubit probes (the d=2 edge: pair (0,2) in Z carries Z̄1; pair (0,1) in X carries X̄1).

## Flight
`ibm_fez` (fallback marrakesh if fez unavailable), 14 pubs × 8,000 shots, static, transpiled 2q ≤ 6
(asserted in-code): 4 logical states {|0L⟩,|1L⟩,|+L⟩,|−L⟩} × 3 bases {Z,X,Y} + 2 readout-mitigation
cals. Stabilizer postselection per basis (even parity). Est. cost ~40–60 s of the 4,109 s remaining.

## Frozen reading rule (implemented in `grade()` before flight)
- **PASS-CLOAK**: max_q χ_single(mitigated) < 0.01 bit AND min logical readout F > 0.9.
- **PASS-EDGE**: min pair-probe MI > 5 × max(χ_single, 1e-4).
- **PASS-CLOAK+EDGE** = both. **CLOAK-LEAK** if F > 0.9 but χ ≥ 0.01 (a real, quantified privacy leak
  of physical hardware — reported as the finding). **READOUT-FAIL** if F ≤ 0.9 (no cloak claim either way).
- Raw AND mitigated χ both reported; grading on mitigated (G7). All-bit grading: every pub's acceptance
  fraction + all 4 single-qubit tomograms + both pair MIs are in the card by construction.

## PD gates (all passed pre-freeze)
PD-1 sim-exactness: per-qubit reductions = I/2 for all 4 states (χ=0 to 1e-9), logical readouts exact,
pair probes = 1.0 bit, grader returns PASS-CLOAK+EDGE on ideal counts. Depth assert ≤ 6 transpiled 2q.

## Pre-filed prediction (before any data)
**PASS-CLOAK+EDGE, confidence 0.75.** χ_single(mit) predicted < 0.005 bit (readout asymmetry is the
main leak channel and mitigation should hold it under 0.01); F_logical ~0.93–0.97 (3-CZ encodes at
Heron error rates, postselected); pair edges ~0.5–0.8 bit (attenuated from 1.0 by the same errors).
**Named failure modes**: (i) crosstalk/readout asymmetry pushes some χ_q ≥ 0.01 → CLOAK-LEAK, reported
as the measured privacy leak of real silicon (a finding, not a spin); (ii) acceptance < 50% on Y pubs
(YYYY postselection is the fragile one) → statistics thin, se's widen, reported plainly.
