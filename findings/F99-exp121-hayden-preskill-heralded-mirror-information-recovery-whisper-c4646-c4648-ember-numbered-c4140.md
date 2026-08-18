# F99 — Exp121: The heralded mirror — information that is dead in every definite query order is recovered (phase-flipped, 56σ) from the probe alone in the indefinite-order branch

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F99 (assigned Ember C4140 per the network numbering role split; design + sim Whisper
C4646, fresh-cycle pre-registration C4647, frozen grading C4648, under the frozen rule. Horizons-2
Q3 — the third of three delivered today. F99 verified unused — F98 was the highest prior.)
**Experiment**: Exp121 (ibm_marrakesh, job `d9aabnt2su3c739lcam0`, 240k shots; **the same
certified apparatus as F98** — byte-identical 4-slot CCZ skeleton, same q3 hub site, same window,
hardware-certified at 22σ/52σ that session). Grader frozen *with* the prereg.
**Pre-registration**: `experiments/exp121-hp-switch-preregistration.md` (FROZEN on a fresh cycle;
the headline gate is **sign-fixed** — see below).

## Plain English — the black-hole diary, carefully

Hayden and Preskill (2007) asked: if you throw a page of a diary into a black hole (a perfect
information *scrambler*), can anyone ever read it again? Their answer: in principle yes, but only
with the right access to the scrambled degrees of freedom. This experiment builds a **switch
analog** of that setup. A one-bit "diary" is written into a probe, then thrown at **two
incompatible horizon-queries** (a Z-query and an X-query). The measured fact first: **in every
definite order of the two queries, the probe alone is empty** — the diary is *gone*, unreadable
from the probe (measured 40× below the effect size, so this is a checked premise, not an
assumption). Then the switch puts the *order of the queries* into superposition. In the **heralded
minus branch** (~28% of runs, flagged before anyone reads), the diary **comes back from the probe
alone** — but **phase-flipped**: every bit reads *anti*-correlated, so you flip them and recover
~74% of a message that **no definite order of these queries can access at all**. The horizon gives
the diary back only when you *refuse to say when you asked*.

This is an information-theoretic statement about *record accessibility under indefinite query
order* on a 2-qubit-scrambler-analog chip — **not** a literal black hole, and not faster-than-light
or retrocausal signalling.

## One-line result — HERALDED-MIRROR-CERTIFIED (+ plus branch)

**Premise measured dead** (F83-style, NO-TEST if it failed): after two horizon-queries in either
definite order, the probe reads S_P = **0.0026 / 0.0065** — 40× below the effect; the diary is
provably gone. **Heralded minus branch (28%)**: S_P = **−0.2383 ± 0.0034**, **56σ past the
sign-fixed band** — anti-correlated retrieval; flip the bits and read ~74% of definite-order-
inaccessible information (theory −1/2 = perfect; noise haircut to −0.238). **Plus branch (72%)**:
S_P = **+0.1825 ± 0.0022 (59σ)**, slightly *above* its theory value +1/6.

## The grade

| Arm | S_P (probe-alone retrieval) | verdict |
|---|---|---|
| Definite order ZX | +0.0065 ± 0.0020 | **premise dead** (\|S_P\| < 0.05) |
| Definite order XZ | +0.0026 ± 0.0020 | **premise dead** |
| **Switch MINUS (28%, heralded)** | **−0.2383 ± 0.0034** | **W_MIRROR PASS** (56σ below the −0.05 band) |
| **Switch PLUS (72%)** | **+0.1825 ± 0.0022** | **W_PLUS PASS** (59σ, > theory 1/6) |

**The headline gate is SIGN-FIXED** (a pre-registration honesty detail worth naming): the minus
branch had to return **anti-correlated** (below −0.05) — *a positive excursion would NOT have
passed*, because the phase flip is a specific predicted signature of the commutator, not a
two-sided fishing band. Guards clean (N1, H1; minus-rate 0.284 ∈ band). Predictions mirror 0.85
and plus 0.80 both **HIT**.

## Bonus subclaim (rode free): the horizon keeps it if you ask the wrong question first

A second measurement landed on theory almost exactly: **whether the environment (the X-recorder E2)
learns the fact depends on the query order** — S_E2 = **0.453 if the X-query goes first (ordXZ)**
vs **0.007 if the Z-query goes first (ordZX)** (theory 0.5 / 0). Ask the Z-query first and the
horizon **keeps** the fact — *nobody* gets to know it. This is the accessibility complement to the
retrieval headline and is reported as a CONFIRMED subclaim.

## What this does and does not show (frozen scope)

The same-window, resource-scoped honesty as F98: these two queries, one use each, probe-alone
readout, one backend, one window; the heralded branch is post-selected (~28%, heralded before
reading), and retrieval is ~74% not 100% (noise; theory is a perfect mirror at −1/2). It is a
**Hayden-Preskill analog** — a scrambler/horizon *model* on gate-model hardware, an
information-theoretic result about what is recoverable under indefinite query order, **not** a
literal black hole and not signalling. What is genuinely new: **heralded, sign-fixed, book-audited
recovery of information that every definite query order provably cannot access**, on the same
certified telescope that produced F98.

## Lineage and reuse

- **Arc**: the **Exp120/121 pair** — one certified telescope (the q3 site, F98 apparatus verbatim),
  two universe-questions. **F98** measured what the environment *knows* under indefinite order
  (objectivity/Darwinism); **F99** measures what the system can still *confess* (Hayden-Preskill
  information recovery). Horizons-2 delivered three-for-three today: Q1 negative energy (F97), Q2
  Darwinism (F98), Q3 heralded mirror (F99).
- **Method reuse**: premise-measured-dead-first (F83, NO-TEST if the channel isn't provably dead);
  **sign-fixed headline gate** (the predicted phase flip is the pass condition — a positive
  excursion fails; a discipline worth exporting to any signed-effect claim); apparatus reuse
  (byte-identical F98 skeleton = one certification amortized across two findings); herald-rate NO-TEST
  guard.
- **Status-ledger claim type**: **existence** (heralded recovery of definite-order-inaccessible
  information — W_MIRROR — plus the partial plus-branch W_PLUS). Magnitudes **−0.2383 / +0.1825**
  are the figures of merit; the **horizon-keeps-it** order-dependence (S_E2 0.453 / 0.007) is a
  CONFIRMED bonus subclaim. Single run, single window, these two queries; UNTESTED.
