# Exp129 Pre-Registration — THE NAVIGATOR'S SEXTANT: GHZ Metrology vs the Standard Quantum Limit

**Author**: Whisper (DC15W), C4668 (2026-07-13)
**Status**: FROZEN before hardware submission
**Directive**: Creator ("F107 numbered, run the next one!") — audit item (c), the *practical*
advantage class: entanglement-enhanced phase estimation. Completes the advantage-genre sweep:
games (F106), storage (F107), and now **metrology**.

## Scope, stated first

- **What this is**: a measured **Fisher-information advantage** for phase estimation. N=3
  probes sense the same phase φ. Separable probes each yield a cos(φ) fringe — per-shot Fisher
  information F_sep = 3·V₁². A GHZ probe yields ONE fringe at **3φ** (super-resolution) —
  F_GHZ = 9·V₃². Advantage ⇔ F_GHZ > F_sep at equal qubits and equal shots. **The SQL
  reference is executed, not assumed** (the Exp128 standard): both Fisher informations are
  measured on the same three physical qubits in the same window and the same shot budget.
- **What this is NOT**: not Heisenberg *scaling* (that needs an N-ladder — natural follow-up),
  not a sub-shot-noise interferometer deployment, not loophole-anything. Rz phases are
  compiler-frame rotations; the claim is about the probe state's information content per shot,
  the standard GHZ-metrology figure. Prior art plain: GHZ phase super-resolution is textbook
  (Bollinger et al. 1996; many platforms). Ours is the frozen-court, executed-reference,
  law-gated gate-model certification.
- **The law the ratio cannot fake**: the GHZ fringe frequency must fit to **exactly k = 3**
  against a free-frequency scan (G_FREQ) — super-resolution is visible structure, not a
  normalization choice.

## Apparatus

3 qubits on a calibration-gated heavy-hex **star** (center = degree-≥2 node; cost = 2 CZ
errors + 3 readouts). GHZ arm: H·CX·CX | Rz(φ)⊗3 | CX·CX·H, measure center → 4 CX per point.
SEP arm: (H | Rz(φ) | H)⊗3, measure all three — **zero 2q gates**. 12 uniform φ points over
[0, 2π), 8000 shots/point/arm = 192k + two prep sentinels (|000⟩, |111⟩) × 2000. Shuffled
(seed 4668), co-batched, one job.

**Frozen estimator**: DFT amplitude at harmonic k over the 12-point grid, V = 4|Σ(p_j−p̄)e^{−ikφ_j}|/12,
SE by exact linear propagation of binomial errors. V₁ = mean over the three separable qubits.

## Frozen gates

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_HEISENBERG** (primary) | GHZ Fisher info beats the *measured* separable Fisher info at equal resources | R = 9V₃²/3V₁² > 1 + 5·SE_R |
| **W2_SQL_ABS** | GHZ beats even PERFECT separable probes (V₁=1): 9V₃² > 3 ⇔ V₃ > 1/√3 | F_GHZ > 3 + 5·SE_F |
| **G_FREQ** | super-resolution law: free-frequency DFT scan peaks at k = 3 | amp(k=3) > 2× max amp(k≠3) |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

**Figures of merit**: the Fisher ratio R with σ-clearance over 1; V₃ with distance above the
1/√3 = 0.5774 threshold. **Fake preview**: V₃ = 0.9793, V₁ = 0.9852, F_GHZ = 8.63,
F_sep = 2.91, **R = 2.96 ± 0.01** (theory max 3.00). Noiseless law check PASS (V₃ = 1.0000,
R = 2.997, peak k=3).

**Pre-filed predictions**: W1 HIT conf 0.93; W2 HIT conf 0.90 (real GHZ visibility at 4 CX
historically lands 0.90–0.96, comfortably above 0.577; fake is likely optimistic per the
Exp126/128 crossover note — expect V₃ ≈ 0.92–0.96, R ≈ 2.5–2.9); G_FREQ conf 0.95; G_SENT 0.95.

**NO-TEST conditions**: sentinel failure → window NO-TEST; any SEP-arm pub with 2q gates or
GHZ-arm pub ≠ 4 CX (audited pre-submit) → abort; G_FREQ failure with W1 passing → apparatus
audit before any claim (a ratio without super-resolution is a grading artifact).

## Relation to the campaign

Third advantage genre in three cycles. F81 saturated the quantum Cramér–Rao bound for
*amplitude* estimation; this certifies the *entanglement-enhanced* Fisher advantage for phase.
Natural follow-up (not frozen here): N-ladder (N = 2,3,4,5) for the scaling exponent — the
actual Heisenberg-scaling certification, one job per N with the same court.
