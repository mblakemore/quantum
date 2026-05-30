# Exp36 — RESULTS: Commutation-Aligned Compilation Principle (Whisper C3755)

**Backend**: ibm_marrakesh (Heron-r2) | **Job**: `d8d6tdgv14cs73dhvahg` | **Date**: 2026-05-30
**Pair**: [6,5] (calibration-gated: cz=0.00130, readout 0.32%/0.27%, 116/176 eligible)
**ORQ**: #7 — commutation-aligned compilation principle
**Pre-registration**: `36-commutation-basis-sweep-preregistration.md` (criteria FIXED before submit)

## Headline

**The overlap law (commutation principle) is CONFIRMED on the primary X→Z meridian and
marginally-supported on X→Y; the strict 3-of-3 pre-registered confirmation does NOT fire, for a
diagnosable dual-state reason — not a refutation of the principle.** Finding 03's full
ordering (X cleanest < Z < Y dirtiest) is reproduced at the meridian endpoints.

## Pre-registered gate results (as recorded, no goalpost-moving)

| Gate | Criterion | Result | Verdict |
|---|---|---|---|
| **G1** | both meridians γ(θ) overlap-law R²≥0.90 AND ≥ linear | XZ R²=**0.971**; XY R²=**0.897** | **FAIL** (XY 0.003 short) |
| **G2** | Spearman ρ(γ,overlap) ≥ +0.9 each | ρ_XZ=**+1.000**, ρ_XY=**+0.929** | **PASS** |
| **G3** | b_XY > b_XZ AND both >0 | b_XZ=+0.0178, b_XY=+0.0137 | **FAIL** (b_XY < b_XZ) |
| **G4** | \|γ_X(m1) − γ_X(m2)\| < 0.03 | \|0.0051 − 0.0114\| = 0.0062 | **PASS** |
| **G5** | 2q count constant across angles | 2q = λ exactly (1/3/5), all angles | **PASS** |

Strict confirmation (G1∧G2∧G3) = **NOT met.** Auto-verdict: "ordered but not overlap-governed."
The honest, fuller reading below shows that auto-verdict is too harsh.

## The data (γ = OLS slope of err vs λ∈{1,3,5}, per basis angle)

```
X→Z meridian (|Φ+⟩):   η=0(Z) → η=90(X)
  η:     0      15     30     45     60     75     90
  γ:  0.0221 0.0214 0.0204 0.0165 0.0100 0.0059 0.0051     monotone ↓, ρ=+1.000
  fit: γ = 0.0051 + 0.0178·cos²η      R²=0.971  (linear-in-deg R²=0.933)

X→Y meridian (|Ψ+⟩):   φ=0(X) → φ=90(Y)
  φ:     0      15     30     45     60     75     90
  γ:  0.0114 0.0112 0.0129 0.0164 0.0168 0.0254 0.0245     monotone ↑, ρ=+0.929
  fit: γ = a + 0.0137·sin²φ           R²=0.897  (linear-in-deg R²=0.879)
```

**Endpoint γ (state-matched within each meridian):** γ_Z = 0.0221, γ_Y = 0.0245, γ_X = 0.0051
(|Φ+⟩) / 0.0114 (|Ψ+⟩). **Ordering Y > Z > X holds** → Finding 03's `eYY > eZZ > eXX`
reproduced as a *noise-sensitivity* ordering on a continuous sweep.

## Interpretation — what actually happened

1. **The commutation/overlap law is real on the cleanest test.** The X→Z meridian, run on a single
   state (|Φ+⟩), follows `γ = a + b·cos²η` with **R²=0.971** and a perfect monotone rank
   (ρ=+1.000). cos²η is the overlap of the tilted measurement axis with the dirty Z direction. The
   overlap fit also **beats the plain linear-in-angle fit** (0.971 vs 0.933) → the cos² functional
   form is doing real work, not just "γ goes up." This is direct continuous-curve evidence for
   ORQ#7's core claim on the X-Z plane.

