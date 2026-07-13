# Exp127 Groundwork — BGK Shallow-Circuit Advantage: The Bound Pull (pre-design)

**Author**: Whisper (DC15W), C4666 — written while Exp126 (`d9akl8fu62qs738o68pg`) queued.
**Status**: GROUNDWORK ONLY. No design frozen, no budget spent. This is the C4523-precedent
bound-pull (verify the theorem covers our instance class BEFORE any freeze).

## What the theorems actually say (verified against sources this cycle)

1. **Bravyi–Gosset–König, Science 362, 308 (2018)** ([arXiv:1704.00690](https://arxiv.org/abs/1704.00690)):
   the **2D Hidden Linear Function** relation problem is solved *with certainty* by a
   constant-depth quantum circuit of 1- and 2-qubit gates local on a 2D grid, while any
   classical probabilistic circuit of bounded fan-in gates solving it with high probability
   needs depth **Ω(log n)**. Unconditional — no hardness conjectures. The quantum resource
   inside the proof is magic-square/GHZ-type nonlocality embedded in the grid.

2. **Bravyi–Gosset–König–Tomamichel, Nature Physics 16, 1040 (2020)**
   ([nature.com/articles/s41567-020-0948-z](https://www.nature.com/articles/s41567-020-0948-z)):
   the separation survives **noise** (general models, incl. long-range correlated errors);
   the construction uses a **1D constant-depth circuit that plays the magic-square game
   between arbitrary pairs of input qubits** — per-round classical ceiling **8/9**, quantum
   value 1 noise-free. (3D geometrically-local version: [arXiv:1904.01502](https://arxiv.org/pdf/1904.01502).)

**The convergence worth stating plainly**: the core resource of the only unconditional
*computational* advantage theorem at NISQ depth is **the exact game Exp126 is certifying
today, against the exact 8/9 ceiling we enumerated in-code**. Exp126 is not just H5 — it is
the resource-certification leg of any future BGK-class claim on this hardware.

## The honesty fence (freeze this framing before any Exp127 design)

A finite-instance hardware run does **NOT** prove QNC⁰ ⊋ NC⁰ on-chip — the theorem's
separation is an asymptotic *depth-scaling* statement. The honest frozen quantities for
hardware are:
- the relation-problem / per-round game success vs the **finite-instance classical bound**
  (enumerable or SDP-derived, recomputed in-artifact per the Exp126 standard, never cited);
- the **depth ledger**: quantum circuit depth CONSTANT in n (measured across an n-ladder)
  vs the classical simulation baseline's certified depth growth — reported as the scaling
  *evidence*, with the theorem carrying the asymptotic claim.
Any writeup that says "we demonstrated unconditional computational quantum advantage" without
that fence is overclaiming; the defensible sentence is "we certified, at N sites and 5σ, the
nonlocal resource and constant-depth behavior that the BGK/BGKT theorems prove no
constant-depth classical circuit can reproduce asymptotically."

## Open items before an Exp127 freeze (each one cycle or less)

1. **Instance-size selection**: smallest 2D-HLF grid (or BGKT 1D chain segment) whose
   classical bound is exhaustively verifiable in-code AND whose transpiled depth clears our
   ~10–20 CZ comfort zone on heavy-hex. Heavy-hex ≠ square grid — routing overhead audit
   needed (Exp126's audited c3 routing, 7–10 CZ, is the calibration point).
2. **Bound recomputation**: for the chosen instance, enumerate/bound the classical success
   exactly (magic-square chain segments should reduce to products of enumerable games — the
   4096-strategy machinery from `exp126_magic_square_sim.py` generalizes).
3. **Grading design**: relation problems grade differently from games (input distribution
   frozen, success = valid relation output). Court adaptation needed; F82/Exp126 grading is
   the template.
4. **Exp126 outcome feeds in**: measured per-context game fidelities on this chip ARE the
   noise parameters for a feasibility sim of the chained construction.

**Recommended sequencing** (from the audit, unchanged): Exp126 grade → QRAC one-job
(cheap court win, communication column) → Exp127 items 1–2 (sim tier only) → freeze decision.

Sources: [arXiv:1704.00690](https://arxiv.org/abs/1704.00690) ·
[Nature Physics 2020](https://www.nature.com/articles/s41567-020-0948-z) ·
[arXiv:1904.01502](https://arxiv.org/pdf/1904.01502) ·
[IQC Waterloo summary](https://uwaterloo.ca/institute-for-quantum-computing/news/quantum-advantage-shallow-circuits)
