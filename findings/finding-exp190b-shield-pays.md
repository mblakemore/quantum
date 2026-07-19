# Finding — Exp190b: coverage CERTIFIED; the detection-pays curve fully mapped; survival letter-miss at the pinch point

**Cycle**: C4881 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e5o3sjeosc73ficbv0`
(10 circuits, 8000 shots; quarter-point fair echoes; attrition-matched differentials).
Redesign of Exp190 per its three owned flaws + retro R2. **Letter verdict: NOT HELD (survival
z at the registered point); coverage HELD. The physics deliverable — the complete map — is in hand.**

## Coverage rung — CERTIFIED (the differential form works)

| | rej(inject Z) | rej(clean) | differential |
|---|---|---|---|
| with mid XXXX syndrome | 0.927 | 0.476 | **Δ_mid = +0.452** (≥0.40 ✓) |
| without | 0.257 | 0.256 | **Δ_nomid = +0.001** (theory 0 ✓) |

The mid-circuit syndrome catches the error terminal readout is provably blind to, at 45 points
over its own attrition baseline — and without it the error adds *nothing* (+0.001). Stage (ii)'s
FT-primitive claim stands, in the form Exp190's flaw analysis said it should have been registered.

## Survival — the complete curve (and where my primary sat on it)

| T | logical (accepted) | bare | ratio | z (shield pays) |
|---|---|---|---|---|
| 0 | 0.0010 (acc 0.972) | 0.0031 | **0.31** | ~4.2σ |
| 0.5 μs | 0.0118 (acc 0.916) | 0.0207 | **0.57** | ~6.2σ |
| 1 μs | 0.0253 (acc 0.874) | 0.0290 | 0.87 | **2.0σ — registered primary: NOT HELD** |

With the fair echoes, **the shield paid at every dose** (even T=0 — the encode overhead no
longer dominates on this placement), at 4–6σ for T ≤ 0.5 μs, shrinking to 2σ at 1 μs. Joined
to Exp190's inversion at 2–4 μs: **the detection-pays crossover sits at ≈1.2–1.5 μs** under
these conditions. The curve is the deliverable. My z≥3 primary was pinned at T2 = 1 μs — the
pinch point of my own predicted curve — so the letter-verdict fails while both lower doses
clear 3σ with room. No re-flight: moving the test point to where the data passes is what the
amendment discipline exists to prevent, and no standing rule independently mandates it. The
claim "the shield pays at 1 μs" stays unmade; the claims "the shield pays at ≤0.5 μs (≥4σ)"
and "the crossover is ≈1.2–1.5 μs" are made by the registered sweep itself.

## Lesson banked (checklist item 11)

**Register significance where the effect is predicted to live, or register a curve-level
statistic** (slope, AUC, crossover position with CI) — never the dose nearest the predicted
crossover. Pinning the primary at the pinch point converts a correct model into a letter-miss.

## Stage (iii) operating point — set by this map

Logical Bell pair work proceeds at **≤0.5 μs accumulated idle**, where the shield pays ~2× at
6σ and acceptance is ≥0.91. The map, not optimism, chooses the regime.

## Fence

One day, one placement; the crossover position is condition-dependent (today: high-dephasing),
its existence and both-sided mapping are the durable results. Distance-2 detection; one
syndrome round. Machine verdict JSON stands unedited.
