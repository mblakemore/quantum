#!/usr/bin/env python3
"""grade_exp129.py — Exp129 GHZ-vs-SQL frozen-gate grading (Whisper C4668).
Prereg: experiments/exp129-ghz-sql-preregistration.md
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp129_ghz_sql_sim import fourier_vis, freq_fit, p0  # noqa: E402


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp129_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    ghz = [None] * 12
    sep = [None] * 12
    sents = []
    for pub, meta in zip(res, man["metas"]):
        counts = pub.data.c.get_counts()
        if meta["kind"] == "ghz":
            ghz[meta["j"]] = p0(counts)
        elif meta["kind"] == "sep":
            sep[meta["j"]] = [p0(counts, i) for i in range(3)]
        else:
            tot = sum(counts.values())
            sents.append(counts.get(meta["prep"], 0) / tot)

    ps, ses = zip(*ghz)
    V3, seV3 = fourier_vis(ps, ses, 3)
    k0, amps = freq_fit(ps)
    v1s = []
    for i in range(3):
        pi = [pt[i][0] for pt in sep]
        si = [pt[i][1] for pt in sep]
        v1s.append(fourier_vis(pi, si, 1))
    V1 = float(np.mean([v[0] for v in v1s]))
    seV1 = float(np.sqrt(np.sum([v[1] ** 2 for v in v1s])) / 3)
    F_ghz, F_sep = 9 * V3 ** 2, 3 * V1 ** 2
    seF_ghz, seF_sep = 18 * V3 * seV3, 6 * V1 * seV1
    R = F_ghz / F_sep
    seR = R * np.sqrt((seF_ghz / F_ghz) ** 2 + (seF_sep / F_sep) ** 2)
    amp3 = amps[2]
    amp_next = max(a for i, a in enumerate(amps) if i != 2)
    freq_ratio = amp3 / max(amp_next, 1e-9)

    gates = {"W1_HEISENBERG": R > 1 + 5 * seR,
             "W2_SQL_ABS": F_ghz > 3 + 5 * seF_ghz,
             "G_FREQ": (k0 == 3) and (freq_ratio > 2),
             "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "V3": [V3, seV3], "V1": [V1, seV1],
           "F_ghz": [F_ghz, seF_ghz], "F_sep": [F_sep, seF_sep],
           "ratio": [float(R), float(seR)], "freq_peak": k0,
           "freq_ratio": float(freq_ratio), "dft_amps": amps,
           "sentinels": sents, "ghz_curve": [list(x) for x in ghz],
           "gates": {k: bool(v) for k, v in gates.items()},
           "sigma": {"W1": (R - 1) / seR, "W2": (F_ghz - 3) / seF_ghz,
                     "V3_over_SQLthresh": (V3 - 1 / np.sqrt(3)) / seV3}}
    print(f"V3={V3:.4f}±{seV3:.4f} V1={V1:.4f}±{seV1:.4f}")
    print(f"F_ghz={F_ghz:.3f}±{seF_ghz:.3f} F_sep={F_sep:.3f}±{seF_sep:.3f}")
    print(f"R={R:.3f}±{seR:.3f} freq_peak={k0} freq_ratio={freq_ratio:.1f}")
    print("GATES:", out["gates"])
    print("SIGMA:", {k: round(v, 1) for k, v in out["sigma"].items()})
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp129_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp129_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
