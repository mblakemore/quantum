# Exp 33 — Hardware-Aware QAOA Depth Ceiling (PRE-REGISTRATION, Whisper C3739)

**ORQ #6** (README): *"Finding 05's 800–1000 CZ wall implies a hard ceiling on QAOA `p`.
Empirically map `p_max` for standard MaxCut. Pre-reg gate: identify the `p` value at which
output entropy crosses 0.95× uniform."*

**Registered BEFORE submission. Backend `ibm_marrakesh` (same device as Finding 05 → clean
wall comparison). One co-submitted job → single calibration snapshot.**

## Hypothesis

Finding 05 established a phase transition at ~800–1000 two-qubit gates on `ibm_marrakesh`: past
that depth, circuit output is statistically uniform (no usable signal). QAOA's cost layer costs
`2|E|` two-qubit gates per layer, so depth scales as `2|E|·p`. **Prediction:** QAOA output
entropy crosses 0.95× uniform at a `p` whose 2q-gate count falls in / near the 800–1000 CZ band.

## Design

- **Problem:** MaxCut on path graph **P6** (n=6, edges (0,1)…(4,5), |E|=5 → 10 two-qubit
  gates/layer). A path maps to a LINE on heavy-hex with zero routing overhead → transpiled 2q
  count is a clean `2|E|·p = 10p` (no SWAP confound; clean tie to the CZ wall).
- **Angles:** FIXED Trotterized-annealing schedule, total time `T=10.0`:
  `s_k=(k+0.5)/p`, `dt=T/p`, `γ_k=s_k·dt`, `β_k=(1−s_k)·dt`. No per-run optimization (removes the
  optimizer as a confound; fully reproducible).
- **Sweep:** `p ∈ {8, 16, 24, 32, 48, 64, 96}` → clean 2q `∈ {80,160,240,320,480,640,960}`,
  straddling the 800–1000 wall. (p<8 excluded: the anneal is too coarse there, leaving H_ideal
  high and muddying the 0.95×-uniform gate.)
- **Metric:** Shannon entropy of the measured output distribution `H = −Σ p_x log2 p_x`;
  `ratio(p) = H_hw(p)/n_qubits` (uniform = n = 6 bits). Also compute noiseless statevector
  `H_ideal(p)` so the **noise excess = H_hw − H_ideal** isolates decoherence from algorithm.
- 8192 shots/circuit, opt_level=1, seed_transpiler=42.

**Sim-preview validation (FakeMarrakesh, before submit):** H_ideal stays flat-low (ratio
0.32–0.49, top-2 optimal-cut mass 0.65–0.85) while H_hw rises monotonically 0.65→0.96; crossing
at p=96 (960 CZ) — consistent with the wall. Confirms the metric separates noise from algorithm.

## Pre-registered criteria (FIXED)

- **`p_max` := smallest swept `p` with `ratio_hw(p) ≥ 0.95`.**
- **G1 (CEILING EXISTS):** `p_max` found within the sweep OR top ratio (p=96) ≥ 0.90.
- **G2 (NOISE-DRIVEN):** at `p_max`, noise excess `H_hw − H_ideal ≥ 0.5` bit (crossing is
  decoherence, not the algorithm being intrinsically high-entropy).
- **G3 (WALL CONSISTENCY):** 2q-gate count at `p_max` ∈ [500, 1500] (consistent with Finding 05's
  ~800–1000 CZ wall, generous band for QAOA structural overhead).

### Interpretation
- **G1∧G2∧G3 PASS** → QAOA has an empirically-mapped hard depth ceiling co-located with the
  Finding 05 scrambling wall → the wall is an *algorithm-level* utility horizon, not just a
  diagnostic-circuit artifact.
- **G1∧G2 PASS, G3 FAIL (cz@p_max < 500)** → the QAOA ceiling is *tighter* than the raw scrambling
  wall — full-algorithm overhead (mixer RX + readout + the structured cost layers) decoheres
  faster than the bare CZ-counting circuits of Finding 05. Honest, publishable refinement.
- **G1 FAIL** → no ceiling within p≤96; extend the sweep to higher p in a follow-up job.

## Method note (do()/identification discipline)
The noise-excess gate (G2) is the same identification logic as Exp30's IDLE-arm control and the
Exp31 flatness-across-folds diagnostic: a metric must be tied to its generating mechanism before a
verdict is drawn. ratio≥0.95 alone could fire on an intrinsically high-entropy algorithm; G2 forces
the crossing to be *noise-attributable* before `p_max` is accepted. Prevents the C3733/C3737
overstatement pattern (acting on a signal whose cause wasn't verified).
