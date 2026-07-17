#!/usr/bin/env python3
"""Exp144 conv stage-1 wave-3 decode (Elder) — folds the CO-BATCHED w3 job.

Sequential-SPRT decode of record (chair R1/R1b): frozen committed wave-1 p0/p1,
sticky verdicts, seed-blind. Waves 1-2 are per-k jobs; wave-3 is ONE co-batched
job (chair C4798): 15 pubs = 5 instances x [sentinel, conv_wave3, sentinel], so
instance i's conv pub is at result index 3*i+1, over its alive_rows_in.
"""
import json, math, hashlib
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA, BETA = 0.05, 0.01
N = 4
A = math.log((1 - BETA) / ALPHA); B = math.log(BETA / (1 - ALPHA))
svc = QiskitRuntimeService()
R = "../results"


def pub_rows(pub):
    d = pub.data
    reg = getattr(d, "c", None) or getattr(d, "meas", None)
    arr = reg.get_bitstrings()
    per = reg.num_shots or len(arr)
    return [[sum(1 - 2 * (b.count("1") % 2) for b in arr[i*per:(i+1)*per]),
             len(arr[i*per:(i+1)*per])] for i in range(len(arr) // per)]


def job_rows_perk(job_id):          # waves 1-2: skip leading/trailing sentinel
    res = svc.job(job_id).result()
    rows = []
    for pub in res[1:-1]:
        rows += pub_rows(pub)
    return rows


# co-batched wave-3 job, retrieved once
cb = json.load(open(f"{R}/exp144_conv_n{N}_w3_cobatch_manifest.json"))
w3res = svc.job(cb["job_id"]).result()
w3_by_k = {}
for i, inst in enumerate(cb["instances"]):
    conv_pub = w3res[3 * i + 1]                 # middle pub of the instance triple
    w3_by_k[inst["k"]] = (inst["alive_rows_in"], pub_rows(conv_pub))

out = {"decoder": "elder", "arm": "conv_stage1_sequential", "n": N,
       "through_wave": 3, "instances": {}}
for k in (1, 2, 3, 4, 5):
    w1c = json.load(open(f"{R}/exp144_conv_s1_w1_verdicts_elder_v2.json"))["instances"][f"n{N}_k{k}"]
    p1, p0 = float(w1c["p1_measured"]), float(w1c["p0_measured"])
    lpos, lneg = math.log(p1 / p0), math.log((1 - p1) / (1 - p0))

    def verdict(se, sh):
        r = (1 + se / sh) / 2
        llr = r * sh * lpos + (1 - r) * sh * lneg
        return "CONSERVED" if llr >= A else ("REJECTED" if llr <= B else "ALIVE")

    # wave 1
    acc = job_rows_perk(json.load(open(f"{R}/exp144_conv_n{N}_k{k}_w1_a2_manifest.json"))["job_id"])
    state = {i: verdict(acc[i][0], acc[i][1]) for i in range(len(acc))}
    # wave 2 (per-k)
    m2 = json.load(open(f"{R}/exp144_conv_n{N}_k{k}_w2_manifest.json"))
    r2 = job_rows_perk(m2["job_id"])
    for ridx, (s2, sh2) in zip(m2["alive_rows_in"], r2):
        acc[ridx][0] += s2; acc[ridx][1] += sh2
        if state[ridx] == "ALIVE":
            state[ridx] = verdict(acc[ridx][0], acc[ridx][1])
    # wave 3 (co-batched slice)
    alive_in, r3 = w3_by_k[k]
    assert len(r3) == len(alive_in), f"k{k} w3 {len(r3)} vs {len(alive_in)}"
    for ridx, (s3, sh3) in zip(alive_in, r3):
        acc[ridx][0] += s3; acc[ridx][1] += sh3
        if state[ridx] == "ALIVE":
            state[ridx] = verdict(acc[ridx][0], acc[ridx][1])

    cons = sorted(i for i in state if state[i] == "CONSERVED")
    alive = sorted(i for i in state if state[i] == "ALIVE")
    rej = sum(1 for i in state if state[i] == "REJECTED")
    out["instances"][f"n{N}_k{k}"] = {"conserved_rows": cons, "alive_rows": alive,
        "n_conserved": len(cons), "n_rejected": rej, "n_alive": len(alive)}
    tag = "CLOSED" if not alive else f"alive {alive}"
    print(f"n{N} k{k}: CONS {len(cons)} {cons} | REJ {rej} | {tag}")

tc = [out["instances"][f"n{N}_k{k}"]["n_conserved"] for k in range(1, 6)]
ta = sum(out["instances"][f"n{N}_k{k}"]["n_alive"] for k in range(1, 6))
print(f"THROUGH WAVE 3: conserved {tc} = {sum(tc)} | ALIVE {ta}")
fn = f"{R}/exp144_conv_s1_n{N}_seq_w3_elder.json"
json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
print("->", fn, "sha", hashlib.sha256(open(fn, "rb").read()).hexdigest()[:12])
