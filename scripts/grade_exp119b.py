#!/usr/bin/env python3
"""grade_exp119b.py — Exp119b grader (Whisper C4641). FROZEN AT PREREG.
Prereg: experiments/exp119b-coherent-negative-energy-preregistration.md.
Upgrade over grade_exp119: exact SE propagation through the readout correction."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp119_qet_sim import C1, C2  # noqa: E402
from grade_exp119 import assign  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

NSIG = 5


def arm_stats(counts_zb, counts_xx, arm, F):
    def expec(c, which):
        n = t = 0
        for k, v in c.items():
            t += v
            if which == "zB":
                n += v * (1 - 2 * int(k[0]))
            elif which == "zA":
                n += v * (1 - 2 * int(k[1]))
            elif which == "xx":
                bA = int(k[1]) if arm == "ground" else int(k[2])
                n += v * (1 - 2 * int(k[0])) * (1 - 2 * bA)
        return n / t, t
    zB, nz = expec(counts_zb, "zB")
    xx, nx = expec(counts_xx, "xx")
    se_zB = np.sqrt((1 - zB * zB) / nz)
    se_xx = np.sqrt((1 - xx * xx) / nx)
    eb_raw = zB + 2 * xx + C1 + C2
    se_raw = float(np.hypot(se_zB, 2 * se_xx))
    vA = F["A"]["F0"] + F["A"]["F1"] - 1
    vB = F["B"]["F0"] + F["B"]["F1"] - 1
    zB_c = (zB - (F["B"]["F0"] - F["B"]["F1"])) / vB
    xx_c = xx / (vA * vB)
    eb_c = zB_c + 2 * xx_c + C1 + C2
    se_c = float(np.hypot(se_zB / vB, 2 * se_xx / (vA * vB)))
    ea = None
    if arm in ("ground", "fixp", "fixm"):
        zA, _ = expec(counts_zb, "zA")
        ea = zA + C1
    return {"E_B_raw": eb_raw, "SE_raw": se_raw, "E_B_corr": eb_c,
            "SE_corr": se_c, "E_A": ea, "zB": zB, "xx": xx}


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp119b_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    counts = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        counts[meta["label"]] = arr.get_counts()

    F = assign(counts["cal0"], counts["cal1"])
    arms = {a: arm_stats(counts[f"{a}_zb"], counts[f"{a}_xx"], a, F)
            for a in ("qet_def", "ground", "fixp", "fixm")}
    d, g = arms["qet_def"], arms["ground"]
    fix_raw = 0.5 * (arms["fixp"]["E_B_raw"] + arms["fixm"]["E_B_raw"])
    fix_se = 0.5 * float(np.hypot(arms["fixp"]["SE_raw"],
                                  arms["fixm"]["SE_raw"]))

    no_test = g["E_B_raw"] + NSIG * g["SE_raw"] < 0
    V1 = d["E_B_corr"] + NSIG * d["SE_corr"] < 0
    d2 = d["E_B_corr"] - g["E_B_corr"]
    se2 = float(np.hypot(d["SE_corr"], g["SE_corr"]))
    V2 = d2 + NSIG * se2 < 0
    d3 = d["E_B_raw"] - fix_raw
    se3 = float(np.hypot(d["SE_raw"], fix_se))
    V3 = d3 + NSIG * se3 < 0

    verdict = ("NO-TEST(ground-negative)" if no_test else
               "NEGATIVE-LOCAL-ENERGY-CERTIFIED(coherent)"
               if (V1 and V2 and V3) else "FAIL-CERTIFICATION")
    out = {"arms": arms, "fix_pooled_raw": [fix_raw, fix_se],
           "readout_assignment": F,
           "gates": {"G0_no_test": bool(no_test), "V1": bool(V1),
                     "V2": bool(V2), "V3": bool(V3)},
           "key_numbers": {
               "E_B_def_corrected": [d["E_B_corr"], d["SE_corr"]],
               "upper_bound_5sig": d["E_B_corr"] + NSIG * d["SE_corr"],
               "V2_diff": [d2, se2], "V3_diff": [d3, se3]},
           "verdict": verdict}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp119b_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
