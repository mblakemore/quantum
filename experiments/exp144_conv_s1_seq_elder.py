#!/usr/bin/env python3
"""Exp144 conv stage-1 SEQUENTIAL decode through all flown waves (Elder).

The decode-of-record protocol (chair R1/R1b, C4800/C4802), generalized to any
wave count:
  * p0/p1 FROZEN at the COMMITTED wave-1 per-instance values (no re-estimation).
  * Verdicts are STICKY: once a row is CONSERVED/REJECTED it stays; only ALIVE
    rows fold the next wave's shots and are re-tested (SPRT is sequential).
  * Seed-blind (observable = product of all n bits). Row-indexed, order-blind.
Auto-detects waves: folds exp144_conv_n{N}_k{K}_w{W}_manifest.json for W=2,3,...
(wave-1 = ..._w1_a2_manifest.json) until none remains. Run on each landing.
Usage: python3 exp144_conv_s1_seq_elder.py [N]   (default N=4)
"""
import json, math, os, sys, hashlib
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA, BETA = 0.05, 0.01
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
A = math.log((1 - BETA) / ALPHA); B = math.log(BETA / (1 - ALPHA))
svc = QiskitRuntimeService()
R = "../results"


def rows_even_parity(job_id):
    res = svc.job(job_id).result()
    out = []
    for pub in res[1:-1]:                       # skip sentinels
        d = pub.data
        reg = getattr(d, "c", None) or getattr(d, "meas", None)
        arr = reg.get_bitstrings()
        per = reg.num_shots or len(arr)
        for i in range(len(arr) // per):
            chunk = arr[i*per:(i+1)*per]
            out.append([sum(1 - 2 * (b.count("1") % 2) for b in chunk), len(chunk)])
    return out


out = {"decoder": "elder", "arm": "conv_stage1_sequential", "n": N, "instances": {}}
max_wave = 1
for k in (1, 2, 3, 4, 5):
    # FROZEN committed wave-1 constants
    w1c = json.load(open(f"{R}/exp144_conv_s1_w1_verdicts_elder_v2.json"))["instances"][f"n{N}_k{k}"]
    p1, p0 = float(w1c["p1_measured"]), float(w1c["p0_measured"])
    lpos, lneg = math.log(p1 / p0), math.log((1 - p1) / (1 - p0))

    def verdict(sum_e, shots):
        r = (1 + sum_e / shots) / 2
        llr = r * shots * lpos + (1 - r) * shots * lneg
        return "CONSERVED" if llr >= A else ("REJECTED" if llr <= B else "ALIVE")

    # wave 1 (all rows)
    m1 = json.load(open(f"{R}/exp144_conv_n{N}_k{k}_w1_a2_manifest.json"))
    acc = rows_even_parity(m1["job_id"])
    state = {i: verdict(acc[i][0], acc[i][1]) for i in range(len(acc))}
    # waves 2..: fold onto current ALIVE rows only
    w = 2
    while os.path.exists(f"{R}/exp144_conv_n{N}_k{k}_w{w}_manifest.json"):
        mw = json.load(open(f"{R}/exp144_conv_n{N}_k{k}_w{w}_manifest.json"))
        rw = rows_even_parity(mw["job_id"])
        assert len(rw) == len(mw["alive_rows_in"]), f"k{k} w{w} row count"
        for ridx, (s2, sh2) in zip(mw["alive_rows_in"], rw):
            # tolerate her-vs-my wave1 alive set: fold + (re)verdict regardless
            acc[ridx][0] += s2; acc[ridx][1] += sh2
            if state[ridx] == "ALIVE":
                state[ridx] = verdict(acc[ridx][0], acc[ridx][1])
        max_wave = max(max_wave, w); w += 1

    cons = sorted(i for i in state if state[i] == "CONSERVED")
    alive = sorted(i for i in state if state[i] == "ALIVE")
    rej = sum(1 for i in state if state[i] == "REJECTED")
    out["instances"][f"n{N}_k{k}"] = {
        "p1_frozen": p1, "p0_frozen": p0,
        "conserved_rows": cons, "alive_rows": alive,
        "n_conserved": len(cons), "n_rejected": rej, "n_alive": len(alive)}
    print(f"n{N} k{k}: CONS {len(cons)} {cons} | REJ {rej} | ALIVE {len(alive)} {alive}")

out["through_wave"] = max_wave
tc = [out["instances"][f"n{N}_k{k}"]["n_conserved"] for k in range(1, 6)]
ta = sum(out["instances"][f"n{N}_k{k}"]["n_alive"] for k in range(1, 6))
print(f"THROUGH WAVE {max_wave}: conserved {tc} = {sum(tc)} | ALIVE {ta}")
fn = f"{R}/exp144_conv_s1_n{N}_seq_w{max_wave}_elder.json"
json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
print("->", fn, "sha", hashlib.sha256(open(fn, "rb").read()).hexdigest()[:12])
