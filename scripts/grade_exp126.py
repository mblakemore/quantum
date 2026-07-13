#!/usr/bin/env python3
"""grade_exp126.py — Exp126 magic-square game, frozen-gate grading
(Whisper C4666). Prereg: experiments/exp126-magic-square-preregistration.md
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp126_magic_square_sim import grade  # noqa: E402

CEIL = 8.0 / 9.0


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp126_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    job = svc.job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "classical_bound": CEIL, "contexts": {}}
    pooled = {"main": [], "null": []}
    sent_ok = []
    for pub, meta in zip(res, man["metas"]):
        counts = pub.data.c.get_counts()
        kind = meta["kind"]
        if kind == "sentinel":
            tot = sum(counts.values())
            hit = counts.get(meta["prep"], 0)
            integ = hit / tot
            sent_ok.append(integ)
            out["contexts"][meta["label"]] = {"integrity": integ}
            continue
        p, se = grade(counts, meta["r"], meta["c"])
        out["contexts"][meta["label"]] = {"p": p, "se": se,
                                          "twoq": meta["twoq"]}
        pooled[kind].append((p, se, meta["shots"]))

    def pool(entries):
        tot = sum(s for _, _, s in entries)
        p = sum(pp * s for pp, _, s in entries) / tot
        se = float(np.sqrt(max(p * (1 - p), 1e-9) / tot))
        return p, se

    p_main, se_main = pool(pooled["main"])
    p_null, se_null = pool(pooled["null"])
    mains = [(k, v["p"], v["se"]) for k, v in out["contexts"].items()
             if k.startswith("main_")]
    kmin, pmin, semin = min(mains, key=lambda t: t[1])

    w1 = p_main > CEIL + 5 * se_main
    w2 = pmin > CEIL + 5 * semin
    gnull = p_null < CEIL
    gsent = all(s >= 0.95 for s in sent_ok)
    out["pooled"] = {"main": [p_main, se_main], "null": [p_null, se_null],
                     "min_context": [kmin, pmin, semin]}
    out["gates"] = {"W1_GAME": bool(w1), "W2_MIN": bool(w2),
                    "G_NULL": bool(gnull), "G_SENT": bool(gsent)}
    out["sigma_clearance"] = {
        "W1": (p_main - CEIL) / se_main,
        "W2": (pmin - CEIL) / semin,
        "null_below": (CEIL - p_null) / se_null}
    print(json.dumps(out["pooled"], indent=1))
    print("GATES:", out["gates"])
    print("SIGMA:", {k: round(v, 1) for k, v in out["sigma_clearance"].items()})
    print("per-context main:",
          {k: round(v["p"], 4) for k, v in out["contexts"].items()
           if k.startswith("main_")})
    print("sentinels:", [round(s, 4) for s in sent_ok])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp126_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp126_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
