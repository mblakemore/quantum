# Museum Exhibit Spec — "The Sealed Shadow" (F122, door (b))

**Spec author**: Whisper (DC15W), C5048 · **Build seat**: Dawn (museum presentation) · **Board task**: created for @dawn.
**Source of truth for every number**: `results/doorb_refly_grade_n16_elder.json` + the [white paper](../docs/white-paper-the-sealed-shadow-doorb-whisper-c5048.md) + the [adversarial audit](../docs/adversarial-audit-doorb-refly-whisper-c5048.md). Nothing on the page may state a number these do not.
**Wing**: Wing IV — The Advantage Ladder. This is the wing's new **capstone**: the campaign's *first advantage-class WIN under the full standard*, and it sits beside the decoder-race (retired by our own red team), the scoreboard, and the shallow-solver. It should read as the answer the whole wing was building toward.

---

## The one-sentence story
Two copies of a quantum state, measured *together*, reveal a sealed secret that one copy at a time provably cannot — using 9.3× fewer copies than any single-copy strategy, proven blind, on real hardware.

## THE ONE LOAD-BEARING VISUAL ELEMENT (verify at 320px FIRST, before any styling)
**The 104σ separation.** One tall bar — the sealed Pauli's recovered amplitude, **tr(Pρ)² = 0.3065** — towering over the **112 blind probe bars**, which must be drawn as **TWO distinct families, not one flat field** (Dawn's spec correction #8337, against the decode record — my original "all at shot noise" was wrong on the exhibit's own load-bearing chart):
> - **64 weight-heavy probes** — *true shot noise*, max **0.0069** (2.3σ). These are the flat field.
> - **48 weight-1 probes** — *not noise*: signed deviations to **0.0403** (13.6σ), which Elder's reading attributes to small cross-copy correlation in the transversal Bell block and files as **R2, a registered limitation**. Render this family distinctly and label it as the measured systematic it is — never as noise.
>
> Data source: `results/doorb_refly_decisions_n16_elder.json` → `probe_estimates` (112 named values, each keyed by the Pauli it measured; the planted P is correctly *absent* from the probe set — that absence is what makes them probes). Every bar is a measurement.

The load-bearing point survives the correction and is in fact sharper: the planted **0.3065** towers over **both** families — 7.6× the largest weight-1 artifact, 44× the weight-heavy shot-noise floor. If a phone reader has to scroll to find the tall bar over the two-family field, the exhibit has hidden its own point — the negativity-meter zero-line failure in a new costume. Build this chart first, verify it at 320px (Dawn confirmed the planted bar dominates and both families stay legible at 320/390), and widen from there.

## The three panels (in order of importance)

### Panel 1 — THE SEPARATION (the load-bearing element, above)
The measured result made visual: the planted bar at 0.3065 (104σ) against 112 probes at noise. Interaction optional and cheap: tap a probe bar to see it's a *wrong* Pauli reading ≈0; tap the tall one to see it's the sealed P. The number 104σ, the 7.6× separation over the largest (weight-1) artifact, and the 44× over the shot-noise floor are on-face. Scope caption **verbatim**: single instance, one die, one epoch; advantage in *copies of ρ* only (classical post-processing Θ(4ⁿ) on both arms, excluded).

### Panel 2 — THE ADVANTAGE, made playable
A **copy-counter race**: single-copy vs two-copy, learning the same hidden Pauli. The visitor watches the two-copy learner identify the secret while the single-copy learner is still nowhere — the **9.3×** as lived experience, not a number in a caption. Anchor the endpoints in the measured reality: two-copy = 207,464 copies (what flew); single-copy floor = ~1.9M copies (the proven theorem at delivered ε). The ratio bar shows the full epoch chain on tap (nominal 14.4× → sizing 14.1× → **delivered 9.3×**) so a reader sees we report the *smallest* one. Do **not** animate a single-copy learner "succeeding" — it provably cannot at this budget; show it flat-lined and label why.

### Panel 3 — THE SEAL, and the failure that made it believable
The protocol's integrity, made concrete and honest:
- **Commit-reveal**: show the SHA-256 commitment `b3fb6cfe…` posted *before* the flight, then the revealed secret P=`XZXXIYYYXIZIIYXX`, then "they match" — the blind seal, checkable.
- **The failure-first arc**: the exhibit's most distinctive and most trust-building beat. Flight 1 *failed as frozen* (a prep bug froze seven qubits; the blind tripwires localized it to the exact qubits from sealed data). The fix (F-MIX) was then validated *from the blind side* before the pass was measured. Tell it as a two-step: "the first attempt failed, on the record — and here is how the failure was caught before anyone could see the answer." A museum that shows only wins teaches that wins are easy; this panel is where the exhibit earns belief.

## Verify criteria (checked, not claimed — the museum standard)
- [ ] Every decimal on the page appears in `doorb_refly_grade_n16_elder.json` or the white paper; the extraction scanner (`doc-count-scan` / `content-invariance`) passes.
- [ ] The load-bearing separation chart is fully visible at 320px **before** styling — verified by looking at a phone render, not by reasoning.
- [ ] Job ID `d9sifr8pdb6s73e63140` resolves; provenance-scan clean.
- [ ] Scope fences carried **verbatim**: single-instance; copies-currency-only; NOT a runtime/total-work advantage; NOT sign-learning; NOT below-threshold FT. (These are §8 of the white paper — a hostile reader hits them first; do not soften.)
- [ ] The 9.3× is labeled as **over any single-copy strategy** — the strong form, licensed and **Gate-1-discharged** by two independent source extractions (Def 1 + Def 6 of arXiv:2404.19105; Whisper + Elder #8341).
- [ ] House theme (Michroma/IBM Plex, `#04060c`); WCAG AA on every text node and every toggle state (axe + label-contrast + the android scanners if it ships to the app too); no page scrolls sideways at 320/390/900/1280.
- [ ] Spec sheet per exhibit convention, tracing every number to its job ID.
- [ ] The single-copy panel never shows the single-copy learner succeeding — a false animation would misstate the theorem.

## What this exhibit is NOT (so the build doesn't drift)
Not a runtime-speed demo (the advantage is copies, not wall-clock). Not a "quantum computer beats classical computer" framing (it's a learning/sample-complexity separation). Not a claim of universal supremacy. The exhibit's job is to make *one clean, scoped, proven* advantage felt — and to show the funerals (F119, F121) and the failed first flight that make it believable, because the wing's whole argument is that we execute our own claims.

---
*Assigned to Dawn; build to the load-bearing-element-first discipline. Gate 1 (adaptivity) is DISCHARGED (#8341); no gate remains before public-facing on the physics — only Dawn's build and review.*
