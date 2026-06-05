# Exp38 Pre-Registration: X-Basis QAOA vs Standard QAOA Noise Wall Comparison
**Pre-registered**: 2026-06-05 (Whisper C3943) | FakeMarrakesh simulation
**ORQ**: #8 — Commutation-Aligned QAOA: Does X-basis formulation extend the depth ceiling?

## Scientific Motivation

Arc 3 established the **commutation-aligned compilation principle** (Exp 36, ibm_marrakesh):
- The cos²η overlap law governs noise vs measurement-basis angle (R²=0.971)
- Endpoint ordering: γ_X=0.0051 << γ_Z=0.0221 < γ_Y=0.0245
- X-basis measurement gives **4.3× noise immunity** vs Z-basis

Arc 2 established the **QAOA depth ceiling** (Exp 33/35):
- Noise wall at p≈16 (portfolio, ~1002 CZ gates)
- Standard QAOA: Cost Hamiltonian = ZZ, Mixer = Rx (X-basis rotation)
- Rx does NOT commute with dominant CZ Z-dephasing channel

**Key synthesis insight** (Whisper C3943): Standard QAOA mixer (Rx = exp(-iβ X)) does NOT commute 
with Z-dephasing. But an X-basis QAOA reformulation has:
- Cost: XX correlations (implemented as H·ZZ·H)
- Mixer: Rz rotations (exp(-iβ Z)) — PERFECTLY commutes with Z-dephasing
- Measurement: X-basis (H before readout)

The Rz mixer is 100% noise-immune to Z-dephasing by construction. Does this extend useful QAOA depth?

## Problem Setup

4-node MaxCut problem (unweighted, edges: (0,1), (0,2), (1,3), (2,3) — ring topology)
Maximum cut value = 4 (all edges cut, two-coloring: {0,3} vs {1,2})

### Standard QAOA (Z-basis)
- Initial state: |0000⟩
- Cost layers: exp(-iγ Zᵢ Zⱼ) for each edge (implemented via CX + Rz + CX)
- Mixer layers: exp(-iβ Xᵢ) = Rx(2β) on each qubit
- Measurement: Z-basis (computational)

### X-basis QAOA (commutation-aligned)
- Initial state: |++++⟩ (H⁴|0000⟩)
- Cost layers: exp(-iγ Xᵢ Xⱼ) for each edge (implemented via H + CX + Rz + CX + H)
- Mixer layers: exp(-iβ Zᵢ) = Rz(2β) on each qubit (COMMUTES with Z-dephasing)
- Measurement: X-basis (H before readout → equivalent to POVM {|+⟩, |−⟩})

## Pre-Registered Goals

### G1: Approximation ratio advantage at p=8
**Prediction**: X-basis QAOA approximation ratio (r_X) > Z-basis ratio (r_Z) at p=8
**Predicted magnitude**: r_X ≥ r_Z + 0.05
**Probability**: 0.60
**Rationale**: Rz mixer immunity + X-basis measurement should compound ~2 noise reductions.
At p=8 (~640 CZ gates), Z-basis is in the mid-range of its decline; X-basis should still be near peak.

### G2: Extended depth ceiling
**Prediction**: X-basis noise wall (entropy crossing 0.95× uniform) occurs at p_X > p_Z baseline (p≈16)
**Predicted p_X**: ≥ 20 (25%+ extension)
**Probability**: 0.55
**Rationale**: Rz mixer layers have zero Z-dephasing contribution → circuit decoherence per layer is
reduced → noise wall shifts to higher depth. The 4.3× immunity factor from Exp36 predicts ~4×
extension, but saturation effects reduce this (2-3× realistic estimate → p≈32-48).

### G3: Mixer-layer noise differential
**Prediction**: Noise contribution per p-layer is lower for X-basis vs Z-basis when measured at
the same CZ-gate count (normalizing away cost-layer overhead)
**Probability**: 0.70
**Rationale**: This is the most direct test of Rz commutativity. Rz gates add zero Z-dephasing
noise; Rx gates are maximally sensitive. Per-layer error budget should be measurably different.

### G4 (calibration check): Equal performance at p=0
**Prediction**: Both formulations converge to the same approximation ratio at p=0 (uniform dist)
**Probability**: 0.99
**Rationale**: At p=0, both are flat distributions. Any divergence indicates circuit construction bug.

## Circuit Depth Model

For 4-node ring graph with p layers:
- Standard QAOA: 4 edges × 2 CX gates × p layers + 4 Rx × p layers = 8p CX + 4p Rx
- X-basis QAOA: Same CX count in cost layers (8p CX), PLUS 8 H gates per cost layer (4×2),
  plus 4 Rz (mixer), plus 4H (initial), plus 4H (final readout)
- CZ equivalence: CX = CZ + H decomposition (1 CZ per CX)
- Total CZ at p=16: Standard = 128 CZ; X-basis = 128 CZ (cost) + near-zero (Rz)

Note: The X-basis QAOA does NOT reduce CZ count — both have same cost-layer CZ count.
The advantage is purely in MIXER layer noise: Rz has zero CZ gates AND commutes with Z-dephasing.

## Simulation Setup

Backend: FakeMarrakesh (hardware-realistic noise model, Heron-r2 topology)
Shots: 4096 per circuit
p range: 1, 2, 4, 8, 12, 16, 24, 32 (both formulations)
Optimization: COBYLA for beta/gamma parameters (10 restarts per p)
Metric: Approximation ratio r = C_achieved / C_max (C_max = 4 cuts for ring graph)

## Falsification Criterion

If G1 AND G2 both FAIL (r_X < r_Z at p=8 AND p_X ≤ p_Z), the commutation principle does NOT
extend to QAOA depth advantage and Arc 4 should pivot to a different question.

If G1 OR G2 PASS, the principle has partial application and further study is warranted.

## Connection to Finding 03 (Structural X-Basis Noise Immunity)

This experiment is the first direct test of whether Finding 03's structural noise immunity
translates to an ALGORITHMIC advantage. Arc 3 showed it at the circuit-characterization level
(passive measurement); Exp 38 tests it at the optimization-algorithm level (active QAOA).

If the principle holds, this would constitute:
- A new hardware-aware QAOA variant with provable noise advantage on NISQ hardware
- Direct financial application: deeper QAOA → better portfolio optimization approximation ratios
- A bridge from the commutation-aligned compilation principle (ORQ#7) to QAOA algorithm design (ORQ#8)

## Pre-registered by Whisper C3943
Date: 2026-06-05 | Quantum budget: 0 (FakeMarrakesh only at pre-registration)
Real hardware validation: Queued for when QPU quota frees (~June 10-15 est.)
