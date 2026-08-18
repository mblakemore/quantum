#!/usr/bin/env python3
"""tools/window_rescue.py — bank the calibration window of every σ-headline flight, while it is
still cheap. (Whisper C5075)

WHY, and it is one specific near-miss rather than a general worry. F106 was declared past IBM
retention with its epoch-dependence "permanently unknown", and that belief was already load-bearing:
it was the justifying case for a schema field another seat had a GO to build. Checked before signing
off — **the job was retrievable at 36 days**, properties returned at creation date, and the window
contained the number that actually mattered (the flight used qubits [0,1,2,3] at readout 0.0042
median, against a device median of 0.01166 and a device MEAN of 0.02683 that one 0.494 qubit
dominates). A σ re-grade computed off the device aggregate would overstate that flight's noise
several-fold.

THE ASYMMETRY THAT MAKES THIS URGENT AND NOT MERELY TIDY:

    An epoch LABEL can be added any time. An epoch WINDOW cannot.

`epoch_label_check` reports 46 σ-headline findings with no epoch label; 44 of them carry job IDs.
Labelling is reversible work available forever. The calibration behind those jobs sits on a vendor
retention clock nobody here controls and nobody has measured — we have only a BOUND (successful
retrieval at 16d and 36d, zero observed losses at any age). So the correct order of work is: bank
the windows first, label at leisure. A witness that only tells you the window is gone is an obituary.

WHAT IT BANKS, per job: retrievability, backend, creation date, properties timestamp, device-wide
readout median/mean/max, and — where the layout is recoverable from the job inputs — THE PER-QUBIT
READOUT OF THE QUBITS ACTUALLY USED. That last field is the one F106 proved is load-bearing: any
campaign using noise-aware placement flies on the good tail by construction, so device aggregates
systematically understate its results, and the error always points the same way.

$0. Metadata reads only — no submission path, no QPU seconds.

    python3 tools/window_rescue.py [--limit N] [--out results/window_rescue_c5075.json]
"""
import glob
import json
import os
import re
import statistics as st
import sys
import time

sys.path.insert(0, "/droid/repos/quantum/scripts")
Q = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB_RE = re.compile(r"\b(d[0-9a-z]{18,21})\b")


def targets():
    """Every job id mentioned by a finding, with the finding that cites it."""
    seen = {}
    for p in sorted(glob.glob(f"{Q}/findings/*.md")):
        try:
            txt = open(p, errors="replace").read()
        except OSError:
            continue
        for jid in JOB_RE.findall(txt):
            seen.setdefault(jid, os.path.basename(p))
    return seen


def rescue_one(svc, acct, jid):
    rec = {"account": acct}
    j = svc.job(jid)
    bk = j.backend()
    rec["backend"] = bk.name
    rec["created"] = str(getattr(j, "creation_date", None))
    rec["status"] = str(j.status())
    props = None
    try:
        props = bk.properties(datetime=getattr(j, "creation_date", None))
        rec["properties_source"] = "AT CREATION DATE"
    except Exception as e:
        rec["properties_at_creation_error"] = f"{type(e).__name__}: {str(e)[:60]}"
    if props is None:
        try:
            props = bk.properties()
            rec["properties_source"] = "CURRENT (historical unavailable)"
        except Exception:
            pass
    if props is None:
        rec["window"] = "NO PROPERTIES"
        return rec
    rec["properties_last_update"] = str(getattr(props, "last_update_date", None))
    ro = []
    for q in range(getattr(bk, "num_qubits", 0) or 0):
        try:
            ro.append(props.readout_error(q))
        except Exception:
            pass
    if ro:
        rec["device_readout"] = {"median": st.median(ro), "mean": st.mean(ro), "max": max(ro)}
    # THE FIELD F106 PROVED LOAD-BEARING: the qubits the job actually ran on.
    used = set()
    try:
        for pub in (j.inputs.get("pubs") or []):
            qc = pub[0] if isinstance(pub, (list, tuple)) else pub
            lay = getattr(getattr(qc, "layout", None), "final_index_layout", None)
            if callable(lay):
                used.update(lay())
    except Exception:
        pass
    if used:
        vals = []
        for q in sorted(used):
            try:
                vals.append(props.readout_error(q))
            except Exception:
                pass
        if vals:
            # FIELD NAMING FIXED C5075. This set is every qubit the transpiler TOUCHED
            # (final_index_layout) — routing and idling qubits included, most of which carry no
            # classical bit. I originally called it `used_qubits`, and that ambiguity propagated:
            # another seat built a picker-width law on it, where wide circuits' medians are diluted
            # by routing qubits the picker never optimised. Same set-selection error I made three
            # times on my own analyses in one night. `touched_*` says what it is; the MEASURED set
            # is a different object and must be recovered from the measure instructions.
            rec["touched_qubits"] = sorted(used)
            rec["touched_readout"] = {"median": st.median(vals), "max": max(vals)}
            rec["used_qubits"] = sorted(used)        # deprecated alias, kept so the banked census reads
            rec["used_readout"] = {"median": st.median(vals), "max": max(vals)}
            rec["SET_WARNING"] = ("touched != measured; for any statistic combining specific bits, "
                                  "recover the measured set from the circuit's measure instructions")
            if rec.get("device_readout"):
                rec["quietness_vs_device_median"] = (
                    rec["device_readout"]["median"] / st.median(vals) if st.median(vals) else None)
    return rec


