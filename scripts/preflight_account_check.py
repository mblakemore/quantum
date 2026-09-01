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

WHY A CHECKER AND NOT A MASS EDIT. 247 submission-path FAILs across 602 files in this repo
(218 unowned legacy, 28 Ember, 1 Whisper, 0 Elder), most written when there was ONE account — so
at the time defaulting was CORRECT and not a defect. They are not 247 live hazards; they are 247
files that would misroute IF RE-RUN, and several are explicitly re-runnable (_refly_/_topup_/_submit_). Mass-converting frozen archival scripts risks breaking real artifacts to fix
a defect that cannot fire on code nobody executes. The exposure is the subset that DOES run — so
the gate belongs at the moment of flight, not in a sweep.

    python3 scripts/preflight_account_check.py <script.py> [more.py ...]
    python3 scripts/preflight_account_check.py --all          # audit the repo, exit 0 always
    python3 scripts/preflight_account_check.py --selftest

Exit 0 = clear to fly · 1 = IMPLICIT account resolution on a submission path · 2 = bad usage.

HONEST LIMITS, so nobody reads more into a PASS than it carries:
  * Static, not execution. The bare-construction test is an AST parse (so prose about the defect is
    not counted as the defect), but "does this file SUBMIT?" is still a regex over the text — that
    half can over- and under-fire.
  * A file with both a hardware branch and a simulator branch is flagged; the checker cannot know
    which branch today's flags take. FLAGGED IS NOT PROVEN — read the site.
  * A service built through an indirection this cannot see reads as clean.
  * A PASS means "no implicit account resolution found here", NOT "this script routes
    correctly". v2 of this checker matched ONE shape and returned PASS on 28 genuinely
    exposed files; if you find a shape it misses, ADD IT TO DEFAULTING_HELPERS rather
    than trusting the PASS.
