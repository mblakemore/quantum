# Exp141 — PRE-REGISTRATION: the BGK 2D-HLF constant-depth solver on Quantinuum H2 (native all-to-all, past the heavy-hex routing wall)

**Author**: Whisper (DC15W), C4744 (2026-07-15) · **Substrate**: claude-opus-4-8
**Status**: FLIGHT-READY DRAFT — contingent on **Azure Quantum / Quantinuum access** (new billing channel,
Creator decision). Not frozen until access exists and the instances are generated + committed.
**Lineage**: extends F113 (BGK solver on silicon, n=4) and F114 (heavy-hex ladder to n=9). The move here is
**topology**: H2's all-to-all connectivity embeds the 2D grid with **zero SWAP routing** — the exact
limiter that walls the heavy-hex ladder (physical 2q count 10→16→39 while logical depth stays O(1)).

---

## Scope fence (read first — inherited from the C4715 audit, non-negotiable)

This is a **depth-separation demonstration**, NOT a quantum cost-race advantage. 2D-HLF is in **P**
(Gauss-elimination over F₂ solves any instance in poly(n)); a real classical computer beats this at every
size. The BGK separation is **QNC⁰ vs NC⁀⁰** — constant-depth quantum vs constant-depth *classical circuit*
(Ω(log n) required) — and it is **asymptotic**, so at any fixed grid a constant-depth classical circuit
also solves it. **The advantage is theorem-carried; what this run certifies is the constant-depth apparatus
executing correctly on native-connectivity hardware at 25–49 grid vertices.** Every grade table carries the
"compared-to-what" row. No tracker-advantage claim is made.

## Hypothesis / pre-registered outcomes

**H**: on H2's all-to-all topology, the constant-depth BGK solver clears strong-majority-valid at grids
(5×5, 7×7) far beyond the heavy-hex n=9 ladder, because zero routing keeps the *physical* 2q count equal to
the grid edge count (40, 84) instead of ballooning it. Both outcomes pre-registered (informative-null
discipline, per F114): where — if anywhere — does P(valid) fall below strong majority?

## Instances (frozen at generation time)

- **Grid family**: square lattice m×m, one qubit per vertex. **First run m=5 (25 qubits, 40 edges);
  stretch m=7 (49 qubits, 84 edges).** H2 has 56 qubits → 7×7 fits with headroom.
- **HLF instance**: symmetric `A ∈ F₂^{N×N}` supported on the grid adjacency (A_ij=1 iff (i,j) is a grid
  edge), plus linear `b ∈ F₂^N`. **3 random (A-on-grid, b) instances per grid size**, seeded and committed
  before flight (seeds frozen in this doc at generation).
- **Circuit** (plain BGK-2018 Clifford solver, identical to F113): `H^⊗N · (CZ on each grid edge) · (S on
  each i with b_i=1) · H^⊗N`, measure all in the computational basis. Logical depth O(1): grid edges
  4-colour → 4 CZ layers + 2 H layers + 1 S layer. On H2 each grid-edge CZ = one native 2q gate, **no SWAPs**.

## Verifier (free, exact, poly-time — reuse F113/F114 code, do NOT rebuild)

The valid set is the circuit's **Gauss-sum support**: the coset `{z : ℓ_z(x)=q(x) ∀x∈L}` computed
classically in poly(N) directly from `A,b` (the F113/F114 `valid-z set recomputed in-artifact` routine).
No circuit simulation, exact at every scale. Grader frozen with this pre-reg.

## Pre-registered grade gates

1. **W1_STRONG_MAJORITY**: P(valid z) > 0.5, per instance, per grid size. (Primary. Strong-majority, not a
   point estimate — the fidelity model below is an optimistic ceiling.)
2. **W2_COSET_COVERAGE**: every valid z appears; the empirical distribution over the coset is near-uniform
   (χ² not rejecting uniform at the pre-filed level) — defeats a lazy single-answer mimic (W3 of F113).
3. **W3_COMPARED_TO_WHAT** (mandatory honesty row, not a pass/fail): record that a classical solver returns
   a valid z with P=1 at this N; the certified object is the constant-depth apparatus, advantage inherited
   from BGK asymptotics.
4. **W4_LADDER**: does strong-majority persist 5×5 → 7×7 (like F114's ladder), or is there a boundary? Both
   pre-registered.

## Expected P(valid) — fidelity-product model, calibrated to F113 (0.996^10 → measured 0.90)

H2 specs (June 2026): 2q 99.9%, 1q ~99.99%, SPAM ~99.9%.

| Grid | N | CZ | model P(valid) | note |
|---|---|---|---|---|
| 5×5 | 25 | 40 | 0.999⁴⁰·0.9999⁶²·0.999²⁵ ≈ **0.93** | vs ~0.50 for the same grid routed on heavy-hex (~140 CZ) |
| 7×7 | 49 | 84 | 0.999⁸⁴·0.9999¹²²·0.999⁴⁹ ≈ **0.86** | |

**Caveat (binding on the gate)**: 99.9% is the *gate* fidelity; H2 executes serially via ion shuttling, so
memory/idle error accrues over the run and is not in that number — real P(valid), especially at 7×7, likely
a few points lower. Hence the pre-registered bar is **strong-majority (>0.5)**, not the point estimate.

## HQC budget + $ estimate (formula confirmed from Quantinuum data sheet)

`HQC = 5 + C·(N₁q + 10·N₂q + 5·Nm)/5000` (C = shots). 2q term dominates (weight 10); CZ counts exact.

| Circuit | shots | HQC | $ @ $10.3/HQC | $ @ $12.5/HQC |
|---|---|---|---|---|
| 5×5 | 500 | 80 | ~$820 | ~$1,000 |
| 5×5 | 1000 | 155 | ~$1,600 | ~$1,940 |
| 7×7 | 500 | 156 | ~$1,610 | ~$1,950 |
| 7×7 | 1000 | 307 | ~$3,160 | ~$3,840 |

**First campaign** (3 instances each at 5×5 + 7×7, 1000 shots) ≈ **1,386 HQC ≈ $14k–$17k**, and **fits inside
one Standard-plan month (10,000 HQC)** with ~8,600 HQC to spare.

**Rate provenance / uncertainty**: the $/HQC is *derived* from Quantinuum's Azure subscription plans
(Premium $175,000/mo ÷ 17,000 HQC ≈ $10.3/HQC; a Standard tier implies ~$12.5). **Pay-as-you-go per-HQC is
not publicly listed — requires a Quantinuum sales quote** (sales@quantinuum.com). So the $ band is an
estimate, not a posted price; a subscription makes it a flat monthly fee regardless of run count. The HQC
numbers themselves are exact from the formula.

## Cost gate (analog of the QPU budget policy)

- Per-shot HQC well under the 50-HQC/shot hard cap (5×5 = 0.15, 7×7 = 0.30). Job ≤ 10,000 shots (hard limit).
- Freeze instances + seeds before flight; ABORT if the generated coset is degenerate (|coset| = full space
  or single point → no discrimination).
- Any spend needs Creator ack (this is a new paid channel, not the IBM tranche).

## What a green result establishes

The BGK constant-depth solver at **25 then 49 grid vertices** — a 3–5× leap past the heavy-hex n=9 — on
hardware where routing no longer fights the 2D structure, cleanly extending the *depth-separation*
demonstration to the largest on-silicon grids we can reach. Not a tracker advantage (2D-HLF ∈ P), but the
strongest version of the F113/F114 milestone.
