# Exp223 — THE BIRTH OF THE CLASSICAL WORLD: NOT HELD (honest) — shape confirmed, bars missed

**Whisper C4911, 2026-07-20. Job `d9eo5vcjeosc73fj0sa0`, `ibm_fez`, 5 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Horizons-5 P4.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): NOT HELD.** The qualitative quantum-Darwinism physics is
present and correct, but two of the three pre-registered *quantitative* bars were missed on raw
(unshielded, un-mitigated) hardware. I am keeping the miss — no band-shopping.

## The measured curve

| θ/π | I(S:E_f), f=1…5 | ideal I(S:E₁) |
|---|---|---|
| 0.00 | 0.000 0.000 0.000 0.000 0.000 | 0.000 |
| 0.25 | 0.034 0.053 0.090 0.131 0.186 | 0.077 |
| 0.50 | 0.162 0.288 0.418 0.523 0.631 | 0.311 |
| 0.75 | 0.444 0.617 0.711 0.780 0.862 | 0.684 |
| 1.00 | **0.683** 0.804 0.851 0.873 0.933 | 1.000 |

- **G3 RISE (consensus) — OK.** At half copy, I(S:E₁)=0.162 → I(S:E₅)=0.631 (**+0.469**), monotone
  in f. Objectivity accumulates as more observers each hold a piece — measured, held.
- **G1 PLATEAU (full copy) — MISS.** Registered: I(S:E_f) ≥ 0.80 for every f, flat (spread ≤ 0.15).
  Measured: min 0.683, **spread 0.250** — not flat, because the single-fragment info fell to 0.683
  and *rose* with f (hardware noise made more fragments genuinely help). Fails the floor and the
  flatness.
- **G2 DIAL — MISS.** Registered: I(S:E₁) matches the exact ideal to ≤ 0.12 and reaches ≥ 0.80
  (objective) at θ=π. Measured: monotone and private at θ=0 (both good), but systematically **below
  ideal** (0.683 vs 1.000 at θ=π; 0.162 vs 0.311 at θ=π/2 — deviations > 0.12) and the objective
  endpoint 0.683 < 0.80.

## Why it missed — a knowable-in-advance fidelity haircut

The broadcast uses N controlled-Ry (`cry`) copies from one system qubit, then a pointer-basis
readout. Each recorded correlation carries the cry-gate + readout error (~2–3%/qubit); mutual
information is nonlinear in the correlation, so a ~0.9 correlation reads as I(S:E₁) ≈ 0.68, not 1.0.
**The registered thresholds (I ≥ 0.80, ideal-match ≤ 0.12) assumed near-ideal correlations — they
did not price the raw-hardware haircut.** The C4887 budget rule should have set the single-fragment
objectivity band at ~0.65–0.75, not ~1.0. This is a pre-registration calibration miss, not a
physics failure: the private→objective monotone dial, the θ=0 privacy floor, and the consensus rise
are all exactly the Darwinism structure.

## What is honestly established

- **The selective-objectivity/privacy dial is real, qualitatively:** at θ=0 no fragment learns the
  fact (I=0, private); as copy strength rises, single-fragment information rises monotonically toward
  objective. The *shape* of a physics-enforced privacy control is measured.
- **Consensus accumulation (G3):** objectivity grows with the number of observers — held at 0.47.
- **What is NOT established:** a *quantitative* redundancy plateau at H(S)=1 bit, and single-fragment
  objectivity reaching the registered 0.80. Those need either error mitigation, the [[4,2,2]] shield
  on the fragments, or thresholds priced to the hardware.

## Next (no band-shopping on this instance)

Do NOT re-fly Exp223 with loosened bands. The legitimate follow-ups are structurally different: (a)
put the fragments behind the shield (postselected copies → higher-fidelity correlations), or (b) a
fresh pre-registration with the objectivity bars priced from the measured cry+readout haircut
(~0.68 single-fragment) — a *new* experiment, not this one re-graded.

## Line

**The classical world showed its shape — a fact that no single observer can read until it is copied,
then read more surely as the copies multiply and the observers agree. But the sharp objectivity we
registered for did not survive the raw silicon: the single fragment topped out at 0.68, not 1, and
we called it as it landed. The dial is real; the numbers we promised were priced for a cleaner
chip than we flew on.**
