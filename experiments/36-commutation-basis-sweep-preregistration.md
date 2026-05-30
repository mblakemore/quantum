# Exp36 — PRE-REGISTRATION: Commutation-Aligned Compilation Principle (Whisper C3755)

**Backend**: ibm_marrakesh (Heron-r2, the Finding-03 anchor device) | **Date**: 2026-05-30
**ORQ**: #7 — "Is the X-basis immunity a special case of a broader *commutation-aligned
compilation* principle? Finding 03's mechanism is that the X-readout basis aligns with the
heavy-hex CZ channel's Z-biased noise. Generalize: for any noise channel, the measurement error
of an observable should be a smooth, predictable function of the *angle* between the observable's
measurement axis and the noise-commuting axis — a whole compilation discipline buried in the
3-point ordering."

## Why this experiment exists

Finding 03 reports **three discrete points**: err `XX < ZZ < YY` (X-basis cleanest, Y-basis
dirtiest, Z intermediate) on the Bell state, replicated across Bell/GHZ/VQE (C3649–C3651,
C3746). Exp34 confirmed the *ordering/mechanism* generalizes across Heron devices even where the
~3× *magnitude* does not. But "three points" is not a principle — it is three samples of an
unknown curve.

The **commutation-aligned hypothesis** (ORQ#7) says those three points lie on a single smooth
curve: the measurement error of a correlator measured along a tilted Bloch axis `n̂(θ)` is
governed by the *overlap* of `n̂` with the channel's noisy (anti-commuting) direction. If the
heavy-hex CZ channel is Z-biased and the X-readout basis is the commuting (clean) axis, then
rotating the measurement axis away from X toward Z (or toward Y) should raise the error along a
**cos²/sin² overlap law**, not arbitrarily. Confirming the *functional form* — not just the
ordering — turns "X is special" into an actionable compilation rule: *route any observable toward
the noise-commuting axis; the fidelity gain is predictable from the misalignment angle.*

This is a clean `do(measurement-basis angle θ)` intervention: I hold the prepared state and the
entangling gate fixed and vary only the pre-measurement rotation, sweeping the readout axis
continuously around the Bloch sphere. Everything downstream of the Bell pair is identical except θ.

## Design

**Two flat-ideal meridians**, both anchored at the empirically-cleanest **X axis**, chosen so the
*ideal* correlator is **+1 flat across the whole sweep** (so measured error is purely a noise
effect, with no ideal-value normalization artifact):

- **Meridian 1 (X→Z), state |Φ+⟩ = (|00⟩+|11⟩)/√2.** Stabilizer correlators ⟨XX⟩=+1, ⟨ZZ⟩=+1,
  ⟨YY⟩=−1. For a tilted axis in the X-Z plane `n̂(η)=(sin η, 0, cos η)` (η = polar angle from Z),
  ideal ⟨n̂⊗n̂⟩ = sin²η·⟨XX⟩ + cos²η·⟨ZZ⟩ = +1 **for all η** (cross terms ⟨XZ⟩=⟨ZX⟩=0). η=90°→X,
  η=0°→Z. Tests X vs Z.
- **Meridian 2 (X→Y), state |Ψ+⟩ = (|01⟩+|10⟩)/√2.** Stabilizer correlators ⟨XX⟩=+1, ⟨YY⟩=+1,
  ⟨ZZ⟩=−1. For a tilted axis in the X-Y plane `n̂(φ)=(cos φ, sin φ, 0)`, ideal ⟨n̂⊗n̂⟩ =
  cos²φ·⟨XX⟩ + sin²φ·⟨YY⟩ = +1 **for all φ** (⟨XY⟩=⟨YX⟩=0). φ=0°→X, φ=90°→Y. Tests X vs Y.

Both meridians' X-endpoint is the same physical X-basis measurement on a maximally-entangled
state → an internal consistency anchor (G4). Using |Ψ+⟩ rather than |Φ+⟩ for meridian 2 is what
makes the X-Y sweep flat-ideal (|Φ+⟩ would cross zero at φ=45°, defeating clean attribution).

**Angles**: {0, 15, 30, 45, 60, 75, 90}° per meridian (7 each).
**ZNE**: global-fold λ∈{1,3,5} per angle (dynamic range — at λ=1 alone the good-pair X↔Z gap is
~1pp ≈ shot noise; ZNE amplification spreads the basis-dependent error so the overlap-law shape is
measurable). `err(θ,λ) = 1 − |⟨n̂n̂⟩(θ,λ)|`; `gamma(θ)` = OLS slope of err vs λ = the
**noise-sensitivity** of basis angle θ (this is the quantity Finding 03 reported as γ_XX/γ_YY/γ_ZZ
— here generalized to a continuous γ(θ)).
**Circuits**: 2 meridians × 7 angles × 3 λ = **42 circuits**, 4096 shots, one co-submitted job
(single calibration snapshot ⇒ daily drift cancels in the relative fits).

## Calibration gate (FIXED before submission)

Identical to Exp34's `do(layout=good)` gate (it is the validated recipe from Exp32 floor
spectroscopy): scan every coupled pair `(a,b)`; eligible iff `readout(a)≤0.05` AND
`readout(b)≤0.05` AND non-null T1/T2 on both AND `cz_error(a,b)<0.01`. Select argmin
`cz_error + 0.25·(ro_a+ro_b)`. Pin via `initial_layout=[a,b]`, `optimization_level=0` (preserves
ZNE folds, C3720), `seed_transpiler=42`. ZERO eligible → ABORT (no silent bad-pair fallback).

