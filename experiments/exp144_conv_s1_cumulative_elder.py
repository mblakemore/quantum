#!/usr/bin/env python3
"""Exp144 conv stage-1 CUMULATIVE decode through wave W (Elder).

Accumulates even-parity evidence per row across all flown waves (wave-1 = all
3^n rows @60 shots; wave-k>1 = only that wave's alive_rows_in @60 shots each),
re-fits the empirical two-cluster (p_cons/p_anti) on the accumulated per-row
rates, and re-runs SPRT (frozen alpha=.05/beta=.01) with each row's OWN
accumulated shot count. Seed-blind by full-weight construction (observable =
product of all n bits). Row-indexed verdicts committed for 2-of-2.
"""
import glob, json, math, os, re, sys
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA, BETA = 0.05, 0.01
N, MAXW = 4, 2                          # rung, highest wave to fold in
svc = QiskitRuntimeService()

def even_parity_sum(bitstrings, n):
    """(sum of +1/-1 even-parity outcomes, shots) for a chunk of shots."""
    s = 0
    for b in bitstrings:
        s += 1 - 2 * (b.count("1") % 2)
    return s, len(bitstrings)

out = {"decoder": "elder", "arm": "conv_stage1_cumulative", "through_wave": MAXW,
       "n": N, "instances": {}}
for k in (1, 2, 3, 4, 5):
    # ---- wave 1: all rows, 60 shots each ----
    m1 = json.load(open(f"../results/exp144_conv_n{N}_k{k}_w1_a2_manifest.json"))
    res1 = svc.job(m1["job_id"]).result()
    acc = {}          # row_idx -> [sum, shots]
    ri = 0
    for pub in res1[1:-1]:
        d = pub.data
        reg = getattr(d, "c", None) or getattr(d, "meas", None)
        arr = reg.get_bitstrings()
        per = reg.num_shots or len(arr)
        for i in range(len(arr) // per):
            s, sh = even_parity_sum(arr[i*per:(i+1)*per], N)
            acc[ri] = [s, sh]; ri += 1
    nrows = ri
    # ---- waves 2..MAXW: only alive_rows_in, add shots ----
    for w in range(2, MAXW + 1):
        mf = f"../results/exp144_conv_n{N}_k{k}_w{w}_manifest.json"
        if not os.path.exists(mf):
            continue
        mw = json.load(open(mf))
        alive_in = mw["alive_rows_in"]
        resw = svc.job(mw["job_id"]).result()
        rows_w = []
        for pub in resw[1:-1]:
            d = pub.data
            reg = getattr(d, "c", None) or getattr(d, "meas", None)
            arr = reg.get_bitstrings()
            per = reg.num_shots or len(arr)
            for i in range(len(arr) // per):
                rows_w.append(even_parity_sum(arr[i*per:(i+1)*per], N))
        assert len(rows_w) == len(alive_in), f"k{k} w{w}: {len(rows_w)} vs {len(alive_in)}"
        for ridx, (s, sh) in zip(alive_in, rows_w):
            acc[ridx][0] += s; acc[ridx][1] += sh
    # ---- re-fit two clusters on accumulated per-row rates ----
    rates = np.array([(1 + acc[i][0] / acc[i][1]) / 2 for i in range(nrows)])
    hi = rates[rates > 0.65]; lo = rates[rates <= 0.65]
    p1 = float(np.median(hi)) if len(hi) else 0.75
    p0 = float(np.median(lo)) if len(lo) else 0.48
    A = math.log((1 - BETA) / ALPHA); B = math.log(BETA / (1 - ALPHA))
    lpos, lneg = math.log(p1/p0), math.log((1-p1)/(1-p0))
    v = {"CONSERVED": [], "REJECTED": [], "ALIVE": []}
    for i in range(nrows):
        r, sh = rates[i], acc[i][1]
        llr = r * sh * lpos + (1 - r) * sh * lneg
        v["CONSERVED" if llr >= A else ("REJECTED" if llr <= B else "ALIVE")].append(i)
    out["instances"][f"n{N}_k{k}"] = {
        "p1_measured": round(p1, 3), "p0_measured": round(p0, 3),
        "conserved_rows": v["CONSERVED"], "alive_rows": v["ALIVE"],
        "n_conserved": len(v["CONSERVED"]), "n_rejected": len(v["REJECTED"]),
        "n_alive": len(v["ALIVE"]),
        "shots_max": max(acc[i][1] for i in range(nrows))}
    print(f"n{N} k{k}: CONS {len(v['CONSERVED'])} | REJ {len(v['REJECTED'])} | "
          f"ALIVE {len(v['ALIVE'])} (p1={p1:.3f} p0={p0:.3f}, max shots {out['instances'][f'n{N}_k{k}']['shots_max']})")

tc = sum(x["n_conserved"] for x in out["instances"].values())
ta = sum(x["n_alive"] for x in out["instances"].values())
print(f"TOTALS through w{MAXW}: conserved {[out['instances'][f'n{N}_k{k}']['n_conserved'] for k in range(1,6)]} = {tc} | ALIVE {ta}")
fn = f"../results/exp144_conv_s1_n{N}_cumulative_w{MAXW}_elder.json"
json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
import hashlib
print("->", fn, "sha", hashlib.sha256(open(fn,'rb').read()).hexdigest()[:12])
