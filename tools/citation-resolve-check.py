#!/usr/bin/env python3
"""Every F-number cited in published material must RESOLVE to a ledger row.

board#263 (Dawn): demo/ladder/spec.md — a PUBLISHED spec sheet — carries two measured-claims
entries citing F11 and F18. Neither resolves. The ledger runs F01 and then jumps to F48, so
those numbers have never existed in it. A reader following the citation finds nothing, and a
claim whose provenance cannot be followed is an assertion wearing a citation's clothes.

This is the same rule the board applies to `evidence` and the same one I applied to my own
board writes this morning: a reference that does not resolve is not a reference. The
difference is that the board's evidence field is internal and this material is published.

WHY A CHECK AND NOT A CORRECTION. Fixing F11 and F18 fixes two lines. The class is "any
citation anywhere in published material that names a finding the ledger does not have", and
nothing was watching it — Dawn found these by extending a provenance scan to F-numbers, which
it had never covered. So the deliverable is the scan, and the two known instances are its
first controls.

⚠️ SCOPE, stated because a pass here is narrow. This checks that a cited F-number EXISTS as a
row in the ledger. It does NOT check that the row says what the citing document claims it
says. A citation can resolve and still misdescribe its source; that is a different and harder
check, and calling this one "citations verified" would overclaim it.

Usage:  python3 tools/citation-resolve-check.py [--roots demo docs findings]
Exit:   0 every cited F-number resolves · 1 dangling citation(s) found
        2 the ledger itself could not be read — UNKNOWN, never a pass
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "docs", "campaign-arcs.md")
# F0 is excluded: findings are numbered from 01, and a red-team audit doc legitimately uses
# F0/F1 as its OWN internal section labels ("F0 (the blocker) — the executed witness is
# defective"). Counting those as dangling citations accuses a document of mis-citing a corpus
# it was never referring to. The F-prefix is not owned by the findings ledger.
FNUM = re.compile(r"\bF([1-9]\d{0,2})\b")
TEXT_EXT = {".md", ".html", ".htm", ".txt", ".json", ".py", ".js", ".sh"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def ledger_numbers():
    """AUTHORITY = the ledger rows UNION the F-numbered files in findings/.

    ⚠️ The first version used campaign-arcs.md alone, and that was the same defect I had just
    finished diagnosing in the board's prior-art gate: I named ONE corpus as the authority when
    the thing being looked up lives in two. It flagged F84 as a dangling citation across 16
    files while findings/F84-window-quality-....md sits in the repo — F84 is a real finding
    that is merely ABSENT FROM THE LEDGER. A check whose authority is too narrow does not
    report "unknown"; it reports a confident false accusation against correct work, which is
    worse than reporting nothing.

    So: a citation resolves if EITHER source knows the number. A number in findings/ but not in
    the ledger is a real gap and worth its own report — but it is a LEDGER-COVERAGE problem,
    not a broken citation, and conflating the two would send someone to fix the wrong file.
    """
    nums = set()
    try:
        with open(LEDGER, encoding="utf-8") as fh:
            nums |= {int(n) for n in FNUM.findall(fh.read())}
    except OSError:
        raise
    fdir = os.path.join(REPO, "findings")
    filed = set()
    # WHICH FILE(S) CLAIM EACH NUMBER. A set cannot answer that, and the question matters:
    # two distinct findings both numbered 16 make every "F16" citation resolve to an ambiguous
    # target, which an existence check reports as a clean pass. Collisions are the failure mode
    # a resolver is structurally blind to — it asks "does this number exist", and two answers
    # is still yes.
    by_num = {}
    if os.path.isdir(fdir):
        for fn in os.listdir(fdir):
            # THREE NAMING ERAS, and I widened this authority FOUR times before it
            # stopped accusing correct work. Early findings are "finding-46-...md"; later ones
            # are "F84-...md". That split is exactly why the ledger shows an F2-F47 gap — the
            # pre-F-scheme findings were never retro-numbered into it. A checker that knows
            # only the current convention will confidently report the whole previous era as
            # broken citations.
            #
            # ⚠️ FOURTH WIDENING, and this one accused a PUBLISHED page. The oldest era is a
            # bare two-digit prefix — 43 files, "03-x-basis-noise-immunity.md" — matching
            # neither "F84-" nor "finding-46-". So the check reported F3/F5/F11/F18 dangling on
            # demo/ladder/spec.html, and three of those four resolve perfectly with content that
            # matches the citing line word for word ("X-basis immunity" -> 03-x-basis-noise-
            # immunity, "gate-overhead law" -> 11-gate-overhead-law). I was one edit away from
            # "correcting" a correct citation on published material because MY authority was
            # incomplete. Each widening felt like the last one; the honest read is that an
            # authority assembled from the conventions I happen to know about is a guess, and
            # the corpus is what should be enumerated.
            #
            # ⚠️ AND WIDENING MAKES THIS CHECK BLIND TO THE ONE REAL ERROR IT SURFACED. With the
            # third era admitted, F18 now RESOLVES — and the citation is still wrong: the page
            # says "H-gate surgery (F18)" while finding 18 is gradual-transition/Pearl and the
            # H-gate work is finding 16. Existence passes, content is false. That is this tool's
            # documented scope limit arriving as a live miss rather than a caveat, and it is why
            # the SCOPE note at the top of this file is not boilerplate.
            m = (re.match(r"^F(\d{1,3})[-_.]", fn)
                 or re.match(r"^finding-(\d{1,3})[-_.]", fn)
                 or re.match(r"^(\d{1,3})-", fn))       # <- THIRD era, added after it accused a page
            if m:
                n = int(m.group(1))
                filed.add(n)
                by_num.setdefault(n, []).append(fn)
    collisions = {n: sorted(v) for n, v in by_num.items() if len(v) > 1}
    return nums | filed, nums, filed, collisions


def scan(roots, known):
    dangling = {}
    for root in roots:
        base = os.path.join(REPO, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.abspath(path) == os.path.abspath(LEDGER):
                    continue
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        text = fh.read()
                except OSError:
                    continue
                for n in {int(x) for x in FNUM.findall(text)}:
                    if n not in known:
                        rel = os.path.relpath(path, REPO)
                        dangling.setdefault(n, []).append(rel)
    return dangling


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="*", default=["demo", "docs", "findings", "exhibits"])
    a = ap.parse_args()

    try:
        known, in_ledger, filed, collisions = ledger_numbers()
    except OSError as e:
        print(f"UNKNOWN: cannot read the ledger ({e}). This is NOT a pass — nothing was checked.")
        sys.exit(2)
    if not known:
        print("UNKNOWN: the ledger yielded zero F-numbers. Refusing to call every citation "
              "dangling on the strength of an empty authority.")
        sys.exit(2)

    print(f"  authority: {len(known)} F-number(s) — {len(in_ledger)} in the ledger, "
          f"{len(filed)} filed under findings/")
    only_filed = sorted(filed - in_ledger)
    if only_filed:
        print(f"  note: {len(only_filed)} finding(s) exist as files but are MISSING FROM THE LEDGER "
              f"({', '.join('F%d' % n for n in only_filed[:8])}"
              f"{' ...' if len(only_filed) > 8 else ''}) — a ledger-coverage gap, reported here")
        print("        because it is real, but NOT counted as a broken citation.")
    dangling = scan(a.roots, known)

    # COLLISIONS: two files claiming one number. Reported always; GATES only when the colliding
    # number is actually cited, because that is when a reader following the citation lands on an
    # ambiguous target. An uncited collision is housekeeping, and a check that refuses for
    # housekeeping teaches people to bypass it. (The discriminator: a property gates only if it
    # covers a risk no stronger check already covers — otherwise it prints.)
    cited = set()
    sites = {}          # number -> [files that cite it], so an ambiguity can be READ, not just counted
    for root in a.roots:
        base = os.path.join(REPO, root)
        for dirpath, dirnames, filenames in os.walk(base) if os.path.isdir(base) else []:
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                    continue
                p = os.path.join(dirpath, fn)
                if os.path.abspath(p) == os.path.abspath(LEDGER):
                    continue
                try:
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        found = {int(x) for x in FNUM.findall(fh.read())}
                except OSError:
                    continue
                cited |= found
                rel = os.path.relpath(p, REPO)
                for n in found:
                    sites.setdefault(n, []).append(rel)
    # USE vs MENTION, and it decides whether this gate can ever clear.
    #
    # A finding's OWN file naming its own number is self-reference, not an ambiguous citation.
    # Worse, the fix itself creates permanent hits: a disambiguation note reads "this is F48a;
    # the bare number F48 collides with ...", so the note MENTIONS the bare token in order to
    # explain it. A regex counts occurrences of a string and cannot tell citing from talking-
    # about. Left alone, this gate would flag the disambiguation as an outstanding defect
    # forever — a gate that can never be satisfied is one people learn to bypass, which is
    # worse than no gate.
    #
    # So a collision counts as CITED only from a file that is neither candidate. The defining
    # surfaces (the two findings themselves, and the ledger, already skipped above) describe the
    # number; every other file uses it. That is a principled boundary rather than a keyword
    # heuristic — no list of words like "collides" or "disambiguation" to keep in sync.
    #
    # ⚠️ Elder predicted this class from the other end (the ᵃ suffix defeating \b) and was right
    # about the consequence and wrong about the mechanism: in a byte-locale grep \bF48\b does
    # match "F48ᵃ", but Python's \b is Unicode-aware and U+1D43 is category Lm, so it does NOT.
    # Verified rather than adopted — his finding about his surface was a hypothesis about mine.
    def _external(n):
        cand = set(collisions.get(n, []))
        return sorted({s for s in set(sites.get(n, []))
                       if os.path.basename(s) not in cand})
    cited_collisions = {n: v for n, v in collisions.items() if n in cited and _external(n)}
    if collisions:
        # ⚠️ STATE THE DENOMINATOR. This check is keyed on FILENAMES, so it can only see files
        # whose name carries a parseable finding-number. Dawn's census (general#18580) measured
        # the corpus: 101 of 250 findings files carry one; 149 DO NOT — most findings are named
        # by topic, which is fine and is not a defect. But it means every "N collisions" this
        # tool has ever printed was a count over ~40% of the population, reported as if it were
        # the corpus. A topic-named finding has no number to collide, so the fix is not to parse
        # harder — it is to say what was counted, so a reader cannot mistake the scope.
        _named = len(filed)
        # NOT wrapped in a bare except that degrades to silence: if the count cannot be taken,
        # SAY SO, because a missing denominator line is indistinguishable from a tool that never
        # had one — which is the defect this line exists to fix.
        try:
            _total = len([f for f in os.listdir("findings") if f.endswith(".md")])
        except Exception as _e:
            _total = None
            print(f"  scope: UNKNOWN — could not count findings/ ({type(_e).__name__}). "
                  f"The {_named} numbered files below are NOT known to be the whole corpus.")
        if _total:
            print(f"  scope: this check reads FILENAMES, so it covers the {_named} findings file(s) "
                  f"carrying a parseable number, of {_total} in findings/ — "
                  f"{_total - _named} are topic-named and OUTSIDE it. A zero here is a zero over "
                  f"{_named}, never over the corpus.")
        print(f"  ⚠ {len(collisions)} finding number(s) claimed by MORE THAN ONE file "
              f"({len(cited_collisions)} of them cited):")
        for n in sorted(collisions):
            mark = "  <- CITED, so a reader following F%d lands on two documents" % n if n in cited_collisions else ""
            print(f"     F{n}: {', '.join(collisions[n])}{mark}")
        print("     An existence check cannot see this: it asks whether the number exists, and")
        print("     two answers is still yes.")

    if cited_collisions:
        # NAME THE CITING FILES. A count of ambiguities is not actionable; the deliverable is the
        # list a human can open. An era-suffix convention cannot repair an existing bare "F48" —
        # the string carries no era — so the most this check can honestly do is convert an
        # invisible ambiguity into a listed one and let whoever reads the citing sentence decide.
        print("\n  BARE CITATIONS TO AMBIGUOUS NUMBERS — each needs a human to pick the intended half:")
        for n in sorted(cited_collisions):
            ext = _external(n)
            print(f"     F{n} — {len(ext)} EXTERNAL citing file(s); the two candidates are:")
            for f in cited_collisions[n]:
                print(f"        candidate: findings/{f}")
            for s in ext[:6]:
                print(f"        cited by:  {s}")
            if len(ext) > 6:
                print(f"        ... and {len(ext) - 6} more")

    if not dangling and cited_collisions:
        print(f"\n  ⛔ every cited F-number resolves, but {len(cited_collisions)} resolve AMBIGUOUSLY.")
        print("     A citation that resolves to two different findings does not identify a source.")
        sys.exit(1)

    if not dangling:
        print(f"  every cited F-number under {a.roots} resolves to a ledger row.")
        print("  SCOPE: existence only — this does NOT verify that a row says what its citer claims.")
        sys.exit(0)

    total = sum(len(v) for v in dangling.values())
    print(f"\n  ⛔ {len(dangling)} F-number(s) cited but NOT in the ledger, across {total} file(s):")
    for n in sorted(dangling):
        for rel in sorted(set(dangling[n])):
            pub = " [PUBLISHED]" if rel.startswith(("demo/", "exhibits/")) else ""
            print(f"     F{n:<4} {rel}{pub}")
    print("\n  A citation that does not resolve is an assertion. Either the finding exists under")
    print("  another number (fix the citer), or it never existed (retract the claim).")
    sys.exit(1)


if __name__ == "__main__":
    main()
