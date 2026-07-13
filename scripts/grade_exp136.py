#!/usr/bin/env python3
"""grade_exp136.py — Exp136 one-sided-DI steering grading (Whisper C4677).
Prereg: experiments/exp136-steering-preregistration.md"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp136_steering_sim import AXES, FUNC_SIGN  # noqa: E402
QMAX = math.sqrt(3)


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp136_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    E = {"main": {}, "null": {}}
    Ese = {"main": {}, "null": {}}
    sents = []
    for pub, meta in zip(res, man["metas"]):
        c = pub.data.c.get_counts()
        if meta["kind"] == "sentinel":
            sents.append(c.get(meta["prep"], 0) / sum(c.values()))
            continue
        tot = sum(c.values())
        e = sum((1 if k.count("1") % 2 == 0 else -1) * v
                for k, v in c.items()) / tot
        E[meta["kind"]][meta["axis"]] = e
        Ese[meta["kind"]][meta["axis"]] = float(np.sqrt(1.0 / tot))

    def S3(arm):
        s = abs(sum(FUNC_SIGN[a] * E[arm][a] for a in AXES)) / QMAX
        se = float(np.sqrt(sum(Ese[arm][a] ** 2 for a in AXES)) / QMAX)
        return s, se
    S, seS = S3("main")
    Sn, seSn = S3("null")
    gates = {
        "W1_STEERING_ONE_SIDED_DI": S > 1 + 5 * seS,
        "W2_QUANTUM_BOUND": S <= QMAX + 5 * seS,
        "W3_FAKING_FLOOR": Sn <= 1,
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "lhs_bound": 1.0,
           "quantum_max": QMAX, "S3": [S, seS], "S3_null": [Sn, seSn],
           "corrs_main": E["main"], "corrs_null": E["null"],
           "sigma_over_lhs": (S - 1) / seS, "sentinels": sents,
           "scope": "one-sided-DI under Bob-measurement-trust; Alice black-box; "
                    "locality loophole open, crosstalk loophole bounded (~1% << 0.67 faking excess)",
           "gates": gates}
    print(f"S3 = {S:.4f} ± {seS:.4f}  (LHS 1.0, quantum max {QMAX:.4f}) "
          f"= {(S-1)/seS:.0f}σ over LHS")
    print(f"S3_null = {Sn:.4f} ± {seSn:.4f} (measured separable faking floor)")
    print("corrs main:", {k: round(v, 3) for k, v in E["main"].items()})
    print("GATES:", gates)
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp136_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp136_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
