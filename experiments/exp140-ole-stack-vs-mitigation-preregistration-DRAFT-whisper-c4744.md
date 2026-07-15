# Exp140 — PRE-REGISTRATION (DRAFT, not yet frozen/flown): does the characterization stack sharpen a *mitigated* Operator-Loschmidt-Echo estimate at tracker scale?

**Author**: Whisper (DC15W), C4744 (2026-07-15) · **Substrate**: claude-opus-4-8
**Status**: **SIM-GATE PASSED (Option 2 done, C4744) → design frozen → awaiting only the QPU ack (Option 1).**
Creator picked "2 & 1". The sim-tier feasibility kill-gate PASSED (see `exp140-sim/RESULT-...c4744.md`):
the tracker's literal `49x648` echo signal clears the shot floor across the realistic depolarizing range;
ground truth is **exactly 1.0** (α=0 mirror echo). Frozen design below. Not yet flown.
**Bridge**: A (C4744) — the one live quantum-vs-classical *cost/accuracy race* our findings can support.
**Target instance**: `operator_loschmidt_echo_49x648` (tracker `/data`, observable-estimations lane).

---

## The finding that reshapes this test (read first)

Bridge A was framed as "stack-on vs stack-off." Inspecting the tracker's **actual submissions** kills that
framing: **the quantum contenders on this lane are error-mitigated.** IBM's OLE hardware submissions use
**"Global rescaling"** (`ibm_boston`, `ibm_pittsburgh`); the su2_hadron contender uses **readout-error
mitigation + a differential measurement protocol** (120 qubits, 2q-depth 259). The classical field is
strong: Belief-Propagation Tensor Networks (BD 192–512), Single-path Monte Carlo (UChicago/EPFL/Flatiron).

**Consequence**: a raw "stack-on vs raw stack-off" hardware run is a **strawman** — it says nothing about a
race whose quantum entrant is mitigated. The honest comparison is:

> **stack + mitigation** vs **mitigation-alone**, both graded against a **known ground truth**.

Our stack (noise-aware placement F57/F58/F65–70; sentinel window-gating F81; IPE/semiclassical readout
F51) is a set of causal interventions on the noise DAG that are **independent of** and **compose with** the
contenders' mitigation (global rescaling / REM act on residual bias; placement+window act on which/when).
So the test is well-posed and non-redundant — but it is a **project**, not a one-shot flight.

## The ground-truth unlock (and its unavoidable tension)

The OLE observable `f_δ(O)` has **no classical ground truth at α≠0** — that is *why* it is a contested
active candidate. But at **α = 0 (no scattering)** the evolution is `U = (U_b†)^L (U_b)^L = I` exactly, so
`f_δ(O)` reduces to `(1/2ⁿ)·Tr(O V_δ† O V_δ)` with `V_δ = e^{-iδG}`, `G = Σ_{P} X` — **analytically
computable at 49–70 qubits** because it is local in `O` and `G` (no full-circuit simulation needed).

- **α = 0** → *truth, but no live competitor* (classical also nails the identity trivially).
- **α ≠ 0** → *live competitor, but no truth* (the whole point of the lane).

You cannot get both on one instance. So the α=0 run is **not** a claimed advantage — it is a
**trust-calibration of the quantum estimator at contested depth**: evidence that the stack pulls the
*mitigated hardware estimate* close enough to the *known* α=0 value that the *same pipeline's* α≠0 number
deserves to be believed over (or alongside) the tensor-network value. That is bridge A stated honestly —
"race support," a reason to trust the quantum entrant, not a new win.

## Instance & cost (the `49x648` circuit, verified from the QASM)

- 49 active qubits (156-qubit register), **648 CZ gates**, native Heron basis (rz/rx/cz/sx). Observable
  `O = Z_{52} Z_{59} Z_{72}` (3-body). Deep but in IBM's demonstrated utility regime.
- OLE estimator: average `f_δ^{z}(O)` over `N_init` random initial basis states `|z⟩`; SE ∝ 1/√N_init.
- **Cost driver**: circuits = `N_init × arms`. Arms = {mitigation-alone, stack+mitigation} (+ optional raw
  baseline for the record). With `N_init = 12` and 2 arms = 24 deep circuits × ~4000 shots.
- **Estimated QPU time: ~120–240 s** (648-CZ circuits are slow per shot). **This crosses the 180 s
  Creator-ack threshold** (QPU budget policy C4536, rule 2) and debits the **window/characterization
  tranche**. → **Requires Creator ack before any submit.**

## Pre-registered design (to be FROZEN on Creator scope decision)

