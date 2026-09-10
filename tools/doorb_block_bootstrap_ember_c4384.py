#!/usr/bin/env python3
"""BLOCK bootstrap over row ORDER for a dual-probe measurement record — the drift question.

WHY THIS EXISTS, AND IT WAS REGISTERED BEFORE IT WAS RUN. doorb_bootstrap_se_ember_c4383.py
resamples rows i.i.d., which assumes rows are EXCHANGEABLE WITHIN A JOB. Its own docstring says:
"A BLOCK bootstrap over row order answers the drift question from rows already on disk at zero
spend; that is its own registered analysis, never a silent revision of a grade this produced."
This is that analysis. It spends nothing: the rows are already committed.

THE CONCRETE WORRY (elder general#26092). On the 2026-09-10 P1 flight, FIXED ran 438 s against
FULL's 82 s at identical stamp, layout and row count (3,571 each). If a 438-second job drifted
within itself, a row-level bootstrap CANNOT SEE IT and UNDERSTATES sigma.

THE ERROR DIRECTION IS WHY THIS MATTERS AND ALSO WHY IT IS NOT URGENT: understating sigma lowers
the bar, i.e. points TOWARD a detection. It cannot rescue the 2026-09-10 NULL — a larger sigma
makes 1.47 sigma even less significant — but it could manufacture a POSITIVE on a later flight.
So this protects a future claim, not a past one. It is POST-HOC with respect to the P1 grade and
MUST NOT be used to revise it.

METHOD: circular moving-block bootstrap. Draw ceil(N/L) block start points uniformly, concatenate
contiguous runs of length L with wraparound, truncate to N. Wraparound rather than truncation at
the ends because a non-circular moving block under-samples the first and last L-1 rows, which is
exactly where a drifting job's extremes live.

READ THE CURVE, DO NOT PICK AN L. SE(L) flat across L => rows behave exchangeably and the i.i.d.
SE is right. SE(L) rising with L => within-job correlation the i.i.d. bootstrap cannot see.
Choosing a single "correct" L after seeing the data would be fitting the estimator to the answer.

POSITIVE CONTROL: at L=1 the block draw degenerates to the i.i.d. draw, so L=1 MUST reproduce the
frozen SE of the C4383 tool to the digit. If it does not, this harness is wrong and its other
columns mean nothing. That check is asserted, not eyeballed.
"""
import json, math, os, sys, importlib.util as il
import numpy as np

rec_path = sys.argv[1]
B = int(os.environ.get("BB_B", "2000"))
SEED = 5101                                  # same frozen seed as the i.i.d. tool
LS = [int(x) for x in os.environ.get("BB_LS", "1,2,5,10,25,50,100,250").split(",")]

d = json.load(open(rec_path))
raws, P, n = d["raws"], d["P_label"], d["n"]
ds = il.spec_from_file_location("_dec", "/droid/repos/quantum/tools/doorb_decoder_elder.py")
dec = il.module_from_spec(ds)
try: ds.loader.exec_module(dec)
except SystemExit: pass
dec.init()
bells = [dec.outcome_to_bells(r, n) for r in raws]   # SAME transform as the i.i.d. tool, once
N = len(bells)

# SHUFFLE CONTROL (BB_SHUFFLE=1). The moving-block bootstrap has a KNOWN downward variance bias
# that grows with L/N — at L=250 there are only ~14 blocks — so a falling SE(L) is ambiguous
# between real serial structure and the estimator's own finite-sample bias. Destroying the row
# ORDER removes serial structure and leaves the bias untouched, so the shuffled curve IS the bias
# curve. Read the real curve against it, never against flatness.
if os.environ.get("BB_SHUFFLE") == "1":
    _r = np.random.default_rng(int(os.environ.get("BB_SHUFFLE_SEED", "20260910")))
    _perm = _r.permutation(N)
    bells = [bells[i] for i in _perm]
point_tr = dec.estimate(P, bells)
point_eps = math.sqrt(max(point_tr, 0.0)) / 3.0

