#!/usr/bin/env python3
"""grade_exp132.py — Exp132 DFS-cloak 3-way race grading (Whisper C4671).
Prereg: experiments/exp132-dfs-cloak-preregistration.md
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp132_dfs_cloak_sim import (DELAYS_US, corr2, exp1,  # noqa: E402
                                  logical_coherence)


def corr_se(counts):
    tot = sum(counts.values())
    return float(np.sqrt(1.0 / tot))  # |parity|<=1, conservative binomial


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp132_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    log = {d: {} for d in DELAYS_US}
    logse = {d: {} for d in DELAYS_US}
    bare = {d: {} for d in DELAYS_US}
    barese = {d: {} for d in DELAYS_US}
    echo = {d: {} for d in DELAYS_US}
    echose = {d: {} for d in DELAYS_US}
    sents = []
    for pub, meta in zip(res, man["metas"]):
        c = pub.data.c.get_counts()
        if meta["kind"] == "sentinel":
            sents.append(c.get(meta["prep"], 0) / sum(c.values()))
            continue
        d, s = meta["delay"], meta["setting"]
        if meta["kind"] == "logical":
            log[d][s] = corr2(c)
            logse[d][s] = corr_se(c)
        elif meta["kind"] == "bare":
            bare[d][s] = exp1(c)
            barese[d][s] = corr_se(c)
        else:
            echo[d][s] = exp1(c)
            echose[d][s] = corr_se(c)

    def coh1(v, se):
        C = float(np.hypot(v["X"], v["Y"]))
        s = float(np.hypot(v["X"] * se["X"], v["Y"] * se["Y"]) / max(C, 1e-6))
        return C, s

    def cohL(v, se):
        C = logical_coherence(v)
        # propagate: X_L=(XX+YY)/2, Y_L=(XY-YX)/2, C=hypot
        XL, YL = (v["XX"] + v["YY"]) / 2, (v["XY"] - v["YX"]) / 2
        sXL = np.hypot(se["XX"], se["YY"]) / 2
        sYL = np.hypot(se["XY"], se["YX"]) / 2
        s = float(np.hypot(XL * sXL, YL * sYL) / max(C, 1e-6))
        return C, s

    curves = {"logical": [], "bare": [], "echo": []}
    ses = {"logical": [], "bare": [], "echo": []}
    for d in DELAYS_US:
        cL, sL = cohL(log[d], logse[d])
        cB, sB = coh1(bare[d], barese[d])
        cE, sE = coh1(echo[d], echose[d])
        curves["logical"].append(cL); ses["logical"].append(sL)
        curves["bare"].append(cB); ses["bare"].append(sB)
        curves["echo"].append(cE); ses["echo"].append(sE)

    def norm(arm):
        c0 = curves[arm][0]
        n = [c / c0 for c in curves[arm]]
        # normalized SE (ratio); ignore c0 error to first order (dominant term)
        ns = [ses[arm][i] / c0 for i in range(len(n))]
        return n, ns

    logN, logNse = norm("logical")
    bareN, bareNse = norm("bare")
    echoN, echoNse = norm("echo")

    def fit(n):
        xs = np.array(DELAYS_US, float)
        ys = np.array([max(v, 1e-3) for v in n])
        a, _ = np.polyfit(xs, np.log(ys), 1)
        return float(-1 / a) if a < 0 else float("inf")

    i = len(DELAYS_US) - 1  # d*
    echo_dfs = echoN[i] - logN[i]
    echo_dfs_se = float(np.hypot(echoNse[i], logNse[i]))
    echo_bare = echoN[i] - bareN[i]
    echo_bare_se = float(np.hypot(echoNse[i], bareNse[i]))
    dfs_bare = logN[i] - bareN[i]
    dfs_bare_se = float(np.hypot(logNse[i], bareNse[i]))
    t2 = {a: fit(norm(a)[0]) for a in ("logical", "bare", "echo")}

    W3 = ("CLOAK" if dfs_bare > 5 * dfs_bare_se else
          "NO_PASSIVE_PROTECTION" if dfs_bare < -5 * dfs_bare_se else
          "INCONCLUSIVE")
    W2 = ("ECHO_PROTECTS" if echo_bare > 0.05 + 5 * echo_bare_se else
          "MEMORYLESS" if echo_bare < 5 * echo_bare_se else "MARGINAL")
    gates = {
        "W1_ACTIVE_BEATS_PASSIVE": echo_dfs > 5 * echo_dfs_se,
        "W2_ECHO_PROTECTS": W2, "W3_DFS": W3,
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "delays_us": DELAYS_US,
           "curves": curves, "norm": {"logical": logN, "bare": bareN,
                                      "echo": echoN},
           "T2_us": t2,
           "dstar": {"echo_minus_dfs": [echo_dfs, echo_dfs_se],
                     "echo_minus_bare": [echo_bare, echo_bare_se],
                     "dfs_minus_bare": [dfs_bare, dfs_bare_se]},
           "T2_ratios": {"echo_over_bare": t2["echo"] / t2["bare"],
                         "dfs_over_bare": t2["logical"] / t2["bare"],
                         "fake_dfs_floor": 0.15},
           "sentinels": sents, "gates": gates}
    print(f"T2(us): {  {k: round(v,1) for k,v in t2.items()} }")
    print(f"norm@d*: echo={echoN[i]:.3f} bare={bareN[i]:.3f} dfs={logN[i]:.3f}")
    print(f"echo-dfs={echo_dfs:.3f}±{echo_dfs_se:.3f}  "
          f"echo-bare={echo_bare:.3f}±{echo_bare_se:.3f}  "
          f"dfs-bare={dfs_bare:.3f}±{dfs_bare_se:.3f}")
    print(f"T2 ratios: echo/bare={t2['echo']/t2['bare']:.2f} "
          f"dfs/bare={t2['logical']/t2['bare']:.3f} (fake floor 0.15)")
    print("GATES:", gates)
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp132_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp132_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
