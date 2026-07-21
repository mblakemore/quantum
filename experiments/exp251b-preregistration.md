# Exp251b (H7-P3 redo) — PRE-REGISTRATION: THE LIVE-CORRECTED PATTERN BUFFER

**FROZEN before submission. Whisper C4964, substrate claude-opus-4-8. Creator directive: "redo P3 as the
in-circuit Exp251b." Builder+grader frozen together: `experiments/exp251b_pattern_buffer_incircuit.py`.**

## What Exp251 got wrong, and the two fixes
Exp251 (NO-ADVANTAGE) had TWO errors, both corrected here: (1) it used OFFLINE decode, which cannot
re-pump a decaying memory — replaced with Exp241's ACTIVE in-circuit `if_test` feed-forward; (2) it
compared the code to a BARE single qubit, which unfairly charges the code its whole encoding overhead —
replaced with the **Exp241 confound-free comparison: corrected vs SHAM** (the identical circuit —
teleport, encode, rounds, mid-circuit measure, reset — minus ONLY the fix). The sham isolates the
correction's value from its machinery.

## Claim
Exp241 certified corrected > sham for a held |1_L⟩ (gain growing to +0.34 at R=4). Exp251b asks whether
that live-correction advantage SURVIVES the teleport front-end: is teleport+corrected > teleport+sham?

## Flight
`ibm_fez`, 7 pubs × 8,000 shots, DYNAMIC (`if_else` feed-forward, verified on fez), τ=30 µs/round.
Teleport |1⟩ (frame-deferred) → encode → R∈{3,4} rounds of {idle → syndrome → if_test fix → reset} →
read logical Z + offline teleport frame. Transpiled 2q ≤ 45 (asserted). Est. 40–70 s of 3,949 s.

## Frozen gates
- **G_CORRECTION** (primary, Exp241-style): F(tp_corr) − F(tp_sham) > 5·se at R=3 **or** R=4 (the gain
  grows with R). Sham = identical machinery, correction off.
- **G_SEAM**: F(tp_immediate) > 0.90.
- **LIVE-BUFFER-CERTIFIED** = both. Reported: bare single-qubit reference (the overhead-charged compare).

## PD note (honest — the sim cannot validate this)
Noiseless PD-1: pipeline+frame exact at R=4 (logic verified). A crude thermal-relaxation sim (T1=90/T2=60
µs) shows NO gain — but that same sim FAILS to reproduce Exp241's known real-hardware gain (+0.12/+0.34
at R3/R4), so it is not a valid predictor here. Real fez T1 is the only arbiter; this is deliberately a
hardware-decided composition question, not a sim-confirmed one.

## Pre-filed prediction (before any data)
**Genuinely uncertain — confidence 0.5.** Exp241's corr>sham gain exists on real hardware and peaks at
R=4; the teleport front-end (~3 CZ + Bell measurement) adds depth that may or may not suppress it.
Predicted: G_SEAM holds (>0.90); G_CORRECTION more likely at R=4 than R=3 if it holds at all. **Named
outcomes, both kept with full weight**: (i) LIVE-BUFFER-CERTIFIED — Exp241's advantage composes with
teleportation (the P3 deliverable, properly done); (ii) NO-CORRECTION-GAIN — the teleport depth
suppresses the correction advantage (an honest composition-tax boundary, completing the Exp251 story).
