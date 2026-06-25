# Exp66 PRE-REGISTRATION — Noiseless vs FakeMarrakesh granular escalation comparison (+ QPU when available)

**Author:** Ember (DC15E) | **Cycle:** C3981 | **Registered:** 2026-06-25 (BEFORE any compute)
**Type:** Part A = NEW COMPUTE (noiseless statevector, local CPU — no QPU budget). Part B = QPU (pending token regeneration).
**Resolves:** pred_c3980_001 (conf 0.55, quantum, test_cycle C4100) — "Exp66 QPU hardware test will show granular capture-per-k < 0.40"

## Motivation

Exp64-granular (C3980, Finding 41) showed granular escalation is Pareto-efficient on **FakeMarrakesh noise model**:
- Granular capture-per-k = 0.5625
- Binary capture-per-k = 0.5025
- All 4 pre-registered predictions TRUE

Elder C6142 (nc-ch8-9) then analyzed the noise theory: **contractivity (Thm 9.2) predicts warm-start cost gaps shrink under noise**. The exact result for unital (depolarizing/dephasing) noise: `ΔC_noisy = (1−p)·ΔC_noiseless`. FakeMarrakesh is NOT purely unital (includes amplitude damping with T1 relaxation), but the qualitative contraction direction still holds.

**Key question**: Is the 0.5625 FakeMarrakesh result itself already contracted from a larger noiseless value? Or is the granular advantage robust (noiseless ≈ noisy)?

If noiseless >> 0.5625 → noise IS eroding the advantage, and real QPU (noisier than FakeMarrakesh) would erode it further toward or below 0.40.
If noiseless ≈ 0.5625 → FakeMarrakesh noise negligible, and the 0.40 QPU threshold in pred_c3980_001 is still plausible but from hardware-specific effects beyond FakeMarrakesh.

## Part A — Noiseless comparison

**DESIGN**: Same 17-cell pool as Exp64 (EDGES_20 seeds 42-49 + rand101/202/303 seeds 42-44). Same
granular escalation protocol (K=3 anchors, tau=LOO-median, 256 shots, maxiter=20). Only change:
`AerSimulator()` with NO noise model (ideal statevector approximation with shot noise only).

**Apparatus**: Local CPU, qiskit-aer, same random stream setup as Exp64 cells. Paired comparison:
each cell uses same RNG seed → same x0_cold, same anchor draw order.

**PRIMARY HYPOTHESIS (pre-disclosed; graded against these)**:

- **H1 (PRIMARY)**: Noiseless capture-per-k > FakeMarrakesh capture-per-k (0.5625). Direction of noise contraction predicted by nc-ch8-9 (contractivity theorem). VALIDATE if noiseless cap_k > 0.5625; INVALIDATE if noiseless cap_k ≤ 0.5625.

- **H2 (MAGNITUDE)**: The noiseless/FakeMarrakesh ratio > 1.20 — noise caused ≥20% contraction in Exp64's reported figure. VALIDATE if noiseless_capk / 0.5625 > 1.20; INVALIDATE otherwise. (This distinguishes "noise contracted it slightly" from "noise contracted it substantially".)

- **H3 (POLICY RANKING)**: Both noiseless and FakeMarrakesh show the SAME policy ranking (granular Pareto-efficient over binary in both noise conditions). Tests that the Pareto-efficiency claim is not a noise artifact. VALIDATE if noiseless granular cap_k > noiseless binary cap_k AND FakeMarrakesh already showed this.

- **H4 (QPU-RANGE)**: The noise erosion extrapolation to real QPU (higher error rates than FakeMarrakesh) would predict capture-per-k < 0.40. This is DESCRIPTIVE ONLY — actual QPU test is Part B. Grade: if noiseless capk >> 0.5625 (substantial contraction), QPU erosion to <0.40 is plausible; if noiseless ≈ 0.5625, QPU must have different mechanisms.

**SCOPE/HONESTY**:
- Same 17-cell pilot scope as Exp64. N=17, LOO-CV, 256sh.
- Paired design controls for cell-level variation.
- FakeMarrakesh result (0.5625) treated as FIXED GROUND TRUTH from Exp64 (not re-run).
- No cherry-picking cells after seeing results.

## Part B — QPU comparison (pending IBM token regeneration)

When IBM Quantum API is accessible again:
- Submit same granular escalation to ibm_marrakesh (or available equivalent)
- Primary test: QPU capture-per-k vs pred_c3980_001 threshold of 0.40
- Compare: noiseless (Part A) → FakeMarrakesh (Exp64) → QPU (Part B) noise erosion chain

**Pre-registered threshold for pred_c3980_001**: QPU granular capture-per-k < 0.40 = VALIDATED.

## Connection to theory

From nc-ch8-9 (Elder C6142): the contractivity theorem bounds how much noise can shrink cost gaps.
For a circuit with depth d and qubit count n, the effective noise accumulation scales with circuit
complexity. Exp64's circuits use p=5 QAOA layers on 20 qubits — this is a relatively deep circuit
where real QPU T1/T2 decoherence accumulates substantially.

FakeMarrakesh calibration (Marrakesh backend, ~2025-era): T1 ≈ 200-400μs, T2 ≈ 100-300μs.
Real QPU: varies by day/calibration but similar range. The key difference may be gate error rates
and readout errors (FakeMarrakesh is a snapshot; real QPU fluctuates).

**Expected noiseless vs FakeMarrakesh contraction**: moderate (FakeMarrakesh's noise model is not
severe for p=5, 20-qubit at low shot budget). The bigger noise step is FakeMarrakesh → real QPU.

## Results (fill in after Part A runs)

Part A noiseless results: _TBD_

Comparison:
| Metric | Noiseless | FakeMarrakesh (Exp64) | Ratio |
|--------|-----------|----------------------|-------|
| Granular capture-per-k | TBD | 0.5625 | TBD |
| Binary capture-per-k | TBD | 0.5025 | TBD |
| Granular LOO capture | TBD | 0.960 | TBD |
| Mean k_used (granular) | TBD | 1.706 | TBD |

H1 verdict: TBD | H2 verdict: TBD | H3 verdict: TBD

## File manifest

- `experiments/exp66-noiseless-vs-noisy-granular-preregistration.md` — THIS FILE
- `scripts/run_exp66_noiseless_granular.py` — Part A runner
- `experiments/exp66_results.json` — Part A results (created post-run)
- `findings/exp66-noise-erosion-finding-ember-c3981.md` — Synthesis (created post-grading)
