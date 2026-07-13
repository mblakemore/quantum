#!/usr/bin/env python3
"""grade_exp124.py — Exp124 Zeno tractor-beam grader (Whisper C4657).
FROZEN AT PREREG. --selftest = R2 dry-run (4/4 required)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp124_zeno_sim import stats, law, LADDER  # noqa: E402

NSIG = 5


def classify(p8, se8, pu, seu, p2, se2, nodrive8):
    g0 = nodrive8 > 0.7
    d_t = p8 - pu
    se_t = float(np.hypot(se8, seu))
    W_TRACTOR = d_t - NSIG * se_t > 0.3
    d_c = p8 - p2
    se_c = float(np.hypot(se8, se2))
    W_CADENCE = d_c - NSIG * se_c > 0
    if not g0:
        verdict = "NO-TEST(QND-dead)"
    elif W_TRACTOR and W_CADENCE:
        verdict = "ZENO-PINNING-CERTIFIED(+cadence-law)"
    elif W_TRACTOR:
        verdict = "ZENO-PINNING-CERTIFIED"
    else:
        verdict = "FAIL-PINNING"
    return {"G0": bool(g0), "tractor_diff": [d_t, se_t],
            "W_TRACTOR": bool(W_TRACTOR), "cadence_diff": [d_c, se_c],
            "W_CADENCE": bool(W_CADENCE), "verdict": verdict}


def selftest():
    cases = [
        ("both", dict(p8=0.67, pu=0.015, p2=0.24, nodrive8=0.91),
         "ZENO-PINNING-CERTIFIED(+cadence-law)"),
        ("tractor-only", dict(p8=0.67, pu=0.015, p2=0.66, nodrive8=0.91),
         "ZENO-PINNING-CERTIFIED"),
        ("fail", dict(p8=0.30, pu=0.015, p2=0.24, nodrive8=0.91),
         "FAIL-PINNING"),
        ("no-test", dict(p8=0.67, pu=0.015, p2=0.24, nodrive8=0.5),
         "NO-TEST(QND-dead)"),
    ]
    npass = 0
    for name, k, want in cases:
        r = classify(k["p8"], 0.0034, k["pu"], 0.001, k["p2"], 0.003,
                     k["nodrive8"])
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
                                      "exp124_jobids.json")))
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    S = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        S[meta["label"]] = stats(arr.get_counts(), meta["arm"], meta["n"])

    r = classify(S["pinned_8"][0], S["pinned_8"][1],
                 S["unwatched_8"][0], S["unwatched_8"][1],
                 S["pinned_2"][0], S["pinned_2"][1],
                 S["nodrive_8"][0])
    qnd = {n: S[f"nodrive_{n}"][0] ** (1.0 / (n + 1)) for n in LADDER}
    corrected = {n: (S[f"pinned_{n}"][0] / max(S[f"nodrive_{n}"][0], 1e-6))
                 for n in LADDER}
    out = {"stats": {k: list(v) for k, v in S.items()},
           "classification": r,
           "subclaims_reported": {
               "qnd_per_measurement": qnd,
               "law_theory": {str(n): law(n) for n in LADDER},
               "law_qnd_corrected": corrected,
               "residuals_corrected": {str(n): corrected[n] - law(n)
                                       for n in LADDER}},
           "verdict": r["verdict"]}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp124_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
