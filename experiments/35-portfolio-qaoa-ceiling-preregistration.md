# Exp 35 — Portfolio-QAOA Depth Ceiling: CZ-count-governed vs p-governed wall (PRE-REGISTRATION, Whisper C3747)

**ORQ #6 leftover** (README): *"Empirically map p_max for ... portfolio-optimization benchmarks."*

**Registered BEFORE hardware submission. Backend `ibm_marrakesh` (same device as Exp33 + Finding 05).
One co-submitted job → single calibration snapshot.**

## The question this settles (not just "another benchmark")

Finding 05 claims the QAOA utility wall is governed by **total two-qubit-gate count** (~800–1000),
an information-theoretic/scrambling horizon — *not* by the algorithm's nominal depth `p`. Exp33
(RESOLVED) mapped MaxCut on a **sparse** path P6 (|E|=5, 10 CZ/layer) → wall at **p_max=96 = 960
transpiled CZ**. But for a path graph (transpiled CZ) ∝ (nominal p) with a fixed constant and **zero
SWAP overhead**, so Exp33 alone *cannot separate*:

- **H_A (CZ-count-governed):** the wall is at ~800–1000 *transpiled CZ* regardless of problem.
- **H_B (p-governed / structure):** the wall is at ~p=96 layers regardless of CZ/layer.

**Portfolio optimization breaks the proportionality.** The Markowitz QUBO is **fully connected**
(all-pairs covariance ZZ + budget-penalty cross terms), |E| = N(N−1)/2. For N=6: 15 edges =
30 nominal CZ/layer + SWAP overhead on degree-3 heavy-hex. So per layer it spends 3–6× the CZ of the
path graph → the two hypotheses make **distinct predictions on nominal p** (H_A: low p_wall; H_B: p≈96).

## Design (parity-controlled with Exp33 — ONE varied variable = problem density)

- Backend `ibm_marrakesh`, opt_level=1, seed_transpiler=42, 8192 shots — **identical to Exp33**.
- **Same** fixed Trotterized-annealing schedule (T=10): `γ_k=s_k·dt, β_k=(1−s_k)·dt, s_k=(k+0.5)/p,
  dt=T/p`. No per-run optimization (removes optimizer confound).
- **Deliberately NO calibration-gated `initial_layout`** (the Exp34 `do(layout)` gate): adding it
  would change a *second* variable vs Exp33 and confound the density comparison. The entropy/noise-
  excess metric measures *global* decoherence-to-uniform, robust to a few weak qubits → parity is the
  correct control. (Documented trade-off; a calibration-gated replicate is a clean follow-up.)
- **Problem:** N=6 assets, select K=3, Markowitz QUBO `min q·xᵀΣx − μᵀx + λ·(Σx − K)²`, **hardcoded
  reproducible instance** (no RNG). Strong budget penalty (λ=2) makes the K=3 subspace dominate.
  QUBO→Ising: `h_i = −Q_ii/2 − ¼Σ_{j≠i}Q_ij, J_ij = Q_ij/4`. Cost layer = RZ(2γh_i) per qubit +
  CX·RZ(2γJ_ij)·CX per all-pairs edge; mixer RX(2β).
- **Sweep:** `p ∈ {4,8,12,16,24,32,48}` (denser → wall expected at far lower nominal p than 96).

## Metric choice (revised in sim-preview, BEFORE submission)

Exp33 used `ratio = H_hw/N` vs a 0.95×-uniform gate because the sparse path's noiseless output
`H_ideal` stayed **flat-low** across the whole sweep (structured reference). For the **dense**
portfolio that fails: the fixed annealing-ramp needs many layers to concentrate, so `H_ideal` is
near-uniform at small p (sim: ratio 0.99 @ p=4) and only drops at p≥16. A ratio gate is therefore
**contaminated at low p** — it would fire on an *unconverged anneal*, not on noise (sim-confirmed). The
correct, **noise-attributable-by-construction** metric is the **noise excess**
`noise_excess(p) = H_hw(p) − H_ideal(p)`: it subtracts the algorithm's own spread, isolating hardware
decoherence at every p. (Sim-preview, FakeMarrakesh: excess flat-low 0.0→0.58 bit through p=12=750 CZ,
then **jumps to 3.29 bit at p=16 = 1002 transpiled CZ** — a clean gap straddling the threshold.)

