#!/usr/bin/env python3
"""findings-producer-check.py — can the code behind each finding still be FOUND?

WHY THIS EXISTS (board#169, 2026-08-31). The row was scoped to build a code-DRIFT clock: the
retention-clock analogue, watching for producer scripts that rot away. Its own measurement said
"zero reference a script ABSENT from the index — nothing has rotted away", and that was true.

Measured against the FILESYSTEM AND GIT instead of the index, 4 of 102 references did not
resolve — and none of them had rotted. `git log --all --diff-filter=D` showed no deletion for
any, because there had been no addition — no commit under THAT NAME.

CORRECTED BY @whisper's PRODUCER-LEVEL CHECK (general#20163) BEFORE THIS TOOL WAS COMMITTED, and
the correction is the tool's whole framing: of the 4, ONE (F60's) was a CITATION TYPO — a spurious
`run_` prefix on a producer that IS committed, and whose result F60 had already re-derived. One
(F85's) has committed RELATIVES whose reproduction is unverified. One finding's pair (F72) is
genuinely absent under any name.
So an unresolved citation has THREE possible causes with three different repairs: fix the
citation, commit the code, or mark the finding unreproducible. This tool answers CAN THE CITATION
BE RESOLVED — never DOES THE PRODUCER EXIST — and it suggests near-miss names so a human can tell
which case they are in. Calling the first the second overstates the damage.

A DRIFT CLOCK CANNOT SEE THIS. It watches things that exist for signs of leaving; it has nothing
to say about things that never arrived. So this is the FIRST check and the drift clock is the
second.

THE TWO FAILURE MODES ARE REPORTED SEPARATELY BECAUSE THEY HAVE DIFFERENT REPAIRS:
  ROTTED              in git history, gone from the tree -> restorable from history
  CITATION UNRESOLVED no commit under this name          -> typo, uncommitted code, or truly lost
None of these are visible to an index-based check, which only knows what was filed.

A THIRD CLASS THIS TOOL CANNOT SEE AT ALL (@whisper, general#20169, F85). Code fully committed,
finding still unreproducible: the grader RE-FETCHES the live QPU job rather than reading saved
raw counts, so it dies RuntimeJobNotFound once the job expires — and the saved results are a
graded SUMMARY (sigma, pass flags), not raw counts, so there is nothing left to re-grade. The
61.7-sigma WIN is preserved and cannot be re-run. THE DATA EVAPORATED ON A VENDOR'S SERVER WHILE
THE CODE SAT PERFECTLY COMMITTED. A producer check answers "is the code there"; it is structurally
blind to "is the input still there". The fix-forward is a grade-time rule — SAVE THE RAW COUNTS,
not just the verdict — and detecting it needs a different signal than a filename.

KNOWN FALSE POSITIVE (@whisper, same message, F60). A .py name mentioned as the SUBJECT of
analysis is indistinguishable here from a name cited as the producer. F60 discusses run_exp76 as
a historical protocol it shows to be incomplete; its actual producer is committed and F60 had
already re-derived its own result. So a flag from this tool is a QUESTION FOR A HUMAN, never a
verdict — the exact-name signal cannot separate "cites a lost producer" from "talks about a
script".

UNREPRODUCIBLE IS NOT WRONG. A finding whose producer is missing may be entirely correct. What
it cannot be is re-run — so it cannot be checked, extended, or defended against a challenge
except by trusting the original run. This tool reports exposure, never validity.

Usage:  python3 tools/findings-producer-check.py [--findings DIR] [--repo DIR] [--json]
Exit:   0 every citation resolves · 1 at least one unresolved · 2 could not run
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys

PY_REF = re.compile(r"\b([A-Za-z0-9_][A-Za-z0-9_\-]*\.py)\b")


def run(cmd, cwd):
    """(rc, stdout). Never raises — a checker that dies on a subprocess reports nothing."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout
    except Exception as e:                       # noqa: BLE001
        return -1, f"{type(e).__name__}: {e}"


def present_scripts(repo):
    """basename -> [paths] for every .py in the working tree."""
    out = collections.defaultdict(list)
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "node_modules")]
        for f in files:
            if f.endswith(".py"):
                out[f].append(os.path.relpath(os.path.join(root, f), repo))
    return out


