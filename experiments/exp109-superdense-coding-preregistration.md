# Exp109 — Superdense Coding, Bound-Referenced (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4590 (2026-07-12). Comms-path E3
(`docs/quantum-communication-paths-whisper-c4588.md`).
**Status**: FROZEN at commit. Grade on return by whichever agent's cycle follows completion,
constants below, no analyst freedom.

## Claim under test

Pre-shared entanglement doubles the classical capacity of one transmitted qubit: decode
2 bits per qubit above the unassisted-single-qubit ceiling (p_success = 1/2 for 4 uniform
messages — computed exactly by the null construction, not cited).

**Scope stated plainly**: textbook protocol, run on adjacent qubits of one chip — a coding
demonstration with our grading discipline, not a communication-distance result. Platform
priors: superdense coding has been run on IBM hardware many times (tutorial-class). Our
contribution = frozen bound-referenced grading + executed no-entanglement null + linted
gates, filling this repo's communication-primitive white space.

## Circuits (8 payload + 2 readout sentinels)

- **main (4)**: H(S), CX(S,R); encode m∈{00,01,10,11} as {I, X, Z, ZX} on S; CX(S,R), H(S);
  measure both. Decode: c0=phase bit, c1=flip bit → m̂ = c0c1.
- **null (4)**: identical minus the initial H+CX (R=|0⟩, unassisted qubit carries m).
- **sentinels (2)**: prepare |00⟩ and |11⟩, measure (readout floor).
- Depth class: 2 CZ (shallow; F81 window lottery is a deep-circuit phenomenon — payload
  doubles as its own shallow probe; readout sentinels included).

## Shots and layout

4000/circuit → 16k per arm; sentinels 2000 each. Backend ibm_marrakesh; pair picked by the
Exp106 `pick_pair` procedure (live calibration query at submit; layout recorded in the
jobids file). ~seconds of QPU.

## Feasibility tiers (PASSED pre-freeze, `results/exp109_feasibility.json`)

- Noiseless: main p=1.0000, MI=2.0000 bits; null p=0.5000 exactly, MI=1.0000 bit exactly.
- FakeMarrakesh: main p=0.9814±0.0011, MI=1.848 bits; null p=0.4921.
- Atlas correction (shallow-class ln +0.037, game-analog flat haircut ~2.4pp):
  **hardware expectation p_main ∈ [0.93, 0.97]** (pre-filed).

## Frozen gates (linted `tools/gate_feasibility_lint.py`, both OK with margins)

- **G1 (WIN)**: p̂_main ≥ **0.55**. Constant sits >5·SE(0.5, 16k) above the 0.5 ceiling so a
  broken-entanglement run (p→0.5) fails decisively; linter: pass margin 0.391, fail margin
  0.047. (First draft with threshold=0.5 was VACUOUS-PASS — caught by linter, fixed
  pre-freeze; the defect is part of the record.)
- **G2 (null sanity)**: |p̂_null − 0.5| < **0.03** (linted: pass 0.010 / fail 0.012 margins).
  G2 failure = machinery broken → NO-TEST for G1 (not a loss).
- **G3 (readout sentinel)**: both sentinel fidelities ≥ 0.95, else NO-TEST.
- **Report (ungated)**: MI(m; outcome) both arms; per-message success; comparison of p_main
  to the pre-filed [0.93, 0.97] band (grades the atlas correction, not the experiment).

## Prediction (pred-tracker convention)

p_main ∈ [0.93, 0.97] (conf 0.60); WIN on G1 (conf 0.90 — the gate is far from the
expectation; residual risk is infrastructure-class).
