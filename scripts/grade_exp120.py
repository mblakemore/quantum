#!/usr/bin/env python3
"""grade_exp120.py — Exp120 Darwinism x ICO grader (Whisper C4644).
FROZEN AT PREREG. Estimators imported from the sim module (zero drift).
Prereg: experiments/exp120-darwinism-ico-preregistration.md."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp120_darwinism_ico_sim import counts_arm  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

NSIG = 5


def w_of(branch):
    w = branch["A_Z"] + branch["A_X"]
    se = float(np.hypot(branch["SE_A_Z"], branch["SE_A_X"]))
    return w, se


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp120_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    counts = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        counts[meta["label"]] = arr.get_counts()

    arms = {arm: counts_arm(counts[f"{arm}_z"], counts[f"{arm}_x"], arm)
            for arm in ("ordZX", "ordXZ", "switch", "null")}

    # guards
    null = arms["null"]["all"]
    n1_val = null["A_X"] - null["A_Z"]
    n1_ok = n1_val > 0.2
    n_minus = arms["switch"]["1"]["n_z"] + arms["switch"]["1"]["n_x"]
    n_total = sum(arms["switch"][b][f"n_{sb}"] for b in ("0", "1")
                  for sb in ("z", "x"))
    minus_rate = n_minus / n_total
    h1_ok = 0.10 <= minus_rate <= 0.40

    # measured hull
    wZX, seZX = w_of(arms["ordZX"]["all"])
    wXZ, seXZ = w_of(arms["ordXZ"]["all"])
    (w_min, se_min), (w_max, se_max) = sorted(
        [(wZX, seZX), (wXZ, seXZ)], key=lambda t: t[0])
    w_plus, se_plus = w_of(arms["switch"]["0"])
    w_minus, se_minus = w_of(arms["switch"]["1"])

    d_plus = w_plus - w_max
    se_dp = float(np.hypot(se_plus, se_max))
    d_minus = w_minus - w_min
    se_dm = float(np.hypot(se_minus, se_min))
    W_PLUS = d_plus - NSIG * se_dp > 0
    W_MINUS = d_minus + NSIG * se_dm < 0
    inside_plus = abs(d_plus) <= NSIG * se_dp or d_plus < 0
    inside_minus = abs(d_minus) <= NSIG * se_dm or d_minus > 0

    if not (n1_ok and h1_ok):
        verdict = "NO-TEST(" + ("null-classification" if not n1_ok
                                else "herald-rate") + ")"
    elif W_PLUS and W_MINUS:
        verdict = "DARWINISM-HULL-VIOLATED(both-branches)"
    elif W_PLUS or W_MINUS:
        verdict = ("DARWINISM-HULL-VIOLATED("
                   + ("plus" if W_PLUS else "minus") + "-branch)")
    elif inside_plus and inside_minus:
        verdict = "ORDER-ROBUST-OBJECTIVITY(inside-hull)"
    else:
        verdict = "INDETERMINATE"

    out = {"arms": arms,
           "guards": {"N1_value": n1_val, "N1_ok": bool(n1_ok),
                      "minus_rate": minus_rate, "H1_ok": bool(h1_ok)},
           "hull_measured": {"w_min": w_min, "w_max": w_max,
                             "w_ordZX": wZX, "w_ordXZ": wXZ},
           "branches": {"w_plus": [w_plus, se_plus],
                        "w_minus": [w_minus, se_minus]},
           "diffs": {"plus_vs_hullmax": [d_plus, se_dp],
                     "minus_vs_hullmin": [d_minus, se_dm]},
           "gates": {"W_PLUS": bool(W_PLUS), "W_MINUS": bool(W_MINUS)},
           "subclaims_reported": {
               "plus_record_symmetry": abs(arms["switch"]["0"]["A_Z"]
                                           - arms["switch"]["0"]["A_X"]),
               "minus_erasure_dev_AZ": arms["switch"]["1"]["A_Z"] - 0.5,
               "minus_erasure_dev_AX": arms["switch"]["1"]["A_X"] - 0.5,
               "theory": {"w_plus": 5 / 3, "w_minus": 1.0, "hull_point": 1.5,
                          "minus_rate": 0.25}},
           "verdict": verdict}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp120_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
