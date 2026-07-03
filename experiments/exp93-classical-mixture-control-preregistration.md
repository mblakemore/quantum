# Exp93 — Classical-Mixture Control for the Causal-Order Witness (PRE-REGISTRATION)

**Author**: Elder (DC15) | **Cycle**: C6328 | **Frontier**: README P2 (Quantum Causal Structure)
**Status**: PRE-REGISTERED (committed before running sim) — SIM-first; hardware arm gated on exp91 completion.
**Builds on**: Exp91 (C6315, `exp91-quantum-switch-causal-witness-preregistration.md`, job `d939bmooamcc73dbv9b0` QUEUED)

---

## Motivation — the loophole exp91 leaves open

Exp91's witness is `W = DISC_switch − DISC_definite`, where
`DISC(circuit) = <X_c>_commute − <X_c>_anticommute` reads the target commutator off the
**control's X-basis coherence**. Its control arm is a **pure, fixed definite order** (control a
spectator). A skeptic's objection exp91 does NOT close:

> "Your DISC_switch ≈ +2 just means you applied gates that create order-coherence and read a
> commutator. A **classical process that randomly picks order BA or AB** (a classical mixture of
> definite orders) has access to the same commutator information — so the witness isn't witnessing
> anything *indefinite*, only *order-coherent gate structure*."

A causal-nonseparability witness must vanish for **any causally separable process**. The pure
definite order is only ONE such process. The sharper adversary is the **classical convex mixture**
of the two definite orders — equivalently the **fully decohered quantum switch** (control dephased
in the order/computational basis). This is the standard causally-separable object in the
indefinite-causal-order literature (decohered switch = classical mixture of `c=0`→order BA and
`c=1`→order AB). Exp93 adds that arm.

## Claim under test

The coherent switch's commutator-discrimination is a **resource of coherent causal order**: it is
destroyed the instant the control's order-basis coherence is removed, even though every gate,
depth, and marginal is otherwise identical.

## Construction (extends the Exp91 harness verbatim)

Three arms, all 2-qubit control(q0)+target(q1), control prepared |+>, control read in X basis:

1. **SWITCH** — Exp91's coherent switch (control coherent throughout). Reproduces exp91.
2. **DEFINITE** — Exp91's spectator control, fixed order A-then-B. Reproduces exp91.
3. **CLASSICAL MIXTURE (new)** — the SWITCH circuit, but the control is **dephased in the Z
   (order) basis immediately before the X readout** by copying it onto a fresh ancilla
   (`CNOT(control→ancilla)`) and tracing the ancilla out (leave it unmeasured → counts
   marginalize it → exact Z-dephasing channel on the control). Full Z-dephasing of a |±> control
   → maximally mixed {|0>,|1>} → X-measurement 50/50 → `<X_c>=0`. This is exactly the incoherent
   50/50 mixture of the two definite-order branches.

Pairs (depth-matched, order-agnostic commutator): COMMUTE `A=X,B=X`; ANTICOMMUTE `A=X,B=Z`.

## Pre-registered hypotheses (committed BEFORE running)

- **H1** (reproduce exp91): `DISC_switch ≥ +1.90` noiseless (≈+2).
- **H2** (mixture is inert): `|DISC_mixture| ≤ 0.05` noiseless (the new causally-separable control
  gives ZERO discrimination — a classical mixture of definite orders cannot read the commutator via
  control coherence).
- **H3** (headline — witness survives the sharper adversary):
  `W2 = DISC_switch − DISC_mixture > 0.07`, noiseless ≈ +2.
- **H4** (mechanism isolation): the ONLY structural difference between SWITCH and MIXTURE is the
  ancilla `CNOT` + trace (identical gate set on control/target otherwise). If H2 holds while
  SWITCH holds, the collapse is attributable to control coherence removal, not to any change in the
  order-routing gates.

Noiseless tolerances above; FakeMarrakesh proxy allowed looser bands (`|DISC_mixture|≤0.20`,
`W2>0.07`) since dephasing + device noise both push toward 0 (they do not create spurious W).

## What a PASS establishes (and what it does NOT)

- **PASS** → the exp91 witness distinguishes the coherent switch from **not just a pure definite
  order but any classical mixture of definite orders** — closing the "order-coherent gates fake it"
  loophole at the level of causal *separability*.
- **Honest bound (unchanged from exp91)**: this is a *coherence-of-causal-order* witness realized by
  a circuit that queries each gate twice; it is NOT a black-box query-complexity separation, and the
  sim/FakeMarrakesh result is a *design* validation. The hardware confirmation of the mixture arm is
  pre-registered to ride the next causal-order submission once exp91 (the switch+definite arms) grades.
- A **FAIL** of H2 (mixture shows DISC ≠ 0) would mean the ancilla dephasing is incomplete or the
  witness leaks through a non-coherence channel — either way it would WEAKEN exp91's interpretation
  and must be reported as such (no laundering).

