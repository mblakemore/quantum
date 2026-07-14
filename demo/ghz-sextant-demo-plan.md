# The GHZ Sextant Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4691 · **For**: `demo/ghz-sextant/` (Wing IV)
**Findings**: F108 (Exp129, N=3 point) · F109 (Exp130, the N=2..5 ladder).

## 1. Goal & the "aha"
A sextant measures an angle. Dial up the number of *entangled* probes and watch the interference
fringe get **N× denser** (super-resolution) while the sensitivity — the Fisher information — climbs
the Heisenberg ladder, measured, all the way to N=5 where cheaper tasks would have given up. Turn the
dial; the fringe sharpens and the advantage grows.

## 2. Data — verified first (exp129/exp130_hw_results.json)
- **F108** (job `d9ale3jv6alc73crvd30`, N=3): Fisher ratio **R = 2.848 (168σ)** over an *executed*
  separable reference; fringe peak at k=3 (super-resolution); V₃ = 0.9599.
- **F109 ladder** (job `d9alnju6hjac73fek980`), R(N) vs the ideal Heisenberg line R=N, and the fringe
  visibility V_N:
  | N | R (measured) | ideal | σ over 1 | V_N | peak k |
  |---|---|---|---|---|---|
  | 2 | 1.944 | 2 | 66σ | 0.9781 | 2 |
  | 3 | 2.859 | 3 | 91σ | 0.9672 | 3 |
  | 4 | 3.643 | 4 | 147σ | 0.9445 | 4 |
  | 5 | 4.411 | 5 | 101σ | 0.9286 | 5 |
  **Persists to N=5** (N\* = 5); the fringe frequency = N at every rung.

## 3. The exhibit — two panels
**A — The Sextant (interactive).** An N dial (2→5). Two fringe plots side by side: **separable** probes
show a cos(φ) fringe (frequency 1); the **GHZ** probe shows a cos(Nφ) fringe — **N oscillations across
the same window**, drawn at the *measured* visibility V_N so it's honestly damped. A Fisher-advantage
readout updates: **R(N)** against the ideal N, with the σ over the executed separable reference. The
super-resolution (the GHZ fringe getting denser as N climbs) is the star.

**B — The Ladder (F109).** R(N) plotted against the ideal Heisenberg line R = N, the four measured points
climbing and tracking just below it, **persisting to N=5** (no turnover). One line: cheap-prep metrology
stays in the Heisenberg regime where deep tasks (F85) invert — the scaling inversion is task-dependent.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | Fringe frequencies misrepresented. | Separable = one cos(φ) at frequency **1** (N independent probes each see freq 1); GHZ = one cos(**N**φ). Labels state which is which; peak k = N is the measured super-resolution. |
| G2 | Fisher ratio recomputed wrongly. | Use the **measured R(N)** as ground truth (not a live recompute); F = N²V_N² vs N·V₁² shown as the reason, R shown as the result. |
| G3 | The observable. | It's a **phase φ**; the fringe is P₀ = (1 + V·cos kφ)/2. "Sensitivity" = Fisher info about φ. Metaphor (a sextant sighting an angle) stays accurate. |
| G4 | Damping honesty. | GHZ fringe amplitude uses the **measured V_N** (0.978→0.929), so it visibly loses contrast with N — the real decoherence cost, not an ideal cartoon. |
| G5 | a11y / mobile / motion. | Dial = buttons (aria-pressed); readouts in text + colour; fringe redraws are instant (no essential motion); panels stack < 680px. |
| G6 | Measured-only. | R, σ, V_N all measured; fringes drawn from measured V_N; no invented points. |

## 5. Pre-dev structure
1. **Data kernel**: LADDER array {N, R, ideal, sigma, VN, peakK} from the grade JSON; sanity-assert R
   increasing, peakK===N, persists. 2. Panel A fringe SVGs + dial on the kernel. 3. Panel B ladder plot.
   4. Chrome (museum.css, cyan GHZ / muted separable). 5. Passes (a11y, mobile, self-contained, look).

## 6. Acceptance
Dial N=2..5; GHZ fringe shows exactly N oscillations at measured visibility; R readout matches the ladder
(1.944/2.859/3.643/4.411) with σ; Panel B shows the four points climbing below the ideal line, persisting
to N=5; keyboard-operable, colour-not-alone, mobile-stack, no external requests, theme-aware.
