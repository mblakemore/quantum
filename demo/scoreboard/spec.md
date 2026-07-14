# Have we found quantum advantage? The five-scoreboard answer

`Nature Campaign summary (5 scoreboards)`  ·  `Hardware IBM Heron · 2026 campaign`  ·  `Experiments ~110 · F01–F117`  ·  `Every number a job ID`

> **◇ FOUND ON FOUR OF FIVE · theorem ceilings cleared 21σ to 341σ**

Full Specification Sheet · Methodology & Sources

This is the methodology sheet behind the visual scoreboard. The exhibit answers one question — **have we found quantum advantage?** — across **five scoreboards**, each cleared against an **exact theorem ceiling**, and it states plainly what is **not** claimed. Every σ below is transcribed verbatim from the exhibit (the tiles and the enumerated `rows` array); nothing is invented. Sources in §5.

## 1 · The verdict, in one line

**Yes — measurably, on four of five scoreboards**, against exact theorem ceilings cleared by **21σ to 341σ**. On the fifth — computational — the wall against a brute-force speedup is **measured** (F54), and the constant-depth solver that the only depth-separation theorem is built on now **runs on silicon at 90%**. No shortcut is claimed that the hardware does not hold.

## 2 · The five scoreboards

- **Games & correlations — FOUND.** 216.8σ causal-order game; the three great no-go theorems in one court — Bell, indefinite causal order, contextuality (8/9 at 196σ). `F82 · F106`
- **Communication & sensing — FOUND.** 341σ superdense coding; a ladder including 2→1 QRAC (110σ) and GHZ metrology beating the standard quantum limit (168σ). `F87 · F107 · F108/9`
- **Thermodynamics — FOUND.** 21.1σ ICO refrigeration: population inversion from passive baths, a full cycle, negative local energy. `F86 · F94/5 · F97`
- **Information — FOUND.** 42σ negative conditional entropy S(B|A)<0 — a sign classical physics forbids — plus zero-capacity transmission. `F103 · F105`
- **Computational — WALL + BRIDGE.** No brute-force speedup (F54's wall), but the constant-depth 2D-HLF solver runs at **0.90** (438σ over chance) and persists to n=9. `F113 · F114`

## 3 · The theorem ceilings — clearance over the classical / theorem bound

Each headline clears an exact, pre-registered bound. The flagship σ values, transcribed from the exhibit's enumerated table with the null each is measured against:

| scoreboard headline | clearance | over the bound |
| --- | --- | --- |
| Superdense coding | 341σ | over 0.5 (unassisted) |
| Causal-order game | 216.8σ | over 0.8695 (SDP) |
| Magic-square contextuality | 196σ | over 8/9 (enumerated) |
| GHZ metrology | 168σ | over executed SQL |
| One-sided-DI steering | 96σ | over LHS bound 1 |
| Capacity activation | 55.6σ | over 0 |
| Negative conditional entropy | 42σ | S(B|A) < 0 |
| ICO refrigeration | 21.1σ | over 0 |

> **The through-line**
> The classical hardness of the **computational** problem (`F113`) **is** the magic-square **contextuality** (`F106`), certified at 196σ — the correlation advantage and the computational advantage are the **same resource**.

## 4 · What is NOT claimed

The boundary column — each an explicit limit printed on the exhibit:

## 5 · Sources & provenance

- **Exhibit:** `demo/scoreboard/index.html` — the five tiles, the log-scale σ bars, the through-line, and the "what is not claimed" list. All σ values on this sheet are transcribed from it (tiles + `rows` array).
- **Campaign ledger:** `docs/campaign-arcs.md` (F01–F117) — per-finding rows corroborate each headline: F82 (216.8σ), F106 (196σ), F87 (341σ), F108 (168σ), F83 (55.6σ), F86 (21.1σ), F113/F114 (438σ / n=9), F117 (0.65 bit/use, one-sided-DI).
- **Scope of the whole board:** ~110 experiments · 2 Heron chips + a foreign-device exam · 2 standing tools (SDP-randomness, QPU-weather). Every number traces to a pre-registered job with a public ID.
- **Full argument:** `docs/quantum-advantage-the-complete-answer-whisper-c4682.md`.

---

*Rendered from [`demo/scoreboard/spec.html`](spec.html) — the interactive exhibit is at [`demo/scoreboard/`](index.html). Part of [The Quantum Museum](../).*
