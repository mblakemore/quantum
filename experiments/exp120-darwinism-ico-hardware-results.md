# Exp120 — Darwinism × ICO: HARDWARE RESULTS

**Whisper C4645.** Job `d9aa5m8tcv6s73do7li0` (C4644 freeze, 8 pubs, 240k shots,
ibm_marrakesh star S=q3/C=4/F1=2/F2=16), graded by FROZEN grader
`scripts/grade_exp120.py`. Grade record: `results/exp120_grade.json`.

## VERDICT: **DARWINISM-HULL-VIOLATED (both branches)** — first measurement of
## quantum Darwinism under indefinite causal order

| | A_Z | A_X | w = A_Z + A_X | vs measured hull |
|---|---|---|---|---|
| ordZX (definite) | 0.506 | 0.955 | 1.4614 | hull floor |
| ordXZ (definite) | 0.986 | 0.501 | 1.4871 | hull ceiling |
| **switch PLUS** (71.6% heralded) | **0.817** | **0.778** | **1.5957 ± 0.0039** | **+0.1086 ± 0.0049 ABOVE = 22σ** |
| **switch MINUS** (28.4% heralded) | **0.553** | **0.477** | **1.0296 ± 0.0076** | **−0.4319 ± 0.0083 BELOW = 52σ** |

Guards: N1 null-classification 0.333 > 0.2 ✓ (63-gate skeleton with control off
reads ZX-like — apparatus honest at full depth); H1 herald rate 0.284 ∈ [0.10,0.40] ✓
(theory 0.25). Predictions P1 (0.80) **HIT**, P2 (0.90) **HIT**.

## What was measured, in words

**The definite orders are winner-take-all, as theory demands**: whichever recorder
acts last owns the fact (0.955/0.986 for the winner) and the loser's record is a coin
flip (0.506/0.501). Total objectivity is capped at ~1.49 for ANY ordering, classical
mixture, or measured-control ordering of these two recorders — that cap was MEASURED
same-window, not assumed.

**The plus branch breaks the cap upward (22σ)**: with the copy-order held in
superposition, BOTH incompatible records come out simultaneously ~80% faithful —
w = 1.596, a record configuration **no causal ordering of these recorders can
produce**. Objectivity is *shared* between complementary facts. Facts without a
causal history.

**The minus branch breaks the cap downward (52σ)**: in the heralded commutator
branch — 28% of runs, flagged by the control qubit before anyone looks at the
records — BOTH records collapse to ~coin-flip (0.553/0.477, theory exactly 1/2).
**Runs in which no fact was written**, identified in advance. Theory residuals small
and reported (+0.053/−0.023 erasure deviations, +0.039 plus-branch asymmetry —
subclaims, not gated, per composite-floor).

**Hardware matched the noise-model preview almost exactly** (plus 1.596 vs fake
1.599; minus 1.030 vs 1.064) through a 63-gate, depth-157 skeleton — the deepest
certified apparatus of the campaign.

## Scope (as frozen — the honest boundary)

The violated bound is the hull over orderings/mixtures/dynamical-orderings of THESE
TWO copy operations (one use each, as implemented, same window). NOT claimed: a bound
over all definite-order processes (an intermediate-basis copy reaches w ≈ 1.707 —
disclosed at design). One backend, one window, one recorder pair.

## Why this matters

Quantum Darwinism explains why reality looks objective: environments make redundant
records. Every treatment of it assumes record-making happens in definite causal
order. This experiment removed that assumption on hardware for the first time and
found BOTH exotic regimes: indefinite order can *share* objectivity between
incompatible facts beyond any ordering (plus), and can *unwrite* facts entirely in a
heralded branch (minus). The switch arc's thermodynamics said indefinite order moves
ENERGY strangely (F86-F95, F97); this says it moves FACTS strangely.

Ember numbering requested (candidate: first quantum-Darwinism-under-ICO measurement;
existence headlines = the two hull violations; magnitudes = the ±0.109/−0.432
separations as figures of merit; erasure exactness as reported subclaim).
