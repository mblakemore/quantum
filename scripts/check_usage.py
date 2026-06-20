#!/usr/bin/env python3
"""
check_usage.py — Read-only IBM Quantum account/instance usage check.

Diagnoses the recurring Ember-E9 cancellation hypothesis (C3538): the IBM SDK
warning "This instance has met its usage limit" suggests an ACCOUNT-LEVEL usage
quota is exhausted, causing queued jobs to be cancelled regardless of backend.

This script confirms or denies that hypothesis empirically by querying the
platform usage endpoint(s). Read-only — never submits or cancels.

WHAT THE NUMBER MEANS (Whisper C4245 — ends a recurring ambiguity):
  `instances/usage.usage_consumed_seconds` is billed QPU-SECONDS (quantum
  runtime actually executed on hardware), NOT wall-clock. The Open-plan cap is
  600 QPU-seconds (~10 min) over a ROLLING 28-day window. Two consequences that
  burned prior cycles re-litigating "is 600/600 stale?":
    1. Local classical simulations (e.g. exp54/exp55/exp57 warm-start runs) do
       NOT consume this budget — they eat wall-time, not QPU-seconds.
    2. `usage_limit_reached: true` at 600/600 is therefore the REAL depletion
       signal, not the inflated wall-clock metric. When it says reached, it is
       genuinely reached — the lever is a Creator top-up, not "wait, it's stale."

USAGE:
  python3 scripts/check_usage.py

EXIT CODES:
  0 = budget available (usage_limit_reached false)
  1 = budget exhausted (usage_limit_reached true) — hardware jobs will be blocked
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


def _summarize(usage):
    """Human-readable verdict from instances/usage. Returns exit code (0/1)."""
    print("\n=== SUMMARY (QPU-seconds, NOT wall-clock) ===")
    if not isinstance(usage, dict):
        print("  ⚠ Could not retrieve instances/usage — see errors above.")
        return 2
    consumed = usage.get("usage_consumed_seconds")
    limit = usage.get("usage_limit_seconds")
    reached = usage.get("usage_limit_reached")
    period = usage.get("usage_period", {})
    try:
        pct = 100.0 * float(consumed) / float(limit) if limit else float("nan")
        pct_s = f"{pct:.0f}%"
        remaining = max(0.0, float(limit) - float(consumed))
    except (TypeError, ValueError):
        pct_s, remaining = "?", "?"
    print(f"  Consumed : {consumed} / {limit} QPU-seconds ({pct_s})")
    print(f"  Remaining: {remaining} QPU-seconds")
    print(f"  Window   : {period.get('start_time', '?')} → {period.get('end_time', '?')} (rolling ~28d)")
    if reached:
        print("  VERDICT  : 🔴 EXHAUSTED — hardware jobs will be blocked/cancelled.")
        print("             This is the REAL QPU-second counter, not stale wall-time.")
        print("             Lever = Creator top-up (standing offer). Local sims unaffected.")
        return 1
    print("  VERDICT  : 🟢 AVAILABLE — hardware submission permitted.")
    return 0


def main():
    try:
        token, crn = _load_account()
        bearer = _iam_token(token)
    except Exception as e:
        print(f"❌ Credential error: {e}")
        return 2

    hdr = {"Authorization": f"Bearer {bearer}", "Service-CRN": crn}
    print(f"Instance CRN: {crn[:60]}...")

    # instances/usage is the authoritative QPU-second counter (confirmed C4245).
    # The old /usage probe is a confirmed 404 and has been dropped.
    _try("instances/configuration", f"{API_BASE}/instances/configuration", hdr)
    usage = _try("instances/usage", f"{API_BASE}/instances/usage", hdr)
    return _summarize(usage)


if __name__ == "__main__":
    sys.exit(main())
