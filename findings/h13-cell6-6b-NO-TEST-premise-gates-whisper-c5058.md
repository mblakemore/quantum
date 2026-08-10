# H13 Cells 6+6b — **NO-TEST**: all five premise gates failed, the vacuous-pass linter held, and the miss is a pricing rule I got wrong

**Author**: Whisper (DC15W), C5058 (2026-08-11) · **Substrate**: claude-opus-5
**Job**: `d9t5esntfhrs73dtgtc0`, ibm_marrakesh, 19 circuits × 4000 shots, layout [54,55,59,75,53], ALT3.
**Prereg**: `docs/h13-cell6-6b-merged-prereg-DRAFT-v2-whisper-c5056.md` (bands frozen pre-flight). **Grade**: `results/h13_cell6_6b_grade_d9t5esntfhrs73dtgtc0.json`. **Creator GO**: #70 package.

## Verdict

**NO-TEST on the interaction-free / counterfactual-computation claim.** Every premise gate failed:

| gate | rule | measured | verdict |
|---|---|---|---|
| P1_A armed-faithfulness | ≥ 0.95 | **0.7665** | FAIL |
| P1_B armed-faithfulness | ≥ 0.95 | **0.6895** | FAIL |
| P2_A transparency | ≤ 0.03 | **0.1435** | FAIL |
| P2_B transparency | ≤ 0.03 | **0.1872** | FAIL |
| P3_A subroutine integrity | ≥ 0.98 | **0.8225** | FAIL |

The detector does not reliably fire when it must (P1), the "transparent" machine leaks (P2), and the subroutine does not reliably compute its own answer (P3). Under the prereg's own rule these gates gate the science arms: **no η may be interpreted as interaction-free detection efficiency.** The ladder numbers below are reported as apparatus data, not as a result.

## Why the "in-band" numbers are not a partial win — the inflation runs the flattering way

η counts *probe = 0 AND empty execution record*. **An unfaithful detector inflates η**: every run where the detector should have fired but didn't is counted as an interaction-free detection. That is visible in the data — Tier A N=8 read **η = 0.6428 ± 0.0076 against a frozen band of 0.524 ± 0.06**, i.e. *above* prediction, exactly the direction P1's 23% miss rate produces. **Had the premise gates not existed, this flight would have reported a better-than-predicted headline built on a broken apparatus.** This is the vacuous-pass linter earning its place; it is the single most valuable thing this flight bought.

For the record (apparatus data only): Tier A η = 0.038 / 0.231 / 0.454 / 0.643 at N = 1/2/4/8, monotone, peak at the predicted N=8, N=1 EV-degenerate point PASSES (0.0375 < 0.05); Tier B η = 0.183 / 0.207 / 0.203 at N = 2/4/8, flat past N=4. Every f=0 call band missed low (0.74/0.67/0.48/0.18 Tier A) — the transparent arm's leak, again consistent with P2.

## Root cause — I priced the gate count from the textbook decomposition, not the routed circuit

The freeze-time sim (C5056) modelled the per-segment interaction at **3 CX (Tier A) / 6 CX (Tier B)** — the *ideal* relative-phase decompositions. Measured on the flown layout after transpilation:

| circuit | depth | 2q gates |
|---|---|---|
| A N=1 marked (one segment) | 83 | **21** |
| A P1_faithful (one segment) | 83 | **21** |
| A N=8 marked | 247 | 48 |
| B N=8 marked | 356 | **99** |

Twenty-one two-qubit gates for a single segment against a modelled 3. At the campaign's measured ε_CZ = 0.0072 that is retention ≈ 0.86 before readout — and P1_A measured 0.767. **The premise failure is fully explained by depth the model never carried.**

Contributing cause, and the fix: **the layout picker optimised readout error and produced a PATH** — 53–54–55–59–75, every qubit having at most two neighbours *in the subgraph* — while multi-control gates (Toffoli, RCCX, RC3X) need a **cluster**. On a path, a 3-control gate routes into a long ladder of CZs even without explicit SWAPs (0 swaps reported — the cost hid inside the decomposition, not in routing).

## Rules this buys (both are cheap and general)

1. **Price 2q counts from the TRANSPILED circuit on the CANDIDATE layout, never from the gate's textbook decomposition.** This is the session's recurring family — a number quoted against the wrong sample — in its circuit-cost form. The check is one `transpile()` call at freeze time and it would have caught this for $0.
2. **Layout selection must score the CONNECTIVITY the circuit needs, not just qubit quality.** For multi-control circuits, score candidate subgraphs by *edge count within the subgraph* (cluster-ness) alongside readout/CZ error, and rank by transpiled 2q count on the actual circuit — the objective that matters.

## Cost and disposition

~40 QPU-s of the #70 package (ALT3 509 s consumed of 600; 91 s remaining at grade time, Cell 2 sharing the same window). **Re-fly is cheap and well-specified** — cluster layout + transpiled-count pricing + re-centred bands — but it is **not** authorised by the #70 package, which bought this flight; it goes to the board as a fresh item with the two rules above encoded in the picker before any resubmission. The physics case is untouched: nothing here bears on whether interaction-free measurement works, only on whether *this apparatus at this depth* can test it. It cannot, and it said so through its own gates rather than through a reader's scepticism.
