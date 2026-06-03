#!/usr/bin/env python3
"""
check_job_status.py — Read-only IBM Quantum job status check (no cancellation).

Use THIS for status checks. Use cancel_job.py only when you intend to cancel.

USAGE:
  python3 scripts/check_job_status.py <job_id>
  python3 scripts/check_job_status.py d8fu393o3njc73f0rsqg

OUTPUT:
  Job ID, status, backend, created time, estimated_start_time_in_seconds (bss)

EXIT CODES:
  0 = success (job found)
  1 = job not found or permission error
  2 = credential / network / API error
"""
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

_BASE_HEADERS = {"User-Agent": "dc-quantum/1.0", "Accept": "application/json"}


def _load_account():
    with open(ACCOUNT_PATH) as fh:
        acct = json.load(fh)[ACCOUNT_KEY]
    return acct["token"], acct["instance"]


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


def _get(url, headers):
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.load(resp)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/check_job_status.py <job_id>")
        return 1

    job_id = sys.argv[1].strip()
    print(f"Checking IBM Quantum job: {job_id}")

    try:
        token, crn = _load_account()
        bearer = _iam_token(token)
    except Exception as e:
        print(f"❌ Credential error: {e}")
        return 2

    hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}

    try:
        d = _get(f"{API_BASE}/jobs/{job_id}", hdr)
        status = d.get("status", "unknown")
        backend = d.get("backend", "?")
        created = d.get("created", "")[:19]
        bss = d.get("estimated_start_time_in_seconds", "N/A")
        print(f"  Status:  {status}")
        print(f"  Backend: {backend}")
        print(f"  Created: {created}")
        print(f"  BSS:     {bss}")
        if status == "DONE":
            print("  ✅ Ready to finalize.")
        elif status == "Queued":
            if bss == 0 or bss == "0":
                print("  ⚠️  bss=0 — possible fairshare stall (never started despite queue=0)")
            else:
                print(f"  ⏳ Queued, estimated wait: {bss}s")
        elif status in ("CANCELLED", "ERROR"):
            print(f"  🔴 Terminal state: {status}")
        return 0
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ Job {job_id} not found")
            return 1
        print(f"❌ HTTP {e.code}: {e.read().decode()}")
        return 2
    except Exception as e:
        print(f"❌ Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
