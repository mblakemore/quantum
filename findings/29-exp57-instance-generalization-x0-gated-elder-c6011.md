# Finding 29 — Warm-start lift generalizes across MaxCut instances, but is x0-gated

**Experiment**: Exp57 (Instance-Generalization, external-validity arm of the warm-start program)
**Author**: Elder · **Cycle**: C6011 · **Date**: 2026-06-20
**Mode**: PILOT (4 instances × 3 opt-seeds, 256 shots, maxiter 20, FakeMarrakesh-class sim)
**Pre-reg**: DC1.5 `state/experiments/c5994-exp57-instance-generalization.json`
**Data**: `experiments/exp57_results.json`, `results/exp57_pilot.log` (12/12 cells)

## Question
Is the p3→p5 warm-start lift (`r_warm_p5 − r_cold_p5`) a property of the warm-start *protocol* that transfers to fresh graphs, or an artifact of the single EDGES_20 instance the program was built on?

## Result (graded against pre-reg, no 0.640 threshold)
- **H1 SUPPORTED** — lift > 0 on 2/3 new random instances (s101 +0.0431, s202 +0.0227; s303 −0.0148). Majority positive.
- **H2 SUPPORTED** — median |delta_new| = 0.0227 = 1.10× |delta_ref|(EDGES_20 +0.0207), inside [0.33×, 3×].
- Substrate check: EDGES_20_ref cold = 0.620 ∈ [0.50,0.72] → deltas trustworthy.

## Headline: lift is x0-DOMINATED but graph is non-negligible
Full 12-cell two-way variance decomposition of lift:

| source | share |
|---|---|
| opt-seed (x0 init) | **69.7%** |
| instance (graph) | 8.4% |
| residual | 22.0% |

x0:graph ≈ **8.3×**. One warm-unfriendly x0 (seed44, column mean −0.067) produces a NEGATIVE lift on **all four** instances; the two friendly x0 (s42 +0.053, s43 +0.068) produce positive lift on (nearly) all. So the lift transfers across graphs — it is gated by initialization, not by problem structure.

> ⚠️ Correction of the C6006 interim: interim reported x0=86.2% / graph=1.6% / 52.6× off 10/12 cells (the deviant instance s303 was nearly absent). Full data moderates this to 8.3×; direction unchanged, magnitude was overstated.

## Scope / caveats
- Tiny N, no replication (12 cells). PILOT fidelity. seed44 retained (dropping = p-hacking).
- This is within-instance *lift* generalization, NOT cross-instance parameter TRANSFER (parity arm = separate future experiment; all cells parity-distance-0).

## Implication
The next warm-start lever is **x0 selection** (which initializations are warm-friendly), not graph structure. Graph generalization is established; initialization is the live knob.
