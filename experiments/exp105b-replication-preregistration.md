# Exp105b — Causal Discrimination Game REPLICATION on ibm_fez (pre-registration addendum)

**Author**: Whisper (DC15W), C4527 (2026-07-09) — Creator-directed second-chip replication
**Parent pre-reg**: `exp105-causal-game-preregistration.md` (FROZEN, commit 3dd64f3) — **inherited
verbatim**: same 51-pair optimal-q\* game, same padded uniform 4-CZ skeleton, same deterministic-
weighting estimator, same shuffle seed 4117, same shot counts (51×2000 game + 51×1000 null +
6×2000 sentinel START/MID/END), same gates and grade rule. NOTHING about the game changes;
only the device does. Submit script: `run_exp105_causal_game_submit.py --backend ibm_fez --tag
exp105b` (backend/tag flags are the only patch; game construction untouched).

**Purpose**: cross-device replication is this campaign's calibration standard (README; it demoted
F03's 3× and promoted F70's picker). Marrakesh result (Exp105, C4526): WIN, p̂ = 0.976931 ±
0.000495 vs 0.8695, all gates green. One device = one device. This addendum extends the arc to a
third chip (game marrakesh / cosine-law kingston / game fez).

**Device choice**: ibm_fez — queue 0–4 at scan (kingston 165), F62–F70 precedent (toric arc +
quiet-qubit cross-device validation ran there), same Heron CZ gate set. Live scan (FREE) at C4527:
pair (22,23) cost 0.01070, game histogram **{4: 51}** identical to parent, LIVE AUDIT PASS,
budget 160s pre-job.

## Frozen grade rule (inherited, constants identical)

1. Sentinel gate: min replicate DISC ≥ **+1.60**; null gate: weighted null success < **0.70**.
   Either fails → **NO-TEST** (infrastructure verdict, not a loss; may not be invoked selectively).
   Device-risk note, pinned now: fez has NO switch-DISC anchor (F77's +1.900 is marrakesh; F76's
   cosine law is kingston). If fez's sentinel lands below +1.60 the honest outcome is NO-TEST and
   a report of the measured DISC — not a re-shopped gate.
2. **WIN** iff p̂ − 5·SE_w > **0.8695**; **LOSS** iff p̂ + 5·SE_w < 0.8695 with gates passing;
   else UNDERPOWERED/AMBIGUOUS.
3. Grade by first post-drain cycle, `grade_exp105.py` pointed at `results/exp105b_jobids.json`
   (mechanical; grader need not be author).

## Pre-registered prediction (pred_c4527_001, conf 0.55 — quantum cap honored)

- Sentinel gate PASSES on fez and p̂ ∈ [0.93, 0.985] → WIN. The two-sided risk named in advance:
  fez sentinel is unanchored (NO-TEST risk), and fez readout/2q calibration differs from the
  marrakesh pair that produced 0.977. Replication SUCCESS = same verdict (WIN), not same p̂.

## Replication-specific honesty

- This is a same-design, same-analysis replication — it tests DEVICE-generality of the beat, not
  the design (the design's analyst degrees of freedom were already frozen at 3dd64f3).
- Budget: ~160s remaining pre-job; job ~40–60s expected (marrakesh drew within budget); Exp100
  probe #6 (~7 q-sec) remains affordable after. Creator has standing budget-refresh directive.
