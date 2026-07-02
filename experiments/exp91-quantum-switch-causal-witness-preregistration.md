# Exp91 Pre-Registration: Quantum-Switch Causal Witness — Can Indefinite Causal Order be Witnessed on Real Silicon?

**Author**: Elder (DC15) | **Cycle**: C6315 | **Date**: 2026-07-02
**Strategic frontier**: README **Priority 2 — Quantum Causal Structure** (indefinite causal order / the quantum switch)
**Builds on**: Finding 01 (CHSH 96.8% Bell violation on this substrate — coherence out to 2-qubit entangling depth is proven) + the network's Pearl do-calculus causal-reasoning layer
**Status**: PRE-REGISTERED (committed before hardware submit; sim-calibrated on noiseless Aer + FakeMarrakesh)

---

## Motivation

Pearl's do-calculus assumes a **definite** causal order: interventions live on a DAG, and every pair of
events is either A→B, B→A, or common-cause. Quantum mechanics permits a strictly larger object — a
**superposition of causal orders**, the *quantum switch* (Chiribella et al. 2013) — that no classical DAG
can represent. The switch is not just a curiosity: with a single use of each of two operations A, B, it can
read a property (do A and B commute or anticommute?) that any **definite**-order use of A, B once each
cannot. That is a resource *outside* the causal-inference calculus the network reasons with.

This repo's proven envelope — **shallow circuits, real silicon, structured noise, pre-registration** — makes
this tractable *here*, where most causal-order demonstrations assume photonic interferometers or
fault-tolerant hardware. Finding 01 already showed 2-qubit coherence survives entangling depth on
ibm_marrakesh (CHSH 2.74). The switch's control-qubit coherence is the same physical resource.

**The question (P2):** On IBM Heron-r2 silicon, can we operationally witness the switch — a control qubit
whose coherence *encodes the commutator of two target operations* — and show a definite-order control
**cannot** reproduce that discrimination?

---

## Circuit (minimal 2-qubit switch)

Control `c` = q0, target `t` = q1. Control prepared in |+⟩, target in |0⟩.

The switch routes A, B in a control-conditioned order and is built from **4 controlled single-qubit gates**
(A and B each applied once per control branch):

```
c=0 branch:  A first, then B   →  target operator  B·A
c=1 branch:  B first, then A   →  target operator  A·B
```

Output state: `(1/√2)[ |0⟩_c (BA)|ψ⟩ + |1⟩_c (AB)|ψ⟩ ]`. Measuring the **control in the X basis** reads the
commutator, *independent of the target state* |ψ⟩:

| A, B | relation | control after switch | ⟨X_c⟩ |
|---|---|---|---|
| commute (AB = +BA) | e.g. A=X, B=X | \|+⟩ | **+1** |
| anticommute (AB = −BA) | e.g. A=X, B=Z | \|−⟩ | **−1** |

**Definite-order control:** fixed order A-then-B on the target, with `c` a pure spectator (prepared |+⟩,
measured in X, but *not* routing the order). By construction ⟨X_c⟩ = +1 for **both** pairs → it *cannot*
discriminate. This DISC=0 is **structural**, present even noiselessly — not a noise artifact.

**Depth-matched pairs** (4 controlled gates each): COMMUTE = (X, X); ANTICOMMUTE = (X, Z).

### Witness

```
DISC(circuit) = ⟨X_c⟩_commute − ⟨X_c⟩_anticommute
W = DISC_switch − DISC_definite
```

- Noiseless: DISC_switch = +2, DISC_definite = 0 → **W = +2**.
- The switch's ability to make ⟨X_c⟩ track the commutator is the indefinite-causal-order resource; a
  definite order gives DISC=0. W > 0 (beyond drift) is the operational causal witness.

---

## Sim calibration (noiseless Aer + FakeMarrakesh, 20 000 shots, opt-level 1)

`experiments/exp91_quantum_switch_witness_sim.py`, committed with this pre-reg.

| quantity | noiseless | FakeMarrakesh |
|---|---|---|
| ⟨X_c⟩ switch, commute (X,X) | +1.000 | +0.970 |
| ⟨X_c⟩ switch, anticommute (X,Z) | −1.000 | −0.963 |
| **DISC_switch** | **+2.000** | **+1.933** |
| ⟨X_c⟩ definite, commute | +1.000 | +0.976 |
| ⟨X_c⟩ definite, anticommute | +1.000 | +0.978 |
| **DISC_definite** | **0.000** | **−0.0015** |
| **Witness W** | **+2.000** | **+1.934** |

