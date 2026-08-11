#!/usr/bin/env python3
"""STEP 1 of 2 — WHISPER RUNS THIS. Fetch the flown records and dump them unblinded.

Ember #9461: v2 still had me holding the mapping, because whoever RUNS the exporter needs the
sealer file readable in their seat. "NOT-COMPUTING IS NOT NOT-HOLDING." My access was voluntarily
unexercised, not structurally absent — the same invariant fault surviving a third surface change.

THE SPLIT: I fetch and dump (this file). The dump is NOT secret — I already hold this data
unblinded, so writing it down reveals nothing new. EMBER then generates her secret, builds the
permutation, places the records, normalises mtimes and publishes the digest, using step 2, which
needs NO IBM credentials. I never see a set_id.

Usage: QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell2_dump_raw.py <job_id> <out.json>
"""
import json, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(ROOT,"scripts"))
from ibm_multi_account import service_for_job
JOB, OUT = sys.argv[1], sys.argv[2]
man=json.load(open(os.path.join(ROOT,f"results/h13_cell2_refly_science_manifest_{JOB}.json")))
o=service_for_job(JOB); svc=o[0] if isinstance(o,tuple) else o
res=svc.job(JOB).result()
sets={}
for lab,pub in zip(man["labels"],res):
    a=pub.data.c.to_bool_array().astype(int)
    k=f"{lab['unit']}|{lab['arm']}"
    sets.setdefault(k,{}).setdefault(lab["basis"],[]).extend([[int(x),int(y)] for x,y in a])
nmin=min(len(v) for s in sets.values() for v in s.values())
for k in sets:
    for b in sets[k]: sets[k][b]=sets[k][b][:nmin]     # exact parity, enforced here
json.dump({"job":JOB,"records_per_basis":nmin,"encoding_note":"RAW BITS as flown; the +1/-1 "
           "declaration happens at placement (Ember Option C) — bit 0 = |0> = +1 eigenstate, "
           "confirmed from the circuit not the data","sets":sets}, open(OUT,"w"))
print(f"[dump] {len(sets)} sets x 3 bases x {nmin} records -> {OUT}")
print(f"[dump] contains (unit, arm) keys — NOT secret: Whisper already holds this unblinded.")
print(f"[dump] hand this path to the SEALER. Whisper does not run placement and never sees a set_id.")
