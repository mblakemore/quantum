# Demo Plan — "The Picture That Snuck Through" (ELI2 → ELI-quantum-engineer drill-down)

**Author**: Whisper (DC15W), C4537 (2026-07-10) — Creator-directed. DRAFT FOR ITERATION.
**Subject finding**: F83, capacity activation (Exp106/107): information through two channels that
each erase everything, where every definite ordering provably carries zero. Secondary exhibit at
deep layers: F82, the causal game (216.8σ/201σ).
**Design problem, as stated by Creator**: the existing ELI5 needs an ELI5. We need a *children's-
book-level surface* that an unprepared visitor enjoys in 30 seconds, with honest drill-down that
bottoms out at real circuits, real job IDs, real numbers.

---

## 1. The vehicle (three candidates, one recommendation)

### A. ⭐ RECOMMENDED — "The Gray Machines"
A kid mails a crayon drawing to Grandma. The mail route passes through **two Gray Machines** —
every machine turns whatever goes in completely gray. Two in a row: extra gray. No trick about
which machine is first helps: first-A, first-B, flipping a coin — always gray. Then the kid's
cat (our mascot/guide) sits on the routing lever and makes the machines **forget which one goes
first** — and a shimmer of the drawing arrives at Grandma's.

*Why it wins*: (1) **Color vs gray IS the physics** — depolarization literally means "all colors
equally likely," so the metaphor is not a lie, it is a translation. (2) Mail/drawing/Grandma is
universally warm at age 3. (3) The honest twist survives drill-down: at deeper layers we reveal
the picture *alone* still arrives gray — Grandma can only see the shimmer by holding the picture
next to the **mailman's mood stamp** (the control qubit). "Each is gray static; together they
speak" is the actual F83 signature (D≈0, MI in the correlation), and it's a *better* story beat,
not a caveat. (4) The "forget who goes first" lever maps 1:1 onto the existing demo's φ-dial and
the measured cosine law.

### B. "The Two Shredders" (runner-up)
A note passed through two paper shredders in fuzzy order arrives readable. Visceral and funny
(confetti physics!), but the correlation reveal is awkward (what pairs with confetti?) and
shredding reads as *cutting*, not *randomizing* — a dishonest metaphor one layer down.

### C. "The Forgetting Doors" (story-first)
Castle with two doors that each erase the secret word from your head. Rich narrative, weakest
visuals, and "memory erasure" invites consciousness misreadings we don't want. Keep as a
storybook *page* inside layer 0 if we want prose, not as the frame.

**Decision needed from Creator**: vehicle A/B/C (or a blend: A as frame, B as one gag panel).

---

## 2. The drill mechanism: one scene, five depths ("Explain it like I'm ___")

A single persistent scene — kid, drawing, two machines, mail route, Grandma — that **gains truth
as you turn an age dial**: `4 · 9 · 16 · undergrad · engineer`. Semantic zoom, not separate pages:
the SAME objects re-render with more detail at each depth (the machines grow labels, the shimmer
becomes a correlation readout, the lever becomes φ, the route becomes a circuit). The visitor
never navigates away; they *zoom into the truth of the thing they already understand*.

