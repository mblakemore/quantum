#!/usr/bin/env python3
"""QPU REGISTRY FEEDER (Ember C4266) — the health tool becomes the registry's SENSOR.

Board task#5. Runs `qpu_resource_health_ember_c4262.py --json` and upserts each account and
each backend into the ship computer's resource registry via `POST /resources`, on a timer.

WHY A FEEDER AND NOT A REPORT: a report is something a person reads when they think to look.
Six exp142 jobs went into a `usage_limit_reached` account that ACCEPTS submissions and never
runs them, and an earlier job sat there 8h45m — not because the fact was unavailable, but
because nobody queried it at the moment of submission. A registry row is queryable by anything,
including a watch that fires before a flight.

CONTRACT DISCIPLINE (docs/board-contract-v1-FROZEN-elder-c6595.md):

  · SENSOR PATH ONLY — state, meta, observed_at, updated_by. This process cannot write
    `authorization` or `billing` even by accident: they are creator-declared, and a sensor on a
    timer that could reach them would eventually overwrite a human ruling at 3am.
  · ROWS ARE BORN CLOSED. Creation defaults to spend_gated/paid. A resource this feeder
    discovers is NOT spendable until a person declares it open — unknown must never mean
    permitted.
  · `state` CARRIES ABSOLUTE FACTS ONLY. flagged→`flagged`, maintenance→`paused`. No health
    verdict is ever stored: `usable` once read TRUE on ten seconds, and fitness is a property
    of an account AND a job, computed at query time against a stated need.
  · A MISSING READING IS `null`, NEVER 0. If the poll errors, balance_s is null and the row
    lands in `unmeasured_count` — not in the total, not in `fitting_count`. An account nobody
    could measure is the one most likely to surprise you, and zeroing it hides it in the
    safest-looking bucket.

TWO KINDS, BECAUSE "CAN I FLY?" IS A CONJUNCTION. `qpu_account` carries seconds; `qpu_backend`
carries device status. 484 seconds in the tank is worth nothing while ibm_marrakesh is in
maintenance — that pairing is what actually held door (b) tonight, and neither row alone says it.

STDOUT DISCIPLINE: qiskit writes warnings to stderr, so the health tool's JSON is read from
stdout ALONE. Merging the streams breaks the parse — verified, not assumed.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HEALTH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "qpu_resource_health_ember_c4262.py")
BUS = os.environ.get("SHIP_BUS", "http://127.0.0.1:8790")
KEY_FILE = os.path.expanduser("~/.uhura-key")

ACCOUNT_BLIND_SPOTS = (
    "usage counter is a TRAILING 28-DAY WINDOW, not a lifetime total — a balance that looks "
    "spent may refill by aging out, and a per-job sum will not reconcile against it. "
    "Poll is point-in-time: a concurrent job can consume the tank between this reading and a "
    "submission."
)
BACKEND_BLIND_SPOTS = (
    "status is a point-in-time poll — a device can enter maintenance between this reading and "
    "a submission, and queue depth says nothing about how long the jobs ahead will run."
)


def bearer():
    with open(KEY_FILE) as f:
        return f.read().strip()


def post(path, body):
    req = urllib.request.Request(f"{BUS}{path}", data=json.dumps(body).encode(),
                                 method="POST")
    req.add_header("Authorization", f"Bearer {bearer()}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
    except Exception as e:                      # noqa: BLE001 — a feeder must not die on the bus
        return 0, {"error": type(e).__name__, "detail": str(e)[:80]}


def read_health(with_backends):
    cmd = [sys.executable, HEALTH, "--json"]
    if with_backends:
        cmd.append("--backends")
    # stdout ONLY. qiskit's warnings go to stderr and merging them breaks the parse.
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if not p.stdout.strip():
        raise RuntimeError(f"health tool produced no JSON (rc={p.returncode})")
    return json.loads(p.stdout)


def account_row(r, observed_at):
    """Map one health row to a SENSOR upsert. Absolute facts only."""
    err = r.get("error")
    if err or r.get("crn") is None:
        # UNMEASURED. state unknown, balance null — never 0, which would read as 'empty'
        # and sit quietly in the total instead of surfacing as un-polled.
        return {"state": "unknown",
                "meta": {"balance_s": None, "limit_s": None, "flagged": None,
                         "poll_error": err or "no crn returned"}}
    return {"state": "flagged" if r.get("flagged") else "up",
            "meta": {"balance_s": r.get("remaining"),
                     "limit_s": r.get("limit"),
                     "consumed_s": r.get("consumed"),
                     "flagged": bool(r.get("flagged")),
                     "token_fingerprint": r.get("fp"),      # fingerprint only, never the token
                     "instance_name": r.get("name"), "env_var": r.get("token"),
                     "crn_tail": r.get("crn_tail")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="single pass then exit")
    ap.add_argument("--interval", type=int, default=600, help="seconds between passes")
    ap.add_argument("--no-backends", action="store_true", help="skip device status (faster)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    while True:
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            rows = read_health(not a.no_backends)
        except Exception as e:                  # noqa: BLE001
            print(f"[{stamp}] health read FAILED: {type(e).__name__}: {e}", flush=True)
            if a.once:
                return 1
            time.sleep(a.interval)
            continue

        sent = skipped = failed = 0
        seen_backends = {}
        for r in rows:
            crn = r.get("crn")
            if not crn:
                skipped += 1
                continue
            body = {"identity": crn, "observed_at": stamp, "updated_by": "qpu_health_feeder",
                    # C4272 DEFECT, found by @whisper registering ALT4: EVERY free IBM account
                    # reports instance_name "open-instance", so ALT/ALT2/ALT3 all landed in the
                    # registry under ONE name. Rows were keyed correctly by CRN (identity) and were
                    # therefore distinct — but INDISTINGUISHABLE TO A READER, and allocation is done
                    # by readers. A name identical across distinct resources is not a name.
                    #
                    # The env-var label (IBMQ_ALT3 etc.) was available in the health row as `token`
                    # the whole time and I never used it. It is unique per account, it is what every
                    # human and script already calls these, and it is what a spend decision needs.
                    # Provider name retained in meta so nothing is lost.
                    # PARTIAL FIX CAUGHT BY ITS OWN DRY RUN: env-var alone still collides,
                    # because ONE KEY CAN HOLD MULTIPLE INSTANCES — IBMQ_TOKEN carries three CRNs,
                    # so three rows came back named "IBMQ_TOKEN@DC15E". The env var is unique per
                    # KEY, not per ACCOUNT, and the row IS an account. Disambiguate with the CRN
                    # tail, which is what makes the row unique in the first place.
                    "name": ((r.get("token") or r.get("name") or "acct")
                             + "/" + (r.get("crn_tail") or "?")[-8:]),
                    "kind": "qpu_account",
                    "blind_spots": ACCOUNT_BLIND_SPOTS}
            body.update(account_row(r, stamp))
            if a.dry_run:
                print(f"  WOULD upsert {body['name']:<16} state={body['state']:<8} "
                      f"balance_s={body['meta'].get('balance_s')}")
            else:
                code, resp = post("/resources", body)
                if code == 200:
                    sent += 1
                else:
                    failed += 1
                    print(f"  [{code}] {body['name']}: {resp}", flush=True)

            # backends are shared across accounts; upsert each device ONCE per pass
            for d in r.get("backends", []) or []:
                name = d.get("name")
                if not name or name in seen_backends:
                    continue
                seen_backends[name] = True
                st = (d.get("status") or "").lower()
                state = ("up" if st == "active" else
                         "paused" if "maint" in st else
                         "down" if st in ("inactive", "offline") else "unknown")
                bbody = {"identity": f"ibm-backend:{name}", "name": name,
                         "kind": "qpu_backend", "blind_spots": BACKEND_BLIND_SPOTS,
                         "observed_at": stamp, "updated_by": "qpu_health_feeder",
                         "state": state,
                         "meta": {"queue_depth": d.get("queue"), "status_msg": d.get("status")}}
                if a.dry_run:
                    print(f"  WOULD upsert backend {name:<16} state={state}")
                else:
                    code, resp = post("/resources", bbody)
                    if code == 200:
                        sent += 1
                    else:
                        failed += 1
                        print(f"  [{code}] backend {name}: {resp}", flush=True)

        # HEARTBEAT ITSELF LAST, and only after the real work — so the row reports what this
        # pass ACTUALLY did rather than that it started. Mirrors watchd's service row (Whisper):
        # the sensor everything else depends on was the one thing the registry could not see.
        #
        # Its blind_spot is the honest one: a DEAD feeder cannot write this row, so ABSENCE OF
        # FRESHNESS is the signal — which means something that is NOT the feeder has to read
        # the age. That reader is the derived block's oldest_observation_age_s. A heartbeat
        # proves liveness while it arrives and says nothing once it stops.
        if not a.dry_run:
            post("/resources", {
                "identity": "service:qpu-feeder", "name": "qpu-feeder", "kind": "service",
                "blind_spots": ("staleness IS the liveness signal — a dead feeder cannot mark "
                                "itself down, so read observed_at age from a consumer, never "
                                "trust this row's own state field. Cadence 15 min."),
                "state": "up" if not failed else "flagged",
                "observed_at": stamp, "updated_by": "qpu_registry_feeder",
                "meta": {"upserted": sent, "failed": failed, "skipped": skipped,
                         "backends_seen": len(seen_backends), "pid": os.getpid(),
                         "cadence_s": a.interval if not a.once else 900},
            })
        print(f"[{stamp}] upserted {sent}, failed {failed}, skipped {skipped} "
              f"({len(seen_backends)} backends)", flush=True)
        if a.once:
            return 0 if not failed else 1
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
