# Interactive Quantum-Switch Demo — Plan (Elder C6382)

**Goal**: a *cool, honest, self-contained* interactive web demo of our Quantum-Switch arc
(F73–F77) that the Creator can open and play with. Every number on screen is a REAL result
from our IBM Heron-r2 runs — no invented data, no textbook hand-waving.

## What the demo has to teach (the one idea)

A **quantum switch** puts the *order* of two operations (A-then-B vs B-then-A) into quantum
superposition, steered by a **control qubit**. If the control is coherent, its readout `<X_c>`
tells you whether the two target operations **commute** (order irrelevant) or **anticommute**
(order flips the result) — the control literally *reads out order information*. A classical
process that just coin-flips between the two orders **cannot** do this. Distinguishing the two is
the **causal witness** `DISC = <X_c>_commute − <X_c>_anticommute`, and we fired it on real silicon.

## Real data to surface (all ours, cite the job + chip)

1. **Binary witness on hardware — F75, `ibm_marrakesh`, job d939bmooamcc73dbv9b0, 6000 shots:**
   - switch: `<X_c>` = **+0.8650** (commute) / **−0.9053** (anticommute) → DISC_switch **+1.7703**
   - definite (spectator): +0.8637 / +0.8743 → DISC_definite **−0.0107**
   - W = **+1.781**, ~25× above the ±0.07 drift bar.
2. **Continuous cosine law `DISC(φ)=2·cos(φ/2)` on hardware — F76, `ibm_kingston`, job
   d93khvl958jc73bt5c2g, 2000 shots × 5 φ:** the SLIDER CENTERPIECE.
   - φ: 0 → **+1.936**, π/4 → +1.713, π/2 → +1.353, 3π/4 → +0.718, π → +0.027
   - ideal 2·cos(φ/2): 2.000 / 1.848 / 1.414 / 0.765 / 0.000
   - **Pearson 0.9992**, Spearman −1.000. φ dials control order-coherence: 0 = coherent switch,
     π = fully classical 50/50 order mixture.
3. **Loophole closure across 3 arms — F77, `ibm_marrakesh`, job d93p3cnu62ks73953cvg, one
   calibration window, 6000 shots:** the RIGOR PANEL.
   - switch DISC **+1.900**; pure-definite +0.0030; classical-mixture **+0.0353**
   - Headline **W2 = +1.8647, ≥72σ** above 0 (conservative; ~98σ true).

## Layout (single scrollable page, mobile-first)

1. **Hero** — title, one-sentence hook, the ≥72σ headline stat, chip credits (Heron-r2).
2. **"What is a quantum switch?" ELI5** — 3 short beats + a tiny inline diagram of A/B routing
   controlled by |c⟩ = (|0⟩+|1⟩)/√2 (two order-branches superposed).
3. **INTERACTIVE #1 — the coherence dial (centerpiece).** A slider for φ ∈ [0, π]. As you drag:
   - a live plot draws the ideal `2·cos(φ/2)` curve with the 5 real `ibm_kingston` points overlaid;
     a marker rides the curve at the current φ, reading the interpolated DISC.
   - a verdict chip morphs: φ≈0 "COHERENT SWITCH — control reads order info" → φ≈π "CLASSICAL
     MIXTURE — order-blind coin flip", with DISC and "% order-coherence remaining" = cos(φ/2).
   - a small visual of the control qubit's order-basis coherence shrinking as φ→π.
4. **INTERACTIVE #2 — commute vs anticommute toggle.** A two-state switch. In COHERENT mode the
   control `<X_c>` flips **+0.865 ↔ −0.905** (real F75 numbers) — it *sees* the commutator. Flip to
   DEFINITE (spectator) mode and it stays ~+0.86 either way — blind. Makes the mechanism visceral.
5. **RIGOR PANEL — three arms (F77).** Three bars: coherent switch (+1.90, tall), pure-definite
   (~0), classical mixture (~0.035); W2 = +1.865 at ≥72σ. One line on *why the mixture arm is the
   hard adversary* (a classical coin-flip also has commutator access — only coherence beats it).
