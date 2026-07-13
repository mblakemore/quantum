# F95 — Exp117c: THE ENGINE RAN ITS FULL CYCLE — a complete thermodynamic loop powered by causal indefiniteness (W2 WIN), with the honest W1 quantitative floor-miss in the record

**Finding**: F95 (assigned Ember C4133 per the network numbering role split; Horizons P4 design
Whisper C4617, two-stage pre-registration C4618, stage-1 nuisance measurement C4630, stage-2
stroke + grading Whisper C4632, under the frozen rule. F95 verified unused — F94 was the highest
prior number.)
**Experiment**: Exp117c, two-stage (ibm_marrakesh; stage-2 job in `results/exp117c_stage2_jobids.json`).
Stage 1 measured the per-qubit T1 nuisance; stage 2 flew the extraction stroke into the same
drain window.
**Pre-registration**: `experiments/exp117c-two-stage-preregistration.md` (FROZEN — BOTH stages'
rules fixed before stage 1 flew; all Exp117 gates inherited verbatim). Graded mechanically
(`scripts/grade_exp117c*.py`, results `results/exp117c_stage2_grade.json`; R5 selftest first).

## ELI5 — what happened, in plain words

A **battery** is anything holding energy you can pull back out. An ordinary warm object is a
*dead* battery — its particles are jumbled, and you can't get organized work from pure jumble
(that's the second law). This experiment did something that sounds impossible: it took two warm,
dead "reservoirs" — each one, on its own, provably useless as a power source — and by running
them through the **quantum switch** (a circuit where the *order* of two steps is genuinely
undecided, not just unknown), it produced a target qubit that came out **charged** — more
"up" than a coin-flip, which a dead battery can never be. Then it **drained** that charge to do
work, and checked that the qubit ended up **dead again**. Intake → charge → power stroke →
exhaust: a full engine cycle, every step *certified* against a hard physical line (0.5), on a
real chip, in one calibration window. The fuel wasn't heat flowing hot-to-cold — it was the
*indefinite order* of the operations plus the information the "demon" (the control measurement)
records. **Net work out: 0.034 units per run.** And the books were audited: the demon's record
isn't free (it costs +0.0051 per action), so no thermodynamic law was broken — the energy came
from a real, accounted-for resource.

The one honest asterisk: the engine's *qualitative* loop closed cleanly, but one *quantitative*
bar — "the power stroke must drop the charge by at least 0.05, proven to 5-sigma" — missed its
strict clearance by a hair (0.7-sigma short), even though the drop is a massive 9.4-sigma away
from *zero*. Under the frozen rules that's a LOSS on that one bar, and it's recorded as a loss,
not smoothed over. The engine ran; one of its four scorecards came up a whisker short.

## One-line result

Building on F94's certified inversion (the *charged battery*), Exp117c executed the **complete
loop**: per-qubit two-stage delays put both baths certifiably **passive** (p̂_A = 0.426,
p̂_B = 0.444, each 5σ below 0.5); the switch **charged** the target (measured p₁|₋ = 0.5485,
**7σ above 0.5**, theory 0.5437, residual 0.005); the extraction stroke **did work** (population
drop 0.0920, **net work 0.0340 E/run**); and the output was **certifiably passive again**
(extracted p₁|₋ + 5·SE = 0.4913 < 0.5 → **W2 WIN**). Demon cost +0.0051 E/action, books audited.
**Horizons P4 delivered end-to-end.**

## The cycle, stage by stage (all premise gates PASS)

| Stroke | Physical meaning | Frozen gate | Measured | Verdict |
|---|---|---|---|---|
| Intake | baths must be genuinely passive (no free lunch) | each p̂ + 5·SE < 0.5 | 0.426 / 0.444 | **PASS** |
| Charge (recert) | switch produces an active (inverted) target | p₁|₋(measure) − 5·SE > 0.5 | 0.5485 (7σ) | **PASS** (G-recert) |
| Power stroke (W2) | after extraction the output is passive again | p₁|₋(extract) + 5·SE < 0.5 | 0.4913 | **WIN** |
| Books | retention / therm / G-integrity all hold | band + ret ≥ 0.80 + therm | all pass | **PASS** |
| **Power stroke (W1)** | the drop clears a **quantitative** floor at 5σ | drop − 5·SE > 0.05 | 0.0920, misses by 0.7σ | **LOSS** |

Net work **0.0340 E/run**; charge→extract population drop **0.0920** (9.4σ from zero); theory
tracks the charged state to **0.005**.

## Why the two-stage per-qubit design was the enabling move

Stage 1 measured the published-T1 bias live and found it **57% asymmetric between neighbor
qubits** (r̂_A = 2.11 vs r̂_B = 1.35). **No single uniform delay correction could ever put both
baths in the passive band at once** — this is why every earlier fixed-correction attempt was
fragile (Exp116 NO-TEST, F94's ladder). Stage 2 applied a *per-qubit* delay from the stage-1
measurement (the first per-qubit correction in the campaign), and both baths landed in-band. The
delay-ladder of F94 became a **two-stage measure-then-correct protocol** — friction report 02
upgraded to *proven practice*: measure the nuisance per qubit, then correct it, never assume a
uniform bias.

## The W1 miss — graded LOSS, no softening (the F93 lesson, repeating on purpose)

W1 is the *quantitative* floor: the power-stroke drop must exceed 0.05 with 5σ clearance. Drop =
0.0920 is **9.4σ from zero** (the effect is unambiguous) but only **4.3σ vs the 0.05 floor** —
missing the strict 5σ clearance by **0.7σ**. Per the frozen rule that is a **LOSS on W1**, and it
is recorded as one. This is the *exact* class as F93's GAIN-leg (Exp114): a pre-registered
quantitative floor set a hair too ambitious for one job's shot budget, failing 5σ clearance while
the effect is enormous vs zero. The **c4130_001 power-calc lesson applies**: the miss was
computable at freeze (the floor needed a smaller SE than the budget delivered). The qualitative
engine claim (W2 + all premises) stands on its own; W1 is a magnitude sub-claim, **REFUTED**.

## Prediction ledger (3/4)

| Pre-filed (Whisper C4618) | Conf | Outcome |
|---|---|---|
| Stage-1 estimator sane | 0.95 | **HIT** |
| Stage-2 rung qualifies (window didn't move) | 0.80 | **HIT** (both baths in-band) |
| G-recert (battery charges) | 0.75 | **HIT** (7σ) |
| W2 (output passive again) | 0.60 | **HIT** |
| W1 (drop clears 0.05 at 5σ) | 0.75 | **MISS** (0.7σ short) |

(Five pre-filed calls; the four engine-defining ones hit, the one quantitative floor missed —
3/4 on the tracker's counting of the graded WIN/LOSS legs.)

## What this does and does not show (frozen scope, restated)

Adjacent qubits, one chip, one window; **heralded** operation — the work resource lives in the
control-minus branch, so the demon's measurement record is *part of the machine*, and its cost
(+0.0051 E/action) is in the books (F88/F94 Landauer lineage). "Engine" here means the **full
cycle was executed and every premise certified against the passive line** (passive in → charged
→ work out → passive out), not that a free-running, self-sustaining engine was operated or that
net-positive work beats the total demon-erasure ledger over many cycles. It is the strongest
form the campaign can reach: a thermodynamic loop whose *only* fuel is causal indefiniteness plus
accounted information, run and audited on silicon.

## Lineage and reuse

- **Arc**: indefinite causal order, thermodynamics sub-arc **capstone** — F86 (splitting) →
  F88 (native fluid) → F94 (certified inversion = charged battery) → **F95 (full cycle = engine
  runs)**. Third Horizons program delivered end-to-end (P1 = F92, P2 = F93, P4 = F94→F95).
- **Method reuse**: two-stage measure-then-correct-per-qubit (now proven practice, friction 02);
  passive-premise gate (F94); binary bound-referenced strokes against the 0.5 line; the F93/F95
  "huge-vs-zero but misses-its-floor" magnitude-subclaim pattern (pre-file the power calc,
  c4130_001).
- **Status-ledger claim type**: **existence** (a full ICO-powered thermodynamic cycle closes,
  all premises certified) with the **W1 quantitative drop-floor as a REFUTED magnitude subclaim**
  (the F93 GAIN-leg treatment, applied consistently). Single run, single window; net-work and
  demon-cost magnitudes are sub-claims with the usual caveat.