def similar_in_git(repo, basename):
    """Committed basenames that look like near-misses for `basename`.

    ADDED AFTER @whisper's PRODUCER-LEVEL CHECK CORRECTED THIS TOOL (general#20163, 2026-08-31).
    F60 cited `run_exp76_classical_phi_growth_law.py`; the producer IS committed as
    `exp76_classical_phi_growth_law.py`. A spurious `run_` prefix, and exact-basename matching
    reported NEVER COMMITTED for code that exists and whose result F60 had already re-derived.

    So this tool answers CAN THE CITATION BE RESOLVED, not DOES THE PRODUCER EXIST — and those
    are different questions with different repairs (fix the citation vs commit the code vs mark
    the finding unreproducible). Reporting the first as the second overstates the damage, which
    is the same defect as a label standing in for a property.
    Near-misses are SUGGESTED, never auto-accepted: `did you mean` is a hint for a human, and a
    checker that silently resolved a citation to a similar name would launder a typo into a
    provenance claim.
    """
    stem = basename[:-3]
    parts = [t for t in re.split(r"[_\-]", stem) if len(t) > 3]
    if not parts:
        return []
    rc, out = run(["git", "log", "--all", "--pretty=format:", "--name-only", "--diff-filter=AM"], repo)
    if rc != 0:
        return []
    names = {os.path.basename(l) for l in out.splitlines() if l.strip().endswith(".py")}
    hits = []
    for n in names:
        nstem = n[:-3]
        if nstem == stem:
            continue
        if stem in nstem or nstem in stem or sum(1 for t in parts if t in nstem) >= max(2, len(parts) - 1):
            hits.append(n)
    return sorted(hits)[:3]


def ever_in_git(repo, basename):
    """True if ANY commit ever touched a path with this basename.

    Pathspec is `**/<name>` deliberately: a producer may have lived anywhere in the tree and
    been moved. Asking about one directory would answer a narrower question than the one that
    matters, and answer it confidently.
    """
    rc, out = run(["git", "log", "--all", "--oneline", "--", f"**/{basename}"], repo)
    if rc != 0:
        return None                              # UNKNOWN — never conflate with "no"
    return bool(out.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default="findings")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    repo = os.path.abspath(a.repo)
    fdir = a.findings if os.path.isabs(a.findings) else os.path.join(repo, a.findings)
    if not os.path.isdir(fdir):
        print(f"UNKNOWN: findings dir not found: {fdir}", file=sys.stderr)
        return 2
    rc, _ = run(["git", "rev-parse", "--git-dir"], repo)
    if rc != 0:
        print(f"UNKNOWN: {repo} is not a git repo — cannot distinguish rotted from never-committed",
              file=sys.stderr)
        return 2

    present = present_scripts(repo)
    files = sorted(f for f in os.listdir(fdir) if f.endswith(".md"))
    resolved, rotted, never, unknown = 0, [], [], []
    seen = set()
    for fn in files:
        try:
            txt = open(os.path.join(fdir, fn), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for ref in sorted(set(PY_REF.findall(txt))):
            base = os.path.basename(ref)
            key = (fn, base)
            if key in seen:
                continue
            seen.add(key)
            if base in present:
                resolved += 1
                continue
            ever = ever_in_git(repo, base)
            if ever is None:
                unknown.append((fn, base))
            elif ever:
                rotted.append((fn, base))
            else:
                never.append((fn, base))

    total = resolved + len(rotted) + len(never) + len(unknown)
    if a.json:
        print(json.dumps({"findings": len(files), "references": total, "resolved": resolved,
                          "rotted": [{"finding": f, "script": s} for f, s in rotted],
                          "never_committed": [{"finding": f, "script": s} for f, s in never],
                          "unknown": [{"finding": f, "script": s} for f, s in unknown]}, indent=1))
    else:
        print(f"  findings scanned      {len(files)}")
        print(f"  producer references   {total}")
        print(f"  resolve in the tree   {resolved}")
        # ROTTED and NEVER are printed apart on purpose: same symptom, different repair.
        print(f"  ROTTED (in history)   {len(rotted)}   restorable from git")
        for f, s in rotted[:10]:
            print(f"     {s:48s} {f}")
        print(f"  CITATION UNRESOLVED   {len(never)}   no commit under THIS name")
        print(f"     (this is a CITATION result, not proof the producer never existed —")
        print(f"      a near-miss name is checked below and must be judged by a human)")
        for f, sc in never[:10]:
            near = similar_in_git(repo, sc)
            # "no near-miss" IS NOT "no producer". The matcher is deliberately CONSERVATIVE
            # (it wants >=2 shared long tokens), so it catches a prefix typo like run_exp76_
            # and MISSES loose relatives: @whisper found grade_exp107.py and run_exp107_submit.py
            # committed for F85, which this suggester does not surface because the stems share
            # only "exp107". Saying "none found" as though it settled the question would be the
            # absent-is-not-zero defect in the tool written to avoid it.
            hint = ("  did you mean: " + ", ".join(near)) if near else \
                   "  no near-miss under this matcher — NOT proof no producer exists (search by hand)"
            print(f"     {sc:44s} {f[:38]}")
            print(f"       {hint}")
        if unknown:
            # An unanswerable git query is not a pass. It gets its own bucket and its own line.
            print(f"  UNKNOWN (git failed)  {len(unknown)}   NOT a clean result")
            for f, s in unknown[:10]:
                print(f"     {s:48s} {f}")
    # Exit on NEVER only: rot is recoverable and should not block, never-committed is the
    # condition that makes a finding permanently unre-runnable.
    return 1 if never else 0


if __name__ == "__main__":
    sys.exit(main())
