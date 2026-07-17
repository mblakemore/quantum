#!/usr/bin/env python3
"""Exp144 REVEAL orchestrator (Ember, seal-holder) — chair C4819 "EMBER, REVEAL".

The sealer ADVERTISED `--reveal DIR` in its docstring but never implemented it (do_reveal
absent; argparse dispatches only --seal). That is the untested-path class that bit wave-1
(ModuleNotFoundError) — a path that only runs when it matters, never once exercised. So this
is a SEPARATE minimal orchestrator that REUSES the sealer's own committed serialization
(reveal_record / convseed_reveal_record / reference_verify — the identical functions that
built the commitments), adding no new crypto. It just: read secrets -> build 18 reveal records
-> VERIFY all 18 against the committed hashes -> only then write.

ATOMIC HARD GATE: every one of the 18 must verify against its commitment BEFORE any file is
written. A partial reveal (some published, some not) is worse than none. If any fails, abort
with zero writes.

  python3 exp144_do_reveal_ember.py --check          # verify 18/18, write nothing
  python3 exp144_do_reveal_ember.py --reveal          # verify 18/18 then write reveal records
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "exp144_reveals")


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = _load("sealer", "exp144_seal_reveal_ember.py")


def build_and_verify():
    """Return (records, all_ok). records = [(filename, reveal_dict, verified_bool)]."""
    sec = json.load(open(S.SECRETS_PATH))
    recs, all_ok = [], True

    for n in S.RUNGS:
        for k in S.INSTANCES:
            e = sec["instances"][str(n)][str(k)]
            rr = S.reveal_record(n, k, e["salt_hex"], e["terms"], e["coeffs"])
            cf = os.path.join(S.COMMIT_DIR, f"commitment_{S.ENS}_n{n}_k{k}.json")
            commit = json.load(open(cf))
            ok = S.reference_verify(commit, rr)
            all_ok &= ok
            recs.append((f"reveal_{S.ENS}_n{n}_k{k}.json", rr, ok))

    for n in S.CONVSEED_RUNGS:
        cs = sec["convseeds"][str(n)]
        rr = S.convseed_reveal_record(n, cs["salt_hex"], cs["seed"])
        cf = os.path.join(S.COMMIT_DIR, f"commit_convseed_n{n}.json")
        commit = json.load(open(cf))
        ok = S.convseed_reference_verify(commit, rr)
        all_ok &= ok
        recs.append((f"reveal_convseed_n{n}.json", rr, ok))

    return recs, all_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify 18/18, write nothing")
    ap.add_argument("--reveal", action="store_true", help="verify then WRITE reveal records")
    a = ap.parse_args()
    if not (a.check or a.reveal):
        ap.print_help(); return 0

    recs, all_ok = build_and_verify()
    nver = sum(1 for _, _, ok in recs if ok)
    print(f"reveal records built: {len(recs)} | verified against committed hashes: {nver}/{len(recs)}")
    for fn, _, ok in recs:
        if not ok:
            print(f"  FAIL: {fn} does NOT verify against its commitment")
    if not all_ok or len(recs) != 18:
        print(f"ABORT: {'a reveal record failed verification' if not all_ok else f'expected 18 records, got {len(recs)}'}. "
              f"NOTHING WRITTEN — a partial or unverified reveal is worse than none.")
        return 1

    if a.check:
        print("CHECK PASS: 18/18 verify. Re-run with --reveal to publish.")
        return 0

    # Atomic-ish write: all 18 verified above; now publish.
    os.makedirs(OUT_DIR, exist_ok=True)
    for fn, rr, _ in recs:
        p = os.path.join(OUT_DIR, fn)
        if os.path.exists(p):
            print(f"REFUSING: {fn} already exists — reveal already published? Not overwriting.")
            return 3
    for fn, rr, _ in recs:
        with open(os.path.join(OUT_DIR, fn), "w") as f:
            json.dump(rr, f, indent=1)
    print(f"\nREVEALED: 18 reveal records -> {os.path.relpath(OUT_DIR, HERE)}/")
    print("  15 instance (salt+terms+coeffs) + 3 convseed (salt+seed), each verified vs its "
          "committed hash. Published for three-way verification; frozen grader next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
