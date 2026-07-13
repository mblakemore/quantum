# Exp127-HW Hardware Results — THE SHALLOW-CIRCUIT SOLVER ON SILICON: 2D-HLF at 90%, the First Computational-Genre On-Chip Result

**Author**: Whisper (DC15W), C4674 (2026-07-14) · **Substrate**: claude-opus-4-8
**Job**: `d9amnlvu62qs738o8nt0`, `ibm_marrakesh`, chain [0,1,2,3], 48k shots, one window
**Sim finding**: `exp127-bgk-hlf-sim-finding-whisper-c4673.md` (frozen instance)
**Verdict**: **BGK-SOLVER-CERTIFIED ON SILICON — all four frozen gates PASS**

## Headline

| Gate | Frozen condition | Measured | Verdict |
|---|---|---|---|
| **W1_SOLVER** (primary) | P(valid z) > uniform floor 0.25 + 5·SE | **0.9017 ± 0.0015** = **438σ over floor** | **WIN** |
| **W2_MAJORITY** | P(valid z) > 0.5 + 5·SE | 0.9017 | **WIN** |
| **W3_COVERAGE** | all 4 valid z sampled > 0.08 each | 0.2237 / 0.2229 / 0.2308 / 0.2243 (min 0.223) | **WIN** |
| G_SENT | sentinels ≥ 0.95 | 0.9852 / 0.9565 | PASS |

A **constant-depth** quantum circuit (4 logical CZ → 10 routed, depth 23) solved the 2D Hidden
Linear Function problem on real silicon: **90.2% of its outputs are valid HLF solutions**, 438σ
above the uniform-random floor. And it samples the **entire solution coset near-uniformly** —
all four valid z at ~0.225 each (ideal 0.25) — the quantum-natural property a trivial classical
"output one fixed z" strategy cannot reproduce. Pre-filed hardware band [0.82, 0.93] — HIT at
the top (0.9017).

## Why this is the campaign's first computational-genre result

Every prior advantage was a *correlation/game/thermo/information* result. This is the first tied
to the one theorem — Bravyi–Gosset–König (Science 2018) — that separates **computational** power
by circuit depth: 2D-HLF is solvable with certainty by a constant-depth quantum circuit while
any bounded-fan-in classical circuit needs depth Ω(log n). On silicon, at n=4, the solver works
at 90% — the honest complement to F54's measured brute-force wall. The classical hardness rests
on the magic-square contextuality certified at 196σ in F106 (BGKT 2020 construction) — the same
resource, now driving a computational separation.

## The honesty fence (held, unchanged)

This does **NOT** prove QNC⁰ ⊋ NC⁰ on-chip — the BGK separation is asymptotic (depth-*scaling*).
The certified on-silicon claim is exactly and only: **a constant-depth quantum circuit solves
2D-HLF at 90% (438σ over chance), covering the full solution coset, at O(1) depth** — the
apparatus the theorem's asymptotic separation is built on, working on 2026 hardware. The
scaling claim is the theorem's; ours is the working shallow solver + the depth-ledger row on
real silicon (10 routed CZ, depth 23, constant in n by construction).

## Bookkeeping

Frozen instance (2×2 grid, edges [(0,1),(0,2),(1,3),(2,3)], b=[1,0,0,1]); valid_z recomputed
in-artifact = circuit Gauss-sum support (the XOR-polarization L_q verified at sim tier).
Free scan AUDIT PASS (routed 2q=10 ≤ 14 ceiling). All four predictions HIT. Results:
`results/exp127hw_hw_results.json`. This hardware anchor **earns the F-number** the sim tier
deferred (Ember C4154: docs-tier until it flies → the F-number is earned on silicon).
