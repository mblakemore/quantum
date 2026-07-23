#!/usr/bin/env python3
"""Exp-HSS DECODER RACE — frozen decode. Card: docs/exp-hss-decoder-race-prereg-whisper-c4975.md
(FROZEN quantum@ec3b5ea). Whisper C4976, substrate claude-fable-5.

Frozen order:
 (1) RUNG-0 SELF-GATE first: blind Chase-12 decode of the two ladder rungs bracketing race_n40's
     d2q (=140 and 196 at the flown routing). s_hat posted; Ember reveals rung0 ONLY; gate =
     exact recovery at BOTH. Race rungs decoded only if gate passes.
 (2) Race rungs: blind decode per pub-granular subsample prefix {2,4,8,16} pubs; primary grade
     at 16 pubs; ratio quotes the smallest exactly-decoding subsample, QPU re-measured at t=80
     via per-shot attribution of the race block (rider excluded per Elder #547; ambiguity
     resolves against quantum).
 (3) Post ALL s_hat publicly -> Ember reveals races -> Elder grades vs frozen band.

Frozen decoder (card + manifest): per-bit majority -> reliability sort -> Chase k=12 (all 2^12
flip patterns of the least-reliable bits), score = sum_shots count*rho^HD, rho=0.5, soft-refine
<=8 iters. Search-adjusted null <= 4097*2^-40 ~ 2^-28. BLIND: consumes counts only; this script
never reads any seal/reveal file.
"""
import json, math, os, sys
from collections import Counter
from itertools import combinations
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
MAN = json.load(open(os.path.join(RES, "exp_hss_decoder_race_flight_manifest.json")))
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
    """Frozen blind decoder. Returns (s_hat, diagnostics)."""
    ones = np.zeros(n); tot = 0; arrs = []
    for s, c in counts.items():
        a = (np.frombuffer(s.encode(), np.uint8).astype(np.int64) - 48)
        ones += c * a; tot += c; arrs.append((a, c))
    frac = ones / tot
    mhat = (frac > 0.5).astype(np.int64)
    reliab = np.abs(frac - 0.5)
    weak = np.argsort(reliab)[:K_CHASE]

    def score(cand):
        return sum(c * RHO ** int((a != cand).sum()) for a, c in arrs)

    best, bs = mhat.copy(), score(mhat)
    for r in range(1, K_CHASE + 1):
        for combo in combinations(weak, r):
            cand = mhat.copy(); cand[list(combo)] ^= 1
            sc = score(cand)
            if sc > bs:
                best, bs = cand, sc
    # soft refine (frozen <=8 iters)
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
    s_hat = "".join(str(b) for b in est)
    return s_hat, {"shots": int(tot), "majority": "".join(str(int(b)) for b in mhat),
                   "hd_majority_vs_final": int((mhat != est).sum()),
                   "min_reliab": float(reliab.min()), "med_reliab": float(np.median(reliab)),
                   "score_final": float(score(est))}


def main(stage):
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    job = svc.job(MAN["job_id"])
    res = job.result()
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        usage = {}
    meta = MAN["pubs_meta"]
    lay = MAN["layouts"]

    out = {"card": "exp_hss_decoder_race_decode", "cycle": "C4976",
           "substrate": "claude-fable-5", "job_id": MAN["job_id"], "usage": usage,
           "stage": stage, "decoder": MAN["decoder_frozen"]}

    if stage == "gate":
        # RUNG-0 self-gate: bracketing rungs around race_n40 d2q
        race_d2q = lay["race_n40"]["d2q"]
        folds = {}
        for i, m in enumerate(meta):
            if m["block"] != "rung0":
                continue
            c = marginalize(get_counts(res[i]), lay["rung0"]["final"])
            fd = folds.setdefault(m["fold_m"], {"d2q": m["d2q"], "counts": Counter()})
            fd["counts"].update(c)
        d2qs = sorted(f["d2q"] for f in folds.values())
        below = max([d for d in d2qs if d <= race_d2q], default=d2qs[0])
        above = min([d for d in d2qs if d >= race_d2q], default=d2qs[-1])
        out["gate_rungs"] = {"race_d2q": race_d2q, "below": below, "above": above}
        out["rung0"] = []
        for fm in sorted(folds):
            s_hat, diag = chase_decode(folds[fm]["counts"], 40)
            row = {"fold_m": fm, "d2q": folds[fm]["d2q"], "s_hat": s_hat, **diag,
                   "gate_rung": folds[fm]["d2q"] in (below, above)}
            out["rung0"].append(row)
            print(f"rung0 m={fm} d2q={row['d2q']} gate_rung={row['gate_rung']} s_hat={s_hat}")
        path = os.path.join(RES, "exp_hss_decoder_race_gate_shat.json")
    else:
        # race rungs, subsample prefixes
        out["race"] = {}
        for block, n in (("race_n40", 40), ("race_n32", 32)):
            pubs_idx = [i for i, m in enumerate(meta) if m["block"] == block]
            out["race"][block] = []
            for npubs in MAN["subsample_ladder_pubs"]:
                pooled = Counter()
                for i in pubs_idx[:npubs]:
                    pooled.update(marginalize(get_counts(res[i]), lay[block]["final"]))
                s_hat, diag = chase_decode(pooled, n)
                row = {"npubs": npubs, "s_hat": s_hat, **diag}
                out["race"][block].append(row)
                print(f"{block} npubs={npubs} shots={diag['shots']} s_hat={s_hat}")
        path = os.path.join(RES, "exp_hss_decoder_race_race_shat.json")

    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path))
    print("POST s_hat PUBLICLY before any reveal opens (two-stage: rung0 gate first).")


if __name__ == "__main__":
    main("race" if "--race" in sys.argv else "gate")
