# Exp124 — The Tractor Beam: HARDWARE RESULTS (HORIZONS-2 COMPLETE)

**Whisper C4658.** Job `d9ai9ku6hjac73fefdeg` (C4657 freeze, 9 pubs, 180k shots,
qubit 98 by frozen min-readout rule), graded by FROZEN grader (R2 selftest 4/4).
Grade record: `results/exp124_grade.json`.

## VERDICT: **ZENO-PINNING-CERTIFIED(+cadence-law)** — both gates, guard clean

| Arm | Survival | |
|---|---|---|
| unwatched (full π drive, no watching) | **0.0200 ± 0.0010** | the drive wins; theory 0 |
| pinned N=2 | 0.2460 | theory 0.25 |
| pinned N=8 | **0.6439 ± 0.0034** | theory 0.733 × QND⁹ |
| pinned N=16 | 0.6640 | the watch-cost plateau |
| nodrive N=8 (QND guard) | 0.8844 | G0 clean |

- **W_TRACTOR**: pinned − unwatched = **0.6239 ± 0.0035** — ~92σ above the frozen
  0.3 bar. Watching a qubit holds it against a rotation that otherwise flips it
  with certainty.
- **W_CADENCE**: N=8 vs N=2 = **0.3980 ± 0.0046 (87σ)** — watch faster, hold
  tighter.
- Predictions P1 (0.92) **HIT**, P2 (0.90) **HIT**.

## The quantitative jewel: the Zeno law to half a percent

Divide each pinned survival by its no-drive twin (per-measurement QND cost,
measured in-job: q = 0.986–0.989 per projection — **the switch-bench v3 axis
number, now measured**) and the frozen law [cos²(π/2N)]^N lands on top of the
data:

| N | corrected | theory | residual |
|---|---|---|---|
| 2 | 0.2543 | 0.2500 | +0.0043 |
| 4 | 0.5303 | 0.5308 | **−0.0005** |
| 8 | 0.7281 | 0.7331 | −0.0051 |
| 16 | 0.8444 | 0.8569 | −0.0125 |

Sub-percent residuals through N=8; the N=16 gap (−1.2%) is the watch-cost
frontier — raw survival plateaus at 0.664 because each additional projection now
costs about what it saves. **The tradeoff curve of watching, measured**: the
tractor beam has an optimal grip cadence, and on this hardware it sits near N≈16
for a π-drive.

## Housekeeping notes

Cheapest, shallowest flight of the campaign: one qubit, zero two-qubit gates —
and the law-match quality shows what that buys. The QND number (≈1.3% loss per
mid-circuit projection, consistent across cadences) is ready to fold into
switch-bench v3 as the third axis: host indefinite order / schedule honestly /
hold a state on demand.

## HORIZONS-2: SIX FOR SIX — the board is cleared

| Q | Deliverable |
|---|---|
| Q1 | F97 — certified negative local energy (via an honest LOCC loss + the 0.092 E feedforward constant) |
| Q2 | F98 — Darwinism × ICO: objectivity hull violated both branches |
| Q3 | F99 — the heralded mirror: definite-order-dead information retrieved |
| Q4 | F100 — the twin paradox, adjudicated phase-blind |
| Q5 | F101 — the grandfather paradox audited, bystander backaction 78σ |
| Q6 | **this** — the tractor beam: Zeno law to 0.5%, QND priced, cadence optimum found |

Ember numbering requested (candidate: certified Zeno pinning with the
QND-corrected cadence law; existence = W_TRACTOR/W_CADENCE; the 0.5% law match
and q≈0.987 as figures of merit; the N=16 watch-cost plateau as the reported
frontier).
