# Exp112 — Bell Violation Through Entanglement-Swapping Stations (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4598. Comms-path E4 — the arc closer.
**Status**: FROZEN at commit. Grade on return, constants below, no analyst freedom.

## Question

Does a CHSH violation survive distribution through k entanglement-swapping stations
(k ∈ {0,1,2}) on-chip — the repeater primitive — and what does the correction strategy cost?
Two arms carry the arc's own lesson (F90: feedforward works but costs ~5–6× per hop):

- **frame**: stations Bell-measure with NO feedforward; CHSH graded branch-resolved with
  per-branch sign patterns **frozen from the noiseless tier** (reference-relative to Φ+;
  the validator caught the raw-sign double-count — fix in the sim file, part of the record).
- **active**: stations correct via if_test X/Z (Exp110-validated machinery); pooled CHSH.

## Circuits and budget

Per (arm, k, setting): settings a∈{0,π/2}, b∈{π/4,−π/4} (Ry before Z-measure);
S = E(a,b)+E(a,b′)+E(a′,b)−E(a′,b′). k=0 shared between arms. 20 payload circuits × 3000
shots + 4 readout sentinels × 2000 = 68k shots. Chain: best 6-qubit path by (CZ+readout)
cost at submit (Exp110 finder, CHAIN_LEN=6). Apparatus frozen: opt_level=1,
seed_transpiler=4598, initial_layout=chain.

## Frozen estimators

Per-setting correlations E from the 2-bit chsh register (parity); frame arm: per-branch E,
combined per frozen sign matrix (`results/exp112_feasibility.json` signs_frozen), pooled by
branch weight. SE: binomial propagation, SE(S) = 2·√(Σ per-setting (1−E²)/n).

## Frozen gates

- **G1 (readout sentinels)**: all four ≥ 0.95, else NO-TEST.
- **G2 (apparatus anchor)**: k=0 S − 5·SE > 2.0, else NO-TEST (the F01 anchor re-run in this
  window; decohered apparatus lands ≈1.4, decisive fail; preview 2.71, SE ≈ 0.026).
- **WIN(k, arm)** for k ∈ {1,2} × {frame, active}: S − 5·SE > **2.0** — Bell violation
  certified through k stations under that correction strategy. Four independent grades.
- **LOSS(k, arm)**: S + 5·SE < 2.0 with G1/G2 passing. Else AMBIGUOUS per cell.

## Pre-filed expectations

FakeMarrakesh previews (no feedforward noise modeled — stated): frame {2.713, 2.617, 2.562},
active {2.713, 2.689, 2.569}. Atlas mid-class correction (+0.10 ln) → hardware S(k=2)
expectation ≈ **2.3 ± 0.1** — violations should survive with margin.
**Predictions (pred-tracker convention)**: all four WIN cells pass, conf 0.75;
active(k) < frame(k) on hardware for k ≥ 1 (the feedforward cost, invisible to the model —
F90 pattern), conf 0.65; S(k) monotone decreasing in k both arms, conf 0.80.

## What closes the arc

With Exp112 graded, every path from the C4588 communication review is executed or parked
with its gap named: E1 (F89), E3 (F87), fridge (F86/F88), E2 (F90), E4 (this), E5 (parked,
entropy-accumulation gap named). The comms white space of C4588 §1 is filled.
