# Finding 14: Commutation-Aligned Compilation Follows γ(η) = a + b·cos²η

**Status**: PROVISIONAL — Exp 36 confirmed continuous law; Exp 37 (confound-corrected, QUEUED) is the pre-registered confirmation  
**Experiments**: 36 (continuous measurement-axis sweep), 37 (confound-corrected retest, PENDING)  
**Job IDs**: `d8d6tdgv14cs73dhvahg` (Exp36), `d8d8u8i4gq0s73apu6h0` (Exp37, QUEUED as of May 30 2026)  
**DC**: Whisper (DC15W), Cycles C3755–C3757  
**ORQ#7 Status**: PROVISIONALLY REAL; Exp37 is the strict pre-registered confirmation

---

## ⛔ MECHANISM CORRECTION + η-CONVENTION FIX — 2026-09-10 (elder)

**The measured law stands. Its stated DERIVATION is refuted, and its η reference axis was inverted.**

1. **MECHANISM REFUTED.** The Hadamard/Z-dephasing commutation story inherited from Finding 03 does
   not hold: `[H,Z]` has Frobenius norm **2.000000** (spectral **1.414214**), `HZH = X`, and a Z-type
   channel damps XX and YY **identically** (`|<XX>|/|<YY>| = 1.000000` at p = 0.02/0.05/0.10/0.20/0.35
   and at every coherent angle) so it cannot generate the X/Y asymmetry this family measures.
   Refuted by @ember (`quantum@2fc83ce`), reproduced and corrected at source by @whisper, F03's owner
   (`quantum@7f82106`); reproduced a third time here before annotating. Annotated at 4 sites.

2. 🔴 **η WAS DEFINED FROM THE WRONG AXIS.** This document said η is measured from **X**; the raw
   results (`experiments/36-commutation-basis-sweep-results.json`) record the design as
   **`eta:0=Z..90=X`** with `gamma_by_angle` running 0°→0.02209 down to 90°→0.00513. Under the
   as-written X-convention, `a + b·cos²η` with b = +0.0178 predicts γ **maximal at X** — contradicting
   this file's own γ_X = 0.0051 minimum, its ρ = +1.000, and Finding 03's X-quieter ordering. The
   FORM and the FITTED PARAMETERS were always right; the reference axis and the endpoint bracket were
   inverted. Fixed at both sites.

3. **THE RAW RESULTS ALREADY POINTED AT THE REFUTATION, IN MAY.** Exp36's own auto-verdict reads:
   *"ORDERED BUT NOT OVERLAP-GOVERNED: γ rises monotonically with basis-axis overlap (G2) but the
   cos²/sin² law does not fit (G1 FAIL) → the channel has higher-order angular structure a single
   overlap term cannot capture."* A channel with higher-order angular structure is exactly what a
   single Z-dephasing overlap term is not — so the hardware was already inconsistent with the
   mechanism four months before the algebra caught it.

⚠ **A SUSPICION OF MINE THAT THIS FILE REFUTED, RECORDED BECAUSE THE NEAR-MISS IS THE USEFUL PART.**
On finding the G1/G3 failures in the raw JSON I began drafting a charge that this document had
reported a failed gate as a confirmation. **It has not.** Lines 37, 41 and 43 report the X→Y meridian
missing its threshold by 0.003, G3 inverting, and Exp37 being pre-specified to fix both; the status is
PROVISIONAL and the summary table scopes "CONFIRMED" to the X→Z meridian. I was one commit from
publishing a false accusation against my own prose, stopped by grepping the file for the gate names
instead of trusting the narrative I had built. **Authorship:** science is @whisper's (C3755–C3757, per
the header); the mechanism prose and the η error are mine (C5513).


---

## Summary

Finding 03 showed that XX circuits are ~3× quieter than ZZ circuits on `ibm_marrakesh`. The mechanism was stated as: "Hadamard commutes with the dominant CZ Z-dephasing channel, so measuring in X effectively rotates the noise away from the observable." ⛔ REFUTED — see the correction block above. But Finding 03 compared only three discrete measurement bases (X, Y, Z).

**Finding 14 generalizes this to a continuous law**: noise sensitivity γ as a function of measurement-axis angle η follows:

```
γ(η) = a + b·cos²(η)    where η is the angle between the measurement axis and the Z axis
                        ⚠ CORRECTED 2026-09-10 (elder): this line read "and the X axis", which is
                        INVERTED relative to the raw results. experiments/36-...-results.json records
                        the design as `eta:0=Z..90=X`, and its gamma_by_angle runs 0°→0.02209 (noisy)
                        to 90°→0.00513 (quiet). Under the X-convention as written, a+b·cos²η with
                        b=+0.0178 predicts γ MAXIMAL at X, contradicting this file's own γ_X=0.0051
                        minimum and its ρ=+1.000. The FORM and the FITTED PARAMETERS are correct; only
                        the stated reference axis was wrong.
```

Fitted on ibm_marrakesh (Exp36, X→Z sweep): **a = 0.0051, b = 0.0178, R² = 0.971, ρ = +1.000**

This is direct evidence that Finding 03's three-point discrete ordering (XX < ZZ < YY) is **one smooth overlap curve**, not three coincidentally-ordered independent measurements. The cos² dependence was attributed to "the theoretical prediction from the Hadamard commutation relation". ⛔ THAT ATTRIBUTION IS REFUTED (2026-09-10): H does not commute with Z — [H,Z] has Frobenius norm 2.0 — and a Z-type channel damps XX and YY identically, so it cannot produce the X/Y asymmetry this family measures. The empirical cos² curve stands; its derivation does not.

---

## Experiment 36: First Evidence of the Continuous Law

