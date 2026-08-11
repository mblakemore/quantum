#!/usr/bin/env python3
"""Blinded records export for the Cell 2 RE-FLY science block. Whisper C5058.

Emits ONLY Elder's declared seam: one file per record set, flat dir, opaque names,
{"records":[{"basis":"XX","a":0,"b":1}, ...]} with RAW 0/1 (his decoder owns the 0->+1,1->-1
mapping; this tool does NOT re-map upstream). UNPAIRED, shuffled: 80 sets, pairing unrecoverable
from content, order or filename — the structure section A prices.
The set_id -> arm mapping is withheld; only its sha256 is published, for Ember to seal.
I DO NOT DECODE. The grader seat is Elder's and the seal is Ember's.
"""
import json, os, sys, hashlib
import numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(ROOT,"scripts"))
from ibm_multi_account import service_for_job
JOB=sys.argv[1]
man=json.load(open(os.path.join(ROOT,f"results/h13_cell2_refly_science_manifest_{JOB}.json")))
o=service_for_job(JOB); svc=o[0] if isinstance(o,tuple) else o
res=svc.job(JOB).result()
# one SET = (unit, arm); the three diagonals live inside it, twirl components pooled
sets={}
for lab,pub in zip(man["labels"],res):
    a=pub.data.c.to_bool_array().astype(int)
    sets.setdefault((lab["unit"],lab["arm"]),{}).setdefault(lab["basis"],[]).append(a)
keys=sorted(sets.keys())
# Independent shuffle stream — deliberately NOT derived from the flight seed's position, which
# would make the permutation reconstructible by anyone who reruns the builder. Seeded from the
# job id so it is reproducible for audit AFTER the mapping is unsealed, not before.
rng=np.random.default_rng(int(hashlib.sha256(JOB.encode()).hexdigest()[:8],16))
perm=rng.permutation(len(keys))
uids=[hashlib.sha256(f"{man['seed']}:refly:{i}".encode()).hexdigest()[:16] for i in range(len(keys))]
outdir=os.path.join(ROOT,f"results/h13_cell2_refly_blinded_{JOB}")
os.makedirs(outdir,exist_ok=True)
mapping={}
nmin=min(sum(x.shape[0] for x in v) for s in sets.values() for v in s.values())
for slot,src in enumerate(perm):
    unit,arm=keys[src]; uid=uids[slot]; recs=[]
    for b in ("X","Y","Z"):
        arr=np.vstack(sets[(unit,arm)][b])[:nmin]
        recs += [{"basis":b+b,"a":int(x),"b":int(y)} for x,y in arr]
    json.dump({"records":recs}, open(os.path.join(outdir,f"{uid}.json"),"w"))
    mapping[uid]=arm
digest=hashlib.sha256(json.dumps(mapping,sort_keys=True).encode()).hexdigest()
print(f"[export] {len(mapping)} sets x {nmin*3} records ({nmin}/basis, exact parity) -> {outdir}")
print(f"[audit]  per-record fields ['basis','a','b']; per-file key ['records']; no arm/scenario/label/circuit")
print(f"[seal]   {len(mapping)}-entry set_id->arm mapping sha256 = {digest}")
json.dump({"mapping_sha256":digest,"n_sets":len(mapping),"records_per_basis":nmin,
           "job":JOB,"structure":"UNPAIRED, shuffled — pairing unrecoverable",
           "note":"mapping withheld for Ember's seal; Whisper does not decode"},
          open(os.path.join(ROOT,f"results/h13_cell2_refly_mapping_digest_{JOB}.json"),"w"),indent=1)
