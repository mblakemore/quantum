#!/usr/bin/env python3
"""findings-raw-counts-check.py — is each HARDWARE finding re-gradeable from RAW COUNTS on disk? (board#377)

THE RULE (split from board#169, the third fragility class): a finding derived from hardware results
is not gradeable unless the RAW COUNTS are stored in the repo at grade time — not a summary, and not
a job id. A job id is a POINTER TO SOMEONE ELSE'S RETENTION POLICY; a summary is a lossy derivative.
Neither survives the vendor expiring the job, and nothing in the record marks the transition: the
finding reads exactly the same the day after the evidence evaporates as the day before.

WHY THE TWO EXISTING CHECKS CANNOT SEE IT. findings-producer-check.py asks whether the cited
producer can still be FOUND; grader-raw-counts-check.py asks whether the grader CODE persists
counts. F85 passes both — its grader is committed and findable — and its stored result is
`results/exp107_hw_results.json`: a job_id string and a page of floats. Both checks look at the
CODE; the defect is in the DATA. This one looks at the data.

WHAT IT DOES. For every finding document it locates the evidence files — paths cited in the body,
the ledger's retest_ref, and every results/ file named after the finding's experiment stem — and
classifies each as RAW (a counts dict keyed by bitstrings with integer values), POINTER (job ids,
no counts), SUMMARY (numbers, no counts), or MISSING. The finding's disposition follows:
RAW_COUNTS if any file is RAW; otherwise POINTER_ONLY / SUMMARY_ONLY / FILES_MISSING / NO_FILES.
The partition is printed in full and sums to the population, so no reason hides in a gap.

THE CONTROLS ARE COMPILED IN AND RUN EVERY TIME. If the known summary-only case (F85) ever
classifies as RAW, or the known raw case ever fails to, the matcher has drifted and the checker
REFUSES TO REPORT (exit 2) rather than print a clean board. A rule that cannot fail the case that
motivated it is not a rule.

Usage:  python3 tools/findings-raw-counts-check.py [--json] [--finding ID] [--repo DIR]
Exit:   0 every hardware finding is RAW_COUNTS · 1 at least one is not · 2 could not run / control failed
"""
import argparse
import glob
import json
import os
import re
import sys

BITS = re.compile(r"[01 ]+")
STEM = re.compile(r"\b(exp\d+[a-z]?)\b", re.I)
EXPERIMENT_LINE = re.compile(r"\*\*Experiment\*\*:\s*(Exp\d+[a-z]?)", re.I)
CITED = re.compile(r"results/[A-Za-z0-9_./-]+\.json")
HARDWARE = re.compile(r"ibm_[a-z]+|marrakesh|torino|brisbane|fez|kyiv|braket|ionq|rigetti|aria|harmony|garnet|"
                      r"hardware run|on hardware|real hardware|QPU", re.I)
JOB_KEY = re.compile(r"job_?ids?$", re.I)

KNOWN_SUMMARY = "F85"                              # exp107: job_id + floats, the case this rule exists for
KNOWN_RAW = "finding-exp183-secret-sharing"        # exp183b/c results carry bitstring counts

DISPOSITIONS = ["RAW_COUNTS", "POINTER_ONLY", "SUMMARY_ONLY", "FILES_MISSING", "NO_FILES"]


