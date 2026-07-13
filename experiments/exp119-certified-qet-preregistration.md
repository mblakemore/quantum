# Exp119 — CERTIFIED QUANTUM ENERGY TELEPORTATION: PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4639. Creator directive: "Run it!" (horizons-2 Q1,
`docs/star-trek-horizons-2-whisper-c4638.md`). Design+sim tier same cycle —
fresh-cycle freeze, sim clean on first pass. Sim: `exp119_qet_sim.py` →
`results/exp119_feasibility.json`.

## Claim under test

Hotta QET, minimal 2-qubit model (h=k=1): Alice's local measurement deposits energy
E_A at A; her ONE CLASSICAL BIT lets Bob extract energy at B, driving Bob's local
energy E_B = ⟨H_B + V⟩ BELOW the ground level (negative local energy — the
exotic-matter ingredient). Our value-add over the 2023 demonstrations: the claim runs
inside the campaign court — passivity baselines, scrambled-message controls, demon
ledger pricing the bit, frozen 5σ gates, composite-floor discipline.

## Frozen model + parameters (derived in-code, not recalled — C4558 discipline)

- H = Z_A + Z_B + 2·X_A X_B + offsets (c1 = 1/√2 each local, c2 = √2 interaction)
  chosen so every local ground expectation is 0. Ground |g⟩ = cosα|00⟩ − sinα|11⟩,
  α from direct diagonalization.
- θ\* = **0.161 rad** frozen from the sim argmin scan (closed-form cross-check agreed).
- Exact theory: E_B(qet) = **−0.11475**, E_A = +0.70711, E_B(scram) = +0.10903,
  E_B(ground) = 0.
- E_B estimator: ⟨Z_B⟩ + 2⟨X_A X_B⟩ + 3/√2 from two measurement bases;
  E_A = ⟨Z_A⟩ + 1/√2. Analytic SEs. X_A in protocol arms = Alice's recorded
  mid-circuit outcome μ.

## Frozen arms (builders byte-identical with `exp119_qet_sim.py`)

| Arm | Content | Theory E_B |
|---|---|---|
| ground | prepare \|g⟩, measure | 0 |
| qet_ff | Alice X-measures (mid-circuit), **classical feedforward** Ry(2μθ\*) on B | −0.1147 |
| qet_def | deferred/coherent control (Ry(2θ)+CRy(−4θ)) — diagnostic arm | −0.1147 |
| fixp / fixm | Alice measures, Bob rotates +θ\*/−θ\* IGNORING μ; pooled = scrambled-message control | +0.109 |
| cal0 / cal1 | readout assignment calibration (\|00⟩, \|11⟩) | — |

2 bases per protocol arm (zb, xx) → **12 pubs**; 30k shots protocol / 20k calib =
**340k shots, one job, ibm_marrakesh**. Pair = frozen min-2q-error rule
(`run_exp105_causal_game_submit.pick_pair`). Transpile seed 4639, opt level 1.
Pub order shuffled, seed 4639.

**Transpile audit (go/no-go)**: 2q count per pub — ground/qet_ff/fixp/fixm = 1,
qet_def = 3, calib = 0; all 2q on the selected edge; feedforward branch survives
in qet_ff ISA.

## Frozen gates (existence headline; magnitudes as subclaims — F93/F95 discipline)

SE_diff = √(SE₁² + SE₂²); sim-at-budget SEs: single-arm ≈ 0.008-0.010, diff ≈ 0.012.

- **G0 apparatus integrity (NO-TEST guard, one-sided)**: noise can only bias E_B
  POSITIVE (constants don't attenuate). If E_B(ground) + 5·SE < 0 → apparatus broken
  → **NO-TEST**.
- **W1a (headline)**: E_B(qet_ff) − E_B(ground) < 0 at 5σ. Sim preview −0.129 (fake).
- **W1b (headline)**: E_B(qet_ff) − E_B(scram_pooled) < 0 at 5σ. Preview −0.222.
  W1a ∧ W1b = **ENERGY TELEPORTED**: extraction activated only by the message.
- **W2 (subclaim, raw)**: E_B(qet_ff) + 5·SE < 0 — absolute negative local energy,
  uncorrected. Fake preview −0.064 ± 0.008 (passes with 1.7× margin; real readout
  may be worse — this is the at-risk leg and is FILED as the magnitude subclaim).
- **W2c (subclaim, readout-corrected)**: same gate after the frozen correction:
  per-qubit assignment (F0,F1) from cal0/cal1; ⟨Z⟩_corr = (⟨Z⟩−(F0−F1))/(F0+F1−1);
  ⟨XX⟩_corr = ⟨XX⟩raw/(vA·vB), v = F0+F1−1. X-basis reuses Z-assignment (1q-H error
  ~2 orders below readout, neglected — stated). F95 friction-02 proven practice:
  measure the nuisance, then correct.
- **D1 (diagnostic, not gated)**: E_B(qet_def) − E_B(qet_ff) — feedforward vs
  coherent-control cost. Sim says def is NOISIER (extra 2q from CRy) — pre-filed.
- **Demon ledger (reported)**: E_A deposit, extraction |E_B|, efficiency |E_B|/E_A
  (theory 0.162), 1 classical bit/run Landauer-priced — the QET message IS a demon
  record; books printed by the grader.

## Predictions (registered at freeze)

- **P1** W1a ∧ W1b (energy teleported, existence): **0.75**.
- **P2** W2 raw absolute negativity: **0.50** (fake passes 1.7×; hardware readout risk).
- **P2c** W2c corrected negativity: **0.65**.
- **P3** NO-TEST (G0 or audit): **0.05**.

## What would make this wrong (stated at freeze)

Readout bias is common-mode across arms — differentials (W1a/W1b) are
attenuation-robust (F89 matched-haircut lesson); absolute W2 is not, which is exactly
why it is a subclaim. If feedforward latency decoheres B before the conditional
rotation fires, qet_ff degrades toward the fixp/fixm arms — that failure mode is
DETECTABLE as W1b shrinking while qet_def stays deep (the D1 comparison isolates it).
Gate lint: `experiments/exp119_gate_lint_spec.json` → `results/exp119_gate_lint.txt`
(all gates must be OK: can-pass AND can-fail at budget).
