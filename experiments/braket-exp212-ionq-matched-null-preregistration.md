# Exp212 (Braket) — PRE-REGISTRATION: structurally-matched definite-order null + same-window witness re-fly on IonQ Forte-1, plus gate-free bit-order calibration

**FROZEN before submission. Substrate: claude-fable-5. Whisper, C4944. Creator cap approval: $300 (2026-07-21).**
Plan: `exp212-ionq-structural-matched-null-PLAN.md` (incl. §10 gap review v2). This file freezes the
flight, the bounds, the reading rule, and the predictions. Nothing here changes after data is seen.

## Flights (all IonQ Forte-1, one submission batch each)

**A. Gate-free bit-order calibration** (`ionq_bitorder_cal.py --gate-free --submit --shots 100`)
- Circuit: x(0); x(1);x(1); measure both. Known input |c=1,t=0⟩, ZERO entangling gates — probes the
  entangler-free compilation class (the Exp211b null's class; the C4942 CX cal certified only the
  entangled class). Cost: 1 task × $0.30 + 100 × $0.08 = **$8.30**.
- Reading (frozen): `'01'` → GATEFREE-PRESERVED (permutation hypothesis REFUTED, 211b anomaly stays
  unexplained); `'10'` → GATEFREE-SWAPPED (211b NULL-FAIL fully explained as server-side bookkeeping).
- **Diagnostic only.** It gates nothing (the matched null lives in the entangled class, already
  convention-certified by the C4942 CX cal `'01'`), and CANNOT un-withdraw anything by itself.

**B. Exp212 main** (`braket_switch_causal.py --matched-null --submit --device ionq` = 100 shots/pub)
- 8 pubs, ONE submission batch (same-window): witness w_start_c/w_end_c/w_start_a/w_end_a
  (byte-identical frozen circuits) + matched null mnull_d0_c/d0_a/d1_c/d1_a
  (witness circuit with initial h(0) → |0⟩/|1⟩ prep; instruction-identical downstream; 2q-count
  asserted equal in-code). Cost: 8 × $0.30 + 800 × $0.08 = **$66.40**.

**Total $74.70. IonQ cumulative ≈ $211 + $74.70 = ~$285.70 < $300 cap.**

## Pre-flight gates (all PASSED before this freeze, C4943-44, free)
1. Abstract local sim @4000 shots: W_witness = +2.0000 (89.4σ), W_matched = −0.0235, all 8 marginals
   in band, verdict LOOPHOLE-CLOSED(restore).
2. **Native-sim gate**: exact `run(native=True)` client-side compile rebuilt for all 8 flight pubs +
   the gate-free cal, simulated on the Braket local simulator: total-variation vs ideal ≤ 0.0068 on
   every pub — ALL PASS.
3. Convention gate for the entangled class: C4942 CX calibration (task 6750e981) returned `'01'`
   (preserved) — reused per plan §4, not re-flown.

## Frozen grading (grade_matched, committed before flight)
- Per-pub **all-bit marginals**: P(target = ideal) ≥ 0.85 (comm t=0, anti t=1, deterministic ideally);
  P(c=0) ∈ [0.30, 0.70] (control ideally 50/50). Every one of the 4 null pubs must pass.
- Per-prep bands: |W_D0| ≤ 0.3 AND |W_D1| ≤ 0.3 (no hiding an artifact in the average).
- Mixture band: |W_matched| ≤ 0.3. (At 100 shots se(W_matched) ≈ 0.10; the band ≈ 3σ. The artifact
  class being hunted — 211b-style permutation — signals at |W| ≈ 2, i.e. ~20σ. Stated per §10.4.)
- Same-window witness re-certification under the ORIGINAL Exp211 rule: W ≥ 1.3 AND W − 5·seW > 0
  (seW = √(2/shots) = 0.141 at 100 shots).
- Separation: W_witness − W_matched > 1.0.

## Reading rule (frozen, three branches — §10.4.3)
1. null_ok AND witness re-certifies AND separation > 1.0 → **LOOPHOLE-CLOSED(restore)**: the IonQ
   cross-modality certification is restored (witness + structurally-matched validated null, same
   window). The **new same-window witness W becomes the canonical number**; the old 500-shot
   W = 1.894 stands as corroboration only. Paper body + title revised same cycle.
2. NOT null_ok → **NULL-FAIL(stays-withdrawn)**: the witness does not discriminate ICO on IonQ;
   cross-modality claim **permanently withdrawn**; recorded as a hardware finding.
3. null_ok but witness does NOT re-certify → **WITNESS-NO-REFIRE(stays-withdrawn)**: claim stays
   withdrawn (device drift / non-reproducibility finding). No partial credit.
No band changes, no shot changes, no re-reads after data. Either outcome kept with full weight.

## Pre-filed predictions (before any data)
- **A (gate-free cal)**: predict `'10'` GATEFREE-SWAPPED, confidence **0.7** — the C4943 permutation
  hypothesis (counts one permutation from perfect; client compile exonerated; cal-v1 idle-drop
  precedent). Named failure: `'01'` → hypothesis refuted, 211b anomaly genuinely open; recorded.
- **B (matched null)**: predict null_ok = True, W_matched ∈ [−0.15, +0.15], confidence **0.85**
  (entangled class + native-sim gate passed).
- **B (witness re-fly)**: predict W ∈ [1.7, 1.95], confidence **0.85** (Exp211 gave 1.894; drift risk
  named: ion chips recalibrate — a lower-but-firing W [1.3, 1.7] is the most likely miss mode).
- **Overall**: predict **LOOPHOLE-CLOSED(restore)**, joint confidence **~0.72**.

## Outcome handling
- Restore → white paper §banner replaced; body/title revised to three-substrate with the full
  211/211b/211c/212 audit trail (incl. both negatives) in §8; STATUS doc updated.
- Either stays-withdrawn branch → paper stays two-substrate; §10 findings + this flight recorded as
  the honest boundary; no further IonQ spend against this question without a new Creator decision.
