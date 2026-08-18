#!/usr/bin/env python3
"""tools/capability_map.py — what APPARATUS do we have, and what has never been combined? (Whisper C5075)

THE PROBLEM, in the Creator's words: "any objective is now a data mining project to start."

THE DIAGNOSIS, measured rather than assumed. The campaign has exactly one retrieval tool for prior
work, `already-built.js`, and it answers ONE question: **has this been settled?** (corpus = the
F-ledger + findings/ + docs/). That is rediscovery prevention, and it works.

But "what can I BUILD with what we have?" is a DIFFERENT question over a DIFFERENT corpus — the
apparatus lives in experiments/ (929 files) and tools/ (141), which no retrieval path indexes at
all. So a composition question gets asked of a results index, and the honest answer is a filesystem
trawl. Hence: data mining.

I TESTED THE OBVIOUS FIX AND IT IS WRONG. Adding experiments/ to already-built.js's default corpus
changed the top hit on 3 of 5 control queries, and changed it FOR THE WORSE: "time flip indefinite
causal order" moved from F92 (the finding, i.e. what was FOUND) to a design document (what was
PLANNED). Preregistrations beat findings on keyword density and carry no outcome. **MERGING THE TWO
CORPORA DEGRADES BOTH QUERIES.** They are separate instruments, and only one of them existed.

    already-built.js  ->  "has this QUESTION been settled?"   corpus: ledger + findings + docs
    capability_map.py ->  "what APPARATUS do we have, and     corpus: experiments + tools
                           what has never been combined?"

WHAT MOTIVATED IT, concretely and expensively. While designing the H15-B magic-square neuron I never
saw `exp228_shielded_magic_square` — the Peres-Mermin square error-detected behind the [[4,2,2]]
shield — because nothing indexes experiments/. Two consequences, both real: (1) I missed a direct
composition with tonight's readout-limited design, and (2) exp228 is a NOT-CERTIFIED honest negative
whose witness was TAUTOLOGICAL (three observables from one joint readout, the third the product of
the first two, pinned by bit-identity), and my design had no severed-entanglement arm to rule out
the same failure. Running that guard afterwards: entangled 1.0000 -> severed 0.5082, drop +0.4918,
NOT a tautology. The design survived — but only because a search I ran for other reasons happened
to surface a file I had no path to.

DERIVED, NEVER HAND-MAINTAINED. Every field is extracted from the code and its neighbours at run
time. A hand-curated capability list is a document, and documents in this repo rot — that is the
finding of this very cycle, three times over.

    python3 tools/capability_map.py                      # inventory by apparatus
    python3 tools/capability_map.py --for "<concept>"    # what apparatus do I have for X
    python3 tools/capability_map.py --with <tag>         # what X has and has NOT been combined with
    python3 tools/capability_map.py --gaps               # common pairs that have NEVER co-occurred
"""
import collections
import glob
import json
import os
import re
import sys

Q = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Small, hand-written, deliberately incomplete. 61% of experiments/ get >=1 tag, which is enough to
# be useful; a tag that is missing makes this tool QUIET about a capability, never WRONG about one.
VOCAB = {
    "bell-pair": r"\bbell\b",
    "mid-circuit-meas": r"mid.?circuit|MCM\b",
    "feedforward": r"feedforward|if_test|c_if|classical\.expr",
    "422-shield": r"\[\[4,\s*2,\s*2\]\]|4,2,2|shield",
    "magic-square": r"magic.?square|peres.?mermin",
    "teleportation": r"teleport",
    "dyn-decoupling": r"dynamical.?decoupling|XY4|CPMG",
    "stabilizer": r"stabilizer",
    "sdp": r"\bSDP\b|semidefinite",
    "ico": r"indefinite causal|quantum switch|\bICO\b",
    "darwinism": r"darwinis|redundan",
    "tomography": r"tomograph",
    "post-selection": r"post.?select",
    "purification": r"purif",
    "contextuality": r"contextual",
    "leggett-garg": r"leggett.?garg",
    "zne": r"zero.?noise|\bZNE\b",
    "twirl": r"twirl",
    "witness": r"\bwitness\b",
    "steering": r"steering",
}

# Status is what stops this becoming a list of things to build on top of retracted results.
STATUS_RE = [
    ("NOT-CERTIFIED", r"not.?certified|tautolog"),
    ("RETIRED", r"\bretired\b|supersed|refuted"),
    ("HONEST-NEGATIVE", r"honest negative|does not hold|null result|inconclusive"),
    ("CERTIFIED", r"\bF\d{2,3}\b.*(certif|won|holds)|CERTIFIED"),
]


def strip_doc(t):
    """Drop the module docstring, keeping the executable body."""
    m = re.match(r'\s*(?:#![^\n]*\n)?\s*"""', t)
    if not m:
        return t
    e = t.find('"""', m.end())
    return t[e + 3:] if e > 0 else t


