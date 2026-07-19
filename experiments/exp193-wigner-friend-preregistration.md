# Exp193 Pre-registration — THE FRIEND IN THE MACHINE: are observed facts absolute?

**Cycle**: C4886 · **Backend**: ibm_fez · **Shots**: 8000 × 8 · Creator go: "fly the 3".
**Class**: foundations capstone of the late-choice lineage (Brukner Wigner's-friend Bell test;
Proietti-style, circuit form).

## The question
Two labs share a Bell pair. In each lab a FRIEND qubit measures the system (an entangling CX —
a recorded fact). The superobservers then choose late, per side: **TRUST the fact** (read the
friend's record, effectively θ=0) or **OVERRULE it** (coherently reverse the friend's
measurement — CX again — and measure the system at ±π/3). If the friends' facts are absolute
(one observer-independent value exists once recorded), the facts-CHSH
S = E(F,F) + E(F,B₁) + E(A₁,F) − E(A₁,B₁) obeys **S ≤ 2**. QM predicts 2.5 at these angles.
And the deeper twist: COPY the facts to the environment (a dump-qubit CX — decoherence) and
the reversal fails — absoluteness returns (ideal S = 1.75). **Facts become facts when they
are copied.**

## Arms (8 circuits)
live × 4 setting pairs {trust/overrule}² · decohered (friend records copied to dumps) × 4.
6 qubits: a, F_A, dump_A, b, F_B, dump_B. Angles: A₁ = +π/3, B₁ = −π/3 (S_ideal = 2.5).

## Criteria (formulas; se_S ≈ √(Σ(1−E²)/N) ≈ 0.019)
- **Primary**: S_live > 2 at ≥5σ. Band **2.15–2.45** (ideal 2.50).
- **Decoherence restores absoluteness**: S_dec ∈ **1.55–1.90** (ideal 1.75), UNDER 2, with
  S_live − S_dec ≥ 0.30 at ≥5σ.
- **Fact correlation gauge**: E(F,F) ≥ 0.85 both arms (the records really record).
- **Audit**: friend-record marginals independent of the other side's choice (spread < 0.035,
  se-derived).
## Fences
Friend = one qubit (a memory, not a human); "reversal" is exact only for an isolated memory —
which is the point the decohered arm makes; one die; compiled choices (the live-coin upgrade
is priced machinery if wanted later). Selftest gates: S_live=2.50, S_dec=1.75, E(F,F)=1.
