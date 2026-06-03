#!/usr/bin/env python3
"""
cancel_job.py — Cancel or status-check an IBM Quantum job via REST API (hang-proof).

⚠️  WARNING: Default mode CANCELS QUEUED jobs. Use --status for status-check only.
    Ember C3526 / Whisper C3827 lesson: accidental cancel from "status check" is a real hazard.

Same auth pattern as check_backend_status.py (direct REST, no qiskit client).

USAGE:
  python3 scripts/cancel_job.py --status <job_id>     # ✅ STATUS CHECK ONLY (no cancel)
  python3 scripts/cancel_job.py <job_id>              # ⚠️  CANCEL job (destructive)

EXIT CODES:
  0 = success (cancelled or status shown)
  1 = failed (job not found, already done, permission error)
  2 = credential / network / API error
"""
import json
import os
import sys
import urllib.request
import urllib.error

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


def _post_form(url, data, headers):
    import urllib.parse
    body = urllib.parse.urlencode(data).encode()
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.load(resp)


def _delete(url, headers):
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, headers=hdrs, method="DELETE")
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        try:
            return json.load(resp)
        except Exception:
            return {}


def _get(url, headers):
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.load(resp)


def _iam_token(api_key):
    out = _post_form(
        IAM_URL,
        {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
        {"Content-Type": "application/x-www-form-urlencoded"},
    )
    return out["access_token"]


def main():
    # Parse --status flag (Ember C3526 safety fix: status-check ≠ cancel)
    status_only = False
    args = sys.argv[1:]
    if args and args[0] == "--status":
        status_only = True
        args = args[1:]
    if not args:
        print("Usage: python3 scripts/cancel_job.py --status <job_id>   # status check only")
        print("       python3 scripts/cancel_job.py <job_id>            # CANCEL (destructive)")
        return 1

    job_id = args[0].strip()
    if status_only:
        print(f"Checking IBM Quantum job: {job_id}")
    else:
        print(f"⚠️  CANCELLING IBM Quantum job: {job_id}  (use --status for status check only)")

    try:
        token, crn = _load_account()
        bearer = _iam_token(token)
    except Exception as e:
        print(f"❌ Credential error: {e}")
        return 2

    hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}

    # Check current status first
    try:
        status_data = _get(f"{API_BASE}/jobs/{job_id}", hdr)
        status = status_data.get("status", "unknown")
        backend = status_data.get("backend", "unknown")
        created = status_data.get("created", "N/A")
        bss = status_data.get("estimated_start_time", "N/A")
        print(f"  Status:  {status}")
        print(f"  Backend: {backend}")
        print(f"  Created: {created}")
        print(f"  BSS:     {bss}")
        if status == "Queued":
            print(f"  ⏳ Queued, estimated wait: {bss}s")
        elif status == "Running":
            print(f"  🔄 Running")
        elif status in ("DONE", "Completed"):
            print(f"  ✅ Completed")
        if status in ("DONE", "ERROR", "CANCELLED", "Completed", "Failed", "Cancelled"):
            print(f"  Job is already terminal ({status}) — no cancel needed.")
            return 0
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ Job {job_id} not found")
            return 1
        print(f"❌ Status check failed: {e}")
        return 2

    # If --status only, stop here
    if status_only:
        return 0

    # Cancel — IBM Quantum requires POST /jobs/{id}/cancel, not DELETE /jobs/{id}
    try:
        post_hdr = {**hdr, "Content-Type": "application/json"}
        req = urllib.request.Request(
            f"{API_BASE}/jobs/{job_id}/cancel",
            data=b"{}",
            headers={**_BASE_HEADERS, **post_hdr},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
            try:
                result = json.load(resp)
            except Exception:
                result = {}
        print(f"✅ Cancel request sent. Response: {result}")
        # Verify cancellation
        try:
            status_data2 = _get(f"{API_BASE}/jobs/{job_id}", hdr)
            new_status = status_data2.get("status", "unknown")
            print(f"  Post-cancel status: {new_status}")
        except Exception:
            pass
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ Cancel failed (HTTP {e.code}): {body}")
        return 1
    except Exception as e:
        print(f"❌ Cancel error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
