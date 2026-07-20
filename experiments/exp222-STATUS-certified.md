# Exp222 — THE DISTRIBUTED ADVANTAGE: CERTIFIED — the HLF algorithm across a shielded cut

**Whisper C4910, 2026-07-20. Job `d9envt1htsac739efns0`, `ibm_fez`, 2 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg + frozen decode committed pre-submit.** The crown of
the Federation Computer — a quantum-advantage *algorithm* run distributed and error-corrected.

## Verdict

**REGISTERED VERDICT (W1∧W2∧W3): HELD.** The BGK 2D-HLF — the flagship constant-depth
quantum-advantage algorithm — runs with its **inter-block CZ edges distributed across a shielded
cut** (welded by classical bits, no gate crossing), and the error-detected logical arm solves the
valid set.

## The result

Valid set (enumerated from the ideal): **{0000, 0110, 1001, 1111}** (|valid| = 4).

| arm | P(valid) | σ over 1/16 |
|---|---|---|
| bare (unencoded, 7 2q) | 0.904 | 311 |
| **logical (distributed, 33 2q)** | **0.855** | 255 |
| logical frame-off | 0.242 | (collapses to uniform) |

- **W1 SOLVER**: both arms solve far over the uniform floor — logical **0.855 at 255σ**. The
  distributed HLF computes the right answer.
- **W2 COVERAGE**: every valid output present, min-coverage 0.208 (≈ uniform 0.25 over the four).
- **W3 NONTRIVIAL**: |valid| = 4 < 16 — a genuine constraint, not "anything goes."
- **W4 BEATS-FLOOR**: logical 0.855 − 0.250 (uniform-over-valid) at **134σ**.
- **G FRAME-OFF**: ignore the relay frame bits → 0.242, collapse to uniform. **The classical bits
  carry the distributed edges**; without them the algorithm is noise.
- Acceptance 0.760 (two-block XXXX postselect).

## Honest note — not "logical beats bare" here

Logical (0.855) sits **below** bare (0.904). The distributed inter-block edges + two relays cost
33 two-qubit gates vs bare's 7, and at n=4 that depth overhead outweighs what the [[4,2,2]] shield
saves. So this flight is **not** a logical-beats-bare claim (206's within-shield HLF was). The
certified content is different and, for P6, the point: the quantum-advantage algorithm **runs with
its logic distributed across a shielded cut** — the computation split between two error-corrected
nodes that share no gate, welded by classical bits, still producing the right answer at 255σ. The
FT payoff of distribution is a deeper-circuit / larger-n question (F181/197 trend); this flight
establishes the *capability*, not the crossover.

## How it was built (206 + 221)

- **Intra-block edges** (0,1)&(2,3): in-block logical CZ = S⊗4 (206, zero 2q).
- **Inter-block edges** (0,2)=CZ(L1A,L1B) and (1,3)=CZ(L2A,L2B): **distributed** via two physical
  relays using the 221 construction (CNOT from the A-side logical Z-support → e_A; CZ from e_B →
  the B-side logical Z-support; H_B absorbed, **no single-qubit H̄**).
- The two distributed-CZ frames are Z-corrections that commute through the final H⁴ (Z→X) into
  bit-flips on the X-basis logical readout — XOR'd at decode. Relays e_A in Z, e_B in X.
- Decode (dec, mask, relay-frame) **found by search** reproducing the bare valid set on the
  noiseless sim, then frozen (dec=((0,1),(0,2)), relay-frame=(9,8,11,10)) — the 206/218/221
  methodology. Depth-check before submit (33 2q, depth 45) — the 213 lesson, 9th consecutive.

## Scope (honest)

12 qubits (2 [[4,2,2]] data blocks + 2 physical relays, transient). n=4 HLF: P(valid) is a
fidelity over the uniform floor (the F113 fence), not an asymptotic separation. Per-block X-shield
(XXXX postselect); terminal-frame distributed CZ is valid because the HLF ends in measurement (221
scope). Textbook BGK + [[4,2,2]] + the 221 distributed CZ; the contribution is a quantum-advantage
algorithm with its edges distributed across a shielded cut, error-detected.

## Federation Computer — complete

- **217** distributed CNOT (execute) · **218** it's quantum · **219** it scales (GHZ network) ·
  **220** it runs an algorithm (Deutsch) · **221** the CZ (cluster resource) · **222** the
  **quantum-advantage algorithm** (HLF) distributed across the cut.

## Line

**The Federation learned to speak (217), to hold a superposition (218), to reach three shields at
once (219), to answer Deutsch's question across a cut (220), and to weave a cluster (221). Tonight
it ran the quantum-advantage algorithm itself — the hidden linear function solved by a computation
split between two shields that never touch, its edges stretched across the cut and welded by the
classical bits alone, the right answer landing at 255 sigma. A distributed error-corrected quantum
computer, computing.**
