# The Twin Paradox Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4693 · **For**: `demo/twin-paradox/` (Wing III)
**Finding**: F100 (Exp122b) — an excited "clock" qubit ages, its aging marks the interferometer path, and that which-path record destroys the interference the vacuum twin keeps.
**Upstream**: `demo/twin-paradox/spec.html` — the Full Spec Sheet (new process step). This plan builds the *interactive* view of what the spec certifies. The exhibit links to it prominently.

> **Process (upgraded C4693 per Creator):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.

## 1. Goal & the "aha"
Split a particle onto two paths at once so it interferes with itself; interference only survives if nothing records
which path it took. Put a *clock* on it. If the clock **ages**, its reading becomes a which-path record — and the
interference dies. So: the twin who **ages** loses coherence; the twin who **doesn't** keeps it. Drag a delay
(= proper time) and watch the excited-clock fringe wash to grey while the vacuum-clock fringe holds.

## 2. Data — verified first (results/exp122b_grade.json, job d9ah35eg26ic73demgag)
Phase-blind visibility |V| = √(X²+Y²) down the delay ladder [0, 36.6, 73.2, 146.4, 292.7] µs:
- **vacuum clock**: 0.885 · 0.657 · 0.493 · 0.283 · 0.066
- **excited clock (ages)**: 0.862 · 0.355 · 0.155 · 0.052 · 0.027
- **aging gap** (vac − exc): 0.023 · 0.302 · **0.338 (36σ) @73µs** · **0.230 (23σ) @146µs** · 0.038 (floor)
- **echo recovery @73µs = −0.119 ± 0.010** (wrong sign → static-ZZ mechanism REFUTED). W_ROT did NOT fire.
- **Verdict: AGING-CERTIFIED-CLEAN.** V-ratio 0.314 measured vs √0.1=0.667 → excited decay ~2× faster than pure T1 (reported).

## 3. The exhibit — panels
**A — The Two Twins (interactive).** A delay dial across the ladder (0 · 36.6 · 73.2 · 146.4 · 292.7 µs, labelled
"proper time"). Two side-by-side interferometer **fringe strips** — "Vacuum twin (stays home)" cyan, "Excited twin
(ages)" amber — whose **contrast = the measured |V|** at that delay. Crisp bands = coherent; washed grey = decohered.
Live readouts of each |V| and the **aging gap** with σ. At 73µs the split is widest (36σ) — named.

**B — The aging curves.** Two |V|-vs-delay decay curves with the aging gap **shaded** between them, four measured
dots each, σ callouts at 73µs (36σ) and 146µs (23σ), and the noise-floor note at 292µs.

**C — "How we know it's aging, not a trick" (short).** Three receipts: (1) phase-blind |V| is rotation-immune by
construction; (2) echo recovery −0.119 wrong sign → static-ZZ **refuted**; (3) the self-attached-asterisk provenance
(Exp122's withheld 67σ). Prominent link to the Full Spec Sheet.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Visibility" is jargon. | Show it AS fringe contrast: crisp bands vs washed grey. Say it: interference = self-interference, contrast = how alive it is (1 crisp → 0 grey). |
| G2 | Fringe implies a known phase, but data is phase-blind. | Draw contrast only; annotate "band position (phase) is arbitrary — we measure only contrast |V|=√(X²+Y²)". No phase claim on the page. |
| G3 | Could read as "excited qubit just decays faster, so what." | Frame the *gap* as the finding (which-path record), name 73µs=36σ, and carry the echo-refutation so it isn't a trivial-T1 story. |
| G4 | Over-claiming literal time dilation. | Scope pill + spec §6: this is a which-path **clock-decoherence analog** (Zych–Brukner), not literal dilation. |
| G5 | The honesty story (withheld 67σ) is the soul of F100 and easy to drop. | Panel C receipt + the spec's §5 adjudication, linked prominently. |
| G6 | a11y / mobile / motion / self-contained. | Dial = buttons (aria-pressed); |V| in text + colour; fringe strips have text contrast readouts; panels stack <680px; fringe transition honours reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context request (Creator). | A "what's an interferometer / what's aging here" explainer block right after the lede, plain-language, before the interactive. |
| G8 | Spec discoverability (Creator). | Prominent "◇ Full Spec Sheet" button in the hero, repeated in Panel C and the footer. |

## 5. Pre-dev structure
1. **Data kernel**: LAD array `{us, vac, exc, gap, sigma}`; assert gap@73µs≈0.338 & 36σ, vac>exc at every rung>0, echo wrong-sign.
2. Panel A: dial + two SVG fringe strips (contrast=|V|) + readouts. 3. Panel B: two decay curves + shaded gap + σ marks.
4. Panel C: three receipts + spec links. 5. Chrome (museum.css, violet wing accent; cyan=vac, amber=exc). 6. Passes.

## 6. Acceptance
Dial moves 0→292.7µs; both fringe strips lose contrast, excited faster; readouts show the table values; aging-gap shows
0.338/36σ at 73µs; Panel B shows both curves + shaded gap + two σ callouts; Panel C carries phase-blind + echo-refuted +
withheld-67σ and links the spec; keyboard-operable, colour-not-alone, mobile-stack, no external requests, theme-aware.
Then: Playwright render (0 console errors, 0 external requests, screenshot light+dark) → UI improvement pass.
