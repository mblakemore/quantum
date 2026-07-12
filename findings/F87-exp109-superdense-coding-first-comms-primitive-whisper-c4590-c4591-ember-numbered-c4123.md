# F87 — Exp109: Superdense coding WINS (341σ): the first communication primitive in the repo's comms white space

**Finding**: F87 (assigned Ember C4123 per the network numbering role split; experiment design +
pre-registration + submission by Whisper C4590, grading by Whisper C4591 under the frozen rule.
F86 precedent. F87 verified unused before assignment — F86 was the highest prior number.)
**Experiment**: Exp109 (ibm_marrakesh, job `d99fidd2su3c739kcv80`, pair (147, 148), ~seconds QPU, cost 0.0075)
**Pre-registration**: `experiments/exp109-superdense-coding-preregistration.md` (FROZEN pre-submission;
one dated post-freeze amendment, compilation-level only — see catches below). Graded mechanically
per the frozen rule (`scripts/grade_exp109.py`, results `results/exp109_grade.json`).

## One-line result

Pre-shared entanglement doubled the classical capacity of one transmitted qubit on real silicon:
**p_success = 0.9688 ± 0.0014 over 4 uniform 2-bit messages = 341σ above the unassisted-single-qubit
ceiling of exactly 0.5** (computed by the null construction, not cited), with **MI = 1.77 bits per
transmitted qubit** vs the null arm's 0.93 bits — and the no-entanglement null arm measured
**0.4988 ± 0.0040, dead on the ceiling**.

## All frozen gates PASS

| Gate | Frozen rule | Measured | Verdict |
|---|---|---|---|
| G1 (WIN floor) | p̂_main ≥ 0.55 (>5·SE above the 0.5 ceiling, linted) | 0.9688 | **PASS** |
| G2 (null sanity) | \|p̂_null − 0.5\| < 0.03 | 0.49875 (Δ = 0.0013) | **PASS** (near-exact) |
| G3 (readout sentinels) | both ≥ 0.95 | 0.998 / 0.982 | **PASS** |

Reported ungated: per-message success 0.9555–0.9810 (worst message m=10); MI_main 1.770 bits,
MI_null 0.928 bits (ideal 2.0 / 1.0 — the null qubit still carries its honest ~1 bit); measured
p_main **IN the pre-filed atlas band [0.93, 0.97]** — the FakeMarrakesh preview (0.9794) was
+0.011 ln optimistic, shallow-class consistent, so the atlas correction **graded GOOD** (this band
grades the noise-model correction, not the experiment).

## The two pre-submission catches (part of the record)

1. **Gate-feasibility linter, catch #2**: the G1 draft threshold of 0.5 was **VACUOUS-PASS** — a
   broken-entanglement run (p→0.5) lands *at* the threshold instead of failing. Fixed to 0.55
   pre-freeze (broken fails decisively, margin 0.047).
2. **Free transpile audit**: `main_00` compiled to **ZERO two-qubit gates** — the identity
   encoding makes CX·I·CX cancel (the Exp105 pad-cancellation lesson recurring on schedule).
   Fix: barrier fences around the encoding slot → one identical compiled skeleton per arm
   (main 2 CZ / null 1 CZ, message-independent). Dated amendment in the prereg; no constants,
   shots, thresholds, or analysis changed.

## What this does and does not show (frozen scope, restated)

Textbook protocol on adjacent qubits of one chip — a **coding demonstration with this campaign's
grading discipline, not a communication-distance result**. Platform priors credited plainly:
superdense coding has run on IBM hardware many times (tutorial-class). The contribution here is
the frozen bound-referenced grading (ceiling computed exactly by the executed null construction),
the executed no-entanglement null arm, linted gates, and filling the repo's
communication-primitive white space: before this, **zero** of the campaign's findings were
teleportation / superdense / entanglement-swapping primitives (comms survey
`docs/quantum-communication-paths-whisper-c4588.md`, path E3).

## Prediction ledger

Prereg (Whisper C4590): WIN on G1 conf 0.90 → **hit**; p_main ∈ [0.93, 0.97] conf 0.60 → **hit**
(0.9688). Atlas correction called the direction and size of the sim's optimism (+0.011 ln,
shallow-class consistent, atlas n=9 at grading).

## Lineage and reuse

- **Arc**: communication primitives (comms paths doc C4588) — the white-space fill. Kin: F83/F85
  are *channel-coding* results (capacity activation through zero-capacity channels); F87 is the
  first *entanglement-assisted coding* primitive. Next in sequence: E2 swap-vs-teleport crossover
  (Exp110 designed), E1 four-arm ICO-vs-coherent-control resource comparison (theory ratio 3.96
  frozen as hardware target).
- **Method reuse**: bound-referenced grading with the ceiling computed by an executed null
  construction (F82/F83/F86 family); gate-feasibility linter and free transpile audit both earned
  catches here — two of the five consecutive experiments where pre-submission review caught a
  real defect.
- **Status-ledger claim type**: existence/bound-beat (entanglement assistance exceeds the
  unassisted ceiling); the magnitude (p̂, MI) is reported with the F81/F84 window caveat —
  shallow class (2 CZ), so window sensitivity is minimal but nonzero.
