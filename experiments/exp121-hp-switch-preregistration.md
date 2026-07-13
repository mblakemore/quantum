# Exp121 — HAYDEN-PRESKILL × SWITCH, THE HERALDED MIRROR: PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4647. Creator: "run it." Fresh-cycle freeze
(design+sim C4646 per no-tired-freeze). Design: `exp121-hp-switch-design.md`.
Sim: `exp121_hp_switch_sim.py` → `results/exp121_feasibility.json`.

## Claim under test

A diary (one bit, encoded in the probe's X basis) is thrown to two incompatible
horizon-queries (Z-query into E1, X-query into E2 — the F98 recorder blocks,
byte-identical). **Premise (measured, not assumed)**: in EVERY definite query order
the diary is dead in the probe alone (theory S_P = 0 exactly). **Claim**: the
heralded switch minus-branch retrieves it from the probe alone (theory S_P = −1/2
EXACTLY — perfect anti-correlation; flip the bit and read the whole diary), and the
plus branch retrieves partially (theory +1/6). Scope: retrieval economics for THESE
two queries, one use each, probe-alone readout; one backend/window.

## Frozen apparatus

Builders byte-identical to `exp121_hp_switch_sim.py::build` (which reuses the F98
4-slot CCZ skeleton verbatim — hardware-certified 22σ/52σ at C4645). Arms
ordZX / ordXZ / switch / null(C=|0⟩) × diaries |+⟩/|−⟩ = **8 pubs × 30,000 shots
= 240k, one job, ibm_marrakesh**. Site: frozen star rule REUSED
(`run_exp120_submit.select_star` — S-hub degree-3 junction, deterministic). Layout
[C,P,E1,E2]. Transpile seed 4647, opt 1, shuffle seed 4647. **Audit**: all 2q inside
the site; skeleton pubs share one 2q count; definite pubs share one count.

## Frozen statistics

S_P = P(probe X-outcome = diary) − 1/2 pooled over both diaries (balanced);
S_E2 likewise from E2's record. Binomial SEs. Herald branches from c0 (switch arm).

## Frozen gates

- **PREMISE_DEAD (NO-TEST guard, F83 pattern)**: |S_P(ordZX)| < 0.05 AND
  |S_P(ordXZ)| < 0.05 (frozen constant, ~an order of magnitude under the fake minus
  signal 0.349; fake definite arms read 0.002/−0.006). The channel must be MEASURED
  dead in definite order or retrieval is untestable → NO-TEST.
- **N1 (NO-TEST guard, classification)**: null arm reads ZX-like:
  |S_P(null)| < 0.05 AND S_E2(null) < 0.25 (ordXZ would read 0.5).
- **H1 (NO-TEST guard)**: herald minus-rate ∈ [0.10, 0.40] (theory 0.25).
- **W_MIRROR (HEADLINE, sign theory-fixed)**: S_P(minus) + 5·SE < −0.05 →
  **HERALDED MIRROR CERTIFIED** — the probe alone returns diary information beyond
  the definite-order premise band, anti-correlated as theory demands. (Fake preview:
  −0.349 + 5×0.0039 = −0.330; margin ~6×.) A POSITIVE excursion does NOT pass — the
  sign is part of the claim.
- **W_PLUS (secondary, sign fixed)**: S_P(plus) − 5·SE > +0.05 (theory +1/6; fake
  +0.142, margin ~1.8×).
- **Subclaims (reported, not gated — composite-floor)**: mirror depth vs −1/2;
  plus depth vs +1/6; the horizon-keeps-it asymmetry S_E2(ordZX) ≈ 0 vs
  S_E2(ordXZ) ≈ 0.5 (query order controls what the environment learns — free bonus
  measurement); branch rates vs 3/4, 1/4.

## Predictions (registered at freeze)

- **P1** W_MIRROR: **0.85** (fake margin ~90σ; apparatus hardware-validated at C4645;
  residual risk = premise-band inflation from readout bias on agreement estimators).
- **P2** W_PLUS: **0.80** (smaller margin, 1.8× over the band).
- **P3** NO-TEST: **0.07**.

Lint: `experiments/exp121_gate_lint_spec.json` → `results/exp121_gate_lint.txt`.
Grader `scripts/grade_exp121.py` FROZEN with this prereg; estimators imported from
the sim module.
