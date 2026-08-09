#!/usr/bin/env python3
"""registry_fit_precheck.py — ADVISORY pre-check against the ship-computer resource registry.

Elder C6596, the named consumer of the 3C fit-gate advisory pattern
(ship-computer/docs/witness-derivation-rules-elder-c6595.md §3-4).

"Can I fly?" is a CONJUNCTION (Ember #7676): an account that FITS and a venue that is UP.
This asks the registry both halves BEFORE any flight-building work is spent.

ADVISORY MEANS (F1): may REFUSE EARLY, may never AUTHORIZE alone. Exit 0 here does NOT
clear a submission — the runtime submit-guard at run() (full-CRN pin, balance re-read,
backend assert, per-JOB fit gate) remains the measurement. The registry is a cache of
someone else's measurement.

Usage:
  python3 tools/registry_fit_precheck.py --need 181 --venue ibm_marrakesh [--stale-min 45] [--json]

Exit codes (distinct by contract — F2: the consumer must not collapse the reason):
  0 = account FITS and venue UP        -> proceed to the runtime guard
  5 = venue wall (not 'up')            -> weather/scheduling, no account state helps
  4 = GATED (fits but for authorization) -> ask the declare-key holder; capacity is not the problem
  3 = MEASURE FIRST (unmeasured rows / stale readings) -> unknown is neither fit nor unfit
  1 = REFUSE (nothing fits, measured)
  2 = registry unreachable             -> UNKNOWN, not zero; fall back to direct instruments
"""
import argparse, json, os, sys, urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("UHURA_URL", "http://127.0.0.1:8790")

def get(path):
    key = open(os.path.expanduser("~/.uhura-key")).read().strip()
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)

def age_min(iso):
    if not iso:
        return None
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - t).total_seconds() / 60.0
    except ValueError:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--need", type=int, required=True, help="required seconds")
    ap.add_argument("--venue", required=True, help="backend name, e.g. ibm_marrakesh")
    ap.add_argument("--stale-min", type=float, default=45.0,
                    help="reading older than this = unmeasured for this gate (F3; feeder cadence 15m)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        acct = get(f"/resources?kind=qpu_account&need={a.need}")
        ven = get("/resources?kind=qpu_backend")
    except Exception as e:
        print(f"🔴 REGISTRY UNREACHABLE ({e}) — fit is UNKNOWN, not zero. "
              "Use direct instruments (Alpaca-clock-style venue check + account balance read).")
        sys.exit(2)

    bd = acct["derived"].get("breakdown", {})
    vrow = next((r for r in ven["resources"]
                 if r["identity"].endswith(":" + a.venue) or r["name"] == a.venue), None)

    # F3: stale readings demote to unmeasured AT THE CONSUMER.
    stale_notes = []
    for label, obs in (("accounts", acct["resources"][0].get("observed_at") if acct["resources"] else None),
                       ("venue", vrow.get("observed_at") if vrow else None)):
        m = age_min(obs)
        if m is None or m > a.stale_min:
            stale_notes.append(f"{label} reading {'missing' if m is None else f'{m:.0f}min old'} (> {a.stale_min:.0f}min tolerance)")

    out = {"need_s": a.need, "venue": a.venue, "breakdown": bd,
           "venue_state": vrow["state"] if vrow else None,
           "venue_blind_spots": vrow.get("blind_spots") if vrow else None,
           "stale": stale_notes, "advisory": "exit 0 does NOT authorize; run()-site guard governs"}
    if a.json:
        print(json.dumps(out, indent=1))

    if stale_notes:
        print("⚠️ MEASURE FIRST (stale/absent readings): " + "; ".join(stale_notes))
        sys.exit(3)
    if vrow is None:
        print(f"⚠️ MEASURE FIRST: venue {a.venue} not in registry — unknown is neither up nor down.")
        sys.exit(3)
    if vrow["state"] != "up":
        print(f"⛔ VENUE WALL: {a.venue} is '{vrow['state']}' — weather/scheduling; no account state helps. "
              f"(blind_spots: {vrow.get('blind_spots') or 'none declared'})")
        sys.exit(5)
    if bd.get("fitting", 0) > 0:
        print(f"✅ PRE-CHECK CLEAR: {bd['fitting']} account(s) fit {a.need}s and {a.venue} is up. "
              "Proceed to the RUNTIME guard — this is advisory, not authorization.")
        sys.exit(0)
    if bd.get("gated", 0) > 0:
        print(f"🔒 GATED: {bd['gated']} account(s) fit BUT FOR authorization — ask the declare-key holder; "
              "capacity is not the problem.")
        sys.exit(4)
    if bd.get("unmeasured", 0) > 0:
        print(f"⚠️ MEASURE FIRST: {bd['unmeasured']} account(s) unmeasured — unknown is neither fit nor unfit.")
        sys.exit(3)
    print(f"⛔ REFUSE: nothing fits {a.need}s, measured (too_small={bd.get('too_small', 0)}, "
          f"unavailable={bd.get('unavailable', 0)}).")
    sys.exit(1)

if __name__ == "__main__":
    main()
