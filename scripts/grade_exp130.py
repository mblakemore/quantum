#!/usr/bin/env python3
"""grade_exp130.py — Exp130 GHZ Heisenberg-ladder grading (Whisper C4669).
Prereg: experiments/exp130-ghz-ladder-preregistration.md
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp130_ghz_ladder_sim import (LADDER, NMAX, fourier_vis,  # noqa: E402
                                   freq_scan, p0)


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp130_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    NP = 16
    sep = [[None] * NMAX for _ in range(NP)]
    ghz = {n: [None] * NP for n in LADDER}
    sents = []
    for pub, meta in zip(res, man["metas"]):
        counts = pub.data.c.get_counts()
        if meta["kind"] == "sep":
            sep[meta["j"]] = [p0(counts, i) for i in range(NMAX)]
        elif meta["kind"] == "ghz":
            ghz[meta["n"]][meta["j"]] = p0(counts)
        else:
            tot = sum(counts.values())
            sents.append(counts.get(meta["prep"], 0) / tot)

    V1 = []
    for i in range(NMAX):
        pi = [sep[j][i][0] for j in range(NP)]
        si = [sep[j][i][1] for j in range(NP)]
        V1.append(fourier_vis(pi, si, 1))

    rungs = {}
    for n in LADDER:
        ps, ses = zip(*ghz[n])
        VN, seVN = fourier_vis(ps, ses, n)
        k0, amps = freq_scan(ps)
        amp_n = amps[n - 1]
        amp_next = max(a for i, a in enumerate(amps) if i != n - 1)
        F_ghz = n ** 2 * VN ** 2
        seF_ghz = 2 * n ** 2 * VN * seVN
        F_sep = float(np.sum([V1[i][0] ** 2 for i in range(n)]))
        seF_sep = float(np.sqrt(np.sum(
            [(2 * V1[i][0] * V1[i][1]) ** 2 for i in range(n)])))
        R = F_ghz / F_sep
        seR = R * np.sqrt((seF_ghz / F_ghz) ** 2 + (seF_sep / F_sep) ** 2)
        rungs[n] = {"VN": [VN, seVN], "F_ghz": [F_ghz, seF_ghz],
                    "F_sep": [F_sep, seF_sep], "R": [R, seR], "R_ideal": n,
                    "freq_peak": k0, "freq_ratio": amp_n / max(amp_next, 1e-9),
                    "R_over_1_sigma": (R - 1) / seR}

    fg = {n: rungs[n]["F_ghz"][0] for n in LADDER}
    nstar = max(fg, key=fg.get)
    dF = rungs[5]["F_ghz"][0] - rungs[2]["F_ghz"][0]
    sedF = np.sqrt(rungs[5]["F_ghz"][1] ** 2 + rungs[2]["F_ghz"][1] ** 2)
    dR = rungs[5]["R"][0] - rungs[2]["R"][0]
    sedR = np.sqrt(rungs[5]["R"][1] ** 2 + rungs[2]["R"][1] ** 2)
    persists = (dF > 5 * sedF) and (dR > 5 * sedR)

    gates = {
        "W1_ADVANTAGE": all(rungs[n]["R_over_1_sigma"] > 5 for n in LADDER),
        "W2_SCALING": "PERSISTS" if persists else f"TURNOVER@N={nstar}",
        "G_FREQ": all(rungs[n]["freq_peak"] == n
                      and rungs[n]["freq_ratio"] > 2 for n in LADDER),
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "V1": V1, "rungs": rungs,
           "Fghz_argmax": nstar, "dF_5_2": [float(dF), float(sedF)],
           "dR_5_2": [float(dR), float(sedR)], "persists": bool(persists),
           "sentinels": sents, "gates": gates}
    print("V1:", [round(v[0], 4) for v in V1])
    for n in LADDER:
        r = rungs[n]
        print(f"N={n}: VN={r['VN'][0]:.4f} F_ghz={r['F_ghz'][0]:.2f} "
              f"R={r['R'][0]:.3f}(ideal {n}) k={r['freq_peak']} "
              f"Rsig={r['R_over_1_sigma']:.0f}")
    print(f"N*={nstar} | dF(5-2)={dF:.2f}±{sedF:.2f} "
          f"dR(5-2)={dR:.3f}±{sedR:.3f} | PERSISTS={persists}")
    print("GATES:", gates)
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp130_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp130_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
