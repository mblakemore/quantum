#!/usr/bin/env python3
"""Exp142 REVEAL-PATH PRE-FLIGHT (Ember, before the chair calls reveal).

P2 path matrix: wave x submit/decode/grade/seal/reveal. The SEAL path ran once
(C4185). The REVEAL path has NEVER been exercised — same untested-production-path
class (c4186_001/c4188_001) that voided wave 1. If salt encoding, P formatting, or
the preimage concatenation is off by anything, the commitments will not verify and
the whole blind protocol collapses AT the reveal moment, in public, with nothing
recoverable.

So: recompute hash(salt_bytes || utf8("exp142|{ensemble}|{n}|{P}")) for all 4 rungs
from the off-git secrets and compare to the PUBLISHED commitment hashes.

PRINTS NO SECRETS. Only per-rung MATCH/MISMATCH. Nothing here reaches the decoders.
"""
import hashlib
import json
import os

SEC = os.path.expanduser("~/.ember-exp142-secrets.json")
COM = "/droid/repos/quantum/experiments/exp142_commitments"
ENSEMBLE = "fullweight_eps1"

with open(SEC) as f:
    sec = json.load(f)

ok = 0
fail = 0
for n in (4, 6, 8, 10):
    with open(f"{COM}/commitment_{ENSEMBLE}_n{n}.json") as f:
        com = json.load(f)
    published = com["hash_sha256"]

    entry = sec[ENSEMBLE][str(n)]
    P = entry["P"]
    salt_hex = entry.get("salt") or entry.get("salt_hex")
    salt = bytes.fromhex(salt_hex)

    preimage = salt + f"exp142|{ENSEMBLE}|{n}|{P}".encode("utf-8")
    computed = hashlib.sha256(preimage).hexdigest()

    match = (computed == published)
    ok += match
    fail += (not match)
    # Print only the first 12 hex chars of the PUBLISHED hash (already public) and the verdict.
    print(f"n={n:2d}: published {published[:12]} | recomputed {computed[:12]} | "
          f"{'MATCH ✅' if match else 'MISMATCH ❌'}  (P len {len(P)}, salt {len(salt)}B)")

print()
print(f"REVEAL PATH PRE-FLIGHT: {ok}/4 verify" + (" — reveal will be valid on chair call" if fail == 0
      else f" — {fail} MISMATCH, REVEAL WOULD FAIL PUBLICLY, escalate NOW"))
raise SystemExit(0 if fail == 0 else 1)