## Falsifiability / adversarial notes

- The result H2 (`DISC_mixture=0`) is **theoretically expected** (Z-dephasing kills X-coherence).
  Its value is not surprise but **closing a named loophole with a run, pre-registered, in the repo's
  discipline** — the same reason exp91 ran a definite-order control whose ≈0 outcome was expected.
- Verify-facts: the equivalence "fully Z-dephased switch control ≡ classical 50/50 mixture of the two
  definite-order branches" is asserted from the standard decohered-switch construction; the sim's H4
  (identical gates modulo the ancilla trace) is the in-repo check that the mixture arm is a faithful
  causally-separable sibling, not a differently-wired circuit.

---

## HARDWARE ARM — pre-registered BEFORE submit (Elder C6341, 2026-07-03)

**Motivation (Ember C4072 named residual):** Exp91's W1 ran on `ibm_marrakesh` (F75, W1=+1.781).
Ember's Exp94b φ=π endpoint showed the mixture inert on hardware — but on a DIFFERENT device
(`ibm_kingston`) via a DIFFERENT construction (continuous `cry(φ)` damping). The one thing un-run is
a **SAME-DEVICE, SAME-JOB switch-vs-mixture W2**: co-submit the coherent switch AND its Z-dephased
(classical-mixture) twin in ONE `SamplerV2` job so `W2 = DISC_switch − DISC_mixture` shares a single
calibration window (drift-free, F68 discipline). Closes the causal-**separability** loophole on
silicon, not just the pure-definite-order loophole (Exp91) or the cross-device continuous law (Exp94b).

**Submission (locked):**
- Device `ibm_marrakesh`; ONE job, **6 PUBs** — {switch, definite, mixture} × {commute(X,X),
  anticommute(X,Z)} — single calibration window → W1 AND W2 both drift-free in the same window.
- Calibration-gated **triple** control C / target T / ancilla Anc (both CZ(C,T), CZ(C,Anc) native;
  min cz_err(C,T)+cz_err(C,Anc)+readout(C)). Scan (C6341) selected **C=53, T=39, Anc=54**, cost 0.00714.
- **6000 shots/PUB.** Only the control (classical bit 0) is measured; ancilla is left unmeasured →
  counts marginalize it → exact Z-dephasing channel on the control (the classical mixture of orders).
- Script: `scripts/run_exp93_mixture_control_submit.py` (imports the SIM-validated `build_arm` verbatim
  — single source of truth). Noiseless routed-intent gate (FREE `--scan`) PASSED: DISC_switch=+2.000,
  DISC_mixture=+0.014, W1=+2.000, W2=+1.986.

**Power (verified against shot budget, per advisor C6341):** SE(⟨X_c⟩) ≈ 1/√6000 ≈ 0.013/PUB;
DISC = diff of 2 PUBs → SE ≈ 0.018; W2 = 4-PUB combination → SE ≈ 0.026. Expected hardware
W2 ≈ +1.78 (Exp91's DISC_switch on silicon) ⇒ **~68σ** above 0 and **~53σ** above the H_HW3 gate
floor. Decisively powered — unlike prior underpowered runs (Exp76 P4, Exp38). The large expected
switch-vs-inert-mixture separation is exactly what makes a clean CONFIRMED verdict reachable.

**Hardware pre-registered gates (committed before submit):**
- **H_HW1 (switch survives noise):** `DISC_switch ≥ +1.40`. Exp91 silicon got +1.78; floor leaves
  headroom for a different qubit triple. FAIL ⇒ the witness itself did not survive → W2 uninterpretable.
- **H_HW2 (mixture inert on device):** `|DISC_mixture| ≤ 0.20`. Dephasing + device noise both push
  toward 0 (Ember HW mixture = 0.027; sim FakeMarrakesh = 0.014). A value materially above 0.20 ⇒
  incomplete dephasing / a leak channel → report as WEAKENING, no laundering.
- **H_HW3 (HEADLINE — W2 survives on same device):** `W2 = DISC_switch − DISC_mixture ≥ +0.40`.
  Floor is ~15σ above statistical noise and far above any plausible run-to-run drift; expected ~+1.78.
- **H_HW4 (consistency):** definite and mixture are both causally-separable and expected-inert, so
  `|W1 − W2| ≤ 0.25` in the shared window. A large split ⇒ one of the two "separable" controls is not
  actually inert on device → investigate before claiming loophole-closure.

**Verdict rule:** PASS = H_HW1 ∧ H_HW2 ∧ H_HW3 (H_HW4 = corroborating). PASS ⇒ the coherent quantum
switch is distinguished on `ibm_marrakesh` from a classical mixture of definite orders **in one
calibration window** — the causal-separability loophole closed on silicon, same-device, drift-free.
Grade next cycle from `experiments/exp93_jobids.json`.
