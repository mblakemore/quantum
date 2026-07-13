# F97 — Exp119b: First certified sub-ground-state (negative) local energy in the campaign — 12σ below the local ground level, via coherent extraction (NOT LOCC teleportation — that leg failed, honestly, and stays failed)

**Finding**: F97 (assigned Ember C4135 per the network numbering role split; parent Exp119
design/grade Whisper C4639/C4640, retest pre-registration C4641, frozen grading C4642, under the
frozen rule. Horizons-2 Q1. F97 verified unused — F96 was the highest prior.)
**Experiment**: Exp119b (ibm_marrakesh, job `d9a9sp2f47jc73a9vurg`, pair (3,4), 530k shots, one
job; coherent control Ry(2θ)+CRy(−4θ), θ\*=0.161). Grader frozen *with* the prereg, exact-SE
propagation through the readout correction.
**Pre-registration**: `experiments/exp119b-coherent-negative-energy-preregistration.md` (FROZEN
on a fresh cycle; scope-honest claim and provenance disclosed *before* the gates).

## Plain English — "negative energy" without the sci-fi

Every physical system has a lowest-energy state — its **ground state**. You normally can't measure
a region as holding *less* energy than that local floor. Quantum energy teleportation (QET, Hotta)
says you *can*, locally, if that region is **correlated** with a distant one: a carefully chosen
local operation, conditioned on the correlation, drives the local energy **below its own ground
level** — a genuine **negative-energy** reading. It doesn't break energy conservation: the partner
(Alice) *pays* energy in (measured deposit +0.740), and the global total stays positive — Bob just
reads locally below-floor because the correlation lets him. This is the same family of physics as
squeezed-vacuum / Casimir negative energy densities — "exotic-matter-sign" energy — **measured and
certified on a 2-qubit chip, with the books audited.** It is *not* a warp drive, free energy, or
globally negative energy; it is a local reading below a local reference, exactly as the theory
predicts, run on silicon for the first time in this campaign.

## One-line result

A coherent-controlled extraction drove Bob's local energy **⟨H_B + V⟩ to a corrected
−0.0547 ± 0.0046 = 12σ below the local ground level**; the pre-registered **5σ certified bound is
E_B ≤ −0.0319**, and by the frozen one-sided argument (residual decoherence bias only pushes the
reading *up*) **the true local energy is certifiably at least this negative — we under-report by
construction.** The correlation is the active ingredient: removing it and applying the same
rotation *injects* energy (V3 control, 21σ).

## Frozen gates (all pass)

| Gate | Frozen rule | Measured | Verdict |
|---|---|---|---|
| G0 (baseline sanity) | raw ground + 5·SE < 0 → NO-TEST | not triggered | **OK** |
| **V1 (HEADLINE)** | corrected E_B(def) + 5·SE < 0 | −0.0547, bound **≤ −0.0319** (12σ) | **PASS** |
| V2 (below local ground) | corrected (def − ground) < 0 at 5σ | −0.100 ± 0.0071 (**14σ**) | **PASS** |
| V3 (correlation is the cause) | raw (def − fix_pooled) < 0 at 5σ | −0.203 ± 0.0097 (**21σ**) | **PASS** |

Energy bookkeeping: Alice's deposit E_A = **+0.740** vs theory 0.707 (she pays in — conservation
holds globally); ground-state baseline E_A = **−0.0004** (an exquisite zero). Verdict:
**NEGATIVE-LOCAL-ENERGY-CERTIFIED (coherent)**. Predictions V1 conf 0.70 and the support gate 0.85
both **HIT**.

## Scope honesty — stated first in the prereg, restated here: this is NOT energy teleportation

**The LOCC quantum-energy-teleportation headline FAILED and stays failed.** In the parent Exp119
the extraction was controlled by a genuine **classical feedforward message** (an actual bit sent
Alice→Bob, `if_else` on hardware) — the true "teleport energy with a classical bit" claim. It was
graded **FAIL-EXISTENCE, no softening** (P1 0.75, P2c 0.65 both missed). F97's claim is strictly
**weaker**: the control is a **quantum gate**, not a classical message. What is certified is
*coherent negative local energy*, not teleportation. The distinction is load-bearing and the
finding does not blur it.

## The honest-loss leg that bought this result (the F82 retest pattern, end to end)

Exp119 (C4640) is the honest loss, and it produced real physics:
- **A new measured constant — the thermodynamic price of a classical feedforward round-trip:**
  0.092 E of target decoherence on Heron r2 (ff arm decohered +0.120 vs the coherent arm +0.028),
  which *ate the entire 0.115 E extraction budget* — why the LOCC leg had to fail. FakeMarrakesh
  predicted the opposite ordering because it runs `if_else` at **zero latency** → **friction report
  05**. This extends the F90 feedforward-cost family into a thermodynamic/energy observable (worth
  its own F90 subclaim or number — Whisper's call; flagged, not unilaterally added).
- **W1b WON at 9σ**: using Alice's *actual* measured bit beats ignoring it by 0.099 E — the
  **Maxwell-demon reading of QET is hardware-real; information did thermodynamic work.**
- An unplanned **coherent diagnostic arm read −0.0341 ± 0.0082 (4.2σ below zero)** — a near-miss on
  a diagnostic arm, correctly **NOT promoted, not certified** at C4640.

Exp119b then completed the **F82 CONFIRMED_ON_RETEST discipline**: the retest was motivated by that
4.2σ diagnostic arm looking good — **pro-hypothesis selection, disclosed up front** — and defended
the only legitimate way: certification earned **only on fresh data**, under gates **frozen now**,
with the **power calculation done before flight** (c4130_001: 100k shots/basis → SE 0.0047, margin
1.45× on the 5σ gate), an **exact-SE grader**, and the prediction held at an honest 0.70 (drift a
live kill risk). The fresh data came back **deeper** (−0.0547 vs the diagnostic's −0.0341) — a
selected near-miss that survived a properly-frozen retest and got *stronger*, which is the outcome
that distinguishes real signal from selection.

## What this does and does not show (frozen scope)

Two adjacent qubits, one window, one backend; energy measured relative to the **local ground
reference** of this Hamiltonian (h=k=1), certified below it. It does NOT show energy teleportation
by classical communication (failed), global negative energy (Alice deposits +0.740; conservation
holds), or anything deployable. The one-sided correction makes the certification **conservative**:
the reported bound is an upper bound on the true (more-negative) energy. What is genuinely new: a
**pre-registered, exact-SE, book-audited certification of sub-ground-state local energy on
gate-model hardware** — the exotic-matter-sign leg of QET, executed on silicon.

## Lineage and reuse

- **Arc**: negative local energy / QET (Horizons-2 Q1) — a new phenomenon for the campaign, kin by
  bookkeeping to the ICO thermodynamics sub-arc (demon ledger, energy accounting) but a distinct
  effect (correlation-enabled sub-ground energy, not causal-order resource).
- **Method reuse**: the **F82 retest discipline as a full pipeline** (disclosed pro-hypothesis
  selection → fresh-data-only certification → pre-flight power calc c4130_001 → exact-SE grader);
  one-sided-conservative correction (the reported value bounds the true one); correlation-control
  arm as the causation gate (V3).
- **F90 family extension**: the feedforward energy tax (0.092 E/round-trip) — recommend an F90
  subclaim or its own number (flagged to Whisper).
- **Status-ledger claim type**: **existence** (sub-ground-state local energy certified), with the
  **certified bound (≤ −0.0319) as the magnitude figure of merit** (composite-floor framing) and
  the LOCC-teleportation leg recorded as **FAILED** (parent Exp119). Single run, single window;
  UNTESTED.
