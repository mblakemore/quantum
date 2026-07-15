# Exp139 — Coherent entropy concentration seeded at F118 (PRE-REGISTRATION, FROZEN)

**Author**: Whisper (DC15W), C4720 (2026-07-15), Creator-directed ("run it").
**Status**: FROZEN before submission. Circuit `experiments/exp139_concentration.py`.

## 1. HONEST SCOPE (frozen, load-bearing — read first)
This is an **engineering artifact, not new ICO physics.** Majority-vote of 3 biased qubits is
**classical entropy compression** (`p₁(dest) = 3p² − 2p³`); it works on *any* biased qubit, the
inputs are diagonal thermal populations, the majority commutes with the computational basis, and
**no coherence is used**. The identical statistics come from taking the classical majority of 3
measured qubits in post-processing. So this run does **not** extend indefinite-causal-order physics
(that is F118, unchanged; the cascade fixed point **0.177** is ICO's real cooling floor —
`docs/ico-cooling-floor-and-concentration-boundary-whisper-c4720.md`). The **only** thing hardware
adds over post-processing: a **physically-produced** (not post-selected) destination qubit colder
than any single input, built by a coherent majority gate that runs without the depth eating the
classically-predicted number. Fuel-mislocation guard (F94/C4717): the cooling is the **classical
majority**, not the ICO resource. Inputs are prepared **at F118's measured cold population (0.21)**
to isolate the concentration step, rather than fly 3 live fridges (13-qubit NO-TEST risk for no new
physics). Any write-up says "classical entropy-compression primitive seeded by F118," never "ICO
drove a qubit to 0.11."

## 2. Circuit (4 qubits, temperature-independent concentration + pooling)
q0,q1,q2 = inputs, q3 = destination (|0>). Prep inputs to a basis state (b0,b1,b2) with X gates,
then `dest = majority` via three Toffolis (`ccx(0,1,3) ccx(1,2,3) ccx(0,2,3)`), measure dest. The 8
basis circuits are **input-temperature-independent**; pooling them with weights `∏ w(bᵢ)`, `w(1)=p`,
realizes 3 i.i.d. inputs at population p **exactly**, and the **same 8 circuits** pool to both
p=0.21 (cold) and p=0.25 (bath) readouts. Single-input reference: 2 circuits (input |0>/|1>) pooled
to p — captures readout error with no gate depth. Payload depth: **24 CZ** (FakeMarrakesh),
opt-level-3, live re-audit aborts on drift from the frozen seed 4720.

## 3. Theory targets (classical)
`dest(cold 0.21) = 0.1138` · `dest(bath 0.25) = 0.1562` · `single = 0.21`. Sentinels:
`conc_000 → 0`, `conc_111 → 1` (majority logic + noise floor).

## 4. FROZEN grade rule
- **INTEGRITY (any fail ⇒ NO-TEST):** `conc_000 < 0.05` AND `conc_111 > 0.95` (majority gate
  intact); live skeleton within the 2q class bound.
- **PRIMARY (WIN):** the concentrated destination is colder than a single input on the same chip:
  `dest_cold + 5·√(se_dest² + se_single²) < single_cold`.
- **SECONDARY (WIN):** colder inputs concentrate colder: `dest_cold + 5·√(se²) < dest_bath`.
- **CONTEXT (reported, not gated):** `dest_cold` vs the classical prediction 0.1138 (does depth
  degrade it, and by how much).
- **RESULT:** WIN iff INTEGRITY pass AND PRIMARY pass. One SamplerV2 job, frozen shuffle seed 4720,
  no auto-resubmit.

## 5. Feasibility preview (FREE, informational)
- Noiseless: dest_cold 0.1138 (exact), single 0.21, sentinels 0/1 — all gates PASS.
- FakeMarrakesh (24 CZ): dest_cold **0.1266 ± 0.0013**, dest_bath 0.1674, single 0.2113, sentinels
  0.017/0.975 — PRIMARY passes at ~55σ (0.085 colder than single). Low-risk, 4 qubits.

## 6. Submission hygiene
Calibration-gated 4-chain (min 2q-error + readout), 24-perm layout scan, live 2q re-audit (abort on
drift), ONE SamplerV2 job, cost stated up front, backend ibm_marrakesh (Heron r2).

## 7. Provenance
Seed value from F118 (`results/exp138b_grade.json`, cold branch 0.2100). Classical bound 3p²−2p³.
Cascade-floor / classical-boundary context:
`docs/ico-cooling-floor-and-concentration-boundary-whisper-c4720.md`. Family: Wing I sidebar —
classical amplifier on the ICO cold, ICO physics **not** extended.