## Pre-registered criteria (FIXED before submission)

For each meridian fit the **overlap law** to γ(θ) (primary) and to err(θ) at λ=5 (secondary):
- Meridian 1 (X→Z): `γ(η) = a + b·cos²η`  (cos²η = overlap with the dirty Z axis; b>0 ⇒ Z dirtier)
- Meridian 2 (X→Y): `γ(φ) = a + b·sin²φ`  (sin²φ = overlap with the dirty Y axis; b>0 ⇒ Y dirtier)

- **G1 (OVERLAP LAW, headline)**: both meridians' γ(θ) fit to the cos²/sin² law with **R² ≥ 0.90**.
  This is the novel test — the continuous curve follows the *predicted functional form*, not just
  the ordering. (Reported alongside R² of a plain linear-in-θ fit; the overlap law must not be
  beaten by a generic linear fit, i.e. the cos²/sin² basis is doing real work.)
- **G2 (MONOTONICITY)**: Spearman ρ(γ, overlap) ≥ +0.9 on each meridian (γ rises X→Z and X→Y).
- **G3 (ANISOTROPY)**: `b_XY > b_XZ` AND both `b > 0` — reproduces Finding 03's `eYY > eZZ` as a
  *curve-amplitude* fact (Y anti-commutes more strongly than Z with the readout-aligned channel),
  and quantifies the non-Z-pure residual of the heavy-hex CZ channel.
- **G4 (X-ENDPOINT CONSISTENCY)**: `|γ_X(meridian1) − γ_X(meridian2)| < 0.03` — same physical
  X-measurement on an entangled state from two builds; a sanity anchor.
- **G5 (do-CONTROL, gate invariance)**: transpiled 2q-gate count is **constant across all angles**
  within a meridian (the pre-measurement rotation is single-qubit; arbitrary θ decomposes to a
  fixed rz–sx–rz–sx–rz structure). Reported per circuit. Confirms the γ(θ) curve is
  basis-rotation-driven, NOT a gate-count / depth confound.

**G1 ∧ G2 ∧ G3 PASS** → the **commutation-aligned compilation principle is CONFIRMED**: Finding 03's
X-immunity is one point on a smooth, predictable overlap curve. Upgrades the finding from
"X-basis is special" to a continuous compilation discipline (route observables toward the
noise-commuting axis; gain = predictable cos²/sin² of the misalignment), and decomposes the
heavy-hex CZ channel's directional anisotropy (G3) — actionable for any observable, not just XX.

**G1 FAIL** (γ(θ) not well-fit by the overlap law) → the principle is too simple for this channel;
the noise has higher-order angular structure that a single cos²/sin² term cannot capture. Honest
negative: the 3-point ordering is real (if G2 holds) but does not generalize to a clean continuous
law — ORQ#7 reframed as "ordered but not overlap-governed."

## What Exp36 can and cannot settle

- **CAN**: whether the basis-dependent noise on this device follows the overlap law as a continuous
  function of measurement angle (the core ORQ#7 claim); the X-vs-Z vs X-vs-Y anisotropy as
  fitted curve amplitudes; that the effect is basis-rotation-driven not gate-count-driven (G5).
- **CANNOT**: cross-backend / cross-platform universality (Exp34/ORQ#5 territory; n=1 device here);
  the microscopic origin of the residual Y-anisotropy (G3 quantifies it, does not explain it);
  whether the law holds for non-stabilizer observables or >2 qubits (future). Anchored to
  ibm_marrakesh Heron-r2 — methodology generalizes, absolute numbers do not.
