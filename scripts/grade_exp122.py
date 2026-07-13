#!/usr/bin/env python3
"""grade_exp122.py — Exp122 twin-paradox grader (Whisper C4650).
FROZEN AT PREREG. Prereg: experiments/exp122-twin-paradox-preregistration.md."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp122_twin_paradox_sim import vis_from_counts  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

NSIG = 5


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp122_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    counts = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        counts[meta["label"]] = (meta, arr.get_counts())

    ladder = man["ladder_us"]
    curves = {"exc": {}, "vac": {}}
    for lab, (meta, cts) in counts.items():
        if meta["arm"] in ("exc", "vac"):
            v, se = vis_from_counts(cts)
            curves[meta["arm"]][meta["dt_us"]] = (v, se)

    # in-job T1 fits (grading truth; F95 lesson)
    t1 = {}
    for lane, pos in (("K", 1), ("L", 2)):
        pts = []
        for lab, (meta, cts) in counts.items():
            if meta["arm"] == f"cal{lane}":
                n = sum(cts.values())
                alive = sum(v for k, v in cts.items() if k[2 - pos] == "1")
                pts.append((meta["dt_us"], alive / n))
        pts.sort()
        xs = np.array([p[0] for p in pts if p[0] > 0])
        ys = np.array([max(p[1], 1e-4) for p in pts if p[0] > 0])
        p0 = [p[1] for p in pts if p[0] == 0.0][0]
        slope = float(np.polyfit(xs, np.log(ys / p0), 1, w=np.sqrt(ys))[0])
        t1[lane] = {"T1_fit_us": -1.0 / slope, "p0": p0,
                    "points": [list(p) for p in pts]}

    dt3, dt4 = ladder[2], ladder[3]
    g0 = (curves["exc"][ladder[0]][0] > 0.7
          and curves["vac"][ladder[0]][0] > 0.7)

    def sep(dt):
        d = curves["vac"][dt][0] - curves["exc"][dt][0]
        se = float(np.hypot(curves["vac"][dt][1], curves["exc"][dt][1]))
        return d, se
    d3, se3 = sep(dt3)
    d4, se4 = sep(dt4)
    W_AGE = d3 - NSIG * se3 > 0
    W_LAD = d4 - NSIG * se4 > 0

    # law subclaim (REPORTED): ln R slope vs -(GK+GL)/2 from in-job T1s
    gk = 1.0 / t1["K"]["T1_fit_us"]
    gl = 1.0 / t1["L"]["T1_fit_us"]
    pred_slope = -(gk + gl) / 2.0
    xs, ys = [], []
    for dt in ladder:
        ve, vv = curves["exc"][dt][0], curves["vac"][dt][0]
        if vv > 0.05 and ve > 0.01:
            xs.append(dt)
            ys.append(np.log(ve / vv))
    meas_slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) >= 3 else None

    verdict = ("NO-TEST(interferometer-dead)" if not g0 else
               "AGING-MARKS-THE-PATH" + ("(+ladder)" if W_LAD else "")
               if W_AGE else "FAIL-SEPARATION")
    out = {"curves": {a: {str(k): list(v) for k, v in c.items()}
                      for a, c in curves.items()},
           "in_job_T1": t1,
           "gates": {"G0_ok": bool(g0), "W_AGE": bool(W_AGE),
                     "W_AGE_LADDER": bool(W_LAD)},
           "key_numbers": {"sep_dt3": [d3, se3], "sep_dt4": [d4, se4],
                           "dt3_us": dt3, "dt4_us": dt4},
           "law_subclaim_reported": {
               "measured_lnR_slope_per_us": meas_slope,
               "predicted_slope_per_us": pred_slope,
               "excess_ratio": (meas_slope / pred_slope
                                if meas_slope else None),
               "note": "NOT gated (prereg: fake showed ~1.3x excess; "
                       "mechanisms pre-named: clock dephasing in transit, "
                       "CSWAP records)"},
           "verdict": verdict}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp122_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
