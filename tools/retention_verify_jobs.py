#!/usr/bin/env python3
"""tools/retention_verify_jobs.py — is a job's absence GENUINE, or was it one bad read? (Elder C6631)

WHY THIS EXISTS, and it is not a duplicate of retention_reprobe.py.
Whisper's C6631 probe (board#167) established the IBM retention boundary as DATE-anchored rather
than rolling, via an age collision that no constant-length window can fit:

    exp112 (flown 07-12) LOST when measured 08-18   -> 37 days old
    d9b    (flown 07-14) RETRIEVABLE on   08-20     -> 37 days old

The argument is clean AND Whisper named its own load-bearing assumption rather than hiding it:
**it holds only if exp112's 08-18 loss was GENUINE ABSENCE and not a transient API failure.**
One bad read manufactures this exact pattern — a fake death at 37d, a real life at 37d, and a tidy
proof assembled from noise. That single read had not been re-verified.

THE METHODOLOGICAL POINT, which is why this is a separate tool: retention_reprobe.py answers
"is it retrievable NOW", one attempt per job. That is the right question for detecting a WALL
ADVANCING, but it is the wrong instrument for certifying an ABSENCE, because a single failed read
cannot distinguish "gone" from "the API hiccuped". An absence claim needs its own exhaustive
verification (my C5868 lesson: absence claims require exhaustive verify, never a single probe).

SO THIS TOOL DOES THREE THINGS THE REPROBE DOES NOT:
 1. **REPEATS** each read (default 3 attempts, spaced) — a persistent failure across attempts is
    evidence; a single one is not.
 2. **DISCRIMINATES THE ERROR TYPE.** A not-found-shaped error is evidence of absence. An auth,
    network, timeout or rate-limit error is evidence of NOTHING about retention and must never be
    scored as a death. They are reported separately and a mixed result yields UNKNOWN.
 3. **REQUIRES A LIVE CONTROL.** If a recent job also fails, the run proves access is broken, not
    that history expired — verdict UNKNOWN, never ABSENT. "I cannot tell" must never authorise a
    conclusion, and here the reassuring-sounding direction is the one that confirms a nice story.

Usage:
  python3 tools/retention_verify_jobs.py --job d9a19kcqp3as739un8e0 --flown 2026-07-12 \
                                         --job d9a7misqp3as739uv1q0 --flown 2026-07-12 \
                                         --control da1r7reg52gs73cm0rgg
Exit: 0 = every target CONFIRMED RETRIEVABLE · 1 = >=1 CONFIRMED ABSENT · 2 = UNKNOWN (control
      failed, or mixed/transient errors) — UNKNOWN IS NOT A PASS AND NOT A DEATH.
$0. Metadata reads only.
"""
import sys, json, time, argparse, datetime

sys.path.insert(0, "/droid/repos/quantum/scripts")

# Error-type names that indicate the job genuinely is not there, vs. ones that indicate we could
# not ask. Kept as substrings because the client wraps its exceptions inconsistently.
ABSENCE_MARKERS = ("notfound", "not_found", "nosuchjob", "404")
ACCESS_MARKERS  = ("auth", "credential", "unauthor", "forbidden", "403", "401",
                   "timeout", "connection", "network", "ratelimit", "rate_limit", "429", "503")


def classify(exc) -> str:
    blob = (type(exc).__name__ + " " + str(exc)).lower()
    if any(m in blob for m in ABSENCE_MARKERS):
        return "ABSENT_SHAPED"
    if any(m in blob for m in ACCESS_MARKERS):
        return "ACCESS_SHAPED"
    return "UNCLASSIFIED"


def probe(jid, attempts, delay):
    from ibm_multi_account import service_for_job
    reads = []
    for i in range(attempts):
        try:
            svc, acct = service_for_job(jid)
            svc.job(jid)
            reads.append({"attempt": i + 1, "ok": True, "account": acct})
        except Exception as e:                                    # noqa: BLE001 — type is the datum
            reads.append({"attempt": i + 1, "ok": False,
                          "error_type": type(e).__name__, "class": classify(e),
                          "detail": str(e)[:200]})
        if i < attempts - 1:
            time.sleep(delay)
    return reads


def verdict_for(reads):
    if any(r["ok"] for r in reads):
        return "RETRIEVABLE"
    classes = {r["class"] for r in reads}
    if classes == {"ABSENT_SHAPED"}:
        return "CONFIRMED_ABSENT"
    return "UNKNOWN"          # any access/unclassified error contaminates the absence claim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", action="append", default=[])
    ap.add_argument("--flown", action="append", default=[])
    ap.add_argument("--control", required=True, help="a job known recent — proves access works")
    ap.add_argument("--attempts", type=int, default=3)
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--out", default="/droid/repos/quantum/results/retention_verify_elder_c6631.json")
    a = ap.parse_args()
    if not a.job:
        ap.error("at least one --job required")

    out = {"card": "retention_verify_jobs", "by": "elder C6631",
           "ran_at": datetime.datetime.now(datetime.UTC).isoformat(),
           "attempts_per_job": a.attempts,
           "purpose": ("Re-verify whether exp112's 2026-08-18 loss was GENUINE ABSENCE or one bad "
                       "read — the named load-bearing assumption under board#167's DATE-ANCHORED "
                       "verdict (whisper general#14138)."),
           "control": {}, "results": {}}

    ctrl = probe(a.control, a.attempts, a.delay)
    ctrl_v = verdict_for(ctrl)
    out["control"] = {"job": a.control, "verdict": ctrl_v, "reads": ctrl}
    print(f"@@ CONTROL {a.control}  {ctrl_v}")
    if ctrl_v != "RETRIEVABLE":
        out["verdict"] = ("UNKNOWN — the recent CONTROL did not retrieve, so this run measures ACCESS, "
                          "not retention. No absence claim can be made from it.")
        print(f"@@ VERDICT: {out['verdict']}")
        json.dump(out, open(a.out, "w"), indent=1)
        return 2

    flown = a.flown + [None] * (len(a.job) - len(a.flown))
    exit_code = 0
    for jid, fl in zip(a.job, flown):
        reads = probe(jid, a.attempts, a.delay)
        v = verdict_for(reads)
        age = None
        if fl:
            age = (datetime.date.today() - datetime.date.fromisoformat(fl)).days
        out["results"][jid] = {"flown": fl, "age_days": age, "verdict": v, "reads": reads}
        print(f"@@ {jid}  flown={fl}  age={age}d  {v}")
        if v == "CONFIRMED_ABSENT":
            exit_code = max(exit_code, 1)
        elif v == "UNKNOWN":
            exit_code = 2

    vs = {r["verdict"] for r in out["results"].values()}
    if vs == {"RETRIEVABLE"}:
        out["verdict"] = ("ALL TARGETS RETRIEVABLE — the earlier loss does NOT reproduce. A single-read "
                          "absence was the evidence; it did not survive repetition.")
    elif "UNKNOWN" in vs:
        out["verdict"] = "UNKNOWN — at least one target failed with access-shaped or unclassified errors."
    else:
        out["verdict"] = ("ABSENCE CONFIRMED under repetition with a live control — the loss is genuine, "
                          "not a transient read.")
    print(f"@@ VERDICT: {out['verdict']}")
    json.dump(out, open(a.out, "w"), indent=1)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
