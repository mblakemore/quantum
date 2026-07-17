#!/usr/bin/env python3
"""Exp144 conv stage-1 INCREMENTAL SPRT decode (Elder — 2-of-2 reconcile fix).

Sequential-SPRT-correct: wave-1 CONSERVED/REJECTED verdicts are FINAL (an SPRT
that has crossed a boundary stops and decides — it does not un-decide). Only
wave-1 ALIVE rows accumulate wave-2 shots and are re-tested, holding the wave-1
cluster fit (p1=att is a physical per-instance constant). This replaces the
cumulative-refit consumer, which wrongly re-classified already-decided rows and
diverged from Whisper C4797 (my bug, caught by 2-of-2 — cf. the wave-1 v1
att-estimator bug).
"""
import json, math, os
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

ALPHA, BETA = 0.05, 0.01
N = 4
svc = QiskitRuntimeService()
A = math.log((1 - BETA) / ALPHA); B = math.log(BETA / (1 - ALPHA))

def rows_even_parity(job_id):
    res = svc.job(job_id).result()
    out = []
    for pub in res[1:-1]:
        d = pub.data
        reg = getattr(d, "c", None) or getattr(d, "meas", None)
        arr = reg.get_bitstrings()
        per = reg.num_shots or len(arr)
        for i in range(len(arr) // per):
            chunk = arr[i*per:(i+1)*per]
            s = sum(1 - 2 * (b.count("1") % 2) for b in chunk)
            out.append([s, len(chunk)])
    return out

out = {"decoder": "elder", "arm": "conv_stage1_incremental", "through_wave": 2,
       "n": N, "instances": {}}
for k in (1, 2, 3, 4, 5):
    # ---- wave 1: all rows, fit clusters, classify ----
    m1 = json.load(open(f"../results/exp144_conv_n{N}_k{k}_w1_a2_manifest.json"))
    acc = rows_even_parity(m1["job_id"])           # [sum, shots] per row, 60 shots
    nrows = len(acc)
    # R1 (chair C4800): FREEZE p0/p1 at the COMMITTED wave-1 per-instance values.
    # No re-estimation on later waves — constants must not drift with the data they gate.
    _w1 = json.load(open("../results/exp144_conv_s1_w1_verdicts_elder_v2.json"))["instances"][f"n{N}_k{k}"]
    p1 = float(_w1["p1_measured"]); p0 = float(_w1["p0_measured"])
    lpos, lneg = math.log(p1 / p0), math.log((1 - p1) / (1 - p0))
    def verdict(sum_e, shots):
        r = (1 + sum_e / shots) / 2
        llr = r * shots * lpos + (1 - r) * shots * lneg
        return "CONSERVED" if llr >= A else ("REJECTED" if llr <= B else "ALIVE")
    state = {i: verdict(acc[i][0], acc[i][1]) for i in range(nrows)}   # wave-1 verdicts
    # ---- wave 2: fold onto ALIVE rows only, re-test (verdicts are sticky) ----
    mw = json.load(open(f"../results/exp144_conv_n{N}_k{k}_w2_manifest.json"))
    w2 = rows_even_parity(mw["job_id"])
    assert len(w2) == len(mw["alive_rows_in"])
    w1_disagree = []   # rows Whisper re-flew (her wave-1 ALIVE) that my wave-1 decided
    for ridx, (s2, sh2) in zip(mw["alive_rows_in"], w2):
        if state[ridx] != "ALIVE":
            w1_disagree.append((ridx, state[ridx]))   # my wave-1 verdict != her ALIVE
        acc[ridx][0] += s2; acc[ridx][1] += sh2
        state[ridx] = verdict(acc[ridx][0], acc[ridx][1])
    cons = sorted(i for i in state if state[i] == "CONSERVED")
    alive = sorted(i for i in state if state[i] == "ALIVE")
    rej = sum(1 for i in state if state[i] == "REJECTED")
    out["instances"][f"n{N}_k{k}"] = {
        "p1_measured": round(p1, 3), "p0": p0,
        "conserved_rows": cons, "alive_rows": alive,
        "n_conserved": len(cons), "n_rejected": rej, "n_alive": len(alive),
        "wave1_verdict_disagreements": w1_disagree}
    print(f"n{N} k{k}: CONS {len(cons)} {cons} | REJ {rej} | ALIVE {len(alive)} (p1={p1:.3f})")

tc = [out["instances"][f"n{N}_k{k}"]["n_conserved"] for k in range(1, 6)]
ta = sum(out["instances"][f"n{N}_k{k}"]["n_alive"] for k in range(1, 6))
print(f"TOTALS: conserved {tc} = {sum(tc)} | ALIVE {ta}")
fn = f"../results/exp144_conv_s1_n{N}_incremental_w2_elder.json"
json.dump(out, open(fn, "w"), indent=1, sort_keys=True)
import hashlib
print("->", fn, "sha", hashlib.sha256(open(fn,'rb').read()).hexdigest()[:12])
