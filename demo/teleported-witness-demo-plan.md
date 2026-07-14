# The Teleported Witness Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4696 · **For**: `demo/teleported-witness/` (Wing I)
**Finding**: F92 (Exp113) — the control qubit carrying indefinite causal order is teleported one hop and still certifies over a QUANTUM channel (DISC 1.825, 90σ), but the identical teleport over a CLASSICAL channel kills it (0.0175 ≈ 0). Survives quantum, dies classical — transmission by entanglement.
**Upstream**: `demo/teleported-witness/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.
> **Wing I accent = cyan** (the switch signature), NOT the Wing III violet. good=survives, bad=dies.

## 1. Goal & the "aha"
Indefinite causal order is a physical resource carried by one control qubit. Teleport that qubit one hop across the
chip before reading its witness. Over a real ENTANGLED (quantum) channel it arrives intact — 97% of the un-teleported
value, 90σ. Over a DEPHASED (classical) channel — same protocol — the witness reads ~0: dead. The contrast IS the
finding: indefiniteness rides on the entanglement, not on "surviving noise." Pick a channel, watch the witness live or die.

## 2. Data — verified first (results/exp113_grade.json, job d9a36352su3c739l3kf0)
DISC = ⟨X⟩_comm − ⟨X⟩_anti; 0 = classical/definite, 2 = noiseless indefinite max, WIN bar = 1.0.
| channel | DISC | vs bar 1.0 | % of direct | survives |
|---|---|---|---|---|
| direct (no teleport) | 1.8805 ± 0.008 | +116σ | 100% | anchor |
| tele · **quantum** | **1.8250 ± 0.009** | **+90σ** | **97.0%** | ✓ survives |
| tele · quantum + feedforward | 1.7660 ± 0.010 | +73σ | 93.9% | ✓ survives |
| tele · **classical** (dephased) | **0.0175 ± 0.022** | dead | 0.9% | ✗ dies |
- Channel separation (quantum − classical) = 1.8075 ± 0.024 → 33σ over the 1.0 bar. W1 WIN, W2 WIN.
- G3 null integrity: classical channel genuinely dead (|0.0175|+5·SE = 0.13 < 0.15 bar), not leaky.
- Feedforward cost (honest, ungated): tele_active 1.766 < tele_frame 1.825 (model previewed the opposite → corrected). All 4 preds hit.

## 3. The exhibit — panels
**A — Teleport the witness (interactive).** A channel selector: **direct · quantum · quantum+feedforward · classical**.
A small teleport schematic — control qubit at node A, a channel LINK to node B, witness readout at B — where the link
is drawn as a live entangled bond (quantum: glowing cyan) or a broken/greyed bond (classical: dashed/dead). A witness
gauge (DISC 0→2, WIN bar at 1.0, classical value at 0) fills to the DISC value; survival % (of direct) + survives/dies verdict.

**B — The channel scoreboard (chart).** DISC scale 0→2 with the 0 (classical), 1.0 (WIN bar), 2.0 (noiseless max)
marks; the three quantum channels clustered high (survive) + the classical channel at ~0 (dead); σ callouts (90σ, 33σ separation).

**C — Receipts.** (1) the classical null was EXECUTED same-job/same-window — that's what makes it "transmission by
entanglement," not "survived noise"; (2) all 4 pre-filed predictions hit, incl. the feedforward cost the model got
backwards; (3) first flight under the R5 grader-selftest rule (grader proved itself on synthetic data before touching
hardware). Prominent Full Spec link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Causal witness / DISC" is opaque. | Primer: DISC = one number; 0 = ordinary order (or coin-flip), 2 = fully indefinite. Gauge labels the 0 end "classical/definite" and 2 end "indefinite". |
| G2 | Teleportation reads as sci-fi / FTL. | Primer + scope: standard teleportation (Bell pair + 2 classical bits), no FTL; the novelty is WHAT is teleported. |
| G3 | "Survived teleportation" alone is unfalsifiable (could be noise). | Lead the contrast: the classical channel (same protocol) reads ~0. The gauge/verdict for classical says DEAD; Panel C receipt 1 names why the executed null matters. |
| G4 | The channel link visual could imply data flowing, not a resource. | Draw the link as an ENTANGLED BOND (quantum = intact glowing; classical = broken/dephased), and label it "entangled resource" vs "dephased resource" — the resource is the thing that lives or dies. |
| G5 | Feedforward cost (tele_active<tele_frame) easy to drop; it's an honesty jewel. | Keep it as its own channel in the gauge + a receipt noting the model previewed the opposite. |
| G6 | a11y / mobile / motion / self-contained. | Selector buttons (aria-pressed); DISC + % in text + colour + survives/dies word; link state in text ("entangled"/"dephased"); stack <680px; gauge/link transitions honour reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What's a causal witness?" + "What's teleportation here?" primer cards after the lede. |
| G8 | Spec discoverability. | Cyan "◇ Full Spec Sheet" button in hero + Panel C + footer. |

## 5. Pre-dev structure
1. **Data kernel**: CHAN `{key,label,disc,se,sigma,pct,alive,link,note}` + BAR 1.0 + MAX 2.0; assert quantum survive >1, classical dead <0.15, separation 33σ.
2. Panel A: selector + teleport schematic (A—link→B) + DISC gauge (bar+max). 3. Panel B: static scoreboard.
4. Panel C: receipts + spec links. 5. Chrome (museum.css, CYAN wing accent; good=survive, bad=dead). 6. Passes.

## 6. Acceptance
Selector cycles 4 channels; the link glows (quantum) or breaks (classical); DISC gauge fills to 1.88/1.83/1.77/0.02
with WIN bar at 1.0; survival % + survives/dies verdict correct; Panel B scoreboard has 0/1.0/2.0 marks + 4 channels +
σ; Panel C carries executed-null + 4-preds-hit + R5-selftest and links the spec; keyboard-operable, colour-not-alone,
mobile-stack, no external requests, theme-aware. Then: Playwright render (0 console errors, 0 external requests,
selector varies readouts, light+dark) → UI improvement pass.
