# Exp122b — PHASE-BLIND TWIN RETEST: PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4653. Creator: "Green light go!" (retro R1: close the
asterisk before new fronts). Parent: Exp122 (C4651 — win-as-frozen, mechanism
CONFOUNDED: negative ⟨X⟩ exposed a coherent ZZ clock-pull my X-only estimator could
not separate from which-path decoherence). Sim/builders:
`exp122b_phase_blind_sim.py` → `results/exp122b_feasibility.json`.

## Question (mechanism adjudication — every outcome first-class, pre-filed)

Was Exp122's 67σ twin separation (a) genuine aging-marks-the-path decoherence,
(b) a coherent ZZ clock-pull rotation, or (c) both? Fix: **|V| = √(⟨X⟩²+⟨Y⟩²)**
(rotation-immune, Rice-bias-corrected, frozen estimator in the sim module) plus an
**echo arm** (X on C mid-delay; cancels static ZZ, leaves irreversible decoherence).
Echo bookkeeping verified at design: mid-delay X relabels branches so BOTH end with
the clock at L; emission records unchanged; no new distinguishability.

**Fake preview (pre-filed)**: fake delay noise is pure relaxation → Y≈0, |V|≈X,
echo≈raw (confirmed in sim). Hardware divergence between raw-X and |V|/echo IS the
ZZ measurement.

## Frozen apparatus

Builders byte-identical (`build_b`). Site: frozen chain rule REUSED
(`run_exp122_submit.select_chain`). Ladder rule REUSED ({0,0.15,0.3,0.6,1.2}·T̄ from
submit-time published T1s; grade by in-job calib — the 3-strike rule). Arms:
- exc, vac × 5 ladder pts × {X,Y readout} @20k = 20 pubs
- exc_echo × {0, dt3, dt4} × {X,Y} @20k = 6 pubs
- calib 2 lanes × 4 delays @10k = 8 pubs
**34 pubs, 600k shots, one job, ibm_marrakesh.** Seeds 4653 (transpile+shuffle).
Audit: uniform 2q counts per class (echo class separate — extra X), all inside site.

## Frozen statistics and gates

|V| per (arm, dt) from paired X/Y pubs (Rice-corrected, delta-method SE, frozen in
sim module). dt3/dt4 = ladder points 3/4.

- **G0 (NO-TEST)**: V_exc(0) > 0.7 AND V_vac(0) > 0.7 (fake 0.884/0.895).
- **W_TWIN (aging, phase-blind)**: sep(dt) = V_vac(dt) − V_exc(dt) − 5σ > 0 at dt3
  OR dt4 (pre-registered OR; both reported). Theory with C4651 in-job T1s
  (334/166µs): V-ratio √(p0p1) ≈ 0.81 at dt3 → sep ≈ 0.088 if V_vac ≈ 0.47;
  5σ ≈ 0.05 at budget → margin ~1.7×.
- **W_ROT (rotation)**: echoX_exc(dt3) − rawX_exc(dt3) − 5σ > 0 (echo recovers
  coherence that raw-X lost to static ZZ). C4651 raw-X at dt3 was −0.165; if
  rotation-dominated, recovery ≈ +0.4-class.
- **Verdict classification (frozen)**: W_TWIN∧W_ROT → **MIXED-BOTH-MECHANISMS**
  (aging certified + rotation quantified); W_TWIN only → **AGING-CERTIFIED-CLEAN**;
  W_ROT only → **CLOCK-PULL-CERTIFIED** (aging null at budget — first-class,
  the F96-style certification of the confound); neither → **UNRESOLVED**.
- **Subclaims (reported)**: measured V_exc/V_vac ratio vs √(p0p1) from in-job T1s
  (residual quoted); echo recovery fraction; Y-magnitudes (the rotation's direct
  signature); clock survivals.

## Predictions (registered at freeze — honest split)

- **P1** W_TWIN (aging real at 5σ): **0.55** (theory demands emission records exist,
  but at T1≈334µs the aging is SLOW; margin 1.7× only if V_vac holds up).
- **P2** W_ROT (rotation real at 5σ): **0.80** (the C4651 curves scream rotation).
- **P3** joint MIXED: **0.45**; CLOCK-PULL-only: **0.25**; AGING-only: **0.10**;
  UNRESOLVED: **0.15**; NO-TEST: **0.05**.

## R2 compliance (first applicable cycle)

`grade_exp122b.py --selftest` feeds synthetic counts through the FULL gate/
classification logic (4 scenarios: mixed, aging-only, rotation-only, unresolved)
and must print 4/4 PASS before hardware grading. Run at freeze; output in
`results/exp122b_selftest.txt`.

Lint: `experiments/exp122b_gate_lint_spec.json` → `results/exp122b_gate_lint.txt`.
