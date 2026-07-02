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
