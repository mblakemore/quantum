# The Quantum Museum — Landing-Page Refactor Plan

**Author**: Whisper (DC15W), C4684 (2026-07-14) · **Substrate**: claude-opus-4-8
**Directive**: Creator — refactor `mblakemore.github.io/quantum/demo/` from a switch-only page
into a landing that encompasses the whole campaign; propose new visual demos. "It seems like we
have a museum worth of content." — We do. This plan makes the museum.

---

## 1. Where we are

- **`demo/index.html`** *is* the quantum-switch demo (19 "switch" mentions; every H2 is about
  order-coherence). It's a strong single exhibit wearing the landing-page URL.
- **Standalone exhibits already built** but not unified: `demo/static-duel/` (classic-vs-quantum
  decoder race), `demo/casebook/` + `demo/casebook-pnp/` (interrogation game + print-&-play),
  `demo/ladder/`, `demo/weather/` (QPU weather), `demo/scoreboard/` (the campaign scoreboard).
- **The content behind them**: findings F01–F117, ~110 experiments, the switch arc, the ICO
  engine, the comms/metrology ladders, the Horizons-2 "six universe-questions", the computational
  bridge, the trust ladder. Genuinely a museum's worth — currently a single lit room and a
  corridor of unmarked doors.

**The move**: promote the switch to *one flagship exhibit*, and turn the landing into the
**museum lobby** — a curated hall that routes visitors through themed wings, every exhibit
anchored to real measured data.

---

## 2. The architecture — lobby + five wings

```
demo/index.html          ← THE LOBBY (new): hero + the five wings as exhibit galleries
demo/switch/             ← move the current switch demo here (flagship of Wing I)
demo/<exhibit>/          ← every exhibit its own self-contained page, one design system
```

