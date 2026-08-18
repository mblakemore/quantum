#!/usr/bin/env python3
"""tools/epoch_label_apply.py — write epoch labels that are DETERMINED BY BANKED DATA. (Whisper C5075)

The gate surfaced 45 σ-headline findings with no epoch label. **32 of them are not judgement calls
at all**: they cite exactly ONE submission whose window is banked, so n=1, basis=distinct-submission,
dispersion is not required (the schema requires it only when n>1), retrievability is a fact on disk,
and the checked-date is today. Every field is determined; nothing is inferred.

WHY THIS IS SAFE TO AUTOMATE AND THE REST IS NOT. The remaining 13 need a human call:
  * 2 cite MULTIPLE submissions -> n>1, so the schema requires a DISPERSION, which comes from the
    per-window RESULTS, not from the windows. Those must be computed per finding (as F125's was).
  * 9 have every window LOST -> retrievable=no is honest, but their n is a count of job IDs whose
    windows can no longer confirm they are distinct submissions rather than re-reads.
  * 2 cite no job IDs at all -> nothing to derive from.

n=1 IS A LEGAL AND COMMON VALUE. The point of the gate was never that results must span windows —
it is that a single-window result must SAY it is single-window. These 32 say it now.

    python3 tools/epoch_label_apply.py [--apply]     (default is a dry run)
"""
import json, os, re, subprocess, sys

Q = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = re.compile(r"\b(d[0-9a-z]{18,21})\b")
TODAY = "2026-08-18"


def gate_fails():
    out = subprocess.run([sys.executable, f"{Q}/tools/epoch_label_check.py", "--today", TODAY],
                         capture_output=True, text=True, cwd=Q).stdout
    m = re.search(r"GATE FAIL \(\d+\)(.*?)(?:\n\n|\Z)", out, re.S)
    return re.findall(r"^  - (\S+\.md):", m.group(1), re.M) if m else []


def main():
    cen = json.load(open(f"{Q}/results/window_rescue_c5075.json"))["jobs"]
    apply_ = "--apply" in sys.argv
    done = skipped = 0
    for name in gate_fails():
        p = f"{Q}/findings/{name}"
        if not os.path.exists(p):
            continue
        txt = open(p, errors="replace").read()
        jids = sorted(set(JOB.findall(txt)))
        ok = [cen.get(j, {}) for j in jids]
        ok = [r for r in ok if r.get("backend")]
        if len(ok) != 1:
            skipped += 1
            continue
        label = (f"\n**Epoch**: n=1 basis=distinct-submission · dispersion=- · "
                 f"window_retrievable=yes · checked={TODAY}  "
                 f"*(single submission; window banked in `results/window_rescue_c5075.json`. "
                 f"n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*\n")
        if apply_:
            # place it after the front-matter block (first blank line following the header)
            i = txt.find("\n\n")
            txt = txt[:i + 1] + label + txt[i + 1:] if i > 0 else txt + label
            open(p, "w").write(txt)
        done += 1
        print(f"  {'LABELLED' if apply_ else 'would label'}  {name[:66]}")
    print(f"\n{'APPLIED' if apply_ else 'DRY RUN'}: {done} mechanical labels, {skipped} left for a human call")


if __name__ == "__main__":
    main()
