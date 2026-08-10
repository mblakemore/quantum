# H10-B4 PRE-REGISTRATION — Heat Flowing Backward (the two-spin arrow reversal)

*Whisper C5017, 2026-08-01, substrate claude-fable-5. Status: **FLOWN & GRADED (status corrected C5055 — see findings/h10-*-whisper-c5055.md; this line previously read: FROZEN TEXT, awaiting Ember
spec-seal + Creator GO.** Parent: `h10-b4-heat-backward-scout-whisper-c5017.md` (GO, all inputs
frozen §§2–6). Every number below is computed in `results/h10_b4_heatback_bars_c5017.json` and
`results/h10_b4_prep_route_c5017.json` — nothing is asserted that was not computed. No secret is
involved: this is not a blind-decode experiment; the seal asked of Ember is the SPEC-FREEZE
(ancestry-style commit of this text before submission), and the grading is mechanical against the
bars herein.*

## 1. Claim shape (printed first)

A chip analogue of Micadei et al. (Nat. Commun. 10, 2456 (2019)): with pre-prepared correlations,
the two-spin energy flow REVERSES (cold→hot) under the same interaction that drives normal
hot→cold flow on the uncorrelated pair — and the reversal is PAID FOR by the correlations,
measured as a mutual-information drop. **Not claimed**: anything about baths (states are
prepared), the vacuum (correlations are prepared, not harvested — C2's flight), or time's arrow
at large. Effective temperatures are prepared states; said exactly so in every output.

## 2. Frozen design

- **System**: 2 qubits. H_i = (ω/2)Z, ω=1 (energy read as ⟨Z⟩·ω/2).
- **State**: ρ(α) = ρ_A(β_h=0.5) ⊗ ρ_B(β_c=2.0) + χ, χ = α|01⟩⟨10| + h.c., **α = 0.157i**
  (the positivity bound).
- **Preparation (frozen route, scout §6)**: classical mixture — per shot, sample one of FOUR
  pure-state circuits with probabilities {0.5483, 0.4067, 0.0450, 0.0001}; two are product
  (0 CX), two entangled (1 CX). Eigendecomposition reconstruction error 5.6e-17.
- **Interaction**: U(θ) = exp(−iθ(XX+YY)/2), **θ = 2.35** (iSWAP-family, native-cheap).
- **Backend**: any Heron; 2 qubits + spectator-free placement; ALT open instance.

## 3. Arms and frozen bars (exact theory; SE = per-shot binomial on ⟨Z⟩)

| # | Arm | Frozen prediction | Registered bar |
|---|---|---|---|
| 1 | Correlated, θ=2.35 | ΔE_cold = **−0.0262** | **G1**: ΔE_cold < 0 at ≥5σ (reversal sign) |
| 2 | Uncorrelated control (χ=0), same session | ΔE_cold = **+0.1308** | **G2**: ΔE_cold > 0 at ≥5σ AND arm1−arm2 separation ≥5σ |
| 3 | θ-sweep {0.5, 1.2, 2.35, 2.9} correlated | exact curve overlay | **G3 (reported, not gated)**: sign of ΔE_cold tracks the exact curve at each point within 2σ |
| 4 | Energy books: ⟨Z_A⟩ + ⟨Z_B⟩ arm 1 | ΔE_hot = +0.0262 + interaction term | **G4**: total energy change consistent with the exact ledger within 3σ |
| 5 | MI ledger: 2-qubit tomography before/after, arm 1 | I(A:B): 0.278 → 0.214 (Δ = −0.064) | **G5 (reported, not gated)**: ΔI < 0 at ≥2σ — the correlations-pay receipt |

**Registered verdict = G1 ∧ G2 ∧ G4.** G3/G5 are reported legs (the calibration curve and the
ledger receipt) — misses there are findings, not verdict-changers, and will be published either
way. Statistic categories per the C5014 rule: G1/G2 are SIGN+SEPARATION tests; G4 is a
consistency bound; none is a works-claim about anything beyond its stated observable.

## 4. Budget (frozen)

- Arms 1,2: 3,000 shots each (5σ on the sign needs ~9.1k for arm 1 alone at worst-case — arm 1
  gets 12,000; arm 2 keeps 3,000; separation needs only ~254).
  **Correction applied before freeze**: arm 1 = 12,000 shots (sign at 5σ), arm 2 = 3,000.
- Arm 3: 4 × 2,000 = 8,000. Arm 4 rides arms 1–2 (same measurements). Arm 5: 2 × 9 tomography
  settings × 1,000 = 18,000.
- **Total ≈ 41,000 shots ≈ ~2–4 QPU-seconds** (measurement-dominated; prep circuits ≤1 CX).
  Against the fresh pool (283s remaining of 600 at time of freeze-draft): negligible.

## 5. Analysis (frozen)

Per-shot ⟨Z⟩ estimators with binomial SEs; the classical mixture is analyzed POOLED (the sampling
probabilities are part of the state definition, printed in the artifact per arm). Readout
mitigation: none (the claim is differential arm1-vs-arm2 on the same pair, same session — the
F94/F95 grammar; absolute calibration cancels in G2's separation and biases G1 conservatively
only if symmetric; asymmetric-readout residual is captured by G4's books). Decode script and its
known-answer self-test (reproduce §3's exact numbers from the frozen state and unitary before
touching flight data) ship in the same commit as the flight script.

## 6. Kill/no-fly conditions

- Pre-flight sim gate: the flight script's own noiseless run must reproduce every §3 number to
  1e-6 (known-answer, C5016 method). Fail → no submission.
- Backend calibration at submit: 2q gate error > 2% on the chosen pair → hold (the OP's smallest
  bar, G1's −0.026, needs the iSWAP family at reasonable fidelity).

## 7. Seats

Whisper: flight + decode + this text. Ember: spec-seal (commit ancestry of this frozen text
pre-submission; no secret to hold). Elder: grader seat at landing (mechanical against §3).
Creator: GO (this is the G4-analog: budget quoted above; fresh pool number printed).

*Frozen text ends. Changes after Ember's seal require a numbered amendment.*
