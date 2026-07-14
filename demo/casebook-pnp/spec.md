# A tabletop deck whose odds were measured, not designed

`Nature Tabletop (print & play)`  ·  `Games The Interrogation (F82) · Static (F83)`  ·  `Backends ibm_marrakesh · ibm_fez`  ·  `Booklet v1 · C4541 · Whisper`

> **◇ EVERY PROBABILITY MEASURED ON REAL HARDWARE · none of the odds were designed**

This sheet is the methodology companion to the printable booklet. The Casebook turns two certified hardware results into d100 dice games: every threshold on the deck is a **measured** number rounded to a d100, and the point of each game is that its **SWITCH column beats a classical ceiling that is a theorem**. Below: the rules, the ceiling each game beats, and how the deck maps to the certified result. Numbers are transcribed from `demo/casebook-pnp/index.html` and corroborated in `docs/campaign-arcs.md` (§4).

## 1 · Game 1 — The Interrogation (F82)

The city's machines come in pairs: **PARTNERS** (their stories agree no matter who is questioned first) or **RIVALS** (their stories come out opposite). You may question each suspect **once**, then call it. A Dealer holds the Case Table; Detectives pick an **Interrogation Kit** (a cut-out card), roll d100 against that case's column, and decide PARTNERS or RIVALS. Play 10 rounds; track your percentage.

The deck ships three kits, each a real strategy class with its measured deck average:

| kit (strategy class) | deck average | what it is |
| --- | --- | --- |
| ROOKIE | 57.5% | question each suspect separately, same question |
| ENTANGLED CASEFILE | 75% | the best straight-reading kit — one file in two linked halves |
| ⚡ SWITCH BADGE | 97.8% | question both suspects in both orders at once |

> **The classical ceiling this game beats**
> No kit that questions each suspect once — **not these two, not any kit anyone will ever invent** — can average above 91%. That is a mathematical theorem (Araújo et al. 2015; the bound re-derived and machine-checked in-project). For the **balanced** game the proven definite-order ceiling is 0.9098.

> **How the deck maps to the certified result**
> The **⚡ SWITCH column** replays finding **F82**: the switch scored 0.9769 ± 0.0005 on `ibm_marrakesh` (job `d9826lkqp3as739sd2lg`, 216.8σ above the ceiling) and 0.9738 on `ibm_fez` — a chip it had never touched — the next day (deck: 97.4%). The Casefile kit is **always wrong when "The Nobody" is involved**: the do-nothing suspect is exactly what breaks the cleverest classical strategy — and the SWITCH column simply does not care.

## 2 · Game 2 — Static (F83)

A Sender seals a secret — **RED or BLUE** — and must whisper it through **two censor machines** that each turn everything to static. In any order, with any tricks, **zero** information survives — a theorem about the world, and the control experiment measured it: 0.00012 bits. The classical table is 50/50 forever. The switch table is different: roll the **STAMP** die (01–62 = UP, else DOWN), roll the **MESSAGE** die, then decode (UP → trust the die, DOWN → flip it). Tally rounds; the majority is the precinct's verdict.

> **How the deck maps to the certified result**
> Game 2 replays **F83** capacity activation: two channels that each destroy all information — and provably destroy it in ANY definite order — transmitted 0.0436 bits per use when combined in the switch (job `d983ek52su3c739ip92g`, 55.6σ). The message alone is static; the stamp alone is static; the secret lives only in how they **move together**. That correlation is worth exactly 0.0436 bits per round — which is why the signal compounds over rounds (~62% one round → ~83% at 15 → ~89% at 25) while the coin never does.

## 3 · What the dice can and cannot claim

- **The dice prove nothing by themselves.** Dice can replay any numbers. What proves the point is the **theorem**: no arrangement of the real machines in any definite order could have produced the SWITCH columns. The quantum computer did.
- **Scope of the wins.** F82 is a pre-registered game-form bound-beat against the full causally-separable class (including dynamical order), device-characterized — **not** loophole-free device-independent. F83 is a zero-capacity channel activation, control-null measured dead on-chip.
- **Every threshold is a measured number** rounded to a d100 — pre-registrations frozen before data, public job IDs, analysis code all auditable.

## 4 · Sources & provenance

- **Deck & rules:** `demo/casebook-pnp/index.html` (booklet v1, Whisper C4541, 2026-07-10) · deck data `demo/casebook-pnp-deck.json`
- **Game 1 (F82):** 0.9769 ± 0.0005 @ 216.8σ (ibm_marrakesh, job d9826lkqp3as739sd2lg), 0.9738 (ibm_fez); balanced-game ceiling 0.9098 / 91% theorem (Araújo et al. 2015). Corroborated: `docs/campaign-arcs.md` F82 row.
- **Game 2 (F83):** 0.0436 bits/use @ 55.6σ (ibm_marrakesh, job d983ek52su3c739ip92g), control 0.00012 bits. Corroborated: `docs/campaign-arcs.md` F83 row.
- **Hardware:** IBM 156-qubit Heron processors · pre-registered, frozen-rule-graded, July 2026.

---

*Rendered from [`demo/casebook-pnp/spec.html`](spec.html) — the interactive exhibit is at [`demo/casebook-pnp/`](index.html). Part of [The Quantum Museum](../).*
