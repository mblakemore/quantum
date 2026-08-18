#!/usr/bin/env python3
"""H15 epoch survey — SUBMIT one epoch (Whisper C5075). Unsealed, claim-free diagnostic;
same authorisation class as the R1 probes (Elder general#12730 precedent), no seal-bound GO.

  python3 h15_survey_fly_whisper_c5075.py --epoch N            # sim gate only
  python3 h15_survey_fly_whisper_c5075.py --epoch N --fly      # gate then submit

ONE EPOCH PER INVOCATION BY DESIGN. The 13 epochs must be spread across TIMES AND DAYS; a
loop that fires them back-to-back would measure one weather system and call it a climate,
which is the exact error that produced the retracted 0.875 reading."""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from h15_survey_epoch_whisper_c5075 import build_epoch, selftest, BASE_SEED

# ACCOUNT FALLBACK (C5075). Extending the survey 13 -> 20 epochs needs ~25 QPU-s while ALT4 held
# 17 — the run would have stalled around epoch 12 when the driver's tank guard tripped, quietly and
# with a "held" log line rather than a failure. Both accounts are open-instance on the SAME backend
# (kingston, runtime-verified plan=open), so this is a BILLING ROUTE, not a device change: no
# physics differs between epochs flown on either. The route actually used is recorded per-epoch in
# each manifest so the analysis can check the assumption instead of inheriting it.
ACCOUNTS, BACKEND = ("IBMQ_ALT4", "IBMQ_ALT5"), "ibm_kingston"
MIN_S = 3

def pick_account():
    """First account with enough tank. Never silently picks a paid route: both entries are
    runtime-verified open plans and service_for_submission's #151 gate refuses anything else."""
    import ibm_multi_account as M
    for acct in ACCOUNTS:
        try:
            svc = M.service_for_submission(acct)
            u = svc.usage()
            rem = u.get("usage_remaining_seconds")
            if rem is None or rem >= MIN_S:
                print(f"account {acct}: remaining {rem}s -> selected")
                return acct, svc
            print(f"account {acct}: remaining {rem}s < {MIN_S}s -> skip")
        except Exception as e:
            print(f"account {acct}: unreadable ({type(e).__name__}) -> skip")
    raise SystemExit("NO ACCOUNT WITH TANK — not flying (this is a halt, not a silent skip).")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epoch", type=int, required=True)
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    ok, d = selftest(a.epoch)
    print(f"SIM GATE epoch {a.epoch}: ok={ok} {json.dumps(d)}")
    if not ok:
        sys.exit("SIM GATE FAILED - no submission.")
    if not a.fly:
        return
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    import ibm_multi_account as M
    ACCOUNT, svc = pick_account()
    backend = svc.backend(BACKEND)
    tqcs = transpile(build_epoch(a.epoch), backend, optimization_level=1,
                     seed_transpiler=BASE_SEED + a.epoch)
    snap = M.submit_snapshot(backend)
    print(f"queue snapshot: {snap}")
    job = SamplerV2(mode=backend).run([(t,) for t in tqcs], shots=1)
    jid = job.job_id()
    print(f"JOB ID (ANNOUNCED AT SUBMIT): {jid}")
    out = os.path.join(HERE, "..", "results", f"h15_survey_epoch{a.epoch}_manifest_c5075.json")
    json.dump({"card": "h15_epoch_survey", "cycle": "C5075", "epoch": a.epoch,
               "job_id": jid, "backend": BACKEND, "account": ACCOUNT,
               "rows": len(tqcs), "shots_per_row": 1, "seed": BASE_SEED + a.epoch,
               "authorisation": "unsealed claim-free diagnostic (Elder general#12730 class)",
               "queue_at_submit": snap}, open(out, "w"), indent=1)
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
