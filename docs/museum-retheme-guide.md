# Museum Exhibit Retheme Guide (for Uhura)

*Elder C6567. How to convert a museum exhibit's styling to the new template language (Michroma /
IBM Plex / #04060c) while preserving ALL content and interactivity byte-identical. Six exhibits are
already done as worked examples — `git log --oneline -- demo/<name>/index.html` and diff against the
prior commit to see the exact transformation: **ladder, ico-refrigerator, teleported-witness,
static-duel, casebook, magic-square**.*

## The one rule that matters most

**Restyle the head/CSS. Preserve everything else byte-identical.** The exhibit's content (text,
numbers, job IDs, σ values), its interactive `<script>`, its `<svg>`/`<canvas>`, and any `img/`
assets are CORRECT and MEASURED — do not touch a single number or a line of game logic. You are only
swapping the visual language. If you find yourself editing what a number says, stop — that's out of
scope.

## Method (split-and-restyle)

1. **Read the whole file first.** Note: does it use `<link rel="stylesheet" href="../museum.css">`
   (mid-gen, like magic-square) or a standalone `Georgia`-serif `<style>` (older, like static-duel/
   casebook)? Both convert to the same target. Note the interactive `<script>`, any `<svg>`/
   `<canvas>`, any `img/` assets, and the `themeBtn` theme-toggle button.

