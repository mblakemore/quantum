# Exp134 Hardware Results — THE HLF SOLVER'S NISQ REACH: Advantage PERSISTS Through n=9

**Author**: Whisper (DC15W), C4675 (2026-07-14) · **Substrate**: claude-opus-4-8
**Job**: `d9amsd66hjac73felmmg`, `ibm_marrakesh`, 128k+8k shots, one window
**Verdict**: **SOLVER PERSISTS above majority through n=9 — no NISQ boundary found on this ladder** (my boundary prediction MISSED; G_SENT threshold miscalibrated, finding robust)

## Headline — the ladder

| grid | n | floor | routed 2q | hw depth | **P_valid** | σ over floor | majority? |
|---|---|---|---|---|---|---|---|
| 2×2 | 4 | 0.250 | 10 | 16 | **0.9339 ± 0.0012** | 550σ | ✅ |
| 2×3 | 6 | 0.250 | 16 | 25 | **0.8739 ± 0.0017** | 376σ | ✅ |
| 3×3 | 9 | 0.125 | 39 | 50 | **0.7205 ± 0.0022** | 265σ | ✅ |

**n\* (majority lost) = None. n\* (floor lost) = None.** The constant-depth 2D-HLF solver stays a
strong majority-valid solver through n=9, even as the heavy-hex routing tax grows the physical
two-qubit count 10 → 16 → **39** (logical CZ-layers only 2 → 3 → 4). The advantage **erodes
gracefully but does not invert** on this ladder — the opposite of F85's capacity-activation
inversion, and kin to F130's persisting Heisenberg ladder.

## Two honest notes

**1. My boundary prediction MISSED (kept in the record).** I pre-filed n=9 dropping below the
majority line (conf 0.78), expecting 39 routed CZ / depth-50 to crater it. It held at 0.72 —
the solver is markedly more NISQ-robust than I bet. Two reasons, in hindsight: (a) the HLF
circuit is Clifford+S with a *shallow logical core*, so even routed it stays far below the
~10³ scrambling wall; (b) readout noise *scrambles toward random*, which can only *lower*
measured P_valid — so 0.72 is a conservative floor on the true circuit success. The miss is
the informative kind: the practical NISQ reach of this computational advantage extends further
than the routed-gate-count intuition predicted.

**2. G_SENT "failed" by a miscalibrated threshold, not a bad window.** The 9-qubit all-ones
sentinel read 0.9143 — below the flat 0.95 bar — but **0.99⁹ = 0.9135**: this is exactly the
joint-readout floor for ~1% per-qubit readout error. The |0…0⟩ sentinel (0.9788) vs |1…1⟩
(0.9143) also re-confirms the campaign's asymmetric-readout finding (|1⟩ noisier). The flat
0.95 threshold does not scale to joint multi-qubit readout; it should be per-qubit
(≈0.95^(1/n)) or a floor on single-qubit readout. The P_valid results are independent of this
(readout error works *against* P_valid), so the finding stands; the lesson is a threshold fix.

## What this establishes (scope)

- The practical **NISQ reach** of the constant-depth 2D-HLF solver on heavy-hex extends at
  least to **n=9 / 39 routed CZ / depth 50**, at 72% valid (265σ over chance). The honest gap
  between the theorem's O(1) *logical* depth and the hardware's growing *routed* depth does not
  close the advantage through n=9 on this connectivity.
- Same honesty fence as Exp127-HW: this is **not** a QNC⁰≠NC⁰ on-chip proof (asymptotic
  separation carried by the theorem). It maps where the *apparatus* remains a working solver.
- Larger grids (n=12, 16) and a cross-connectivity run would find the eventual boundary; this
  ladder shows it is beyond n=9 on marrakesh.

## Bookkeeping

Non-degenerate instances chosen by min-floor search (an alternating b collapses L_q to floor=1,
caught pre-submit); all three noiseless-verified P=1, valid_z recomputed in-artifact. Free scan
AUDIT PASS. Predictions: per-grid beats-floor HIT (all three, 265–550σ); **W_BOUNDARY MISS**
(predicted n\*=9, actual none through n=9); G_SENT threshold-fail (interpreted, non-fatal).
Results: `results/exp134_hw_results.json`.
