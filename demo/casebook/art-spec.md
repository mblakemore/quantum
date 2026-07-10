# Suspect Portrait Asset Spec — The Interrogation (demo/casebook)

**Whisper C4550, for Creator. What's needed to add suspect profile pictures.**

## The one non-negotiable rule (game integrity)

**Exactly ONE shared silhouette asset for the un-revealed state — never per-character
silhouettes.** The ceiling (91%) is a theorem about detectives who cannot identify the
suspects; if outlines differ, repeat players identify pairs before calling and the game's
honesty breaks (same reason the digital version hides names until the call). One anonymous
"figure under interrogation-room light" card, used for both slots, every case. Portraits
appear only at reveal.

## Inventory (12 assets total)

| # | Asset | Physics | Design brief (art should encode the physics) |
|---|---|---|---|
| 0 | **Shared silhouette** | pre-call state | featureless figure, backlit, no identifying outline traits |
| 1 | **The Nobody** (𝟙) | does nothing | a person-shaped absence: empty coat + hat, pale gray, instantly forgettable — *the most dangerous suspect in the deck* (the best kit is always wrong about them) |
| 2 | **The Mirror** (X) | flips 0↔1 | perfectly left-right symmetric face, chrome/reflective surfaces |
| 3 | **The Twist** (Y) | flips + imaginary phase | asymmetric, spiral motif, slightly translucent/off-kilter — the one the Rookie Kit is confidently wrong about |
| 4 | **The Judge** (Z) | flips signs only | stern, dark robe, high collar; changes nothing you can see directly |
| 5 | **Blend East** ((X+Y)/√2) | 45° Mirror+Twist | visible hybrid of 2+3, warm accent, leaning right |
| 6 | **Blend West** ((X−Y)/√2) | the conjugate | near-twin of East, mirrored lean, cool accent — East & West are RIVALS (their pairing anticommutes): design them as estranged twins |
| 7 | **Blend North** ((X+Z)/√2) | Mirror+Judge | chrome + robe hybrid, upright |
| 8 | **Blend South** ((X−Z)/√2) | conjugate | North's estranged twin, inverted accent |
| 9 | **Blend Dawn** ((Y+Z)/√2) | Twist+Judge | spiral + robe, warm sunrise accent |
| 10 | **Blend Dusk** ((Y−Z)/√2) | conjugate | Dawn's estranged twin, cold dusk accent |
| 11 | *(optional)* Detective Whisper | mascot | trench coat, big ears, for header/PnP cover |

The estranged-twin pairs (5/6, 7/8, 9/10) are a real teaching device: twins read as RIVALS at
reveal, which is the actual anticommutation structure.

## Technical requirements

- **Master format**: 512×640 px (3:4 portrait) PNG with transparent or #1a1a26-matched dark
  background, OR SVG (preferred if the style allows — crisp at any size, tiny, inline-able).
- **Rendered size** in-game: 96×124 px — faces must read at that size (bold shapes, high
  value-contrast; avoid fine linework).
- **Style**: consistent noir-lite cartoon across all 12; must sit on dark UI (#0d0d14–#1a1a26);
  one shared palette + one accent color per character (the accent doubles as their case-log
  color later).
- **Delivery**: files in `demo/casebook/img/` named `nobody.png`, `mirror.png`, `twist.png`,
  `judge.png`, `east.png`, `west.png`, `north.png`, `south.png`, `dawn.png`, `dusk.png`,
  `silhouette.png` (+ optional `whisper.png`). If we want the page to stay single-file,
  I base64-inline them at build time (budget ≈ 25–50 KB/portrait → ~400 KB page, acceptable;
  SVG would be ~5 KB each).
- **License**: repo is public — art must be original, AI-generated with redistribution rights,
  or CC0. Attribution line goes in the page footer.
- **Accessibility**: I write the alt text per character (e.g., "Suspect revealed: The Twist —
  a translucent, spiraling figure leaning off-center"); art just needs to be describable.

## Three ways to source it (pick one)

- **A. I generate geometric SVG emblems now** — zero assets needed from you: badge-style
  portraits (shape grammar: mirror-symmetry for X, spiral for Y, scales/gavel glyph for Z,
  blended glyphs at 45° for the twins, an empty outline for the Nobody). Consistent, tiny,
  honest, shippable this cycle; replaceable later without code changes.
- **B. You generate with an image model** — I supply the prompt pack (one master style prompt +
  12 character prompts, consistent-character technique). Drop the 12 PNGs in
  `demo/casebook/img/` and I wire them in + write alt text.
- **C. Commission** — same spec sheet works as the brief.

**Recommendation**: A now (the game gets faces today), B to replace when you feel like art
directing. The code path is identical either way: portraits keyed by character name at reveal,
one shared silhouette before.
