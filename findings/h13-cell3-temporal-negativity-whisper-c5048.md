# Finding — H13 Cell 3: THE TEMPORAL NEGATIVITY METER — a density matrix with a negative eigenvalue, 293σ deep, and the certificate that this correlation lived in time

**Cycle**: C5048 · **Date**: 2026-08-09 · **Backend**: `ibm_fez` · **Job**: `d9rufentfhrs73ds52cg`
(27 circuits: 18 temporal + 9 spatial control, 2000 shots each; account IBMQ_ALT2; temporal qubit 22, spatial pair (137,147)). **Prereg**: [FROZEN at e7ca10d](../docs/h13-cell3-pdm-prereg-FROZEN-whisper-c5048.md), committed before flight. Creator GO: general#7376. **First flight of the H13 Temporal Investigations arc. All four frozen gates HELD — verdict PASS.**

## Result

| quantity | measured | frozen criterion | verdict |
|---|---|---|---|
| **min-eig(R_temporal)** | **−0.4782 ± 0.0016 (292.8σ below PSD)** | < 0 at ≥5σ, band [−0.50, −0.30] | **G1 HELD** |
| min-eig(R_spatial) — Φ⁺ control | −0.0105, SE 0.0072 (within −2·SE = −0.0145) | ≥ −2·SE | **G2 HELD** |
| off-diagonal \|c_ij\| (temporal) | max 0.026 | ≤ 0.10 | **G3 HELD** |
| singles (temporal, I/2 input) | max \|c\| 0.023 | ≤ 0.06 | **G4 HELD** |

Diagonal two-time correlators: c_XX = +0.972, c_YY = +0.979, c_ZZ = +0.962 — **all three positive at once**, the pattern no bipartite quantum state can carry (any physical state with all three near +1 would violate positivity; the maximally entangled states cap at sign pattern (+,−,+) up to local frames). The same estimator pipeline pointed at an actual Φ⁺ pair reads (+0.956, −0.943, +0.938) and assembles into a PSD matrix, exactly as a state must.

## The sentence made true

A density matrix's eigenvalues are probabilities — they cannot be negative. We measured a "density matrix" (the Fitzsimons–Jones–Vedral pseudo-density matrix of one qubit at two times) whose smallest eigenvalue is **−0.478, half a probability below zero, at 293σ**. That negative number is a *certificate of temporality*: no two systems side by side in space could produce these statistics; only one system visiting two moments can. The campaign's arrow meter (Exp194) measures how much of the past is irreversible; this meter measures **whether a correlation is made of time at all** — and it read 96% of the theoretical maximum (ideal −0.5).

## Ledger

- Priced at c ≈ 0.90 from T0.4; measured c ≈ 0.97 — qubit 22's 0.24% readout beat the noise-model class. min-eig landed at −0.478, inside the frozen band [−0.50, −0.30] with room.
- Zero two-qubit gates in the temporal arm (F102 lineage); zero postselection anywhere — every shot kept.
- Falsifier structure: the spatial arm. It landed at −0.0105 with SE 0.0072 — negative-but-within-2SE, exactly the "genuine state reads PSD within error" behavior the prereg demanded. Had the pipeline manufactured negativity, it would have shown here.
- **Cost accounting (miss, kept)**: estimated 3–5 QPU-s, billed **16 QPU-s** — the historical shallow-flight heuristic (~60µs/shot-circuit) under-prices mid-circuit-measurement circuits ~3×. ALT2 now reads 606/600 (IBM soft-caps at job granularity). Lesson: **price MCM circuits at ~3× the shallow heuristic** until a measured per-shot rate replaces it.

## Fence

Negativity is certified **under the frozen sequential projective measurement model** (rotate–measure–unrotate, identity evolution). Symmetric readout error only shrinks correlators and pulls toward PSD — the conservative direction for the headline. This is a temporal-correlation witness, not an advantage claim; nothing here needed a claim card.

*The meter's first reading: this correlation could not exist between two objects. Only between two moments.*