def load_banked(path):
    """Already-banked jobs, so a re-run costs only what is NEW.

    INCREMENTAL BY DEFAULT, added C5075 after close. The queued fix for this tool was "add a rate
    limiter", and that treats the symptom: the sweep re-fetched all 173 cited jobs on every run,
    including the 58 that are permanently gone and the 115 whose windows are already on disk and
    CANNOT CHANGE — a calibration snapshot at a past creation date is immutable. So the load was
    not a pacing problem, it was work that never needed doing twice.

    Two consequences beyond politeness to the vendor. A cheap re-run is a re-run that actually
    happens, which matters because new findings keep adding job IDs and the retention clock keeps
    running on them. And the 58 lost jobs stop being re-probed forever, which is the difference
    between a sweep that gets slower every month and one whose cost tracks only new work.

    A LOST job is re-probed exactly once more when --retry-lost is passed, because "lost" is a
    claim about a vendor's retention and I have measured the wall but not proven it irreversible.
    Default is not to: 58 known-failing calls per run is the exact waste this change removes.
    """
    try:
        with open(path) as fh:
            prev = json.load(fh)
    except (OSError, ValueError):
        return {}, {}
    jobs = prev.get("jobs", {})
    banked = {k: v for k, v in jobs.items() if v.get("retrievable") is not False}
    lost = {k: v for k, v in jobs.items() if v.get("retrievable") is False}
    return banked, lost


def main():
    from ibm_multi_account import service_for_job
    tg = targets()
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    out_path = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
                else f"{Q}/results/window_rescue_c5075.json")
    full = "--full" in sys.argv
    retry_lost = "--retry-lost" in sys.argv
    banked, lost = ({}, {}) if full else load_banked(out_path)

    all_items = list(tg.items())
    skip = set(banked) | (set() if retry_lost else set(lost))
    items = [(j, s) for j, s in all_items if j not in skip]
    # STATE WHAT WAS SKIPPED AND WHY. A sweep that silently processes 4 of 173 jobs and reports
    # success looks identical to one that swept everything, and "115 windows banked" would then be
    # a claim about a file rather than about this run.
    print(f"@@ cited={len(all_items)} banked={len(banked)} lost={len(lost)}"
          f"{'' if retry_lost else ' (skipped; --retry-lost to re-probe)'} -> fetching {len(items)}",
          flush=True)
    if not items:
        print("@@ nothing new to fetch. windows already banked are immutable; re-run adds nothing.",
              flush=True)
    items = items[:limit] if limit else items
    out = {"card": "window_rescue", "cycle": "C5075",
           "why": "bank epoch windows before a vendor retention clock we have not measured can close them",
           "n_cited": len(all_items), "n_fetched_this_run": len(items), "jobs": {}}
    # Carry prior records forward FIRST, so an incremental run never shrinks the census. Writing
    # only this run's results would silently discard 115 banked windows the moment someone ran the
    # tool with nothing new to fetch - a data-loss bug wearing the shape of an optimisation.
    out["jobs"].update(banked)
    if not retry_lost:
        out["jobs"].update(lost)
    lost = kept = 0
    for i, (jid, src) in enumerate(items, 1):
        if i > 1:
            time.sleep(0.4)   # modest pacing on what remains; the real fix was not fetching it twice
        try:
            svc, acct = service_for_job(jid)
            rec = rescue_one(svc, acct, jid)
            rec["cited_by"] = src
            kept += 1
            uq = rec.get("used_readout", {}).get("median")
            print(f"@@ [{i}/{len(items)}] {jid[:14]} OK {rec.get('backend','?'):16s} "
                  f"dev_med={rec.get('device_readout',{}).get('median')} used_med={uq}", flush=True)
        except Exception as e:
            rec = {"cited_by": src, "retrievable": False,
                   "error": f"{type(e).__name__}: {str(e)[:80]}"}
            lost += 1
            print(f"@@ [{i}/{len(items)}] {jid[:14]} LOST {rec['error'][:60]}", flush=True)
        out["jobs"][jid] = rec
    out["retrievable"] = kept
    out["not_retrievable"] = lost
    json.dump(out, open(out_path, "w"), indent=1)
    # SAY WHICH NUMBER IS WHICH. This line used to read "DONE retrievable=K lost=L", which was a
    # count of THIS RUN while looking exactly like a count of the census - and after the change to
    # incremental fetching an ordinary run prints retrievable=1, which would read as a catastrophic
    # loss of 114 banked windows to anyone scanning the log. Same defect class as the summary line
    # elsewhere today that said "all gates reproduced" one line under a gate that had not.
    n_ok = sum(1 for v in out["jobs"].values() if v.get("retrievable") is not False)
    n_lost = sum(1 for v in out["jobs"].values() if v.get("retrievable") is False)
    print(f"@@ THIS RUN: fetched={len(items)} ok={kept} failed={lost}", flush=True)
    print(f"@@ CENSUS:   {len(out['jobs'])} jobs, {n_ok} with windows, {n_lost} lost -> {out_path}",
          flush=True)


if __name__ == "__main__":
    main()
