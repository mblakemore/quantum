# The Quantum Darwinism Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4694 · **For**: `demo/quantum-darwinism/` (Wing III)
**Finding**: F98 (Exp120) — objectivity is redundant environmental copies; complementarity boxes two incompatible facts into a hull; a superposed causal order breaks the hull on BOTH branches (facts without a causal history, and record erasure).
**Upstream**: `demo/quantum-darwinism/spec.html` — the Full Spec Sheet, linked prominently from the exhibit.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.

## 1. Goal & the "aha"
A fact is objective when the environment holds many faithful copies of it. Complementarity forbids faithful copies of
two incompatible facts (Z & X) at once — so under any definite recorder order, joint objectivity w = A_Z + A_X is boxed
into a narrow **hull** and it's winner-take-all (last recorder wins, the other is erased to a coin-flip). Put the order
in **superposition** and the box breaks: the + branch smashes **through the ceiling** (both facts ~0.80 objective at
once — impossible), the − branch drops **through the floor** (both erased). Pick an order and watch w leave the hull.

## 2. Data — verified first (results/exp120_grade.json, job d9aa5m8tcv6s73do7li0)
| arm | A_Z | A_X | w | vs hull |
|---|---|---|---|---|
| Z-then-X (definite) | 0.506 | 0.955 | 1.4614 | hull floor |
| X-then-Z (definite) | 0.986 | 0.501 | 1.4871 | hull ceiling |
| switch → **+** (72%) | 0.817 | 0.778 | **1.5957 ± 0.0039** | **+0.109 · 22σ** |
| switch → **−** (28%) | 0.553 | 0.477 | **1.0296 ± 0.0076** | **−0.432 · 52σ** |
- **Hull = [1.4614, 1.4871]** (measured, same window). Theory: w+=1.667, w−=1.0, hull=1.5, minus_rate=0.25. 63 two-qubit gates. Verdict **DARWINISM-HULL-VIOLATED(both-branches)**.

## 3. The exhibit — panels
**A — Break the hull (interactive).** A recorder-order selector: **Z-then-X · X-then-Z · Superposed → + · Superposed → −**.
Two "recorder" gauges (Z-fact cyan, X-fact amber) show each copy's faithfulness A, with an OBJECTIVE / ERASED state.
A **w-scale** (number line ~1.0→1.7) with the **hull band [1.461, 1.487]** shaded ("all any definite order can reach")
and a live marker: definite orders sit inside the band; + breaks above (green); − drops below (red). Verdict line per mode.

**B — The objectivity hull (chart).** The definitive annotated w number-line: hull band, both definite-order dots on
its edges, the + marker at 1.596 (22σ, above), the − marker at 1.030 (52σ, below), theory ghosts at 1.667 / 1.0. One glance = both violations.

**C — "How we trust a 63-gate result" (receipts).** (1) definite orders obey winner-take-all EXACTLY (0.955/0.986) —
the apparatus is calibrated; (2) the hull is MEASURED same-window, not assumed; (3) the intermediate-basis cheat
disclosed & excluded (F82 lineage). Prominent Full Spec Sheet link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Objectivity / faithfulness" is jargon. | Primer cards after lede: objectivity = many redundant copies; A=1 perfect copy, A=0.5 coin-flip. Gauges labelled "objective record" vs "erased (coin-flip)". |
| G2 | The hull is the whole point and easy to miss. | Make the shaded hull band the visual anchor of BOTH the live w-scale (A) and the chart (B); label it "everything a causal order can reach". |
| G3 | "Above the cap" could read as just a bigger number, not impossibility. | Frame + as "both facts objective at once — no ordering can do this"; − as "both erased". Colour the two violations good/bad, definite orders neutral. |
| G4 | Over-claiming ("facts are subjective!" / universal bound). | Scope pill + spec §6: RESOURCE-scoped (these two recorders), analog, cheat excluded. w-scale labelled "these two recorders, this window". |
| G5 | Deep-circuit skepticism (63 gates — why believe it?). | Receipt 1: definite orders reproduce winner-take-all to 0.955/0.986 and hardware matched the noise model to 3rd decimal → the apparatus is trustworthy. |
| G6 | a11y / mobile / motion / self-contained. | Selector = buttons (aria-pressed); A values in text + colour + state word; w-marker position in text; panels stack <680px; marker transition honours reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "Why is anything a fact?" + "What's the catch?" primer cards after the lede. |
| G8 | Spec discoverability. | Violet "◇ Full Spec Sheet" button in hero + repeat in Panel C + footer. |

## 5. Pre-dev structure
1. **Data kernel**: MODES array `{key,label,az,ax,w,se,rel,state}` + HULL `{min,max}` + THEORY; assert w±, hull edges, 22σ/52σ.
2. Panel A: selector + two gauges + w-scale (shared hull band). 3. Panel B: annotated hull number-line. 4. Panel C receipts + spec links.
5. Chrome (museum.css, violet wing accent; cyan=Z, amber=X, good=+above, bad=−below). 6. Passes.

## 6. Acceptance
Selector cycles 4 modes; gauges show table A-values + OBJECTIVE/ERASED; w-marker moves inside band (definite), above
(+ green, 22σ), below (− red, 52σ); Panel B shows hull band + 4 points + theory ghosts + σ; Panel C carries
winner-take-all + measured-hull + cheat-excluded and links the spec; keyboard-operable, colour-not-alone, mobile-stack,
no external requests, theme-aware. Then: Playwright render (0 console errors, 0 external requests, selector varies
readouts, light+dark) → UI improvement pass.