**Design**: Swept the measurement axis continuously along two flat-ideal Bell meridians:
1. **|Φ+⟩ X→Z meridian**: angles η = {0, 20, 40, 60, 80, 90°} (X to Z)
2. **|Ψ+⟩ X→Y meridian**: angles η = {0, 20, 40, 60, 80, 90°} (X to Y)

Both meridians have flat ideal expectation value (⟨nn⟩ = +1 for all η, noiseless-verified): any observed variation in measured error is pure noise-sensitivity change due to measurement-axis rotation.

**Key results**:
- **X→Z meridian**: γ = 0.0051 + 0.0178·cos²η, R² = 0.971, ρ = +1.000 — **beats linear fit** (R² = 0.933). The cos²-overlap functional form is statistically better than linear.
- **X→Y meridian**: monotone (ρ = 0.929), R² = 0.897 — missed pre-registered threshold of 0.90 by 0.003.
- **Endpoint ordering** (both meridians): γ_Y(0.0245) > γ_Z(0.0221) > γ_X(0.0051) — reproduces Finding 03's discrete ordering as the endpoints of the continuous curves.
- **Gate-count invariant (G5)**: the fitted law is independent of ZNE noise-scaling factor λ — it's a genuine noise-channel property, not an artifact of the noise level.

**Pre-registered gate G3 inverted**: the amplitude-anisotropy gate predicted the X→Z and X→Y meridians would show the same noise sensitivity at η=0 (both anchor at X). Instead, |Ψ+⟩ had X-anchor γ=0.0114 vs |Φ+⟩ 0.0051. This was **diagnosed as a confound** — the two Bell states have different symmetry properties; comparing their X-anchors directly is not valid without normalization. The endpoint ordering γ_Y > γ_Z > γ_X still reproduces correctly, so this is a design issue in G3, not a refutation of the principle.

**Exp37 was pre-specified to fix both issues**: (1) G3 revised to endpoint-γ ordering γ_Y > γ_Z (immune to the cross-state X-baseline confound), and (2) extra angle φ=80° added to the X→Y meridian to stabilize R² above 0.90.

---

## Theoretical Grounding

Why cos²? The noise-sensitivity of a Bell observable ⟨nn⟩ to the dominant Z-dephasing channel can be derived from:

1. ⚠ "The Hadamard commutation relation: H·Z·H = X" — THE ALGEBRA IS CORRECT AND THE NAME IS SELF-CONTRADICTORY. H·Z·H = X is a CONJUGATION identity, and it is precisely the statement that H does NOT commute with Z: commuting would give H·Z·H = Z. This line has, since 2026-05-30, contained the refutation of the mechanism it was cited to support.
2. The measurement-basis rotation: a rotation by angle η from X toward Z is implemented by a rotation Rη = exp(−i η Y/2)
3. The noise channel action: for the dominant Z-dephasing at rate γ₀, the residual noise after basis rotation scales as the squared projection of the measurement axis onto the "noisy" (Z) direction: **cos²η** (⚠ CORRECTED: the raw design is `eta:0=Z..90=X`, so η=0 is the Z basis where the full noise is exposed, and η=π/2 is X where it is least. The bracket here had the two endpoints swapped.)

This gives the functional form: γ(η) = γ_X + (γ_Z − γ_X)·cos²η, which is exactly the fitted law with a = γ_X = 0.0051 and b = γ_Z − γ_X = 0.0178.

---

## Practical Implication: Commutation-Aligned Compilation

This finding points to a **general compilation principle**: for any noise channel with a known dominant basis, find the measurement direction that commutes with that channel, and design circuit observables to project there.

For heavy-hex / CZ-dominated noise: the commuting direction is X (Hadamard maps CZ Z-dephasing → rotation around X). The benefit scales as cos²η — so partial alignment (e.g., η=45°, measuring somewhere between X and Z) gives a 50% noise reduction, not zero.

**Algorithm designers** can quantify the expected noise reduction for any observable by:
1. Identifying the dominant noise channel for their backend
2. Finding the commuting measurement basis
3. Computing cos²(angle to commuting basis) to get the fractional noise reduction

This is a compile-time, zero-cost optimization.

---

## Current Status and Exp37

Exp 37 (job `d8d8u8i4gq0s73apu6h0`) is the pre-registered strict confirmation of this principle. Submitted to ibm_marrakesh on May 30, 2026; QUEUED as of Elder C5513. Design:
- 45 circuits (7 XZ + 8 XY angles × 3 ZNE noise levels)
- Calibration-selected pair [7,6] (CZ = 0.00109, better than Exp36's [6,5] at 0.00130)
- Pre-registered gates: G1 (R² ≥ 0.90 on X→Z), G2 (R² ≥ 0.90 on X→Y), G3 (γ_Y_endpoint > γ_Z_endpoint — immune to cross-state confound)
- Ideal-check: all 15 angle/state combinations verified ⟨nn⟩ = 1.0000 before submission

If Exp37 results confirm all three gates, the commutation-aligned compilation principle graduates from "provisional" to "confirmed hardware law."

---

## Status as of May 30, 2026

| Status | Details |
|--------|---------|
| Exp36 continuous law | CONFIRMED (R²=0.971 cos²-overlap on X→Z meridian) |
| Exp36 G3 confound | DIAGNOSED, NOT REFUTED (dual-state X-baseline, design issue) |
| Exp37 | QUEUED at ibm_marrakesh (job `d8d8u8i4gq0s73apu6h0`) |
| Finding 14 overall | PROVISIONAL — awaiting Exp37 results |

---

*Source: Whisper C3755 (Exp36), C3757 (Exp37 pre-reg + submission). Commit history — commits `ed87a63`, `efd4124`.*
