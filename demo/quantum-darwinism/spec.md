# Two objective facts that no causal order can hold at once

`Finding F98`  ·  `Experiment Exp120 (Darwinism × ICO)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9aa5m8tcv6s73do7li0`  ·  `Cycle C4645 · Whisper`

> **✓ VERDICT — DARWINISM-HULL-VIOLATED (both branches) · 22σ & 52σ**

Full Specification Sheet

This sheet is the source-of-truth specification behind the interactive exhibit. Every number on the exhibit is drawn from here; every number here is drawn from the frozen grade file `results/exp120_grade.json` and its job record `results/exp120_jobids.json`. It is the crown jewel of Horizons-2 and the campaign's deepest certified apparatus — **63 two-qubit gates**.

## 1 · The idea, in plain language

**Why is anything a "fact"?** Quantum Darwinism (Zurek) says a property becomes **objective** when the environment makes **many redundant copies** of it. You and I agree the moon is there because countless photons each carry the same record of it — we can each read a different fragment of the environment and get the same answer. Objectivity is redundancy.

**The catch: complementarity.** A quantum system has properties that cannot both be sharply defined — here, a Z-fact and an incompatible X-fact. The environment cannot hold faithful copies of **both** at once. So if two recorders each try to copy one property, there is a hard ceiling on how objective the two facts can jointly be.

> **The measured quantity**
> Each recorder's **faithfulness** `A` is how good its copy is: `A = 1` a perfect objective record, `A = 0.5` a coin-flip (no information). The **joint objectivity** is their sum `w = A_Z + A_X`. Under **any definite order** of the two recorders, w is boxed into a narrow **hull** — that box is what a causal history permits.

**The twist (indefinite causal order).** A quantum switch puts the **order** of the two recorders into superposition — recorder-Z-then-X **and** X-then-Z at the same time. Now measure w. If it leaves the hull, we have joint objectivity that **no ordering of events could have produced**: facts without a causal history.

## 2 · The objectivity hull — winner-take-all

Under a definite order, the **last** recorder wins: it copies its property faithfully (`A ≈ 0.95–0.99`) while the earlier recorder's copy is scrambled by the later measurement to a coin-flip (`A ≈ 0.50`). The two orders trace the edges of the hull:

> **Measured hull (same window, these two recorders)**
> Z-then-X: `A_Z=0.506` (lost), `A_X=0.955` (won) → `w=1.4614`. X-then-Z: `A_Z=0.986` (won), `A_X=0.501` (lost) → `w=1.4871`. **Hull = [1.4614, 1.4871]** — everything a definite order can reach. The winner-take-all pattern is exactly what theory demands.

## 3 · Pre-registered gates (frozen before flight)

- **N1** — Herald sanity: the switch-control witness must register indefinite order. PASS (0.333).
- **H1** — Minus-branch rate in the expected window (theory 0.25). PASS (0.284).
- **W_PLUS** — `w_plus > hull_max` by >5·SE — joint objectivity **above** the ceiling. PASS (+0.109, 22σ).
- **W_MINUS** — `w_minus < hull_min` by >5·SE — both records **erased** below the floor. PASS (−0.432, 52σ).

## 4 · The measured data

Faithfulness of each recorder, and the joint objectivity `w`, for every arm. 30,000 shots per definite arm; the switch branches are split by the heralded control outcome (+ = 71.6%, − = 28.4%).

| arm | Z-fact A_Z | X-fact A_X | w = A_Z+A_X | vs hull |
| --- | --- | --- | --- | --- |
| Z-then-X (definite) | 0.506 | 0.955 | 1.4614 | hull floor |
| X-then-Z (definite) | 0.986 | 0.501 | 1.4871 | hull ceiling |
| switch → + branch (72%) | 0.817 | 0.778 | **1.5957 ± 0.0039** | **+0.109 · 22σ** |
| switch → − branch (28%) | 0.553 | 0.477 | **1.0296 ± 0.0076** | **−0.432 · 52σ** |

Theory targets (reported, not gated): `w_plus = 1.667`, `w_minus = 1.0`, `hull point = 1.5`, `minus rate = 0.25`. The hardware matched the noise-model preview to the third decimal.

## 5 · The two violations

> **+ branch (72%) — facts without a causal history**
> Both incompatible records land at **~0.80 faithful at once** (`w=1.596`), a joint objectivity **0.109 above the ceiling** that any definite order can reach — **22σ**. Two complementary facts share the environment's redundancy at the same time, a configuration **no sequence of events can produce**.

> **− branch (28%, heralded) — record erasure**
> Both records collapse to **coin-flip** (`A_Z=0.553`, `A_X=0.477`, `w=1.030`) — **0.432 below the floor**, **52σ**. The environment holds **no** faithful copy of either fact. Erasure is **flagged by the herald before anyone reads the records**.

## 6 · Scope & caveats

- **Resource-scoped.** The hull is the reachable set of **these two recorders** in this window, not a universal bound over all possible apparatus. The claim is: **within this fixed resource**, superposed order exits a box that every definite order is confined to.
- **The intermediate-basis cheat is excluded by construction.** A recorder reading in a cleverly-tilted intermediate basis could fake shared objectivity; that loophole is disclosed and structurally removed (F82 lineage). The recorders read the pure Z and X bases.
- **Separations are the figures of merit.** The +/− **excursions past the hull** (22σ, 52σ) are the certified results. The exact erasure values and theory-matching are **reported**, not gated.
- **Deepest apparatus.** 63 two-qubit gates — the campaign's deepest certified circuit (the deliberate opposite of the grandfather audit's 3-gate shallowest). Hardware matched the noise model to the third decimal, which is why a circuit this deep still certifies.

## 7 · Provenance

- **Grade file:** `results/exp120_grade.json` · **Job record:** `results/exp120_jobids.json` · **Job:** d9aa5m8tcv6s73do7li0
- **Backend:** ibm_marrakesh (Heron r2) · **Shots:** 30,000/definite arm · **Depth:** 63 two-qubit gates
- **Sibling telescope:** F99 (the heralded Hayden–Preskill mirror) shares this exact certified skeleton, site, and window
- **Family:** Horizons-2 Q2 · lineage F82 (loophole discipline)

---

*Rendered from [`demo/quantum-darwinism/spec.html`](spec.html) — the interactive exhibit is at [`demo/quantum-darwinism/`](index.html). Part of [The Quantum Museum](../).*
