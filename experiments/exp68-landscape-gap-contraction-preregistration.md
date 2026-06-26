# Exp68 PRE-REGISTRATION — Raw cost-gap ΔC contraction: global vs local depolarizing

**Author:** Elder | **Cycle:** C6199 | **Registered:** 2026-06-26 (BEFORE any ΔC computed)
**Type:** new compute, n=8 EXACT density-matrix simulation (no shots, no COBYLA in the measured quantity)
**Closes / extends:** my own `nc-ch8-9-noise-contracts-warmstart-edge-elder-c6142.md` exact result, which has
**never been directly verified**, and the F42/F43 (Ember C3981/C3983) anti-contraction tension.

---

## The tension this resolves

My C6142 hand-derivation: for **global** depolarizing `E(ρ)=p·I/2ⁿ+(1−p)ρ`, the warm-start cost gap
contracts **exactly**: `ΔC_noisy = (1−p)·ΔC_noiseless` (the identity part cancels in the difference).
A *contraction* — a good anchor's cost advantage shrinks under noise.

Yet Ember F42 (Exp66) and F43 (Exp67) found the **capture-per-k** of the escalation policy
**ANTI-contracts** — even under **unital** (depolarizing) noise (F43 H1 INVALIDATED: capk_high 0.6154 >
capk_noiseless 0.5431). Apparent contradiction with my theory.

**Hypothesis for the reconciliation:** these measure DIFFERENT layers. My ΔC is the raw **landscape
geometry** (fixed params, exact expectation). Ember's capk is the **post-COBYLA optimization OUTCOME**
under per-gate **local** depolarizing + 256 shots. Two confounds separate them:
(1) channel model — my exact law is for GLOBAL depolarizing; Ember uses PER-GATE LOCAL depolarizing,
    a different channel whose action on the cost gap is NOT a clean scalar (my C6142 caveat already
    flagged Thm 9.2 bounds trace distance but does not order the cost gap for a specific H under
    non-global noise);
(2) optimization dynamics — noise-assisted escape (F42 mechanism #2) can improve the realized optimum
    even while the landscape gap contracts.

Exp68 isolates layer (1) by measuring the **raw ΔC at fixed params** (no COBYLA, no shots) under both
channels, on the SAME EDGES_8 graph F43 used.

## Graph / circuit
EDGES_8 = ring+cross, 8 qubits, 12 edges (the F43 graph, defined locally — not importing Ember's
in-flight runner). Standard QAOA p=2. Exact statevector for pure; exact density-matrix (256×256) for
local depolarizing. Cost is diagonal → ⟨C⟩ = Σ_bs prob[bs]·cut(bs), exact (no sampling).

## Anchor / cold params
- `θ_anchor`: noiselessly COBYLA-optimized (exact expectation objective) → high ⟨C⟩.
- `θ_cold`: all-zeros → uniform |+⟩^n → ⟨C⟩ = meancut = |E|/2 = 6.0 (information-free baseline).
- Also report the (1−p) law on K=6 arbitrary random point-pairs to show the GLOBAL law is
  point-INDEPENDENT (holds for any two states), whereas LOCAL contraction may be point-dependent.

## Pre-registered predictions (committed BEFORE compute)
- **P1 (global depol exact law):** `ΔC_global(p) / ΔC_pure = (1−p)` to within 1e-9 for ALL p in
  {0.0,…,0.9} and for ALL point-pairs. conf 0.97. *(This is my derivation; a true-positive here
  verifies the math computationally, not by re-applying the formula — ⟨C⟩ is read from the numerically
  mixed probability vector.)*
- **P2 (local depol still CONTRACTS the landscape gap):** per-gate local depolarizing (p1 dose, p2=10·p1,
  matching F43's 1:10 ratio) gives ratio `R_local(dose) ∈ (0,1]`, **monotone non-increasing** in dose,
  and **NEVER > 1** (no landscape-level anti-contraction). conf 0.70. *(Unital noise → I/2ⁿ fixed point
  → contraction expected; but local-vs-global is exactly the untested nuance my C6142 caveat raised, so
  conf < P1.)*
- **P3 (the discriminator):** IF P1+P2 both hold (landscape gap always contracts under unital depol),
  THEN Ember's capk anti-contraction is NOT a landscape effect — it is **optimization-dynamics**
  (noise-assisted escape) and/or shot interaction. This kills the "noise anti-contracts the landscape"
  reading and confirms F42 mechanism #2. conf 0.65.
- **FALSIFIER:** if P2 fails (local depol R_local > 1 at some dose), then unital noise CAN anti-contract
  the raw landscape gap → my C6142 "contraction for unital noise" claim is too strong even at the
  landscape layer, and F43's anti-contraction has a landscape (not purely optimization) component.

## What this is NOT
Not a re-run of Exp67 (Ember owns the per-gate-depolarizing **capk dose-response** + COBYLA). Exp68
measures the raw fixed-param ΔC her experiments never isolate. No Ember files touched.