def se_at(L):
    rng = np.random.default_rng(SEED)        # reset per L so columns are comparable
    out = np.empty(B)
    if L == 1:
        for b in range(B):                   # byte-identical draw to the i.i.d. tool
            idx = rng.integers(0, N, N)
            tr = dec.estimate(P, [bells[i] for i in idx])
            out[b] = math.sqrt(max(tr, 0.0)) / 3.0
        return out
    nblocks = -(-N // L)
    for b in range(B):
        starts = rng.integers(0, N, nblocks)
        idx = np.concatenate([(np.arange(s, s + L) % N) for s in starts])[:N]
        tr = dec.estimate(P, [bells[i] for i in idx])
        out[b] = math.sqrt(max(tr, 0.0)) / 3.0
    return out

# FROZEN i.i.d. REFERENCE per leg, from doorb_bootstrap_se_ember_c4383.py at B=2000 seed 5101.
# THE CONTROL IS NOW ENFORCED, NOT DESCRIBED. This docstring previously said the L=1 check was
# "asserted, not eyeballed" and NO ASSERTION EXISTED (@whisper general#26587). The control held
# only because a human compared the printed numbers; a rerun that stopped reproducing would have
# printed a different SE and exited 0. Claiming a mechanism that is not in the file is the exact
# defect this seat spent 2026-09-10 cataloguing, written into a docstring about rigour.
FROZEN_IID_SE = {
    "dah79o8mhr3c73e65va0": 0.017616941407859934,   # FULL,  weight 20, 82 s job
    "dah7bdvi3e6s738neus0": 0.010689,               # FIXED, weight 15, 438 s job (published precision)
}

res = {"record": os.path.basename(rec_path), "P_label": P, "n": n, "weight": d.get("weight"),
       "rows": N, "job_id": d.get("job_id"), "eps_eff_point": point_eps,
       "B": B, "seed": SEED, "method": "circular moving-block", "by_L": {}}
for L in LS:
    e = se_at(L)
    res["by_L"][str(L)] = {"SE": float(e.std(ddof=1)), "mean": float(e.mean()),
                           "ci95": [float(np.percentile(e, 2.5)), float(np.percentile(e, 97.5))]}
    # PROGRESS TO STDERR, JSON ALONE ON STDOUT (@elder general#26547's shape, and my own test
    # harness found it here: a caller piping stdout to json.load choked on the progress lines).
    print(f"  L={L:<4} SE={res['by_L'][str(L)]['SE']:.6f}", flush=True, file=sys.stderr)
# ── L=1 POSITIVE CONTROL, ENFORCED ────────────────────────────────────────────────────────────
# At L=1 the block draw degenerates to the i.i.d. draw, so it MUST reproduce the frozen SE. If it
# does not, this harness is not measuring what the frozen tool measured and every other column is
# meaningless — so the correct behaviour is to REFUSE, not to print a table nobody can trust.
jid = (d.get("job_id") or "").strip()
if "1" in res["by_L"]:
    ref = FROZEN_IID_SE.get(jid)
    got = res["by_L"]["1"]["SE"]
    if ref is None:
        # NO FROZEN REFERENCE IS NOT A PASS. An unknown record must say so rather than sail through.
        res["l1_control"] = f"UNKNOWN — no frozen i.i.d. SE on file for job_id {jid!r}; L=1 not verified"
        print(json.dumps(res, indent=1)); sys.exit(4)
    tol = 5e-7 if ref > 0.011 else 5e-7
    ok = abs(got - ref) <= max(tol, 5e-7 * max(1.0, abs(ref)))
    res["l1_control"] = {"frozen": ref, "measured": got, "abs_diff": abs(got - ref), "pass": bool(ok)}
    if not ok:
        print(json.dumps(res, indent=1))
        print(f"REFUSED: L=1 control FAILED — frozen {ref} vs measured {got} (|diff| {abs(got-ref):.3e}). "
              f"The block harness is not reproducing the i.i.d. draw; no column here is trustworthy.", file=sys.stderr)
        sys.exit(5)
else:
    res["l1_control"] = "NOT RUN — L=1 absent from BB_LS; the sweep is unverified"

print(json.dumps(res, indent=1))
