# Exp136 Pre-Registration — ONE-SIDED DEVICE-INDEPENDENCE: Quantum Steering on One Chip

**Author**: Whisper (DC15W), C4677 (2026-07-14) · **Substrate**: claude-opus-4-8
**Status**: FROZEN before hardware submission (advisor-scoped pre-freeze, C4677)
**Directive**: Creator "next one" — the real semi-DI step Exp135 flagged: a certificate valid
under a weaker, chip-appropriate trust structure than full DI.

## Scope, stated first — why steering is honest on one chip where DI CHSH was not

Exp135 showed the DI CHSH randomness bound needs no-signaling between two sites, which one chip
cannot enforce — a shared-control classical device saturates S=2√2 at zero entropy, so the DI
quantity was **fully** fakeable (Type-B, quarantined). Steering is different, on three precise
points:

1. **The residual loophole is bounded, not total.** By the LHS theorem, any separable state
   obeys S₃ ≤ 1. Faking the expected violation (**~1.667**) requires manufacturing correlation
   excess of order **~0.67**. The only on-chip mechanism that can do that is Alice's-setting
   back-acting on Bob's qubit via **crosstalk** — which this campaign has itself measured at the
   **~1% level** (C4671 correlated tail; F55/F56 structured noise). Percent-level crosstalk
   cannot fake a 0.67 excess. That quantitative gap is the entire reason this certificate holds
   on one chip and the CHSH one did not.

2. **The assumption is exact at the logical level.** One-sided no-signaling (Alice's setting ⇏
   Bob's marginal) is *mathematically exact*: for any bipartite ρ and any local unitary on
   Alice, Tr_A(U_A ρ U_A†) = Tr_A(ρ). So the assumption fails *only* through physical
   crosstalk, never through the state — a strictly stronger statement than "structurally
   motivated."

3. **The null is the measured faking floor.** The separable-state arm (product |+⟩|0⟩) at
   S₃ ≈ 0 is direct empirical evidence that *this apparatus does not manufacture steering
   correlations from a separable state* — the load-bearing control here. Honest limitation: it
   bounds faking for *this* separable state, not an adversarially-chosen one.

**What is claimed**: a **one-sided device-independent** entanglement/steerability certificate
under **Bob-measurement-trust** (Bob's are the trusted mutually-unbiased X/Y/Z triple; Alice is
a **black box** whose outcome-sign relabel is already absorbed into the functional). This is a
genuine step up from Exp135's tier-2 (Alice goes from trusted to black-box). **What is NOT
claimed**: not loophole-free (Alice/Bob are not space-like separated — locality loophole open;
adversarial-crosstalk loophole bounded, not closed); not full DI.

## Apparatus

|Φ⁺⟩ = (|00⟩+|11⟩)/√2 on a calibration-gated adjacent pair (1 CX). Bob (q1, TRUSTED) and Alice
(q0, black box) measure matched axis ∈ {X,Y,Z}. CJWR linear steering functional
**S₃ = (1/√3)|⟨XX⟩ − ⟨YY⟩ + ⟨ZZ⟩|** — sign-matched to |Φ⁺⟩; the −1 on Y is absorbed into
Alice's untrusted A_Y → −A_Y, so the CJWR **LHS (unsteerable) bound = 1** for the trusted MUB
triple is unchanged; quantum max = √3 ≈ 1.732. Main arm (entangled) + null arm (separable). 3
axes × 2 arms × 20k + 2 sentinels ≈ 128k shots, shuffled (seed 4677), co-batched.

## Frozen gates

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_STEERING_ONE_SIDED_DI** (primary) | steerable (⇒ entangled) under Bob-trust; beats the LHS bound | S₃ > 1 + 5·SE |
| **W2_QUANTUM_BOUND** | apparatus honesty — no super-quantum result | S₃ ≤ √3 + 5·SE (violation ⇒ audit, not a win) |
| **W3_FAKING_FLOOR** | measured separable-state faking floor | null-arm S₃ ≤ 1 (expected ≈ 0) |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

**Figures of merit**: S₃ with σ-clearance over the LHS bound 1; the ~0.67 faking-excess-vs-1%-
crosstalk gap; the null faking floor. **Fake preview**: S₃ = 1.667 (well above 1, 96% of √3),
null 0.003. Noiseless S₃ = 1.732 = √3, null 0.003, PASS.

**Pre-filed predictions**: W1 HIT conf 0.95 (S₃ ≈ 1.60–1.68 on a good pair, ~60σ over 1);
W2 respected conf 0.93; W3 HIT conf 0.95; G_SENT conf 0.93.

**NO-TEST**: sentinel failure → window NO-TEST; S₃ > √3 + 5σ (super-quantum) → apparatus audit.

## Relation to the campaign

Completes the randomness/certification mini-arc: Exp135 (on-chip CHSH — quantum witness +
fully-trusted randomness, DI quarantined) → Exp136 (one-sided-DI steering — Alice demoted to a
black box under the weaker chip-holdable assumption). The honest ladder of trust: full-trust
(Born) → one-sided-DI (steering, here) → full-DI (needs space-like separation, off-chip). Each
rung claims exactly its assumption, no more.
