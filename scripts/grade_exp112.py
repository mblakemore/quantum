#!/usr/bin/env python3
"""grade_exp112.py — apply the FROZEN Exp112 grade rule (Whisper C4599).

Prereg: experiments/exp112-swap-chain-chsh-preregistration.md. Frame arm uses
per-shot register zipping (bitstrings) for branch resolution — join_data
concatenation is avoided per the C4597 lesson. Signs from the frozen
exp112_feasibility.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MANIFEST = os.path.join(HERE, "..", "results", "exp112_jobids.json")
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

SETTING_KEYS = ["a,b", "a,bp", "ap,b", "ap,bp"]
COMBO = {"a,b": 1, "a,bp": 1, "ap,b": 1, "ap,bp": -1}
LABEL2KEY = {"ab": "a,b", "abp": "a,bp", "apb": "ap,b", "apbp": "ap,bp"}


def per_shot(pub, k):
    chsh = pub.data.chsh.get_bitstrings()
    if k == 0:
        return [("-", c) for c in chsh]
    sts = [getattr(pub.data, f"st{i}").get_bitstrings() for i in range(k)]
    return [(" ".join(s[j] for s in reversed(sts)), chsh[j])
            for j in range(len(chsh))]


def main():
    man = json.load(open(MANIFEST))
    feas = json.load(open(os.path.join(HERE, "..", "results",
                                       "exp112_feasibility.json")))
    signs = {int(k): v for k, v in feas["signs_frozen"].items()}
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)

    # E[(arm,k,setting)][branch] = (sum_parity, n)
    acc = {}
    sent = {}
    for pub, meta in zip(res, metas):
        if meta["arm"] == "sent":
            c = pub.data[list(pub.data.keys())[0]].get_counts() if False else \
                getattr(pub.data, list(pub.data.keys())[0]).get_counts()
            want = meta["label"][-1]
            sent[meta["label"]] = c.get(want, 0) / sum(c.values())
            continue
        arm, k = meta["arm"], meta["k"]
        skey = LABEL2KEY[meta["label"].split("_")[-1]]
        for branch, cbits in per_shot(pub, k):
            e = 1 if cbits.count("1") % 2 == 0 else -1
            key = (arm, k, skey)
            acc.setdefault(key, {}).setdefault(branch, [0, 0])
            acc[key][branch][0] += e
            acc[key][branch][1] += 1

    def S_for(arm, k):
        use_signs = (arm in ("frame", "shared")) and k > 0
        branches = set(b for skey in SETTING_KEYS
                       for b in acc[(arm, k, skey)])
        tot_n = 0
        s_weighted = 0.0
        var_sum = 0.0
        for b in branches:
            s_b = 0.0
            n_b = 0
            for skey in SETTING_KEYS:
                tot, n = acc[(arm, k, skey)].get(b, (0, 0))
                if n == 0:
                    continue
                e = tot / n
                # sim convention (chsh_from): S = COMBO * frozen_sign * E.
                # First grader pass dropped COMBO when use_signs (frame k=1 read
                # 1.36 while the frozen matrix matched hardware exactly) — C4599.
                sg = COMBO[skey] * (signs[k][b][skey] if use_signs else 1)
                s_b += sg * e
                var_sum_term = (1 - e * e) / n
                var_sum += var_sum_term * ((n / 1) ** 2) * 0 + 0  # placeholder
                n_b += n
            s_weighted += s_b * n_b
            tot_n += n_b
        S = s_weighted / tot_n * 1.0
        # SE: per-setting pooled-branch propagation (conservative, branch-pooled)
        var = 0.0
        for skey in SETTING_KEYS:
            n_all = sum(n for _, n in acc[(arm, k, skey)].values())
            e_all = sum(t for t, _ in acc[(arm, k, skey)].values()) / n_all
            var += (1 - e_all ** 2) / n_all
        return S, float(np.sqrt(var))

    G = man["gates"]
    S = {}
    S[("shared", 0)] = S_for("shared", 0)
    for arm in ("frame", "active"):
        for k in (1, 2):
            S[(arm, k)] = S_for(arm, k)

    g1 = all(v >= G["G1_readout_floor"] for v in sent.values())
    s0, se0 = S[("shared", 0)]
    g2 = s0 - 5 * se0 > G["G2_k0_floor"]
    cells = {}
    for arm in ("frame", "active"):
        for k in (1, 2):
            s, se = S[(arm, k)]
            cells[f"{arm}_k{k}"] = ("WIN" if s - 5 * se > G["WIN_floor"] else
                                    "LOSS" if s + 5 * se < G["WIN_floor"] else
                                    "AMBIGUOUS")
    verdict = "NO-TEST" if not (g1 and g2) else cells

    out = {"S": {f"{a}_k{k}": {"S": v[0], "SE": v[1]} for (a, k), v in S.items()},
           "sentinels": sent, "gates": {"G1": bool(g1), "G2": bool(g2)},
           "cells": cells, "verdict": verdict,
           "preview": man["preview_S"]}
    print(f"=== Exp112 GRADE (job {man['job_id']}, chain {man['chain']}) ===")
    print(f"  k=0 anchor: S={s0:.4f}±{se0:.4f} (F01 re-anchor; G2={'PASS' if g2 else 'FAIL'})")
    for arm in ("frame", "active"):
        for k in (1, 2):
            s, se = S[(arm, k)]
            print(f"  {arm:7s} k={k}: S={s:.4f}±{se:.4f}  (S-5SE={s-5*se:.4f})  "
                  f"-> {cells[f'{arm}_k{k}']}")
    fa = {k: S[('frame', k)][0] - S[('active', k)][0] for k in (1, 2)}
    print(f"  frame-minus-active: k1={fa[1]:+.4f} k2={fa[2]:+.4f} "
          f"(pre-filed: active<frame conf 0.65)")
    print(f"  sentinels min={min(sent.values()):.3f} | VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp112_grade.json"),
                        "w"), indent=1, default=float)
    print("wrote results/exp112_grade.json")


if __name__ == "__main__":
    main()
