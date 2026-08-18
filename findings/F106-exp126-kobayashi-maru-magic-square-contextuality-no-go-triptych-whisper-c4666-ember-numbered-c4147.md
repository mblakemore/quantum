# F106 — Exp126 "The Kobayashi Maru": the Peres–Mermin magic-square game won at 196σ over an *enumerated* classical ceiling — contextuality certified, completing the no-go triptych (Bell · causal order · contextuality)

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

> ### ⚠️ SCOPE LABEL ADDED C5075 — ROBUSTNESS TO READOUT DRIFT IS UNMEASURED
>
> **The 196σ stands as what it is: a STATISTICAL statement — "this measurement is not chance,
> given the observed rate." It is NOT a ROBUSTNESS statement.** 0.969 is a fact about the window
> this flew in. What is *not* established, and what a reader is invited to assume, is that 0.969
> is a property of the DESIGN rather than of that WINDOW.
>
> **Why it matters (Whisper C5075, verified by Elder general#12844):** the ceiling is 8/9 = 0.8889,
> so the flown margin is only **+0.0801**. At the campaign's TRUE drift-inflated readout (~2.9%,
> i.e. published × the F81-measured 3.4× understatement) a 4-qubit/4-read circuit of this shape
> projects to ~0.89 — **margin +0.0011, and 196σ becomes ~2.7σ.** The result would not clear.
>
> **Both routes to settling it are closed**: job `d9akl8fu62qs738o68pg` is past IBM retention, and
> our local artifacts banked the RESULTS but not the CALIBRATION CONTEXT. So the honest label is
> **epoch-dependence UNKNOWN** — not wrong, not retracted, and not silently assumed robust.
>
> **The trap is camouflaged by its own σ.** A large σ reads as unassailable, and the number it
> certifies is a single-epoch draw. *σ measures distance from chance; it says nothing about
> distance from a different Tuesday.* This campaign hit that shape three times in one session — a
> 32-row probe whose 97.7% qualification was overturned nine minutes later, an N1 flight
> attribution marked provisional, and now a certified result whose window cannot be recovered.
>
> **Forward fix (C5075):** `ibm_multi_account.submit_snapshot()` now banks the calibration context
> alongside the queue state, so no future flight can leave this hole.


**Finding**: F106 (assigned Ember C4147 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4666, under the frozen rule. Horizons-3 H5.
F106 verified unused — F105 was the highest prior.)
**Experiment**: Exp126 (ibm_marrakesh, job `d9akl8fu62qs738o68pg`, 4 qubits, 20 pubs, 220k shots).
**Pre-registration**: `experiments/exp126-magic-square-preregistration.md` (FROZEN; scope stated
first; the classical bound **enumerated in-code**, and a vacuous broken-scenario caught by the
linter pre-freeze).
Companion to the C4666 audit `docs/quantum-advantage-audit-whisper-c4666.md` (Creator's question,
"have we found quantum advantage?").

## Plain English — the no-win scenario that quantum mechanics wins

The Peres–Mermin **magic square** is a 3×3 grid you're asked to fill with ±1 so that every row and
column multiplies to +1, except one column that must multiply to −1. **No consistent classical
assignment exists** — try it and you always fail at least one of the nine — so the best any classical
strategy can do, even with shared cheat-sheets, is win **8 of 9** contexts. It's a *no-win scenario*,
the Kobayashi Maru. Quantum mechanics **wins it with certainty**, because quantum observables are
**contextual**: the value you get for a measurement depends on which *other* compatible measurements
you make alongside it, so the square doesn't need one fixed answer per cell. On this chip the game was
won at **96.9%** — and the classical ceiling it beats (8/9) wasn't looked up, it was **computed by
brute force over all 4,096 classical strategies inside the experiment's own code**. Beating a ceiling
you re-derived yourself is the strongest form of the claim.

## One-line result — CONTEXTUALITY-CERTIFIED, all four gates PASS

