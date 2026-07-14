# The No-Go Triptych Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4698 · **For**: `demo/no-go-triptych/` (Wing II)
**Findings**: CHSH (Bell) · F82 (indefinite causal order) · F106 (contextuality) — three independent no-go theorems, three classical ceilings, all breached on one chip, each with an executed null.
**Upstream**: `demo/no-go-triptych/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.
> **Wing II accent = cyan (chrome).** THREE walls, three colors: Bell=cyan, causal=violet, contextuality=amber. good=breach.
> **This is a UNIFYING meta-exhibit** (some walls have deeper exhibits: Interrogation=game, Magic Square=F106) — link them.

## 1. Goal & the "aha"
A no-go theorem is a proof of a hard ceiling no classical strategy can pass. Three different classical intuitions —
locality (Bell), a definite order of events (causal order), pre-set values (contextuality) — each get their own
proven wall, and quantum hardware crests over all three on the same silicon. Each wall has an EXECUTED classical
control that lands at the wall, so the breach is a contrast, not an absolute reading.

## 2. Data — verified first (three grade files, ibm_marrakesh)
| wall | forbids | classical ceiling | quantum measured | σ | executed null | job |
|---|---|---|---|---|---|---|
| **Bell (CHSH)** | local hidden variables | \|S\| ≤ 2 | S = 2.7522 ± 0.0141 | 53σ | 0.036 ≈ 0 | d9an47mg26ic73dev0s0 |
| **Causal order (F82)** | a definite order | ≤ 0.8690 (SDP) | p̂ = 0.9769 ± 0.0005 | 217σ | 0.615 (fixed order) | d9826lkqp3as739sd2lg (+fez 0.9738, 201σ) |
| **Contextuality (F106)** | pre-set values | ≤ 8/9 = 0.8889 (enum) | 0.96901 ± 0.0004 | 196σ | 0.657 (no entangle) | d9akl8fu62qs738o68pg |
- Quantum ceilings: Bell Tsirelson 2.8284; games 1.0. All on ibm_marrakesh; game cross-device concordant on fez.

## 3. The exhibit — panels
**A — The three walls (interactive triptych).** THREE columns side by side (stack on mobile), one per theorem, each
its own color. Each column = a "tower": a solid **wall block** up to the classical ceiling (labelled with the bound),
the **quantum measured value cresting OVER** the wall (bright line + marker + big σ), and the **executed null** as a dot
at/below the wall. A selector (Bell · Causal order · Contextuality) highlights one column (dims the others) and drives a
detail verdict below (the theorem, exact numbers, executed null, cross-device, deeper-exhibit link). Each column uses
its OWN axis (independent scales) with values labelled — the σ carries the quantitative truth.

**B — One court (receipts + links).** Three receipts: (1) the bounds are PROVEN not cited (SDP-resolved / enumerated
over 4096 / textbook CHSH); (2) every wall has an EXECUTED null on the same chip; (3) same silicon + the game
reproduced on a 2nd device (fez, 201σ). Links to the deeper exhibits (Interrogation, Magic Square) + scope
(game-value not speedup; device-characterized not loophole-free) + Full Spec.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | Three different scales invite a misleading side-by-side (visual gaps not proportional). | Each column its OWN axis; label the bound + measured value + null explicitly on each; state "each has its own scale"; the σ (comparable) is the headline. |
| G2 | "No-go theorem" is jargon. | Primer + Panel A intro: a proof of a ceiling no classical strategy can pass; beating it FALSIFIES the classical picture. Name what each forbids in plain words. |
| G3 | Could read as "we did well" not "we falsified something". | Frame each as WALL (classical territory) vs CREST (quantum-only region); the executed null sitting at the wall makes the breach a contrast. |
| G4 | Over-claiming (loophole-free / computational advantage). | Scope: game-value/correlation advantages (not speedup); device-characterized not loophole-free; textbook priors credited. |
| G5 | Redundancy with Interrogation / Magic Square exhibits. | Frame as the UNIFYING piece ("three walls, one court") and LINK to the deeper single-wall exhibits; the value-add is the shared standard (proven bounds + executed nulls + one chip). |
| G6 | a11y / mobile / motion / self-contained. | Selector buttons (aria-pressed); every value in text + colour; columns have text labels for wall/measured/null; stack <680px; highlight transitions honour reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What is a no-go theorem?" primer + a one-line what-each-forbids under each column. |
| G8 | Spec discoverability. | Cyan "◇ Full Spec Sheet" button in hero + Panel B + footer. |

## 5. Pre-dev structure
1. **Data kernel**: WALLS `[{key,name,color,forbids,ceiling,measured,se,sigma,null,niceMax,niceMin,note,deeper}]`; assert measured>ceiling all three, null<=ceiling.
2. Panel A: 3 SVG tower columns (wall block + crest marker + null dot) + selector highlight + detail verdict.
3. Panel B: 3 receipts + deeper-exhibit links + scope + spec. 4. Chrome (museum.css, cyan; per-wall cyan/violet/amber). 5. Passes.

## 6. Acceptance
Three columns render walls + cresting measured values + null dots with correct numbers; selector highlights one +
shows its detail (null, cross-device, deeper link); σ 53/217/196 shown; Panel B carries proven-bounds + executed-nulls
+ one-court and links Interrogation/Magic Square + spec; keyboard-operable, colour-not-alone, mobile-stack, no external
requests, theme-aware. Then: Playwright render (0 console errors, 0 external requests, selector varies highlight/detail,
light+dark; CHECK label gutters — recurring overflow class) → UI improvement pass.
