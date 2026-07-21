# Exp212 RESULTS — matched null + same-window witness + gate-free cal (IonQ Forte-1), and the root cause of everything

**Whisper, C4944-45. Substrate: claude-fable-5. Pre-reg: `braket-exp212-ionq-matched-null-preregistration.md` (frozen at quantum@3cfea9c BEFORE submission).**
Tasks: main batch `29012b69-51bf-424f-99ba-be06f666bc0e` ($66.40); gate-free cal `9e7acae7-1c4f-404e-9160-6125c45ffacc` ($8.30). IonQ cumulative ≈ $285.70 < $300 cap.

## 1. Verdict as instrumented (frozen rule, no re-reads)

**NULL-FAIL(stays-withdrawn).** The frozen `grade_matched` reported W_matched = +1.8900 ± 0.0325
(band ≤ 0.3 violated; every one of the 8 marginal checks failed), same-window witness W = +1.8800 ± 0.1414
(WITNESS-FIRED, 13.3σ). Per the frozen three-branch rule, the cross-modality claim **stays withdrawn**.
This grading stands as the instrument produced it and is recorded with full weight.

**Pre-filed prediction grading (honest):**
- Gate-free cal `'10'` (conf 0.7): **MISS** — returned `'01'` 98/100 (GATEFREE-PRESERVED). The C4943
  "entangler-free class" localization was WRONG.
- Null clean (conf 0.85): **MISS** as instrumented.
- Witness re-fire 1.7–1.95 (conf 0.85): **HIT** (1.88).
- Overall restore (conf 0.72): **MISS** as instrumented.

## 2. The diagnosis the flight bought (worth more than the verdict)

The null counts show the exact mirror of theory: the deterministic bit sits in the control slot and the
50/50 bit in the target slot, in ALL FOUR null pubs — the C4943 permutation signature again. But this time
the confound is broken: the **gate-free cal (single task) decoded correctly** while the **entangled null
(program-set batch) decoded swapped**. The swap tracks the **submission path**, not gate content:

| flight | path | decode |
|---|---|---|
| C4942 CX cal, C4944 gate-free cal | single-circuit task | **correct** |
| Exp211b null (2 circuits), Exp211 witness (4), Exp212 batch (8), Exp210 Rigetti (4+64) | **program set** | **bit-order swapped** |

**Root cause, line-exact (qiskit-braket-provider 0.18.1, `providers/braket_quantum_task.py`,
`BraketQuantumTask.result()`, program-set branch):** `counts=executable_result.counts` passes raw
Braket-order (q0q1) keys through **without** the `k[::-1]` little-endian reversal that the single-task
path (`_result_from_circuit_task`) applies. The same branch's `memory` field DOES reverse
(`shot_result[::-1]`) — an internal inconsistency proving omission, not convention.

**Ground truth from the raw device payloads (pre-conversion, already paid for):**
- **Exp212 null (raw, Braket order)**: control 41–52% (theory 50/50 ✓), target deterministic 95–100%
  correct per arm ✓ in all four pubs. **The matched null physically collapsed.**
- **Exp211b (raw)**: `wnull_c` c=0 99%, t=0 ✓; `wnull_a` c=0 99%, t=1 ✓ → **W_def(corrected) = 0.00.
  The null that triggered the C4942 retraction was CLEAN; its "failure" was this decode bug.**
- IonQ device behavior is exonerated entirely — every flight executed correctly, every time.

## 3. Corrected readings (frozen bands, corrected decode — for the record)

| quantity | bug-decoded | corrected | frozen band |
|---|---|---|---|
| Exp212 W_matched | +1.8900 | **−0.0900** (W_D0 −0.22, W_D1 +0.04) | ≤ 0.3 ✓ |
| Exp212 null marginals (8) | all FAIL | **all PASS** (t det. 95–100%, c 41–52%) | ✓ |
| Exp212 witness (same window) | +1.8800 | **+1.9100** | ≥1.3, −5seW>0 ✓ |
| separation | −0.01 | **+2.00** | > 1.0 ✓ |
| Exp211 witness | +1.8940 | **+1.8920** (palindrome-robust) | — |
| Exp211b W_def | +1.96 | **0.00 → NULL-CLOSED** | \|W\|<0.3 ✓ |
| Exp210 Rigetti W | 1.1138 | **1.2165** (49.7→54.4σ) | PASS ✓ |
| Exp210 Rigetti R̄ / D | 0.2712 / +0.0169 | **0.2873 / −0.0039** | PASS ✓ / clean ✓ |

Under the corrected decode, every frozen numeric criterion of the pre-registered reading rule is
satisfied (restore branch). Exp210's PASS-CAUSAL is decode-robust and its numbers *improve* (Rigetti was
~9% better than reported; `braket_causal_rigetti_CORRECTED.json`).

## 4. Status and the decision (Creator's call — no unilateral restoration)

The frozen rule bound the grading to the instrument, and the instrument said NULL-FAIL; the same
pre-registration forbade re-reads. A decode-bug correction validated by raw payloads + source inspection
is different in kind from band-shopping — but after C4942, restoration on a corrected re-read is a
governance decision, not mine alone. Options:

- **(a) Restore on the standing evidence**: device raw payloads (6 null pubs across 2 experiments, all
  physically perfect), the line-exact reproducible source bug, the 2×2 path confound break, and the
  Rigetti consistency check. No further spend.
- **(b) Buy the last inch (~$16.30, needs cap ≈ $305)**: pre-registered known-input **program-set**
  calibration — 2 known-input circuits flown AS a program set; predict recorded keys come back
  unreversed (`'10'` where truth is `'01'`). Certifies the decode correction with paid ground truth in
  the exact submission path; then Exp212 regrades under the certified correction.
- **(c) Letter of the rule**: permanent withdrawal despite the proven instrument bug.

Recommendation: **(b)** if any doubt is to remain closed; (a) is defensible on the evidence.
Either restoration path also mandates: paper body/title/§8 rewrite (with ALL negatives and this bug in
the audit trail), Exp210 corrected numbers adopted, and an upstream bug report to qiskit-braket-provider
(Creator call — external communication).

## 5. Data availability
Raw payloads fetched from tasks: Exp212 `29012b69`, gate-free cal `9e7acae7`, Exp211b `ca68e121`,
Exp211 witness `b479e273`, Exp210 `c5d0e765`/`4196545e`. Corrected Rigetti card:
`results/braket_causal_rigetti_CORRECTED.json`. As-instrumented Exp212 card:
`results/braket_causal_ionq_matched.json`.
