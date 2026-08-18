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


def main():
    from ibm_multi_account import service_for_job
    tg = targets()
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    out_path = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
                else f"{Q}/results/window_rescue_c5075.json")
    items = list(tg.items())[:limit] if limit else list(tg.items())
    out = {"card": "window_rescue", "cycle": "C5075",
           "why": "bank epoch windows before a vendor retention clock we have not measured can close them",
           "n_targets": len(items), "jobs": {}}
    lost = kept = 0
    for i, (jid, src) in enumerate(items, 1):
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
    print(f"@@ DONE retrievable={kept} lost={lost} -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
