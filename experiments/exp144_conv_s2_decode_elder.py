#!/usr/bin/env python3
"""Exp144 n=4 conv STAGE-2 magnitude decode (Elder).

Frozen §3 statistic (chair-ruled): per survivor, over F=12 rotated gauge-random
probes, compute the probe readout mean; MEDIAN over the 12; |median| >= CUT2=0.10
=> ACCEPT (planted term) else conserved-non-planted. Accepted set = recovered
support (expect 3/instance = the m=3 planted terms). Uses the published n=4
survivor row->candidate map (chair C4809: n=4 sweep closed 2-of-2, identities
reveal nothing about which are PLANTED under the frozen rule) to derive
conv_probe(cand, w). n=6 map stays sealed until its stage-1 closes.

Co-batched job layout (manifest): 60 pubs = 5 instances x 12 waves, instance-
major: instance at list-position i, wave w -> pub index i*12 + (w-1); each pub
holds that instance's survivors (survivor_rows order) at S2_SHOTS.
"""
import json, os, sys
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp144_flight_kit import conv_probe          # frozen probe semantics
from exp144_decode_meter import probe_outcomes    # +-1 product over probe sites
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'scripts'))
from ibm_multi_account import multi_account_service  # C6578: sweep ALL accounts, not the default one

CUT2 = 0.10
R = "../results"
MAP = f"{R}/exp144_conv_n4_survivor_map.json"
if not os.path.exists(MAP):
    sys.exit("survivor map not published yet (awaiting Ember per chair C4809) — re-run when present")

svc = multi_account_service()
man = json.load(open(f"{R}/exp144_conv_n4_stage2_manifest.json"))
F = man["s2_family"]
smap = json.load(open(MAP))                        # {"n4_k1": {row_index: cand, ...}, ...}
res = svc.job(man["job_id"]).result()

def bits(pub):
    d = pub.data
    reg = getattr(d, "c", None) or getattr(d, "meas", None)
    return reg.get_bitstrings()

out = {"decoder": "elder", "arm": "conv_stage2", "n": 4, "cut2": CUT2, "instances": {}}
for i, inst in enumerate(man["instances"]):
    k = inst["k"]
    surv = inst["survivor_rows"]                   # ordered list of row indices
    kmap = smap.get(f"n4_k{k}", smap.get(str(k), {}))
    accepted, mags = [], {}
    for j, row in enumerate(surv):
        cand = kmap[str(row)] if str(row) in kmap else kmap[row]
        wave_means = []
        for w in range(1, F + 1):
            pub = res[i * F + (w - 1)]              # instance-major layout
            arr = bits(pub)
            per = len(arr) // len(surv)             # shots per survivor-row in this pub
            probe = conv_probe(cand, w)             # frozen semantics from the published cand
            wave_means.append(float(np.mean(probe_outcomes(arr[j*per:(j+1)*per], probe))))
        med = float(np.median(wave_means))
        if abs(med) >= CUT2:
            accepted.append(row)
        mags[row] = round(med, 4)
    out["instances"][f"n4_k{k}"] = {
        "n_survivors": len(surv), "accepted_support_rows": sorted(accepted),
        "n_accepted": len(accepted), "medians": mags}
    print(f"n4 k{k}: {len(surv)} survivors -> {len(accepted)} accepted (support) "
          f"{sorted(accepted)}  | medians {mags}")

tot = sum(x["n_accepted"] for x in out["instances"].values())
print(f"TOTAL accepted support: {[out['instances'][f'n4_k{k}']['n_accepted'] for k in range(1,6)]} = {tot}  (expect 3/instance = 15)")
fn = f"{R}/exp144_conv_s2_n4_support_elder.json"
json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
import hashlib
print("->", fn, "sha", hashlib.sha256(open(fn, "rb").read()).hexdigest()[:12])
