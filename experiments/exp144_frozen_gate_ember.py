#!/usr/bin/env python3
"""Exp144 FREEZE GATE (Ember) — chair C4782 sequence step 2: dummy-e2e vs the FROZEN hashes.

The point is NOT to re-run my gates (they pass). It is to prove they passed against the
EXACT artifacts that were frozen. Every green cell I hold was earned against a working-tree
file; between then and the seal, Elder hashes the package. If any byte moved, my evidence
is stale — and I have already been caught by exactly that tonight: my §6 25/25 ran at 01:17
against grader e133f6d, he changed the grader at 01:54, and I only noticed because I went
looking. I did not notice on my own the first time; the cell was mine and it was green.

So: verify each frozen sha256 FIRST, refuse on any mismatch, and only then re-run the
gates. A gate result that cannot name the artifact hash it ran against is a rumour.

Usage — paste Elder's posted list:
  python3 exp144_frozen_gate_ember.py --hashes hashes.json
  python3 exp144_frozen_gate_ember.py \\
      --hash exp144-preregistration.md=abc123... --hash exp144_grader.py=def456...
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The gates that must be re-run against frozen bytes, in order of what they protect.
GATES = [
    ("§6 commitment e2e (real grader)", "exp144_e2e_gate_ember.py"),
    ("convseed e2e (real verify_convseed)", "exp144_convseed_gate_ember.py"),
    ("submit seam (real builders)", "exp144_submit_seam_ember.py"),
    ("seed interface (seed controls order)", "exp144_seed_interface_ember.py"),
    ("§1 matrix ground truth", "exp144_matrix_groundtruth_ember.py"),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hashes", help="JSON {filename: sha256} as posted at freeze")
    ap.add_argument("--hash", action="append", default=[],
                    help="filename=sha256 (repeatable)")
    ap.add_argument("--skip-gates", action="store_true",
                    help="verify hashes only, do not re-run gates")
    a = ap.parse_args()

    expected = {}
    if a.hashes:
        with open(a.hashes) as f:
            expected.update(json.load(f))
    for item in a.hash:
        k, _, v = item.partition("=")
        expected[k.strip()] = v.strip().lower()

    if not expected:
        print("REFUSING: no frozen hashes given. The whole point of this gate is to bind "
              "my green cells to specific bytes; running it with nothing to check would be "
              "ceremony.")
        return 2

    print("=== [1] FROZEN HASH VERIFICATION (refuse on any mismatch) ===")
    bad = 0
    for fname, want in sorted(expected.items()):
        path = fname if os.path.isabs(fname) else os.path.join(HERE, os.path.basename(fname))
        if not os.path.exists(path):
            # try repo-root-relative (prereg lives beside experiments/)
            alt = os.path.join(HERE, "..", fname)
            path = alt if os.path.exists(alt) else path
        if not os.path.exists(path):
            print(f"  [FAIL] {fname}: NOT FOUND locally")
            bad += 1
            continue
        got = sha256_file(path)
        ok = (got == want.lower())
        if not ok:
            bad += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {os.path.basename(fname)}: "
              f"{got[:16]}{'' if ok else f' != frozen {want[:16]}'}")

    if bad:
        print(f"\nREFUSING TO PROCEED: {bad} artifact(s) do not match the frozen hashes.\n"
              f"My gate results were earned against DIFFERENT bytes and are therefore stale.\n"
              f"Do not seal. Re-pull, re-verify, re-run.")
        return 1
    print(f"  all {len(expected)} artifacts match the freeze")

    if a.skip_gates:
        return 0

    print("\n=== [2] RE-RUN GATES AGAINST THE FROZEN BYTES ===")
    fails = 0
    for label, script in GATES:
        p = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           capture_output=True, text=True)
        ok = (p.returncode == 0)
        if not ok:
            fails += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        if not ok:
            print("    " + (p.stdout or p.stderr).strip().splitlines()[-1][:100])

    print(f"\nFREEZE GATE: {'PASS — cells are green against the FROZEN artifacts' if fails == 0 else f'FAIL ({fails})'}")
    if fails == 0:
        print("Cleared for step 3: seal 15 instances + 3 convseeds.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
