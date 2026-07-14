# The Magic Square Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4687 (2026-07-14) · **For**: `demo/magic-square/` (Wing II)
**Finding**: F106 (Exp126) — the Peres–Mermin pseudo-telepathy game, measured on `ibm_marrakesh`.

---

## 1. Goal & the "aha"

Let the visitor **feel the classical impossibility** — try to fill a 3×3 square of ±1 obeying
six simple rules, and fail, always, at 5 of 6 — then watch a **real quantum computer win all
nine contexts** where no classical player can beat 8/9. The exhibit's whole job is to make one
abstract sentence ("contextuality: no consistent value-assignment exists") into something you
bump into with your own hands, and then to show the measured escape.

## 2. Data — verified before design (never invent a number)

**Puzzle math** (parity convention: rows → +1 all; columns → +1, +1, −1 — matches Exp126),
verified by exhaustive enumeration in-repo (C4687):
- Fill-the-table puzzle: **max 5 of 6** rules satisfiable; **0 of 512** tables satisfy all six.
- Game ceiling: **best classical = 8/9 = 0.8889**, over **4096** strategy pairs.
Both will be **re-enumerated live in the browser** (the museum "we checked it" ethos), not asserted.

**Measured hardware** (`results/exp126_hw_results.json`, job `d9akl8fu62qs738o68pg`, ibm_marrakesh):
- Pooled quantum win **0.9690** (196σ over 8/9); min context r3c3 **0.9482** (37.8σ).
- No-entanglement null **0.6570** (a quantum machine *without* the shared pairs also can't do it).
- Per-context 3×3 (the heatmap), row-major:
  `0.9833 0.9832 0.9497 / 0.9823 0.9849 0.9527 / 0.9640 0.9726 0.9482`.

## 3. The exhibit — two panels

**Panel A — The Impossible Square** *(the classical wall)*
- Interactive 3×3 grid; each cell a **button** toggling +1/−1 (shown as `+`/`−`, green/red **and** the glyph, never colour alone).
- Row targets on the right (`+ + +`), column targets on the bottom (`+ + −`). Each rule indicator shows ✓/✗ live.
- Live counter: **rules satisfied N/6**. The visitor discovers 6/6 is unreachable; best is 5/6.
- Standing hint: *"The whole grid multiplies to +1 across the rows but −1 down the columns — a contradiction. One rule always breaks."*
- **"Prove the ceiling"** button → enumerates in-browser: reports *"0 of 512 squares satisfy all six; the best classical strategy wins 8 of 9 games (checked all 4096 pairs)."* → sets the headline **CLASSICAL CEILING 8/9 = 88.9%**.

**Panel B — The Quantum Key** *(measured)*
- The Pauli operator square (`XI IX XX / IZ ZI ZZ / XZ ZX YY`) with one lay sentence: *"Swap the ±1 numbers for these quantum measurements. Within any row or column they're compatible and multiply to the required sign — so all six rules hold at once. Alice and Bob share entangled pairs."*
- **"Run it on the quantum computer"** → reveals the measured 3×3 **heatmap** (per-context wins, all lit above 8/9), animating in.
- Readouts: **quantum 96.9%** vs the **88.9% wall** — **196σ** past it; and the **65.7% null** (no entanglement ⇒ no win, even on the quantum machine).
- Measured-data badge: F106 · job `d9akl8fu62qs738o68pg` · 8/9 enumerated over 4096 pairs · ibm_marrakesh.

**Frame** (top): *"The Magic Square — a pen-and-paper puzzle with no solution, and the quantum computer that solves it anyway."* Scope chip: *"Pseudo-telepathy is textbook (Mermin–Peres); the contribution is the frozen-court, enumerated-bound measurement."*

## 4. Gap review — v1 → v2 (revisions folded in above)

| # | Gap found reviewing v1 | Fix (in the plan above) |
|---|---|---|
| G1 | **Two different numbers** — the puzzle's "5/6 rules" vs the game's "8/9 win" risk being conflated. | Keep them distinct and both true: the puzzle counter is `N/6 rules`; the **ceiling is 8/9 (the game)**, stated separately with a one-line bridge. Both re-enumerated live. |
| G2 | The "why quantum wins" could over-claim a proof. | One accurate lay sentence (compatible-within-row/col, multiply to the sign) — an *idea*, not a proof; the operator grid carries the rigor. |
| G3 | **Colour-alone** satisfied/violated (a11y). | Every state carries a glyph (`+`/`−`, ✓/✗) *and* colour; cells are real `<button>`s (focusable, Enter/Space toggles), aria-labels. |
| G4 | Grid → data mapping error risk. | Per-context array is embedded **row-major with an explicit r,c index**; the heatmap cell reads `data[r][c]` — asserted against the known min at r3c3=0.9482. |
| G5 | Ceiling claim not self-evidently true. | The browser **enumerates it live** (512 tables + 4096 pairs), matching Exp126's in-artifact-bound discipline; no asserted magic numbers. |
| G6 | Mobile: two 3×3 grids + margins. | Panels stack < 680px; grids use `aspect-ratio` cells and `min()` sizing; margin targets wrap. |
| G7 | Scope/honesty. | Scope chip (textbook prior art + our contribution); every displayed number is measured or live-enumerated. |

## 5. Pre-dev structure (build order)

1. **Correctness kernel first** — the parity check + the two in-browser enumerators (512 tables, 4096 pairs), unit-sanity: max=5, solvable=0, ceiling=8/9. Build these before any UI so the numbers are trusted.
2. **Panel A UI** on top of the kernel (grid buttons, rule indicators, counter, prove-button).
3. **Panel B** (static operator grid + measured heatmap + readouts, revealed on click).
4. **Chrome** — top bar, hero, scope chip, footer badge, theme toggle; shared `../museum.css` (Wing II accent).
5. **Passes** — a11y (keyboard/aria/glyphs), mobile (stack + wrap), reduced-motion, self-contained (0 external refs), and a final render-and-look.

## 6. Acceptance criteria

- Every number on screen is measured (F106) or **enumerated live in-browser** — nothing hard-coded that isn't also derivable on the page.
- Panel A: a user can reach 5/6 but never 6/6; the prove-button reports 8/9 / 4096.
- Panel B: heatmap matches `exp126_hw_results.json` (min cell r3c3 = 0.9482); readouts 96.9 / 88.9 / 65.7.
- Keyboard-operable, colour-not-alone, stacks on mobile, no external requests, theme-aware.
