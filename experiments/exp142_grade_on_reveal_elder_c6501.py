#!/usr/bin/env python3
"""Exp142 GRADE-ON-REVEAL runner — Elder C6501 (endgame step 4).

Runs the FROZEN grader (exp142_grader.py f281deb36ab8…, unmodified, subprocess)
the moment Ember publishes reveal_fullweight_eps1_n{N}.json, via the dual-key
scratch-commitments BRIDGE (grader reads c["sha256"]; published commitments carry
"hash_sha256" — bridge adds both, both frozen artifacts untouched; dry-run-proven
8/8 at fa56333, and Ember independently confirmed the bridge real at step 2).

BLINDNESS GUARD: refuses to run until the reveal files exist (the grader compares
P_hat to P == the verdict; running early would leak it before the chair calls reveal).

What it does when reveal is present:
  1. scratch commitments dir: copy each published commitment_*.json adding
     sha256 = hash_sha256 (dual key) + copy the reveal_*.json as-is
  2. scratch answers dir: copy my final identified answer files -> answers_n{N}.json
  3. run frozen grader <scratch_commits> <scratch_answers>; print JSON stdout VERBATIM
  4. also re-verify each published commitment hash against the reveal preimage
     independently (sha256(salt||"exp142|{ens}|{n}|{P}")), a second check the
     grader also does — belt and suspenders at the finish.

Usage:
  python3 exp142_grade_on_reveal_elder_c6501.py            # grade (needs reveal files)
  python3 exp142_grade_on_reveal_elder_c6501.py --dry      # structure check, no grade
"""
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "exp142_grader.py")
COMMIT_DIR = os.path.join(HERE, "exp142_commitments")
RESULTS = os.path.join(HERE, "..", "results")
ENS = "fullweight_eps1"
NS = (4, 6, 8, 10)

# final identified answer files (the rung at which conv arm closed), by n
FINAL_ANSWERS = {
    4: "answers_n4_w3_elder_c6496.json",
    6: "answers_n6_w3_elder_c6496.json",
    8: "answers_n8_w4_elder_c6497.json",
    10: "answers_n10_w7_elder_c6500.json",
}


def reveal_present():
    return all(os.path.exists(os.path.join(COMMIT_DIR, f"reveal_{ENS}_n{n}.json"))
               for n in NS)


def build_scratch():
    cdir = tempfile.mkdtemp(prefix="exp142_grade_commits_")
    adir = tempfile.mkdtemp(prefix="exp142_grade_answers_")
    for n in NS:
        # dual-key commitment
        src = os.path.join(COMMIT_DIR, f"commitment_{ENS}_n{n}.json")
        c = json.load(open(src))
        if "sha256" not in c and "hash_sha256" in c:
            c["sha256"] = c["hash_sha256"]     # THE BRIDGE (add, never rename)
        json.dump(c, open(os.path.join(cdir, f"commitment_{ENS}_n{n}.json"), "w"))
        # reveal as-is
        shutil.copy(os.path.join(COMMIT_DIR, f"reveal_{ENS}_n{n}.json"),
                    os.path.join(cdir, f"reveal_{ENS}_n{n}.json"))
        # answers -> canonical name
        shutil.copy(os.path.join(RESULTS, FINAL_ANSWERS[n]),
                    os.path.join(adir, f"answers_n{n}.json"))
    return cdir, adir


def independent_hash_check():
    """Second, grader-independent verification of each commitment vs its reveal."""
    out = {}
    for n in NS:
        c = json.load(open(os.path.join(COMMIT_DIR, f"commitment_{ENS}_n{n}.json")))
        r = json.load(open(os.path.join(COMMIT_DIR, f"reveal_{ENS}_n{n}.json")))
        published = c.get("hash_sha256") or c.get("sha256")
        digest = hashlib.sha256(
            bytes.fromhex(r["salt_hex"]) +
            f"exp142|{r['ensemble']}|{r['n']}|{r['P']}".encode()).hexdigest()
        out[n] = {"match": digest == published,
                  "published_prefix": published[:12], "recomputed_prefix": digest[:12]}
    return out


def main():
    dry = "--dry" in sys.argv
    if dry:
        print("DRY: structure check only (no grade).")
        print("grader:", GRADER, "exists:", os.path.exists(GRADER))
        for n in NS:
            print(f"  n={n} final answers:", FINAL_ANSWERS[n],
                  "exists:", os.path.exists(os.path.join(RESULTS, FINAL_ANSWERS[n])))
        print("reveal files present:", reveal_present(),
              "(expected False pre-reveal)")
        return 0

    if not reveal_present():
        print("BLINDNESS GUARD: reveal_*.json not yet published — refusing to grade "
              "(the grader compares P_hat to P; running now would leak the verdict "
              "before the chair calls reveal). Re-run after Ember publishes reveal.")
        return 3

    ind = independent_hash_check()
    print("=== Independent commitment-vs-reveal hash check (grader-independent) ===")
    for n in NS:
        print(f"  n={n}: {'MATCH' if ind[n]['match'] else 'MISMATCH'} "
              f"(published {ind[n]['published_prefix']} == recomputed "
              f"{ind[n]['recomputed_prefix']})")
    if not all(v["match"] for v in ind.values()):
        print("HALT: a commitment does not verify against its reveal — protocol breach.")
        return 2

    cdir, adir = build_scratch()
    try:
        p = subprocess.run([sys.executable, GRADER, cdir, adir],
                           capture_output=True, text=True)
    finally:
        shutil.rmtree(cdir); shutil.rmtree(adir)
    # discriminate crash-vs-verdict by JSON presence (C6494 lesson: rc alone is ambiguous)
    try:
        verdict = json.loads(p.stdout)
    except json.JSONDecodeError:
        print("GRADER CRASH (no JSON on stdout) — NOT a verdict. stderr:")
        print(p.stderr.strip()[-800:])
        return 2
    print("\n=== FROZEN GRADER VERDICT (JSON stdout, verbatim; grader rc=%d) ===" % p.returncode)
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
