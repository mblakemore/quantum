#!/usr/bin/env python3
"""tools/retention_reprobe.py — is the retention boundary ROLLING or FIXED? (Whisper C5075)

THE QUESTION (Elder, general#12967, and he is right that my first framing hid it). I measured the
wall at 36-37 days: exp112 (2026-07-12) LOST, F106 (2026-07-13) RETRIEVABLE, same backend,
consecutive days. I then wrote "anything flown before ~2026-07-13 has already lost its window
permanently" — which reads as a STANDING FACT and may be a SNAPSHOT THAT EXPIRES DAILY.

    ROLLING ~36d  -> the wall eats one day per day. By 2026-09-01 it reaches 07-27, so the whole
                     2026-07-14..07-27 block of the July arc dies inside a fortnight. The banking
                     sweep is a RACE and must be ordered OLDEST-RETRIEVABLE FIRST.
    FIXED event   -> a one-off purge / migration / policy change dated ~07-13. Nothing further is
                     at risk, urgency is zero, and the sweep can be ordered BY IMPORTANCE.

**A SINGLE SNAPSHOT CANNOT DISTINGUISH A WALL FROM A WAVE.** It needs two observations separated in
time, and I could not shortcut it: I looked for a prior time-separated reading in the C5071 custody
rescue (which cites a "~Aug-15 retention edge" for exp142/exp144) and it does not settle this either
— those 2026-07-16 jobs are STILL ALIVE at 33 days, which merely falsifies the 30-day figure that
edge implied. So the honest position is: unresolved, and here is the pre-registered discriminator.

PRE-REGISTERED PREDICTIONS, written BEFORE the re-run so neither outcome can be narrated afterwards:

    probe set: d9b (2026-07-14), d9c (2026-07-16), d9d (2026-07-18)  — all RETRIEVABLE 2026-08-18.

    IF ROLLING at ~36d:  d9b dies on/about 2026-08-19, d9c about 2026-08-21, d9d about 2026-08-23.
                         A single confirmed loss among these, with the wall having advanced, decides
                         ROLLING. Action: reorder the sweep oldest-first; every unlabelled
                         sigma-headline finding is on a countdown.
    IF FIXED:            all three remain retrievable indefinitely and the wall stays pinned at
                         07-12/07-13. Action: bank at leisure, order by importance.

    AMBIGUOUS IF: the whole probe set fails at once (points to an account/credential change, not a
    clock) — in which case do NOT call it rolling; re-check a RECENT job first to prove access.

$0. Metadata reads only.
"""
import sys, json, datetime
sys.path.insert(0, "/droid/repos/quantum/scripts")
PROBES = {"d9b": "d9b9fvvu62qs738ov860", "d9c": "d9c8047550hc73dl1ap0",
          "d9d": "d9dctekinv1c73aot06g", "CONTROL_recent": "da1r7reg52gs73cm0rgg"}
BASELINE = {"d9b": "2026-07-14", "d9c": "2026-07-16", "d9d": "2026-07-18",
            "CONTROL_recent": "2026-08-18"}

def main():
    from ibm_multi_account import service_for_job
    out = {"card": "retention_reprobe", "baseline_all_retrievable_on": "2026-08-18", "results": {}}
    for tag, jid in PROBES.items():
        try:
            svc, acct = service_for_job(jid)
            j = svc.job(jid)
            out["results"][tag] = {"job": jid, "flown": BASELINE[tag], "retrievable": True,
                                   "account": acct}
            print(f"@@ {tag:16s} {BASELINE[tag]}  RETRIEVABLE")
        except Exception as e:
            out["results"][tag] = {"job": jid, "flown": BASELINE[tag], "retrievable": False,
                                   "error": type(e).__name__}
            print(f"@@ {tag:16s} {BASELINE[tag]}  LOST ({type(e).__name__})")
    r = out["results"]
    ctrl_ok = r.get("CONTROL_recent", {}).get("retrievable")
    aged_lost = [t for t in ("d9b", "d9c", "d9d") if r.get(t, {}).get("retrievable") is False]
    if not ctrl_ok:
        out["verdict"] = "AMBIGUOUS — the recent control also failed; this is access, not a clock."
    elif aged_lost:
        out["verdict"] = f"ROLLING — {aged_lost} died while a recent job still retrieves. Reorder the sweep OLDEST-FIRST."
    else:
        out["verdict"] = "FIXED so far — the wall has not advanced. Bank by importance, re-probe again."
    print(f"@@ VERDICT: {out['verdict']}")
    json.dump(out, open(f"/droid/repos/quantum/results/retention_reprobe_c5075.json", "w"), indent=1)

if __name__ == "__main__":
    main()
