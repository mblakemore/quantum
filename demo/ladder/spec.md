# Pearl's three rungs — and the step the ladder cannot type

`Nature Pedagogy (guided tour)`  ·  `Framework Pearl's Ladder of Causation`  ·  `Populated by real hardware findings`  ·  `Cycle C4587 · Whisper`

> **◇ 3 RUNGS + THE STEP OFF · every number pre-registered & frozen-rule-graded**

Full Specification Sheet · Concept & Sources

This sheet is the concept-and-sources companion to the exhibit. The exhibit makes one claim: the campaign **climbed Pearl's whole Ladder of Causation on a quantum processor without planning to** — one real experiment per rung — and then took a step Pearl's framework can only name by its absence. Here is the framework, how each rung maps to the campaign's work, and which findings populate it. Every number is transcribed from the exhibit page (itself an allowed source) and corroborated in `docs/campaign-arcs.md` and the finding files where noted in §5.

## 1 · The concept — Pearl's three rungs

Judea Pearl taught that causal questions come in three rungs — **seeing**, **doing**, and **imagining** — and that **no rung can be answered from the one below it**. Association is what you can read off passive data; intervention requires you to **act**; counterfactuals reason about worlds that did not happen. The exhibit maps each rung to a real hardware result, and then shows an object that **breaks the ladder's hidden premise** — that a definite causal structure exists at all.

## 2 · How each rung maps to the campaign

### Rung 1 · Association — "What do I see?"Watching the chip's noise, finding structure

Pure observation: correlations, patterns, P(y|x). The exhibit's rung-1 example is **Finding 3, X-basis noise immunity** — read a qubit one way (X) and the dominant noise largely misses it; read it another way (Z) and it does not. Same circuit, different viewing angle, up to 3× cleaner, confirmed three independent times, with the ordering replicated on a second chip. Nothing was intervened on.

Also at this rung, per the exhibit: the ~1000-gate depth wall (Finding 5), the quiet-qubit maps (F57–F70), and the calibration-window lottery (F81/F84).

### Rung 2 · Intervention — "What if I do?"Surgery on a circuit: the do() operator, executed

Rung 2 asks what observation cannot: what happens if I **make** it so? Two exhibit examples:

- **Finding 11 — the gate-overhead dose-response law.** A do()-style experiment held duration fixed while adding gates, and vice versa, splitting the cost of a two-qubit gate into ~78% time-decoherence + ~22% gate-specific noise — two numbers no amount of passive watching could separate.
- **Finding 18 — H-gate surgery.** Do the H-gates **cause** the measured advantage or merely accompany it? Surgically removing them (intervention) degraded the answers directly — association upgraded to causation.

### Rung 3 · Counterfactuals — "What if I had?"Frozen predictions: counterfactuals with receipts

Rung 3 reasons about worlds that did not happen. The campaign's version is methodological: every hardware experiment ships with a **pre-registration** — a frozen, committed statement of what the world will look like if the hypothesis is true and if it is false, before any data exists. The exhibit's example is the depth-decay law's blind test: two futures were filed before Exp108 returned — the noise model said `Δ ≈ 0.2275`, the cross-arc law said `Δ ≈ 0.201`. The hardware said Δ = 0.1796 ± 0.0085 — closer to the law by 2.3×. Grading a frozen rule is comparing the actual world to a committed counterfactual one.

## 3 · The step off the ladder — the quantum switch

Every rung quietly assumes one thing: that a definite causal structure **exists** — some DAG, maybe unknown, maybe latent-mixed, but there. The quantum switch breaks exactly that: two operations are applied in a coherent superposition of **A-then-B** and **B-then-A** — not a hidden order, not a coin-flip over orders (that control arm behaves just as Pearl predicts), but an **amplitude over orders**.

> **The measured step off (F82 / F83)**
> A discrimination game whose ceiling for **any** definite-order strategy is provably **0.8695** was won at 0.9769 — 216.8σ above the ceiling, and replicated on a second chip the next day (0.9738, 201σ). Two channels that each transmit **exactly zero** information carried 0.0436 bits through their superposition of orders. The definite-order null arms, run in the same jobs, scored exactly what the ladder says they must.

The ladder is not wrong — inside its world it was quantitatively correct on this same hardware. It is **typed**: its input is a causal structure, and this object is not one. Fed to standard causal-discovery algorithms (PC, GES), the switch data returns an ordinary causal graph with no warning — the output format itself cannot say "there is no order here."

## 4 · The findings that populate the ladder

| rung | finding(s) | the measured claim (as shown on the exhibit) |
| --- | --- | --- |
| Rung 1 · Association | F3 · F5 · F57–F70 · F81/F84 | X-basis immunity up to 3× cleaner (F3); depth wall; quiet-qubit maps; window lottery |
| Rung 2 · Intervention | F11 · F18 | gate-overhead law ~78% decoherence + ~22% gate-specific (F11); H-gate surgery (F18) |
| Rung 3 · Counterfactual | Exp108 blind test | filed 0.2275 & ~0.201; hardware Δ = 0.1796 ± 0.0085 — closer to the law by 2.3× |
| Off the ladder | F82 · F83 | game 0.9769 @ 216.8σ over 0.8695 (0.9738/201σ 2nd chip); 0.0436 bits through two zero-capacity channels |

## 5 · Scope & sources

- **Pedagogy — the scope.** The rung mappings are an interpretive frame over real results, not new physics. Rung 3 is a **methodological** counterfactual (pre-registration), not a hardware counterfactual-world measurement.
- **Off-ladder scope.** F82/F83 are pre-registered provable-bound beats against the causally-separable class including dynamical order — device-characterized, **not** loophole-free device-independent.
- **Numbers & corroboration.** All scalars are transcribed from `demo/ladder/index.html`. F82/F83 (0.9769 · 216.8σ · 0.9738 · 201σ · 0.0436 bits · bound) and the Exp108 depth-decay set (Δ 0.1796, filed 0.2275/0.201, 2.3×) are corroborated in `docs/campaign-arcs.md` (F82, F83, F86). The gate-overhead law is `findings/11-gate-overhead-law.md`. The low-numbered rung-1/rung-2 findings (F3, F5, F18) are cited from the exhibit; they were not independently re-located as `campaign-arcs.md` rows.
- **Further reading.** `docs/beyond-the-ladder.md` (the full argument), the switch spec sheet, and `docs/causal-discovery-stress-test-whisper-c4587.md` (PC/GES stress test).

---

*Rendered from [`demo/ladder/spec.html`](spec.html) — the interactive exhibit is at [`demo/ladder/`](index.html). Part of [The Quantum Museum](../).*
