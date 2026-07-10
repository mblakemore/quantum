# Exp106 — Capacity Activation: information through two zero-capacity channels (PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4529 (2026-07-10) — Creator-directed (roadmap T1.1)
**Status**: FROZEN at the pre-submission commit. Creator directly authorized the spend; the
Exp105 sibling-review checklist was self-applied in lieu of a review window (see §Self-review),
and the sim tiers serve as the compensating controls. Siblings: object post-hoc and it grades
accordingly — the rule below cannot be changed after data.
**Theory**: Ebler, Salek, Chiribella, PRL 120, 120502 (2018). Prior art stated honestly:
photonic demonstrations exist (superposition-of-channels 2023, cyclic-orders 2025 arXiv:2510.07127).
Ours is the gate-model superconducting, pre-registered version on the certified Exp105 apparatus.

## Claim under test

A completely depolarizing qubit channel transmits zero information, and so does EVERY
causally-separable composition of two of them (fixed order A∘B or B∘A, classical mixtures,
dynamical order — all yield the fully depolarizing channel; the causal value of the
discriminator below is EXACTLY 0, no SDP needed). In the quantum switch with control |+⟩,
the input survives in the control–target correlation.

**Exact theory targets** (derived independently at C4529; noiseless sim reproduces all four):
P(control=+) = 5/8 input-independent; target|+ = (ρ+2𝟙)/5; target|− = (2𝟙−ρ)/3;
discriminator R(b) = ⟨Z_t|+⟩ − ⟨Z_t|−⟩ = ±8/15; symmetrized R̄ = (R(0)−R(1))/2 = 8/15 ≈ 0.5333;
I(B;C,T) = 0.0489 bits. **Signature**: the UNCONDITIONED target is exactly depolarized even in
the switch arm (D = 0) — the bit lives only in the correlation with the control.

## Design (frozen)

- **Channels**: full depolarizing = uniform Pauli mixture (Kraus σ_i/2). The switch of two
  mixed-unitary channels decomposes incoherently over Pauli labels, so the 16 (i,j)
  switch-of-Pauli circuits at equal shots, POOLED, are the exact channel twirl
  (deterministic weighting, Exp105 estimator logic).
- **Circuits**: Exp105 padded template (`exp106_capacity_activation.py::build_circuit`);
  every switch circuit = identical 4-CZ skeleton (controlled-𝟙 barrier-fenced CZ·CZ pads),
  locals-only differences (C4525 pair-independence requirement). Inputs |0⟩/|1⟩ (X-prep);
  control read in X (clbit 0), target in Z (clbit 1).
- **Arms**: 32 switch (16 pairs × 2 inputs × 1500 shots) + 32 null (same pairs/inputs,
  DEFINITE order A-then-B, control spectator) + 6 sentinels (F77 (X,X)/(X,Z) switch pairs,
  START/MID/END, 2000 shots) = 70 PUBs, 108k shots, ONE SamplerV2 job.
  Shuffle seed 4529; live re-audit aborts if the switch histogram drifts from {4:32}.
- **Backend**: ibm_marrakesh, calibration-gated pair (exp91 pick_pair).

## Sim gates (both PASSED pre-freeze, see results/exp106_feasibility.json)

Noiseless: R̄ = +0.5333 (=8/15), P(+) = 0.6250 both inputs, null D = 0, switch D = 0,
MI = 0.0488 bits — all four gates PASS (theory + implementation confirmed jointly).
FakeMarrakesh: R̄ = +0.510 ± 0.009, null D = 0.000 ± 0.005, MI = 0.0448 bits → preview WIN.

## Frozen grade rule

1. **Sentinel gate**: min replicate DISC ≥ +1.60, else NO-TEST.
2. **Null gate**: |D_null| + 5·SE < 0.05, else NO-TEST (depolarization integrity — if the
   definite-order arm carries input signal, the channel implementation is broken).
3. **WIN** iff R̄_switch − 5·SE_R > **0.10** (theory 0.533, sim-with-noise 0.510, causal
   value exactly 0; the 0.10 floor is ~11σ of expected SE and absorbs systematics).
4. **LOSS** iff R̄_switch + 5·SE_R < 0.10 with gates passing; else AMBIGUOUS.
5. Reported, ungraded consistency checks: P(+) ∈ 0.625 ± 0.05 both inputs; |D_switch| < 0.05
   (information-in-correlation-only signature); empirical MI vs 0.0489 bits.

## Self-review (Exp105 checklist applied to my own design)

- Skeleton uniformity: ✓ inherited padding; switch arm strictly {4:32} with live re-audit.
- Estimator validity: ✓ pooling = exact uniform twirl; incoherence across Pauli labels is the
  channel definition, not an approximation.
- Null observable: ✗→✓ CAUGHT PRE-FREEZE — the conditional discriminator R starves on the
  null arm (spectator control ⇒ almost no c=− samples; FakeMarrakesh SE 0.041). Null gate
  redefined on the UNCONDITIONED D (well-sampled; also the theory-correct null observable).
- Drift: ✓ shuffle seed 4529 + sentinel triplet gating on MIN.
- Bound applicability: ✓ causal value is exactly 0 by channel algebra (all orders of two
  fully-depolarizing channels are fully depolarizing); no measure-dependence this time.
- Device-characterized scope: ✓ same concession as Exp105, stated.

## Prediction (pred_c4529_001, conf 0.60 quantum cap)

Sentinel + null gates pass; R̄_switch ∈ [0.38, 0.55] → WIN; MI ∈ [0.02, 0.05] bits.
Risk named: target-qubit readout error dilutes R̄ multiplicatively (~1−2ε per readout);
FakeMarrakesh under-modeled readout on Exp103 (errs both directions).

## Cost

108k shots ≈ 25–45s of the ~100s remaining window. Creator authorized; standing refresh applies.
