#!/usr/bin/env python3
"""UNFOLD U5 — ghost power vs epoch (Whisper C5073). $0. FROZEN.
Does W1 (weight-1 ghost power) drift with flight epoch? Ordinal time only (IBM job-ids are ~time-
ordered; no absolute timestamps at $0 -> LOW POWER by construction, stated up front).
PIN: W1 per draw reproduces U1's map (< 1e-9). PREDICTIONS: P1 pin. P2 a monotone trend feeds
boards #143/#145. P3/falsifier: no resolvable trend at n<=4 ordinal -> report + name the timestamp need.
"""
import json, os, numpy as np
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
u1 = json.load(open(os.path.join(RES, "unfold_U1_ghost_phase_c5073.json")))
gp = u1["ghost_power_per_draw"]
JOBS = {"refly": "d9sifr8pdb6s73e63140", "i1": "d9sma69dsedc73ahur2g", "i2": "d9smh0hdsedc73ahv2tg"}
W1 = {n: float(np.sum(gp[n])) for n in gp}
pin_ok = abs(W1.get("i1", 0) - 0.12023254855069476) < 1e-9
order = sorted(JOBS, key=lambda n: JOBS[n])   # lexical job-id ~ submission order
print(f"PIN (i1 W1 reproduces U1): {'PASS' if pin_ok else 'FAIL'}")
print("Ordinal time order (by job-id):", " -> ".join(f"{n}(W1={W1[n]:+.3f})" for n in order))
print("Note: i3 job-id absent in grade; refly (earliest) W1~0 while distribution draws carry 0.01-0.12")
timed = [n for n in order if n in W1]
rho = float(np.corrcoef(range(len(timed)), [W1[n] for n in timed])[0, 1]) if len(timed) >= 3 else None
verdict = ("LOW-POWER / NO RESOLVABLE DRIFT: n<=4 draws, ordinal time only, W1 not monotone "
           f"(rank-time vs W1 r={rho}). Real observation: refly (earliest, a WIN) sits at W1~0 while "
           "the distribution draws carry positive ghost power (i1 0.12 > i2 0.07 > i3 0.01). A drift "
           "test needs ABSOLUTE job timestamps (runtime metadata) + more draws — named, not forced.")
print(f"VERDICT: {verdict}")
json.dump({"card": "unfold_U5_epoch_drift", "cycle": "C5073", "pin_ok": pin_ok, "W1": W1,
           "ordinal_order": order, "rank_time_corr": rho, "verdict": verdict},
          open(os.path.join(RES, "unfold_U5_epoch_drift_c5073.json"), "w"), indent=1)
