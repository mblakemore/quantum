# Exp59 — x0-Selection: does the opt-seed gate warm-start LIFT via p3-anchor quality or cold-luck?

**Author**: Elder · **Cycle**: C6017 · **Date**: 2026-06-20
**Program**: warm-start (Exp48–57, Findings 23–29)
**Runner**: `scripts/run_exp59_x0_selection.py`
**Pre-reg mirror**: DC1.5 `state/experiments/c6017-exp59-x0-selection.json`

## The gap
Finding 29 (Exp57, C6011) established warm-start lift is **x0-gated** — opt-seed explains
~69.7% of lift variance vs graph 8.4% (≈8.3×). One "warm-unfriendly" seed (44) gave NEGATIVE
lift on all four instances. But `lift = r_warm_p5 − r_cold_p5` **conflates two mechanisms**:

- **(A) warm-anchor path** — the seed's p3 optimization lands a bad anchor (low `r_p3_base`);
  the padded p5 warm-start inherits a poor floor → low `r_warm`.
- **(B) cold-luck path** — the seed's cold-p5 x0 happens to land an unusually GOOD cold
  baseline → lift is negative even though warm is fine.

C6011 (3 seeds, lift only) could not separate them. Exp59 varies x0 across **N=12 seeds on the
fixed reference instance EDGES_20** (graph held constant — justified by C6011's 8.4% graph share)
and **decomposes the gating path**, then asks whether any cheap a-priori x0 statistic predicts
anchor quality.

## Why it matters (unifies three threads)
- **C6011** — x0 gates lift (the WHAT).
- **C5980** — p5 escape is INHERITED from the p3 anchor (monotone floor) — the candidate WHY.
- **Whisper P-C4208-a** — p3-anchor quality = the joint lever.

If path (A) dominates, "x0 selection" reduces to "**p3-anchor selection**", and the actionable
rule is **best-of-k p3 multi-start** (p3 is cheaper than p5) before the single p5 warm-start.

## Design
- Instance = EDGES_20 (every prior escape/warm-start finding lives here).
- Per opt-seed (`np.random.seed(seed)` reproduces both x0 draws, matching Exp54/57):
  - `cold_p5`: COBYLA p=5 from random x0_cold (len 10) → `r_cold`
  - `p3_base`: COBYLA p=3 from random x0_p3 (len 6) → `r_p3`, best params x3
  - `warm_p5`: pad x3 to p5 (zeros = identity) → COBYLA → `r_warm`
- `lift = r_warm − r_cold`. Record x0 vectors + cheap a-priori stats (mean/std/min/max/|x−π|mean).
- Fidelity = Exp57 EDGES_20 pilot cells (256 shots, maxiter 20, FakeMarrakesh) so seeds 42/43/44
  cross-check the pilot's EDGES_20_ref column.

## Hypotheses (named observables — graded against these, no post-hoc threshold)
- **H1 (MEDIATION, PRIMARY)**: warm-anchor drives lift.
  `Spearman ρ(r_p3_base, r_warm_p5) > 0` **AND** `ρ(r_p3_base, lift) > +0.30`.
  REFUTE if `ρ(r_p3_base, lift) ≤ 0` (lift gating is NOT via anchor quality).
- **H2 (PATH DOMINANCE)**: classify the dominant path by **variance share** —
  `Var(r_warm)` vs `Var(r_cold)` (lift = warm − cold; warm-anchor dominant iff
  `Var(r_warm) ≥ Var(r_cold)`). Report `Var(lift)=Var(r_warm)+Var(r_cold)−2Cov` and the shares.
  `|ρ(·,lift)|` is a SECONDARY diagnostic only — NOT the classifier, because both r_warm and
  r_cold mechanically correlate with their own difference (smoke-test C6017 confirmed |corr|
  mis-classifies). **Pre-disclosed direction: warm-anchor.**
- **H3 (A-PRIORI x0 STAT)**: does any cheap stat of x0_p3 (mean / std / |x−π|mean) predict
  `r_p3_base` at `|ρ| > 0.30`? **Pre-disclosed prior: NULL** (COBYLA from any uniform x0 in a
  multi-modal landscape reaches varied local optima with no simple a-priori map). A NULL here is
  the **informative** result — it means x0-selection must be empirical best-of-k p3 multi-start,
  not an a-priori filter.

## Scope / honesty
- PILOT fidelity (256 sh / maxiter 20). Establishes SIGN + rough magnitude of mediation, not a
  definitive campaign. N=12 is a real distribution (vs C6011's 3) but still small; Spearman on
  N=12 reported with caveat, no p-value fishing.
- Single instance BY DESIGN (isolates the dominant knob); cross-instance is C6011-settled (graph
  8.4%). Mediation-generalization across instances = separate future arm.
- Seeds retained as drawn; no dropping inconvenient seeds (C5923 flattering-result discipline —
  Exp57 retained seed44).

## Grading
Read `experiments/exp59_results.json` `summary` block; grade H1/H2/H3 against the named
observables above; write Finding 30. Est completion ~13h background (12 cells × ~65 min,
reniced to yield to the in-flight Exp54 ArmA run that C5980 grades off).
