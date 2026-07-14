# The Shallow-Circuit Solver Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4701 · **For**: `demo/shallow-solver/` (Wing IV) — **the museum's final card**
**Finding**: F113 (Exp127hw) — a constant-depth quantum circuit solves the n=4 2D-HLF at P(valid)=0.9017 (437.8σ over 0.25), covering all four valid answers near-uniformly (the un-fakeable coverage gate). Hardness inherited from contextuality (F106).
**Upstream**: `demo/shallow-solver/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.
> **Wing IV accent = cyan.** valid/solve=good, invalid=ink-3, cheat=amber/bad. **Design out both label-bug classes.**
> **HONESTY FENCE stated FIRST** (asymptotic separation, not proven on-chip) — the finding demands it up front.

## 1. Goal & the "aha"
Bravyi–Gosset–König: a QUANTUM constant-depth circuit solves a problem NO classical constant-depth circuit can —
UNCONDITIONALLY (no P≠NP assumption). "Constant depth" = fixed layers regardless of problem size. The 2D-HLF has MANY
valid answers (a coset); the un-fakeable test is COVERAGE (spread answers across the whole coset — a one-answer mimic
scores 100% on validity but fails coverage). On silicon at n=4: 90% valid, all four covered near-uniformly.

## 2. Data — verified first (results/exp127hw_hw_results.json, job d9amnlvu62qs738o8nt0)
- **P(valid) = 0.9017 ± 0.0015 = 437.8σ** over the uniform floor **0.25** (4 valid z of 16 possible).
- 4 valid z: 0001→0.2237, 1000→0.2229, 0110→0.2308, 1111→0.2243. min 0.2229 (W3 coverage). invalid aggregate 0.0983.
- hw depth 23, 10 routed CZ, O(1) logical depth. Gates W1_SOLVER/W2_MAJORITY/W3_COVERAGE/G_SENT PASS. band [0.82,0.93] hit at top. sentinels 0.985/0.957.
- Hardness inherited from contextuality: BGKT-2020 embeds the magic square (F106, 196σ). Complement to F54 deep-circuit wall.

## 3. The exhibit — panels
**A — Two tests, three strategies (interactive).** A strategy toggle: **Quantum solver · Random guess · One-answer
cheat**. A bar chart over the 4 valid z (+ an "invalid (12 others)" bar). Two gate readouts: **W1 P(valid)** vs floor
0.25, and **W3 coverage** (min over the 4 valid z). PASS/FAIL badges per gate. The teaching: Quantum passes BOTH
(0.90 / min 0.223); Random FAILS W1 (0.25 = floor); the one-answer cheat PASSES W1 (1.0) but FAILS W3 (min 0 — misses 3
of 4). Only the real solver passes both — coverage is un-fakeable.

**B — Constant depth.** The "shallow" story: a fixed few layers (O(1) logical depth, hw depth 23, 10 CZ) regardless of
problem size, vs the classical impossibility (asymptotic). The 437.8σ headline. The honesty fence restated (asymptotic,
not on-chip; fidelity not a beaten bound).

**C — The through-line + receipts.** (1) coverage un-fakeable (cheat fails W3); (2) hardness INHERITED FROM
CONTEXTUALITY — BGKT embeds the magic square F106 (link the Magic Square exhibit) — the campaign's through-line;
(3) unconditional (no P≠NP). Scope + Full Spec link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | Over-claiming a proven complexity separation on-chip. | HONESTY FENCE stated FIRST (hero, before the interactive): asymptotic separation, theorem carries the limit; n=4 = fidelity demo. Repeat in Panel B + spec §Scope. |
| G2 | "Constant depth / QNC⁰ / NC⁰" is jargon. | Primer: depth = layers; constant = fixed regardless of size; the quantum circuit beats classical WITHOUT assuming P≠NP (unconditional). |
| G3 | "P(valid) 90%" alone looks fakeable. | Make COVERAGE the centerpiece: the one-answer cheat scores 100% validity but fails coverage. The interactive proves why coverage is the real gate. |
| G4 | Floor 0.25 unexplained. | State it: 4 valid answers of 16 possible outputs = 4/16 = 0.25 random. |
| G5 | The contextuality through-line is the jewel and easy to drop. | Panel C receipt 2 + spec §5: the classical hardness IS the magic-square contextuality (F106); link the exhibit. Same fact seen twice. |
| G6 | a11y / mobile / motion / self-contained. | Strategy buttons (aria-pressed); P/coverage in text + colour + PASS/FAIL word; bars have value labels in HTML; stack <680px; bar transitions honour reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What's a constant-depth circuit?" + "Why is coverage the real test?" primer cards after the fence. |
| G8 | Spec discoverability. | Cyan "◇ Full Spec Sheet" button in hero + Panel C + footer. |
| G9 | Label-bug classes (both). | Value labels in HTML; centered SVG text; data-vs-threshold on opposite sides. Verify in render pass. |

## 5. Pre-dev structure
1. **Data kernel**: VALID_Z [{bits,p}] + INVALID_AGG + FLOOR 0.25 + strategies {quantum, random, cheat} each with per-z dist + W1/W3 pass; assert quantum passes both, cheat W1-pass/W3-fail, random W1-fail.
2. Panel A: strategy toggle + bar chart + two gate readouts. 3. Panel B: constant-depth visual + headline + fence.
4. Panel C: receipts + magic-square link + spec. 5. Chrome (museum.css, cyan; valid=good, cheat=amber). 6. Passes (both label classes out).

## 6. Acceptance
Strategy toggle switches the bar chart + gate readouts; Quantum PASS/PASS, Random FAIL-W1, Cheat PASS-W1/FAIL-W3;
coverage framed as un-fakeable; honesty fence prominent (hero + Panel B); Panel C carries contextuality through-line +
links the Magic Square + spec; keyboard-operable, colour-not-alone, mobile-stack, no external requests, theme-aware; NO
label overflow/collision. Then: Playwright render (0 console, 0 external, toggle varies chart+gates, light+dark) → UI
improvement pass. **Completing the museum: 22 live / 0 in dev — every finding walkable.**
