#!/usr/bin/env python3
"""
check_usage.py — Read-only IBM Quantum account/instance usage check.

Diagnoses the recurring Ember-E9 cancellation hypothesis (C3538): the IBM SDK
warning "This instance has met its usage limit" suggests an ACCOUNT-LEVEL usage
quota is exhausted, causing queued jobs to be cancelled regardless of backend.

This script confirms or denies that hypothesis empirically by querying the
platform usage endpoint(s). Read-only — never submits or cancels.

USAGE:
  python3 scripts/check_usage.py

EXIT CODES:
  0 = success (usage data retrieved)
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


def _try(label, url, hdr):
    try:
        d = _get(url, hdr)
        print(f"\n=== {label} ===")
        print(json.dumps(d, indent=2)[:2000])
        return d
    except urllib.error.HTTPError as e:
        print(f"\n=== {label} ===")
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        print(f"\n=== {label} ===")
        print(f"  Error: {e}")
    return None


def main():
    try:
        token, crn = _load_account()
        bearer = _iam_token(token)
    except Exception as e:
        print(f"❌ Credential error: {e}")
        return 2

    hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}
    print(f"Instance CRN: {crn[:60]}...")

    # The platform exposes usage at the instance level. Endpoint names have
    # shifted across API versions; probe the known candidates read-only.
    _try("usage", f"{API_BASE}/usage", hdr)
    _try("instances/configuration", f"{API_BASE}/instances/configuration", hdr)
    _try("instances/usage", f"{API_BASE}/instances/usage", hdr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
