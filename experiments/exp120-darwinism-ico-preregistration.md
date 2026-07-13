# Exp120 — QUANTUM DARWINISM × INDEFINITE CAUSAL ORDER: PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4644. Creator: "Run your next cycle - Exp120." Fresh-cycle
freeze (design+sim C4643 per no-tired-freeze). Design: `exp120-darwinism-ico-design.md`.
Sim: `exp120_darwinism_ico_sim.py` → `results/exp120_feasibility.json`.

## Claim under test (RESOURCE-SCOPED — the C4643 self-catch, load-bearing)

Two record-making operations on system S: **copy-Z** (into F1) and **copy-X** (into F2)
— incompatible recorders; the pointer-basis competition. Witness w = A_Z + A_X (record
fidelities vs S's own measured outcomes). **Scope**: processes composed of ONE use of
each of these two operations (as implemented, same window), in fixed order, classical
mixture of orders, or dynamical (measured-control) order — for all of these,
w ∈ [min, max] of the two measured definite arms. NOT claimed: a bound on all
definite-order processes (an intermediate-basis copy reaches w≈1.707 — disclosed at
design, out of scope by construction).

**Exact theory** (statevector, in-code): definite orders are winner-take-all
(w_ZX = w_XZ = 1.5 — the hull is a point). Switch branches: **plus (rate 3/4)
A_Z = A_X = 5/6, w = 5/3** (objectivity SHARED between incompatible records);
**minus (rate 1/4) A_Z = A_X = 1/2 exactly, w = 1** (every record erased).

## Frozen apparatus (builders byte-identical: `exp120_darwinism_ico_sim.py::build`)

- S = Ry(π/4)|0⟩; F1,F2 = |+⟩ phase-kickback recorders; copy-Z = CZ(S,F1);
  copy-X = H_S·CZ(S,F2)·H_S; switch = 4-slot CCZ skeleton, C heralded in X.
- Arms × S-basis: ordZX, ordXZ, switch, null(C=|0⟩ through full skeleton) × {z,x}
  = **8 pubs × 30,000 shots = 240k, one job, ibm_marrakesh**.
- **Site (frozen deterministic rule, live map at submit)**: hub S = degree-≥3 qubit
  minimizing summed 2q-error over its best 3 edges (dead-qubit guard as Exp118);
  roles: C = hub-neighbor with lowest readout error (herald quality), F1/F2 =
  remaining two by edge error. Layout [C,S,F1,F2]. Transpile seed 4644, opt 1,
  shuffle seed 4644.
- **Audit (go/no-go)**: every 2q gate inside the 4-qubit site; switch+null pubs share
  ONE 2q count; definite pubs share one count; counts recorded in manifest.

## Frozen gates (existence headlines vs the MEASURED same-window hull — F82 style)

Hull = [w_min, w_max] over the two measured definite arms. SE_w = √(SE_AZ²+SE_AX²);
diffs use √(SE_w1²+SE_w2²).

- **N1 (NO-TEST guard, classification not band — F96 depth lesson)**: null arm must
  read ZX-like: A_X(null) − A_Z(null) > 0.2 (theory +0.5, fake +0.42). Fail → NO-TEST.
- **H1 (NO-TEST guard)**: herald minus-rate ∈ [0.10, 0.40] (theory 0.25, fake 0.28).
- **W_PLUS (headline 1)**: w(plus) − 5σ_diff > w_max → **plus branch holds MORE
  objectivity than any ordering of these recorders** (fake preview: +0.112, ~23σ).
- **W_MINUS (headline 2)**: w(minus) + 5σ_diff < w_min → **minus branch holds LESS
  than any ordering** — record erasure beyond causal-order explanation (fake: −0.42, ~49σ).
- **Null-first (C4596)**: if both branches land INSIDE the measured hull at 5σ →
  **ORDER-ROBUST-OBJECTIVITY** grades as a first-class certification outcome
  (pre-filed, though theory predicts violation).
- **Subclaims (reported, NOT gated — composite-floor)**: record symmetry
  |A_Z − A_X| per branch (theory 0); minus-branch erasure depth |A − 1/2| (theory
  exactly 0; fake shows +0.02-0.04 noise bias — a 5σ exactness band would fail on
  noise alone, so erasure exactness is reported with theory residuals, never gated).

## Predictions (registered at freeze)

- **P1** W_PLUS: **0.80** (fake margin 23σ; risk = hardware routing depth on a real
  star site + control decoherence collapsing branches toward the mixture).
- **P2** W_MINUS: **0.90** (fake margin 49σ; the more robust direction).
- **P3** NO-TEST (N1 or H1): **0.07**.

Lint: `experiments/exp120_gate_lint_spec.json` → `results/exp120_gate_lint.txt`.
Grader `scripts/grade_exp120.py` FROZEN with this prereg. Estimators imported from
the sim module — byte-identical, zero drift.

## What either outcome means (pre-filed)

- Violations land: **records exist that no ordering of these recorders can produce**
  — objectivity beyond causal history (plus), and heralded runs where no fact was
  written (minus). First Darwinism × ICO measurement, period.
- Inside hull: **objectivity is order-robust** on this hardware — a certified
  invariance the decoherence literature assumes without proof.
