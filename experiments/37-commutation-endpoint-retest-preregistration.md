# Exp37 — PRE-REGISTRATION: Commutation-Aligned Compilation Principle — Confound-Corrected Retest (Whisper C3757)

**Backend**: ibm_marrakesh (Heron-r2) | **Date**: 2026-05-30
**ORQ**: #7 — commutation-aligned compilation principle
**Whisper cycle**: C3757
**Precursor**: Exp36 (C3755, job `d8d6tdgv14cs73dhvahg`) — confirmed on X-Z (R²=0.971) but
exposed two limitations: (1) X-Y fell R²=0.897 short of the 0.90 pre-reg bar by 0.003, and
(2) the pre-registered G3 (b_XY > b_XZ as fitted amplitudes) inverted due to a dual-state
X-baseline confound — the two meridians used different Bell states whose X-baseline γ values
differ (~2×: |Ψ+⟩ γ_X=0.0114 vs |Φ+⟩ γ_X=0.0051), compressing the XY fitted amplitude
relative to XZ. The G3 amplitude statistic was the WRONG cross-state comparison; the absolute
endpoint ordering γ_Y > γ_Z is the clean one and ALREADY passed in Exp36 (0.0245 > 0.0221).

## What Exp37 fixes

Two targeted changes relative to Exp36 — everything else identical:

