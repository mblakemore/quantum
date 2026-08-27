# Inert classes: four answered questions

**Status:** ANSWERED — four purposeful, no defect. Answered by Dawn, cycle 99 (three) and 2026-08-27 (the fourth)
(board#224). This document is the authority `dawn/tools/accepted/inert-class.json` cites.

`tools/inert-class-scan.py` asks a question rather than reporting a defect: *does this class change
anything a reader can see?* A class can be inert on purpose — a JS state hook, a selector target, or
a class whose rules style only its CHILDREN — so the scan says so on its face and leaves the
judgement to the author.

Three have been asked on every run for weeks. All three were re-read in source and all three are
purposeful.

## The accepted residual (4 answered)

| class | where | why it is inert HERE, and correct |
|---|---|---|
| `.val` | `horizons.html` (5 sites) | Styles its CHILDREN, not itself. `.field .val{color:var(--text)}` computes identical to inherited, but `.field.result .val b{color:var(--cyan)}` is a live selector target (`horizons.html:130-132`). |
| `.mono` | `demo/switch/index.html` | Redundant, not inert-by-mistake: `font-family:var(--mono)` + `tabular-nums` on a `<b>` already inside a mono container (`demo/switch/index.html:62`). |
| `.figure` | `demo/trust-ladder/index.html` | A JS state hook AND an animation target — `.cert .bignum.dissolve .figure` (`:108`, `:120`), queried at `:277`. |

Keyed on **(class, page)**: the same class on a NEW page is a NEW question and surfaces. The count
above is what the ledger must match, and a mismatch makes the ledger unusable rather than merely
noisy.

## Why this is a document and not the board row

It was board#224 at first, and closing that row broke the ledger — correctly. `accepted_limits.py`
refuses a CLOSED row as an authority on the grounds that closing is how a decision is retired, and
that rule is right for a decision. **It is wrong for a RECORD.** A row that records an answer gets
closed when the recording is done, which is the opposite of the answer being withdrawn.

So the rule stands and the authority moved. A ruling that must outlive a work item belongs in a
document; a task row is a work item with a lifecycle, and its lifecycle will eventually contradict
the ruling it was carrying.


## The fourth (added 2026-08-27, Dawn)

`.excl` on an `<i>` in `demo/causal-compass/index.html` — the legend swatch for a set withdrawn
before decode.

**Re-read in source and MEASURED in the browser, not judged by eye.** The rule is a descendant
selector, `.lgd i.excl { border-style: dashed }`, and the scanner looks for a bare `.excl` rule, so
it cannot see it. Computed style on the live page: the `.excl` swatch renders `dashed` where its
`.cc` sibling renders `solid`. The class changes what a reader sees, which is exactly what the
scan asks.

**So this is a scanner limitation, not a page defect** — and it will recur for any purposeful class
styled only through a descendant selector. Recorded here rather than fixed in the scanner because
resolving arbitrary CSS specificity is a bigger instrument than this question deserves; the answer
is cheap and the question is rare.
