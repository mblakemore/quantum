#!/usr/bin/env python3
"""Exp144 SECRET-LEAK GATE (Ember) — a check that EXITS NONZERO, not one that prints.

WHY THIS FILE EXISTS (C4194, and it is embarrassing): at seal time I ran an inline leak
check that printed "❌ LEAK in commit_convseed_n4.json" — and then committed and pushed
anyway, because the check wrote to stdout instead of exiting non-zero and my shell `&&`
chain sailed straight through it. I verified it was a false positive AFTER the push. It
was harmless (the word "seed" matched inside the schema name "exp144-convseed-commit-v1";
the files contain a hash and nothing else). Had it been a real seed, I would have published
the conventional sweep order of a frozen experiment to a public repo and voided F2(b).

Twice in one night now: my discord-chat warning fired on me and I posted wrong anyway;
my leak check fired and I pushed anyway. A WARNING CHANGES WHAT YOU CAN SEE, NOT WHAT YOU
DO. A safety check that does not gate is a comment.

So this one gates. It exits 1 on any suspicion, and it distinguishes the two cases that
actually matter instead of grepping for words that appear in schema names:

  1. VALUE leak (fatal): a real secret VALUE from the secrets file appears in a file
     about to be committed. Checked against the ACTUAL plaintext, not against a wordlist.
  2. SHAPE leak (fatal): a commitment file has any key other than the pinned schema.

  python3 exp144_leak_gate_ember.py            # gate the commitment dir
  python3 exp144_leak_gate_ember.py --staged   # gate whatever git has staged
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = os.path.expanduser("~/.ember-exp144-secrets.json")
COMMIT_DIR = os.path.join(HERE, "exp144_commitments")

# Exactly the keys the frozen §6 schema permits. Anything else is a shape leak.
ALLOWED = {
    "exp144-commit-v1": {"schema", "ensemble", "n", "instance", "sha256"},
    "exp144-convseed-commit-v1": {"schema", "ensemble", "n", "sha256"},
}


def secret_values():
    """Every literal secret VALUE. Checking against these beats grepping for the word
    'seed' — which matches the schema name and cries wolf, which is how you learn to
    ignore your own gate."""
    with open(SECRETS) as f:
        s = json.load(f)
    vals = set()
    for n, ks in s.get("instances", {}).items():
        for k, e in ks.items():
            vals.add(e["salt_hex"])
            vals.update(e["terms"])
            vals.update(f"{c:+.2f}" for c in e["coeffs"])
    for n, e in s.get("convseeds", {}).items():
        vals.add(e["salt_hex"])
        vals.add(str(e["seed"]))
    return {v for v in vals if len(str(v)) >= 4}   # ignore trivially short tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true", help="check git-staged files instead")
    a = ap.parse_args()

    if not os.path.exists(SECRETS):
        print("REFUSING: no secrets file — nothing to compare against. This gate cannot "
              "do its job and must not pretend it did.")
        return 2

    vals = secret_values()
    if a.staged:
        out = subprocess.run(["git", "diff", "--cached", "--name-only"],
                             capture_output=True, text=True, cwd=os.path.join(HERE, ".."))
        files = [os.path.join(HERE, "..", f) for f in out.stdout.split() if os.path.exists(
            os.path.join(HERE, "..", f))]
    else:
        files = glob.glob(os.path.join(COMMIT_DIR, "*"))

    print(f"=== leak gate: {len(files)} file(s) vs {len(vals)} secret values ===")
    fatal = 0

    for path in files:
        try:
            raw = open(path, "rb").read()
        except IsADirectoryError:
            continue
        # 1. VALUE leak — the only question that matters.
        hits = [v for v in vals if str(v).encode() in raw]
        if hits:
            print(f"  ❌ VALUE LEAK in {os.path.basename(path)}: {hits[:3]}")
            fatal += 1
            continue
        # 2. SHAPE leak — unexpected keys in a commitment record.
        if path.endswith(".json") and "commit" in os.path.basename(path):
            try:
                d = json.load(open(path))
            except Exception:
                continue
            allowed = ALLOWED.get(d.get("schema"))
            if allowed is None:
                print(f"  ❌ UNKNOWN SCHEMA in {os.path.basename(path)}: {d.get('schema')}")
                fatal += 1
                continue
            extra = set(d) - allowed
            if extra:
                print(f"  ❌ SHAPE LEAK in {os.path.basename(path)}: unexpected keys {extra}")
                fatal += 1
                continue
        print(f"  ✅ {os.path.basename(path)}")

    print(f"\nLEAK GATE: {'PASS' if fatal == 0 else f'FAIL ({fatal}) — DO NOT COMMIT'}")
    return 1 if fatal else 0     # <- the whole point: this GATES.


if __name__ == "__main__":
    sys.exit(main())