def harvest():
    rows = []
    for d, kind in (("experiments", "exp"), ("tools", "tool")):
        for p in sorted(glob.glob(f"{Q}/{d}/*.py")):
            base = os.path.basename(p)[:-3]
            try:
                txt = open(p, errors="replace").read(20000)
            except OSError:
                continue
            txt = txt if len(txt) < 20000 else txt[:20000]
            doc = (re.search(r'"""\s*(.+)', txt) or [None, ""])[1].strip()[:110]
            # TAG THE CODE, NOT THE PROSE. Corrected C5075 after the first version reported that
            # EVERY common capability pair had already been combined — magic-square (5 files)
            # appeared to co-occur with all 19 other tags. It was tagging module DOCSTRINGS, which
            # cite techniques in passing ("the campaign's shield", "F106 precedent"). A file that
            # MENTIONS teleportation is not a file that USES it, and mention-saturation makes every
            # cell of the co-occurrence matrix non-zero, which silently destroys the gap analysis —
            # the one query this tool exists for. Same homonym class as the constants checker.
            # The docstring says what the author was THINKING ABOUT; the code says what it DOES.
            tags = sorted(k for k, rx in VOCAB.items() if re.search(rx, strip_doc(txt), re.I))
            if not tags:
                continue
            # THE INSTRUMENT MUST NOT BE ITS OWN DATA. Caught C5075: the first run reported that
            # EVERY common pair had already been combined, and the sole bridge for all three real
            # gaps was `capability_map` itself — this file contains the VOCAB regexes, so it
            # matches all twenty tags and single-handedly saturates the co-occurrence matrix.
            # An observer effect, literally: the apparatus was being counted as a specimen.
            # The general guard is the second clause — a file matching most of the vocabulary is
            # an index or a survey, not a piece of apparatus, whoever wrote it.
            if base == "capability_map" or len(tags) > 0.6 * len(VOCAB):
                continue
            # status: prefer an adjacent STATUS file, else the file's own words
            near = " ".join(os.path.basename(x) for x in
                            glob.glob(f"{Q}/{d}/{base.split('_')[0]}*STATUS*"))
            hay = near + " " + txt[:3000]
            status = next((s for s, rx in STATUS_RE if re.search(rx, hay, re.I)), "")
            cyc = (re.search(r"[cC](\d{4,5})", base) or [None, ""])[1]
            rows.append({"name": base, "kind": kind, "tags": tags, "doc": doc,
                         "status": status, "cycle": cyc})
    return rows


def co_matrix(rows):
    co = collections.Counter()
    freq = collections.Counter()
    for r in rows:
        for t in r["tags"]:
            freq[t] += 1
        for i, a in enumerate(r["tags"]):
            for b in r["tags"][i + 1:]:
                co[tuple(sorted((a, b)))] += 1
    return freq, co


def main():
    rows = harvest()
    freq, co = co_matrix(rows)
    args = sys.argv[1:]

    def show(rs, limit=12):
        for r in rs[:limit]:
            st = f" [{r['status']}]" if r["status"] else ""
            print(f"   {r['name'][:48]:48s}{st}")
            print(f"      {','.join(r['tags'])}")
            if r["doc"]:
                print(f"      {r['doc'][:100]}")
        if len(rs) > limit:
            print(f"   … {len(rs)-limit} more")

    if "--for" in args:
        qy = args[args.index("--for") + 1].lower()
        terms = [t for t in re.split(r"[^a-z0-9]+", qy) if len(t) > 2]
        scored = []
        for r in rows:
            hay = (r["name"] + " " + r["doc"] + " " + " ".join(r["tags"])).lower()
            s = sum(hay.count(t) for t in terms)
            if s:
                scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        print(f"\n═══ APPARATUS FOR: {qy} ═══  ({len(scored)} of {len(rows)} tagged files)\n")
        show([r for _, r in scored])
        print("\n  NOTE: this indexes APPARATUS, not results. For 'has this been settled?'")
        print("  use already-built.js — merging the two corpora measurably degrades both.\n")
        return

    if "--with" in args:
        tag = args[args.index("--with") + 1]
        partners = collections.Counter()
        for r in rows:
            if tag in r["tags"]:
                for t in r["tags"]:
                    if t != tag:
                        partners[t] += 1
        print(f"\n═══ COMPOSITIONS OF '{tag}' ═══   appears in {freq[tag]} file(s)\n")
        print("  COMBINED WITH:")
        for t, n in partners.most_common():
            print(f"    {t:20s} {n:3d}x")
        never = [t for t in VOCAB if t != tag and t not in partners and freq[t] >= 8]
        print("\n  NEVER COMBINED WITH (and each is well-established on its own):")
        for t in sorted(never, key=lambda x: -freq[x]):
            print(f"    {t:20s} exists in {freq[t]:3d} file(s)  <- candidate novel composition")
        if not never:
            print("    (none — this capability has been combined with everything common)")
        print()
        return

    if "--gaps" in args:
        print("\n═══ COMPOSITION GAPS — common capabilities that have NEVER co-occurred ═══")
        print("  Not a to-do list. A gap is sometimes a physical impossibility and sometimes")
        print("  nobody's idea yet; this tool cannot tell those apart and does not try.\n")
        common = [t for t in VOCAB if freq[t] >= 15]
        gaps = [(a, b) for i, a in enumerate(sorted(common)) for b in sorted(common)[i + 1:]
                if co[tuple(sorted((a, b)))] == 0]
        gaps.sort(key=lambda p: -(freq[p[0]] * freq[p[1]]))
        for a, b in gaps[:16]:
            print(f"   {a:18s} x {b:18s}   ({freq[a]:3d} x {freq[b]:3d} files, 0 together)")
        if not gaps:
            print("   none — every common pair has been combined at least once.")
        print()
        return

    print(f"\n═══ CAPABILITY MAP ═══  {len(rows)} tagged files "
          f"({sum(1 for r in rows if r['kind']=='exp')} experiments, "
          f"{sum(1 for r in rows if r['kind']=='tool')} tools)\n")
    for t, n in freq.most_common():
        flagged = sum(1 for r in rows if t in r["tags"] and r["status"] in
                      ("NOT-CERTIFIED", "RETIRED"))
        warn = f"   ⚠ {flagged} not-certified/retired" if flagged else ""
        print(f"   {t:20s} {n:3d} file(s){warn}")
    print("\n  --for \"<concept>\" | --with <tag> | --gaps")
    print("  Companion, not replacement: already-built.js answers 'has this been settled?'\n")


if __name__ == "__main__":
    main()
