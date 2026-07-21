# Exp251 (H7-P3) — PRE-REGISTRATION: THE PATTERN BUFFER

**FROZEN before submission. Whisper C4961, substrate claude-opus-4-8. Creator directive: "Fly the next P"
(ship-computer). Builder+grader frozen together: `experiments/exp251_pattern_buffer.py`.**

## Claim
Two certified H6 capabilities never before chained — teleportation (Pauli-frame deferral, Exp177) and
the repeated-rounds QEC loop (Exp241) — COMPOSE: a state teleported into the live-corrected memory is
protected during the hold, surviving better than the same teleported state held bare, and the teleport
seam does not eat the advantage.

## Flight
`ibm_fez`, 8 pubs × 8,000 shots, static + offline decode (no in-circuit feed-forward), τ=30 µs/round
(Exp241-matched; real T1 provides the hold noise). Transpiled 2q ≤ 40 (asserted). Teleport |1⟩ (the
T1-sensitive state) source→d0 with the Bell frame DEFERRED to post-processing; encode d0 into the
bit-flip memory; hold R rounds; decode offline (majority QEC + teleport X̄ frame); read logical Z.
Est. 30–60 s of 4,014 s remaining.

## Frozen gates
- **G_COMPOSE**: F(tp_corr, R=3) − F(tp_bare, R=3) > 5·se (the corrected memory protects the teleported
  state vs holding it bare through the same idle).
- **G_SEAM**: F(tp_immediate, R=0) > 0.90 (teleport+encode+decode with no hold — the seam is faithful).
- **PATTERN-BUFFER-CERTIFIED** = both. Reported always: R=2 row; direct_corr_R3 (no teleport) to
  isolate the teleport cost.

## PD gates (passed pre-freeze)
PD-1: noiseless pipeline + Bell-frame recover |1⟩ exactly (tp_immediate 1.000, tp_corr_R3 1.000); under
a bit-flip storm proxy the corrected buffer beats bare (0.771 vs 0.137 at R3, 104σ) and teleport cost is
+0.008 → PATTERN-BUFFER-CERTIFIED in sim. Frame bookkeeping (G9) verified: X̄^m1 offline correction
recovers the logical for all Bell outcomes.

## Pre-filed prediction (before any data)
**PATTERN-BUFFER-CERTIFIED, confidence 0.7.** Exp241 established corrected>bare for held |1_L⟩ (R3 gap
~0.36); the teleport front-end (~3 CZ + Bell measurement) adds initial error but should not flip the
verdict. Predicted hardware: tp_immediate 0.90–0.95; tp_corr_R3 0.45–0.60; tp_bare_R3 0.13–0.25;
G_COMPOSE separation +0.20–0.40. **Named failure modes**: (i) G_SEAM < 0.90 → the teleport seam is too
lossy on this die (SEAM-FAIL, a composition-tax finding); (ii) the front-end error drags tp_corr below
tp_bare (NO-ADVANTAGE) — kept with full weight as the honest composition boundary.
