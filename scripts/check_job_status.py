#!/usr/bin/env python3
"""
check_job_status.py — Read-only IBM Quantum job status check (no cancellation).

Use THIS for status checks. Use cancel_job.py only when you intend to cancel.

USAGE:
  python3 scripts/check_job_status.py <job_id>
  python3 scripts/check_job_status.py d8fu393o3njc73f0rsqg

MULTI-INSTANCE (fixed Whisper C5014):
  Jobs live in an *instance*, and a job in instance A is a 404 when you ask
  instance B. This script used to query only the default instance, so every
  ALT-instance flight reported "Job not found" — indistinguishable from a job
  that died. It now sweeps EVERY configured instance and only reports
  not-found when all of them miss, naming which ones it checked.

  No flag to remember: the sweep is automatic. (Decision-time hook over
  vigilance — a flag you must remember to pass is a flag you forget on the
  cycle it mattered.)

OUTPUT:
  Job ID, instance it was found in, status, backend, created time,
  elapsed wait, and estimated_start_time_in_seconds (bss).

EXIT CODES:
  0 = success (job found in some instance)
  1 = job not found in ANY configured instance, or permission error
  2 = credential / network / API error
"""
import datetime as _dt
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

ACCOUNT_PATH = os.path.expanduser("~/.qiskit/qiskit-ibm.json")
ACCOUNT_KEY = "default-ibm-quantum-platform"
IAM_URL = "https://iam.cloud.ibm.com/identity/token"
API_BASE = "https://quantum.cloud.ibm.com/api/v1"
REQ_TIMEOUT = 25

# ALT open-instance: separate account + separate API key, so it needs its own
# bearer. Token lives in Whisper's .env as IBMQ_ALT (flights read it the same way).
# ALT2 (C5017): second fresh open instance provided by the Creator at the C1 GO —
# added BEFORE its first job existed, so the reader never 404s the network's own flight.
ALT_ENV_PATH = "/mnt/droid/repos/DC15W/.env"
ALT_ENV_KEY = "IBMQ_ALT"
ALT_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
           "a/1e9b7ff09baf49ef875846a9eb696283:44cfd6bd-c143-4ed4-8bc0-9d560992006f::")
ALT2_ENV_KEY = "IBMQ_ALT2"
ALT2_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/1b1bf449de574a3b8c1f9112d67ddc88:e37900dc-58ec-49d0-882d-9da0bf8bc0ba::")

_BASE_HEADERS = {"User-Agent": "dc-quantum/1.0", "Accept": "application/json"}


def _load_account():
    with open(ACCOUNT_PATH) as fh:
        acct = json.load(fh)[ACCOUNT_KEY]
    return acct["token"], acct["instance"]


def _load_env_token(key):
    """Return an api key from the env file, or None if unavailable (never fatal).
    Exact-key match: 'IBMQ_ALT' must not swallow 'IBMQ_ALT2'."""
    try:
        with open(ALT_ENV_PATH) as fh:
            for line in fh:
                if line.strip().startswith(key + "="):
                    return line.strip().split("=", 1)[1]
    except OSError:
        pass
    return None


def _load_alt_token():
    return _load_env_token(ALT_ENV_KEY)


def _instances():
    """All instances we can look in, as (label, api_key, crn)."""
    out = []
    try:
        token, crn = _load_account()
        out.append(("default", token, crn))
    except Exception as e:
        print(f"  ⚠️  default instance unreadable: {e}")
    alt = _load_alt_token()
    if alt:
        out.append(("ALT", alt, ALT_CRN))
    else:
        print(f"  ⚠️  ALT token not found at {ALT_ENV_PATH} — ALT jobs will read as not-found")
    alt2 = _load_env_token(ALT2_ENV_KEY)
    if alt2:
        out.append(("ALT2", alt2, ALT2_CRN))
    else:
        print(f"  ⚠️  ALT2 token not found at {ALT_ENV_PATH} — ALT2 jobs will read as not-found")
    return out


