# H13 Cell 4 — THE HINDSIGHT METER — **FROZEN PREREG** (C5058)

**Author**: Whisper (DC15W), C5058 (2026-08-11) · **Substrate**: claude-opus-5
**Creator GO**: "fly whatever else you can with the 91" (general#9189). **Venue**: ALT3 / ibm_marrakesh.
**Supersedes**: `h13-cell4-hindsight-prereg-DRAFT-whisper-c5048.md`. **Design sim**: `results/h13_cell4_hindsight_design_c5048.json`.

## Why THIS cell with the remaining seconds (the C5058 lesson, applied as a selection criterion)
Tonight's Cell 6+6b NO-TEST traced to **21 transpiled two-qubit gates per segment**, and the intended fix — a denser "cluster" layout — **does not exist on this hardware**: every 5-qubit connected subgraph on marrakesh has exactly 4 internal edges, because heavy-hex has no short cycles. With ε_CZ = 0.0072, the P1 ≥ 0.95 premise gate is unreachable above ~7 two-qubit gates. **The gate was right and the apparatus cannot meet it.** Cell 4 is selected because it has **ZERO two-qubit gates by construction** — the wall that killed 6+6b is structurally absent, not merely avoided. A transpiled-count gate in the submit script REFUSES to fly if the count is not 0.

## Claim (law-match genre — NO advantage card, nothing for attack_preflight)
The best guess of a mid-circuit outcome improves when conditioned on **past + future** rather than past alone, by exactly the amount the two-time (past-quantum-state) formalism computes: **gap(θ_f) = sin(θ_f)/2 × readout haircut**, across 7 angles.

## Apparatus (1 qubit, zero entangling gates)
Prep **|0⟩** → projective **mid X-measurement** (H · measure · H) → **Ry(−θ_f)** → final Z-measurement. Foresight is **exactly 1/2 by symmetry** (measuring X on |0⟩ is a fair coin) — the cleanest possible floor, and it is *measured*, not assumed. θ_f ∈ {0,15,30,45,60,75,90}°, 4000 shots each, + one no-mid control = **8 circuits**.
*Prep note, recorded because the dry run caught it:* an earlier build prepped |+⟩, which makes the mid X-measurement **deterministic** (foresight 1.000) and destroys the floor. Caught pre-flight; the frozen circuit preps |0⟩.

## Gates (bands frozen here)
- **G1 law-match**: measured gap(θ_f) within **±0.06** of `sin(θ_f)/2 × h`, where the haircut `h` is derived from the flown qubit's live readout error, **all 7 angles**.
- **G2 null point**: θ_f = 0° gap consistent with **zero within 2σ** — a future measurement orthogonal to the record carries nothing.
- **G3 foresight floor**: measured foresight = **0.500 ± 0.02** at every angle (the symmetry floor holds in data).
- **G4 ceiling label**: θ_f = 90° is a **TRIVIAL COPY** — the future re-reads the collapsed record. It is the ceiling, **not the claim**; the claim lives on the **mid-curve (30–60°)** where the future adds partial information it did not simply record. This label is mandatory in any headline.
- Three-state verdicts (PASS / FAIL / UNDERPOWERED) per house rules. **No postselection** — every shot scores.

## Fences
Intra-QM law-match, **not** a quantum-vs-classical advantage (H13 arc fence №5). Retrodiction here is a statement about optimal *inference* from a two-time record under the projective-measurement model — no retrocausal claim, no signalling (the mid outcome is already recorded before the final basis is chosen; the improvement is in the ESTIMATE, not in the past). Cost priced from the transpiled circuit, per the C5058 rule.
