# The Quantum Museum — 2026 Redesign Plan

**Status**: PROPOSAL — awaiting Creator approval (options are marked; nothing here is implemented except the two proof artifacts noted in §8)
**Author**: Whisper C4989 (plan requested by Creator 2026-07-23)
**Companion artifact**: [`museum-redesign-tile.html`](museum-redesign-tile.html) — the proposed theme rendered live: palette with printed contrast ratios, type specimen, masthead, an exhibit card with a real captured thumbnail, controls, verdict voice, and two alternate directions.

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

## 3. One theme: "Gallery Dusk" (recommended — see tile)

**Concept**: a museum open at night. Twilight-slate walls — unmistakably not black, unmistakably not paper — warm limestone type, and section lighting done with soft radial "spotlight" washes (one warm, one cool) over a subtle top-to-bottom gradient. The existing cyan instrument signature survives (it is the campaign's identity across 45 exhibits) but is retuned for the mid-tone ground.

**Why not a true mid-gray**: backgrounds near L\*50 make 4.5:1 unreachable for *both* light and dark text — AA forces the ground to commit. L\*≈30 slate is the honest "in-between": it reads as neither mode, keeps luminous accents, and passes AA with headroom everywhere.

### Token set (every ratio computed, not eyeballed)

| Token | Hex | Role | Contrast (on bg / on card) |
|---|---|---|---|
| `--bg` | `#252B38` | ground | — |
| `--bg-deep` | `#1F2530` | gradient floor, thumbnail wells | — |
| `--surface` | `#2C3342` | panels | — |
| `--card` | `#303950` | exhibit cards | — |
| `--edge` | `#4A546E` | decorative hairlines | 1.9:1 (decorative only) |
| `--edge-strong` | `#78839E` | control borders (WCAG 1.4.11) | **3.7:1 / 3.0:1** ✓ |
| `--ink` | `#EFECE3` | primary text (warm limestone) | **12.0:1 / 9.7:1** ✓ |
| `--ink-2` | `#C2C6D2` | secondary text | **8.3:1 / 6.7:1** ✓ |
| `--ink-3` | `#9BA3B5` | captions, eyebrows | **5.6:1 / 4.5:1** ✓ |
| `--cyan` | `#6FDCD3` | signature, links, wins | **8.7:1 / 7.0:1** ✓ |
| `--cyan-ui` | `#3FBDB3` | chart fills, range accents | **6.2:1** ✓ (needs 3:1) |
| `--amber` | `#EFB964` | verdicts, graded results | **8.0:1 / 6.5:1** ✓ |
| `--violet` | `#B3A9F5` | secondary wing accent | **6.7:1** ✓ |
| `--good` | `#7ED99A` | pass/live | **8.3:1** ✓ |
| `--bad` | `#F59B92` | fail/wrong | **6.7:1 / 5.5:1** ✓ |
| btn text on `--cyan` | `#12261F` | primary buttons | **8.7:1** ✓ |

Verification script ships as `tools/contrast-check.js` (exists as scratch; formalized in Phase 0) and runs in CI-style before any palette edit lands.

### What gets deleted (the "no switching" sweep)
- The two `:root[data-theme=…]` blocks + the `prefers-color-scheme` block in museum.css → single token set.
- The `qm-theme-restore` inline script on **69 pages**; the theme button + its JS on **61 pages** (scripted removal, per-page verify).
- Per-page inline light-theme overrides where they exist. Print styles **stay** (print is a medium, not a theme).
- `<meta name="theme-color" content="#252B38">` added site-wide for mobile chrome.

### Alternates considered (anchors contrast-checked, not developed)
- **B · Warm Graphite** `#2E2B28` ground — "printed matter after dark." Passes AA (ink 11.8:1). Risk: abandons the observatory-blue identity every exhibit already carries.
- **C · Deep Harbor** `#1F3038` blue-green, amber-led. Passes AA. Risk: reads closer to the current dark theme than to a third thing.
- Recommendation: **A · Gallery Dusk**. The tile renders A; B/C are one-token-set swaps if Creator prefers their temperature.

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

**Signature element — the Gallery Wall**: the hero's graphic is a perspective-tilted strip of *actual exhibit screenshots* (the decoder-race skyline, the switch cosine curve, the scoreboard bars…), drifting slowly (CSS transform animation, fully disabled under `prefers-reduced-motion`, `aria-hidden` with the content duplicated by the wing cards). The museum's proudest claim — *every number is measured* — becomes the literal wallpaper. No stock art, no abstract blobs: the decoration IS the data.

**The graphics pipeline** (`tools/museum-shots.js`, proven this cycle):
- playwright-core + system Chromium; per-exhibit manifest: URL, viewport, optional **pre-interaction** (e.g. decoder-race fires 100 shots first so its thumbnail shows the mid-consensus state; the switch drags coherence to the sweet spot) and capture target (element selector).
- Output `demo/shots/<slug>.jpg` (JPEG q≈80, 1× DPR, ~10–80 KB each; the proof capture is 12 KB). WebP later if tooling (`cwebp`/`sharp`) is added — not required.
- Cards `loading="lazy"`, fixed `aspect-ratio` (no layout shift), meaningful `alt` per exhibit.
- Re-run manually whenever exhibits change; outputs are committed (GitHub Pages is static).
- **Proof of concept exists**: `demo/shots/decoder-race.jpg` rendered inside the tile's exhibit card.

## 5. The exhibit lift

- **Tokens cascade**: all 45 exhibits import museum.css, so the single Gallery Dusk token set restyles them in one edit. The atmosphere (gradient ground + spotlight washes) moves into museum.css `body` so exhibits inherit the entrance's light.
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

- [`demo/museum-redesign-tile.html`](museum-redesign-tile.html) — the theme, live; not linked from any museum page; `noindex`.
- `demo/shots/decoder-race.jpg` — first pipeline capture, rendered in the tile's card.

## 9. Open questions for Creator

1. **Theme direction**: A · Gallery Dusk (recommended) — or B/C temperature from §3?
2. **Horizons + Scoreboard**: restyle inside this effort (adds ~1 cycle to P4) or follow-up? (Recommend: inside — they're both linked from the entrance.)
3. **Gallery-wall motion**: slow drift (motion-safe) vs fully static wall — comfort call.
4. **Root hero headline**: keep "questions the textbooks call impossible" (recommended) or return to the old root's "order of events into superposition" line?
5. Green-light order: full sequence P0→P5, or P0+P1 first as a taste before committing the rest?
