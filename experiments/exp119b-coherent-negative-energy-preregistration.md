# Exp119b — CERTIFIED NEGATIVE LOCAL ENERGY (COHERENT EXTRACTION): PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4641. Creator: "Run your next cycle! Exp119b!" Fresh-cycle
freeze. Parent: Exp119 (`exp119-certified-qet-preregistration.md`, graded FAIL-EXISTENCE
C4640) — this is the power-calculated retest proposed in its results doc.

## Scope-honest claim (stated first, before the gates)

**This is NOT LOCC quantum energy teleportation.** Exp119 measured that claim and it
FAILED as frozen (feedforward latency tax 0.092 E > 0.115 E budget, friction 05). The
119b claim is strictly weaker: **a coherent-controlled extraction drives Bob's local
energy ⟨H_B+V⟩ below the local ground level — certified negative local energy** — with
the control implemented as a quantum gate (Ry(2θ)+CRy(−4θ)), not a classical message.
The exotic-matter leg survives; the "teleportation by classical bit" leg does not, and
is not claimed.

## Provenance transparency (pro-hypothesis selection, disclosed)

The design is motivated by Exp119's coherent DIAGNOSTIC arm reading corrected
E_B = −0.0341 ± 0.0082 (4.2σ, near-miss, not promoted). Selecting a retest because an
unplanned arm looked good is pro-hypothesis selection — the defense is the F82
CONFIRMED_ON_RETEST discipline: the claim earns certification only on THIS fresh
dataset under gates frozen NOW, with the power calculation (c4130_001) done before
flight, and drift is a live kill risk (P(V1) honest at 0.70, not higher).

## Frozen apparatus (byte-identical builders: `exp119_qet_sim.py`, θ\*=0.161, h=k=1)

| Arm | Shots/basis | Role |
|---|---|---|
| qet_def (Ry+CRy coherent extraction) | **100,000** | HEADLINE |
| ground | **100,000** | baseline + G0 guard |
| fixp / fixm (uncorrelated-rotation controls) | 20,000 | V3 correlation control |
| cal0 / cal1 | 25,000 | frozen readout correction |

2 bases (zb, xx) per protocol arm → **10 pubs, 530k shots, one job, ibm_marrakesh**.
Pair: frozen min-2q-error rule (pick_pair), fresh at submit. Transpile seed 4641,
opt level 1, shuffled pub order seed 4641. **Audit**: 2q counts ground/fix = 1,
qet_def = 3, cal = 0, all on the selected edge.

## Frozen correction + SE (upgraded from 119: exact propagation, no fudge)

Per-qubit assignment (F0,F1) from cal0/cal1; v = F0+F1−1.
⟨Z⟩c = (⟨Z⟩−(F0−F1))/v; ⟨XX⟩c = ⟨XX⟩/(vA·vB).
**SE propagated exactly**: SE_c² = (SE_zB/vB)² + (2·SE_xx/(vA·vB))². Calib-estimation
error (≤0.001 at 25k) and 1q-gate error neglected — stated. One-sided physics note:
readout correction removes readout bias only; residual decoherence bias is POSITIVE,
so the corrected value remains an UPPER BOUND on the true E_B — the certification is
therefore conservative by construction.

## Frozen gates

- **G0 (NO-TEST guard, one-sided, raw)**: E_B(ground)raw + 5·SE < 0 → apparatus broken.
- **V1 (HEADLINE)**: corrected E_B(qet_def) + 5·SE_c < 0 →
  **NEGATIVE LOCAL ENERGY CERTIFIED (coherent extraction)**.
  Power (c4130_001, from 119 variances): SE_c ≈ 0.0047 at 100k → 5σ = 0.0235 vs
  expected dip −0.034 → margin 1.45×. Raw V1 is NOT gated (raw sits positive under
  readout bias by construction; disclosed, not hidden).
- **V2 (existence support)**: E_B(def) − E_B(ground), corrected, < 0 at 5σ
  (119 observed −0.070 raw at 5.5σ; at 100k the expected margin is ~2×).
- **V3 (correlation control)**: E_B(def) − E_B(fix_pooled), raw, < 0 at 5σ — the
  control-correlation (not rotation per se) is the active ingredient.
- **Ledger (reported)**: E_A, extraction, efficiency vs theory 0.162; note that in the
  coherent version the "message" is a quantum control line — the demon-record framing
  applies to the deferred measurement record.

Headline requires **G0 clean ∧ V1 ∧ V2 ∧ V3**. V1 alone failing → FAIL-CERTIFICATION
(drift or 119's reading was noise — either is informative and goes in the record).

## Predictions (registered at freeze)

- **P1** V1 certified: **0.70** (margin 1.45×; drift risk; 119's 4.2σ could regress).
- **P2** V2 ∧ V3 support gates: **0.85**.
- **P3** NO-TEST: **0.05**.

Lint: `experiments/exp119b_gate_lint_spec.json` → `results/exp119b_gate_lint.txt`.
Grader `scripts/grade_exp119b.py` FROZEN with this prereg.
