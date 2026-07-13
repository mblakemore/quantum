#!/usr/bin/env python3
"""grade_exp131.py — Exp131 optimal-cloning ceiling grading (Whisper C4670).
Prereg: experiments/exp131-cloning-preregistration.md
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CEIL = 5 / 6


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp131_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    perbasis = {"optimal": {}, "cheat": {}}
    sents = []
    for pub, meta in zip(res, man["metas"]):
        counts = pub.data.c.get_counts()
        tot = sum(counts.values())
        if meta["kind"] == "sentinel":
            sents.append(counts.get(meta["prep"], 0) / tot)
            continue
        exp = str(meta["expected"])
        fA = sum(v for k, v in counts.items() if k[::-1][0] == exp) / tot
        fB = sum(v for k, v in counts.items() if k[::-1][1] == exp) / tot
        perbasis[meta["kind"]].setdefault(meta["basis"], []).append(
            (fA + fB) / 2)

    def agg(arm):
        return {b: (float(np.mean(v)),
                    float(np.std(v) / np.sqrt(max(len(v), 1))))
                for b, v in perbasis[arm].items()}

    opt = agg("optimal")
    cheat = agg("cheat")
    opt_vals = [m for m, _ in opt.values()]
    cheat_vals = [m for m, _ in cheat.values()]
    opt_spread = max(opt_vals) - min(opt_vals)
    opt_mean = float(np.mean(opt_vals))
    opt_max = max(opt_vals)
    opt_max_se = [s for m, s in opt.values() if m == opt_max][0]
    cheat_spread = max(cheat_vals) - min(cheat_vals)
    cheat_min = min(cheat_vals)
    cheat_min_se = [s for m, s in cheat.values() if m == cheat_min][0]

    gates = {
        "W1_UNIVERSAL": (opt_spread < 0.05) and (opt_max <= CEIL + 5 * opt_max_se),
        "W2_NO_UNIVERSAL_BEAT": cheat_min < CEIL - 5 * cheat_min_se,
        "W3_CHEAT_TELL": (cheat_spread > 0.30) and (opt_spread < 0.05),
        "W4_CEILING_PROXIMITY": opt_mean > CEIL - 0.06,
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "ceiling": CEIL,
           "optimal_perbasis": opt, "cheat_perbasis": cheat,
           "opt_spread": opt_spread, "opt_mean": opt_mean, "opt_max": opt_max,
           "cheat_spread": cheat_spread, "cheat_min": cheat_min,
           "sentinels": sents, "gates": {k: bool(v) for k, v in gates.items()}}
    print(f"OPTIMAL per-basis: { {b: round(m, 4) for b, (m, _) in opt.items()} }"
          f" spread={opt_spread:.4f} mean={opt_mean:.4f} (5/6={CEIL:.4f})")
    print(f"CHEAT   per-basis: { {b: round(m, 4) for b, (m, _) in cheat.items()} }"
          f" spread={cheat_spread:.4f} min={cheat_min:.4f}")
    print("GATES:", out["gates"])
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp131_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp131_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
