# Exp122 — The Proper-Time Interferometer / Quantum Twin Paradox (DESIGN)

**Author**: Whisper (DC15W), C4649. Horizons-2 Q4, Creator-directed (freeze+fly
authorized for the following cycle). Sim: `exp122_twin_paradox_sim.py` →
`results/exp122_feasibility.json`.

## The question

In relativity, elapsed time depends on the path; a clock in path-superposition
interferes only while the paths' *ages* stay indistinguishable (Zych-Brukner). The
information-theoretic core on our hardware: the honest clock we already own is
**T1 decay** (the delay-ladder instrument, F88/F94/F95). A path qubit C routes an
EXCITED clock through two physical lanes via CSWAP; during a shared delay the clock
ages in a different lane per branch; **spontaneous emission into that lane's bath is
the which-path age record**. The second CSWAP undoes everything unitary — only
irreversible bath leakage marks the path.

## The law (derived in-code, C4558 — not recalled)

Direct Kraus/density-matrix computation with physical-bath record matching
(`exact_V`): **V(Δt) = √(p₀ p₁)**, p_i = exp(−Δt/T1_lane_i); vacuum twin
(clock |0⟩): V = 1 identically. Only the no-emission amplitudes interfere. Verified
numerically to 1e-12 across asymmetric parameter sets, including the subtle
swap-back bookkeeping (the first draft derivation was WRONG and fixed by careful
position-basis accounting — recorded here as method provenance).

## Sim tier findings (both load-bearing for the freeze)

1. **Feasible**: fake models delay relaxation (lane survivals 0.57/0.70 at 100µs);
   full curves at budget: excited visibility 0.89→0.08 across {0..200µs}, vacuum
   0.91→0.18. The aging-vs-vacuum separation at 50µs: 0.27 vs 0.40 ≈ **13σ**.
2. **Excess decay caught at design time (C4596 null-first applied)**: the ratio
   R = V_exc/V_vac decays ~30% FASTER than √(p₀p₁) even on the fake — extra
   which-path channels exist beyond the amplitude-damping model (candidates:
   clock dephasing in transit between lanes, CSWAP infidelity records). Therefore
   the LAW-MATCH is NOT gate-able; it freezes as a REPORTED subclaim with residuals
   quoted, and the headline is the model-free existence claim below.

## Frozen-freeze plan (next cycle)

- **Arms**: excited × 5-point delay ladder + vacuum × same ladder (the twin control)
  + in-job T1 calibration (2 lanes × 4 delays). ~16 pubs, ~280k shots.
- **Ladder rule (frozen)**: {0, 0.15, 0.3, 0.6, 1.2}·T̄ from submit-time published
  T1s (T̄ = harmonic mean of the two lanes); grading uses IN-JOB calib T1s (the F95
  published-T1-bias lesson: place with published, grade with measured).
- **Site rule (frozen)**: hub C with two lowest-error edges; K = better edge, L =
  other (C touches both in the CSWAP decomposition).
- **Gates**: G0 interferometer-alive guard (V(0) > 0.7 both arms; fake 0.89/0.91);
  **W_AGE headline (model-free)**: V_vac(dt\*) − V_exc(dt\*) > 5σ_diff at the frozen
  mid-ladder point — *the aging clock marks the path; the vacuum twin does not*.
  Law subclaim REPORTED: measured ln-R slope vs −(Γ₀+Γ₁)/2 from in-job calib,
  residual quoted, excess-decay mechanisms pre-named.
- Honest scope pre-stated: an information-theoretic analogue (aging = T1 decay in
  the lab frame), not gravitational time dilation; the which-path record is
  emission location, not metric proper time.
