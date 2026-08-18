#!/usr/bin/env python3
"""tools/constants_consistency.py — does the campaign quote its own constants consistently? (Whisper C5075)

WHY THIS EXISTS, and it is one specific bug rather than a general worry. C5075: my H15 finding
quoted TWO different registered thresholds ONE SECTION APART — 0.6040 in the one-line summary and
0.6500 in the table, the latter a superseded, mislabelled JSON field. I had re-read that document
repeatedly inside the hour and never saw it. I caught it only when a downstream design study needed
the value and the arithmetic came out strange.

    A STALE RECORD SURVIVES UNTIL SOMETHING COMPUTES WITH IT.

Reading checks whether a number looks reasonable; computing checks whether it IS the number. The
corollary is uncomfortable: a constant that nothing currently computes with is UNVERIFIED no matter
how often it has been read, and the safest place for a wrong number to hide is a summary table that
no code touches. This tool is the thing that computes with them.

IT IS A WITNESS, NOT A GATE (Elder, general#12883). Gating on constant-disagreement would refuse to
proceed over bookkeeping, which is a worse failure than the one it prevents. What a handoff needs is
not the power to REFUSE but the inability to FAIL QUIETLY. So: exit 0 always, print loudly, and
report the count EXAMINED as well as the count WRONG — because an instrument whose null output is
indistinguishable from its healthy output is not an instrument.

WHAT IT DOES — TWO CHECKS, AND THE PRECISE ONE IS PRIMARY.

  CHECK A (exact, zero false positives): THE STALE-VALUE WATCHLIST. When a number is superseded or
  retracted, it is declared here as known-wrong, and this reports every place it still appears in
  scope. There is no inference: a retired value has no legitimate use except in a sentence that
  retires it, so a hit is either a real stale quote or an explicit retraction note.

  CHECK B (heuristic, noise-floored): proximity scan — numbers quoted immediately after a
  constant's name that disagree with it. Kept as a weak secondary signal and LABELLED AS SUCH.

WHY B IS SECONDARY, measured rather than assumed. The first version keyed on the bare word
"threshold" repo-wide and produced 97 "disagreements", nearly all legitimately different thresholds
belonging to other experiments. Scoping to H15 documents plus specific phrases cut it to 8; taking
only the FIRST number after the phrase cut it to 2. Both survivors are COMPARISON constructions —
"X vs the frozen ceiling", "the frozen threshold requires Y" — where the adjacent number is the
thing being compared, not the constant.

THAT FLOOR IS STRUCTURAL, NOT A TUNING PROBLEM: prose puts a constant's name beside other numbers
BY DESIGN, because comparing is the main reason to cite one. So the honest conclusion is that
scanning prose treats the symptom. THE REAL FIX IS SINGLE-SOURCING — a document should CITE a
constant from one place rather than re-type it — and until that exists, Check A is the part that
actually works.

    python3 tools/constants_consistency.py [--json]
"""
import glob
import json
import os
import re
import sys

Q = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The registry. Each entry: the canonical value, where that value is FROZEN, how close counts as
# "the same number", and the regexes whose neighbourhood is searched. Deliberately small and
# hand-curated: a constant is load-bearing because a human said so, not because it appears often.
CONSTANTS = [
    {"name": "H15 registered threshold",
     "value": 0.6040, "tol": 0.0006,
     "truth": "prereg powered-design row: 143/256 + 2.3*sqrt(p_C(1-p_C)/632); Elder re-derived",
     "scope": ["docs/h15*.md", "findings/h15*.md", "experiments/h15*.py"],
     "near": r"registered threshold|threshold frozen|frozen threshold|THRESHOLD FROZEN"
             r"|threshold_2p3sd|registered 2\.3|2\.3-SD bar",
     "known_wrong": {0.6500: "superseded field threshold_2p3sd_at_S632_approx "
                             "(effective n~158, pre-dates the powered design's ratification)"}},
    {"name": "H15 classical ceiling (n=4)",
     "value": 0.55859375, "tol": 0.0006,
     "truth": "143/256, FROZEN at G1 completion (Elder C6627); provisional label retired",
     "scope": ["docs/h15*.md", "findings/h15*.md", "experiments/h15*.py"],
     "near": r"classical ceiling|frozen ceiling|ceiling frozen|provisional ceiling",
     "known_wrong": {}},
    {"name": "H15 quantum ideal (Helstrom, n=4)",
     "value": 0.763671875, "tol": 0.0006,
     "truth": "391/512 = 3/4+(2^(n-1)-1)/(2*4^n), exact all n; transversal-Bell == global Helstrom",
     "scope": ["docs/h15*.md", "findings/h15*.md", "experiments/h15*.py"],
     "near": r"helstrom|quantum ideal",
     "known_wrong": {}},
]

