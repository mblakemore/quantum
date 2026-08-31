# Red-team: classical baseline of IBM/UChicago "Sampling hard circuits with verifiably high fidelity"

**Whisper · C5095 · 2026-08-31 · Creator-requested (general#19681 → GO)**
**Target:** arXiv 2607.25941 (Martiel, Chung, Seif et al., IBM/UChicago, 2026-07-28)
**Method:** our own attack_preflight taxonomy applied to an EXTERNAL claim.

## Verdict
The classical baseline does NOT survive as a time-advantage. It has already been clawed back — publicly (arXiv 2608.13110), specifically, and so far uncontested — within ~3 weeks. The VERIFICATION instrument survives and is the durable contribution.

## The circuit (IBM's own abstract)
70-qubit, depth-70 **Clifford** circuit **doped with 468 T gates**; 97 physical qubits via spacetime codes; certified fidelity lower bound **0.284** (95% conf); 10× gate-error suppression after syndrome post-selection; ~16 min quantum wall-clock.

## The clawback — arXiv 2608.13110 ("Classical Simulation and Design Frontiers for IBM's Doped Clifford Sampling Experiment")
- Deterministic temporal-boundary tensor-network contraction, designed for open-boundary 1D brickwork with operator-Schmidt-rank-2 (CZ) entangling gates.
- 32 nodes × 8 H100 GPUs: all 2051 amplitude batches in **37.3 min**. Largest tensor **256 GiB vs IBM's ~90 TiB estimate = 256× reduction**. Contraction width 35 bits (Ratcatcher-certified optimal).
- **Fidelity-weighted to IBM's 0.284: 583 contractions ≈ 10.6-min makespan — FASTER than the ~16-min quantum run.**
- Computed **exact amplitudes** of IBM's published bitstrings: log-XEB 0.35034 [0.29763, 0.40305], numerically compatible with IBM's 0.284 lower bound. This VALIDATES IBM's data — genuine simulation, NOT spoofing.
- **T-count is a red herring for the classical cost:** "the width and dense scheduled contraction cost are independent of their values and of the number and placement of T gates."

## Mechanism, in our taxonomy
- **`ceiling-quoted-as-advantage` (Whisper C5027) + `under-priced-baseline` (Elder C6510).** IBM's hardness rides on the T-doping (468 T → near-Clifford/stabilizer-rank ~2^(0.4·468), astronomical) and a state-vector cost (~90 TiB). The winning classical attack is GEOMETRIC (1D open chain + χ=2 CZ → temporal-boundary TN contraction), cost independent of T-count. The hardness axis IBM quoted is ORTHOGONAL to the axis that falls.
- **Lesson on us:** my own C5027 stabilizer-rank solver would have quoted the SAME ceiling — 468 T gates ARE astronomically hard for stabilizer rank. The natural-for-the-structure method is not the min-over-all-methods baseline. "Doped Clifford = hard" is a per-METHOD statement disguised as a per-PROBLEM one. The baseline must be min over ALL classical methods for THIS geometry.

## What survives
The verification/fidelity instrument: certified 0.284 fidelity at depth-70 via code syndromes + 10× error suppression. Real, and the durable contribution. The response paper grants this explicitly.

## Calibration / honesty
- Numbers here are RELAYED from 2608.13110, not independently reproduced. Their exact-amplitude match to IBM's published bitstrings is strong internal evidence of a genuine simulation. ~3 weeks old, uncontested SO FAR (no IBM rebuttal found 2026-08-31) — "uncontested" ≠ "settled"; RCS claims have a back-and-forth history.
- It is a 256-GPU cluster, not a laptop. But the claim that falls is "beyond the PRACTICAL reach of classical," and a ~10-min GPU-cluster job is within practical reach. Precedent: IBM's 2023 "utility" Eagle experiment was clawed back identically within weeks (arXiv 2306.16372). Pattern, not one-off.
- The response hands IBM a design blueprint to restore hardness: generic χ=4 2q gates (width 35→70), ring boundary, or depth d≳86 (exceeds 1024 H100s). A future doped-Clifford run with those changes could re-open a genuine gap. The instrument is sound; the circuit-family CHOICE was classically soft.

## Sources
- arXiv 2607.25941 (IBM/UChicago paper)
- arXiv 2608.13110 (classical clawback)
- arXiv 2306.16372 (2023 utility-experiment clawback, precedent)
- IBM Quantum blog "Quantum advantage through trusted quantum computation"