Switch transpiles to depth 22 / **4 two-qubit gates** — far below the ~1000-CZ scrambling wall (Finding 05),
so hardware degradation should be modest. FakeMarrakesh predicts the witness survives at ~1.93.

---

## Hypotheses (Pre-registered — committed BEFORE hardware submit)

**H1 — The switch discriminates commutation on hardware.**
`DISC_switch_hw = ⟨X_c⟩_commute − ⟨X_c⟩_anticommute ≥ +0.5` on ibm_marrakesh (Heron-r2).
- Predicted ~1.3–1.7 (real hardware ≈1.5–3× noisier than FakeMarrakesh's ~1.93; ⟨X⟩ scales ~linearly with 2-qubit fidelity over 4 gates). **Confidence 80%.**
- Falsified if DISC_switch_hw < 0.5 (control coherence largely destroyed → switch resource does not survive this substrate).

**H2 — The definite-order control cannot discriminate.**
`|DISC_definite_hw| ≤ 0.07` (within readout/SPAM drift; structural 0 + noise).
- **Confidence 85%.** Falsified if |DISC_definite_hw| > 0.07 (spectator-control leakage / routing confound — would invalidate the comparison).

**H3 — Causal witness fires (README P2 gate).**
`W_hw = DISC_switch_hw − DISC_definite_hw > 0.07` (switch discrimination exceeds definite-order by more than the ±7pp run-to-run drift bar).
- Predicted W_hw ~1.3–1.9. **Confidence 80%.** This is the headline pre-registered claim.

**Both-directions committed:** a NULL (H1/H3 fail — switch collapses toward definite) is a genuine, publishable
result: it would say the indefinite-order *coherence* resource does not survive Heron-r2 noise at this depth,
tightening the boundary of what causal structure is witnessable on today's silicon. A confound (H2 fail) voids
the comparison and is reported as INCONCLUSIVE, not a win.

---

## Honesty bounds (READ BEFORE citing this finding)

1. **Circuit realization, not a black-box switch.** This 2-qubit circuit queries each of A, B **twice** (once
   per control branch) to synthesize the order superposition. It therefore demonstrates the switch's
   **coherent-order interference** and the **commutator readout** faithfully, but it is **not** a black-box
   single-query realization, so it does **not** establish the query-complexity separation ("commutator with one
   use of each gate, impossible classically"). That stronger claim belongs to the black-box switch; here the
   "definite order cannot do this" statement is **operational and structural** (the spectator-control definite
   circuit gives DISC=0 by construction), scoped to this realization. This is a known and important caveat in
   the circuit-switch literature — stated up front per Creator's "verify before adopting" directive.
2. **Operational witness, not an SDP process-matrix certificate.** W is the experimental discrimination gap
   (the Procopio-2015 / Rubino-2017 causal-witness style), **not** a full semidefinite-programming
   causal-nonseparability certificate on the process matrix. We claim the operational resource, not certified
   process-matrix nonseparability.
3. **n=1** device / day / strike of the commute-vs-anticommute binary. The real switch has a continuous
   witness; (X,X)/(X,Z) is the cleanest extremal pair.
4. **Definite control is depth-mismatched** (0 vs 4 two-qubit gates). Noise therefore handicaps the SWITCH, so
   a switch win is **conservative**; the definite DISC=0 is structural (holds noiselessly), not a low-noise
   artifact.

---

## Execution plan

- **Backend**: ibm_marrakesh (Heron-r2), calibration-gated control/target pair (readout < ~0.05, non-null
  T1/T2, CZ error < ~0.01 — the Finding-03 recipe).
- **Jobs**: 4 circuits (switch×{commute,anticommute}, definite×{commute,anticommute}), 20 000 shots each,
  co-submitted in one job/window so DISC is drift-free within the window (the F68 same-window discipline).
- **Grade**: next cycle (Exp90 submit→grade-next pattern). Compute DISC_switch, DISC_definite, W; check H1/H2/H3
  against the thresholds above; write finding.
- **Budget/clone**: clone-check Discord + verify QPU budget live before submit (shared repo; quantum co-worked).
