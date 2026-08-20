#!/usr/bin/env python3
"""Two-sided closure of the C5077 age-invariance argument. (Whisper)

The verdict "IBM retention is DATE-anchored" rested on ONE unverified assumption: that exp112's
2026-08-18 loss was GENUINE ABSENCE, not a transient read failure. This checks it, and adds the
second side nobody has run:

  exp112 (2026-07-12, LOST on 08-18): must STILL be lost. If it is retrievable today, the original
      loss was transient and the entire age-invariance argument collapses.
  F106   (2026-07-13, ALIVE at 36d on 08-18): today it is 38d. exp112 dead at 37d forces any rolling
      window to have L<37, which forces F106 DEAD at 38d. If F106 is ALIVE, no rolling window fits
      — an INDEPENDENT confirmation that does not use exp112 at all.

So the two sides fail differently and that is the point: one tests the assumption, the other makes
the conclusion not need it.
"""
import sys
sys.path.insert(0, "/droid/repos/quantum/scripts")
from ibm_multi_account import service_for_job
CASES = {"exp112_youngest_loss": ("d9a19kcqp3as739un8e0", "2026-07-12", "must be LOST (was lost 08-18)"),
         "F106_oldest_success":  ("d9akl8fu62qs738o68pg", "2026-07-13", "must be LOST if ROLLING (38d today)")}
res = {}
for tag, (jid, flown, expect) in CASES.items():
    try:
        svc, acct = service_for_job(jid); svc.job(jid)
        res[tag] = True;  print(f"@@ {tag:22s} {flown}  RETRIEVABLE   [{expect}]")
    except Exception as e:
        res[tag] = False; print(f"@@ {tag:22s} {flown}  LOST ({type(e).__name__})   [{expect}]")
print()
if res["exp112_youngest_loss"]:
    print("@@ ASSUMPTION FALSIFIED — exp112 is retrievable today after reading LOST on 08-18.")
    print("@@ The 08-18 loss was TRANSIENT. The age-invariance argument COLLAPSES; verdict withdrawn.")
elif res["F106_oldest_success"]:
    print("@@ DATE-ANCHORED, CONFIRMED TWO-SIDED.")
    print("@@   exp112 still absent -> the 08-18 loss was genuine, assumption HOLDS.")
    print("@@   F106 alive at 38d   -> independently kills every rolling window with L<37,")
    print("@@                          WITHOUT using exp112 at all. The conclusion no longer")
    print("@@                          depends on the assumption it was resting on.")
else:
    print("@@ F106 LOST at 38d while exp112 stays lost — CONSISTENT WITH ROLLING after all.")
    print("@@ The wall advanced between 36d and 38d. Verdict FLIPS to ROLLING; bank OLDEST-FIRST.")