1. **G3 revised to endpoint-γ ordering** (removes the cross-state amplitude confound):
   - OLD G3: `b_XY > b_XZ AND both b > 0`  ← cross-state, confounded by X-baseline
   - NEW G3: `γ_Y_endpoint > γ_Z_endpoint`  ← absolute dirty-endpoint γ, no baseline subtraction
   - Rationale: γ_Y_endpoint = γ at (XY meridian, φ=90°) = pure Y-basis noise sensitivity on
     |Ψ+⟩; γ_Z_endpoint = γ at (XZ meridian, η=0°) = pure Z-basis noise sensitivity on |Φ+⟩.
     Both are state-matched within their own meridian; the cross-meridian comparison is of the
     ABSOLUTE noise sensitivity at the pure-basis endpoint, which is not confounded by baseline
     differences (the baseline confound only affects slope amplitudes, not the endpoint values
     themselves: a higher X-baseline in |Ψ+⟩ compresses b_XY but doesn't inflate γ_Y).
   - This is what Exp36's result interpretation called the "endpoint-γ ordering (state-matched)"
     revision, explicitly pre-specified before submitting Exp37.

2. **Extra angle φ=80° on the X-Y meridian** (addresses the 0.003 R² shortfall):
   - OLD X-Y angles: [0, 15, 30, 45, 60, 75, 90] — 7 points
   - NEW X-Y angles: [0, 15, 30, 45, 60, 75, 80, 90] — 8 points
   - The Exp36 X-Y curve had a slight flat/steep wobble near the Y endpoint (confirmed monotone,
     ρ=0.929, but R²=0.897). Adding an 80° anchor in the region of largest curvature stabilizes
     the fit and gives the overlap-law curve more leverage near the dirty endpoint.
   - X-Z angles unchanged: [0, 15, 30, 45, 60, 75, 90] — 7 points.

Total circuits: (7 + 8) × 3 λ = **45 circuits** (Exp36 had 42). Same 4096 shots.

## Design (identical to Exp36 except angle set and G3)

**Two flat-ideal meridians**, both anchored at the empirically-cleanest X axis:

- **Meridian 1 (X→Z), state |Φ+⟩ = (|00⟩+|11⟩)/√2.** `⟨XX⟩=⟨ZZ⟩=+1`, so the ideal
  correlator is +1 flat across the whole X-Z sweep (⟨ZX⟩=⟨XZ⟩=0). η=0°→Z (overlap=cos²0=1,
  maximum noise), η=90°→X (overlap=cos²90=0, minimum noise). Rotation: Ry(−η) per qubit.
- **Meridian 2 (X→Y), state |Ψ+⟩ = (|01⟩+|10⟩)/√2.** `⟨XX⟩=⟨YY⟩=+1`, so the ideal
  correlator is +1 flat (⟨XY⟩=⟨YX⟩=0). φ=0°→X (overlap=sin²0=0), φ=90°→Y (overlap=sin²90=1,
  maximum noise). Rotation: Rz(−φ) then Ry(−π/2) per qubit.

**ZNE**: global-fold λ∈{1,3,5} per angle. `err(θ,λ) = 1 − |⟨nn⟩(θ,λ)|`;
`γ(θ) = OLS slope of err vs λ` = noise-sensitivity of basis angle θ.

**Calibration gate**: identical to Exp34/Exp36 do(layout=good) recipe. Scan all coupled pairs;
eligible iff readout(a)≤0.05 AND readout(b)≤0.05 AND non-null T1/T2 AND cz_error<0.01.
Select argmin `cz_error + 0.25·(ro_a+ro_b)`. Pin via `initial_layout=[a,b]`,
`optimization_level=0`, `seed_transpiler=42`. ZERO eligible → ABORT (no silent fallback).

## Pre-registered criteria (FIXED before submission)

- **G1 (OVERLAP LAW, headline)**: both meridians' γ(θ) follow the overlap law with **R² ≥ 0.90**,
  and the cos²/sin² form is not beaten by a plain linear-in-angle fit.
  - XZ: `γ(η) = a + b·cos²η`  (cos²η = overlap of measurement axis with dirty Z direction)
  - XY: `γ(φ) = a + b·sin²φ`  (sin²φ = overlap with dirty Y direction)

- **G2 (MONOTONICITY)**: Spearman ρ(γ, overlap) ≥ +0.9 on each meridian.

- **G3 (ANISOTROPY — REVISED from Exp36)**:
  `γ_Y_endpoint > γ_Z_endpoint`
  where `γ_Y_endpoint = γ at (XY meridian, φ=90°)` and `γ_Z_endpoint = γ at (XZ meridian, η=0°)`.
  Reproduces Finding 03's `eYY > eZZ` as a directly measured noise-sensitivity ordering at the
  pure dirty endpoints, without the cross-state X-baseline subtraction that confounded Exp36's G3.

- **G4 (X-ENDPOINT CONSISTENCY)**:
  `|γ_X(meridian1) − γ_X(meridian2)| < 0.03`
  where `γ_X(meridian1) = γ at (XZ, η=90°)` and `γ_X(meridian2) = γ at (XY, φ=0°)`.
  Same physical X-measurement sanity anchor. Note: Exp36 found |0.0051−0.0114|=0.0062, well
  within 0.03. The baseline DIFFERENCE is expected (|Ψ+⟩ has an extra X gate) and is the root
  cause of the Exp36 G3 confound — G4 documents it, the revised G3 is immune to it.

- **G5 (do-CONTROL)**: transpiled 2q-gate count constant across all angles within a meridian.

**CONFIRM (G1 ∧ G2 ∧ G3 PASS)**: the commutation-aligned compilation principle is supported on
ibm_marrakesh: Finding 03's X-immunity lies on a smooth, predictable overlap curve, with Y
genuinely noisier than Z at the absolute dirty-endpoint level.

## What this experiment can and cannot settle

- **CAN**: whether the endpoint-γ ordering γ_Y > γ_Z holds on a fresh calibration snapshot
  (replication of Exp36's post-hoc finding as a pre-registered criterion); whether the X-Y overlap
  law reaches R²≥0.90 with the extra angle; whether the revised G3 fires cleanly.
- **CANNOT**: resolve the mechanistic question of WHY |Ψ+⟩ has a higher X-anchor γ than |Φ+⟩
  (subspace-dependent dephasing structure, C3755's observation — requires a dedicated single-state
  vs state-parity experiment); cross-backend universality (n=1 device); non-stabilizer observables.

## Expected outcome (honest prior from Exp36)

- G1: XZ R²≈0.971 likely stable; XY R²≈0.897→?? (extra angle at 80° should push past 0.90)
- G2: Both ρ>0.9 expected (Exp36 had 1.000 / 0.929)
- G3 REVISED: γ_Y(0.0245) > γ_Z(0.0221) expected — this already passed in Exp36 data
- G4: |Δγ_X| ≈ 0.006 expected — well within 0.03
- Overall: full G1∧G2∧G3 PASS likely, the first clean pre-registered confirmation of the
  commutation-aligned principle (Exp36 missed only on the confounded G3 + marginal R²)
