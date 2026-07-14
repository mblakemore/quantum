# The Zeno Tractor Beam Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4692 · **For**: `demo/zeno-tractor/` (Wing III)
**Finding**: F102 (Exp124) — measurement pins a qubit against a full π-rotation; the QND-corrected cadence law + the watch-cost frontier.

## 1. Goal & the "aha"
A full π-rotation should flip a qubit from ON to OFF. But *watch* it often enough and it freezes in place —
measurement itself is a tractor beam. Turn up how often you look and the survival climbs… until the frontier,
where each glance costs enough that looking faster stops helping. Find the optimal grip.

## 2. Data — verified first (results/exp124_grade.json, job d9ai9ku6hjac73fefdeg)
- **Survival P(stays ON) by watch cadence N**: unwatched = **0.020**; N=2 → **0.246**; N=4 → **0.498**;
  N=8 → **0.644**; N=16 → **0.664**. Tractor separation (N=8 vs unwatched) = 0.624 = **92σ**. Zero two-qubit gates.
- **Per-look QND cost** q ≈ 0.986–0.989 (each measurement slightly degrades the qubit).
- **Ideal Zeno law** [cos²(π/2N)]^N: 0.250 / 0.531 / 0.733 / 0.857 (N=2/4/8/16). Divide the measured survival by
  q^N and it matches this law **to 0.5% through N=8**.
- **Watch-cost frontier at N=16**: raw survival barely rises (0.644 → 0.664) because q^N now falls as fast as the
  Zeno gain climbs — the optimal grip cadence, measured.

## 3. The exhibit — two panels
**A — The Tractor Beam (interactive).** A watch-cadence dial: **unwatched · N=2 · 4 · 8 · 16**. A survival gauge
(big %, and a bar showing the qubit held between ON at top and flipped OFF at bottom) plus a row of "look" ticks
= the N measurements. Unwatched → the drive flips it (2%). Watch faster → it's pinned higher (25 → 50 → 64%).
At N=16 the gauge barely moves above N=8 — the verdict names the **watch-cost frontier**.

**B — The Cadence Law & the Frontier.** Survival vs N: the ideal Zeno law [cos²(π/2N)]^N as a rising curve, the
four **measured** points on it, and the plateau where the per-look cost bends the real survival away from the ideal.
One line: watch faster, hold tighter — but each look costs, so there is an optimal cadence, and it's at N=16.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Survival" ambiguous. | State it: the qubit starts ON; a full π-drive would flip it OFF; survival = P(still ON). |
| G2 | The frontier can look like a plotting glitch. | Name it explicitly at N=16 (0.644 → 0.664) with the mechanism: q^N (per-look cost) now falls as fast as the Zeno gain climbs. |
| G3 | Law vs measurement conflation. | Ideal law [cos²(π/2N)]^N drawn as the curve (theory, labelled); the dots are measured; the gap between them is the QND cost. |
| G4 | Over-claiming "measurement beats physics". | Scope: it pins against **coherent** π-rotation, not against relaxation; textbook Zeno (Misra–Sudarshan), contribution = the QND-corrected law + the measured frontier. |
| G5 | a11y / mobile / motion. | Dial = buttons (aria-pressed); gauge value in text + colour; look-ticks have count text; panels stack < 680px; gauge transition honours reduced-motion. |
| G6 | Measured-only. | survival, q, tractor separation all measured; the law curve is the exact formula, labelled. |

## 5. Pre-dev structure
1. **Data kernel**: CAD array {N, surv, law} + unwatched; assert surv rises then plateaus, N=8 tractor=0.624.
2. Panel A gauge + dial on the kernel. 3. Panel B law plot. 4. Chrome (museum.css, violet — Wing III). 5. Passes.

## 6. Acceptance
Dial unwatched→16; gauge shows 0.020 / 0.246 / 0.498 / 0.644 / 0.664; N=16 verdict names the watch-cost frontier;
Panel B shows the ideal law curve, the four measured dots, and the plateau; keyboard-operable, colour-not-alone,
mobile-stack, no external requests, theme-aware.
