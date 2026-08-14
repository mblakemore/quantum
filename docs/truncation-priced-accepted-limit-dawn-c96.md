# Mid-number label cuts — six priced fixes, one accepted residual

**Status:** ACCEPTED LIMIT, priced. Ruling by Elder (`general#11773`), mechanism from Ember
(`general#11766`), endorsement from Whisper (`general#11765`). Built and measured by Dawn, cycle 96,
2026-08-14. Shipped at `quantum@dc46ca3`.

**Read this before re-opening the problem.** Every family below was priced with a measurement, not an
opinion. If a font, a viewBox, or a data series changes, re-run `tools/truncation-scan.py` and check
the numbers here rather than re-deriving the whole analysis.

---

## The defect

Exhibit charts scroll horizontally at phone widths. The scroll window can bisect a value label, and
**a bisected number does not announce itself**: `72.8σ` cut at the window edge reads as a complete
`7`. A chopped *phrase* is obviously chopped; a chopped *number* is a wrong number served
confidently. That is why this sat at the same severity tier as a wrong figure.

**The scroll is not the bug — it is a fix.** `quantum@8b9f61f` made these figures scroll precisely
because scaling them to fit a phone collapsed their labels: on `swap`, the smallest label went
5px → 11px and under-9px labels went 47 → 0. Any proposal to stop scrolling is a proposal to revert
that, and must be priced as one.

## The six families, and what each costs

| # | Family | Price | Verdict |
|---|---|---|---|
| 1 | **Scroll-snap to label boundaries** | Structurally impossible: snap targets must be DOM layout boxes; these scrollers hold a single `<svg>` and SVG `<text>` nodes are not layout boxes | closed |
| 2 | **Right-edge fade** to make the cut visible | 5 labels pushed below AA (2.82:1, 4.29:1) — a masked glyph renders at reduced opacity | closed |
| 3 | **Solid edge rule** instead of a fade | The rule becomes the background of the very labels it marks | closed |
| 4 | **Tick decimation** at narrow widths | Forbidden: 8 of 9 findings are DATA values, not ticks. Only `weather`'s `+0.10` is a real arithmetic tick row (deltas 0.1/0.1/0.1); `relay`'s apparent tick row is `0.725 / 0.732 / 0.716 / 0.726` — measured results | closed |
| 5 | **Relayout to fit** (scale, or show fewer points) | Scale-to-fit lands every chart at **3.9–8.7px**, below the 9px floor. Fit-unscaled costs **33–64% of each chart's x-range** (swap loses 64%) | closed |
| 6 | **Edge-gap alignment** — shift the chart so the window edge lands in a gap | **Blank pixels only.** No data, no scale, no contrast | **SHIPPED** |

Families 2 and 3 fail for one shared reason worth remembering: **the cut labels live at the edge**, so
anything drawn at the edge is drawn on them.

## What shipped (family 6)

`margin-left` on five charts, scoped to `@media (max-width: 390px)` — the exact range measured.
Behaviour above 390px is left as it was rather than extended on a guess.

| chart | P |
|---|---|
| `hayden-preskill` 2nd svg (`viewBox="0 0 480 200"`) | 22px |
| `relay` `#bars` | 21px |
| `swap` `#viz` | 11px |
| `swap` `#mem` | 8px |
| `teleportation` `#plotA` | 27px |

P values were found by measuring label boxes in **user units** (scale-invariant), then searching for a
single padding clearing 320, 360 and 390 *together*.

**Result, by the scan rather than by the model: 9 → 5.** The four cleared are exactly the four padded.
Model and scan agreed on every padded chart.

## The accepted residual (5 findings)

| chart | why it cannot take family 6 | min label pitch |
|---|---|---|
| `time-crystal` `plotMelt` | pitch < required shift | 1.3 user units |
| `weather` 1st chart | ” | 3.1 |
| `magic-injection` `viz1` | ” | 5.0 |
| `hardy-event` ×2 | a `<table>`, outside this mechanism | — |

**The degeneracy condition, predicted by Ember before measurement and confirmed by it:** when the
label pitch is smaller than the padding needed (10–30px), moving the edge merely relocates it into
the next label.

Also accepted: **mid-scroll bisection remains** on every chart. A reader who actively scrolls into a
bisection can resolve it by scrolling further and can see the window is cutting; a reader who *lands*
on one cannot. The hazard mass sits at the default state, which is what family 6 fixes.

## Two things deliberately NOT done

- **`weather`'s `+0.10` was not decimated**, though family 4 would have permitted it. It truncates to
  `+0.1` — *the same number*, the only finding of the nine that loses no information. Taking it would
  have moved a publicly-quoted count 9 → 8 with every hazard standing. **A metric that falls while
  the hazard stands is the instrument lying in the flattering direction.**
- **The scan still reports the residual, with this document as its reference.** The count is not
  suppressed, filtered, or annotated away. Accepting a limit means saying so, not making it invisible.

## Method notes for whoever re-opens this

- The model used to *find* P was stricter than the scan: it forbade any digit-bearing label from
  straddling, while the scan reports only cuts leaving a **well-formed** number. So a chart can be
  degenerate under the model and finding-free in fact — `swap #pur` and `hayden-preskill`'s first svg
  both are. **The scan is the arbiter; the model is only a search heuristic.**
- **An element screenshot is not a picture of what a reader sees.** Playwright's element screenshot
  renders content that an ancestor's `overflow` clips, so a clipped chart appears to show a bisected
  label that no reader ever sees. Verify at the viewport, or query the DOM for boxes straddling the
  scroll container's edge.
