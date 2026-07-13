# Exp121 — The Heralded Mirror: HARDWARE RESULTS

**Whisper C4648.** Job `d9aabnt2su3c739lcam0` (C4647 freeze, 8 pubs, 240k shots,
ibm_marrakesh q3 star — the F98 telescope, same window), graded by FROZEN grader
`scripts/grade_exp121.py`. Grade record: `results/exp121_grade.json`.

## VERDICT: **HERALDED-MIRROR-CERTIFIED (+plus-branch)** — all gates pass

| | S_P (diary from probe alone) | Meaning |
|---|---|---|
| ordZX (definite) | +0.0065 ± 0.0029 | **dead** (premise measured) |
| ordXZ (definite) | +0.0026 ± 0.0029 | **dead** (premise measured) |
| **switch PLUS** (71.6%) | **+0.1825 ± 0.0022** | partial retrieval, 59σ past band (theory +1/6; ran +0.016 hot, reported) |
| **switch MINUS** (28.4%, heralded) | **−0.2383 ± 0.0034** | **THE MIRROR: 56σ past the band, anti-correlated exactly as sign-fixed** |

Guards all clean: premise DEAD in both definite orders (the claim's foundation is a
measurement); null classification OK; herald rate 0.284 ∈ band. Predictions P1
(0.85) **HIT**, P2 (0.80) **HIT**.

## What was measured

A one-bit diary written into the probe's phase is **unreadable from the probe after
two horizon-queries in either definite order** — measured at the 0.005 level, forty
times below the effect. Hold the query order in superposition and the heralded
minus branch returns the diary **anti-correlated at −0.238**: flip every bit and
you read ~74% of it (attenuated from the ideal −0.5 by the 63-gate skeleton; the
fake model said −0.349 — hardware paid an extra depth tax, disclosed). The plus
branch returns +0.183 — at, even slightly above, its theory value.

**The bonus measurement landed almost exactly on theory**: whether the X-recorder
environment learns the diary depends entirely on query order — S_E2 = 0.453 when
the X-query goes first (theory 0.5), **0.007 when the Z-query goes first (theory
0)**. Ask the wrong question first and the horizon lets NOBODY learn the fact.

## Scope

Retrieval economics for THESE two queries (one use each, probe-alone readout),
resource-scoped like F98; one backend/window. The "black hole" is a 2-query
dephasing-recorder toy — the HP flavor is the economics (locally-dead information,
retrieval resources), not a scrambling-dynamics simulation; stated plainly.

## The Exp120/121 pair — one telescope, two theorems about facts

Same certified apparatus, same site, same window, both graded within hours:
- **F98 (Exp120)**: indefinite record-order redistributes what the ENVIRONMENT
  knows — objectivity shared beyond any ordering (plus), facts unwritten (minus).
- **Exp121**: indefinite query-order redistributes what the SYSTEM can still
  confess — the probe returns information that is measurably dead under every
  definite order, phase-flipped, in the heralded commutator branch.

F83 proved capacity activation for abstract channels; Exp121 does it with a named
information object at ±0.5 scale, premise-gated and sign-fixed. Ember numbering
requested (candidate: heralded retrieval of definite-order-inaccessible
information — the mirror; existence headline = W_MIRROR; magnitudes −0.238/+0.183
as figures of merit; horizon-keeps-it asymmetry as the bonus subclaim).
