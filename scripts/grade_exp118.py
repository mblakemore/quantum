#!/usr/bin/env python3
"""grade_exp118.py — Exp118 hidden-order diagnostics grader (Whisper C4634).
FROZEN AT PREREG alongside the submit script — classification rules are
mechanical; no grading discretion. Prereg:
experiments/exp118-hidden-order-preregistration.md.

Per site:
  EXISTS      iff D_order - 5*SE_order > FLOOR
  SYMMETRIC   otherwise (the null is a first-class certification result)
If EXISTS: classify the par arm against references (seqAB, seqBA, 50/50 mix):
  GENUINELY-CONCURRENT  min ref distance - 5*SE > FLOOR (par unlike ALL refs)
  SECRETLY-A-FIRST / SECRETLY-B-FIRST / MIXTURE-LIKE
                        nearest ref, if both distance GAPS clear 5*SE_gap
  UNRESOLVED-NEAREST    nearest ref not 5-sigma separated from alternatives
Experiment gate: control site must read SYMMETRIC, else NO-TEST.
"""
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp118_hidden_order_sim import tvd  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

FLOOR = 0.0223
NSIG = 5
B = 200
BOOT_SEED = 4634


def _resample(counts, rng):
    ks = list(counts)
    v = np.array([counts[k] for k in ks], dtype=float)
    return dict(zip(ks, rng.multinomial(int(v.sum()), v / v.sum())))


def _mix(c1, c2):
    m = Counter()
    for k, v in c1.items():
        m[k] += v / 2
    for k, v in c2.items():
        m[k] += v / 2
    return dict(m)


def grade_site(counts, rng):
    """counts: {'seqAB':..., 'seqBA':..., 'par':...} raw count dicts."""
    ab, ba, par = counts["seqAB"], counts["seqBA"], counts["par"]
    mix = _mix(ab, ba)
    point = {"D_order": tvd(ab, ba), "D_A": tvd(par, ab),
             "D_B": tvd(par, ba), "D_mix": tvd(par, mix)}

    boots = {k: [] for k in point}
    for _ in range(B):
        rab, rba, rpar = (_resample(ab, rng), _resample(ba, rng),
                          _resample(par, rng))
        boots["D_order"].append(tvd(rab, rba))
        boots["D_A"].append(tvd(rpar, rab))
        boots["D_B"].append(tvd(rpar, rba))
        boots["D_mix"].append(tvd(rpar, _mix(rab, rba)))
    se = {k: float(np.std(v)) for k, v in boots.items()}

    out = {"point": point, "se": se, "floor": FLOOR}
    if point["D_order"] - NSIG * se["D_order"] > FLOOR:
        out["order"] = "EXISTS"
        refs = {"SECRETLY-A-FIRST": "D_A", "SECRETLY-B-FIRST": "D_B",
                "MIXTURE-LIKE": "D_mix"}
        dmin_key = min(refs, key=lambda r: point[refs[r]])
        dmin = point[refs[dmin_key]]
        if dmin - NSIG * se[refs[dmin_key]] > FLOOR:
            out["par_class"] = "GENUINELY-CONCURRENT"
        else:
            gaps_clear = True
            for alt, stat in refs.items():
                if alt == dmin_key:
                    continue
                gap = point[stat] - dmin
                se_gap = float(np.std(
                    np.array(boots[stat]) - np.array(boots[refs[dmin_key]])))
                if gap <= NSIG * se_gap:
                    gaps_clear = False
            out["par_class"] = dmin_key if gaps_clear else \
                "UNRESOLVED-NEAREST"
        out["nearest_ref"] = dmin_key
    else:
        out["order"] = "ORDER-SYMMETRIC"
    return out


def split_half(bits):
    """Same-distribution empirical floor: TVD(first half, second half)."""
    h = len(bits) // 2
    return tvd(Counter(bits[:h]), Counter(bits[h:]))


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp118_jobids.json")))
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    res = job.result()

    rng = np.random.default_rng(BOOT_SEED)
    counts = {"hotspot": {}, "control": {}}
    diag = {}
    for pub, meta in zip(res, man["metas"]):
        arr = pub.data[list(pub.data.keys())[0]]
        bits = arr.get_bitstrings()
        counts[meta["site"]][meta["schedule"]] = dict(Counter(bits))
        diag[meta["label"]] = {"split_half_tvd": split_half(bits),
                               "n": len(bits)}

    grades = {site: grade_site(counts[site], rng)
              for site in ("hotspot", "control")}
    no_test = grades["control"]["order"] != "ORDER-SYMMETRIC"
    verdict = {"grades": grades, "split_half_diagnostics": diag,
               "no_test": no_test,
               "headline": ("NO-TEST (control shows hidden order — "
                            "apparatus artifact)" if no_test else
                            f"hotspot: {grades['hotspot']['order']}"
                            + (f" / par={grades['hotspot']['par_class']}"
                               if "par_class" in grades["hotspot"] else ""))}
    print(json.dumps(verdict, indent=1, default=float))
    outp = os.path.join(HERE, "..", "results", "exp118_grade.json")
    json.dump(verdict, open(outp, "w"), indent=1, default=float)
    print(f"wrote {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
