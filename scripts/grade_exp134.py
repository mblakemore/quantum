#!/usr/bin/env python3
"""grade_exp134.py — Exp134 HLF NISQ-boundary ladder grading (Whisper C4675).
Locates n* where routing overhead drops the constant-logical-depth solver
below the majority / floor lines."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp134_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    rungs, sents = [], []
    for pub, meta in zip(res, man["metas"]):
        c = pub.data.c.get_counts()
        tot = sum(c.values())
        if meta.get("kind") == "sentinel":
            key = ("1" * meta["n"]) if meta["ones"] else ("0" * meta["n"])
            sents.append(c.get(key, 0) / tot)
            continue
        valid = set(tuple(z) for z in meta["valid_z"])
        good = sum(v for k, v in c.items()
                   if tuple(int(ch) for ch in k[::-1]) in valid)
        p = good / tot
        se = float(np.sqrt(max(p * (1 - p), 1e-9) / tot))
        rungs.append({"grid": meta["grid"], "n": meta["n"],
                      "floor": meta["floor"], "routed_2q": meta["routed_2q"],
                      "cz_layers_logical": meta["cz_layers_logical"],
                      "hw_depth": meta["hw_depth"], "P_valid": p, "se": se,
                      "sigma_over_floor": (p - meta["floor"]) / se,
                      "beats_floor": p > meta["floor"] + 5 * se,
                      "majority": p > 0.5 + 5 * se})
    nstar = next((r["n"] for r in rungs if not r["majority"]), None)
    nstar_floor = next((r["n"] for r in rungs if not r["beats_floor"]), None)
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "rungs": rungs,
           "n_star_majority": nstar, "n_star_floor": nstar_floor,
           "sentinels": sents,
           "gates": {"per_grid_beats_floor": [r["beats_floor"] for r in rungs],
                     "G_SENT": all(s >= 0.95 for s in sents)}}
    for r in rungs:
        print(f"n={r['n']} ({r['grid']}): P_valid={r['P_valid']:.4f}±{r['se']:.4f} "
              f"floor={r['floor']} ({r['sigma_over_floor']:.0f}σ) "
              f"routed2q={r['routed_2q']} depth={r['hw_depth']} | "
              f"beats_floor={r['beats_floor']} majority={r['majority']}")
    print(f"n* (majority lost) = {nstar} | n* (floor lost) = {nstar_floor}")
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp134_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp134_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
