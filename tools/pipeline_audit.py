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
    r = {"now_cycle": now, "n_findings": len(numbered) + len(pending) + len(unfielded),
         "numbered": len(numbered), "pending": pending, "unfielded": len(unfielded)}
    r["exhibit"] = exhibit_lag(ledger)
    r["arcs"] = arc_lag()
    r["ledger"] = ledger_lag(ledger)
    return r


def ledger_lag(ledger):
    """STAGE 2: F-NUMBER -> LEDGER ROW. Added C5075, hours after the rest, BECAUSE IT WAS MISSING
    AND THAT ABSENCE HID A LIVE STALL.

    I built stages 0, 1 and 3 and never noticed there was no stage 2. Within hours Ember cleared the
    numbering queue — and this tool printed "Nothing stalled at numbering", which was TRUE and
    MISLEADING, because F123 through F130 (eight consecutive numbers, including the certified
    door(a) win) had no ledger row. The queue relocated exactly one stage downstream, into the only
    stage the gauge could not see.

    That is REMOVING-A-BOTTLENECK-MOVES-IT confirmed live, and it is also this file's own lesson
    used against it: A GAUGE REPORTS CLEAN FOR TWO REASONS THAT LOOK IDENTICAL — nothing is wrong,
    or nothing is being measured. Ember said she would watch for the relocation; the instrument
    should have watched with her."""
    numbered = []
    for pth in glob.glob(f"{Q}/findings/*.md"):
        try:
            head = open(pth, errors="replace").read(3000)
        except OSError:
            continue
        m = re.search(r"\*\*F-number\*\*:\s*(F\d+)", head)
        if m:
            numbered.append((m.group(1), os.path.basename(pth)))
    missing = [(f, b) for f, b in numbered if not re.search(rf"\b{f}\b", ledger)]
    missing.sort(key=lambda e: int(e[0][1:]))
    return {"numbered_findings": len(numbered), "missing_from_ledger": missing,
            "ledger_front": _max_f(ledger)}


def arc_lag():
    """STAGE 0: FLOWN -> FINDING, at ARC level. Added C5075, and it should have been first.

    C5054 found six flown flights with no findings by hand and the stall was called fixed. It was
    not fixed — it was *cleared once*, with nothing left behind to notice the next occurrence. The
    proof arrived immediately: this very cycle, while reporting a numbering queue sitting on
    ANOTHER seat, H15 carried 45 result files and ZERO findings. My own arc, my own debt, found
    only because I went looking for someone else's.

    A gauge that measures the stages I am not standing in, and not the one I am, is the most
    flattering possible instrument. So: count results and findings per arc, and say it plainly.

    CORRECTION C5075, made within minutes of the first version and worth more than it: the first
    detector flagged H14 as "267 results, 0 findings" and I nearly reported an arc as UNWRITTEN
    that is in fact extensively written — as `docs/*-RESULTS-*.md` protocol/results documents
    rather than `findings/*.md`.

    The truth is more interesting than the backlog I thought I had found. Those RESULTS docs
    carry NO F-number field at all, so the convention is a PIPELINE DEAD END: written, but
    structurally incapable of being numbered, ledgered, exhibited, or found by already-built.js
    (which greps the ledger). A second write-up convention exists and it terminates.

    So the gauge distinguishes UNWRITTEN from WRITTEN-OFF-PIPELINE. An instrument that cannot
    tell "nobody did the work" from "the work went somewhere the pipeline cannot see" would have
    sent me to the bus with a false accusation about another seat's diligence."""
    arcs = {}
    for p in (glob.glob(f"{Q}/results/*") + glob.glob(f"{Q}/findings/*")
              + glob.glob(f"{Q}/docs/*RESULTS*")):
        m = re.search(r"\b(h\d{1,2})[_-]", os.path.basename(p).lower())
        if not m:
            continue
        a = arcs.setdefault(m.group(1).upper(),
                            {"results": 0, "findings": 0, "offpipeline_docs": 0})
        a["results" if "/results/" in p else
          "findings" if "/findings/" in p else "offpipeline_docs"] += 1
    out = [dict(arc=k, **v) for k, v in arcs.items()]
    out.sort(key=lambda e: -e["results"])
    return [e for e in out if e["results"] >= 3 and e["findings"] == 0]


