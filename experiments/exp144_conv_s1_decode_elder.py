#!/usr/bin/env python3
"""Exp144 A2 conv STAGE-1 blind decode — Elder (C6530).

Blind by construction: every candidate is FULL-WEIGHT, so the conservation
observable is the product of ALL n classical bits — no knowledge of the sealed
sweep order needed. Verdicts are PER ROW-INDEX; only the sealed per-rung seed
maps rows to candidates (Ember at build time, everyone at reveal).

Per row: SPRT (A2-rev1: alpha=0.05 anticommuter-pass, beta=0.01 conserved-kill)
between H_cons: mean = att and H_anti: mean = att*cos(0.6), att estimated
per-instance from the top cluster of row means (the conserved cluster is a
direct measurement of att — no assumed constant; C4790 rule).
Outputs per (n,k): CONSERVED / REJECTED / ALIVE row lists + per-row cumulative
shots, committed for 2-of-2 and for Ember's wave-2/stage-2 build.
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qiskit_ibm_runtime import QiskitRuntimeService
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'scripts'))
from ibm_multi_account import multi_account_service  # C6578: sweep ALL accounts, not the default one

ALPHA, BETA = 0.05, 0.01
OUT = os.path.join(HERE, "..", "results", "exp144_conv_s1_w1_verdicts_elder.json")


def row_outcomes(bitstrings, n):
    """Product of ALL n bits per shot (full-weight conservation observable)."""
    out = []
    for s in bitstrings:
        b = s[::-1]
        v = 1
        for i in range(n):
            v *= (1 - 2 * int(b[i]))
        out.append(v)
    return out


def sprt_verdict(outcomes, att):
    p1 = (1 + att) / 2                       # conserved
    p0 = (1 + att * math.cos(0.6)) / 2       # worst anticommuter
    A = math.log((1 - BETA) / ALPHA)
    B = math.log(BETA / (1 - ALPHA))
    llr = 0.0
    for x in outcomes:
        llr += math.log(p1 / p0) if x > 0 else math.log((1 - p1) / (1 - p0))
    if llr >= A:
        return "CONSERVED", llr
    if llr <= B:
        return "REJECTED", llr
    return "ALIVE", llr


def main():
    svc = multi_account_service()
    out = {"decoder": "elder", "arm": "conv_stage1", "wave": 1, "schedule": "A2-rev1",
           "instances": {}}
    for mf in sorted(glob.glob(os.path.join(HERE, "..", "results",
                                            "exp144_conv_n*_w1_a2_manifest.json"))):
        m = json.load(open(mf))
        fm = re.search(r"_n(\d+)_k(\d+)_", os.path.basename(mf))
        n, k = int(fm.group(1)), int(fm.group(2))
        res = svc.job(m["job_id"]).result()
        # pubs: sentinel, conv chunks..., sentinel — conv chunks are 1..-2
        row_means, row_outs = [], []
        for pub in res[1:-1]:
            d = pub.data
            reg = getattr(d, "c", None) or getattr(d, "meas", None)
            arr = reg.get_bitstrings()
            nrows = reg.num_shots and (len(arr) // reg.num_shots) or 1
            per = reg.num_shots or len(arr)
            nrows = len(arr) // per
            for i in range(nrows):
                outs = row_outcomes(arr[i * per:(i + 1) * per], n)
                row_outs.append(outs)
                row_means.append(float(np.mean(outs)))
        # att = median of the top-decile cluster (conserved rows measure att)
        top = sorted(row_means)[-max(3, len(row_means) // 8):]
        att = float(np.median(top))
        verdicts = {"CONSERVED": [], "REJECTED": [], "ALIVE": []}
        for i, outs in enumerate(row_outs):
            v, llr = sprt_verdict(outs, att)
            verdicts[v].append(i)
        out["instances"][f"n{n}_k{k}"] = {
            "att_measured": round(att, 4),
            "rows": len(row_outs), "shots_per_row": per,
            "conserved_rows": verdicts["CONSERVED"],
            "alive_rows": verdicts["ALIVE"],
            "n_rejected": len(verdicts["REJECTED"]),
            "mean_row_mean": round(float(np.mean(row_means)), 4)}
        print(f"n={n} k={k}: rows {len(row_outs)} att={att:.3f} -> "
              f"CONSERVED {len(verdicts['CONSERVED'])} | ALIVE {len(verdicts['ALIVE'])}"
              f" | REJECTED {len(verdicts['REJECTED'])}")
    with open(os.path.abspath(OUT), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("->", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