def _walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def _is_counts_dict(c):
    if not isinstance(c, dict) or not c:
        return False
    keys = list(c)
    bit_keys = sum(bool(BITS.fullmatch(str(k))) for k in keys)
    if bit_keys >= max(1, len(keys) // 2) and any(isinstance(c[k], int) for k in keys if BITS.fullmatch(str(k))):
        return True
    first = c[keys[0]]
    return isinstance(first, dict) and bool(first) and all(BITS.fullmatch(str(k2)) for k2 in list(first)[:5]) \
        and any(isinstance(v, int) for v in first.values())


def classify_file(path):
    """RAW | POINTER | SUMMARY | MISSING | UNREADABLE"""
    if not os.path.exists(path):
        return "MISSING"
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:  # noqa: BLE001 — a file that will not parse is not evidence either way
        return "UNREADABLE"
    has_job = False
    for k, v in _walk(d):
        if k == "counts" and _is_counts_dict(v):
            return "RAW"
        if _is_counts_dict(v) and BITS.fullmatch(str(next(iter(v)))):
            return "RAW"
        if isinstance(k, str) and JOB_KEY.search(k):
            has_job = True
    return "POINTER" if has_job else "SUMMARY"


def load_ledger(repo):
    try:
        with open(os.path.join(repo, "findings", "status-ledger.json"), encoding="utf-8") as fh:
            rows = json.load(fh)["rows"]
    except Exception:  # noqa: BLE001
        return {}
    by_file = {}
    for r in rows:
        if r.get("file"):
            by_file[r["file"]] = r
    return by_file


def stem_of(body, fname):
    m = EXPERIMENT_LINE.search(body) or STEM.search(body) or STEM.search(fname)
    return m.group(1).lower() if m else None


def evidence_files(repo, body, stem, ledger_row):
    files = set(CITED.findall(body))
    if ledger_row and ledger_row.get("retest_ref"):
        files.add(ledger_row["retest_ref"])
    if stem:
        pat = re.compile(rf"^{re.escape(stem)}[a-z]?(?:[_\-.]|$)", re.I)
        for f in glob.glob(os.path.join(repo, "results", "*.json")):
            if pat.match(os.path.basename(f)):
                files.add(os.path.relpath(f, repo))
    return sorted(files)


def assess(repo, fname, ledger):
    path = os.path.join(repo, "findings", fname)
    with open(path, encoding="utf-8", errors="ignore") as fh:
        body = fh.read()
    row = ledger.get(fname)
    stem = stem_of(body, fname)
    if row is not None and "sim_only" in row:
        hardware = not row["sim_only"]
        basis = "ledger"
    else:
        hardware = bool(HARDWARE.search(body))
        basis = "body"
    files = evidence_files(repo, body, stem, row)
    kinds = {f: classify_file(os.path.join(repo, f)) for f in files}
    present = [k for k in kinds.values() if k not in ("MISSING", "UNREADABLE")]
    if not files:
        disp = "NO_FILES"
    elif "RAW" in kinds.values():
        disp = "RAW_COUNTS"
    elif not present:
        disp = "FILES_MISSING"
    elif "POINTER" in present and "SUMMARY" not in present:
        disp = "POINTER_ONLY"
    else:
        disp = "SUMMARY_ONLY"
    fid = fname.split("-")[0] if fname[0] == "F" and fname[1].isdigit() else fname[:-3]
    return {"id": fid, "file": fname, "stem": stem, "hardware": hardware, "hardware_basis": basis,
            "disposition": disp, "files": kinds}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--finding", help="report one finding id or file stem")
    a = ap.parse_args()
    fdir = os.path.join(a.repo, "findings")
    names = sorted(f for f in os.listdir(fdir) if f.endswith(".md") and (re.match(r"F\d+-", f) or f.startswith("finding-")))
    if not names:
        print("could not run: no finding documents under", fdir)
        return 2
    ledger = load_ledger(a.repo)
    results = [assess(a.repo, f, ledger) for f in names]

    # controls first — the report is not trusted until both hold
    by_id = {r["id"]: r for r in results}
    ks, kr = by_id.get(KNOWN_SUMMARY), by_id.get(KNOWN_RAW)
    if ks is None or kr is None:
        print(f"REFUSING TO REPORT: control finding missing ({KNOWN_SUMMARY}: {ks is not None}, {KNOWN_RAW}: {kr is not None})")
        return 2
    if ks["disposition"] not in ("SUMMARY_ONLY", "POINTER_ONLY"):
        print(f"REFUSING TO REPORT: known summary-only {KNOWN_SUMMARY} classified {ks['disposition']} — the matcher has drifted")
        return 2
    if kr["disposition"] != "RAW_COUNTS":
        print(f"REFUSING TO REPORT: known raw {KNOWN_RAW} classified {kr['disposition']} — the matcher has drifted")
        return 2

    if a.finding:
        sel = [r for r in results if r["id"] == a.finding or r["file"].startswith(a.finding)]
        print(json.dumps(sel, indent=1))
        return 0 if sel and all(r["disposition"] == "RAW_COUNTS" for r in sel) else 1

    hw = [r for r in results if r["hardware"]]
    part = {d: sum(1 for r in hw if r["disposition"] == d) for d in DISPOSITIONS}
    non_hw = len(results) - len(hw)
    body_basis = sum(1 for r in hw if r["hardware_basis"] == "body")
    if a.json:
        print(json.dumps({"population": len(results), "hardware": len(hw), "non_hardware_or_unknown": non_hw,
                          "partition": part, "hardware_basis_body": body_basis, "findings": results}, indent=1))
    else:
        print(f"findings-raw-counts-check — {len(results)} finding documents, {len(hw)} hardware "
              f"({body_basis} classified hardware from the body, not the ledger), {non_hw} sim-only or unknown")
        for d in DISPOSITIONS:
            print(f"  {d:<14} {part[d]:4d}")
        assert sum(part.values()) == len(hw), "partition does not sum to the hardware population"
        bad = [r for r in hw if r["disposition"] != "RAW_COUNTS"]
        for r in bad[:12]:
            fl = ", ".join(f"{os.path.basename(f)}={k}" for f, k in list(r["files"].items())[:3]) or "-"
            print(f"    {r['id']:<8} {r['disposition']:<14} {r['stem'] or '?':<8} {fl}")
        if len(bad) > 12:
            print(f"    ... and {len(bad) - 12} more")
        print(f"  controls: {KNOWN_SUMMARY}={ks['disposition']} (must not be RAW) · {KNOWN_RAW}={kr['disposition']} (must be RAW) — both held")
        print(f"  CHECK COMPLETE — {len(bad)} of {len(hw)} hardware findings cannot be re-graded from raw counts on disk")
    return 0 if part["RAW_COUNTS"] == len(hw) else 1


if __name__ == "__main__":
    sys.exit(main())
