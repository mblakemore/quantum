# H13 Cell 2 — THE CAUSAL COMPASS — **FROZEN PREREG** (court-signed, C5058)

**Author**: Whisper (DC15W), C5058 (2026-08-11) · **Substrate**: claude-opus-5 (model switched mid-session; C4054 stamp)
**Creator GO**: #70 tank package. **Court**: Elder register/decode seat SIGNED (#9035, checklist `docs/h13-cell2-freeze-checklist-elder-c6603.md`), Ember seal/fly seat SIGNED (#9037) on A–C being in the frozen text. This document is that text.
**Supersedes**: `h13-cell2-compass-prereg-DRAFT-whisper-c5048.md`. **Claim card**: `experiments/h13_cell2_claim_card_c5057.json` (5-class attack preflight ALL CLEAR incl. billing-currency).

## 1. Claim
Blind discrimination of **cause-effect vs common-cause from observational quantum data** at ≥5σ over the enumerated classical-observational ceiling. Prior art / framing: Ried et al., Nat. Phys. 11, 414 (2015) — our contribution is protocol + certification on hardware, not the concept.

## 2. Structure (the C5058 reallocation — court-endorsed #9057/#9058)
The statistic yields **≤1 bit per run**; evidence is *across* runs, not within one. Two separately-budgeted line items:

| line item | purpose | circuits | shots | note |
|---|---|---|---|---|
| **PRE-RUN** | measures the FLOOR (precision instrument) | 20 draws × (3 diagonals × 2 arms) = 120 | 1,000 → **20,000 shots/basis-arm** | randomization LIVE (B5); draw count **n = 20** is the estimator's sample (B3) |
| **SCIENCE** | buys CALLS (1 bit each) | **40 runs** × 6 = 240 | 400 | decoder floor N≥100 & \|C\|/se≥5 satisfied with ≥4× margin at the band floor (Elder #9057) |

**runs = 40** covers the required count at the achievable ceiling (Elder: 8k pre-run → 32 runs; 20k → 30). We buy the deeper pre-run *and* the larger run count because the max-of-three numerator (§A) may land above the model estimate. Est. 216,000 shot-circuits ≈ **64 QPU-s** (Cell-3-calibrated MCM rate; conservative — only the CE arm carries mid-circuit measurement).

## 3. Apparatus
**CE arm**: one qubit — measure Pauli *i* → **idle τ** → measure Pauli *i*. **CC arm**: Φ⁺ pair — **idle τ** → measure Pauli *i* on both wings. Diagonal bases only (XX, YY, ZZ) — the frozen statistic reads nothing else.
**Fix-1 variant (b)** — independent injection over a common band: per run, per arm, τ drawn independently ~ U[0, τ_max], **τ_max = 30 µs frozen**. Band **W** = the realized correlator span, **measured in the pre-run, not assumed**.

## A. Classical ceiling (replaces the single-record 0.50287)
`ceiling = 1/2 + d/(2W)`, `d` = **MAX of three numerators, each at its UPPER confidence bound**: (1) model `d/W` from the pooled realized gap; (2) permutation-calibrated empirical TV; (3) executed classical arm cross-validated success (F87). They fail in opposite directions; the max never flatters; which wins is diagnostic. All three come off the **same** pre-run records. **Shot count published with the bound** (B6).

## B. Frozen text items
1. Variant **(b)**. 2. Band via **τ_max = 30 µs**, chosen pre-flight, realized W measured. 3. **Draw count n = 20** (draws, not shots). 4. `d` = the pooled realized inter-arm gap in diagonal-correlator units, defined on the pre-run sample. 5. Pre-run runs **with randomization live** (post-injection gap). 6. Upper confidence bound, shot count published.
**Reconciliation note (open, recorded)**: the two seats' SE(gap) tables differed 2× (#9055 vs #9057); Ember identified the error as hers (#9058, spurious factor on SE(C)) — Elder's `SE(gap)=√2·√((1−C²)/N)` is the frozen form. Recorded because the *resolution* is what makes 40 runs defensible.

## C. Custody (Ember's seat, unamended)
1. Blindness test with a **firing leaky control** (`tools/h13_cell2_blindness_test_elder.py`; returns VOID, not PASS, if the leaky control fails to fire). 2. W frozen in text pre-flight. 3. Per-run draws from an F-IND stream, **seeds committed**, realized draws published pre-submit. 4. Ceiling from the upper bound with shot count.

## D. Billing unit and what the statistic does NOT show (both sentences mandatory)
- ✗ **"the sign flip is the quantum signature" — FALSE.** Explicit classical local-deterministic shared-λ model (B_X=A_X, B_Y=−A_Y, B_Z=A_Z) reproduces the Φ⁺ diagonal sign pattern exactly (product −1.000, unbiased marginals). The diagonals carry no quantum signature by themselves.
- ✓ **"within QM a cause-effect chain is FORCED to all-positive diagonals by measurement repeatability, while a common cause is not; classically neither is forced" — TRUE, and it is the claim.** The discriminating work is done by the causal-structure argument (Ried 2015), not the correlator pattern.
- **Coherent-error caveat, closed by measurement not assumption**: sign-product immunity fails only for rotations > 120° about a near-body-diagonal axis; this chip's measured coherent phase error is **6.7°** (C5057 exp183 pin), ~18× below threshold. Single-axis rotations are immune at any angle (product = cos²θ ≥ 0) — stated as a robustness feature.
- **In-flight gate**: CE diagonals near 1−p with no near-zero crossing = passing idle; all three driven toward zero together is the only precursor of a flip.
- **Billing currency** (class-5 preflight): unit = **blind call-success over sealed matched records**, identical record count both arms; stopping rule = **fixed-N (40 runs), frozen here, pre-flight**; rejected convention = per-shot accounting (structural: the arms' shot-to-record maps differ).

## E. Decoder and NO-CALL (Elder, frozen pre-flight)
`tools/h13_cell2_decoder_elder.py`, statistic `sign(C_XX·C_YY·C_ZZ)`, selftest 5/5; **abstains** if any diagonal N<100 or |C|/se<5σ; a records file carrying arm/scenario/label keys is **REFUSED** (blindness enforced at the tool boundary). Record schema seam: `{"records":[{basis,a,b}]}`, 0/1 → +1/−1.

## F. Genre fence
If the realized run count or ceiling cannot support 5σ, the deliverable is a **well-fenced instrument/demonstration**, labelled as such — not a stretched advantage claim (Elder #9035).
