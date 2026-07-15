# Proposal — A Scalable 2D-HLF Instance Family for the Classically-Verifiable Lane

**Author**: Whisper (DC15W), C4744 (2026-07-15) · **Substrate**: claude-opus-4-8
**Status**: PROPOSAL / right-shape-wrong-scale — **no current quantum-side win over classical is claimed.**
**Source results**: F113 (Exp127-HW, 2D-HLF solver on silicon, n=4) · F114 (Exp134, ladder to n=9).
**Directive**: Creator — "draft the scalable-HLF problem proposal" (bridge B, C4744).

## One-paragraph summary

The 2D Hidden Linear Function (HLF) problem is the cleanest classically-verifiable task our campaign
already runs on hardware: a **constant-depth** quantum circuit solves it, the solution set is an
efficiently-computable coset (self-checking), and it sits on the one depth-separation theorem that needs
**no hardness conjecture** — Bravyi–Gosset–König (Science 2018): QNC⁰ ⊋ NC⁰. This proposal is to
contribute a **scalable instance family** to the tracker's *classically-verifiable* lane — a ladder of
2D-HLF instances on a heavy-hex grid with a frozen verifier. **The honest scope up front: at the sizes we
can run today (n ≤ 9), a classical algorithm also solves each instance, so this is not a live advantage —
it is a well-posed, self-verifying problem family whose *asymptotic* separation is proven and whose
crossover-to-classical-intractability is exactly the open quantity worth tracking.** It fits the lane's
structure (shared instance + efficiently-checkable witness) even though it does not yet fit the lane's
*advantage* bar.

## Why this belongs in the classically-verifiable lane

The lane's stated requirement (from `data/.../classically-verifiable`) is: *"demonstrate quantum advantage
by scoring solutions against known answers or efficiently checkable witnesses."* The 2D-HLF problem is a
textbook efficiently-checkable relation:

- **Instance**: a symmetric matrix `A ∈ {0,1}^{n×n}` and vector `b`, encoding a quadratic form `q(x)` over
  `F_2` supported on a 2D (heavy-hex) grid.
- **Valid answers**: the set of `z` such that `ℓ_z(x) = q(x)` for all `x` in the null-space — a **coset**,
  computable classically in poly(n) time (the circuit's Gauss-sum support). This is the "known answer /
  checkable witness."
- **Score**: fraction of shots landing in the valid coset. F113 measured **0.902 at n=4 (438σ over the
  uniform-random floor 0.25)**; F114 held a **strong majority through n=9** with the *logical* CZ-depth on
  an O(1) plateau (2→3→4) even as physical routing grew the 2q count 10→16→39.

Unlike the lane's sampling problems (peaked / random-graph), verification here needs **no classical
simulation of the circuit at all** — the coset is derived from `A` directly. That makes the verifier free
and exact at every scale, which is a genuinely nice property for a tracked problem.

## What is and is not claimed (honesty fence, inherited from F113/F114 + C4715 audit)

- **Claimed**: a self-verifying, constant-logical-depth problem family that runs on Heron silicon with a
  strong-majority score through n=9; a frozen, scale-free verifier; ties to an unconditional depth
  separation.
- **NOT claimed**: a runtime or cost win over classical on any instance we can run. At n ≤ 9 a laptop
  solves the instance directly; the BGK separation is **asymptotic** (as n→∞), so at fixed small n a
  constant-depth *classical* circuit also succeeds — the advantage is **theorem-carried, the on-chip
  result is the apparatus** (per the C4715 adversarial audit). The 438σ is fidelity over the uniform floor
  0.25, **not** a beaten classical bound.
- **The tracked quantity that would matter**: the largest n at which the hardware still clears strong
  majority. That number rising over hardware generations is the honest, supersede-able signal — it is where
  a future "classical can no longer keep up at constant depth on this family" claim would first appear.

## The instance family (proposed shared artifacts)

| Rung | n | Heavy-hex 2q (routed) | Logical CZ-depth | Status |
|---|---|---|---|---|
| R1 | 4 | 10 | 2 | flown (F113, `d9amnlvu62qs738o8nt0`) |
| R2 | 6 | 16 | 3 | flown (F114) |
| R3 | 9 | 39 | 4 | flown (F114) |
| R4 | 12–16 | (to route) | O(1) plateau | **proposed next rung** |
| R… | ↑ | ↑ | O(1) | ladder continues until strong-majority breaks |

Each rung ships as: the `A`/`b` instance definition, the QASM circuit, the poly-time coset verifier, and
the measured score + job ID. The definition files and verifier already exist in the repo
(`experiments/exp127*`, `experiments/exp134*`); packaging them to the tracker's `problem definition files`
format (circuit + a one-page nontriviality justification) is the concrete submission work.

## Why propose it despite no current advantage

1. **It is the right *shape*** — the one lane where our hardware genuinely competes on the lane's own terms
   (a verifiable relation, not a theorem ceiling), which is exactly the structural gate established in the
   C4743 tracker review. Every other campaign result fails that gate.
2. **The verifier is free and exact at all scales** — a property the sampling problems lack, useful to the
   community regardless of who holds the advantage.
3. **It defines the crossover to watch** — a shared, growing instance family is precisely how the tracker's
   "active-until-superseded" model is supposed to accumulate evidence over time.

## Recommended framing to the maintainers

Submit as a **new problem** in the classically-verifiable category, explicitly labeled *"constant-depth
verifiable family; asymptotic (BGK) separation; no claimed finite-n cost advantage — proposed as a tracked
scaling ladder."* Let classical solvers race the ladder; the interesting entry is the first n where a
constant-depth classical method is measurably strained. Do not overstate — the value is the well-posed
family and its free verifier, not a win today.

---
*Companion: `experiments/exp140-...preregistration` (bridge A — observable-estimation race support).
Both bridges trace to the C4743 tracker-scope review: A is the one live cost-race we can support; B is the
one lane whose *structure* we fit, at a scale that is still ahead of us.*
