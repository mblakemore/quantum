#!/usr/bin/env python3
"""Exp144 conv stage-1 GENERAL sequential decode (Elder) — the decode of record.

Handles BOTH per-k waves (w1 a2, w2) and CO-BATCHED waves (w3, w4, ... — chair
C4798), with arbitrary instance subsets (closed instances drop out of later
co-batches). Protocol (chair R1/R1b): frozen committed wave-1 p0/p1, sticky
verdicts, sequential SPRT, seed-blind. Auto-detects waves; run on each landing.

Co-batch job layout: instances listed in order, each contributing n_pubs pubs
([sentinel, conv_wave, sentinel] -> conv at local index 1). Instance at list
position j starts at cumulative pub offset sum(n_pubs[:j]).
"""
import json, math, os, sys, hashlib
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA, BETA = 0.05, 0.01
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
A = math.log((1 - BETA) / ALPHA); B = math.log(BETA / (1 - ALPHA))
svc = QiskitRuntimeService()
R = "../results"
_jobcache = {}

def result(job_id):
    if job_id not in _jobcache:
        _jobcache[job_id] = svc.job(job_id).result()
    return _jobcache[job_id]

def pub_rows(pub):
    d = pub.data
    reg = getattr(d, "c", None) or getattr(d, "meas", None)
    arr = reg.get_bitstrings()
    per = reg.num_shots or len(arr)
    return [[sum(1 - 2 * (b.count("1") % 2) for b in arr[i*per:(i+1)*per]),
             len(arr[i*per:(i+1)*per])] for i in range(len(arr) // per)]

def perk_rows(job_id):                      # per-k job: skip leading/trailing sentinel
    res = result(job_id)
    out = []
    for pub in res[1:-1]:
        out += pub_rows(pub)
    return out

def cobatch_slice(W, k):
    """(alive_rows_in, rows) for instance k in co-batched wave W, or None."""
    mf = f"{R}/exp144_conv_n{N}_w{W}_cobatch_manifest.json"
    if not os.path.exists(mf):
        return None
    cb = json.load(open(mf))
    res = result(cb["job_id"])
    off = 0
    for inst in cb["instances"]:
        npub = inst.get("n_pubs", 3)
        if inst["k"] == k:
            return inst["alive_rows_in"], pub_rows(res[off + 1])   # conv = middle pub
        off += npub
    return ("_absent_", [])                 # instance closed / not in this co-batch

def perk_wave(W, k):
    mf = f"{R}/exp144_conv_n{N}_k{k}_w{W}_manifest.json"
    if not os.path.exists(mf):
        return None
    m = json.load(open(mf))
    return m["alive_rows_in"], perk_rows(m["job_id"])

out = {"decoder": "elder", "arm": "conv_stage1_general", "n": N, "instances": {}}
max_wave = 1
for k in (1, 2, 3, 4, 5):
    w1c = json.load(open(f"{R}/exp144_conv_s1_w1_verdicts_elder_v2.json"))["instances"][f"n{N}_k{k}"]
    p1, p0 = float(w1c["p1_measured"]), float(w1c["p0_measured"])
    lpos, lneg = math.log(p1 / p0), math.log((1 - p1) / (1 - p0))
    def verdict(se, sh):
        r = (1 + se / sh) / 2
        llr = r * sh * lpos + (1 - r) * sh * lneg
        return "CONSERVED" if llr >= A else ("REJECTED" if llr <= B else "ALIVE")
    # wave 1
    acc = perk_rows(json.load(open(f"{R}/exp144_conv_n{N}_k{k}_w1_a2_manifest.json"))["job_id"])
    state = {i: verdict(acc[i][0], acc[i][1]) for i in range(len(acc))}
    # waves 2..: per-k first, else co-batch; stop when neither exists
    W = 2
    while True:
        got = perk_wave(W, k)
        if got is None:
            got = cobatch_slice(W, k)
        if got is None:
            break
        alive_in, rows = got
        if alive_in != "_absent_":
            assert len(rows) == len(alive_in), f"k{k} w{W} {len(rows)} vs {len(alive_in)}"
            for ridx, (s, sh) in zip(alive_in, rows):
                acc[ridx][0] += s; acc[ridx][1] += sh
                if state[ridx] == "ALIVE":
                    state[ridx] = verdict(acc[ridx][0], acc[ridx][1])
        max_wave = max(max_wave, W); W += 1
    cons = sorted(i for i in state if state[i] == "CONSERVED")
    alive = sorted(i for i in state if state[i] == "ALIVE")
    rej = sum(1 for i in state if state[i] == "REJECTED")
    out["instances"][f"n{N}_k{k}"] = {"conserved_rows": cons, "alive_rows": alive,
        "n_conserved": len(cons), "n_rejected": rej, "n_alive": len(alive)}
    print(f"n{N} k{k}: CONS {len(cons)} {cons} | REJ {rej} | {'CLOSED' if not alive else 'alive '+str(alive)}")

out["through_wave"] = max_wave
tc = [out["instances"][f"n{N}_k{k}"]["n_conserved"] for k in range(1, 6)]
ta = sum(out["instances"][f"n{N}_k{k}"]["n_alive"] for k in range(1, 6))
print(f"THROUGH WAVE {max_wave}: conserved {tc} = {sum(tc)} | ALIVE {ta}")
fn = f"{R}/exp144_conv_s1_n{N}_general_w{max_wave}_elder.json"
json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
print("->", fn, "sha", hashlib.sha256(open(fn, "rb").read()).hexdigest()[:12])