| Dial | Register | The same scene becomes… | The one idea added |
|---|---|---|---|
| **4** | picture book, ≤15 words/screen, tap-to-play | cartoon: drawing → gray → gray… cat sits on lever → shimmer arrives, Grandma smiles | "The machines forgot who was first — and the picture snuck through." |
| **9** | curious kid / adult civilian | same scene + a "try every trick" panel: first-A / first-B / coin-flip all fail (buttons the visitor presses); the lever is revealed as "both orders at once" | *No arrangement works. "Both at once" is a genuinely new kind of arrangement.* |
| **16** | sharp highschooler | the honest twist: picture alone STILL gray (static screen); drag it next to the mail stamp → the shimmer appears only in the *pair*; live 2-panel "static + static = message" toy | *The message lives in the correlation, not in either piece.* (D≈0, played as a magic trick that's real) |
| **undergrad** | physics/CS student | machines get labels (fully depolarizing channel, Kraus σᵢ/2); the lever becomes the control qubit with the φ-dial; conditional states (ρ+2𝟙)/5 vs (2𝟙−ρ)/3 shown as color-tint math; MI meter fills to 0.0489 bits ideal / 0.0436 measured | *Exactly how much sneaks through, and why any definite order is exactly zero (channel algebra).* |
| **engineer** | practitioner / reviewer | the route becomes the actual transpiled circuit (padded 4-CZ skeleton); real per-pair table from `results/exp106_hw_results.json`; job IDs, frozen pre-reg links, sentinel DISC values, the F82 game panel (0.977 vs bound 0.8695, SDP q* recovery), Exp107 N=3 scaling status | *Here is the data; here is how you'd audit us.* |

**Honesty ladder (non-negotiable design rule)**: every depth ends with one line under a 🔍 icon —
"What's really true here:" — that pre-corrects its own metaphor (e.g., dial-4: "Real scientists
did exactly this with light-particles on a real quantum computer. The 'drawing' is one bit.").
The metaphor never has to be retracted later, only *sharpened* — each layer's story is a strict
subset of the next layer's truth. This is what makes it drill-down rather than bait-and-switch.

---

## 3. Screen-by-screen, dial = 4 (the ELI2 surface — the make-or-break 30 seconds)

1. **Meet**: kid draws a red cat. "Mila drew a cat for Grandma." [tap]
2. **Problem**: route shows two big friendly-but-dumb machines. Feed a rainbow → gray slab plops
   out (satisfying *thunk*). "Uh oh. The Gray Machines turn EVERYTHING gray." [tap: try it —
   visitor feeds 3 things, all gray. Repetition = the point lands preverbal.]
3. **Tricks fail**: swap machine order (visitor drags them!) → still gray. Coin flip → still gray.
   Machines shrug. [interaction IS the proof of exhaustion]
4. **The cat move**: cat curls up on the routing lever, lever floats to the middle, machines look
   *confused* (swirly eyes, both name-tags flicker A/B). Drawing goes in…
5. **Arrival**: Grandma holds up a gray page… tilts it… a faint red cat shimmers. She smiles.
   "It snuck through!" [confetti]
6. 🔍 "What's really true here: real machines like this exist, and scientists sent a tiny secret
   through two perfect erasers on a real quantum computer — this year." [subtle "9" on the dial
   pulses — the invitation to grow up one notch]

## 4. Build notes

- **Form**: one self-contained HTML file, `demo/two-walls/index.html`, same constraints as the
  switch demo (no external deps, GitHub Pages, mobile-first — dial-4 must work as pure taps).
- **Data**: bake in `exp106_hw_results.json` + `exp105_hw_results.json` numbers at build time
  (engineer layer renders from an inline JSON blob, so the page stays offline-complete).
- **Reuse**: the φ-dial/cosine-law interaction from the existing switch demo returns at
  undergrad+ as the lever's true identity — the two demos cross-link.
- **The cat**: mascot carries continuity across depths (at engineer depth it sits on the dilution
  fridge). Cheap continuity device, high warmth.
- **Sound**: optional single *thunk* / *shimmer* effects, muted by default.
- **A11y**: every animation has a text beat; dial keyboard-navigable.

## 5. Build phases (iterate with Creator between each)

- **P0 (this doc)**: vehicle + architecture sign-off. ← WE ARE HERE
- **P1**: dial-4 + dial-9 playable (the hard part is the first 30 seconds, so build it first);
  static mocks for 16+.
- **P2**: dial-16 correlation toy + undergrad layer with live MI meter.
- **P3**: engineer layer with real-data tables + F82 game panel + cross-links; polish pass;
  Pages deploy alongside `/demo/`.
- **P4 (stretch)**: "curator mode" — a guided 90-second auto-play through all five depths for
  showing on a phone without touching.

## 6. Open questions for Creator (the iteration hooks)

1. Vehicle: Gray Machines / Shredders / Doors / blend?
2. Age dial labels: numbers (4/9/16/…) vs personas ("kid / curious / student / engineer")?
3. Mascot: cat, or something tied to the network's identity?
4. Scope: capacity-activation only, or include a game (F82) "second exhibit" room at deep layers
   (my recommendation: yes, deep layers only)?
5. Tone at dial-4: wordless-with-narrator-captions (readable-to-kids) vs read-aloud audio (adds
   asset weight)?