"""
import os
import re
import sys

BARE = re.compile(r"QiskitRuntimeService\s*\(\s*\)")
SUBMIT = re.compile(r"SamplerV2|EstimatorV2|sampler\.run|estimator\.run|\.run\s*\(\s*pubs")
# A simulator sampler is not a submission — StatevectorSampler.run() goes nowhere near an account.
SIM = re.compile(r"StatevectorSampler|AerSimulator|FakeMarrakesh|FakeBrisbane|BasicSimulator")
SAFE_HELPER = re.compile(r"multi_account_service|service_for_submission|service_for_job")
QSNAP = re.compile(r"pending_jobs|submit_snapshot")


# Helpers that resolve an account IMPLICITLY. `_get_ibm_service()` walks a fallback chain and
# leaves `instance` at None, so calling it is exactly as account-ambiguous as a bare constructor —
# it just does not look like one.
#
# C6578, SECOND DEFECT IN THIS CHECKER, found by Ember trying to adopt it: v2 detected ONLY bare
# `QiskitRuntimeService()`. Ember's 28 exposed files call `_get_ibm_service()` instead, so the gate
# returned **PASS, exit 0, clear to fly** on the very files it was being adopted to guard.
# A gate that green-lights the hazard is worse than no gate — no gate leaves you cautious, a
# false PASS makes you confident. Same root shape as the defect it hunts: I matched the ONE form I
# had in front of me instead of enumerating the forms that exist.
DEFAULTING_HELPERS = {"_get_ibm_service"}


def _bare_call_lines(src):
    """(lines, used_regex_fallback) for every call that picks an IBM account IMPLICITLY.

    Three shapes count, not one:
      * `QiskitRuntimeService()`                    — bare
      * `QiskitRuntimeService(channel=...)`         — no token AND no instance = still the saved account
      * `_get_ibm_service(...)`                     — resolves via a fallback chain, instance=None

    Parsed with `ast`, not grepped: the regex version flagged this checker's own companion module
    at two lines that were the docstring DEMONSTRATING the fix — it reported documentation of the
    remedy as an instance of the disease. A checker that cannot tell code from prose about code
    cries wolf, and a gate that cries wolf goes unread on the day it is right.

    Regex fallback only when the file does not parse (legacy py2), and the fallback is reported so
    noise stays attributable.
    """
    import ast
    try:
        tree = ast.parse(src)
    except SyntaxError:
        lines = [i + 1 for i, ln in enumerate(src.split("\n"))
                 if BARE.search(ln) or any(h + "(" in ln for h in DEFAULTING_HELPERS)]
        return lines, True
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
        if name in DEFAULTING_HELPERS:
            hits.append(node.lineno)
        elif name == "QiskitRuntimeService":
            kw = {k.arg for k in node.keywords if k.arg}
            # An explicit token or instance means the author NAMED the account. That is the fix.
            if not (kw & {"token", "instance"}):
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
        "queue_snapshot": bool(QSNAP.search(src)),
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
        if r["submits"] and not r.get("queue_snapshot"):
            note += ("  [note: submission path with NO queue snapshot — call "
                     "ibm_multi_account.submit_snapshot(backend) into the manifest "
                     "(C5075 provenance gap: pending-at-submit unrecoverable)]")
        return "PASS", "no implicit account resolution" + note
    where = ",".join(str(x) for x in r["bare_lines"])
    if r["submits"]:
        hedge = " (file also has a simulator branch — confirm which one this run takes)" if r["has_sim"] else ""
        return "FAIL", f"IMPLICIT account resolution at line(s) {where} on a SUBMISSION path{hedge}" + note
    return "WARN", f"implicit account resolution at line(s) {where} on a read path — wrong answers, not wrong actions" + note


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
        # regression: v2 PASSED this shape. Ember's 28 exposed files look exactly like it, so the
        # gate said "clear to fly" on the files it was being adopted to guard.
        ("helper-resolved submit", "from run_exp66_qpu_partb import _get_ibm_service\n"
                                   "svc = _get_ibm_service()\n"
                                   "SamplerV2(mode=svc.backend('x')).run(pubs)\n", "FAIL"),
        # channel-only construction is still the SAVED account — no token, no instance named.
        ("channel-only submit", "svc = QiskitRuntimeService(channel='ibm_quantum_platform')\n"
                                "SamplerV2(mode=svc.backend('x')).run(pubs)\n", "FAIL"),
        # naming the account explicitly IS the fix and must not be flagged.
        ("explicit token submit", "svc = QiskitRuntimeService(channel='c', token=T, instance=CRN)\n"
                                  "SamplerV2(mode=svc.backend('x')).run(pubs)\n", "PASS"),
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
    had_fail = had_error = False
    for t in targets:
        v, why = verdict(scan(t))
        print(f"[{v}] {t}: {why}")
        if v == "FAIL":
            had_fail = True
            worst = max(worst, 1)
        elif v == "ERROR":
            # UNKNOWN, not clean. The check COULD NOT ANALYZE this target (unreadable/missing/
            # typo'd path). An ERROR that exits 0 is the exact silent redirect this gate exists to
            # refuse — the check never saw the real script, yet a caller reading the exit code flies.
            # Found by forced-failure sweep (task#355, Whisper C5095): ERROR returned exit 0. The
            # selftest tests verdict() (which returns "ERROR" correctly), not main()'s exit mapping —
            # the exit contract is a different frame than the cases (Elder, general#20282). ERROR
            # must fail closed; exit 2 distinguishes "could not analyze" from a FAIL violation (1).
            had_error = True
            worst = max(worst, 2)
    if had_fail:
        print("\nREFUSE TO FLY. Fix with:  svc = service_for_submission('IBMQ_ALT2')")
        print("A missing credential must be an ERROR, never a silent redirect to a default account.")
    if had_error:
        print("\nREFUSE TO FLY: a target COULD NOT BE ANALYZED (UNKNOWN, not a PASS). Check the "
              "path — an unreadable target must never read as clear-to-fly.")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
