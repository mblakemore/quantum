# The Quantum Museum — 2026 Redesign Plan

**Status**: PROPOSAL — awaiting Creator approval (options are marked; nothing here is implemented except the two proof artifacts noted in §8)
**Author**: Whisper C4989 (plan requested by Creator 2026-07-23)
**Companion artifact**: `museum-redesign-tile.html` — DELETED 2026-08-11 on the Creator's call (board #27, general#10012). It was the proposed theme rendered live (v2, "The Layered Museum"): the three zoned surfaces, the framed-case-with-label exhibit card holding a real captured thumbnail, placard and vitrine voices, controls, and the full token set with printed contrast ratios.

---

## 0. The brief (Creator's requirements, distilled)

1. The **museum landing becomes the main entrance** at `https://mblakemore.github.io/quantum/`; the current root page (the quantum-switch campaign landing) becomes part of the museum.
2. **Complete UI/UX refresh** of the museum.
3. **Kill light/dark theme switching** — one theme "in between" that looks awesome.
4. The **main landing needs beautiful graphics** — exhibit/chart screenshots explicitly allowed.
5. The **exhibits get lifted** by the new theme.
6. **WCAG AA accessible.**

## 1. Current state (inventoried this cycle)

| Asset | State |
|---|---|
| Root `index.html` (193 lines) | Switch-campaign narrative landing: hero, 3 stats, links to Museum / STATIC / Casebook / Horizons / report. Own inline styles, separate from museum.css. |
| `demo/index.html` (404 lines) | Museum landing: 8 wings, 45 exhibit cards (text-only), topbar with theme toggle. |
| `demo/museum.css` (136 lines) | Shared token system: dark default + light via `prefers-color-scheme` + two `data-theme` override blocks. Print styles. A11y primitives (skip link, sr-only, focus-visible) already present. |
| Theme machinery | 69 pages carry the `qm-theme-restore` localStorage script; 61 carry a `themeBtn`. |
| Exhibits | 45 `demo/*/index.html` + spec pages, all importing museum.css, some with local inline styles and a few hardcoded hexes (e.g. `#ef4444` in decoder-race). |
| Graphics | `images/fig01–fig10*.png` report charts exist; **no exhibit imagery on any landing card**. |
| Other root-level | `horizons.html` (529 lines, own styling), `demo/scoreboard/` (274 lines). |

**Redundancy finding**: every unique thing the old root page links (STATIC, Casebook, Horizons, the switch) already exists as a museum card or can be one section. Nothing is lost by making the museum the front door.

---

## 2. Information architecture — the museum becomes the building

```
BEFORE                                  AFTER
/quantum/            switch campaign    /quantum/            THE MUSEUM ENTRANCE (new landing)
  └ /demo/           museum landing       └ /demo/           redirect → /quantum/  (meta refresh + canonical)
      └ /demo/<x>/   45 exhibits              └ /demo/<x>/    exhibits — URLs UNCHANGED
  horizons.html      plain-language        horizons.html      unchanged URL, restyled, carded on landing
```

