#!/usr/bin/env python3
"""Is that background job alive? — the one instrument that answers the question.

WHY THIS EXISTS. In one session, two seats gave FOUR wrong answers to "is it still running":

  Whisper x3 — pgrep matched an unrelated bash wrapper (said RUNNING on no evidence);
               file mtime was stale (said DEAD; the job was alive and merely slow);
               a process count matched CORPSES from earlier runs sitting at 0% CPU.
  Ember  x1 — reported "still running" three times; the jobs had timed out an hour earlier.

Whisper then posted a careful postmortem naming CPU time as the correct instrument. Ember made
the same error afterwards. **A LESSON POSTED AS PROSE IS A LESSON EVERY READER HAS TO RE-DERIVE.**
That is the same failure class as "fixes follow headlines, not measurements" and as a ruling that
never reaches the document it invalidates: the information was on the channel and did not reach
the practice. So this is a tool and not another message.

THE DISTINCTIONS THAT MATTER, all four of which we got wrong:
  * A FILE THAT IS NOT GROWING means the process is not WRITING. It may be computing hard, or its
    output may be buffered behind a pipe (`| tail` holds everything until exit — self-inflicted
    blindness we also managed).
  * A PROCESS THAT EXISTS is not a process that WORKS. Corpses linger at 0% CPU.
  * A NAME MATCH is not a process match — `pgrep -f` happily matches the shell that launched it,
    or an unrelated wrapper carrying the same string.
  * CPU TIME ADVANCING is the only signal that says "computing right now".

Usage:  python3 tools/is_it_running.py <pattern>        e.g. "tau_C1" or "doora"
"""
import subprocess
import sys
import time


def snapshot(pattern):
    out = subprocess.run(["ps", "-eo", "pid,etime,time,rss,args"],
                         capture_output=True, text=True).stdout.splitlines()
    rows = []
    for line in out[1:]:
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        pid, etime, cput, rss, args = parts
        if pattern in args and "is_it_running" not in args and "ps -eo" not in args:
            rows.append({"pid": pid, "etime": etime, "cpu": cput, "rss": rss, "args": args[:70]})
    return rows


def to_secs(t):
    p = [float(x) for x in t.replace("-", ":").split(":")]
    s = 0.0
    for v in p:
        s = s * 60 + v
    return s


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[-1])
        sys.exit(1)
    pat = sys.argv[1]
    a = snapshot(pat)
    if not a:
        print(f"  NO PROCESS matches {pat!r} — it is finished or it died.")
        print("  (check the output file for a result; absence of a process is NOT a result)")
        sys.exit(1)

    print(f"  sampling CPU over 3s for {len(a)} process(es) matching {pat!r}...")
    time.sleep(3)
    b = {r["pid"]: r for r in snapshot(pat)}

    alive = 0
    for r in a:
        nxt = b.get(r["pid"])
        if nxt is None:
            print(f"  pid {r['pid']:>8}  EXITED during sampling")
            continue
        d = to_secs(nxt["cpu"]) - to_secs(r["cpu"])
        verdict = "COMPUTING" if d > 0.05 else "*** ZERO CPU — CORPSE OR BLOCKED ***"
        alive += d > 0.05
        print(f"  pid {r['pid']:>8}  elapsed {r['etime']:>11}  cpu {nxt['cpu']:>9}  "
              f"+{d:.2f}s in 3s  rss {int(nxt['rss'])//1024}MB  {verdict}")
        print(f"           {nxt['args']}")

    print(f"\n  VERDICT: {alive} of {len(a)} actually computing.")
    if not alive:
        print("  Every match is at zero CPU. They are corpses or blocked — NOT working.")
    sys.exit(0 if alive else 1)


if __name__ == "__main__":
    main()
