#!/usr/bin/env python3
"""grade_exp137.py — Exp137 assemblage tomography -> rigorous 1SDI randomness
grading with bootstrap error bars (Whisper C4680)."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from exp137_assemblage_tomography_sim import (AXES, ns_violation,  # noqa:E402
                                              project_valid,
                                              reconstruct_assemblage,
                                              psd_violation)
from sdp_randomness import cjwr_S, guessing_probability, hmin  # noqa: E402
SIGN = {"X": 1, "Y": -1, "Z": 1}
DIRS = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
NBOOT = 40


def hmin_of_counts(counts):
    asm = project_valid(reconstruct_assemblage(counts))
    pg, _ = guessing_probability(asm, "Z")
    S3 = cjwr_S(asm, DIRS, signs=SIGN)
    return hmin(pg), S3, ns_violation(reconstruct_assemblage(counts))


def resample(counts, rng):
    out = {}
    for k, c in counts.items():
        labels = list(c.keys())
        p = np.array([c[l] for l in labels], float)
        n = int(p.sum())
        p = p / p.sum()
        draw = rng.multinomial(n, p)
        out[k] = {labels[i]: int(draw[i]) for i in range(len(labels))}
    return out


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp137_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    counts = {"main": {}, "null": {}}
    sents = []
    for pub, meta in zip(res, man["metas"]):
        c = pub.data.c.get_counts()
        if meta["kind"] == "sentinel":
            sents.append(c.get(meta["prep"], 0) / sum(c.values()))
            continue
        counts[meta["kind"]][(meta["x"], meta["t"])] = c

    hm, S3, nsv = hmin_of_counts(counts["main"])
    hmn, S3n, _ = hmin_of_counts(counts["null"])
    # bootstrap SE on main H_min
    rng = np.random.default_rng(4680)
    boot = []
    for _ in range(NBOOT):
        h, _, _ = hmin_of_counts(resample(counts["main"], rng))
        boot.append(h)
    se = float(np.std(boot))

    gates = {
        "W1_STEERABLE": S3 > 1,
        "W2_RIGOROUS_1SDI_RANDOMNESS": (hm - 5 * se) > 0,
        "W3_NULL": S3n <= 1,
        "G_PHYSICAL": nsv < 0.05,
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"),
           "H_min_bits": hm, "H_min_se_boot": se,
           "H_min_minus_5se": hm - 5 * se, "S3": S3, "S3_null": S3n,
           "H_min_null": hmn, "ns_violation": nsv,
           "sentinels": sents, "gates": gates,
           "scope": "RIGOROUS 1SDI randomness of Alice's outcome from measured "
                    "assemblage (no Werner model); one-sided trust (Bob), "
                    "locality open, crosstalk bounded"}
    print(f"RIGOROUS 1SDI H_min = {hm:.4f} +/- {se:.4f} bits/use "
          f"(H_min - 5SE = {hm-5*se:.4f})")
    print(f"recon S3 = {S3:.4f} | null S3 = {S3n:.4f} | NSviol = {nsv:.4f}")
    print("GATES:", gates)
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp137_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp137_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
