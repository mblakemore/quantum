# F122 Distribution — incremental-atomic prereg (FROZEN)

**Author**: Whisper (DC15W), C5048 (2026-08-10) · register seat · **Substrate**: claude-fable-5
**Purpose**: turn the single-instance F122 ("The Sealed Shadow") 9.3× point into a *distribution* over sealed P — the one thing that upgrades it from "an advantage demonstrated on one draw" to "a robust advantage" for external submission (Gate 2 of the IBM-readiness assessment, #8332).
**Batch authorization**: Creator go `general#8362` ("fly the distribution, n3") — a **bounded** batch-go for **N ≤ 3** F122-distribution instances. Consistent with the single-use, seal-bound clause (#7813/#7814) at the batch grain: bounded-N stated up front, every per-instance digest published before its own flight, instance 4 would need a fresh go, no retroactive authorization (author-seat ruling #8349).
**FROZEN before any seal exists.** This file's hash binds each instance's seal. Frozen precedes sealed precedes submitted; the ordering is checkable against git and bus timestamps.
**Flight seat**: Ember (`tools/doorb_distribution_batch_ember_c4268.py`). **Decode seat**: Elder. **Same three-seat blind court as F122.**

## 1. The claim
> Over **N** sealed instances (N = flown, never attempted), the two-copy Bell protocol recovers each hidden Pauli's amplitude at ≥5σ, and beats the proven single-copy floor by a **distribution** of ratios — establishing that F122's 9.3× is not a lucky draw and measuring how the ratio varies with the sealed Pauli's weight.

**Currency**: copies of ρ only. Classical post-processing is Θ(4ⁿ) on both arms and is **not** part of the claim (the F121 fence).
**Floor**: Ω(2ⁿ/ε²), Chen–Gong–Ye FOCS 2024, **Definition 1 + Definition 6** (adaptive single-copy — Gate 1 discharged, two independent source extractions, Whisper + Elder #8341). Evaluated at each instance's **delivered** ε.

## 2. Design (each answers a question F122's single instance could not)
- **N ≤ 3**, each a fresh sealed P, incremental-atomic: instance i is sealed → flown → decoded before instance i+1 begins. The claim is always over the instances **flown**, so a short batch cannot be a truncation of a registered plan (it was never registered ahead of flight).
- **P drawn UNIFORM-RANDOM over non-identity 16-strings** (the theorem's own hard-family draw), NOT weight-fixed. This gives a **weight spread**; since delivered ε depends on weight (heavier Paulis decohere more — F122 grade note), the 3-point spread measures the **ratio-vs-weight relationship**, simultaneously answering "lucky draw?" and filling F122's R3 (the ε-vs-weight law a family claim needs).
- **Per-instance sizing**: T(ε) = 4·ln(2·4ⁿ/δ)/ε⁴ (δ=0.05), the F122 frozen function, sized to *that instance's own* delivered ε read from its leading calibration job in the epoch it occupies. No standalone probe (stale-epoch, #7501).
- **Prior seal archived before each new draw** (the sealer's overwrite-refusal is satisfied, not bypassed — scripted in the harness, #8352).

## 3. Per-instance gates (identical to F122; each instance graded independently)
- **F1** — planted tr(Pρ)² > decision bar at ≥5σ, separation ≥ (a stated multiple) over the largest blind probe.
- **F2** — flown budget ≥ T(delivered ε).
- **F3** — decode pipeline reproduces closed-form truth on the verification subset.
- **F-BIAS / F-IND / F-MIX** — all fire correctly (buggy control arms fire, fixed arms pass) before science shots, per instance.
- **G-CRN / G-BACKEND / G-FIT / G-SEAL** — full-CRN pin, `ibm_marrakesh` asserted, per-job balance re-read, seal matches pinned commitment, per instance.

## 4. Budget and the legitimate short-batch outcome
Live tank at freeze: **371s** (read live, never remembered). F122 billed 109s. Modelled depletion 371→262→153: three fit with ~44s spare **at F122-class ε**. **T scales as ε⁻⁴**, so if any instance's epoch delivers a worse ε, that instance's T grows and it may not fit — **G-FIT halts it cleanly**. **"3 attempted, k flown" (k<3) is a PRE-DECLARED LEGITIMATE OUTCOME**, reported as *the budget gate working*, with the headline stating **n = flown**. This is not truncation: incremental-atomic means no instance was ever registered ahead of its flight.

## 5. Grade-time (register-seat commitments)
- Each instance's ratio evaluated at its **delivered** ε (the conservative amplitude), reported with its P's weight.
- The distribution reported as {ratio_i, weight_i, ε_i, σ_i} over the N flown — a spread and, if 3 points allow, a ratio-vs-weight trend (stated as trend, not law, at n≤3).
- Budget defense per instance stands on the union bound over 4ⁿ labels (#7780).
- Blind court: no P in any manifest; decode against the sealed commitment; decisions hashed before unseal; the same words for every outcome, PASS or FAIL.

## 6. What this is NOT
Not a new claim beyond F122 — it is F122's robustness check. Not a family theorem (n≤3 is a spread, not a distribution proof). Not a runtime/total-work advantage. Not sign-learning. The single-copy lane never "succeeds" — it provably cannot at these budgets.

---
*Frozen. On the Creator's batch-go #8362, Ember draws instance-1's seal, publishes its digest, and flies; each subsequent instance archives the prior seal, reads the live tank, seals, flies, decodes. The register seat verifies each instance's T(ε) arithmetic at its calibration decode and defends the budget at grade.*
