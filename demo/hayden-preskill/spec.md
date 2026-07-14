# A message the mirror returns phase-flipped

`Finding F99`  ·  `Experiment Exp121 (Hayden–Preskill × ICO)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9aabnt2su3c739lcam0`  ·  `Telescope byte-identical to F98`

> **✓ VERDICT — HERALDED-MIRROR-CERTIFIED (+ plus branch) · 56σ & 59σ**

This sheet is the source-of-truth specification behind the interactive exhibit. Every number is drawn from the frozen grade file `results/exp121_grade.json` and its job record `results/exp121_jobids.json`. It runs on the **same certified telescope as F98** (Quantum Darwinism) — byte-identical skeleton, site, and window — so the two findings share one calibrated apparatus.

## 1 · The idea, in plain language

**Hayden–Preskill (2007).** Throw a message into a scrambler — the theorists' toy model of a black hole — and it looks instantly lost. But if you hold the right **entangled reference** to the scrambler, the message comes **back out** in the radiation almost immediately. Information isn't destroyed; it's smeared across correlations you can un-smear with the reference.

Here the message is a **one-bit diary**. We interrogate the scrambled state with two **incompatible horizon-queries** — a Z-question and an X-question — and try to read the diary back from a small **probe** alone. Under any **definite order** of the two queries, the diary is **provably dead** in the probe: the probe is a coin-flip. The twist is to put the **order of the two queries in superposition** (a quantum switch) and ask what the probe knows then.

> **The measured quantity**
> `S_P = P(probe reads the diary correctly) − ½`. So `S_P = 0` is a coin-flip (**dead**, no recovery); `S_P = +½` is a perfect direct read; `S_P = −½` is a perfect mirror — the probe is **anti-correlated**, reading the diary exactly **flipped**. Recovery is `½ + |S_P|`; the **sign** tells you whether to read the probe straight or invert it.

## 2 · Dead in every definite order (the premise)

Before claiming recovery we prove there is nothing to recover under ordinary causality. Both definite query orders leave the probe blank:

> **Premise — the diary is dead (F83 NO-TEST discipline)**
> `S_P(X-then-Z) = 0.0026`, `S_P(Z-then-X) = 0.0065` — both a coin-flip, ~40× below the effect and well inside the frozen **±0.05 premise band**. If a definite order could read the diary, there would be no claim to make. It can't.

## 3 · Pre-registered gates (frozen before flight)

- **PREMISE** — `|S_P(definite)| < 0.05` both orders — diary dead. PASS (0.0026, 0.0065).
- **N1 / H1** — Herald registers indefinite order; minus-branch rate near theory 0.25. PASS (0.284).
- **W_MIRROR** — **headline, sign theory-fixed:** `S_P(minus) + 5·SE < −0.05` — recovery must appear as a **negative** (phase-flipped) excursion. PASS (−0.238, 56σ).
- **W_PLUS** — `S_P(plus) − 5·SE > +0.05` — a positive (direct) recovery on the plus branch. PASS (+0.182, 59σ).

**Why the sign matters.** W_MIRROR is **sign-fixed**: theory predicts the minus branch returns the diary **anti-correlated** (S_P = −½). A positive excursion of the same size would **fail** the gate. The phase flip isn't a nuisance sign — it **is** the predicted signature, and the hardware produced exactly it.

## 4 · The measured data

60,000 shots per definite arm; switch branches split by the heralded control (+ = 71.6%, − = 28.4%). "Recovery" = `½ + |S_P|`, with the arrow showing read-direct vs read-flipped.

| arm | S_P | vs ±0.05 band | recovery | theory S_P |
| --- | --- | --- | --- | --- |
| X-then-Z (definite) | 0.0026 | inside — dead | ~50% (coin-flip) | 0 |
| Z-then-X (definite) | 0.0065 | inside — dead | ~50% (coin-flip) | 0 |
| switch → + branch (72%) | **+0.182 ± 0.002** | **+59σ** | **68% · read direct →** | +1/6 |
| switch → − branch (28%) | **−0.238 ± 0.003** | **−56σ** | **74% · flip the bits ⇄** | −1/2 |

## 5 · The bonus that rides free — who gets to know?

The same run measures a second quantity for nothing: `S_E2`, whether the **environment** (a second recorder at the horizon) learns the diary. It depends entirely on **which query is asked first**:

> **S_E2 — the environment's knowledge is order-dependent**
> **X-first:** `S_E2 = 0.453` (theory 0.5) — the environment learns it. **Z-first:** `S_E2 = 0.007` (theory 0.0) — the environment learns **nothing**. Ask the wrong question first and **nobody** — not the probe, not the environment — gets to know. Causal order decides who holds the fact.

## 6 · Scope & caveats

- **Analog, not a black hole.** This is the Hayden–Preskill **scrambler model** on a chip, not a literal event horizon. The claim is about information recovery in the model's information structure.
- **Heralded / post-selected.** The mirror lives on the **minus branch** (28% of runs), selected by the switch-control herald. The herald is measured independently of the diary read, so it is a genuine selection, not a fit.
- **Recovery is partial, and reported as such.** `S_P(minus) = −0.238` is 48% of the ideal −½ — the probe disagrees with the diary **74%** of the time, so flipping recovers 74%, not 100%. The certified result is the sign-fixed excursion past the band (56σ); the depth-vs-theory is reported.
- **Resource-scoped & same telescope as F98.** This is the same certified apparatus that carried the Darwinism hull; the loophole discipline (F82/F83 lineage) is inherited.

## 7 · Provenance

- **Grade file:** `results/exp121_grade.json` · **Job record:** `results/exp121_jobids.json` · **Job:** d9aabnt2su3c739lcam0
- **Pre-registration:** `experiments/exp121-hp-switch-preregistration.md` · **Band:** ±0.05 (frozen) · **Ideals:** S_P = +1/6 (plus), −1/2 (minus)
- **Backend:** ibm_marrakesh (Heron r2) · **Shots:** 60,000/definite arm
- **Sibling telescope:** F98 (the objectivity hull) — byte-identical skeleton, site, window
- **Family:** Horizons-2 Q3 · lineage F82/F83 (loophole & NO-TEST discipline)

---

*Rendered from [`demo/hayden-preskill/spec.html`](spec.html) — the interactive exhibit is at [`demo/hayden-preskill/`](index.html). Part of [The Quantum Museum](../).*