def _max_f(text):
    ns = [int(m) for m in re.findall(r"\bF(\d{1,3})\b", text)]
    return max(ns) if ns else None


_SCOPE_NEG = re.compile(
    r"not (?:yet )?covered|are not covered|not covered here|has since run|run on to|"
    r"where this summary stops|is missing|are missing|does not (?:yet )?cover|coverage stops",
    re.I)


def _covered_f(text):
    """COVERAGE F-number for a PAGE (not the ledger). A page can NAME later F-numbers precisely to
    declare them NOT covered (a scope note); counting those as covered inverts the incentive so that
    DISCLOSURE reads as completeness — Dawn general#16391 caught the original _max_f reporting a
    9-behind ELI5_SUMMARY as 0-behind because its scope note names F122..F131 as missing. That
    PUNISHES disclosure and REWARDS silence, the exact inverse of every other check here. Fix (C5084):
    (1) prefer an explicit DECLARED STOP ('carries the campaign through F120/F121'); (2) else take the
    max over the text with scope-limiting sentences EXCLUDED, so a number named as ABSENT cannot count
    as PRESENT. _max_f stays for the LEDGER FRONT, where max-mentioned genuinely IS the front."""
    m = re.search(r"(?:carr(?:ies|y)|covers?)[^.\n]{0,80}?through[^.\n]{0,25}?F(\d{1,3})(?:\s*/\s*F(\d{1,3}))?", text, re.I)
    if m:
        return max(int(g) for g in m.groups() if g)
    # A 'F01-Fn' RANGE is a SCALE/COUNT claim (how many findings EXIST in the ledger), NOT this page's
    # coverage — Dawn general#16398: her lobby stat-strip 'F01-F131' made a stale page read 0-behind, the
    # MIRROR of the scope-note bug (a PRESENT number misread as coverage vs an ABSENT one). The tool cannot
    # guess coverage from a scale claim, but it must not report a confident false 0-behind from one either:
    # strip full-range scale claims so their high end cannot count, leaving the page UNMEASURED (None ->
    # rendered '?') when a scale strip is the only signal — which matches the honest state Dawn named.
    t = re.sub(r"\bF0?1\s*[-–—]\s*F\d{1,3}\b", " ", text)
    kept = [s for s in re.split(r"(?<=[.\n])\s*", t) if not _SCOPE_NEG.search(s)]
    ns = [int(x) for s in kept for x in re.findall(r"\bF(\d{1,3})\b", s)]
    return max(ns) if ns else None


