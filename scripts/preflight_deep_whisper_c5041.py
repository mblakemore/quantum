#!/usr/bin/env python3
"""PREFLIGHT, ONE IMPORT DEEPER — the gate that exp142c defeated by indirection.

WHY. C5041: six exp142 jobs went into the accepts-and-never-runs account and were cancelled.
The MANDATORY gate (scripts/preflight_account_check.py) had been available the whole time and
would have said PASS: exp142c's OWN text is clean, and the bare service lives in the helper it
imports (scripts/run_exp66_qpu_partb.py, which the same gate FAILS when pointed at directly).

  preflight_account_check.py exp142c_flight_ember_c4215.py   -> [PASS]
  preflight_account_check.py run_exp66_qpu_partb.py          -> [FAIL] REFUSE TO FLY

Elder's rule from the same event: "a guard that protects one code path is not a guard, it is a
local habit." This walks the LOCAL import graph and reports the union.

It does NOT replace the mandatory gate — it wraps it. Same verdict logic, wider scope, so a
PASS here implies a PASS there and nothing that failed before can now pass.

Usage:  python3 scripts/preflight_deep_whisper_c5041.py <script.py>
Exit 0 = every reachable local module clean.  Exit 1 = REFUSE TO FLY.

Substrate: claude-opus-5, Whisper C5041.
"""
import ast, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(REPO, "scripts", "preflight_account_check.py")


def local_imports(path, seen):
    """Modules imported by `path` that resolve to files inside the repo."""
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception:
        return []
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    out = []
    for nm in names:
        leaf = nm.split(".")[-1] + ".py"
        for root, _, files in os.walk(REPO):
            if ".git" in root:
                continue
            if leaf in files:
                p = os.path.join(root, leaf)
                if p not in seen:
                    out.append(p)
                break
    return out


def walk(path):
    seen, order, stack = set(), [], [os.path.abspath(path)]
    while stack:
        p = stack.pop()
        if p in seen or not os.path.exists(p):
            continue
        seen.add(p); order.append(p)
        stack += local_imports(p, seen)
    return order


def main(target):
    mods = walk(target)
    print(f"  DEEP PREFLIGHT — {len(mods)} local module(s) reachable from {os.path.basename(target)}\n")
    bad = []
    for m in mods:
        r = subprocess.run([sys.executable, GATE, m], capture_output=True, text=True)
        line = (r.stdout or r.stderr).strip().splitlines()
        verdict = next((l for l in line if l.startswith("[")), "(no verdict)")
        rel = os.path.relpath(m, REPO)
        # C5048 fix (first real use): the underlying gate's [WARN] means implicit
        # resolution on a READ path — "wrong answers, not wrong actions". Blocking on
        # WARN made this tool refuse every script that imports the mandated guard
        # module itself (ibm_multi_account.py). Block on [FAIL] only; surface WARNs.
        if verdict.startswith("[PASS]"):
            print(f"     {rel}")
        elif verdict.startswith("[WARN]"):
            print(f"  ⚠  {rel}")
            print(f"       {verdict}")
        else:
            print(f"  ❌ {rel}")
            print(f"       {verdict}")
            bad.append(rel)
    if bad:
        print(f"\n  ❌ REFUSE TO FLY — {len(bad)} reachable module(s) resolve an account implicitly:")
        for b in bad:
            print(f"       {b}")
        print("\n  The entry script may itself be clean. THAT IS THE DEFECT THIS TOOL EXISTS FOR:")
        print("  a bare service one import deep still submits, and it submits by DEFAULT ORDER.")
        return 1
    print(f"\n  ✅ CLEAN across the whole reachable graph.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[-3]); sys.exit(2)
    sys.exit(main(sys.argv[1]))
