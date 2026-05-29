# Exp 31 — X-Basis Noise Immunity: Cross-Backend Replication (Whisper C3738)

**Open Research Question #1** (README "Open Research Questions"):
> *Does X-basis immunity generalize across the heavy-hex family? Replicate Finding 03 on
> `ibm_torino`, `ibm_kingston`, and any future Heron-r3 backend. If yes → upgrade from
> substrate-specific observation to architectural principle.*
> **Pre-reg gate: ≥2× X/Z fidelity ratio on at least one independent backend.**

## Motivation

Finding 03 (X-basis immunity) has **three independent confirmations — all on `ibm_marrakesh`**
(Bell C3650, GHZ-3 C3651, VQE-H₂ C3652). The mechanism is claimed to be architectural: the
native CZ gate on heavy-hex Heron is dominated by Z-dephasing, the Hadamard for ⟨XX⟩ readout
**commutes** with that channel (transparent), while the S† for ⟨YY⟩ readout rotates the latent
Z-phase noise **into** the measurement axis (noise injection).

If the mechanism is truly architectural (a property of the heavy-hex CZ channel, not of one
chip's idiosyncratic calibration), it must reproduce on an **independent** Heron device. The
campaign has never left `ibm_marrakesh`. `ibm_kingston` (separate Heron processor, READY,
queue 0 at submission) is the cleanest available independent backend.

## Design

A single Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2 (H on q0, CX q0→q1). Ideal expectation values:
- ⟨ZZ⟩ = +1, ⟨XX⟩ = +1, ⟨YY⟩ = −1  → all have ideal **magnitude 1**.

Basis-resolved ZNE: amplify gate noise by global folding (base · base⁻¹ · base …) at
λ ∈ {1, 3, 5}, then append the basis-rotation readout:
- ZZ: measure directly (computational basis).
- XX: H on both qubits before measure.
- YY: S† then H on both qubits before measure.

Error metric: `err_basis(λ) = 1 − |⟨BB⟩_measured|` (deviation of the magnitude from ideal 1).

3 bases × 3 λ = **9 circuits**, 4096 shots each. Transpile `optimization_level=0`,
`seed_transpiler=42` (opt=0 preserves the folds — the C3720 ZNE-collapse lesson). One
co-submitted job → single calibration snapshot (eliminates the ±7pp cross-day drift confound
that weakens the original three-different-days confirmations).

## Pre-Registered Criteria (FIXED before submission, Whisper C3738)

Let `eXX`, `eYY`, `eZZ` = mean error across λ for each basis. Let `γ_basis` = OLS slope of
`err_basis` vs λ (noise-amplification scaling).

- **T1 (X-IMMUNITY REPLICATES — headline):** `eZZ / eXX ≥ 2.0` AND `eXX < eZZ`.
  This is the README pre-reg gate (≥2× X/Z fidelity ratio on an independent backend).
- **T2 (Y-INJECTION REPLICATES):** `eYY > eXX` (the S†-injection signature: Y-basis worse
  than X-basis), with margin `eYY − eXX ≥ 0.02`.
- **T3 (SLOPE ORDERING):** `γ_ZZ > γ_XX` — under ZNE noise amplification the Z-basis error
  scales steeper than the (near-flat) X-basis error.

**Decision rule:**
- **T1 PASS** → Finding 03 upgrades from substrate-specific observation to **heavy-hex
  architectural principle** (≥2 independent Heron devices, mechanism survives chip change).
- **T1 FAIL (ratio < 2.0)** → X-basis immunity is **substrate/calibration-specific to
  marrakesh**, NOT architectural. Finding 03's "first-class compilation concern" framing
  would need to be downgraded to a marrakesh-specific observation. Either outcome is decisive.

**Honesty constraints:** single Bell circuit (Finding 03's strongest single confirmation was
also Bell, C3650 — direct comparability); single calibration snapshot; n=1 independent backend
(meets the README gate but kingston-only — a third device would further strengthen). ⟨YY⟩ S†
mechanism is the specific claim under T2; T1 (XX vs ZZ) is the core architectural test.
