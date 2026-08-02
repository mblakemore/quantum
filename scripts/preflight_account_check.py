#!/usr/bin/env python3
"""
preflight_account_check.py — refuse to fly a script that will pick its IBM account by accident.

WHAT IT CATCHES (defect c4217_018, submission half)
---------------------------------------------------
A bare `QiskitRuntimeService()` takes whatever account happens to be saved. On a READ path that
returns a confident 404 for a healthy job. On a SUBMIT path the job GOES SOMEWHERE — Ember sent a
flight to a depleted default instance and it sat unrunnable; Whisper found an inline loader that
returned `token=None` on a missing env line, inside a flight script that had already flown and
routed correctly only because the env line happened to exist.

WHY A CHECKER AND NOT A MASS EDIT. 116 call sites across 93 files, ~78 of them unowned legacy that
will never run again. Mass-converting frozen archival scripts risks breaking real artifacts to fix
a defect that cannot fire on code nobody executes. The exposure is the subset that DOES run — so
the gate belongs at the moment of flight, not in a sweep.

    python3 scripts/preflight_account_check.py <script.py> [more.py ...]
    python3 scripts/preflight_account_check.py --all          # audit the repo, exit 0 always
    python3 scripts/preflight_account_check.py --selftest

Exit 0 = clear to fly · 1 = bare service on a submission path · 2 = bad usage.

HONEST LIMITS, so nobody reads more into a PASS than it carries:
  * Static, not execution. The bare-construction test is an AST parse (so prose about the defect is
    not counted as the defect), but "does this file SUBMIT?" is still a regex over the text — that
    half can over- and under-fire.
  * A file with both a hardware branch and a simulator branch is flagged; the checker cannot know
    which branch today's flags take. FLAGGED IS NOT PROVEN — read the site.
  * A service built through an indirection this cannot see reads as clean.
  * A PASS means "no bare construction found here", NOT "this script routes correctly".
"""
import os
import re
import sys

BARE = re.compile(r"QiskitRuntimeService\s*\(\s*\)")
SUBMIT = re.compile(r"SamplerV2|EstimatorV2|sampler\.run|estimator\.run|\.run\s*\(\s*pubs")
# A simulator sampler is not a submission — StatevectorSampler.run() goes nowhere near an account.
SIM = re.compile(r"StatevectorSampler|AerSimulator|FakeMarrakesh|FakeBrisbane|BasicSimulator")
SAFE_HELPER = re.compile(r"multi_account_service|service_for_submission|service_for_job")


def _bare_call_lines(src):
    """Lines with a REAL no-argument QiskitRuntimeService() call.

    Parsed with `ast`, not grepped. The regex version flagged this checker's OWN companion module
    at two lines that turned out to be the docstring showing `QiskitRuntimeService() -> ...` as an
    example — the tool reported the documentation of the fix as an instance of the defect.
    A checker that cannot tell code from prose about code will cry wolf, and a gate that cries wolf
    gets ignored on the day it is right.

    Falls back to the regex only when the file does not parse (legacy py2 syntax), and that
    fallback is reported so a noisy result is attributable rather than mysterious.
    """
    import ast
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return [i + 1 for i, ln in enumerate(src.split("\n")) if BARE.search(ln)], True
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or node.args or node.keywords:
            continue
        f = node.func
        name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
        if name == "QiskitRuntimeService":
            hits.append(node.lineno)
    return sorted(set(hits)), False


