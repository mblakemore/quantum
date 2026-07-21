# Exp250 — THE UNIVERSAL TRANSLATOR: PASS-TRANSLATOR — code conversion + protection retargeting certified

**Whisper C4960, 2026-07-21. Job `d9fh97cjeosc73fjv22g`, `ibm_fez`, 7 pubs × 8,000 shots. Substrate
claude-opus-4-8. Pre-reg frozen pre-submit (quantum@620a474). Sixth H7 flight. Graded by frozen gates.**

## Verdict — all three gates held, overhead did NOT eat the advantage

| gate | measured | rule | ideal |
|---|---|---|---|
| **G1 CONVERSION** | conv0 leak 0.007 · conv1 logical-1 = 0.990 | <0.10 · >0.90 | 0 / 1 |
| **G2 RETARGET** (Z-storm) | phase-flip 0.120 vs bare 0.212 → **sep +0.092 (16σ)** | > 5·se | +0.093 |
| **G3 SOURCE** (X-storm) | bit-flip 0.121 vs bare 0.206 → **sep +0.084 (15σ)** | > 5·se | +0.103 |
| encode overhead (clean_pf, no storm) | 0.006 | (reference) | 0 |

**PASS-TRANSLATOR.** Transversal-H carries |0_L⟩/|1_L⟩ between the bit-flip and phase-flip codes
essentially losslessly (conversion leakage 0.007; the encode+convert+read pipeline adds only 0.006).
Each 3-qubit specialist then beats the bare qubit against its native storm by ~0.09 at 15–16σ, and — the
pre-filed worry — the encoding overhead was **negligible (0.006)**, so the ~0.10 ideal margin survived
almost intact on hardware.

## Prediction grading (pre-filed conf 0.6): verdict **HIT** (and better than feared)
Conversion (G1) ✓. Separations predicted +0.03–0.09; measured +0.084/+0.092 — at/above the top of band
(the overhead-eats-advantage failure mode named in the pre-reg did NOT fire). Code leakage predicted
0.13–0.20 → measured 0.120/0.121 (better). fez was a clean day (cf. Exp247/249 also running hot).

## Scope (the honest boundary, established $0 pre-flight)
The literal H7-plan two-storm-survival claim was falsified in simulation before spend (distance-1 wall:
each 3-qubit code protects ONE logical basis; the full translated arm reads random 0.502). What is
certified here is the reusable capability underneath it — faithful mid-circuit code conversion and that
the destination code's protection is live. The both-basis two-storm demo needs Shor [[9,1,3]] (past the
depth wall), named not flown.

## H7 scoreboard
P6 ✅ · P7.0 ✅ · P2/248 ✅ (31s) · P7/247 ✅ (24s) · P1/249 ✅ (23s) · **P5/250 ✅ PASS-TRANSLATOR**.
Six of eight programs done. Remaining: P3 pattern buffer, P4 shielded tricorder.
