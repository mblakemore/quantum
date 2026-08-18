#!/usr/bin/env python3
"""H15 survey COLLECTOR (Whisper C5075) — banks raw rows for any flown-but-unbanked epoch.

WHY THIS EXISTS: the driver records a job_id and nothing else, which would leave the survey's
data living only at IBM. This campaign has already paid that bill once — C5071 rescued 238 jobs
whose shot records were manifest-only, days from the retention edge. Retrieval is not custody.
Runs after each flight from the same cron; idempotent, banks only what is missing, never recomputes.

Also banks per-row A-WEIGHT alongside the accept bit, which is Declared Output 2 of the survey
(ALT-vs-weight slope) — pre-stated before the survey finished."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from h15_survey_epoch_whisper_c5075 import epoch_rows, decode_epoch, N_EPOCHS
R = os.path.join(HERE, "..", "results")

def bank(epoch):
    man = os.path.join(R, f"h15_survey_epoch{epoch}_manifest_c5075.json")
    dec = os.path.join(R, f"h15_survey_epoch{epoch}_decoded_c5075.json")
    if not os.path.exists(man) or os.path.exists(dec):
        return None
    jid = json.load(open(man))["job_id"]
    import ibm_multi_account as M
    svc = M.service_for_submission("IBMQ_ALT4")
    job = svc.job(jid)
    if "DONE" not in str(job.status()):
        return f"epoch {epoch} job {jid} not DONE yet"
    res = job.result()
    mems = [f"{p.data.act.get_bitstrings()[0]} {p.data.dec.get_bitstrings()[0]} "
            f"{p.data.bell.get_bitstrings()[0]}" for p in res]
    d = decode_epoch(epoch, mems)
    rows = epoch_rows(epoch)
    per_row = []
    for (kind, A, arm), mem in zip(rows, mems):
        if kind != "ALT":
            continue
        w = sum(sum(r) for r in A)                      # planted-term weight -> Output 2
        act = int(mem.split()[0])
        per_row.append({"weight": w, "accept": act})
    m = job.metrics()
    json.dump({"card": "h15_survey_epoch", "epoch": epoch, "job": jid,
               "alt_accept": d["ALT"]["accept"] / d["ALT"]["n"], "counts": d,
               "per_row_ALT_weight_accept": per_row,
               "usage": m.get("usage"), "timestamps": m.get("timestamps"),
               "rows": mems}, open(dec, "w"), indent=1)
    return f"epoch {epoch} BANKED: ALT {d['ALT']['accept']}/{d['ALT']['n']} = {d['ALT']['accept']/d['ALT']['n']:.4f}"

if __name__ == "__main__":
    for e in range(N_EPOCHS):
        msg = bank(e)
        if msg:
            print(msg)
