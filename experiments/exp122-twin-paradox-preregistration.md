# Exp122 — THE PROPER-TIME INTERFEROMETER: PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4650. Creator authorized freeze+fly this cycle
(design+sim C4649). Design: `exp122-twin-paradox-design.md`. Sim:
`exp122_twin_paradox_sim.py` → `results/exp122_feasibility.json`.

## Claim under test (model-free headline; the law is a reported subclaim)

An EXCITED clock routed through two physical lanes in path-superposition loses
interference visibility **because its aging marks the path** — while an identical
interferometer with an UNEXCITED clock (the vacuum twin, same gates, same delays,
same dephasing) does not lose it the same way. Headline = the twin separation, not
the law: the sim tier showed the √(p₀p₁) law under-predicts decay ~30% even on the
noise model (extra which-path channels, mechanisms pre-named) — so law-match is
explicitly NOT a gate (C4596 null-first applied at design; gating it would
manufacture a false loss, the F93-class trap).

## Frozen apparatus (builders byte-identical: `exp122_twin_paradox_sim.py`)

- Qubits [C,K,L]: C = path, K = home lane / clock slot, L = travel lane.
  |+⟩_C; clock = X on K (excited arm) or nothing (vacuum arm); CSWAP(C;K,L);
  delay Δt on K and L; CSWAP back; C read in X. K,L read in Z (diagnostics).
- **Site rule (frozen)**: hub h with the two lowest-error edges among its
  neighbors (dead-qubit guard); layout C=h, K=better-edge neighbor, L=other;
  deterministic tiebreaks (readout, index).
- **Ladder rule (frozen)**: Δt ∈ {0, 0.15, 0.3, 0.6, 1.2}·T̄ rounded to µs, where
  T̄ = harmonic mean of the two lanes' SUBMIT-TIME published T1s. Placement by
  published values, GRADING by in-job calibration (the F95 published-T1-bias
  lesson, frozen as practice).
- **Arms**: excited×5 + vacuum×5 at 20k shots + in-job T1 calib (2 lanes ×
  {0, 0.3, 0.6, 1.2}·T̄) at 10k = **18 pubs, 280k shots, one job, ibm_marrakesh**.
  Transpile seed 4650, opt 1, scheduling asap, shuffle seed 4650.
- **Audit**: interferometer pubs share one 2q count, all 2q inside the site;
  calib pubs 0 two-qubit gates.

## Frozen statistics and gates

V = ⟨X_C⟩ per arm/ladder-point (binomial SE). dt\* = ladder point 3 (0.3·T̄).

- **G0 (NO-TEST guard)**: V_exc(0) > 0.7 AND V_vac(0) > 0.7 (interferometer alive
  through both CSWAPs; fake 0.89/0.91).
- **W_AGE (HEADLINE, model-free)**: V_vac(dt\*) − V_exc(dt\*) > 5·σ_diff →
  **AGING MARKS THE PATH** (fake preview at 0.3T̄-class point: 0.128 gap ≈ 13σ).
- **W_AGE_LADDER (support)**: same separation at 5σ for ladder point 4 (0.6·T̄)
  as well (fake ≈ 9σ) — the separation is a curve, not a point fluke.
- **Subclaims (REPORTED, not gated)**: ln-R slope (R = V_exc/V_vac) vs
  −(Γ_K+Γ_L)/2 from in-job calib T1s — residual quoted; excess-decay ratio
  (measured/predicted slope) with pre-named mechanism candidates (clock dephasing
  in transit between lanes; CSWAP infidelity records). Fake preview of the excess:
  ~1.3×. Per-branch clock survivals from K/L diagnostics.

## Predictions (registered at freeze)

- **P1** W_AGE: **0.85**. **P2** W_AGE_LADDER: **0.80**. **P3** NO-TEST (G0): **0.07**
  (2 CSWAPs ≈ 16 2q gates; fake alive at 0.89).

## Honest scope (pre-stated)

Information-theoretic twin paradox: "aging" = T1 decay in the lab frame; the
which-path record is emission location. Not gravitational time dilation, and not
claimed as such. One backend/window.

Lint: `experiments/exp122_gate_lint_spec.json` → `results/exp122_gate_lint.txt`.
Grader `scripts/grade_exp122.py` FROZEN with this prereg.