Measured game value **0.96901 ± 0.00041** against the classical ceiling **8/9 = 0.88889** →
**clearance 196σ**. The jewel gate: even the **worst** context (r3c3, the 10-CZ routed one) wins at
**0.9482 ± 0.0016 = 37.8σ over 8/9** — and a *minimum-over-contexts* above 8/9 is classically
impossible **even for mixtures** (min ≤ average ≤ 8/9), a strictly stronger statement than the pooled
average. The executed no-entanglement null pooled at **0.657, 92.7σ below** the ceiling (dead on the
pre-filed sim value); sentinels 0.99 / 0.98.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1 (game) | pooled > 8/9 + 5·SE | 0.96901 (196σ) | **WIN** |
| W2 (min-context) | min context > 8/9 + 5·SE | 0.9482 (37.8σ) | **WIN** |
| G_null (control) | no-entanglement null < 8/9 | 0.657 (92.7σ below) | **PASS** |
| G_sent (sentinels) | ≥ 0.95 | 0.99 / 0.98 | **PASS** |

Predictions 0.93 / 0.85 both **HIT**. The per-context 2q depth ranges 2–10 CZ (r3c3 the deepest at 10);
the win holds even at the deepest, routed context.

## Why the *enumerated* bound matters (method subclaim)

The classical ceiling 8/9 is **recomputed exhaustively in the artifact** — a full search over all 4,096
deterministic parity-respecting strategy pairs returns max average win = 8/9 exactly (deterministic
suffices; shared randomness is a convex combination, so it can't do better). It is **not cited from
memory or literature** (pattern c857: verify the bound covers *your* instance class before grading).
A provable-bound beat is only as trustworthy as the bound; here the bound is provable *inside* the
same code that grades the data.

## The vacuous-pass lint save (method subclaim)

The gate-feasibility linter caught the **broken/control scenario as vacuous** pre-freeze and it was
fixed to *entanglement-dead* (the C4657/C4662 self-catch discipline: a control that can't fail tests
nothing). The executed null (0.657, coin-flip-class on the entangled contexts) is the honest control
that resulted.

## The completion — the no-go triptych, certified in one court

With F106 the campaign has now certified, on the same hardware and grading standard, **all three of
quantum theory's great no-go results**:
- **Bell / nonlocality** — the CHSH violation (F73-class; re-anchored in-window by F100).
- **Indefinite causal order** — the causal discrimination game beating the causally-separable bound
  (F82, 216.8σ).
- **Contextuality** — the magic-square game beating the classical parity ceiling (**F106**, 196σ).

Three theorems that each say "no classical/local/definite model can reproduce this," all beaten with
executed nulls and enumerated bounds in one campaign.

## What this does and does not show (scope, stated first in the prereg)

A **game-value** quantum advantage, not a **computational-speedup** claim — no time-to-solution
statement is made (the campaign's one un-won scoreboard; F54's 10× depth deficit stands). The magic
square is **textbook** (Mermin 1990; Brassard–Broadbent–Tapp pseudo-telepathy 2005) and has run on
other platforms; the contribution is the **pre-registered, exhaustively-verified-bound,
adversarially-controlled gate-model certification with an executed no-entanglement null**. Alice and
Bob are two halves of one chip, **not space-like separated** — **no loophole-free claim**; the claim
is that the statistics exceed what *any* parity-respecting classical strategy (any LHV, shared
randomness included) can produce, against the in-code enumerated bound.

## Lineage and reuse

- **Arc**: provable-bound no-go beats (the F82 game class) — completes the **Bell · causal-order ·
  contextuality triptych**. Also the **bridge to the one un-won advantage**: BGKT-2020 noisy
  shallow-circuit separation (the only *unconditional* computational-advantage theorem at this depth)
  runs on exactly this game, and **today's per-context fidelities are its noise parameters** (Exp127
  groundwork committed) — the contextuality win is the on-ramp to a possible computational advantage.
- **Method reuse**: enumerate-the-bound-in-the-artifact (never cite a ceiling you can compute);
  min-over-contexts as a strictly-stronger-than-average gate; vacuous-control lint save; executed
  no-entanglement null as the adversarial control.
- **Status-ledger claim type**: **existence** (contextuality / classical-parity-ceiling beat).
  Figures of merit: **0.96901 / 196σ** (pooled) and **0.9482 / 37.8σ** (min-context). Method subclaims:
  **enumerated-bound-in-artifact** and the **vacuous-pass lint save**. HW tier; single run; UNTESTED.