## Pre-registered criteria (FIXED, noise-excess basis)

- **`noise_wall_p` := smallest swept p with `noise_excess ≥ 1.0 bit`.** (Threshold 1.0 chosen pre-submit
  to sit cleanly **above** the ~0.5-bit unconverged-anneal floor and **below** the ≥3-bit decohered regime.)
- **`cz_at_wall` := transpiled 2q-gate count at `noise_wall_p`.**
- **G1 (NOISE WALL EXISTS):** `noise_wall_p` found within the sweep.
- **G2 (STRUCTURED REFERENCE):** `H_ideal/N ≤ 0.6` at the wall — the noiseless output is genuinely
  structured there, so the excess reflects noise destroying *real* structure (not both near-uniform).
- **G3 (CZ CO-LOCATION = discriminator):** `cz_at_wall ∈ [500, 1500]` (Finding 05's ~800–1000 band,
  generous for QAOA structural overhead).
- **G4 (DENSITY EFFECT / CZ-NOT-p):** `noise_wall_p < 96` (= Exp33 p_max) **and** `cz_at_wall ∈ [500,1500]`
  — the wall arrives at far **fewer layers** but the **same CZ count**.

### Interpretation
- **G1∧G2∧G3∧G4 PASS → H_A CONFIRMED:** the QAOA wall is governed by **total transpiled CZ count**,
  ~invariant across density (sparse 960 CZ @ p=96 vs dense ~1000 CZ @ p≈16). An information-theoretic
  horizon, not nominal depth. Planning constant: `p_max ≈ 1000 / (transpiled-CZ-per-layer)`. For dense
  problems → a hard **low-p** ceiling, directly actionable for portfolio-QAOA on NISQ hardware.
- **G3 FAIL, cz_at_wall ≫ 1500 → H_B:** wall tracks nominal depth/structure, not raw CZ count;
  Finding 05's CZ-count framing is not the right invariant for dense problems. Honest, publishable.
- **G3 FAIL, cz_at_wall < 500:** portfolio ceiling **tighter** than the bare CZ wall (all-to-all + SWAP
  decoheres faster than counted) — a density-driven refinement of Finding 05.
- **G1 FAIL:** no noise wall within p≤48; extend the sweep.

**Secondary read (anneal-convergence vs wall collision):** `p_converge` := first p with `H_ideal/N ≤ 0.5`.
If the transpiled CZ at `p_converge` is itself ~800–1000, the dense anneal only concentrates *at* the
wall → **no usable depth window** (a strong, honest negative result). Sim-preview: `p_converge = 16 =
noise_wall_p` → predicted no-usable-window; the real-hardware test is whether the device holds structure
slightly longer than FakeMarrakesh's noise model and cracks the window open.

## Method note (do()/identification discipline)
The noise-excess basis is the same identification logic as Exp30's IDLE-arm, Exp31's flatness-across-folds,
Exp33's G2, and Exp34's calibration gate: a metric must be tied to its generating mechanism before a
verdict. `ratio≥0.95` alone fires on an intrinsically/uncovergedly high-entropy algorithm; subtracting
`H_ideal` forces the crossing to be noise-attributable. Prevents the C3733/C3737 overstatement pattern.

**Sim-preview (FakeMarrakesh, before submit):** QUBO ground state `x*=[1,0,0,1,1,0]` (sum=3=K ✓);
all four gates PASS in the noise model (`noise_wall_p=16, cz@wall=1002, excess=3.29, ideal_ratio=0.38`).
Real-hardware run is the actual test — the noise model is not the device.
