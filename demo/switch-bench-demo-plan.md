# The Switch-Bench Readout Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4700 · **For**: `demo/switch-bench/` (Wing V) — **the museum's final card**
**Finding**: F112 (Exp133) — a 3-axis instrument for causal-order physics (CAUSAL/SCHEDULE/HOLD) flown intact on a foreign chip (ibm_kingston), certifying every axis against the same frozen bounds with no retuning, and ranking devices on axes QV/CLOPS/EPLG don't touch.
**Upstream**: `demo/switch-bench/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.
> **Wing V accent = cyan (chrome).** three axes: CAUSAL=cyan, SCHEDULE=violet, HOLD=amber. device: home(marrakesh)=ghost/ring, foreign(kingston)=filled.
> **Design out BOTH label-bug classes** (right-edge overflow; data-value-near-threshold collision).

## 1. Goal & the "aha"
Vendor metrics (QV/CLOPS/EPLG) don't tell you if a chip can do causal-order PHYSICS. The switch-bench does — 3 axes,
frozen bounds. The test: fly the whole bench on a chip it's NEVER seen (kingston) and grade against the SAME bounds, no
retuning. It certifies all three — so the physics is a property of the hardware GENERATION (Heron), not one lucky die.
It even RANKS the two chips (kingston edges home on the causal numbers). Flip the device and watch the bench travel.

## 2. Data — verified first (bench cards; kingston d9amd73…, marrakesh d9a7mn2… + Zeno d9ai9ku…)
| axis · metric | ideal | marrakesh (home) | kingston (foreign) | bound |
|---|---|---|---|---|
| CAUSAL · witness W | 2.000 | 1.9265 | **1.9533 ± 0.022 ▲** | ≫ 0 (null) |
| CAUSAL · capacity R̄ | 0.5333 | 0.4978 | **0.5245 ± 0.009 ▲** | ≫ 0.0008 null |
| SCHEDULE · D_order | 0 | symmetric | **0.0130 ± 0.003** | ≤ 0.0223 |
| HOLD · tractor sep | ~0.73 | 0.624 | **0.6487 ± 0.003 ▲** | > 0.30 |
| HOLD · QND q | 1.000 | 0.987 | 0.9847 | ≈ tie |
- Kingston: full bench in ONE job (77 pubs, 208k shots). Verdicts PASS-CAUSAL / ORDER-SYMMETRIC / HOLD-CERTIFIED.
- ▲ = kingston edges home. Edges on W, R̄, hold-sep; ties QND + schedule-symmetry. Scope: same Heron generation; cross-gen (Eagle) NOT claimed.

## 3. The exhibit — panels
**A — The bench travels (interactive).** A device toggle: **marrakesh (home)** / **kingston (foreign · never seen)**.
Three axis gauges — CAUSAL (W), SCHEDULE (D_order, ceiling-type), HOLD (sep) — each showing the selected device's value
vs its frozen bound + ideal, with a PASS/CERTIFIED badge. Flip to kingston: all three still certify (against the SAME
bounds). A verdict line: "the full bench, on a chip it had never seen, certifies all three — no retuning."

**B — The device leaderboard.** kingston vs marrakesh across the axes (W, R̄, hold-sep, QND), kingston edges on
causal+hold, ties QND. Message: the bench RANKS devices on axes QV/CLOPS/EPLG don't measure — and the foreign chip wins.

**C — Receipts + the three axes.** (1) same frozen bounds, no retuning (identical grader on both chips); (2)
site-selection rules re-derived LIVE on kingston's unfamiliar map (deterministic, untouched); (3) device-independence =
generation property (both Heron), not one die. Links to the three axes' exhibits (Causal Switch, Zeno Tractor Beam) +
scope (cross-generation not claimed) + Full Spec.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Switch-bench / 3 axes" is abstract. | Primer: an instrument that measures causal-order PHYSICS (not generic quality); name the 3 axes in plain words + link each to its exhibit. |
| G2 | "Device-independence" is jargon. | Frame as "the bench travels": flew to a chip it had never seen, certified the same. Toggle makes it tangible. |
| G3 | Composite home reference (marrakesh axes from different jobs) could mislead. | Spec §6 + a note: kingston ran all 3 in ONE job; marrakesh is a composite home reference (causal card + Zeno run). Don't imply a single marrakesh job. |
| G4 | Over-claiming (universal device-independence / cross-generation). | Scope: same Heron GENERATION only; cross-generation (Eagle) NOT claimed; same-instrument not same-instant. |
| G5 | The "ranks devices" novelty easy to miss. | Panel B leaderboard: kingston edges on the causal numbers; explicit "axes QV/CLOPS/EPLG don't touch". |
| G6 | a11y / mobile / motion / self-contained. | Toggle + device buttons (aria-pressed); every value in text + colour + PASS word; gauge marks in text; stack <680px; transitions honour reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What's the switch-bench?" + "What does it mean for it to travel?" primer cards after the lede. |
| G8 | Spec discoverability. | Cyan "◇ Full Spec Sheet" button in hero + Panel C + footer. |
| G9 | Label-bug classes (both). | Value labels in HTML; SVG text centered; data-vs-threshold labels on opposite axis sides. Verify in render pass. |

## 5. Pre-dev structure
1. **Data kernel**: DEV {marrakesh, kingston} × AXES [{key,name,color,metric,val,se,bound,ideal,boundType,companion,verdict,exhibit}]; assert all certify both devices, kingston edges on causal+hold.
2. Panel A: device toggle + 3 axis gauges (bound + ideal marks, active marker). 3. Panel B: leaderboard bars.
4. Panel C: receipts + axis links + spec. 5. Chrome (museum.css, cyan; axis colors cyan/violet/amber). 6. Passes (both label classes designed out).

## 6. Acceptance
Device toggle switches all 3 gauges between marrakesh/kingston values; each shows value vs bound vs ideal + PASS badge;
kingston certifies all three against the same bounds; Panel B shows kingston edging on causal+hold, ties QND; Panel C
carries same-bounds + live-site-selection + generation-property and links the axes' exhibits + spec; keyboard-operable,
colour-not-alone, mobile-stack, no external requests, theme-aware; NO label overflow/collision. Then: Playwright render
(0 console, 0 external, toggle varies gauges, light+dark) → UI improvement pass. **Completing the museum: 21 live / 0 in dev.**