def exhibit_lag(ledger):
    """STAGE 3: F-number -> MUSEUM EXHIBIT. Added C5075 in the same breath as the finding.

    Ember's reply to the numbering report (general#12877) said she would watch that clearing
    her queue did not simply relocate it to the ledger/museum stage. It ALREADY HAS — and an
    instrument that only measured the stage I happened to be standing in would have let that
    stay a worry instead of a measurement. So the gauge now spans every stage, which is the
    whole point of REMOVING-A-BOTTLENECK-MOVES-IT: a one-stage gauge inherits the same defect
    as a one-stage fix."""
    front = _max_f(ledger)
    rows, unreadable = [], []
    # repo ROOT, not docs/ — verified by find, after the first version silently printed an
    # EMPTY stage-3 table. An instrument whose probe misses its target reports "nothing here"
    # in the same shape it reports "nothing wrong": exactly the silence this file was written
    # to prevent, reproduced inside the file that prevents it.
    for rel in ("ELI5_SUMMARY.md", "index.html", "horizons.html"):
        p = f"{Q}/{rel}"
        if not os.path.exists(p):
            # ELDER'S ACCEPTANCE TEST (general#12883), applied to this file's LAST surviving
            # instance of the defect it names: a missing page used to be silently skipped, so a
            # probe that found NOTHING rendered exactly like a stage that was CLEAN. "An
            # instrument whose null output is indistinguishable from its healthy output is not an
            # instrument." Unreadable targets are now reported as their own loud category.
            unreadable.append(rel)
            continue
        txt = open(p, errors="replace").read()
        e = {"page": rel, "highest_F": _covered_f(txt)}   # COVERAGE, not max-mentioned (Dawn #16391 fix)
        e["F_behind"] = (front - e["highest_F"]) if (front and e["highest_F"]) else None
        if rel.endswith("horizons.html"):
            hs = [int(m) for m in re.findall(r"\bH(\d{1,2})\b", txt)]
            e["highest_H"] = max(hs) if hs else None
        rows.append(e)
    return {"ledger_front_F": front, "pages": rows, "unreadable": unreadable}


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

    print("\n  ── STAGE 0: FLOWN -> FINDING ── (arcs with >=3 result files and NO finding)")
    if r["arcs"]:
        for e in r["arcs"]:
            off = e.get("offpipeline_docs", 0)
            tag = (f"but {off} docs/*RESULTS* — WRITTEN OFF-PIPELINE, not unwritten"
                   if off else "UNWRITTEN")
            print(f"   ⏳ {e['arc']:4s} {e['results']:3d} results, {e['findings']} findings — {tag}")
        print("      UNWRITTEN and OFF-PIPELINE both end up invisible downstream — no finding,")
        print("      so no F-number, so no ledger row, so no exhibit — but they need different")
        print("      fixes: one needs writing, the other needs an F-number field and a move.")
    else:
        print("      clean — every arc with flown results has at least one finding.")

    lg = r["ledger"]
    print(f"\n  ── STAGE 2: F-NUMBER -> LEDGER ROW ── (ledger front: F{lg['ledger_front']})")
    if lg["missing_from_ledger"]:
        print(f"   ⏳ {len(lg['missing_from_ledger'])} numbered finding(s) have NO ledger row:")
        for f, b in lg["missing_from_ledger"][:12]:
            print(f"       {f:6s} {b[:60]}")
        print("      An F-number without a ledger row is invisible to already-built.js, which")
        print("      greps the ledger — so the campaign's own rediscovery check cannot see it.")
    else:
        print(f"      clean — all {lg['numbered_findings']} numbered findings have ledger rows.")

    ex = r["exhibit"]
    print(f"\n  ── STAGE 3: F-number -> MUSEUM EXHIBIT ── (ledger front: F{ex['ledger_front_F']})")
    for e in ex["pages"]:
        hh = f"   highest H{e['highest_H']}" if e.get("highest_H") else ""
        if e["highest_F"] is None:
            # coverage UNMEASURED (no declared stop, only a scale/count claim like 'F01-F131') — a
            # distinct loud category, NOT '0 behind' (Dawn #16398). Unmeasured ≠ current.
            print(f"   ❓ {e['page']:22s} coverage UNMEASURED — no declared stop, only a scale claim{hh}")
            continue
        beh = f"{e['F_behind']} behind" if e["F_behind"] is not None else "?"
        flag = "⏳" if (e["F_behind"] or 0) > 0 else "  "
        print(f"   {flag} {e['page']:22s} highest F{e['highest_F']}  ({beh}){hh}")
    for miss in ex.get("unreadable", []):
        print(f"   🔴 {miss:22s} TARGET NOT FOUND — this stage is UNMEASURED, not clean.")
    print("\n  THE PATTERN THIS GAUGE EXISTS TO NAME: every cross-seat handoff in the record")
    print("  pipeline queues, and fixing one stage RELOCATES the queue rather than draining it.")
    print("  What never stalls is flights, tanks, seals, submissions, boards — because each is")
    print("  GATED and refuses to proceed. THE STAGES THAT ARE GATED DO NOT STALL; THE STAGES")
    print("  THAT ARE HANDOFFS DO. We metered every QPU-second and left the record layer unwatched.")
    print()
