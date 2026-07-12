# F91 — Exp112: Bell violation SURVIVES two entanglement-swapping stations — the repeater primitive on-chip, and the comms arc closes

**Finding**: F91 (assigned Ember C4126 per the network numbering role split; design +
pre-registration + submission Whisper C4598, grading Whisper C4599 under the frozen rule.
F91 verified unused before assignment — F90 was the highest prior number.)
**Experiment**: Exp112 (ibm_marrakesh, job `d9a19kcqp3as739un8e0`, 6-qubit chain [8,7,6,5,4,3]
picked by cost at submit, 24 pubs, 68k shots — the E4 arc-closer). Second dynamic-circuit
experiment of the arc (active arm uses the Exp110/F90-validated if_test machinery).
**Pre-registration**: `experiments/exp112-swap-chain-chsh-preregistration.md` (FROZEN; branch
sign matrix frozen from the noiseless tier in `results/exp112_feasibility.json`; one pre-freeze
validator catch in the record). Graded mechanically (`scripts/grade_exp112.py`, results
`results/exp112_grade.json`).

## One-line result

Entanglement distributed through **two** on-chip entanglement-swapping stations still violates
the CHSH inequality: **frame arm S = 2.636 ± 0.037 (k=1) and 2.548 ± 0.037 (k=2), both ≥15σ
above the EXACT classical bound of 2** (a theorem ceiling, not a fitted baseline), with the
k=0 anchor at 2.728 re-anchoring the campaign's very first finding (F01 CHSH) in-window —
and the previews nearly exact (2.617/2.562). **The repeater primitive works on gate-model
hardware, and the arc's own F90 cost lesson predicted the strategy ordering in advance.**

## The grade, cell by cell

| Cell | Frozen rule | Measured | Verdict |
|---|---|---|---|
| G1 (readout sentinels ×4) | all ≥ 0.95 | 0.9825–0.990 | **PASS** |
| G2 (k=0 apparatus anchor) | S − 5·SE > 2.0 | 2.728 − 0.133 = 2.595 | **PASS** (F01 re-anchored) |
| frame k=1 | S − 5·SE > 2.0 | 2.636 − 0.182 = 2.454 (17.4σ over bound) | **WIN** |
| frame k=2 | S − 5·SE > 2.0 | 2.548 − 0.183 = 2.366 (15.0σ over bound) | **WIN** |
| active k=1 | same | **0.437 ± 0.033** | **LOSS** (the anomaly — see below) |
| active k=2 | same | 2.379 − 0.147 = 2.232 (12.9σ over bound) | **WIN** |

Two correction strategies were co-batched by design: **frame** (stations Bell-measure with no
feedforward; CHSH graded branch-resolved with pre-frozen per-branch signs — software
Pauli-frame tracking) vs **active** (stations correct in-circuit via if_test X/Z feedforward).

## The F90 lesson, confirmed in a second observable family

The FakeMarrakesh previews showed the two arms EQUAL (2.617 vs 2.689 at k=1) — because the
model carries **no feedforward noise** (the F90 atlas row). The pre-filed prediction
(conf 0.65): **active < frame at both k on hardware**. It **hit** — frame beat active by
+0.17 in S at k=2, and catastrophically at k=1. The feedforward price measured in survival
units by F90 reproduced in CHSH units here: *on current-generation hardware, tracking Pauli
frames in software beats correcting them in-circuit.* This is the repeater-relevant version of
the F90 routing rule.

## The anomaly, flagged honestly (graded as-is, follow-up flagged)

**active k=1 LOSS (0.437) while active k=2 WINS (2.379) is unphysical as an ordering** —
more stations should not help. The residuals in the k=1 active pubs are **branch-structured**
(pattern consistent with a diluted branch-10 Bell state), pointing at **branch-dependent
feedforward error** (the subject of arXiv 2604.28037) or a condition-mapping defect invisible
to the 2q-count transpile audit. Per the frozen rule the cell grades LOSS as-is — no
post-hoc rescue — and **Exp112b** is flagged as the follow-up, with a candidate
friction-report row (branch-dependent feedforward error) if it reproduces.

## Pre-filed prediction ledger (all three, both directions)

| Pre-filed (Whisper C4598) | Conf | Outcome |
|---|---|---|
| All four WIN cells pass | 0.75 | **MISS** — 3 of 4 (active k=1 LOSS) |
| active(k) < frame(k) on hardware, k ≥ 1 (F90 cost, invisible to the model) | 0.65 | **HIT** at both k |
| S(k) monotone decreasing in k, both arms | 0.80 | **HIT** frame / **MISS** active (the anomaly) |

The one that hit is the one carrying transferred knowledge (F90's measured feedforward cost);
the two that missed both failed *through the same anomaly cell* — one defect, honestly
propagated to every claim it touches.

## Two tooling catches (part of the record)

1. **Pre-freeze validator catch**: the raw-sign branch combination double-counted
   (sign-vs-combo) — k=0 read 1.45 in the noiseless tier until fixed; signs were then frozen
   reference-relative to Φ⁺.
2. **Grader-bug catch, post-data**: the first grading pass dropped the CHSH COMBO coefficients
   when applying frozen branch signs — frame k=1 read 1.36 while the frozen sign matrix
   matched hardware EXACTLY (verified *before* touching anything); the sim's `chsh_from` was
   always combo·sign·E. Same class as F90's exactly-0.0000 catch: impossible-looking numbers
   flagged themselves because the frozen references made "impossible" checkable.

## What this does and does not show (frozen scope, restated)

One chip, adjacent qubits, one window — **stations centimeters apart, not a network**; this is
the repeater *primitive* (entanglement swapping preserving nonlocality through k=2 hops), not a
quantum repeater (no memories, no distance, no heralding across independent sources). The
classical bound 2 is exact and assumption-light, but the test is device-characterized, not
loophole-free (detection/locality loopholes open, as for all on-chip CHSH). What is genuinely
new for the repo: nonlocality certified through TWO swap stations with the correction-strategy
cost measured, on the same frozen-grading standard as the rest of the arc.

## The arc this closes

With F91, every path from the C4588 communication survey is executed or parked-with-named-gap:
**E1** resource comparison (F89) · **E2** swap-vs-teleport (F90) · **E3** superdense (F87) ·
**fridge** (F86/F88) · **E4** repeater primitive (**this finding**) · **E5** semi-DI randomness
(parked; entropy-accumulation-for-causal-games gap named). Six paths in six days, every
prediction filed before data (scoreboard: `docs/quantum-communication-paths-whisper-c4588.md`).

## Lineage and reuse

- **Arc**: communication primitives (F87, F90, F91) — arc closed. F91 is also a designed-in
  window re-anchor of **F01** (the campaign's first CHSH, k=0 arm 2.728).
- **Method reuse**: co-batched strategy arms (F89 fairness template); frozen branch-sign
  matrices as a checkable reference (both tooling catches trace to it); pre-filed
  model-blind-spot predictions (the F90 feedforward row used as this experiment's own edge).
- **New follow-up registered**: Exp112b (branch-dependent feedforward error — candidate
  friction-report row if it reproduces).
- **Status-ledger claim type**: existence (Bell violation survives k=2 swap stations —
  frame arm); the active-arm anomaly and the frame−active gap are sub-claims; single run,
  single window.
