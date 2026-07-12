#!/usr/bin/env python3
"""grade_exp111.py — apply the FROZEN Exp111 grade rule (Whisper C4594).

Prereg: experiments/exp111-e1-resource-comparison-preregistration.md (+ dated
compilation amendment). Filters and gate constants read from the manifest.
Outcome vector order (counts keys 'tc'): (t0 c+, t0 c-, t1 c+, t1 c-).
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MANIFEST = os.path.join(HERE, "..", "results", "exp111_jobids.json")
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

PAULIS = ["1", "X", "Y", "Z"]
OUT_ORDER = ("00", "01", "10", "11")   # 'tc': t0c+, t0c-, t1c+, t1c-


def pool(counts_by_label, keys):
    p = {}
    for k in keys:
        for o, v in counts_by_label[k].items():
            p[o] = p.get(o, 0) + v
    n = sum(p.values())
    return np.array([p.get(o, 0) for o in OUT_ORDER]) / n, n


def S_stat(counts_by_label, pref, preps, w):
    lab16 = list(itertools.product(PAULIS, repeat=2))
    d, nn = {}, {}
    for bit in (0, 1):
        d[bit], nn[bit] = pool(counts_by_label,
                               [f"{pref}({a},{b})b{bit}{p}" for a, b in lab16
                                for p in preps])
    S = float(w @ (d[0] - d[1]))
    var = sum(w[o] ** 2 * (d[0][o] * (1 - d[0][o]) / nn[0]
                           + d[1][o] * (1 - d[1][o]) / nn[1]) for o in range(4))
    return S, float(np.sqrt(var)), d


def main():
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    res = job.result()
    metas = man["metas"]
    assert len(res) == len(metas), (len(res), len(metas))
    counts = {}
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            list(pub.data.values())[0].get_counts()
        counts[meta["label"]] = c

    G = man["gates"]
    w_sw = np.array(man["filters_tc_order"]["w_sw"])
    w_pa = np.array(man["filters_tc_order"]["w_pa"])

    S = {}
    S["switch"] = S_stat(counts, "sw", [""], w_sw)
    S["paths"] = S_stat(counts, "pa", [""], w_pa)
    S["sw_mix"] = S_stat(counts, "sm", ["p0", "p1"], w_sw)
    S["paths_mix"] = S_stat(counts, "pm", ["p0", "p1"], w_pa)

    # G2: null integrity, unconditioned D (Exp106 convention): target Z signal by input
    lab16 = list(itertools.product(PAULIS, repeat=2))
    dz, dvar = [], []
    for bit in (0, 1):
        p, n = pool(counts, [f"nu({a},{b})b{bit}" for a, b in lab16])
        z = (p[0] + p[1]) - (p[2] + p[3])   # P(t=0) - P(t=1)
        dz.append(z)
        dvar.append((1 - z * z) / n)
    D_null = (dz[0] - dz[1]) / 2
    D_se = float(np.sqrt((dvar[0] + dvar[1]) / 4))

    # G1: sentinel DISC per replicate: <X_c>_comm - <X_c>_anti
    disc = {}
    for rep in ("start", "mid", "end"):
        xs = {}
        for kind in ("comm", "anti"):
            c = counts[f"sent_{rep}_{kind}"]
            n = sum(c.values())
            xs[kind] = (sum(v for k, v in c.items() if k[1] == "0")
                        - sum(v for k, v in c.items() if k[1] == "1")) / n
        disc[rep] = xs["comm"] - xs["anti"]

    g1 = min(disc.values()) >= G["G1_sent_min_disc"]
    g2 = abs(D_null) + 5 * D_se < G["G2_null_D_band"]
    g3 = (abs(S["sw_mix"][0]) + 5 * S["sw_mix"][1] < G["G3_mix_band"] and
          abs(S["paths_mix"][0]) + 5 * S["paths_mix"][1] < G["G3_mix_band"])
    g4 = S["switch"][0] - 5 * S["switch"][1] > G["G4_switch_floor"]
    g5 = S["paths"][0] - 5 * S["paths"][1] > G["G5_paths_floor"]
    diff = S["switch"][0] - S["paths"][0]
    se_diff = float(np.hypot(S["switch"][1], S["paths"][1]))
    g6 = diff - 5 * se_diff > G["G6_diff_floor"]
    no_test = not (g1 and g2 and g3)
    ratio = S["switch"][0] / S["paths"][0] if S["paths"][0] > 0 else float("inf")

    out = {"S": {k: {"S": v[0], "SE": v[1]} for k, v in S.items()},
           "D_null": D_null, "D_se": D_se, "sentinel_disc": disc,
           "gates": {"G1": bool(g1), "G2": bool(g2), "G3": bool(g3),
                     "G4": bool(g4), "G5": bool(g5), "G6": bool(g6)},
           "verdict": ("NO-TEST" if no_test else
                       {"G4": "WIN" if g4 else "LOSS",
                        "G5": "WIN" if g5 else "LOSS",
                        "G6": "PASS" if g6 else "FAIL"}),
           "S_ratio": ratio, "S_diff": diff, "S_diff_se": se_diff,
           "prefiled": man["prefiled"]}
    print(f"=== Exp111 GRADE (job {man['job_id']}, pair {man['pair']}) ===")
    for k, v in S.items():
        print(f"  {k:10s} S={v[0]:+.5f}±{v[1]:.5f}  (S-5SE={v[0]-5*v[1]:+.4f})")
    print(f"  D_null={D_null:+.5f}±{D_se:.5f} | sentinels DISC {disc}")
    print(f"  gates: {out['gates']}")
    print(f"  S_ratio = {ratio:.3f} (pre-filed {man['prefiled']['S_ratio']}) | "
          f"S_diff = {diff:.4f}±{se_diff:.4f}")
    print(f"  VERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp111_grade.json"),
                        "w"), indent=1, default=float)
    print("wrote results/exp111_grade.json")


if __name__ == "__main__":
    main()
