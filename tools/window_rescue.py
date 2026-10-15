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


def extract_sets(pubs):
    """board#174: the two extraction paths, as a PURE function of the job's input pubs so it can be tested
    without a provider. Returns (used, measured).

    The provider's job.inputs["pubs"] holds the circuits that were SUBMITTED, so a locally transpiled
    circuit is the same object this function reads in production (measured 2026-10-15 on three reachable
    jobs: every input pub carried layout.final_index_layout and measure instructions).

    PATH 1 -- final_index_layout: the TOUCHED set (routing + idling included).
    PATH 2 -- MEASURE INSTRUCTIONS: the MEASURED set, the qubits carrying classical bits. Spec READ from the
    artifacts by Whisper (general#17332): "layout if present, ELSE measure instructions across ALL pubs".
    A circuit shape that cannot be walked is UNKNOWN, never "no measures".
    """
    used, measured = set(), set()
    try:
        for pub in pubs:
            qc = pub[0] if isinstance(pub, (list, tuple)) else pub
            lay = getattr(getattr(qc, "layout", None), "final_index_layout", None)
            if callable(lay):
                used.update(lay())
            try:
                for inst in (getattr(qc, "data", None) or []):
                    op = getattr(inst, "operation", None) or getattr(inst, "op", None)
                    if getattr(op, "name", None) != "measure":
                        continue
                    for q in (getattr(inst, "qubits", None) or []):
                        if hasattr(qc, "find_bit"):
                            measured.add(qc.find_bit(q).index)
            except Exception:
                pass    # a circuit shape we cannot walk is UNKNOWN, never "no measures"
    except Exception:
        pass
    return used, measured


def recoverability(used, measured):
    """A vs B (board#174): only BOTH-empty is unrecoverable. One path returning nothing is a fact about
    the path, not about the data."""
    if not used and not measured:
        return "UNEVALUABLE — both paths empty across all pubs"
    if not used:
        return "RECOVERED via measure instructions (layout absent)"
    return "layout present"


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
    try:                                   # as before the refactor: an unreadable inputs object is an
        pubs = j.inputs.get("pubs") or []  # empty window, never a crash of the whole rescue
    except Exception:
        pubs = []
    used, measured = extract_sets(pubs)
    rec["measured_qubits"] = sorted(measured)
    rec["window_recoverability"] = recoverability(used, measured)
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
            rec["SET_WARNING"] = ("touched != measured; touched_readout OVERCOUNTS (routing+idling). "
                                  "Use measured_readout for any per-bit statistic — now COMPUTED (path-2), "
                                  "no longer merely recommended")
            if rec.get("device_readout"):
                rec["quietness_vs_device_median"] = (
                    rec["device_readout"]["median"] / st.median(vals) if st.median(vals) else None)
    # PATH-2 READOUT (board#174 completion, C5086): the MEASURED set is the correct denominator for
    # any per-bit statistic; touched_readout above overcounts with routing/idling qubits. This runs
    # independent of `used`, so a layout-absent-but-measure-RECOVERED window still gets readout stats
    # — closing the gap where the measured set was computed but never used for the numbers.
    if measured:
        mvals = []
        for q in sorted(measured):
            try:
                mvals.append(props.readout_error(q))
            except Exception:
                pass
        if mvals:
            rec["measured_readout"] = {"median": st.median(mvals), "max": max(mvals)}
            if rec.get("device_readout"):
                rec["quietness_vs_device_median_MEASURED"] = (
                    rec["device_readout"]["median"] / st.median(mvals) if st.median(mvals) else None)
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


def selftest():
    """board#174 fixture: the A/B gate on LOCALLY TRANSPILED circuits. job.inputs["pubs"] holds the submitted
    circuits, so these are the same objects extract_sets reads in production; no provider call, no QPU time."""
    from qiskit import QuantumCircuit, transpile
    from qiskit.providers.fake_provider import GenericBackendV2
    be = GenericBackendV2(num_qubits=8, seed=1)
    def bell(meas=True):
        qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
        if meas: qc.measure([0, 1], [0, 1])
        return qc
    cases, ok = [], 0
    # A, routed: the layout path decides; the measured set is the two physical qubits chosen.
    routed = transpile(bell(), be, initial_layout=[5, 7], optimization_level=0, seed_transpiler=1)
    u, m = extract_sets([routed]); v = recoverability(u, m)
    cases.append(("A routed: layout present, measured = {5,7}", v == "layout present" and m == {5, 7} and {5, 7} <= u))
    # A, identity over the FULL WIDTH (the kingston shape: a circuit submitted already full-width, so path 1
    # returns the whole chip and only path 2 names the qubits that matter). final_index_layout lists the
    # circuit's own virtual qubits, so the fixture must be full-width; a 2-qubit circuit would return 2.
    full = QuantumCircuit(8, 2); full.h(0); full.cx(0, 1); full.measure([0, 1], [0, 1])
    ident = transpile(full, be, initial_layout=list(range(8)), optimization_level=0, seed_transpiler=1)
    u, m = extract_sets([(ident, None)])           # pub given as a (circuit, params) tuple
    v = recoverability(u, m)
    cases.append(("A identity full-width: layout covers all 8, measured = {0,1}", v == "layout present" and u == set(range(8)) and m == {0, 1}))
    # B: no layout (untranspiled), measures present -> recovered by path 2, NOT unevaluable.
    u, m = extract_sets([bell()]); v = recoverability(u, m)
    cases.append(("B no layout + measures: RECOVERED via measure instructions", u == set() and m == {0, 1} and v.startswith("RECOVERED")))
    # Both empty across ALL pubs -> the only UNEVALUABLE case. Two pubs, so "all" is exercised.
    u, m = extract_sets([bell(meas=False), (bell(meas=False), None)]); v = recoverability(u, m)
    cases.append(("neither path, two pubs: UNEVALUABLE", v.startswith("UNEVALUABLE")))
    # Mixed: one pub with only measures + one empty pub -> recovered (a single empty pub never decides).
    u, m = extract_sets([bell(meas=False), bell()]); v = recoverability(u, m)
    cases.append(("mixed pubs, measures in one: RECOVERED", v.startswith("RECOVERED") and m == {0, 1}))
    for name, cond in cases:
        print(("PASS " if cond else "FAIL ") + name); ok += bool(cond)
    print(f"window_rescue selftest: {ok}/{len(cases)} passed")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
