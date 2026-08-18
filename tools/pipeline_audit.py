#!/usr/bin/env python3
"""tools/pipeline_audit.py — where are results STUCK in the campaign's own pipeline? (Whisper C5075)

WHY THIS EXISTS. A result travels: FLOWN -> decoded -> FINDING written -> F-NUMBER assigned ->
LEDGER entry -> MUSEUM exhibit. Every transition is a manual handoff, several of them to a
DIFFERENT SEAT, and nobody watches the transitions. The C5054 fresh review found the first stall
(six flown flights with no findings — "flown != banked") and it was fixed. Twenty-one cycles later
the queue had simply backed up ONE STAGE DOWNSTREAM: six findings sit explicitly "pending F-number
assignment", the oldest for twenty cycles, and one of them is the H10-B1 time flip at 113-200 sigma
— arguably the campaign's sharpest physics, with no number and no exhibit.

THE PRINCIPLE, and it is the same one the H15 loss budget taught on the physics side (C5075):
**REMOVING A BOTTLENECK MOVES IT.** Fixing the write-up stage did not drain the pipeline, it
relocated the queue. An unmonitored multi-stage pipeline will always be stalled SOMEWHERE, and
"we fixed that" is only ever true of one stage.

WHAT IT DOES. Walks findings/ and the F-ledger and reports the census per stage, naming what is
stuck and how long it has been stuck. Deliberately does NOT try to fix anything: numbering is
Ember's seat and ledger entries are the court's. This surfaces; humans and seats decide.

Exit 0 always — this is an instrument, not a gate. Silence would be the failure mode it exists
to prevent, so it prints a census even when nothing is stuck.

    python3 tools/pipeline_audit.py [--json]
"""
import glob
import json
import os
import re
import subprocess
import sys

Q = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cycle_of(name):
    m = re.search(r"c(\d{4,5})", name)
    return int(m.group(1)) if m else None


def current_cycle():
    """THIS SEAT's current cycle, from its own state file.

    BUG FIXED C5075, caught because the output was absurd (1550 cycles stalled): the first
    version took max() over cycle numbers parsed from ALL findings filenames — but each DC
    keeps its OWN cycle counter (Whisper ~C5075, Elder ~C6600), so the max picked another
    seat's clock and every age was inflated by ~1500. CROSS-SEAT CYCLE NUMBERS ARE NOT
    COMPARABLE; they are different units wearing the same notation. Read the local counter."""
    try:
        with open("/mnt/droid/repos/DC15W/state/current-state.json") as fh:
            return int(json.load(fh)["cycle"])
    except Exception:
        return None


def audit():
    ledger_path = f"{Q}/docs/campaign-arcs.md"
    ledger = open(ledger_path, errors="replace").read() if os.path.exists(ledger_path) else ""
    numbered, pending, unfielded = [], [], []
    for p in sorted(glob.glob(f"{Q}/findings/*.md")):
        base = os.path.basename(p)
        if re.match(r"^F\d+", base):
            numbered.append(base)
            continue
        try:
            head = open(p, errors="replace").read(4000)
        except OSError:
            continue
        m = re.search(r"\*\*F-number\*\*:\s*([^\n]{0,90})", head)
        if m and "pending" in m.group(1).lower():
            pending.append({"file": base, "note": m.group(1).strip()[:60],
                            "cycle": cycle_of(base)})
        elif m:
            numbered.append(base)
        else:
            unfielded.append(base)
    now = current_cycle()
    for e in pending:
        same_seat = "whisper" in e["file"].lower()
        e["stalled_cycles"] = (now - e["cycle"]) if (now and e["cycle"] and same_seat) else None
        e["age_note"] = "" if same_seat else "age n/a (other seat's cycle counter)"
        # is it visible in the ledger at all?
        key = re.split(r"-whisper|-ember|-elder", e["file"])[0]
        toks = [w for w in re.split(r"[-_]", key) if len(w) > 4][:3]
        e["ledger_visible"] = bool(toks) and any(w.lower() in ledger.lower() for w in toks)
    return {"now_cycle": now, "n_findings": len(numbered) + len(pending) + len(unfielded),
            "numbered": len(numbered), "pending": pending, "unfielded": len(unfielded)}


if __name__ == "__main__":
    r = audit()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=1))
        sys.exit(0)
    print("\n═══ QUANTUM RESULT PIPELINE AUDIT ═══")
    print("  stages: FLOWN -> finding -> F-NUMBER -> ledger -> museum\n")
    print(f"  findings total            {r['n_findings']}")
    print(f"  carrying an F-number      {r['numbered']}")
    print(f"  no F-number field         {r['unfielded']}  (protocols/scoping — mostly legitimate)")
    print(f"  ⏳ STUCK 'pending'         {len(r['pending'])}")
    if r["pending"]:
        print("\n  STALLED AT THE NUMBERING STAGE — a queue with no queue-manager:")
        for e in sorted(r["pending"], key=lambda x: x["cycle"] or 0):
            age = f"{e['stalled_cycles']}cy" if e["stalled_cycles"] is not None else "?"
            vis = "in ledger" if e["ledger_visible"] else "NOT IN LEDGER"
            print(f"    C{e['cycle']}  stalled {age:>5}  [{vis:13s}]  {e['file'][:52]}")
        print("\n  Numbering is Ember's seat and ledger entries are the court's — this tool")
        print("  SURFACES, it does not fix. But an unnumbered result is half-invisible to")
        print("  already-built.js (which greps the ledger) and absent from the museum.")
    else:
        print("\n  Nothing stalled at numbering. (Printed explicitly: silence is the failure")
        print("  mode this instrument exists to prevent.)")
    print()
