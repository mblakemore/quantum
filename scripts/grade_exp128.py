#!/usr/bin/env python3
"""grade_exp128.py — Exp128 QRAC frozen-gate grading (Whisper C4667).
Prereg: experiments/exp128-qrac-preregistration.md
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CEIL = 0.75
Q_OPT = float(np.cos(np.pi / 8) ** 2)


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp128_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "classical_bound": CEIL, "quantum_optimum": Q_OPT, "cases": {}}
    mains, cls = [], []
    for pub, meta in zip(res, man["metas"]):
        counts = pub.data.c.get_counts()
        tot = sum(counts.values())
        if meta["kind"] == "main":
            target = (meta["x0"], meta["x1"])[meta["q"]]
        else:
            target = meta["x0"]
        hit = sum(v for k, v in counts.items() if int(k) == target)
        p = hit / tot
        se = float(np.sqrt(max(p * (1 - p), 1e-9) / tot))
        out["cases"][meta["label"]] = {"p": p, "se": se}
        (mains if meta["kind"] == "main" else cls).append((p, se, tot))

    tot = sum(t for _, _, t in mains)
    p_pool = sum(p * t for p, _, t in mains) / tot
    se_pool = float(np.sqrt(max(p_pool * (1 - p_pool), 1e-9) / tot))
    lab_min, case_min = min(
        ((k, v) for k, v in out["cases"].items() if k.startswith("main")),
        key=lambda kv: kv[1]["p"])
    p_class = (np.mean([p for p, _, _ in cls]) + 0.5) / 2
    sents = [p for p, _, _ in cls]

    gates = {"W1_QRAC": p_pool > CEIL + 5 * se_pool,
             "W2_MIN": case_min["p"] > CEIL + 5 * case_min["se"],
             "G_QBAND": p_pool <= Q_OPT + 5 * se_pool,
             "G_CLASS": p_class <= CEIL,
             "G_SENT": all(s >= 0.95 for s in sents)}
    out["pooled"] = {"main": [p_pool, se_pool],
                     "min_case": [lab_min, case_min["p"], case_min["se"]],
                     "class": p_class, "sentinels": sents}
    out["gates"] = {k: bool(v) for k, v in gates.items()}
    out["sigma"] = {"W1": (p_pool - CEIL) / se_pool,
                    "W2": (case_min["p"] - CEIL) / case_min["se"],
                    "below_qopt": (Q_OPT - p_pool) / se_pool}
    print(json.dumps(out["pooled"], indent=1, default=float))
    print("GATES:", out["gates"])
    print("SIGMA:", {k: round(v, 1) for k, v in out["sigma"].items()})
    print("cases:", {k: round(v["p"], 4) for k, v in out["cases"].items()})
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp128_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp128_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
