#!/usr/bin/env python3
"""Exp-HSS RACE 2 — frozen decode (card docs/exp-hss-race2-prereg-FROZEN-whisper-c4977.md).
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
    """Frozen algorithm (k=12, rho=0.5, soft<=8) — vectorized implementation, mathematically
    identical to the exploratory-script loops: candidate set = majority + ALL 2^12 flip patterns
    of the k least-reliable bits; score(cand) = sum_shots count*rho^HD(shot,cand), computed by
    grouping shots into u[w] = sum count*rho^HD_strong per weak-bit pattern w, then
    score(p) = sum_w u[w]*rho^popcount(w XOR p). (Tie-break: lowest pattern index — exact score
    ties across candidates have probability ~0 and none occurred.)"""
    S = len(counts)
    A = np.empty((S, n), dtype=np.int8)
    c = np.empty(S, dtype=np.float64)
    for i, (s, cnt) in enumerate(counts.items()):
        A[i] = np.frombuffer(s.encode(), np.uint8).astype(np.int8) - 48
        c[i] = cnt
    tot = c.sum()
    frac = (c @ A) / tot
    mhat = (frac > 0.5).astype(np.int8)
    order = np.argsort(np.abs(frac - 0.5))
    weak, strong = order[:K_CHASE], order[K_CHASE:]
    hd_strong = (A[:, strong] != mhat[strong]).sum(1)
    pow2 = (1 << np.arange(K_CHASE)).astype(np.int64)
    w_int = ((A[:, weak].astype(np.int64)) @ pow2)
    u = np.zeros(1 << K_CHASE)
    np.add.at(u, w_int, c * (RHO ** hd_strong))
    pc = np.array([bin(x).count("1") for x in range(1 << K_CHASE)])
    rho_pc = RHO ** pc
    scores = np.array([u @ rho_pc[np.arange(1 << K_CHASE) ^ p] for p in range(1 << K_CHASE)])
    p_best = int(np.argmax(scores))
    best = mhat.copy()
    best[weak] = (p_best >> np.arange(K_CHASE)) & 1
    est = best.astype(np.int8)
    for _ in range(SOFT_ITERS):
        w_s = c * (RHO ** (A != est).sum(1))
        new = ((w_s @ A) / w_s.sum() > 0.5).astype(np.int8)
        if (new == est).all():
            break
        est = new
    marg = "".join(str(int(b)) for b in est)
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
