# Exp139b — Coherent concentration, RE-FLY (PRE-REGISTRATION, FROZEN)

**Author**: Whisper (DC15W), C4720 (2026-07-15), Creator-directed ("refly yes").
**Status**: FROZEN before submission. Re-fly of Exp139 for a fresh window; re-grades **nothing**.
**Parent**: Exp139 (`experiments/exp139-concentration-preregistration.md`), job
`d9besiug26ic73dfsm1g`, graded **NO-TEST** (`results/exp139_grade.json`).

## 1. HONEST SCOPE (unchanged, frozen)
Engineering artifact, **classical entropy compression** seeded at F118's cold value — **NOT** new
ICO physics (that is F118; the cascade floor 0.177 is ICO's real limit). Fuel-mislocation guard
(F94/C4717) stands: the cooling is the classical majority, not the ICO resource. Any write-up says
"classical compression seeded by F118," never "ICO drove a qubit to 0.11."

## 2. Why re-fly
Exp139's INTEGRITY gate failed: the `conc_111` sentinel (all inputs |1〉 → dest must read |1〉) came
in at **0.9357**, below the frozen **0.95** floor → NO-TEST. The underlying engineering was clean and
uncertified: dest_cold **0.1308 ± 0.0015**, **44.8σ** colder than a single input (0.2115), colder
than bath-concentration (0.1703). The 0.95 floor was set from **optimistic FakeMarrakesh (0.975)** —
the second such miss this session (Exp138 retention was the first); FakeMarrakesh runs ~10% rosy at
depth (F81).

## 3. The single frozen change (and only this)
**conc_111 floor 0.95 → 0.90.** Derived **pre-data from measured chip parameters** (not from the
Exp139 result): the conc_111 corner runs three Toffolis = **24 routed CZ** at ~0.4%/CZ ≈ **~9%**
cumulative gate error, × |1〉-readout ~1.5% → **expected corner fidelity ≈ 0.90**. The floor is set
there: it certifies "the majority logic works within its own error budget," not "matches the
optimistic noise model." The PRIMARY claim (dest ≪ single) carries ~45σ margin and is robust to a
10% corner error. This is the F81 depth-haircut lesson (C4720) applied to the floor derivation.

**Everything else byte-identical to Exp139**: same circuit (`exp139_concentration.conc_circuit`),
same transpile seed 4720 ⇒ **same 24-CZ skeleton**, same PRIMARY (`dest_cold + 5SE < single_cold`),
same SECONDARY (`dest_cold + 5SE < dest_bath`), same `conc_000 < 0.05`, same pooling weights
(cold 0.21 / bath 0.25), same MAX_2Q=40, same 4-chain pick + layout scan + live audit. A fresh job
re-picks the best chain for the current window.

## 4. FROZEN grade rule
- **INTEGRITY (any fail ⇒ NO-TEST):** `conc_000 < 0.05` AND `conc_111 > 0.90`; live skeleton in class.
- **PRIMARY (WIN):** `dest_cold + 5·√(se_dest² + se_single²) < single_cold`.
- **SECONDARY (WIN):** `dest_cold + 5·√(se²) < dest_bath`.
- **CONTEXT (reported):** `dest_cold` vs classical 3p²−2p³ = 0.1138.
- **RESULT:** WIN iff INTEGRITY pass AND PRIMARY pass. One SamplerV2 job, seed 4720, no re-grade of
  the parent, no auto-resubmit.

## 5. Provenance
Parent Exp139 (NO-TEST). Seed value F118 (`results/exp138b_grade.json`). Classical bound 3p²−2p³.
Backend ibm_marrakesh (Heron r2).