**The Lobby** (`demo/index.html`): a short hero — *"We asked a quantum computer six questions
the textbooks call impossible, and pre-registered the answers. Here is the museum."* — then the
five wings, each a labelled gallery of exhibit **cards**. No long prose; the lobby is a map. A
persistent top strip: the one-line verdict + a link to the **Scoreboard** (the museum's "you are
here" summary) and the **full report** / GitHub.

**The five wings** (they already match the README's themed groups — reuse that taxonomy so the
site and the docs tell one story):

| Wing | Theme | Exhibits (● built · ○ proposed) |
|---|---|---|
| **I — The Causal Switch** | indefinite order as a resource | ● Interactive switch · ○ ICO Refrigerator · ○ Capacity Activation · ○ Teleported Witness |
| **II — The No-Go Games** | beating exact classical ceilings | ○ The No-Go Triptych (Bell/causal/magic) · ○ Magic Square · ● Bot Duel (static-duel) · ○ Superdense |
| **III — Foundations on Silicon** | the sci-fi wing (Horizons-2) | ○ Grandfather Paradox · ○ Twin Paradox · ○ Zeno Tractor Beam · ○ Quantum Darwinism · ○ Hayden-Preskill Mirror · ○ Negative Energy |
| **IV — The Advantage Ladder** | the five scoreboards | ● Scoreboard · ○ GHZ Sextant · ○ BGK Shallow Solver · ○ QRAC · ○ Trust Ladder (randomness) · ● Ladder (existing) |
| **V — The Instruments** | how we measured it | ● QPU Weather · ○ Switch-Bench readout · ● Casebook game + Print-&-Play |

---

## 3. New visual demos — the exhibit proposals

Ranked by *impact × cheapness* (cheap = reuses banked data / no new hardware). Each is grounded
in a specific finding, and each renders **real measured numbers**, never a cartoon.

### Flagship builds (Phase 2 — highest impact)

1. **The Magic Square** *(F106, contextuality)* — the crown jewel. A 3×3 grid; the visitor plays
   the pseudo-telepathy game as a *classical* pair and physically cannot exceed 8/9 (the grid
   fights back — no consistent ±1 assignment exists). Flip to the *quantum* strategy and win
   every cell. Ends on the measured 0.9690 / 196σ. *Cheap: banked Exp126 data + a logic puzzle.*

2. **The ICO Refrigerator** *(F86/F95, the engine)* — two thermal baths and the switch. Drag the
   **order-coherence** slider; watch the target qubit split **colder** (|+ branch) or **hotter**
   (|− branch) by control outcome — refrigeration forbidden to every ordered process. A "demon's
   ledger" tallies the work as the full cycle runs (F95). *Cheap: banked F86/F95 curves.*

3. **The Grandfather Paradox Courtroom** *(F101, P-CTC)* — the most shareable. A slider for
   "how hard do you try to kill grandfather"; the timeline *forbids* it (survival drops to the
   measured 1.9%, a 53× suppression) and a bystander's classical record visibly **rotates into
   quantum coherence** (the 78σ backaction the rate can't fake). Three gates, the shallowest
   circuit of the campaign — and it answers the oldest question in time-travel fiction.

4. **The Trust Ladder** *(F115→F117, randomness)* — a vertical slider: **full-trust → one-sided-
   DI → full-DI**. At each rung the exhibit shows what you may assume, what you may claim, and the
   certified private random bits (the DI number visibly *evaporating* at the top rung, the
   one-sided-DI 0.65-bit certificate standing at the middle). The honest-scope lesson made
   tactile. *Cheap: banked F117 + the SDP tool's own curve.*

### Strong Phase-3 builds

5. **The GHZ Sextant** *(F108/F109)* — separable vs GHZ probes chasing a phase; watch the GHZ
   fringe oscillate at N× the rate (super-resolution) and the Fisher advantage climb the ladder,
   persisting to N=5. A dial for N; the σ over the executed SQL updates live.

6. **The BGK Shallow Solver** *(F113)* — a 2D grid; a *constant-depth* quantum circuit lights up
   and returns a valid answer with certainty while a shallow *classical* circuit visibly can't
   reach across the grid. The depth-ledger bar shows quantum staying flat (O(1)) as n grows.

7. **The Zeno Tractor Beam** *(F102)* — a Bloch arrow being driven by a π-rotation; a "watch
   cadence" dial. Watch faster → the arrow freezes (0.644 survival at cadence 8 vs 0.020
   unwatched); past the watch-cost frontier (N=16) the grip weakens. Measurement as a tractor beam.

8. **The No-Go Triptych** *(Bell + F82 + F106)* — three ceilings side by side; beat each as a
   quantum player, watch the three classical walls (2, 0.8695, 8/9) fall. The unifying exhibit
   that says *"three great no-gos, one court."*

### The long tail (fold in as capacity allows)

9. **Quantum Twin Paradox** (F100) — an aging clock marks the path, killing interference.
10. **Quantum Darwinism under indefinite order** (F98) — facts-without-a-history vs erased records.
11. **The Cloning Replicator** (F110) — try to copy a qubit; hit the 5/6 ceiling; the cheat-detector fires.
12. **The Hayden-Preskill Mirror** (F99) — information provably dead in every definite order, recovered phase-flipped from the probe.
13. **Capacity Activation** (F85) — a bit crosses two channels of *exactly zero* capacity.

---

## 4. One design system (so it reads as a museum, not a folder)

The exhibits currently drift between two looks (the switch page's cyan/amber dark-tech; the
scoreboard's cleaner instrument panel). Unify on a shared, subject-grounded language:

- **Tokens**: one `museum.css` of CSS custom properties (surfaces, ink, accent, the four status
  colors, mono/sans), theme-aware light/dark, imported by every exhibit. Retire per-page palettes.
- **The "measured-data" badge** — a standing convention: every exhibit carries a small monospace
  chip with its **job ID + finding number + σ**, because the campaign's whole identity is *"every
  number is real hardware."* The badge is the museum's authenticity seal.
- **The exhibit card** (lobby) — one reusable component: title, one-line hook, a live mini-canvas
  thumbnail (a 6-second looping preview of the interaction), a finding badge, wing tag.
- **Replay-first, live-optional** — every exhibit runs on *banked hardware data* by default (works
  for everyone, offline), with an optional BYOK **LIVE** toggle where it makes sense (the
  static-duel and weather already do this — promote it to a standard affordance).
- **A breadcrumb + wing nav** so a visitor can wander (Lobby › Wing III › Grandfather Paradox) —
  the thing that turns standalone pages into a *museum*.

---

## 5. Build sequence

- **Phase 1 — the Lobby (do first, unblocks everything).** Refactor `demo/index.html` into the
  hall: move the switch demo to `demo/switch/`, build the five-wing gallery of cards, wire the
  existing six exhibits (switch, static-duel, casebook, casebook-pnp, ladder, weather, scoreboard)
  into their wings, ship `museum.css` + the card component + the measured-data badge. *Result: the
  museum exists and every current exhibit has a home, before a single new demo is built.*
- **Phase 2 — four flagships.** Magic Square, ICO Refrigerator, Grandfather Paradox, Trust Ladder.
  The four with the highest wow-per-hour and all cheap (banked data). *Result: each wing has a
  headline.*
- **Phase 3 — depth.** GHZ Sextant, BGK Solver, Zeno, No-Go Triptych, then the long tail as breathing-cycle work.

**Ownership note**: exhibits are one-per-cycle, self-contained, and reuse the results already in
the repo — so this is a long, pleasant tail of breathing-arc builds, not a monolith. Each new
exhibit is also a natural non-quantum-experiment cycle (variation from the flight cadence).

---

## 6. Why this is worth it

The campaign answered a hard question and left the receipts. A report and a scoreboard say *what*
we found; the museum lets someone **feel** it — drag the order-coherence and watch a witness die,
try to beat 8/9 and fail, slide the trust ladder and watch a claim evaporate. The content is
already measured and banked; the museum is the interface that turns 117 findings into something a
person can walk through. The switch earned the front door for a while. Now it earns a wing.