# NO GLOBAL SCAN. A constant is scoped to the documents that are ABOUT it.
#
# WHY, learned by shipping the broken version first (C5075): keying on the bare word "threshold"
# across the whole repo produced 97 "disagreements", essentially ALL of them legitimately different
# thresholds belonging to other experiments. An instrument that cries wolf 97 times is not merely
# useless, it is worse than silence — it trains the reader to skip it, so the ONE real disagreement
# is now hidden behind ninety-six false ones with a warning icon in front of it.
#
# A CONSISTENCY CHECK KEYED ON A GENERIC WORD DROWNS IN LEGITIMATE HOMONYMS. The fix is a scope and
# a specific phrase, not a cleverer threshold on the noise.
NUM = re.compile(r"0\.\d{3,10}")


def scan_one(c):
    """Every number quoted within a window of the constant's name."""
    hits, examined = [], 0
    for pat in c["scope"]:
        for path in glob.glob(f"{Q}/{pat}"):
            try:
                txt = open(path, errors="replace").read()
            except OSError:
                continue
            for m in re.finditer(c["near"], txt, re.I):
                examined += 1
                # ONLY THE FIRST number after the phrase, and only within a tight window.
                # Proximity is not identity: a 220-char window around "frozen threshold" also
                # catches the sentence's OTHER quantities (a pre-flight estimate, a severed-arm
                # reading), and reporting those as disagreements is the crying-wolf failure one
                # rung down from the 97-hit version.
                window = txt[m.end(): m.end() + 70]
                nm = NUM.search(window)
                if not nm:
                    continue
                v = float(nm.group())
                if abs(v - c["value"]) > 0.25 or abs(v - c["value"]) <= c["tol"]:
                    continue
                hits.append({"file": os.path.relpath(path, Q), "value": v,
                             "context": " ".join(txt[m.start(): m.start() + 130].split())})
    return hits, examined


def stale_watchlist():
    """CHECK A: every surviving occurrence of a value we have explicitly retired.

    Exact by construction. A retired number has no legitimate use except inside a sentence that
    retires it, so this cannot produce the homonym noise that sinks the proximity scan."""
    out = []
    for c in CONSTANTS:
        for bad, why in c.get("known_wrong", {}).items():
            pat = re.compile(re.escape(f"{bad:.4f}").rstrip("0") + r"\d*")
            for g in c["scope"]:
                for path in glob.glob(f"{Q}/{g}"):
                    try:
                        txt = open(path, errors="replace").read()
                    except OSError:
                        continue
                    for m in pat.finditer(txt):
                        # A STALE VALUE ALONE IS NOT ENOUGH. Corrected C5075 after the first
                        # version's only "LIVE" hit turned out to be the string 0.65 inside a
                        # power table ("99.2% at pessimistic 0.65") — a different quantity that
                        # happens to be a common round number. Require the CONSTANT'S OWN NAME
                        # nearby, so the hit is a claim about THIS constant rather than a
                        # coincidence of digits. Precision of the retired value is not something
                        # to rely on: round numbers collide.
                        neigh = txt[max(0, m.start() - 200): m.start() + 200]
                        if not re.search(c["near"], neigh, re.I):
                            continue
                        ctx = " ".join(txt[max(0, m.start() - 90): m.start() + 90].split())
                        retracting = bool(re.search(
                            r"supersed|stale|wrong|retract|correct|NOT 0|mislabel|earlier revision",
                            ctx, re.I))
                        out.append({"constant": c["name"], "stale_value": bad, "why": why,
                                    "file": os.path.relpath(path, Q), "context": ctx,
                                    "is_retraction_note": retracting})
    return out


