# H13 Cell 4 — The Hindsight Meter — PREREG DRAFT

**Author**: Whisper (DC15W), C5048 · **Status**: DRAFT — freeze at fly time. **Design sim**: `results/h13_cell4_hindsight_design_c5048.json`.
**Queue**: behind door(b) on ALT3 per Creator directive. Cost ~10-15s (8 circuits).

## Claim (law-match genre — NO advantage card)
The best guess of a mid-circuit measurement outcome improves when conditioned on the future
record, by exactly the amount the two-time formalism computes: gap(θ_f) = sin(θ_f)/2 × readout
haircut. **Design finding baked in**: the naive "maximize the gap" working point (θ_f = 90°) is
a TRIVIAL COPY — the future measurement re-reads the collapsed state. It stays in the sweep as
the labeled ceiling; the claim lives on the mid-curve (30–60°), where the future genuinely adds
partial information it did not simply record.

## Apparatus
Prep |0⟩ · projective mid-circuit X-measurement (foresight = 1/2 exactly, by symmetry — the
cleanest possible floor) · final measurement along θ_f ∈ {0,15,30,45,60,75,90}° · guess-rate
computed per arm from raw records, forward (mid only) vs smoothed (mid|final). 4000 shots/angle
+ one no-mid control. Zero 2q gates. No postselection — every shot scores.

## Gates (bands freeze at fly time)
G1: gap(θ_f) inside per-angle bands tracking sin(θ_f)/2×haircut, all 7 points. G2: θ_f=0 point
consistent with zero (±2σ) — the future carries nothing orthogonal. G3: foresight rate = 0.500
± band at every angle (the floor is exact, not fitted). G4: no-mid control — final-record
marginals flat (the mid measurement's disturbance signature present/absent as theory demands).
Verdicts three-state per house rules.
