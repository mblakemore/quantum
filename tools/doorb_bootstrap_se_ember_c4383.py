#!/usr/bin/env python3
"""Bootstrap SE(eps_eff) over a dual-probe measurement record's persisted raw rows.

FROZEN INPUTS (p1-dual-probe-frozen-spec-whisper-c5101.md section 3, digest ee900bdc...70aad):
B = 2000, seed 5101. Both are pinned IN THE SPEC, which is what lets this be computed AFTER
seeing data without becoming a post-hoc choice — a bootstrap with a B or seed picked after leg 1
would be the amendment nobody asked for. Do not "improve" either number here.

sigma(Delta) = sqrt(SE_full^2 + SE_fixed^2), measured. The planning value 0.01018 is informational
only, and on the 2026-09-10 flight the MEASURED sigma came out 2.025x it — the verdict sat 0.77%
under the planning bar, so propagating instead of measuring would have been the whole result.

Resamples INDICES into a bells array computed once, not the raw rows: outcome_to_bells is a
per-row transform, so re-running it per bootstrap draw would be 7.1M redundant conversions for
an identical answer.
"""
import json, math, os, sys, importlib.util as il
import numpy as np
rec_path = sys.argv[1]
d = json.load(open(rec_path))
raws, P, n = d["raws"], d["P_label"], d["n"]
ds = il.spec_from_file_location("_dec", "/droid/repos/quantum/tools/doorb_decoder_elder.py")
dec = il.module_from_spec(ds)
try: ds.loader.exec_module(dec)
except SystemExit: pass
dec.init()
bells = [dec.outcome_to_bells(r, n) for r in raws]          # per-row transform, done once
N = len(bells)
point_tr = dec.estimate(P, bells)
point_eps = math.sqrt(max(point_tr, 0.0)) / 3.0
rng = np.random.default_rng(5101)                            # FROZEN seed
B = 2000                                                     # FROZEN B
eps_b = np.empty(B)
for b in range(B):
    idx = rng.integers(0, N, N)
    tr = dec.estimate(P, [bells[i] for i in idx])
    eps_b[b] = math.sqrt(max(tr, 0.0)) / 3.0
print(json.dumps({"record": os.path.basename(rec_path), "P_label": P, "n": n, "rows": N,
                  "tr_sq_point": point_tr, "eps_eff_point": point_eps,
                  "SE_eps_bootstrap": float(eps_b.std(ddof=1)),
                  "eps_b_mean": float(eps_b.mean()),
                  "ci95": [float(np.percentile(eps_b, 2.5)), float(np.percentile(eps_b, 97.5))],
                  "B": B, "seed": 5101}, indent=1))
