#!/usr/bin/env python3
"""Exp142 REVEAL WRITER (Ember) — emits reveal_{ensemble}_n{N}.json for the frozen grader.

Endgame step 2 (chair C4760 scope): the WRITER->FILE->GRADER path is the last
un-exercised slice. My C4193 preimage pre-flight validated the SECRETS (recomputed
hashes match published commitments 4/4). This validates that what the writer
actually WRITES is what the frozen grader actually READS.

Schema is dictated by the FROZEN CONSUMER (exp142_grader.py verify_commitment),
not by this writer and not by the sealer (c4185_001: read the frozen consumer's
input schema; the frozen artifact is the authority):
    r["salt_hex"], r["ensemble"], r["n"], r["P"]
    path: <commitments_dir>/reveal_{ensemble}_n{N}.json

NOTE ON THE COMMITMENT KEY (already known + bridged by Elder, NOT a new find):
the frozen grader reads c["sha256"] while my published commitment files carry
"hash_sha256". Elder's dry-run harness parameterizes this (key = sha256 |
hash_sha256 | both) and his run uses a dual-key scratch bridge. This writer does
not touch commitment files at all — it only emits reveal files.

Usage:
  python3 exp142_reveal_writer_ember.py --outdir DIR      # write reveal files
  python3 exp142_reveal_writer_ember.py --outdir DIR --verify  # + parse/hash check

--verify runs ONLY the frozen grader's verify_commitment() (hash + ensemble + n).
It deliberately does NOT run the full grader against real answer files: that would
compare P_hat to P and hand me the verdict before the chair calls the reveal.
"""
import argparse
import importlib.util
import json
import os

ENS = "fullweight_eps1"
RUNGS = (4, 6, 8, 10)
SEC = os.path.expanduser("~/.ember-exp142-secrets.json")
HERE = os.path.dirname(os.path.abspath(__file__))
COMMITS = os.path.join(HERE, "exp142_commitments")


def write_reveals(outdir):
    with open(SEC) as f:
        sec = json.load(f)
    os.makedirs(outdir, exist_ok=True)
    paths = {}
    for n in RUNGS:
        e = sec[ENS][str(n)]
        salt_hex = e.get("salt") or e.get("salt_hex")
        # Exactly the four keys the frozen grader reads. Nothing extra:
        # an unexpected key is harmless here, but a MISSING or RENAMED one is find #6.
        rec = {"n": n, "ensemble": ENS, "salt_hex": salt_hex, "P": e["P"]}
        p = os.path.join(outdir, f"reveal_{ENS}_n{n}.json")
        with open(p, "w") as f:
            json.dump(rec, f, indent=1)
        paths[n] = p
    return paths


def verify(outdir):
    """Import the FROZEN grader and call its own verify_commitment on our files."""
    spec = importlib.util.spec_from_file_location(
        "grader", os.path.join(HERE, "exp142_grader.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)

    fails = 0
    for n in RUNGS:
        rpath = os.path.join(outdir, f"reveal_{ENS}_n{n}.json")
        cpath_pub = os.path.join(COMMITS, f"commitment_{ENS}_n{n}.json")

        # Dual-key scratch bridge (Elder's, replicated locally): the frozen grader
        # reads c["sha256"]; the published file carries "hash_sha256". Bridge in a
        # SCRATCH copy — the published commitment is never modified.
        with open(cpath_pub) as f:
            c = json.load(f)
        c["sha256"] = c.get("sha256", c["hash_sha256"])
        cpath = os.path.join(outdir, f"commitment_{ENS}_n{n}.json")
        with open(cpath, "w") as f:
            json.dump(c, f)

        try:
            ok, P = g.verify_commitment(cpath, rpath)
        except KeyError as ex:
            print(f"  n={n:2d}: SCHEMA FAIL — frozen grader KeyError {ex}")
            fails += 1
            continue
        except Exception as ex:
            print(f"  n={n:2d}: FAIL — {type(ex).__name__}: {ex}")
            fails += 1
            continue
        # Print only the verdict and P's LENGTH — never P itself.
        print(f"  n={n:2d}: frozen grader parsed writer output, commitment "
              f"{'VERIFIES ✅' if ok else 'MISMATCH ❌'} (P len {len(P)})")
        fails += (not ok)
    return fails


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()

    paths = write_reveals(a.outdir)
    print(f"wrote {len(paths)} reveal files -> {a.outdir}")
    for n, p in paths.items():
        with open(p) as f:
            keys = sorted(json.load(f).keys())
        print(f"  reveal_{ENS}_n{n}.json keys={keys}")

    if a.verify:
        print("\nfrozen-grader verify_commitment() against writer output:")
        fails = verify(a.outdir)
        print(f"\nWRITER->FILE->GRADER PATH: {'PASS' if fails == 0 else f'FAIL ({fails})'}")
        raise SystemExit(1 if fails else 0)
