#!/usr/bin/env python3
"""grade_exp127hw.py — Exp127-HW 2D-HLF solver on silicon, frozen-gate grading
(Whisper C4674). Finding: experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp127hw_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    valid = set(tuple(z) for z in man["valid_z"])
    floor = man["uniform_floor"]

    # pub 0 = HLF solver; pubs 1,2 = sentinels 0000,1111
    cts = res[0].data.c.get_counts()
    tot = sum(cts.values())
    perz = {}
    good = 0
    for k, v in cts.items():
        z = tuple(int(c) for c in k[::-1])  # clbit order q0..q3
        perz[z] = perz.get(z, 0) + v
        if z in valid:
            good += v
    p_valid = good / tot
    se = float(np.sqrt(max(p_valid * (1 - p_valid), 1e-9) / tot))
    valid_probs = {z: perz.get(z, 0) / tot for z in valid}
    min_valid = min(valid_probs.values())

    sents = []
    for i, bits in enumerate(man["sentinel_order"], start=1):
        c = res[i].data.c.get_counts()
        sents.append(c.get(bits, 0) / sum(c.values()))

    gates = {
        "W1_SOLVER": p_valid > floor + 5 * se,
        "W2_MAJORITY": p_valid > 0.5 + 5 * se,
        "W3_COVERAGE": all(pp > 0.08 for pp in valid_probs.values()),
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "uniform_floor": floor,
           "P_valid": [p_valid, se],
           "sigma_over_floor": (p_valid - floor) / se,
           "valid_z_probs": {str(z): round(p, 4)
                             for z, p in valid_probs.items()},
           "min_valid_prob": min_valid,
           "routed_2q": man["routed_2q"], "hw_depth": man["hw_depth"],
           "sentinels": sents, "gates": gates}
    print(f"P_valid = {p_valid:.4f} ± {se:.4f}  (uniform floor {floor}) "
          f"= {(p_valid-floor)/se:.0f}σ over floor")
    print(f"valid_z coverage: { {str(z): round(p,4) for z,p in valid_probs.items()} }"
          f"  min={min_valid:.4f}")
    print(f"routed 2q={man['routed_2q']} depth={man['hw_depth']}")
    print("GATES:", gates)
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp127hw_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp127hw_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
