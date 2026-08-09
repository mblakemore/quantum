# H13 Cell 5 — Hardy's Paradox ("The Event That Never Happens") — PRE-REGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C5048 (2026-08-09) · **Substrate**: claude-fable-5
**Arc**: [H13 Temporal Investigations](h13-temporal-investigations-whisper-c5048.md) Cell 5 (Hardy half; pigeonhole is a separate future flight).
**Creator GO**: ship-computer general#7376 · **Venue (declared)**: `ibm_fez` · **Account**: `IBMQ_ALT` (6.0 QPU-s at triage; fit gate re-reads at submit) · **Estimated cost**: ~2–3 QPU-s.
**FROZEN before flight.** Design numeric: `tools/h13_cell5_hardy_freeze.py` → `results/h13_cell5_hardy_freeze_c5048.json` (committed with this file).

## Claim under test

Hardy's nonlocality without inequalities, in the hardware-honest CH difference form. Three joint events are (ideally) never seen; classical logic then forbids the fourth; quantum mechanics delivers it at ~9%. The certified quantity is the LHV-bounded difference
**W = P(11|A₁B₁) − P(11|A₂B₁) − P(11|A₁B₂) − P(00|A₂B₂) ≤ 0 for every local-realist model** — the bound is derived, not cited: measured zeros enter W directly, so imperfect zeros weaken W rather than invalidating it.

## Apparatus (frozen)

- **Hardy state** (frozen amplitudes, real): (−0.204057, −0.615875, 0.412407, −0.639515) on |00⟩,|01⟩,|10⟩,|11⟩ — ideal q = 0.0928, ideal zeros ≤ 1.2×10⁻⁵ (true Hardy point; theory max q = 0.0902 at exact zeros).
- **Measurement settings** (frozen): local Ry(−θ) then Z-measure, outcome 1 ≡ |1⟩; θ_A1 = 1.210571, θ_A2 = 6.158402, θ_B1 = 4.198403, θ_B2 = 5.533757.
- **Hardy arm**: 4 circuits (settings A₁B₁, A₂B₁, A₁B₂, A₂B₂) × 8000 shots.
- **Null arm (the falsifier)**: |00⟩ product state, identical 4 settings × 4000 shots → W_null (an LHV-satisfying source must give W ≤ 0).
- 8 circuits total. State prep via initialize(); **gate-feasibility lint in-script: transpiled 2q count ≤ 3 for the Hardy prep, else abort before submit**. DD off. Layout: live-picked best connected pair, recorded in manifest.

## Frozen gates

| Gate | Criterion | Priced from |
|---|---|---|
| **G1 HEADLINE** | W > 0 at ≥5σ (binomial SEs, quadrature) and inside band **[0.02, 0.09]** | freeze numeric: W ≈ 0.053 at 13.3σ under fez error classes |
| **G2 ZEROS (health)** | each of the three "zero" probabilities ≤ 0.03 | predicted ≈ 0.013–0.015 (readout-dominated) |
| **G3 HARDY FRACTION** | q = P(11\|A₁B₁) ∈ [0.05, 0.12] | predicted 0.096 |
| **G4 NULL** | W_null < 0, and W − W_null > 0 at ≥5σ | product state satisfies LHV by construction |

**Verdicts**: PASS = all four hold. UNDERPOWERED = W > 0 at ≥2σ but <5σ, others hold. FAIL = W ≤ 0 at ≥2σ, or band missed, or G4 broken. **NO-TEST** = any zero > 0.05 (apparatus never realized the Hardy point — the paradox premise is absent, nothing is being tested).

## Postselection / heralding

None. All shots kept; the four probabilities are raw relative frequencies.

*Filed before flight. Either the impossible event shows up, or it doesn't — both go in the ledger.*
