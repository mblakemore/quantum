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
    ap.add_argument("--resolve", nargs="?", const="*", metavar="NAME",
                    help="ALSO return WHICH ACCOUNT to open (env var + identity). Bare --resolve "
                         "picks the fitting account; --resolve NAME pins one and has the registry "
                         "CONFIRM it fits, rather than a script asserting which account it is.")
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
    # ── C6605 / board#101 (@whisper's proposal, my tool): RESOLVE AN IDENTITY. ───────────────
    # THE GAP THIS CLOSES: this gate answered "does anything fit?" and never "here is the identity
    # to open." So every flight script carried a HARD-CODED CRN, because nothing handed it one —
    # and that is the STRUCTURAL cause of a constant named PAID_CRN holding a FREE ALT3 instance
    # for months, with the truth sitting in a comment one line above it. A name is the only handle
    # a script has when the registry will not give it an identity. It cost two decisions today.
    #
    # F1 IS UNCHANGED AND THAT IS THE POINT: RESOLVING AN IDENTITY IS NOT AUTHORIZING A SPEND.
    # This adds a field to the advisory; it does not move the measurement, which stays at the
    # run()-site guard (assert_explicit_account + the flight's own weather gate). An identity you
    # were handed is still an identity you must name explicitly at invocation.
    if a.resolve:
        cands = [r for r in acct.get("resources", []) if r.get("kind") == "qpu_account"] or acct.get("resources", [])
        if a.resolve != "*":
            cands = [r for r in cands if a.resolve in (r.get("name"), r.get("identity"),
                                                       (r.get("meta") or {}).get("env_var"))]
            if not cands:
                out["resolved"] = None
                out["resolve_error"] = (f"account {a.resolve!r} not in the registry — REFUSING to guess. "
                                        "An unknown account is not a default account.")
        # C6605: BALANCE AND env_var LIVE UNDER meta, NOT AT THE ROW TOP LEVEL. My first pass read
        # r["balance_s"] (always None there) and resolved NOTHING while the gate one line below
        # said "1 account fits" — a self-contradicting output, produced by asserting the payload
        # shape instead of reading it. Caught because the two halves disagreed; a resolve that had
        # merely been WRONG rather than CONTRADICTORY would have shipped.
        meta = lambda r, k: (r.get("meta") or {}).get(k)
        # Only ever resolve something the registry says FITS and is authorized; never the first row.
        fit = [r for r in cands if (meta(r, "balance_s") or 0) >= a.need
               and r.get("authorization") == "open" and r.get("state") == "up"]
        if fit:
            r = sorted(fit, key=lambda x: -(meta(x, "balance_s") or 0))[0]
            out["resolved"] = {"env_var": meta(r, "env_var"), "identity": r.get("identity"),
                               "name": r.get("name"), "balance_s": meta(r, "balance_s"),
                               "authorization": r.get("authorization"),
                               "observed_at": r.get("observed_at"),
                               "advisory": True,
                               "note": "IDENTITY ONLY — not authorization. Name it explicitly at "
                                       "invocation (QPU_ACCOUNT_VAR); assert_explicit_account() "
                                       "still refuses an unnamed account."}
        elif "resolved" not in out:
            out["resolved"] = None
            out["resolve_error"] = ("no account both FITS and is authorized — nothing to resolve. "
                                    "This is not a default; it is an absence.")

    if a.json:
        print(json.dumps(out, indent=1))
    elif a.resolve:
        r = out.get("resolved")
        print(f"🔑 RESOLVED: env_var={r['env_var']} balance={r['balance_s']}s auth={r['authorization']}"
              if r else f"🔑 UNRESOLVED: {out.get('resolve_error')}")

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
