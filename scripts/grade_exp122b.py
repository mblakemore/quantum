#!/usr/bin/env python3
"""grade_exp122b.py — Exp122b phase-blind grader (Whisper C4653).
FROZEN AT PREREG. --selftest = R2 synthetic-counts dry-run (must 4/4 PASS
before hardware grading). Prereg: exp122b-phase-blind-preregistration.md."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp122b_phase_blind_sim import expec_c, vis_rice  # noqa: E402

NSIG = 5


def classify(V_exc3, seV_e3, V_vac3, seV_v3, V_exc4, seV_e4, V_vac4, seV_v4,
             echoX3, se_ec3, rawX3, se_rx3, V_exc0, V_vac0):
    g0 = V_exc0 > 0.7 and V_vac0 > 0.7
    sep3 = V_vac3 - V_exc3
    se3 = float(np.hypot(seV_v3, seV_e3))
    sep4 = V_vac4 - V_exc4
    se4 = float(np.hypot(seV_v4, seV_e4))
    W_TWIN = (sep3 - NSIG * se3 > 0) or (sep4 - NSIG * se4 > 0)
    rot = echoX3 - rawX3
    se_rot = float(np.hypot(se_ec3, se_rx3))
    W_ROT = rot - NSIG * se_rot > 0
    if not g0:
        verdict = "NO-TEST(interferometer-dead)"
    elif W_TWIN and W_ROT:
        verdict = "MIXED-BOTH-MECHANISMS"
    elif W_TWIN:
        verdict = "AGING-CERTIFIED-CLEAN"
    elif W_ROT:
        verdict = "CLOCK-PULL-CERTIFIED"
    else:
        verdict = "UNRESOLVED"
    return {"G0": bool(g0), "W_TWIN": bool(W_TWIN), "W_ROT": bool(W_ROT),
            "sep_dt3": [sep3, se3], "sep_dt4": [sep4, se4],
            "echo_recovery_dt3": [rot, se_rot], "verdict": verdict}


def selftest():
    """R2: 4 synthetic scenarios through the full classification."""
    se = 0.007
    cases = [
        ("mixed", dict(V_exc3=0.30, V_vac3=0.45, V_exc4=0.10, V_vac4=0.22,
                       echoX3=0.28, rawX3=-0.16), "MIXED-BOTH-MECHANISMS"),
        ("aging-only", dict(V_exc3=0.30, V_vac3=0.45, V_exc4=0.10,
                            V_vac4=0.22, echoX3=0.31, rawX3=0.30),
         "AGING-CERTIFIED-CLEAN"),
        ("rotation-only", dict(V_exc3=0.44, V_vac3=0.45, V_exc4=0.21,
                               V_vac4=0.22, echoX3=0.43, rawX3=-0.16),
         "CLOCK-PULL-CERTIFIED"),
        ("unresolved", dict(V_exc3=0.44, V_vac3=0.45, V_exc4=0.21,
                            V_vac4=0.22, echoX3=0.44, rawX3=0.43),
         "UNRESOLVED"),
    ]
    npass = 0
    for name, k, want in cases:
        r = classify(k["V_exc3"], se, k["V_vac3"], se, k["V_exc4"], se,
                     k["V_vac4"], se, k["echoX3"], se, k["rawX3"], se,
                     0.85, 0.86)
        ok = r["verdict"] == want
        npass += ok
        print(f"  [{name}] -> {r['verdict']} "
              f"({'PASS' if ok else 'FAIL, wanted ' + want})")
    print(f"SELFTEST {npass}/4 {'PASS' if npass == 4 else 'FAIL'}")
    return 0 if npass == 4 else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp122b_jobids.json")))
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    raw = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        raw[meta["label"]] = (meta, arr.get_counts())

    ladder = man["ladder_us"]
    V = {}
    XY = {}
    for arm in ("exc", "vac", "exc_echo"):
        for dt in ladder:
            kx, ky = f"{arm}_{dt}_x", f"{arm}_{dt}_y"
            if kx not in raw or ky not in raw:
                continue
            x, sx = expec_c(raw[kx][1])
            y, sy = expec_c(raw[ky][1])
            V[(arm, dt)] = vis_rice(x, sx, y, sy)
            XY[(arm, dt)] = {"X": [x, sx], "Y": [y, sy]}

    # in-job T1s
    t1 = {}
    for lane, pos in (("K", 1), ("L", 2)):
        pts = sorted((m["dt_us"], sum(v for k, v in c.items()
                                      if k[2 - pos] == "1") / sum(c.values()))
                     for lab, (m, c) in raw.items()
                     if m["arm"] == f"cal{lane}")
        xs = np.array([p[0] for p in pts if p[0] > 0])
        ys = np.array([max(p[1], 1e-4) for p in pts if p[0] > 0])
        p0 = [p[1] for p in pts if p[0] == 0.0][0]
        t1[lane] = -1.0 / float(np.polyfit(xs, np.log(ys / p0), 1)[0])

    dt3, dt4 = ladder[2], ladder[3]
    r = classify(V[("exc", dt3)][0], V[("exc", dt3)][1],
                 V[("vac", dt3)][0], V[("vac", dt3)][1],
                 V[("exc", dt4)][0], V[("exc", dt4)][1],
                 V[("vac", dt4)][0], V[("vac", dt4)][1],
                 XY[("exc_echo", dt3)]["X"][0], XY[("exc_echo", dt3)]["X"][1],
                 XY[("exc", dt3)]["X"][0], XY[("exc", dt3)]["X"][1],
                 V[("exc", ladder[0])][0], V[("vac", ladder[0])][0])

    pred_ratio3 = float(np.sqrt(np.exp(-dt3 / t1["K"]) * np.exp(-dt3 / t1["L"])))
    out = {"V_curves": {f"{a}_{d}": list(V[(a, d)]) for a, d in V},
           "XY": {f"{a}_{d}": XY[(a, d)] for a, d in XY},
           "in_job_T1_us": t1,
           "classification": r,
           "subclaims_reported": {
               "V_ratio_dt3_measured": (V[("exc", dt3)][0]
                                        / max(V[("vac", dt3)][0], 1e-6)),
               "V_ratio_dt3_predicted_sqrtp0p1": pred_ratio3},
           "verdict": r["verdict"]}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp122b_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
