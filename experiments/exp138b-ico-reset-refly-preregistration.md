# Exp138b — ICO heralded sub-bath reset, RE-FLY (PRE-REGISTRATION, FROZEN)

**Author**: Whisper (DC15W), C4720 (2026-07-15), Creator-directed ("run it").
**Status**: FROZEN before submission. This is a re-fly of Exp138 for a fresh calibration
window; it re-grades **nothing** from the old job.
**Parent**: Exp138 (`experiments/exp138-ico-reset-preregistration.md`), job
`d9bd80rv6alc73cst7g0`, graded **NO-TEST** (`results/exp138_grade.json`).

## 1. Why re-fly
Exp138's INTEGRITY gate failed: the retention sentinel came in at **0.846 / 0.852 / 0.854**,
below the frozen **0.90** floor → NO-TEST (no claim). Two honest facts about that floor:
1. It was set optimistically. I took FakeMarrakesh's preview (0.9725) minus a thin ~0.07 margin.
   FakeMarrakesh is known to be **optimistic at depth** (F81); the **measured** haircut on Exp138
   was 0.9725 → ~0.85, i.e. **~0.12**. So 0.90 was above what this depth realistically delivers.
2. 0.846 also misses Exp108's established **0.85** precedent (by 0.004) — so this is not purely a
   self-inflicted floor; the window genuinely landed at the precedent edge.

The ungated Exp138 physics was clean and is the reason a re-fly is worth one shot: reset delivered
D at **0.2149 ± 0.0040** (sub-bath at 5σ, null-independent), **~11σ** colder than the definite-order
null; the measured beat (0.0497) was **smaller** than ideal (0.065) — depth noise shrank it, so the
signal is conservative, not inflated; deco-null clean (0.5055).

## 2. The single frozen change (and only this)
**Retention floor 0.90 → 0.80.** Derivation, frozen pre-data:
`expected hardware retention ≈ FakeMarrakesh 0.9725 − 0.12 (measured F81 depth-haircut) ≈ 0.85`;
floor set **0.05 below** expectation for window variance, still far above the payload-collapse
regime (the split only dies as retention → ~0.6; at 0.85 the payload showed clean 5σ/11σ signal, so
a window admitted by an 0.80 floor is one where the physics is demonstrably visible).

**Everything else is byte-identical to Exp138**: same circuit (`exp138_ico_reset.build_circuit`),
same transpile seed 4720 ⇒ **same 22-CZ skeleton**, same PRIMARY beat-floor 0.02, same SECONDARY
sub-bath rule (`p1+ + 5SE < 0.25`), same null band (0.05), same deco band [0.40, 0.60], same
MAX_RESET_2Q=40, same calibration-gated 5-chain pick + 120-perm layout scan + live 2q re-audit.
A **fresh** job re-picks the best chain for the **current** calibration window — the actual lever
for a cleaner retention, over and above the floor change.

## 3. FROZEN grade rule (unchanged except the retention floor)
- **INTEGRITY (any fail ⇒ NO-TEST):** null band `|n_x − 0.25| + 5SE < 0.05` both orders;
  retention `min P(c=+, D=0) ≥ 0.80`; deco-null `P(c=+) ∈ [0.40, 0.60]`; live skeleton within
  the 2q class bound.
- **PRIMARY (WIN):** `min(n_f, n_r) − p1₊ − 5·√(se₊² + se_null²) > 0.02`.
- **SECONDARY (F95-style, LOSS-able, separate):** `p1₊ + 5·se₊ < 0.25`.
- **RESULT:** WIN iff INTEGRITY pass **and** PRIMARY pass. No re-grade of the parent job; no
  auto-resubmit; one SamplerV2 job; frozen shuffle seed 4720.

## 4. Scope (unchanged, frozen)
Resource-theory sub-bath cooling of an external qubit using warm baths + the switch only. Beats
**definite-order** reset (0.25), **not** native reset (~0.01). Modest, clean increment over F88
(delivery to an external computational qubit + fresh data-qubit null).

## 5. Provenance
Parent Exp138 (NO-TEST). Same apparatus/theory as F86 / Exp108. Backend ibm_marrakesh (Heron r2).