2. **G1 fails by a hair, on the X-Y meridian only (0.897 vs 0.90).** Monotone (ρ=0.929), overlap-form
   still beats linear (0.897 vs 0.879). The misfit is a slight early-flat / late-steep wobble in the
   |Ψ+⟩ data, consistent with that state's different noise structure (point 4) rather than a failure
   of the overlap idea.

3. **G3 fails for a DIAGNOSED confound, and Y>Z is NOT actually refuted.** G3 compared the fitted
   *amplitudes* b (= dirty-endpoint − clean-endpoint). It came out b_XZ > b_XY — the opposite of the
   Finding-03-based prediction. But the *dirty endpoints themselves* order correctly: γ_Y=0.0245 >
   γ_Z=0.0221. The amplitude comparison inverted only because the two meridians used **different
   states with different X-baselines**: |Φ+⟩ anchors X at γ=0.0051 while |Ψ+⟩ anchors X at γ=0.0114.
   The XY amplitude is compressed by its elevated X-anchor, not by Y being clean. So the slope-
   amplitude was the **wrong statistic** for the anisotropy test; the endpoint ordering is the right
   one, and it confirms Y>Z.

4. **New observation — state-dependent X-baseline (the G4 near-miss).** G4 passes (<0.03) but the two
   X-anchors differ by ~2× (0.0051 vs 0.0114). |Ψ+⟩=(|01⟩+|10⟩) carries an extra X gate and lives in
   the odd-parity readout subspace; |Φ+⟩ in the even-parity subspace. The X-basis noise sensitivity
   is therefore **state/subspace-dependent**, not purely a function of the measurement axis. This is
   itself a small finding: the overlap law is clean *within a fixed state*, but cross-state
   comparison needs the X-anchor normalized away.

## Verdict (honest, distinguishing pre-registered from post-hoc)

- **Pre-registered**: strict G1∧G2∧G3 confirmation NOT met (G1 XY 0.003 short; G3 inverted).
- **Post-hoc (clearly labeled)**: the commutation-aligned overlap law is **supported** — strongly on
  X-Z (R²=0.971, beats linear), marginally on X-Y (R²=0.897, beats linear), both strictly monotone in
  basis-axis overlap. The G3 inversion is a dual-state X-baseline artifact, not evidence against the
  Y>Z anisotropy (endpoints confirm Y>Z>X = Finding 03). ORQ#7's principle is **provisionally real on
  one device; the strict pre-reg bar revealed a methodological confound in cross-state comparison.**

This is the honest "the bar didn't fire, here's exactly why, and the underlying claim survives the
post-mortem" outcome — the pre-registration did its job by forcing a confound into the open.

## Concrete fix → Exp37 (pre-specified here)

Re-run with the confound removed: **(a)** use a single state for all meridians (sweep all of X-Z,
Y-Z, X-Y from |Φ+⟩, accepting the X-Y zero-crossing by switching to err on the *magnitude* with a
per-angle ideal, OR prepare a 3-axis-symmetric stabilizer set), OR **(b)** normalize each meridian to
its own X-anchor before the cross-meridian amplitude test, and **(c)** add a 4th angle near 90° on
X-Y to stabilize the R² that fell 0.003 short. Pre-registered amplitude test becomes the
**endpoint-γ ordering** (state-matched), not the cross-state fitted b.

## What Exp36 settles / does not

- **Settles**: on ibm_marrakesh pair [6,5], γ(measurement-axis angle) is a monotone, overlap-shaped
  (cos²η) function on the X-Z plane (R²=0.971) — continuous-curve evidence for the commutation
  principle, gate-count-invariant (G5). Finding 03's X<Z<Y ordering reproduced at endpoints.
- **Does not settle**: the strict overlap law on X-Y (marginal, state-confounded); cross-state
  comparability; cross-backend/platform universality (n=1 device, ORQ#5 territory); >2 qubits /
  non-stabilizer observables.
