#!/usr/bin/env python3
"""grader-raw-counts-check.py — refuse a grader that re-fetches a live QPU job as its ONLY data path.

THE RULE IT ENFORCES (@whisper, general#20178, adopted network-wide 2026-08-31): every grade on
the IBM Runtime path SAVES THE RAW COUNTS alongside the verdict, and must be able to re-grade
from those counts OFFLINE. The Braket path already does this; the IBM path must match it.

WHY (board#353). F85's 61.7-sigma WIN cannot be re-run: its grader re-fetches the live job
(RuntimeJobNotFound — the job expired) and the saved result is a graded SUMMARY with no counts.
Measured across the corpus: 48 of 49 graders re-fetch, 0 persist counts. The result survives and
the ability to check it does not. Neither a code-drift clock nor a producer check can see this —
THE CODE IS PERFECTLY COMMITTED IN EVERY CASE. What expired was data on a vendor's server.

  fetches a job  +  persists counts   -> OK    (re-gradeable offline once counts are saved)
  fetches a job  +  no counts saved   -> REFUSE (one expiry from unreproducible)
  no fetch                            -> OK    (already reads local data)

THE SELF-TEST IS NOT OPTIONAL AND RUNS ON EVERY INVOCATION. My first version of this measurement
returned 0 of 49 — it required the receiver be named `service` when the code says `svc`, matching
a VARIABLE NAME instead of a METHOD CALL. It reported "no exposure" about a corpus that is 48/49
exposed, and the only thing that caught it was noticing the known-positive case was missing from
a result claiming to cover it. So the known positive is now compiled in: if KNOWN_POSITIVE stops
being flagged, this checker REFUSES TO REPORT rather than printing a clean board.

Usage:  python3 tools/grader-raw-counts-check.py [--graders DIR] [--json]
Exit:   0 every fetching grader persists counts · 1 at least one does not · 2 could not run
"""
import argparse
import json
import os
import re
import sys

# Receiver-agnostic ON PURPOSE: svc.job(), service.job(), self._svc.job() all count. Matching the
# receiver's NAME is what produced a false 0/49.
FETCH = re.compile(r"\.job\s*\(")
COUNTS = re.compile(r"counts", re.I)
DUMP = re.compile(r"json\.dump|\.write\s*\(|to_json|savez|np\.save")
WINDOW = 8          # lines after a dump call in which a counts key still plausibly belongs to it

# The case this checker exists because of. If it ever stops flagging, the matcher has drifted.
KNOWN_POSITIVE = "grade_exp107.py"


def classify(path):
    """(fetches, persists_counts) for one grader file."""
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return None, None
    fetches = any(FETCH.search(l) for l in lines)
    persists = False
    countdown = 0
    for l in lines:
        if DUMP.search(l):
            countdown = WINDOW
            if COUNTS.search(l):
                persists = True
        elif countdown:
            countdown -= 1
            if COUNTS.search(l):
                persists = True
    return fetches, persists


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graders", default="scripts")
    ap.add_argument("--pattern", default="grade_")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not os.path.isdir(a.graders):
        print(f"UNKNOWN: graders dir not found: {a.graders}", file=sys.stderr)
        return 2
    files = sorted(f for f in os.listdir(a.graders)
                   if f.startswith(a.pattern) and f.endswith(".py"))
    if not files:
        # An empty population is not a pass. Nothing was examined, so nothing can be cleared.
        print(f"UNKNOWN: no files matching {a.pattern}*.py in {a.graders} — "
              f"this is NOT 'all graders comply'.", file=sys.stderr)
        return 2

    ok, refuse, unreadable = [], [], []
    for f in files:
        fetches, persists = classify(os.path.join(a.graders, f))
        if fetches is None:
            unreadable.append(f)
        elif fetches and not persists:
            refuse.append(f)
        else:
            ok.append(f)

    # SELF-TEST: the known positive must be among the refusals. A checker that has stopped
    # matching prints a clean board, which is the failure this whole row is about.
    if KNOWN_POSITIVE in files and KNOWN_POSITIVE not in refuse:
        print(f"SELF-TEST FAILED: {KNOWN_POSITIVE} is present and NOT flagged. This checker's "
              f"matcher has drifted and its output cannot be trusted. Refusing to report.",
              file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps({"graders": len(files), "compliant": len(ok),
                          "refused": refuse, "unreadable": unreadable,
                          "self_test": "PASS" if KNOWN_POSITIVE in refuse else "not-applicable"},
                         indent=1))
    else:
        print(f"  graders examined        {len(files)}")
        print(f"  compliant               {len(ok)}   (no fetch, or fetch WITH counts persisted)")
        print(f"  REFUSED                 {len(refuse)}   fetch a live job and save no raw counts")
        for f in refuse[:15]:
            print(f"     {f}")
        if len(refuse) > 15:
            print(f"     ... and {len(refuse) - 15} more")
        if unreadable:
            print(f"  UNREADABLE              {len(unreadable)}   NOT a pass")
        st = "PASS" if KNOWN_POSITIVE in refuse else ("n/a — known positive absent from this dir")
        print(f"  self-test ({KNOWN_POSITIVE}): {st}")
    return 1 if refuse else 0


if __name__ == "__main__":
    sys.exit(main())
