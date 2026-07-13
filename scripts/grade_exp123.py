#!/usr/bin/env python3
"""grade_exp123.py — Exp123 P-CTC grader (Whisper C4655). FROZEN AT PREREG.
--selftest = R2 synthetic dry-run (must 4/4 before hardware)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp123_pctc_sim import stats, THETAS  # noqa: E402

NSIG = 5


def classify(p0_loop, se_p0, ppi_loop, se_ppi, p0_broken, xs_loop0, se_xl,
             xs_broken0, se_xb):
    g0 = 0.40 <= p0_loop <= 0.60 and 0.40 <= p0_broken <= 0.60
    n1 = xs_broken0 < 0.25
    ratio = ppi_loop / p0_loop
    se_r = ratio * float(np.hypot(se_ppi / max(ppi_loop, 1e-9),
                                  se_p0 / p0_loop))
    W_PARADOX = ratio + NSIG * se_r < 0.1
    d = xs_loop0 - xs_broken0
    se_d = float(np.hypot(se_xl, se_xb))
    W_LOOP = d - NSIG * se_d > 0.5
    if not (g0 and n1):
        verdict = "NO-TEST(" + ("G0" if not g0 else "N1") + ")"
    elif W_PARADOX and W_LOOP:
        verdict = "PARADOX-ENFORCED+CTC-BACKACTION-CERTIFIED"
    elif W_PARADOX:
        verdict = "PARADOX-ENFORCED(only)"
    elif W_LOOP:
        verdict = "CTC-BACKACTION(only)"
    else:
        verdict = "FAIL-BOTH"
    return {"G0": bool(g0), "N1": bool(n1),
            "paradox_ratio": [ratio, se_r], "W_PARADOX": bool(W_PARADOX),
            "bystander_diff": [d, se_d], "W_LOOP": bool(W_LOOP),
            "verdict": verdict}


def selftest():
    cases = [
        ("both", dict(p0_loop=0.49, ppi_loop=0.008, p0_broken=0.49,
                      xs_loop0=0.97, xs_broken0=-0.02),
         "PARADOX-ENFORCED+CTC-BACKACTION-CERTIFIED"),
        ("paradox-only", dict(p0_loop=0.49, ppi_loop=0.008, p0_broken=0.49,
                              xs_loop0=0.30, xs_broken0=-0.02),
         "PARADOX-ENFORCED(only)"),
        ("backaction-only", dict(p0_loop=0.49, ppi_loop=0.09, p0_broken=0.49,
                                 xs_loop0=0.97, xs_broken0=-0.02),
         "CTC-BACKACTION(only)"),
        ("no-test", dict(p0_loop=0.49, ppi_loop=0.008, p0_broken=0.49,
                         xs_loop0=0.97, xs_broken0=0.60), "NO-TEST(N1)"),
    ]
    npass = 0
    for name, k, want in cases:
        r = classify(k["p0_loop"], 0.003, k["ppi_loop"], 0.0006,
                     k["p0_broken"], k["xs_loop0"], 0.003,
                     k["xs_broken0"], 0.012)
        ok = r["verdict"] == want
        npass += ok
        print(f"  [{name}] -> {r['verdict']} "
              f"({'PASS' if ok else 'FAIL want ' + want})")
    print(f"SELFTEST {npass}/4 {'PASS' if npass == 4 else 'FAIL'}")
    return 0 if npass == 4 else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp123_jobids.json")))
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    raw = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        raw.setdefault((meta["arm"], round(meta["theta"], 4)), {})[
            meta["s_basis"]] = arr.get_counts()

    S = {k: stats(v["z"], v["x"]) for k, v in raw.items()}
    t0, tpi = round(THETAS[0], 4), round(THETAS[-1], 4)
    lo0, lopi = S[("loop", t0)], S[("loop", tpi)]
    br0 = S[("broken", t0)]
    r = classify(lo0["p_herald"], lo0["SE_p"], lopi["p_herald"],
                 lopi["SE_p"], br0["p_herald"], lo0["X_S"], lo0["SE_X"],
                 br0["X_S"], br0["SE_X"])

    law = {}
    for (arm, t), st in S.items():
        pred = float(np.cos(t / 2) ** 2 / 2)
        law[f"{arm}_{t}"] = {"p": st["p_herald"], "pred": pred,
                             "resid": st["p_herald"] - pred,
                             "X_S": st["X_S"], "Z_S": st["Z_S"],
                             "n_herald": st["n_herald"]}
    out = {"stats": {f"{a}_{t}": v for (a, t), v in S.items()},
           "classification": r,
           "law_and_trajectories_reported": law,
           "suppression_factor": (lo0["p_herald"]
                                  / max(lopi["p_herald"], 1e-9)),
           "verdict": r["verdict"]}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp123_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
