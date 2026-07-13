# Exp120 — Quantum Darwinism × Indefinite Causal Order (DESIGN)

**Author**: Whisper (DC15W), C4643. Horizons-2 Q2 (crown jewel), Creator-directed.
**Status: DESIGN + sim tier this cycle; freeze on a fresh cycle (no-tired-freeze).**

## The question nobody has asked

Classical objectivity emerges when the environment makes redundant records of a
system's pointer state (Zurek's Quantum Darwinism). Every treatment assumes the
record-making events happen in DEFINITE causal order. We own the only certified
apparatus for indefinite order. Question: **what happens to objective records when
the order of record-making is quantum-indefinite?**

## The design subtlety that shapes everything (found at design time)

Copy operations to distinct fragments in the SAME basis **commute** — a switch of
commuting channels is order-symmetric by construction and the experiment would null
trivially. The non-trivial physics is the **pointer-basis competition**: environment
fragment F1 records Z_S while fragment F2 records X_S. Those copy operations do NOT
commute on S; order genuinely matters (the last recorder tends to win the basis
war); and superposing THAT order asks the real question: when it is indefinite
*which incompatible fact got recorded first*, what survives as objective?

## Apparatus (4 qubits: control C, system S, fragments F1, F2)

- S prepared at Ry(π/4)|0⟩ — the in-between state, ⟨Z⟩=⟨X⟩=1/√2: both records
  nontrivial, neither basis privileged.
- **copy-Z**: CZ(S,F1) with F1 in |+⟩, read in X (phase-kickback recorder — CZ IS a
  Z-copier into the fragment's X frame). **copy-X**: H_S·CZ(S,F2)·H_S, same readout.
- Controlled versions for the switch: CCZ(C,S,F1) and H_S·CCZ(C,S,F2)·H_S — the H's
  cancel identically when the control is off, so ONLY the CCZs need control (checked
  in sim by the null arm).
- **2-switch**: C in |+⟩; slot sequence [X(C)·CCZ₁·X(C)][X(C)·H CCZ₂ H·X(C)][H CCZ₂ H][CCZ₁]
  → C=0: Z-then-X; C=1: X-then-Z. Herald C in X basis (±).
- Cost class: 4 CCZ ≈ 24 2q gates on a star-of-S layout — same depth class as the
  certified 22-CZ switch skeletons.

## Arms

| Arm | Content | Role |
|---|---|---|
| ordZX / ordXZ | plain definite orders | the two classical endpoints |
| mix | 50/50 arithmetic pool of ordZX/ordXZ | classical-mixture hull |
| switch | full skeleton, C heralded ± | the indefinite-order branches |
| null | full skeleton, C=|0⟩ (no H) | apparatus honesty: must reproduce ordZX |

2 pubs per arm (S read in Z / in X; fragments always X) → 8 pubs.

## Observables and witness (drafted; frozen numbers only after sim)

- **A_Z** = P(F1 record = S Z-outcome), **A_X** = P(F2 record = S X-outcome) —
  per arm, per herald branch. The (A_Z, A_X) plane: definite orders = two points;
  every classical mixture = the segment between them.
- **Objectivity witness w = A_Z + A_X** (total record fidelity). **Hull rule**: any
  causally-definite process (fixed order, classical mixture, measure-and-reroute)
  satisfies w ∈ [min, max] of the definite arms. A heralded switch branch outside
  that interval at 5σ = **objectivity structure impossible under definite order**.
- Directionality (which of plus/minus branch, which side of the hull) is THEORY-FIXED
  — the sim tier computes exact branch values; the prereg freezes bands
  procedure-theory style (residual bands, as in F86-F95).
- Null-first discipline (C4596): if theory says the branches stay INSIDE the hull,
  the experiment preregisters as a certification (Darwinism is order-robust —
  objectivity survives indefinite order; a real invariance, publishable), with the
  hull-violation as the alternative. The sim decides which is the leading outcome.

## Sim tier deliverables (this cycle)

1. Exact statevector A_Z/A_X for all arms and branches + herald rates.
2. Witness geometry: where the switch branches sit vs the hull; effect size.
3. FakeMarrakesh at budget: SEs, integrity of the null arm, feasibility verdict.
4. Power inputs for the c4130_001 calculation at freeze.

## Why either answer is deep

- **Branches outside the hull**: records exist that no definite-order history can
  produce — "facts without a causal history." The strongest result available.
- **Branches inside the hull**: classical objectivity is invariant under causal
  indefiniteness — definite order is NOT a precondition of facts. A certified
  invariance the decoherence literature currently assumes without proof.
