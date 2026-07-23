#!/usr/bin/env python3
"""Exp-HSS RACE 3 — frozen decode (card docs/exp-hss-race3-prereg-FROZEN-whisper-c4978.md).
Whisper C4978, substrate claude-fable-5. BLIND: counts only; never reads seals. s_hat reported
in s_str display order. Vectorized Chase-12 (quantum@5dca04a lineage, race-2 verified).

Stage "gate": ladder + twin40 + twin32 s_hat (+ subsample prefixes) -> post -> Ember reveals
the two t=0 strings -> Path-B twin gates adjudicated + convention anchor (ladder m0).
Stage "race": race_n40 ({2,4,8,16,32} pubs) + race_n32 ({2,4,8,16}) -> post -> race reveals ->
Elder grades Path A (rho_t from emitted bit_frac vs revealed s) + Path B (n40 only; n32
cap-ineligible per manifest).
Every row emits bit_frac (40/32 floats, marginal-order) so the per-bit bias vs revealed s and
the bootstrap-CI rho_t are computable post-reveal by any court member.
"""
import json, os, sys
from collections import Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
MAN = json.load(open(os.path.join(RES, "exp_hss_race3_flight_manifest.json")))
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
    w_int = (A[:, weak].astype(np.int64)) @ pow2
    u = np.zeros(1 << K_CHASE)
    np.add.at(u, w_int, c * (RHO ** hd_strong))
    pc = np.array([bin(x).count("1") for x in range(1 << K_CHASE)])
    rho_pc = RHO ** pc
    scores = np.array([u @ rho_pc[np.arange(1 << K_CHASE) ^ p] for p in range(1 << K_CHASE)])
    p_best = int(np.argmax(scores))
    best = mhat.copy()
    best[weak] = ((p_best >> np.arange(K_CHASE)) & 1).astype(np.int8)
    est = best
    for _ in range(SOFT_ITERS):
        w_s = c * (RHO ** (A != est).sum(1))
        new = ((w_s @ A) / w_s.sum() > 0.5).astype(np.int8)
        if (new == est).all():
            break
        est = new
    marg = "".join(str(int(b)) for b in est)
    return marg[::-1], {"shots": int(tot),
                        "min_reliab": float(np.abs(frac - 0.5).min()),
                        "med_reliab": float(np.median(np.abs(frac - 0.5))),
                        "bit_frac_marginal_order": [round(float(x), 5) for x in frac]}


def pooled_for(meta, res, block, lay_key, npubs=None):
    idxs = [i for i, m in enumerate(meta) if m["block"] == block]
    if npubs is not None:
        idxs = idxs[:npubs]
    pooled = Counter()
    for i in idxs:
        pooled.update(marginalize(get_counts(res[i]), MAN["layouts"][lay_key]["final"]))
    return pooled


BLOCKS = {
    "ladder_m0": ("ladder", "rung0_base", 40, 0),
    "ladder_m1": ("ladder", "rung0_base", 40, 1),
    "twin40": ("twin40", "twin40_src", 40, None),
    "twin32": ("twin32", "twin32_src", 32, None),
    "race_n40": ("race_n40", "race_n40", 40, None),
    "race_n32": ("race_n32", "race_n32", 32, None),
}


def decode_block(meta, res, name, subsamples):
    block, lay, n, fm = BLOCKS[name]
    rows = []
    if fm is not None:
        idxs = [i for i, m in enumerate(meta) if m["block"] == block and m["fold_m"] == fm]
        pooled = Counter()
        for i in idxs:
            pooled.update(marginalize(get_counts(res[i]), MAN["layouts"][lay]["final"]))
        s_hat, diag = chase_decode(pooled, n)
        rows.append({"block": name, "d2q": meta[idxs[0]]["d2q"], "s_hat": s_hat, **diag})
        return rows
    for npubs in subsamples:
        pooled = pooled_for(meta, res, block, lay, npubs)
        s_hat, diag = chase_decode(pooled, n)
        rows.append({"block": name, "npubs": npubs, "d2q": MAN["layouts"][lay]["d2q"]
                     if name.startswith("race") else MAN["layouts"]["race_n40" if name == "twin40"
                     else "race_n32"]["d2q"], "s_hat": s_hat, **diag})
    return rows


def main(stage):
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(MAN["job_id"])
    res = job.result()
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        usage = {}
    meta = MAN["pubs_meta"]
    out = {"card": "exp_hss_race3_decode", "cycle": "C4978", "substrate": "claude-fable-5",
           "job_id": MAN["job_id"], "usage": usage, "stage": stage,
           "decoder": MAN["decoder_frozen"], "depth_cap": MAN["depth_cap"],
           "advantage_eligible": MAN["advantage_eligible"], "rows": []}
    sub = MAN["subsample_pubs"]
    if stage == "gate":
        for name in ("ladder_m0", "ladder_m1", "twin40", "twin32"):
            subs = sub.get(name)          # twins have subsample ladders; ladder rungs don't
            out["rows"] += decode_block(meta, res, name, subs)
        path = os.path.join(RES, "exp_hss_race3_gate_shat.json")
    else:
        for name in ("race_n40", "race_n32"):
            out["rows"] += decode_block(meta, res, name, sub[name])
        path = os.path.join(RES, "exp_hss_race3_race_shat.json")
    for r in out["rows"]:
        print(f"{r['block']}{'@'+str(r.get('npubs')) if r.get('npubs') else ''} "
              f"d2q={r['d2q']} shots={r['shots']} s_hat={r['s_hat']}")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path), "— POST s_hat before reveals (two-stage).")


if __name__ == "__main__":
    main("race" if "--race" in sys.argv else "gate")
