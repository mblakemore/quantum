# Exp249 (H7-P1) — PRE-REGISTRATION: THE SELF-PRESCRIBING SHIELD (the EMH)

**FROZEN before submission. Whisper C4956, substrate claude-fable-5. Creator go: "fly the next one"
(2026-07-21). Builder + grader frozen together: `experiments/exp249_emh_shield.py`; reuses the
CERTIFIED Exp216 instrument (`circuit`, `_stats`) verbatim — no retuning.**

## Claim (closed loop: diagnose → prescribe → verify, one job)
An in-job mini-scan re-measures the [[4,2,2]] coherent-error transfer function same-window; the FROZEN
prescription rule ("store/read the logical bit in the diagnosed noise axis's own basis") then
neutralizes an injected Z-axis coherent noise that the mis-prescribed orientation accepts silently.
**Refinement over the H7 plan (disclosed)**: per the certified 216 geometry the prescription grants
IMMUNITY (transparent axis), not merely detection — the plan's "fires the detector" mechanism is
superseded by the stronger "own-axis transparency" one, frozen here pre-data.

## Flight
`ibm_fez`, 10 pubs × 8,000 shots, static, transpiled 2q ≤ 8 (asserted): scan_X/Y/Z (X-readout, t=0.5;
scan_Z doubles as ALIGNED@0.5) + aligned_25 + presc_25/50 (Z-readout under the SAME Z-noise) +
clean_X/Z + bare_25/50. Est. 30–60 s of 4,054 s remaining.

## Frozen gates
- **G_SCAN** (diagnosis valid same-window): A(X,Z,.5) ≥ 0.8 AND L(X,Z,.5) ≥ 0.5 AND P_silent(X,X,.5)
  ≤ 0.15. If it fails → **NO-DIAGNOSIS**: prescription arms are NOT graded (drift/stability finding).
- **G1** (prescription works): L(Z,Z,t) ≤ 0.10 at both t AND [L(X,Z,.5) − L(Z,Z,.5)] > 5·se.
- **G2** (no acceptance tax): A(Z,Z,.5) ≥ 0.8.
- **G3** (noise is real): bare corruption@π/2 ≥ 0.4.
- **PASS-PRESCRIPTION** = all four. Ideal values (PD-1, statevector-exact): aligned L=0.75 @ A=1.0;
  prescribed L=0.000 @ A=1.0; bare 0.5; separation 155σ at these shots.

## Pre-filed prediction (before any data)
**PASS-PRESCRIPTION, confidence 0.8.** Predicted: scan shows Y,Z blind / X transparent (216 replicated
same-window); L_aligned(.5) ≈ 0.55–0.70; L_prescribed ≤ 0.05 both doses; A_prescribed ≈ 0.85–0.95;
bare ≈ 0.47–0.52. **Named failure modes**: (i) G_SCAN fails (the transfer function drifted off the
216 calibration) → NO-DIAGNOSIS, itself a stability datum; (ii) prescribed arm corrupts > 0.10 →
own-axis transparency fails off-calibration-day — a major boundary finding for the 216 rule, kept with
full weight.
