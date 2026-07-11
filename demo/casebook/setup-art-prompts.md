# Setup-Section Art — Gemini Prompt Pack (3 images)

**Whisper C4569** (Creator request: illustrate "The setup, in three steps").
Same discipline as the portrait pack (`art-prompts.md`): each prompt fully self-contained
(master style restated, never "same as before"), NO text/letters/numbers/logos guards (the
card captions already carry the numbers — 91%, 97.8% — so the images don't have to),
thumbnail-readable bold shapes.

**Delivery**: `setup1.png`, `setup2.png`, `setup3.png` → `demo/casebook/img/`.
Landscape 4:3 (e.g., 1600×1200). They render at ~300px wide at the top of each setup card;
I'll composite onto the page background, LANCZOS-downscale, optimize, and wire with alt text
(same pipeline as C4552).

---

## setup1.png — "Suspects come in pairs" (two silhouette cards)

> Flat noir cartoon illustration, bold thumbnail-readable shapes, clean vector-like edges,
> high-contrast dramatic lighting, muted palette on a solid very dark blue-black background
> (hex #141420), single warm interrogation-lamp light cone from above, film-noir detective
> atmosphere, subtle film grain. NO text, NO letters, NO numbers, NO logos, NO photorealism.
>
> Subject: two identical playing-card-shaped case files lying side by side on a dark
> detective's desk, angled slightly toward each other. Each card shows the SAME featureless
> backlit human silhouette — a pure black cutout figure against a dim warm glow, no facial
> features, no distinguishing outline details, identical on both cards. Between the two cards,
> a single thin glowing gold thread connects them: on its left half the thread is neatly tied
> in a knot (allies), and on its right half the same thread is frayed and snapping apart
> (enemies) — one continuous thread showing both fates at once. A faint warm lamp cone from
> the top of frame lights the desk; deep shadows everywhere else. Gold accent color
> (hex #e8c268) for the thread and card borders only.

*Card 1 caption already says PARTNERS/RIVALS — the tied-and-fraying thread is the visual.*

## setup2.png — "The wall at 91%" (classical → ceiling → quantum)

> Flat noir cartoon illustration, bold thumbnail-readable shapes, clean vector-like edges,
> high-contrast dramatic lighting, muted palette on a solid very dark blue-black background
> (hex #141420), film-noir atmosphere, subtle film grain. NO text, NO letters, NO numbers,
> NO axis labels, NO logos, NO photorealism.
>
> Subject: a stylized bar-chart as a physical scene. Three ascending rectangular towers in
> dusty blue-violet (hex #4a4a6e to #8888c0 gradient), each taller than the last, all stopping
> short of a bold glowing horizontal red line (hex #e0405e) that spans the entire frame like a
> police line or laser tripwire. The region above the red line is washed in a faint red haze —
> a forbidden zone. To their right, a fourth tower in radiant mint green (hex #8af0ae) SMASHES
> through the red line, the line bending and cracking around it like broken glass, green glow
> spilling into the forbidden zone above. The green tower clearly stands inside the red haze.
> Low camera angle, the towers lit like noir skyscrapers under a night sky.

*The card text supplies "91%"; the image's job is only: three stop below the line, one breaks it.*

## setup3.png — "A real quantum computer" (the chandelier cryostat)

> Flat noir cartoon illustration, bold thumbnail-readable shapes, clean vector-like edges,
> high-contrast dramatic lighting, muted palette on a solid very dark blue-black background
> (hex #141420), single warm interrogation-lamp light cone from above, film-noir detective
> atmosphere, subtle film grain. NO text, NO letters, NO numbers, NO logos, NO brand marks,
> NO photorealism.
>
> Subject: a superconducting quantum computer's dilution-refrigerator "chandelier" — a tall,
> elegant tiered structure of gold-plated discs (hex #e8c268) connected by dozens of fine
> golden cables and slender rods, narrowing as it descends, hanging in a dark laboratory like
> a chandelier in an interrogation room. The bottommost, smallest stage glows faint mint green
> (hex #8af0ae) — the cold quantum heart — casting a soft green pool of light beneath it. The
> warm lamp cone from above catches the gold tiers; the lab around it falls into deep noir
> shadow. Composition: the chandelier fills the frame vertically, slightly off-center, like a
> suspect standing under the lamp.

---

**Consistency notes**: all three share the exact same background hex, grain, lamp-cone motif,
and the page's three accent colors (gold #e8c268 / red #e0405e / quantum green #8af0ae) so
they read as one set with the existing portraits. If a generation adds stray text or a logo,
regenerate — the no-text rule is load-bearing (the captions carry the numbers).
**Alt text** (mine, at wiring time): 1 = the paired-cards-one-thread description; 2 = "three
bars stop below a glowing red line; a green bar breaks through it"; 3 = "a gold tiered
quantum-computer chandelier glowing green at its lowest stage."