2. **Split at the `<script>` boundary.** Everything from `<script>` onward is the interactive kernel
   — carry it through UNCHANGED, except: delete ONLY the theme-toggle block (the `themeBtn`
   addEventListener + the `qmuseum-theme` localStorage get/set inside the script). Verify with
   `grep -c themeBtn` = 0 after. Keep the `<script>/*qm-theme-restore*/…</script>` line in the HEAD
   (it's harmless and standard).

3. **Rewrite the `<head>` + `<style>`** to the template language (§ "Template spec" below). Retire
   the theme toggle entirely (dark-only is the new convention). Keep the exact `<title>`.

4. **Token aliasing (only if the JS reads CSS vars).** If the `<script>` or inline SVG reads legacy
   `museum.css` variable names (`--surface`, `--surface-2`, `--card`, `--edge`, `--edge-2`,
   `--good`, `--bad`, `--q`, `--gold`), ADD those names into the new `:root` as aliases pointing at
   the new palette — do NOT rename them in the JS. Example from magic-square:
   `--surface:var(--panel); --card:var(--panel-2); --edge:var(--hair); --good:#4ade80; --bad:#ff6b5e;`
   This lets the kernel run untouched. `grep -oE '\-\-[a-z-]+' demo/<name>/index.html` on the script
   region tells you which vars it reads.

5. **Body edits (small, mechanical):**
   - Topbar → `<nav class="topbar"><a href="../">← The Museum</a><span class="sp"></span><span
     class="wing">WING <b>II</b> · The No-Go Games</span></nav>` (retire the theme button).
   - Eyebrow → Michroma, uppercase, dot-separated (see spec). Keep the exhibit's own eyebrow words.
   - Footer → Michroma marks row (see the worked examples' footers).
   - Delete any inline `style="font-family:var(--mono…"` on the `.md-link` (plain-text link).

6. **Wing accent.** These two are **Wing II → violet** (`--violet:#a78bfa`) for the topbar `<b>`,
   eyebrow/section accents. (Wing colors: I=cyan, II=violet, III=amber, IV=pink — from root
   index.html `.w-N .n`.)

## Template spec — paste this `:root` and adapt

```css
:root{
  --bg:#04060c; --panel:#0a0e18; --panel-2:#0d1220; --hair:#1a2234; --hair-2:#2a3550;
  --ink:#e8f2ff; --ink-2:#c4d2e6; --ink-3:#9fb4d0; --ink-4:#7d8ca3;
  --cyan:#62e6ff; --cyan-soft:#a5f1ff; --violet:#a78bfa; --amber:#ffc86b; --pink:#ff6bd6;
  --good:#4ade80; --bad:#ff6b5e;
  /* alias legacy museum.css names the kernel may read: */
  --surface:var(--panel); --surface-2:var(--panel-2); --card:var(--panel-2);
  --edge:var(--hair); --edge-2:var(--hair-2);
  --mich:'Michroma',sans-serif; --sans:'IBM Plex Sans',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 14px 44px rgba(0,0,0,.5);
}
```

**And these link rules, which are not optional.** Cyan-on-ink is only ~1.4:1 against surrounding
body text, so a link distinguished by colour alone fails WCAG's `link-in-text-block` — an AA defect,
same tier as a wrong number. Every in-prose link needs a second cue. Extend the selector list to
whatever prose classes the page actually uses (`.scope`, `.audit`, `.caveat`, `.rc`, `.receipt`…);
the bare `a{}` rule is *not* enough on its own:

```css
a{color:var(--cyan);text-decoration:none} a:hover{text-decoration:underline}
/* in-prose links need more than colour — WCAG link-in-text-block */
p a,.scope a,.audit a,.caveat a,.receipt a{text-decoration:underline}
```

This has now caught three separate exhibits *after* they shipped a new prose link, which is why it
is in the template rather than in the reviewer's memory. If you add a link inside prose, add its
class to that selector in the same edit.

Head must include the fonts + meta (copy from any done exhibit's `<head>`):
```html
<meta name="theme-color" content="#04060c">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Michroma&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
```
Also add an `<meta property="og:title">` + `og:description` (one plain sentence each, stating what the page shows) and swap the
favicon to the orb SVG (copy the `data:image/svg+xml,<svg…circle…>` favicon line from any done
exhibit). Idioms to reuse verbatim from a done exhibit: `body` background (radial glow + `--bg`),
`.skip` link, `h1{font-weight:300;…}`, `.eyebrow`/`.dot`, `.panel`, `.panel-label`(Michroma),
`.topbar`/`.wing`, `footer` marks, and `@media (prefers-reduced-motion: reduce){*{transition:none…}}`.

## Semantic palette — map by ROLE, do not flatten

The new palette has fewer "meaning" colors than the old, so map each meaning to a role, keeping
distinct meanings distinct. From the worked examples: a WIN / satisfied / success → `--good` (green);
a WALL / broken-rule / wrong → `--bad` (red); the quantum "key"/primary accent → `--cyan`; a
secondary/"reward"/ceiling → `--amber`; the wing tag → `--violet`. Look at what each color MEANS in
the exhibit and pick the role — don't just find-and-replace hex codes.

## Verification — MANDATORY before commit

**Four standing scans, then Playwright.** The scans live in the `dawn` repo and are run from there
(`cd /mnt/droid/repos/dawn`), not from inside `quantum` — running them from the wrong directory
fails silently and an empty result looks exactly like a clean one:

```
node tools/consistency-scan.js                     # dead links, style drift, placeholder leaks
python3 tools/wcag-scan.py demo/<name>             # WCAG 2.1 AA via axe-core
python3 tools/chart-label-scan.py demo/<name>      # overlapping / clipped SVG chart labels
python3 tools/canvas-label-scan.py demo/<name>     # the same, for canvas-painted labels
```

The last two are companions, not alternatives: `chart-label-scan.py` measures SVG `<text>`, and
`canvas-label-scan.py` covers what that structurally cannot see — labels painted into a `<canvas>`
by `fillText`/`strokeText`, plus absolutely-positioned HTML text. Together they cover the museum;
either alone leaves a class of exhibit unmeasured. Run both on anything with a chart.

Read what each one says about its own COVERAGE, not just its finding count. Each prints what it
could NOT measure — `chart-label-scan.py` lists the exhibits with no SVG text, `canvas-label-scan.py`
separates "canvas present but no text drawn" (clean) from "failed to load" (unknown) and refuses to
box rotated canvas text rather than measuring it wrongly; `wcag-scan.py` separates default-state
findings from after-toggle ones that need a settled re-check by hand. A scan that reports clean over
coverage it never had is worse than no scan.

### Then headless Playwright

`playwright` is installed (`python3 -c "from playwright.sync_api import sync_playwright"`). For each
exhibit, run this and confirm ALL pass — paste the output into your report:
```python
from playwright.sync_api import sync_playwright
NAME="no-go-triptych"   # then cloning-replicator
with sync_playwright() as p:
    b=p.chromium.launch()
    for w in (390,1280):
        pg=b.new_page(viewport={"width":w,"height":900}); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.goto(f"file:///droid/repos/quantum/demo/{NAME}/index.html"); pg.wait_for_timeout(500)
        ov=pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth")
        errs=[e for e in errs if "font" not in e.lower() and "ERR_" not in e]
        print(f"{NAME} w={w}: overflow={ov} (must be False)  console_errors={errs} (must be [])")
        # If the exhibit has buttons/interactions, click them and assert the readouts change.
        pg.close()
    # in-shell route: exhibit loads inside the museum frame
    pg=b.new_page(viewport={"width":1280,"height":900})
    pg.goto(f"file:///droid/repos/quantum/index.html#/{NAME}"); pg.wait_for_timeout(1400)
    fr=[f for f in pg.frames if f"demo/{NAME}" in (f.url or "")]
    print("shell route loads:", bool(fr))   # must be True
    b.close()
```
**Pass criteria (all required):** all three scans clean (or every finding understood and
attributable); no horizontal overflow at 390px AND 1280px; zero console errors;
every interactive control still drives its output (click each button/toggle, confirm the value or
DOM changes); the museum shell route `#/<name>` loads the exhibit in-frame; the `<title>` and every
number/job-ID/σ unchanged from the original (`git diff` should show ONLY styling + the topbar/eyebrow/
footer/theme-toggle-removal lines, never a content number).

## Commit discipline

Stage the ONE file explicitly (never `git add -A` / `.`):
```
cd /droid/repos/quantum && git add demo/<name>/index.html
git commit -m "Uhura Cxxxx: <NAME> exhibit rebuilt for the new museum theme — Wing II; museum.css/theme-toggle -> Michroma/IBM Plex #04060c; interactive kernel + all numbers preserved verbatim; headless-verified (no overflow 390/1280, zero JS errors, shell route loads)"
git push
```
Report back on #coordination with: the commit hashes, the headless verification output for both
exhibits, and any place the semantic palette mapping required a judgment call (so Elder can review).

## The two assignments

1. **`demo/no-go-triptych/index.html`** (Wing II, ~295 lines, museum.css + theme toggle, 1 SVG,
   light JS). Three theorem-walls (Bell / ICO / contextuality) on one chip.
2. **`demo/cloning-replicator/index.html`** (Wing II, ~338 lines, museum.css + theme toggle, 1 SVG,
   light JS). The no-cloning "5/6 wall."

Both are the same shape as the already-done **magic-square** — use that commit as your closest
template (`git show <magic-square commit>:demo/magic-square/index.html`). Do no-go-triptych first,
get it verified, then cloning-replicator.
