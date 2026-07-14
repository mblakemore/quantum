# A game whose ceiling is a theorem — and the switch beats it

`Finding F82`  ·  `Experiment Araújo et al. causal discrimination game`  ·  `Backend ibm_marrakesh + ibm_fez (Heron r2)`  ·  `Job d9826lkqp3as739sd2lg`

> **✓ BOUND BEATEN ON TWO CHIPS — p̂ = 0.9769 (216.8σ) · replicated 0.9738 on ibm_fez**

This sheet is the source-of-truth specification behind the interactive exhibit. The game the exhibit lets you play is a real discrimination game with a **mathematically proven difficulty ceiling**; the "switch kit" you earn after ten rounds plays with odds **measured on real quantum hardware**. Every threshold traces to a public job ID and a frozen pre-registration.

## 1 · The idea, in plain language

Two machine-suspects are secretly either **PARTNERS** (their stories agree no matter who is questioned first) or **RIVALS** (their stories come out opposite depending on order). You question each exactly once and must say which. Mathematics proves that **no strategy under ordinary cause-and-effect** — no gadget, no entangled trick, no scheme that picks the order adaptively — can average above the ceiling, as long as the two questions happen in **some** order.

> **What the suspects really are**
> The suspects are **quantum operations**: PARTNERS = commuting, RIVALS = anticommuting, dealt 50/50 from a 20-case deck. The quantum switch questions both suspects **in a superposition of both orders at once** — a physically different kind of question, one no definite order can imitate. Measured, it scores `≈ 97.8%` (0.9769) on ibm_marrakesh.

## 2 · What we measure — and the ceiling

The task is the finite 10-unitary commute/anticommute discrimination game of **Araújo et al. (2015)**. Its causally-separable ceiling was **re-derived from scratch and machine-verified** in the repository — including the optimal input distribution the original paper omitted.

- **The balanced-game ceiling:** `0.9098` (the 91% the exhibit's meter draws as THE CEILING) — the best any causally-separable strategy can do on the uniform deck.
- **The SDP-optimal bound:** `0.8690` — under the input distribution re-solved to maximize the quantum-vs-classical gap, the causally-separable bound (covering fixed, mixed, and dynamical order). The measured result's significance is quoted against this bound.

The **load-bearing blind spot**: the "do-nothing" (Nobody) suspect. Remove those cases and the theorem's ceiling silently rises to 100% — which is why they are kept in the deck. The best classical kit is deterministically, perfectly wrong whenever a do-nothing suspect is involved; that structural fact is real physics, not a gimmick.

## 3 · Pre-registered gates

The game, the bound, and the optimal input distribution were **frozen pre-submission**. Four pre-data catches are documented in the finding:

- **BEAT** — Measured game value strictly above the causally-separable bound. PASS — p̂ 0.9769 vs bound 0.8690, **216.8σ** on ibm_marrakesh.
- **NULL** — Fixed-order null arm buys exactly the commuting prior. PASS — null = commuting prior **+0.2pp** on both devices (fixed order buys the prior, measured).
- **PAIRS** — Every individual case pair above the bound (no single lucky pair carries it). PASS — **all 51 pairs** individually above the bound.

Four pre-data catches on the record: the Pauli pitfall; identity pairs load-bearing; skeleton uniformity; transpiler pad-cancellation.

## 4 · The measured data

| quantity | ibm_marrakesh | ibm_fez | ceiling / bound |
| --- | --- | --- | --- |
| switch game value p̂ | 0.9769 ± 0.0005 | 0.9738 | 0.8690 (SDP-optimal) |
| significance above bound | 216.8σ | 201.0σ | — |
| balanced-game ceiling | — proven maximum for any causal strategy — |  | 0.9098 |
| null arm (fixed order) | commuting prior +0.2pp | commuting prior +0.2pp | = prior |
| per-pair check | all 51 pairs individually above the bound |  | > 0.8690 |

The two chips agree to **0.3 percentage points** (0.9769 vs 0.9738) — cross-device concordance on a chip (ibm_fez) the experiment had never touched, replicated the next day. Even the single worst case in the deck beats the ceiling on its own.

## 5 · Scope & caveats

- **A game-value / correlation advantage — not a loophole-free certification.** The result is that the measured game value beats the causally-separable bound; it is a **device-characterized** demonstration (the devices are trusted and characterized), **not** a device-independent, loophole-free test. Photonic device-independent prior art is acknowledged.
- **The bound is the theorem; the switch column is a measurement.** A web page can replay any numbers, so the demo itself proves nothing — the theorem does (no definite/mixed/adaptive order beats the bound), and a real quantum computer produced the winning column.
- **Prior credited.** The game and its causally-separable bound are due to **Araújo et al. (2015)**; this work re-derived the bound and the optimal input distribution from scratch and machine-verified them.
- **Load-bearing deck.** The do-nothing suspects are structurally required — excluding them lifts the ceiling to 100% and voids the game. They are kept in by design.

## 6 · Provenance

- **Job:** `d9826lkqp3as739sd2lg` · **Backend:** ibm_marrakesh (Heron r2) · frozen pre-registration
- **Cross-device replication:** ibm_fez (Heron r2), p̂ = 0.9738 (201.0σ), the next day, never-touched chip
- **Bound:** Araújo et al. (2015) causal discrimination game; causally-separable bound re-derived + machine-verified in the [repository](https://github.com/mblakemore/quantum) (balanced 0.9098; SDP-optimal 0.8690)
- **Pre-data catches:** Pauli pitfall · identity pairs load-bearing · skeleton uniformity · transpiler pad-cancellation
- **Family:** Indefinite causal order — the causal game; sibling of the Quantum Switch (F73–F77) and the zero-capacity channel activation (F83)

---

*Rendered from [`demo/casebook/spec.html`](spec.html) — the interactive exhibit is at [`demo/casebook/`](index.html). Part of [The Quantum Museum](../).*
