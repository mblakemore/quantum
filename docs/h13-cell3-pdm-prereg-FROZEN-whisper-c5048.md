# H13 Cell 3 — Temporal Negativity Meter — PRE-REGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C5048 (2026-08-09) · **Substrate**: claude-fable-5
**Arc**: [H13 Temporal Investigations](h13-temporal-investigations-whisper-c5048.md) Cell 3 · Tier-0 gate: [T0.4 GO](h13-tier0-design-studies-whisper-c5048.md)
**Creator GO**: ship-computer general#7376 ("cell 3 and 5 go!") after budget triage general#7374.
**Venue (declared)**: `ibm_fez` · **Account**: `IBMQ_ALT2` (10.0 QPU-s at triage; per-job fit gate re-reads at submit) · **Estimated cost**: ~3–5 QPU-s.
**FROZEN before flight** — this file commits before the submit script runs. No criterion below may change after the job id exists.

## Claim under test

The pseudo-density matrix (Fitzsimons–Jones–Vedral) of ONE qubit measured at two times, R = ¼ Σ_{i,j∈{I,X,Y,Z}} ⟨σ_i(t₁)σ_j(t₂)⟩ σ_i⊗σ_j, has a **negative eigenvalue** — a certificate that the measured correlation cannot be carried by any spatial two-party state, only by one system at two moments. Scope: under the frozen sequential projective measurement model below; symmetric readout error only *shrinks* correlators and therefore pulls **toward** PSD (conservative for the headline).

## Apparatus (frozen)

- **Temporal arm** (18 circuits): input I/2 realized as equal-shot classical mixture of |0⟩ and |1⟩ preps (2 preps × 9 basis pairs). Per circuit: pre-rotate to basis i (X: H · Y: S†H · Z: none), **mid-circuit measure** → c0, rotate back, no evolution (identity), pre-rotate to basis j, final measure → c1. Zero two-qubit gates.
- **Spatial control arm** (9 circuits): Φ⁺ (H+CX), wing A mid-circuit measured in basis i, wing B measured in basis j at the end — the identical estimator pipeline pointed at a genuine state.
- 2000 shots/circuit, 27 circuits total. DD off (campaign default). Transpile opt level 1. Layout: live-picked at submit — temporal qubit = lowest readout error; spatial pair = best (readout+2q) connected pair; pick recorded in manifest, never cached.
- Correlators: c_ij = E[(−1)^{c0+c1}] pooled over preps; singles c_iI, c_Ij pooled from the same counts; c_II = 1.

## Frozen gates

| Gate | Criterion | Priced from |
|---|---|---|
| **G1 HEADLINE** | min-eig(R_temporal) < 0 at ≥5σ (bootstrap SE, B=1000 multinomial resamples per circuit), and inside band **[−0.50, −0.30]** | T0.4: −0.448 predicted at c≈0.93; band floor allows c down to ~0.73 |
| **G2 CONTROL (the falsifier)** | min-eig(R_spatial) ≥ −2·SE_boot | a genuine state must read PSD; if the pipeline manufactures negativity, this arm catches it |
| **G3 STRUCTURE** | all off-diagonal \|c_ij\| ≤ 0.10 (i≠j ∈ {X,Y,Z}), temporal arm | identity evolution predicts 0 |
| **G4 APPARATUS** | pooled temporal singles \|c_iI\|, \|c_Ij\| ≤ 0.06 | I/2 input predicts 0 |

**Verdicts**: PASS = G1–G4 all hold. UNDERPOWERED = G1 sign negative at ≥2σ but <5σ, others hold. FAIL = G1 sign non-negative at ≥2σ, or band missed, or G2/G3 broken. **NO-TEST** = any G4 single >0.10 (prep broken — the apparatus never realized I/2) or G2 broken beyond −4·SE together with G1 (pipeline defect, nothing certified either way).

## Predictions (frozen, from T0.4 + measured fez error classes)

c_diag ≈ 0.90 ± 0.04 each · min-eig(R_temporal) ≈ −0.45 · min-eig(R_spatial) ≈ +0.02 · σ-distance of G1 at 2000 shots ≈ 120σ.

## Postselection / heralding

None. Every shot is kept. No sifting anywhere in this flight.

*Filed before flight. The meter reads what it reads.*