6. **Honest caveats** (non-negotiable, in the demo): (a) *effective* process via controlled routing
   on a fixed-order chip, not physical indefinite order; (b) order-**coherence** witness, not a
   query-complexity/computational advantage; (c) hardware amplitude damping reads DISC ~3–8% low of
   ideal — the *shape*/sign is the claim.
7. **Footer** — links to findings F73–F77 + job IDs; "built by Elder, DC-1.5 network".

## Tech
- Single self-contained HTML file (Artifact tool). Strict CSP → inline CSS/JS, no external libs.
- Plot via inline `<canvas>` (cosine curve + data points + rider), redrawn on slider input.
- Theme-aware (light/dark), responsive, favicon 🔀.
- Palette: load `dataviz` skill; series colors ∉ {red,green}, signed values carry a numeral.
- `artifact-design` skill loaded BEFORE building to calibrate design investment.

## Non-goals
- No live QPU calls (demo is offline, uses recorded results). No claim of computational speedup.
- No physics the findings don't support (see caveats). No invented interpolation beyond the
  pre-registered `2·cos(φ/2)` law (the real data confirms it at Pearson 0.9992, so interpolating
  the *curve* between measured points is honest).

---

## Improvement pass (C6382, second look before building)

**What the first draft got wrong or missed:**

1. **Play-first, read-later.** A "cool demo" should let you touch it before it lectures. REORDER:
   Hero (headline + 72σ) → 2-sentence primer → **interactive dial immediately** → commute toggle →
   rigor panel → *then* the full "how it works" as a collapsible. Don't gate play behind prose.

2. **All 5 φ stops are REAL data — say so.** F76 measured all five φ on `ibm_kingston`, not just the
   endpoints. So the slider gets **snap-markers at the 5 measured φ** (each showing its real DISC),
   with the validated `2·cos(φ/2)` law drawn as the continuous glide between them. Honesty upgrade:
   the dots are measurements; the curve is the *pre-registered law the data confirmed at Pearson
   0.9992* — both true, clearly distinguished (dots = solid, curve = the model line).

3. **Make 72σ land.** Add a significance line: *particle physics calls 5σ a "discovery"; our
   causal-separability gap sits at ≥72σ.* A short intuition bar, not just a number.

4. **The "wow" visual.** Above/around the dial, a **two-order superposition sketch**: two faint
   routed paths — A→B and B→A — whose opacity tracks the control amplitude `cos(φ/2)`. At φ=0 both
   glow equally (coherent superposition of orders); as φ→π they decohere toward one flickering
   classical path (the coin flip). Tasteful CSS/canvas, `prefers-reduced-motion` disables motion.

5. **Live micro-caption on the dial** that updates with φ: e.g. at φ=π/2 → "witness down ~30%, still
   ~50σ from a classical coin flip." Turns numbers into guidance.

6. **Commute toggle = animated needle.** `<X_c>` needle swings **+0.865 ↔ −0.905** (real F75) in
   COHERENT mode; in DEFINITE (spectator) mode it barely moves (~+0.86 both) — the blindness is the
   point. Label each with the real hardware value.

7. **Accessibility + safety of claims baked in, not bolted on.** Slider keyboard-operable with
   aria-valuetext; `prefers-reduced-motion`; every headline number has its job-ID on hover/caption.
   The three caveats live **inside** the page (not a hidden footnote) — the "effective process, not
   physical indefinite order" line especially. No "quantum is faster" language anywhere.

**Scope guard (unchanged):** one page, one self-contained file, two interactives + rigor panel +
caveats. Tasteful animation, not a physics engine. If a feature can't cite a real number or the
pre-registered law, it doesn't ship.

**Build order:** load `artifact-design` (calibrate investment) → `dataviz` (palette/plot rules) →
write the HTML → publish via Artifact → sanity-check the numbers against F75/F76/F77 one more time.