- **Root `index.html` is replaced** by the redesigned museum entrance. The switch-campaign narrative (order-of-events hero, ≥72σ story) is not deleted: its best lines become the entrance's "flagship" section fronting Wing I, where they always belonged — *the quantum switch becomes an exhibit story inside the museum, not the gatehouse in front of it.*
- **`demo/index.html` becomes a redirect stub** (meta refresh + link + `rel=canonical` to root) so every deep link and search result keeps working. Exhibit URLs do not move — 45 directories untouched, zero link rot.
- **Relative paths**: the new root landing references exhibits as `demo/<x>/` (the old root already does this; the museum grid's hrefs get the `demo/` prefix when the page moves up — a mechanical one-pass edit).

## 3. One theme: "The Layered Museum" (v2 — see tile)

> **v2 note**: the first proposal ("Gallery Dusk", a single L\*30 slate ground) was rejected by Creator as too close to the current dark theme — correctly: it moved a luminance dial instead of finding a new idea. v2 changes the *composition*, not the dial.

**Concept**: build the page the way a physical museum is built. Real galleries are never white or black — the **walls** are a mid-tone (putty, sage, clay), the **placards** are paper cards with dark ink, and the **display cases** are dark vitrines lit from within. The theme is that building, as three zoned surfaces coexisting on every page:

- **WALL** `#A8A296` — a true mid-tone putty ground: the literal "in-between." Carries dark-ink signage only; white type never sits on the wall.
- **PLACARD** `#F7F5EF` — paper cards for prose, labels, and exhibit text. Accents on paper are deep engraving colors (teal, rust), never luminous.
- **VITRINE** `#131720` — dark display cases used *only where luminous data earns it*: charts, interactive demos, screenshot thumbnails, verdicts. All the existing luminous accents (cyan, amber, good, bad) live exclusively behind this glass.

This is "in between" by composition rather than by averaging: light and dark genuinely coexist, zoned by function — and it resolves the underlying tension for free (instrument data looks best glowing on dark; reading is best on paper; there is still exactly one theme, no switch).

**The signature**: every exhibit card becomes a **lit case with its wall label** — dark vitrine frame holding the captured screenshot with a job-ID strip, paper placard hanging beneath with title, hook, and finding numbers. The gallery landing literally becomes a hung gallery.

### Token set (every ratio computed, not eyeballed)

| Token | Hex | Zone / role | Contrast |
|---|---|---|---|
| `--wall` | `#A8A296` | ground | ink **5.9:1** ✓ |
| `--wall-deep` | `#9C968A` | gradient floor | ink **5.1:1** ✓ |
| `--wall-ink` | `#23272E` | signage, headings on wall | — |
| `--edge-wall` | `#4A4841` | control borders on wall (1.4.11) | **3.6:1 / 3.1:1** ✓ |
| `--placard` | `#F7F5EF` | paper cards | ink **13.9:1** ✓ |
| `--placard-ink` | `#22262D` | label text | — |
| `--teal` | `#0C6B65` | accent text on paper | **5.8:1** ✓ |
| `--rust` | `#8A4A12` | secondary accent on paper | **6.3:1** ✓ |
| `--vitrine` | `#131720` | display cases | ink **15.3:1** ✓ |
| `--vitrine-2` | `#1A1F2B` | case interior wells | — |
| `--cyan` | `#5BD8CE` | signature, vitrine only | **10.4:1** ✓ (charts: needs 3:1) |
| `--amber` | `#E8B45C` | verdicts, vitrine only | **9.5:1** ✓ |
| `--good` | `#79D695` | pass, vitrine only | **10.1:1** ✓ |
| `--bad` | `#F09A90` | fail, vitrine only | **8.3:1** ✓ |
| btn: vitrine bg + cyan text | — | primary button = "a lit case" | **10.4:1** ✓ |

**Zone rules (enforced, not vibes)**: luminous accents appear only on vitrine surfaces; paper accents are deep; wall carries ink only. White-on-wall is banned (2.3:1 — the one pairing the math rejects). Verification script ships as `tools/contrast-check.js` and gates any palette edit.

### What gets deleted (the "no switching" sweep)
- The two `:root[data-theme=…]` blocks + the `prefers-color-scheme` block in museum.css → single three-zone token set.
- The `qm-theme-restore` inline script on **69 pages**; the theme button + its JS on **61 pages** (scripted removal, per-page verify).
- Per-page inline light-theme overrides where they exist. Print styles **stay** (print is a medium, not a theme — placard tokens map to print naturally).
- `<meta name="theme-color" content="#A8A296">` added site-wide for mobile chrome.

### Rejected directions (kept for the record)
- **Gallery Dusk** `#252B38` single slate ground — rejected by Creator (C4989): too close to the current dark theme. Correct diagnosis; it was a luminance change, not an idea.
- **Warm Graphite** `#2E2B28` / **Deep Harbor** `#1F3038` — same critique applies; both are single-dark-ground variants.
- **True mid-gray everything** — AA-impossible for text at L\*≈50; the three-surface composition is how a mid-tone ground becomes usable at all (the wall never carries body prose — paper does).

## 4. The entrance (new root landing)

Structure, top to bottom — ASCII wireframe:

```
┌──────────────────────────────────────────────────────────────┐
│ THE QUANTUM MUSEUM          Scoreboard · Wings ▾ · Repository │  masthead (sticky, blur)
├──────────────────────────────────────────────────────────────┤
│  IBM HERON · 2026 CAMPAIGN · ~110 EXPERIMENTS · F01–F121      │  eyebrow ticker
│  We asked a quantum computer questions                        │
│  the textbooks call impossible.                               │  display headline
│  [See the verdict →]  [Start with the switch]  [Plain words]  │  3 doors, 3 audiences
│                                                               │
│  ╔═══════╗ ╔═══════╗ ╔═══════╗ ╔═══════╗   ← THE GALLERY     │  signature element:
│  ║ shot  ║ ║ shot  ║ ║ shot  ║ ║ shot  ║     WALL — a slow    │  perspective-tilted wall
│  ╚═══════╝ ╚═══════╝ ╚═══════╝ ╚═══════╝     drift of real    │  of exhibit screenshots
│      (motion-safe: static grid if reduced)    exhibit frames  │  (real data as decor)
├──────────────────────────────────────────────────────────────┤
│  FLAGSHIP — the causal switch story (from the old root page)  │  ≥72σ narrative + stats
├──────────────────────────────────────────────────────────────┤
│  WING I — The Causal Switch          [4 cards w/ thumbnails]  │  8 wings, every card
│  WING II — …                                                  │  now bearing a captured
│  …                                                            │  screenshot thumb + alt
├──────────────────────────────────────────────────────────────┤
│  GAMES ANNEX — STATIC · Casebook · Horizons (plain language)  │  audience on-ramps
├──────────────────────────────────────────────────────────────┤
│  PROVENANCE — every number a job ID · repo · methods · .md    │  footer
└──────────────────────────────────────────────────────────────┘
```

**Signature element — the Hung Gallery**: the hero's graphic is a row of *lit vitrines* — actual exhibit screenshots in dark case frames with job-ID strips, hung on the putty wall exactly like works in a gallery (optionally a slow drift, fully disabled under `prefers-reduced-motion`, `aria-hidden` with content duplicated by the wing cards). The museum's proudest claim — *every number is measured* — becomes the literal artwork on the wall. No stock art, no abstract blobs: the decoration IS the data, behind glass.

**The graphics pipeline** (`tools/museum-shots.js`, proven this cycle):
- playwright-core + system Chromium; per-exhibit manifest: URL, viewport, optional **pre-interaction** (e.g. decoder-race fires 100 shots first so its thumbnail shows the mid-consensus state; the switch drags coherence to the sweet spot) and capture target (element selector).
- Output `demo/shots/<slug>.jpg` (JPEG q≈80, 1× DPR, ~10–80 KB each; the proof capture is 12 KB). WebP later if tooling (`cwebp`/`sharp`) is added — not required.
- Cards `loading="lazy"`, fixed `aspect-ratio` (no layout shift), meaningful `alt` per exhibit.
- Re-run manually whenever exhibits change; outputs are committed (GitHub Pages is static).
- **Proof of concept exists**: `demo/shots/decoder-race.jpg` rendered inside the tile's exhibit card.

## 5. The exhibit lift

- **Tokens cascade**: all 45 exhibits import museum.css, so the three-zone token set restyles them in one edit — the wall ground lands on `body`, and the existing `.panel`/`.card` classes map to the vitrine and placard treatments respectively. Exhibit pages become what they already are semantically: prose placards between lit instrument cases. Their luminous data colors barely change (they already live on dark panels); the room around them changes.
- **Hardcoded-hex audit**: scripted grep across `demo/*/index.html` for `#RRGGBB` literals; each mapped to a token (`#ef4444` → `--bad`, etc.) or consciously kept (SVG art). Estimated small: the design system already pushed most color through vars.
- **Shared masthead**: exhibits get one consistent top bar (museum brand ← back-link, wing label, provenance chip) replacing today's per-page ad-hoc topbars — one class in museum.css, one markup swap per page.
- **Verification contact sheet**: the screenshot pipeline doubles as QA — after the sweep it captures all 45 exhibits and the landing; one eyeball pass catches any page the retheme broke.

## 6. Accessibility — AA as a checklist, not a vibe

Already in place (kept): skip links, `sr-only` texts, focus-visible outlines, prose-link underlines, reduced-motion guards, print styles.

To be enforced across the redesign:
1. **Contrast**: every token pair per §3 table (small text ≥4.5:1, large/bold ≥3:1, non-text UI ≥3:1) — `tools/contrast-check.js` is the gate.
2. **Non-text contrast (1.4.11)**: interactive controls use `--edge-strong` (3.7:1); chart marks use `--cyan-ui`/`--amber` (≥3:1 on ground).
3. **Never color-only (1.4.1)**: status tags keep words; demo cells keep digits/glyphs alongside color (decoder-race already does).
4. **Images (1.1.1)**: every thumbnail gets a specific alt ("40 vote columns climbing out of the coin-flip band"), not "screenshot".
5. **Structure**: one `h1` per page, landmark roles, wing sections labelled (`aria-labelledby` — already present on demo/index, carried over).
6. **Keyboard**: all demos operable via native inputs (they are — buttons/ranges); tab-order smoke test on the 5 most interactive exhibits.
7. **Focus (2.4.7)** on the dusk ground: 2px `--cyan` outline, 3px offset (in the tile).
8. **Target size**: buttons ≥24×24 CSS px (current buttons pass).
9. **Reflow (1.4.10)**: 320 px width, 200 % zoom checks on landing + 3 exhibit archetypes.
10. **Motion (2.3.3)**: gallery-wall drift and card hovers fully disabled under `prefers-reduced-motion: reduce`.
11. **Automated pass**: axe-core via playwright over all 69 pages (landing, exhibits, specs); violations to zero or documented-n/a.

## 7. Phases, estimates, risks

| Phase | Work | Size |
|---|---|---|
| **P0** | museum.css → Gallery Dusk single token set + atmosphere; formalize `tools/contrast-check.js` | S (1 cycle) |
| **P1** | Theme-machinery sweep: remove restore-script/buttons/overrides on 69 pages (scripted + spot checks) | M (1–2 cycles) |
| **P2** | `tools/museum-shots.js` + manifest + capture all 45 exhibits + commit shots | M (1–2 cycles) |
| **P3** | New entrance at root (hero, gallery wall, flagship section, 8 wings w/ thumbnails, annex, footer); `demo/` redirect stub | L (2–3 cycles) |
| **P4** | Exhibit lift: shared masthead swap + hardcoded-hex audit across 45 exhibits | M (2 cycles) |
| **P5** | AA pass: axe-core sweep, keyboard/zoom/reflow checks, contact-sheet review, fixes | M (1–2 cycles) |

Total ≈ 8–12 cycles. Phases are independent enough to ship incrementally (P0+P1 alone already deliver "one theme everywhere"); P3 waits on P2's thumbnails.

**Risks / mitigations**
- *A 12-KB JPEG per card × 45 ≈ manageable (<2 MB landing)*; lazy-loading keeps first paint light. If weight creeps, capture at lower quality or add WebP tooling.
- *Sweep regressions on 69 pages* → contact-sheet QA (P5) is specifically the net for this.
- *Exhibits with bespoke dark-tuned SVG art* may need per-page nudges — budgeted inside P4.
- *OG/social cards* reference current URLs — root swap keeps URLs, so only descriptions need refreshing (inside P3).

## 8. Proof artifacts already in the repo (this cycle — proposal only)

- `demo/museum-redesign-tile.html` — **DELETED 2026-08-11** (Creator, board #27). It held all 11 of the museum's remaining 1.0:1 contrast defects and was linked from no museum page. The link is removed rather than left dangling; the file is recoverable from git history if the redesign is revived.
- `demo/shots/decoder-race.jpg` — first pipeline capture, rendered in the tile's card.

## 9. Open questions for Creator

1. **Theme**: does "The Layered Museum" (v2) land? Wall temperature is tunable (current putty `#A8A296`; sage `#9FAA9B` and slate-blue `#96A3B4` are drop-in wall swaps with the same zone rules) — pick a wall color preference if any.
2. **Horizons + Scoreboard**: restyle inside this effort (adds ~1 cycle to P4) or follow-up? (Recommend: inside — they're both linked from the entrance.)
3. **Gallery-wall motion**: slow drift (motion-safe) vs fully static wall — comfort call.
4. **Root hero headline**: keep "questions the textbooks call impossible" (recommended) or return to the old root's "order of events into superposition" line?
5. Green-light order: full sequence P0→P5, or P0+P1 first as a taste before committing the rest?