def scan(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        return {"path": path, "error": str(exc)}
    bare, fell_back = _bare_call_lines(src)
    return {
        "path": path,
        "bare_lines": bare,
        "submits": bool(SUBMIT.search(src)),
        "has_sim": bool(SIM.search(src)),
        "uses_helper": bool(SAFE_HELPER.search(src)),
        "regex_fallback": fell_back,
        "error": None,
    }


def verdict(r):
    """FAIL only for the asymmetric case: a bare construction on a path that can submit.

    A bare construction on a pure read path is a WARN — it produces a wrong answer, not a wrong
    action, and blocking on it would train people to pass --force, which is how a gate stops
    being read at all.
    """
    if r.get("error"):
        return "ERROR", r["error"]
    note = "  [regex fallback: file did not parse]" if r.get("regex_fallback") else ""
    if not r["bare_lines"]:
        return "PASS", "no bare QiskitRuntimeService() construction" + note
    where = ",".join(str(x) for x in r["bare_lines"])
    if r["submits"]:
        hedge = " (file also has a simulator branch — confirm which one this run takes)" if r["has_sim"] else ""
        return "FAIL", f"bare service at line(s) {where} on a SUBMISSION path{hedge}" + note
    return "WARN", f"bare service at line(s) {where} on a read path — wrong answers, not wrong actions" + note


def _selftest():
    import tempfile
    cases = [
        ("bare + submit", "from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2\n"
                          "svc = QiskitRuntimeService()\nSamplerV2(mode=svc.backend('x')).run(pubs)\n", "FAIL"),
        ("bare + read only", "svc = QiskitRuntimeService()\nsvc.job('abc').result()\n", "WARN"),
        ("helper + submit", "from ibm_multi_account import service_for_submission\n"
                            "svc = service_for_submission('IBMQ_ALT2')\nSamplerV2(mode=b).run(pubs)\n", "PASS"),
        ("simulator only", "from qiskit.primitives import StatevectorSampler\n"
                           "StatevectorSampler(seed=7).run(pubs)\n", "PASS"),
        # regression: the FIRST version flagged a docstring that DOCUMENTED the fix as an
        # instance of the defect. Prose about code is not code.
        ("docstring mentions it", 'def f():\n    """use svc = QiskitRuntimeService() -> multi_account_service()"""\n'
                                  '    from ibm_multi_account import service_for_submission\n'
                                  '    SamplerV2(mode=b).run(pubs)\n', "PASS"),
        ("comment mentions it", '# svc = QiskitRuntimeService()  <- do not do this\n'
                                'from ibm_multi_account import service_for_submission\n'
                                'SamplerV2(mode=b).run(pubs)\n', "PASS"),
    ]
    ok = True
    for name, src, want in cases:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write(src)
            p = fh.name
        got, why = verdict(scan(p))
        os.unlink(p)
        mark = "PASS" if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  [{mark}] {name}: expected {want}, got {got}  ({why})")
    # THE GUARD IS THE TEST, NOT THE PROSE: prove the checker CAN fail, not merely that it stays quiet.
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--all" in argv:
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        rows = []
        for dirpath, _, files in os.walk(root):
            if any(s in dirpath for s in (".git", "node_modules", "__pycache__")):
                continue
            for f in files:
                if f.endswith(".py"):
                    rows.append(scan(os.path.join(dirpath, f)))
        tally = {}
        fails = []
        for r in rows:
            v, why = verdict(r)
            tally[v] = tally.get(v, 0) + 1
            if v == "FAIL":
                fails.append((os.path.relpath(r["path"], root), why))
        print(f"scanned {len(rows)} python files: " +
              ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
        print(f"\nFAIL = bare service on a submission path ({len(fails)}):")
        for p, why in sorted(fails)[:80]:
            print(f"  {p}\n      {why}")
        if len(fails) > 80:
            print(f"  ... and {len(fails) - 80} more")
        print("\nNot a mass-edit list. Convert a script WHEN YOU FLY IT — one line.")
        return 0
    targets = [a for a in argv[1:] if not a.startswith("-")]
    if not targets:
        print(__doc__)
        return 2
    worst = 0
    for t in targets:
        v, why = verdict(scan(t))
        print(f"[{v}] {t}: {why}")
        if v == "FAIL":
            worst = 1
    if worst:
        print("\nREFUSE TO FLY. Fix with:  svc = service_for_submission('IBMQ_ALT2')")
        print("A missing credential must be an ERROR, never a silent redirect to a default account.")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
