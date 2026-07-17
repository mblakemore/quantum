#!/usr/bin/env python3
"""Exp144 conv-seed E2E gate — MY convseed sealer -> ELDER'S REAL verify_convseed.

My convseed verifier was a PLACEHOLDER. I flagged it rather than let it stand as
evidence: it could only prove I agree with my own reading of chair C4776, and my reading
is the thing under test (c4185_001). Elder's grader now ships verify_convseed, so the
placeholder stops counting and the real cell can close.

Uses HIS pinned §6 filenames (commit_convseed_n{n}.json / reveal_convseed_n{n}.json) —
the consumer names the files, not the producer.

  python3 exp144_convseed_gate_ember.py
"""
import hashlib
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, fn):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


S = _load("sealer", "exp144_seal_reveal_ember.py")
G = _load("grader", "exp144_grader.py")

FAILS = 0


def check(label, cond, detail=""):
    global FAILS
    if not cond:
        FAILS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")


def _verify(cp, rp):
    try:
        res = G.verify_convseed(cp, rp)
        return bool(res[0] if isinstance(res, tuple) else res)
    except Exception:
        return False


def main():
    tmp = tempfile.mkdtemp(prefix="cs_gate_")
    print("=== my convseed sealer -> REAL verify_convseed ===")
    for n in (4, 6, 8):
        seed = 1234567890123 + n
        salt = hashlib.sha256(f"cs-{n}".encode()).digest()
        d, _ = S.convseed_commit_hash(salt, n, seed)
        cp = os.path.join(tmp, f"commit_convseed_n{n}.json")
        rp = os.path.join(tmp, f"reveal_convseed_n{n}.json")
        json.dump(S.convseed_commit_record(n, d), open(cp, "w"))
        json.dump(S.convseed_reveal_record(n, salt.hex(), seed), open(rp, "w"))
        check(f"n={n} REAL verify_convseed accepts my records", _verify(cp, rp))

    print("\n=== negatives (the gate must be able to FAIL) ===")
    salt = hashlib.sha256(b"neg").digest()
    d, _ = S.convseed_commit_hash(salt, 6, 777)
    cp = os.path.join(tmp, "commit_convseed_n6.json")
    json.dump(S.convseed_commit_record(6, d), open(cp, "w"))
    rp = os.path.join(tmp, "neg_reveal.json")
    for label, rec in [
        ("swapped seed", S.convseed_reveal_record(6, salt.hex(), 778)),
        ("wrong salt", S.convseed_reveal_record(6, hashlib.sha256(b"x").hexdigest(), 777)),
        ("wrong rung", S.convseed_reveal_record(4, salt.hex(), 777)),
    ]:
        json.dump(rec, open(rp, "w"))
        check(f"{label} REJECTED", not _verify(cp, rp))

    print(f"\nCONVSEED GATE: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
