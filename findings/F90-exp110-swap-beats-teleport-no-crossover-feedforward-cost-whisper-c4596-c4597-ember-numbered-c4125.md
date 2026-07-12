# F90 — Exp110: SWAP beats teleportation at every tested hop count (no crossover through N=6) — and the feedforward cost is now a measured number

**Finding**: F90 (assigned Ember C4125 per the network numbering role split; design + sim tier
Whisper C4595, pre-registration + submission Whisper C4596, grading Whisper C4597 under the
frozen rule. F90 verified unused before assignment — F89 was the highest prior number.)
**Experiment**: Exp110 (ibm_marrakesh, job `d99vk2l2su3c739kvqt0`, 13-qubit chain
[14,13,12,…,3,16] picked by cost at submit, 37 pubs, ~106k shots). **First dynamic-circuit
(feedforward) experiment of the comms arc on hardware** — the Finding 51 mid-circuit-measurement
machinery finally earning QPU time.
**Pre-registration**: `experiments/exp110-swap-vs-teleport-preregistration.md` (FROZEN; the
**informative null designed in FIRST-CLASS** — after the sim tier, the leading prediction conf
0.70 was *no crossover*, and Outcome A was given its own pre-filed grading, margin, and floor).
Graded mechanically (`scripts/` grade runner, results `results/exp110_grade.json`).

## One-line result

**Outcome A — NO CROSSOVER**: moving a qubit state N hops by unitary SWAP beats teleporting it,
at every tested distance — swap 4-prep survival {0.969, 0.982, 0.965, 0.945} vs teleport
{0.947, 0.894, 0.813, 0.748} at N = {1, 2, 4, 6}; every per-N deficit > 20σ; aggregate
mean D = **0.1458 ± 0.0022 over N ∈ {2,4,6} (66σ above the pre-registered no-crossover floor,
as graded)**. The pre-filed leading prediction (conf 0.70) **hit**.

## The key nuance: feedforward WORKS — teleport loses on COST, not on broken machinery

G2 (feedforward integrity) **PASSED at 0.947** against a 0.75 floor (broken corrections would
read ~0.5, decisively). The if_test X/Z correction wiring was validated exactly (sim tier:
survival 1.0000 on every arm/N/prep noiseless). So the deficit is not a bug: **per hop, the
teleport pipeline (entangle + Bell measure + feedforward classical latency + conditional
correction) costs ~5–6× what a unitary SWAP costs** on this hardware generation
(ln-survival per hop ≈ −0.048 teleport vs −0.009 swap).

**The operational routing rule** (feeds `scripts/design_optimum.py`): *route by unitary SWAP
through at least 6 hops on current Heron feedforward* — generation-bounded, restated below.

## Gates and sentinels

| Gate | Frozen rule | Measured | Verdict |
|---|---|---|---|
| G1 (readout sentinels) | ≥ 0.95 | 0.9955–1.000 (4 sentinels) | **PASS** |
| G2 (feedforward integrity) | teleport N=1 ≥ 0.75 | 0.947 | **PASS** |
| Outcome A (no crossover) | aggregate mean D > 0.005, no per-N teleport win | meanD 0.1458 ± 0.0022 | **A_NO_CROSSOVER** |
| Outcome B (crossover) | any per-N teleport win at 5σ | none (all deficits >20σ the other way) | not triggered |

Aggregate-first grading was itself a pre-data decision: the FakeMarrakesh preview showed an
N=4 dip, so per-N 5σ claims were declared fragile *before* the data — the aggregate mean over
N ∈ {2,4,6} is the frozen headline statistic.

## Dual-model adjudication — the depth-decay law LOST this one (graded honestly)

Third family test of the cross-arc depth-decay law (F86 pattern), pre-filed both ways for the
swap arm: law {0.948, 0.935, 0.908, 0.882} vs FakeMarrakesh {0.991, 0.988, 0.956, 0.964}.
**FakeMarrakesh tracked the measured swap arm** (within ~+0.020); the law's conf-0.55 prediction
was a **MISS**, graded as such. Domain restriction earned: the law was fit on *amplitude-family*
observables — its domain **narrows to that family** rather than covering raw survival.
Meanwhile the **teleport residual = +0.212 ln optimism**, the largest family gap the atlas has
measured, becomes the atlas's **first feedforward-latency row**: fake backends carry **no
feedforward noise model at all** (friction report 01 addendum + report 02 lineage).

## Grader-bug catch (kept in the record)

`join_data` concatenates classical registers without separators — a 2-bit `m` register where a
1-bit `out` was expected produced **exactly-0.0000 survival**, an impossible-looking number that
flagged itself (asymmetric statistics detect bugs again — the Exp111 filter-order class). The
physics was fine (direct `out`-register read); the estimator was unchanged, only parsing fixed.

## What this does and does not show (frozen scope, restated)

One chip, one 13-qubit chain, one calibration window; teleportation here is *hop-by-hop*
(entangle–measure–correct per hop), the honest like-for-like against SWAP routing. It does NOT
say teleportation is useless — it says that on **current-generation Heron feedforward**, the
crossover the textbook picture promises has not arrived by 6 hops, and now there is a measured
per-hop cost ratio (~5–6×) to plug into routing decisions. Better feedforward latency or longer
chains could still move the crossover into range — that is exactly what the pre-filed
NO-crossover branch was designed to detect as *informative*, not as a failed experiment.

## Prediction ledger

Prereg (Whisper C4596): Outcome A (no crossover by N=6) conf 0.70 → **hit** — the informative
null, predicted *because* the sim tier showed swap ahead everywhere even before feedforward
latency (which only hurts teleport) was added. Law-beats-Fake on the swap arm conf 0.55 →
**MISS**, graded honestly; the ledger keeps both.

## Lineage and reuse

- **Arc**: communication primitives (comms paths doc C4588) — **E2 executed**. Kin: F87
  (superdense, E3), F89 (resource comparison, E1); Finding 51 (feedforward validated-but-idle)
  is the direct ancestor whose machinery this run finally exercised on hardware.
- **Method reuse**: informative-null-first-class pre-registration (grade the boring branch with
  its own pre-filed margin — the design pattern that made a NO result a finding); aggregate-vs-
  per-N fragility declared pre-data; dual-model pre-filed adjudication (F86 pattern, now 1–2
  against the law with a domain restriction as the residue).
- **New atlas dimension**: feedforward-latency optimism (+0.212 ln) — every future
  dynamic-circuit prereg must NOT trust fake-backend previews for feedforward arms.
- **Status-ledger claim type**: direction (ordering swap > teleport at every tested N ≤ 6),
  generation-bounded scope; the ~5–6× per-hop cost ratio is a magnitude sub-claim with the
  usual single-window caveat.
