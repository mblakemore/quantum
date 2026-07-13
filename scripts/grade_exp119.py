#!/usr/bin/env python3
"""grade_exp119.py — Exp119 certified QET grader (Whisper C4639).
FROZEN AT PREREG. Mechanical; zero grading discretion.
Prereg: experiments/exp119-certified-qet-preregistration.md."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp119_qet_sim import counts_energy, C1, C2  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

NSIG = 5


def assign(counts_c0, counts_c1):
    """Per-qubit readout assignment from cal0/cal1 (clbits c1=A, c2=B)."""
    F = {}
    for q, pos in (("A", 1), ("B", 0)):     # key index: c2 c1 c0
        n0 = sum(v for k, v in counts_c0.items())
        g0 = sum(v for k, v in counts_c0.items() if k[pos] == "0")
        n1 = sum(v for v in counts_c1.values())
        g1 = sum(v for k, v in counts_c1.items() if k[pos] == "1")
        F[q] = {"F0": g0 / n0, "F1": g1 / n1}
    return F


def correct(zB, xx, zA, F):
    vA = F["A"]["F0"] + F["A"]["F1"] - 1
    vB = F["B"]["F0"] + F["B"]["F1"] - 1
    zB_c = (zB - (F["B"]["F0"] - F["B"]["F1"])) / vB
    zA_c = (zA - (F["A"]["F0"] - F["A"]["F1"])) / vA if zA is not None else None
    xx_c = xx / (vA * vB)
    return zB_c, xx_c, zA_c


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp119_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    counts = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        counts[meta["label"]] = arr.get_counts()

    F = assign(counts["cal0"], counts["cal1"])
    arms = {}
    for arm in ("ground", "qet_ff", "qet_def", "fixp", "fixm"):
        eb, se, ea = counts_energy(counts[f"{arm}_zb"], counts[f"{arm}_xx"],
                                   arm)
        # corrected variant (frozen procedure, prereg W2c)
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
            return n / t
        zB = expec(counts[f"{arm}_zb"], "zB")
        zA = expec(counts[f"{arm}_zb"], "zA") if arm != "qet_def" else None
        xx = expec(counts[f"{arm}_xx"], "xx")
        zB_c, xx_c, zA_c = correct(zB, xx, zA, F)
        eb_c = zB_c + 2 * xx_c + C1 + C2
        arms[arm] = {"E_B": eb, "SE": se, "E_A": ea, "E_B_corr": eb_c,
                     "zB": zB, "xx": xx}
    scram = 0.5 * (arms["fixp"]["E_B"] + arms["fixm"]["E_B"])
    scram_se = 0.5 * np.hypot(arms["fixp"]["SE"], arms["fixm"]["SE"])

    g = arms["ground"]
    ff = arms["qet_ff"]
    no_test = g["E_B"] + NSIG * g["SE"] < 0
    d_g = ff["E_B"] - g["E_B"]
    se_g = float(np.hypot(ff["SE"], g["SE"]))
    d_s = ff["E_B"] - scram
    se_s = float(np.hypot(ff["SE"], scram_se))
    W1a = d_g + NSIG * se_g < 0
    W1b = d_s + NSIG * se_s < 0
    W2 = ff["E_B"] + NSIG * ff["SE"] < 0
    W2c = ff["E_B_corr"] + NSIG * ff["SE"] < 0   # SE conservatively raw

    verdict = ("NO-TEST(ground-negative)" if no_test else
               ("ENERGY-TELEPORTED" if (W1a and W1b) else "FAIL-EXISTENCE")
               + ("+NEGATIVE-LOCAL-ENERGY-RAW" if W2 else "")
               + ("+NEGATIVE-LOCAL-ENERGY-CORRECTED" if W2c else ""))
    ledger = {"E_A_deposit_ff": ff["E_A"], "extraction": -ff["E_B"],
              "efficiency": (-ff["E_B"] / ff["E_A"]) if ff["E_A"] else None,
              "theory_efficiency": 0.11475 / 0.70711,
              "message_bits_per_run": 1,
              "note": "QET message = demon record; Landauer floor kT ln2/bit"}
    out = {"arms": arms, "scram_pooled": {"E_B": scram, "SE": scram_se},
           "diffs": {"ff_vs_ground": [d_g, se_g], "ff_vs_scram": [d_s, se_s]},
           "gates": {"G0_no_test": bool(no_test), "W1a": bool(W1a),
                     "W1b": bool(W1b), "W2_raw": bool(W2),
                     "W2c_corrected": bool(W2c)},
           "readout_assignment": F, "demon_ledger": ledger,
           "D1_ff_minus_def": ff["E_B"] - arms["qet_def"]["E_B"],
           "verdict": verdict}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp119_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
