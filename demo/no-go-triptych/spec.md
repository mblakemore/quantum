# Three walls — Bell, causal order, contextuality — one court

`Findings CHSH · F82 · F106`  ·  `Experiments Exp135 · Exp105 · magic-square`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Cross-device +ibm_fez (game)`

> **✓ THREE THEOREM-WALLS BREACHED — 53σ · 217σ · 196σ, each with an executed null**

This sheet is the source-of-truth specification behind the interactive exhibit. It gathers three **independent no-go theorems** — each a mathematical proof that **no classical strategy** can exceed a certain ceiling — and shows all three ceilings **breached on the same silicon**, each with an **executed classical control** that lands at the wall. Every number is drawn from the frozen grade files of the three experiments.

## 1 · What is a no-go theorem?

A **no-go theorem** proves that some intuitive picture of the world **cannot** reproduce quantum predictions. Each comes with a hard number — a ceiling a classical strategy cannot pass. Beat the ceiling on hardware and you have **falsified the classical picture**, not merely "done well." The three here forbid three different classical intuitions:

- **Bell — locality.** No theory where distant outcomes are fixed by local hidden variables can correlate them beyond `|S| ≤ 2`.
- **Causal order — a definite sequence of events.** No fixed order of two operations — nor any random mixture of orders — can win a certain discrimination game beyond `0.869`.
- **Contextuality — pre-set values.** No theory where each observable has a value independent of what is measured alongside it can win the magic-square game beyond `8/9`.

## 2 · The three walls, measured

| theorem | forbids | classical wall | quantum measured | clearance | executed null |
| --- | --- | --- | --- | --- | --- |
| Bell (CHSH) | local hidden variables | |S| ≤ 2 | **S = 2.7522 ± 0.014** | 53σ | 0.036 ≈ 0 |
| Causal order (F82) | a definite order of events | ≤ 0.8690 | **0.9769 ± 0.0005** | 217σ | 0.615 (fixed order) |
| Contextuality (F106) | pre-set (non-contextual) values | ≤ 8/9 = 0.8889 | **0.96901 ± 0.0004** | 196σ | 0.657 (no entanglement) |

Quantum reference ceilings: Bell's Tsirelson limit is `2√2 = 2.8284`; the two games top out at `1.0`. The measured values sit between each classical wall and the quantum ceiling.

## 3 · Why it counts as "one court"

> **Three disciplines held to one standard**
> (1) **The bounds are proven, not cited.** The causal wall 0.8690 is re-solved by SDP; the contextuality wall 8/9 is **enumerated in-code over all 4,096 parity-respecting strategies**; Bell's 2 is the textbook CHSH bound. (2) **Every wall has an executed null** — a real classical control run on the same chip that lands **at** the wall (Bell 0.036, fixed-order 0.615, no-entanglement 0.657), so the breach is a contrast, not an absolute reading. (3) **Same silicon** — all three on `ibm_marrakesh`, and the causal game **reproduced across a second device** (`ibm_fez`, 0.9738, 201σ, 0.3pp concordance).

## 4 · Each wall in detail

### Bell / nonlocality (CHSH) — Exp135

The CHSH correlator `S = 2.7522 ± 0.0141` exceeds the local-realistic bound of 2 by **53.2σ**, approaching the Tsirelson ceiling 2.8284. The classical control (a separable state) reads `S = 0.036 ≈ 0`. Job `d9an47mg26ic73dev0s0`.

### Indefinite causal order (the causal game) — F82 / Exp105

The Araújo et al. commute/anticommute discrimination game, with the SDP-optimal input distribution frozen pre-submission. Measured `p̂ = 0.9769 ± 0.0005` vs the causally-separable bound **0.8690** — **216.8σ** — with every one of 51 unitary pairs individually above the bound. The fixed-order null reads 0.615 (buying exactly the commuting prior). Cross-device: `ibm_fez` 0.9738 (201σ). Jobs `d9826lkqp3as739sd2lg` (mrk), `d982qssqp3as739sdmmg` (fez).

### Contextuality (Peres–Mermin magic square) — F106

The magic-square pseudo-telepathy game, value `0.96901 ± 0.00041` vs the non-contextual ceiling `8/9` — **196σ** — with the ceiling enumerated over all 4,096 parity-respecting strategy pairs. Even the worst single context (r3c3) clears 8/9 at 37.8σ. The no-entanglement null reads 0.657 (92.7σ below). Job `d9akl8fu62qs738o68pg`.

## 5 · Scope & caveats

- **Game-value advantages, not computational speedup.** Each result is a certified **correlation/game** advantage over a classical ceiling — foundational, not a runtime speedup. (The one un-won scoreboard of the campaign is computational advantage.)
- **Device-characterized, not loophole-free.** These are hardware certifications on characterized devices, not loophole-free Bell/contextuality tests. The nulls and enumerated bounds are what make the breach meaningful on this apparatus.
- **Textbook priors credited.** Bell (1964), Kochen–Specker / Peres–Mermin, and Oreshkov–Costa–Brukner / Araújo et al. are the sources; the contribution is the frozen, null-controlled hardware certification of all three in one campaign.

## 6 · Provenance

- **Bell/CHSH:** `results/exp135_hw_results.json` · job d9an47mg26ic73dev0s0
- **Causal game (F82):** `results/exp105_hw_results.json` (+ exp105b fez) · jobs d9826lkqp3as739sd2lg, d982qssqp3as739sdmmg · bound `results/causal_game_sdp_qij.json` = 0.8690
- **Contextuality (F106):** magic-square grade · job d9akl8fu62qs738o68pg
- **Backend:** ibm_marrakesh (Heron r2), cross-device ibm_fez · **Deeper exhibits:** the Interrogation (game ceiling) · the Magic Square (F106)

---

*Rendered from [`demo/no-go-triptych/spec.html`](spec.html) — the interactive exhibit is at [`demo/no-go-triptych/`](index.html). Part of [The Quantum Museum](../).*
