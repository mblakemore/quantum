#!/usr/bin/env python3
"""Exp-HSS RACE 2 — frozen decode (card docs/exp-hss-decoder-race2-prereg-whisper-c4977.md).
Whisper C4977, substrate claude-fable-5. BLIND: consumes counts only, never reads seals.
Reports s_hat in s_str DISPLAY ORDER (reverse of qubit-index marginal — C4976 sim-pinned).

Stage "gate": decode ladder (informational) + BOTH shot-matched gate rungs -> post s_hat ->
Ember reveals rung0 -> gate = exact at both. Stage "race" (only if gate passes): subsample
prefixes {2,4,8,16} pubs per race rung; n32 graded only if d2q_race32 <= gate_above d2q.
"""
import json, os, sys
from collections import Counter
from itertools import combinations
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
MAN = json.load(open(os.path.join(RES, "exp_hss_race2_flight_manifest.json")))
NPHYS = 156
K_CHASE, RHO, SOFT_ITERS = 12, 0.5, 8


def get_counts(res_item):
    return res_item.data[list(res_item.data.keys())[0]].get_counts()


def marginalize(counts, layout):
    idx = [NPHYS - 1 - p for p in layout]
    out = Counter()
    for s, c in counts.items():
        out["".join(s[i] for i in idx)] += c
    return out


def chase_decode(counts, n):
    ones = np.zeros(n); tot = 0; arrs = []
    for s, c in counts.items():
        a = (np.frombuffer(s.encode(), np.uint8).astype(np.int64) - 48)
        ones += c * a; tot += c; arrs.append((a, c))
    frac = ones / tot
    mhat = (frac > 0.5).astype(np.int64)
    weak = np.argsort(np.abs(frac - 0.5))[:K_CHASE]

    def score(cand):
        return sum(c * RHO ** int((a != cand).sum()) for a, c in arrs)

    best, bs = mhat.copy(), score(mhat)
    for r in range(1, K_CHASE + 1):
        for combo in combinations(weak, r):
            cand = mhat.copy(); cand[list(combo)] ^= 1
            sc = score(cand)
            if sc > bs:
                best, bs = cand, sc
    est = best
    for _ in range(SOFT_ITERS):
        num = np.zeros(n); den = 0.0
        for a, c in arrs:
            w = c * RHO ** int((a != est).sum())
            num += w * a; den += w
        new = (num / den > 0.5).astype(np.int64)
        if (new == est).all():
            break
        est = new
    marg = "".join(str(b) for b in est)
    return marg[::-1], {"shots": int(tot),  # display order (card §3c)
                        "min_reliab": float(np.abs(frac - 0.5).min()),
                        "med_reliab": float(np.median(np.abs(frac - 0.5)))}


def pooled_for(meta, res, block, lay_key, npubs=None):
    idxs = [i for i, m in enumerate(meta) if m["block"] == block]
    if npubs is not None:
        idxs = idxs[:npubs]
    pooled = Counter()
    for i in idxs:
        pooled.update(marginalize(get_counts(res[i]), MAN["layouts"][lay_key]["final"]))
    return pooled


def main(stage):
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(MAN["job_id"])
    res = job.result()
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        usage = {}
    meta = MAN["pubs_meta"]
    out = {"card": "exp_hss_race2_decode", "cycle": "C4977", "substrate": "claude-fable-5",
           "job_id": MAN["job_id"], "usage": usage, "stage": stage,
           "decoder": MAN["decoder_frozen"], "gate_plan": MAN["gate_plan"]}

    if stage == "gate":
        rows = []
        for fm in (0, 1):
            idxs = [i for i, m in enumerate(meta) if m["block"] == "ladder" and m["fold_m"] == fm]
            pooled = Counter()
            for i in idxs:
                pooled.update(marginalize(get_counts(res[i]), MAN["layouts"]["rung0_base"]["final"]))
            s_hat, diag = chase_decode(pooled, 40)
            rows.append({"block": f"ladder_m{fm}", "d2q": meta[idxs[0]]["d2q"], "s_hat": s_hat, **diag})
        for tag in ("gate_below", "gate_above"):
            pooled = pooled_for(meta, res, tag, f"{tag}_src")
            s_hat, diag = chase_decode(pooled, 40)
            rows.append({"block": tag, "d2q": MAN["gate_plan"][tag]["d2q"], "s_hat": s_hat, **diag})
            # Elder #571 ask: subsample diagnostics so a fold is interpretable (informational;
            # the GATE adjudicates at full 100k only)
            for npubs in MAN["subsample_ladder_pubs"][:-1]:
                sp = pooled_for(meta, res, tag, f"{tag}_src", npubs)
                sh, dg = chase_decode(sp, 40)
                rows.append({"block": f"{tag}_sub{npubs}", "d2q": MAN["gate_plan"][tag]["d2q"],
                             "s_hat": sh, **dg, "informational": True})
        out["rows"] = rows
        for r in rows:
            print(f"{r['block']} d2q={r['d2q']} shots={r['shots']} s_hat={r['s_hat']}")
        path = os.path.join(RES, "exp_hss_race2_gate_shat.json")
    else:
        out["race"] = {}
        for block, n, lay in (("race_n40", 40, "race_n40"), ("race_n32", 32, "race_n32")):
            out["race"][block] = []
            for npubs in MAN["subsample_ladder_pubs"]:
                pooled = pooled_for(meta, res, block, lay, npubs)
                s_hat, diag = chase_decode(pooled, n)
                out["race"][block].append({"npubs": npubs, "s_hat": s_hat, **diag})
                print(f"{block} npubs={npubs} s_hat={s_hat}")
        path = os.path.join(RES, "exp_hss_race2_race_shat.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path), "— POST s_hat before reveals (two-stage).")


if __name__ == "__main__":
    main("race" if "--race" in sys.argv else "gate")
