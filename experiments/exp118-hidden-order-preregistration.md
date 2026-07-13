# Exp118 — Hidden-Order Diagnostics: PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4634. Frozen on a FRESH cycle per the no-tired-freeze rule
(deferred from C4629 exactly for this). Design doc: `exp118-hidden-order-diagnostics-design.md`
(C4624). Sim/feasibility tier: `exp118_hidden_order_sim.py` → `results/exp118_feasibility.json`
(C4624). Roadmap T2.5 — the last unexecuted roadmap gem; horizons P5.

**Creator directive this cycle**: "freeze and fly Exp118 hidden-order diagnostics."

## Question

When the transpiler schedules two CZ gates "simultaneously" on nearby pairs, does the
hardware execute them order-symmetrically, or is there a hidden effective ordering?
Crosstalk framed as a causal-structure question — the switch arc's apparatus inverted.

## Frozen apparatus

- Probe: 5 qubits `[pairA(0,1), spectator(2), pairB(3,4)]`, all |+⟩ prep, k=**8** amplified
  CZ layers with barrier fences, X-basis read on all 5 (`exp118_hidden_order_sim.py::probe`,
  byte-identical builder used for flight).
- Arms per site: `seqAB` ([A][B]×k), `seqBA` ([B][A]×k), `par` ([A∥B]×k).
- **Budget**: 2 sites × 3 arms × **6000 shots** = 36,000 shots, 6 pubs, one job,
  `ibm_marrakesh`. Pub order shuffled, seed 4634. Transpile: optimization_level=1,
  seed 4634, initial_layout = site layout.
- **Transpile audit (go/no-go)**: every pub has exactly 2k=16 two-qubit gates, all native
  CZ, all on the two intended physical edges. Any FAIL → no submission.

## Frozen site-selection rules (live coupling map at submit; zero discretion)

Implemented in `scripts/run_exp118_submit.py::select_sites`; deterministic given the
calibration snapshot:

- **Hotspot**: disjoint edges A,B plus spectator s ∉ A∪B adjacent to ≥1 qubit of EACH
  edge; minimize err(A)+err(B); tiebreak spectator readout error, then lexicographic.
- **Control**: disjoint edges A,B with graph distance ≥ 3 hops; spectator = lowest-readout
  neighbor of A (∉ A∪B, not adjacent to B); minimize err(A)+err(B); tiebreak lexicographic.
- Dead-qubit guard: any edge/qubit with missing or ≥0.5 error excluded.

## Frozen statistics and classification

TVDs on the joint 5-qubit distributions; bootstrap SEs (B=200, seed 4634).
D_order = TVD(seqAB, seqBA); D_A = TVD(par, seqAB); D_B = TVD(par, seqBA);
D_mix = TVD(par, ½seqAB+½seqBA).

**FLOOR = 0.0223** — sim tier same-distribution TVD at budget: FakeMarrakesh D_order
0.0062 + 5×SE 0.0032 (`results/exp118_feasibility.json`). Frozen now; not tunable at grade.

Per site (grader `scripts/grade_exp118.py`, frozen with this prereg):

1. **EXISTS** iff D_order − 5·SE > FLOOR; else **ORDER-SYMMETRIC**.
2. If EXISTS, classify `par`: **GENUINELY-CONCURRENT** if min ref distance − 5·SE > FLOOR
   (par unlike all of seqAB/seqBA/mix); else nearest reference **SECRETLY-A-FIRST /
   SECRETLY-B-FIRST / MIXTURE-LIKE** if both distance gaps clear 5·SE of the gap;
   else **UNRESOLVED-NEAREST**.
3. **Experiment gate**: control must read ORDER-SYMMETRIC. Control EXISTS → **NO-TEST**
   (apparatus artifact — e.g. the barrier fences themselves inducing asymmetry).

**Null-first discipline (C4596 pattern, applied)**: the noise model has NO crosstalk, so
the model predicts SYMMETRIC everywhere. ORDER-SYMMETRIC at both sites is therefore a
first-class WIN — a schedule-symmetry certification the vendor doesn't provide, with the
quantitative upper bound D_order ≤ D_obs + 5·SE reported as the certification strength
(subclaim, per the F93/F95 composite-floor discipline: existence-class headline, magnitude
as reported bound, no magnitude 5σ floor in the headline).

**Headline outcomes** (all first-class):
- Both sites SYMMETRIC → CERTIFIED SCHEDULE-SYMMETRY (new benchmark axis, switch-bench v2).
- Hotspot EXISTS + control SYMMETRIC → HIDDEN ORDER DISCOVERED (any classification is a
  novel unmodeled effect by construction → friction-report row on the noise model).
- Control EXISTS → NO-TEST (logged as such, no softening).

**Diagnostics (reported, not gated)**: split-half TVD per arm (empirical same-distribution
floor on hardware — checks the sim-derived FLOOR transfer assumption).

## Gate feasibility lint

Spec `experiments/exp118_gate_lint_spec.json`, tool `tools/gate_feasibility_lint.py`
(C4587). Existence gate at both sites: pass scenario D_order=0.05 (plausible amplified
crosstalk), fail scenario 0.0062 (sim true-symmetric bias), SE at budget 0.0032.
Verdicts recorded below at freeze; any VACUOUS verdict → redesign before flight.

- LINT RESULT (run at freeze): see `results/exp118_gate_lint.txt`.

## Predictions (registered with prediction-error-tracker at freeze)

- **P1** Control reads ORDER-SYMMETRIC (experiment is a valid test): **0.85**
  (NO-TEST 0.10; genuine control-side order 0.05).
- **P2** Hotspot reads ORDER-SYMMETRIC: **0.55**. Physics: CZ is diagonal; static ZZ
  crosstalk is also diagonal → commutes → order-symmetric. Hidden order requires
  during-gate non-diagonal dynamics (coupler transients, frequency-collision management)
  surviving ×8 amplification above a 0.022 floor — plausible (0.45), not favored.
- **P3** (conditional on hotspot EXISTS): par_class GENUINELY-CONCURRENT 0.50,
  UNRESOLVED-NEAREST 0.20, MIXTURE-LIKE 0.20, SECRETLY-first (either) 0.10.

## What would make this wrong (stated at freeze)

- FLOOR transfer: hardware same-distribution TVD bias could exceed the sim-derived floor
  (broader support from readout noise). Guards: control site NO-TEST rule + split-half
  diagnostics. If split-half TVDs land above FLOOR, the run is downgraded to NO-TEST at
  grade regardless of classifications (frozen now: split-half median across the 6 arms
  must be ≤ FLOOR for any EXISTS headline to stand; SYMMETRIC certifications quote the
  observed bound either way).