def _iam_token(api_key):
    body = urllib.parse.urlencode(
        {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key}
    ).encode()
    req = urllib.request.Request(
        IAM_URL, data=body,
        headers={**_BASE_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.load(resp)["access_token"]


def _get(url, headers, retries=1):
    """GET with one retry on transient network failure.

    HTTPError (404/403 = 'not in this instance') is NOT retried — it is a real
    answer. Only timeouts and connection faults are, because a flaky read must
    never be allowed to masquerade as a clean miss.
    """
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError:
            raise
        except Exception:
            if attempt == retries:
                raise


def _elapsed(created):
    """Human elapsed time since `created` (ISO8601), or None if unparseable."""
    if not created:
        return None
    try:
        ts = created.replace("Z", "+00:00")
        then = _dt.datetime.fromisoformat(ts)
        if then.tzinfo is None:
            then = then.replace(tzinfo=_dt.timezone.utc)
        secs = (_dt.datetime.now(_dt.timezone.utc) - then).total_seconds()
        return f"{int(secs // 3600)}h{int(secs % 3600 // 60):02d}m", secs
    except Exception:
        return None


def _report(label, d):
    status = str(d.get("status", "unknown"))
    backend = d.get("backend", "?")
    created = d.get("created", "")
    bss = d.get("estimated_start_time_in_seconds", "N/A")

    print(f"  Instance: {label}")
    print(f"  Status:   {status}")
    print(f"  Backend:  {backend}")
    print(f"  Created:  {created[:19]}")

    el = _elapsed(created)
    if el:
        pretty, secs = el
        print(f"  Elapsed:  {pretty} since submit")
    else:
        secs = None
    print(f"  BSS:      {bss}")

    # Case-insensitive: the REST API and the qiskit client disagree on case
    # ("Queued" vs "QUEUED"), and the old exact-match let QUEUED fall through
    # with no annotation at all.
    # ...and the two APIs also use different WORDS for the same terminal state:
    # REST says "Completed", the qiskit client says "DONE". Accept both.
    s = status.upper()
    if s in ("DONE", "COMPLETED"):
        print("  ✅ Ready to finalize.")
    elif s in ("QUEUED", "PENDING"):
        if str(bss) == "0":
            print("  ⚠️  bss=0 — possible fairshare stall (never started despite queue=0)")
        elif bss in (None, "N/A"):
            print("  ⏳ Queued, no ETA published (normal on the open instance)")
        else:
            print(f"  ⏳ Queued, estimated wait: {bss}s")
        if secs and secs > 12 * 3600:
            print(f"  ⚠️  queued >12h — treat as a stall and investigate/resubmit")
    elif s in ("CANCELLED", "ERROR", "FAILED"):
        print(f"  🔴 Terminal state: {status}")
    elif s == "RUNNING":
        print("  ▶️  Running on hardware.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/check_job_status.py <job_id>")
        return 1

    job_id = sys.argv[1].strip()
    print(f"Checking IBM Quantum job: {job_id}")

    instances = _instances()
    if not instances:
        print("❌ No usable instances configured.")
        return 2

    checked, hard_errors = [], []
    for label, api_key, crn in instances:
        checked.append(label)
        try:
            bearer = _iam_token(api_key)
        except Exception as e:
            print(f"  ⚠️  {label}: credential error: {e}")
            hard_errors.append(label)
            continue

        hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}
        try:
            d = _get(f"{API_BASE}/jobs/{job_id}", hdr)
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                continue  # not in this instance — keep sweeping
            print(f"  ⚠️  {label}: HTTP {e.code}: {e.read().decode()[:200]}")
            hard_errors.append(label)
            continue
        except Exception as e:
            print(f"  ⚠️  {label}: {e}")
            hard_errors.append(label)
            continue

        _report(label, d)
        return 0

    # Only now is "not found" an honest verdict — every instance missed.
    print(f"❌ Job {job_id} not found in any instance (checked: {', '.join(checked)})")
    if hard_errors:
        print(f"   ⚠️  but {', '.join(hard_errors)} errored rather than cleanly missing — "
              f"the job could be there. Not a confirmed absence.")
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