1. **Grader (frozen)**: analytic α=0 value `f_δ*(O)` computed from `O`, `G`, `δ` — locked in-artifact
   before the flight, with the computation shown. Primary metric = `|f̂ − f_δ*|` (absolute estimation
   error vs truth).
2. **Arms**: (a) mitigation-alone = global rescaling + REM at default/vendor placement; (b) stack+mitigation
   = same mitigation + quiet-qubit placement (live) + sentinel window-gate + IPE readout where applicable.
   Optional (c) raw = neither, **for the record only** (not the headline comparison).
3. **Primary gate `W_A_STACK_SHARPENS`**: `|f̂_stack+mit − f_δ*|  <  |f̂_mit − f_δ*|` with the gap
   exceeding the bootstrapped SE by ≥ pre-filed margin (e.g. `Δerr − 2·SE_boot > 0`). Both outcomes
   informative (a null = "the stack adds nothing beyond mitigation on this observable" is a real, publishable
   result and part of the honesty record).
4. **Window/sentinel gate**: fly the sentinel first; ABORT to the *characterization tranche* if the nowcast
   says NO-GO (weather-service `--nowcast`), preventing a drained-tranche run in a bad window.
5. **Sim-first (no QPU)**: (i) confirm the analytic α=0 ground truth against a *noiseless local check*;
   (ii) a noisy-model pass (FakeMarrakesh) to confirm the stack-vs-mitigation delta is even **resolvable**
   at 648 CZ before spending QPU. **If the noisy sim shows the delta is below SE, do not fly** — report the
   negative feasibility instead (anti-F55-false-precision discipline).

## FROZEN DESIGN (post sim-gate, C4744) — ready to fly on ack

- **Instance**: `operator_loschmidt_echo_49x648` (tracker literal), O = Z₅₂Z₅₉Z₇₂, 648 CZ / 49 qubits.
- **Ground truth**: **f_δ(O) = 1.0 exactly** (α=0 mirror echo; O disjoint+commuting with the rz(0.3)
  perturbation; U=I confirmed by 100% CZ palindrome + ± angle-pair census). Freeze-time guard: one
  symbolic gate-by-gate inverse check before submit.
- **Arms**: (a) mitigation-alone (global rescaling + REM, default/vendor placement); (b) stack+mitigation
  (same + live quiet-qubit placement F57/F58 + sentinel window-gate F81). Optional (c) raw, record-only.
- **Primary metric**: `|f̂ − 1.0|` (deviation of the mitigated estimate from the exact echo value).
- **Primary gate `W_A_STACK_SHARPENS`**: `|f̂_stack+mit − 1| < |f̂_mit − 1|` with the gap `> 2·SE_boot`.
  Null (stack adds nothing beyond mitigation) is informative and kept.
- **Shot budget**: **≥ 24 initial states × 4000 shots × 2 arms** (kill-gate margin; 30×8000 if the window
  is poor). Sentinel `--nowcast` first; ABORT to the characterization tranche on NO-GO.
- **Cost / ack**: ~120–240 s of the window/characterization tranche → **crosses the 180 s Creator-ack
  gate (budget policy C4536 rule 2)**. This is the one remaining gate.

## The decision for the Creator (scope fork)

- **Option 1 — full honest project**: build/confirm the global-rescaling arm to match the contenders, run
  the α=0 trust-calibration at 49-qubit scale (stack+mit vs mit-alone). Needs the ack above + the
  sim-feasibility green light. Highest fidelity to the actual race.
- **Option 2 — lighter first step**: sim-tier only this cycle (analytic truth + FakeMarrakesh resolvability
  study), no QPU; fly only if the delta is shown resolvable. Zero budget risk, defers the hardware number.
- **Option 3 — design-only**: freeze this pre-reg as the standing plan, fly when a
  window/characterization tranche flight is next scheduled.

**Recommendation**: **Option 2 → then 1.** The sim-feasibility gate is cheap, protects the tranche, and
directly answers the one thing we don't yet know — *is the stack's delta even visible under 648-CZ
mitigation?* If yes, the α=0 hardware flight is worth the ack; if no, we have an honest negative that
saves the QPU. This mirrors the campaign's sim-before-silicon discipline and the C4536 cost-gate rule.

---
*Reshaping finding logged: the observable-estimation contenders are mitigated — the honest bridge-A test is
stack+mitigation vs mitigation-alone, graded at α=0 where truth exists but the competitor is trivial (a
trust-calibration), because α≠0 has the competitor but no truth. Companion: `docs/proposal-hlf-...c4744`
(bridge B). Neither over-claims; both trace to the C4743 tracker-scope review.*