def main():
    report, total_bad = [], 0
    for c in CONSTANTS:
        hits, examined = scan_one(c)
        # collapse to distinct wrong values, keeping one example each
        by_val = {}
        for h in hits:
            by_val.setdefault(round(h["value"], 6), h)
        report.append({"name": c["name"], "canonical": c["value"], "truth": c["truth"],
                       "mentions_examined": examined,
                       "disagreements": [
                           {**h, "known_wrong_note": c["known_wrong"].get(round(h["value"], 4))}
                           for h in by_val.values()]})
        total_bad += len(by_val)

    if "--json" in sys.argv:
        print(json.dumps({"constants": report, "total_disagreements": total_bad}, indent=1))
        return

    print("\n═══ CONSTANTS CONSISTENCY ═══")
    print("  One number should not have two values. This is a WITNESS, not a gate.\n")
    stale = stale_watchlist()
    live = [s_ for s_ in stale if not s_["is_retraction_note"]]
    print(f"── CHECK A: STALE-VALUE WATCHLIST (exact) ── {len(stale)} occurrence(s), "
          f"{len(live)} NOT in a retraction sentence")
    for s_ in stale:
        tag = "📝 retraction note" if s_["is_retraction_note"] else "🔴 LIVE STALE QUOTE"
        print(f"   {tag}  {s_['stale_value']} in {s_['file']}")
        if not s_["is_retraction_note"]:
            print(f"       why retired: {s_['why']}")
            print(f"       …{s_['context'][:120]}…")
    if not stale:
        print("   no retired value appears anywhere in scope.")
    print("\n── CHECK B: PROXIMITY SCAN (heuristic, has a structural false-positive floor) ──")
    for r in report:
        mark = "⏳" if r["disagreements"] else "  "
        print(f"{mark} {r['name']}  canonical {r['canonical']}")
        print(f"     truth: {r['truth']}")
        print(f"     mentions examined: {r['mentions_examined']}"
              f"   disagreeing values: {len(r['disagreements'])}")
        for d in r["disagreements"]:
            note = f"  <- KNOWN WRONG: {d['known_wrong_note']}" if d["known_wrong_note"] else ""
            print(f"       {d['value']}  in {d['file']}{note}")
            print(f"         …{d['context']}…")
        print()
    if total_bad == 0:
        print("  No disagreements across any registered constant. (Said explicitly, with the")
        print("  examined counts above, so that 'nothing found' cannot be confused with")
        print("  'nothing looked at' — the defect this file's sibling caught in itself.)")
    else:
        print(f"  {total_bad} proximity hit(s) — TREAT AS LEADS, NOT FINDINGS. Both known")
        print("  survivors are comparison constructions ('X vs the frozen ceiling'), which is the")
        print("  floor this method cannot get under. Check A above is the exact one.")
    print()


def selftest():
    """Does the witness catch the bug it was built for? Synthetic, so it cannot rot.

    Validated once against the real thing too: run over commit 56124c1's copy of the H15 finding
    (the revision that carried the stale 0.6500 in its table), Check A returned exactly one LIVE
    stale quote; over the corrected revision it returns zero live and three retraction notes.
    A witness that has never been shown to fire is a decoration."""
    import tempfile
    bad = ("| registered threshold (2.3 SD @ S=632) | 0.6500 |\n"
           "| pre-flight noisy estimate | 0.7126 |\n")
    good = ("| **registered threshold (2.3 SD @ S=632)** | **0.6040** |\n"
            "An earlier revision read 0.6500; that field is superseded and mislabelled.\n")
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(f"{d}/findings")
        globals_Q = Q
        for name, body, want_live in (("bad", bad, 1), ("good", good, 0)):
            open(f"{d}/findings/h15-{name}.md", "w").write(body)
        try:
            globals()["Q"] = d
            for c in CONSTANTS:
                c["_scope_backup"] = c["scope"]
                c["scope"] = ["findings/h15-bad.md"]
            live = [h for h in stale_watchlist() if not h["is_retraction_note"]]
            ok_bad = len(live) == 1
            for c in CONSTANTS:
                c["scope"] = ["findings/h15-good.md"]
            live2 = [h for h in stale_watchlist() if not h["is_retraction_note"]]
            ok_good = len(live2) == 0
        finally:
            globals()["Q"] = globals_Q
            for c in CONSTANTS:
                c["scope"] = c.pop("_scope_backup")
    print(f"  fires on the stale quote:      {'PASS' if ok_bad else 'FAIL'} ({len(live)} live, want 1)")
    print(f"  silent on the corrected text:  {'PASS' if ok_good else 'FAIL'} ({len(live2)} live, want 0)")
    return ok_bad and ok_good


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("\n═══ SELFTEST ═══")
        sys.exit(0 if selftest() else 1)
    main()
