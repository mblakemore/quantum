#!/usr/bin/env python3
"""
check_backend_status.py — hang-proof IBM Quantum backend availability check.

WHY THIS EXISTS (Elder C5480 diagnosis of the Exp30 SUBMIT-BLOCKED incident):
  The qiskit_ibm_runtime client's QiskitRuntimeService().backend(name) call was
  hanging indefinitely (>60s) on 2026-05-29, blocking a whole cognitive cycle —
  the quantum analog of the C4107 "never let a network call hang a cycle" lesson.

  Root-cause investigation showed the IBM Quantum *REST API* itself is healthy and
  fast (status ~1.1s, configuration ~0.25s, properties ~0.63s). The hang is in the
  qiskit client object construction, not the service. This tool therefore talks to
  the new IBM Quantum Platform REST API directly (quantum.cloud.ibm.com), with a
  hard wall-clock timeout on every request, so a device-availability check can NEVER
  hang a cycle.

  Use this BEFORE attempting any qiskit submit to confirm the target device is
  `active`/not in maintenance and to see the queue depth.

CREDENTIALS:
  Reads the saved IBM Cloud API key + default instance CRN from ~/.qiskit/qiskit-ibm.json
  (the same account the qiskit scripts use). The saved 'instance' field (a service CRN)
  is required as the Service-CRN header for the new platform API. Elder C5480 added that
  field to the saved account (it was missing → caused the init-time discovery hang).

USAGE:
  python3 scripts/check_backend_status.py                 # all open-plan backends
  python3 scripts/check_backend_status.py ibm_marrakesh   # one device, detailed
  python3 scripts/check_backend_status.py --json          # machine-readable

EXIT CODES:
  0 = at least one requested device is operational and NOT in maintenance
  1 = requested device(s) exist but none are submit-ready (maintenance/offline)
  2 = credential / network / API error
"""
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

ACCOUNT_PATH = os.path.expanduser("~/.qiskit/qiskit-ibm.json")
ACCOUNT_KEY = "default-ibm-quantum-platform"
IAM_URL = "https://iam.cloud.ibm.com/identity/token"
API_BASE = "https://quantum.cloud.ibm.com/api/v1"
REQ_TIMEOUT = 25  # hard per-request wall-clock cap (seconds) — anti-hang


def _load_account():
    with open(ACCOUNT_PATH) as fh:
        acct = json.load(fh)[ACCOUNT_KEY]
    token = acct.get("token")
    crn = acct.get("instance")
    if not token:
        raise RuntimeError("no token in saved account")
    if not crn:
        raise RuntimeError(
            "no 'instance' (Service-CRN) in saved account — run the C5480 account fix "
            "(add the open-instance CRN to ~/.qiskit/qiskit-ibm.json)"
        )
    return token, crn


# IBM IAM rejects the default Python-urllib User-Agent with HTTP 403 — send a
# browser-ish UA + Accept on every request (curl works because it sets its own UA).
_BASE_HEADERS = {"User-Agent": "dc-quantum/1.0", "Accept": "application/json"}


def _post(url, data, headers):
    body = urllib.parse.urlencode(data).encode()
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.load(resp)


def _get(url, headers):
    hdrs = {**_BASE_HEADERS, **headers}
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    with urllib.request.urlopen(req, timeout=REQ_TIMEOUT) as resp:
        return json.load(resp)


def _iam_token(api_key):
    out = _post(
        IAM_URL,
        {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        {"Content-Type": "application/x-www-form-urlencoded"},
    )
    return out["access_token"]


def fetch_status(bearer, crn, name):
    hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}
    t = time.time()
    st = _get(f"{API_BASE}/backends/{name}/status", hdr)
    st["_latency_s"] = round(time.time() - t, 2)
    return st


def list_backends(bearer, crn):
    hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}
    return _get(f"{API_BASE}/backends", hdr).get("devices", [])


def main():
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if not a.startswith("--")]
    targets = args  # specific device names, or empty = all

    try:
        token, crn = _load_account()
        bearer = _iam_token(token)
        all_devices = list_backends(bearer, crn)
    except Exception as e:  # noqa: BLE001
        msg = {"error": str(e)}
        print(json.dumps(msg) if as_json else f"❌ ERROR: {e}")
        return 2

    if not targets:
        targets = all_devices

    results = []
    submit_ready = 0
    for name in targets:
        if name not in all_devices:
            results.append({"name": name, "available_on_plan": False})
            continue
        try:
            st = fetch_status(bearer, crn, name)
        except Exception as e:  # noqa: BLE001
            results.append({"name": name, "available_on_plan": True, "status_error": str(e)})
            continue
        status = st.get("status", "unknown")
        reachable = st.get("state", False)
        queue = st.get("length_queue")
        ready = bool(reachable) and status not in ("maintenance", "offline", "internal")
        if ready:
            submit_ready += 1
        results.append(
            {
                "name": name,
                "available_on_plan": True,
                "reachable": reachable,
                "status": status,
                "queue": queue,
                "submit_ready": ready,
                "latency_s": st.get("_latency_s"),
            }
        )

    if as_json:
        print(json.dumps({"plan_devices": all_devices, "results": results}, indent=2))
    else:
        print("═" * 56)
        print("IBM QUANTUM BACKEND STATUS (REST, hang-proof)")
        print("═" * 56)
        print(f"Plan devices: {', '.join(all_devices) or '(none)'}")
        print("-" * 56)
        for r in results:
            if not r.get("available_on_plan"):
                print(f"  {r['name']}: ❌ NOT on this plan")
                continue
            if "status_error" in r:
                print(f"  {r['name']}: ⚠️ status error: {r['status_error']}")
                continue
            flag = "✅ READY" if r["submit_ready"] else "⛔ NOT submit-ready"
            print(
                f"  {r['name']}: {flag}  status={r['status']} "
                f"queue={r['queue']} ({r['latency_s']}s)"
            )
        print("═" * 56)

    return 0 if submit_ready > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
