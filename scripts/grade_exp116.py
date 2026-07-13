#!/usr/bin/env python3
"""grade_exp116.py — FROZEN Exp116 grade rule (Whisper C4610).
Passive premise (both baths p+5SE<0.5) -> inversion cert (p1|- -5SE>0.5).
R5: 108b double-anchor self-validation first. Ergotropy column included."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
MANIFEST = os.path.join(HERE, "..", "results", "exp116_jobids.json")
import exp108b_native_thermal as m108  # noqa: E402
m108.CALIB_BAND = (0.35, 0.50)
m108.THERM_BAND = 0.10
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402


def main():
    assert m108.self_validate()
    print("R5 SELFTEST PASS (108b double-anchor chain)")
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)
    all_counts = {}
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            getattr(pub.data, list(pub.data.keys())[0]).get_counts()
        lab = meta["label"]
        if lab.startswith(("switch_t", "null_fwd_t", "null_rev_t")):
            arm, t0 = lab.rsplit("_t", 1)
            all_counts[(arm, int(t0))] = c
        elif lab in ("calib_a", "calib_b"):
            all_counts[lab] = c
        elif "retention" in lab:
            all_counts[lab.replace("sent_", "retention_").replace("_retention", "")] = c
        elif "deconull" in lab:
            all_counts["deco"] = c
    g = m108.grade_from_counts(all_counts)

    p_a, p_b = g["p_a"], g["p_b"]
    n_cal = 24000  # 2 x 12000
    se_cal = float(np.sqrt(0.25 / (n_cal / 2)))
    passive = (p_a + 5 * se_cal < 0.5) and (p_b + 5 * se_cal < 0.5)
    band = all(0.35 < p < 0.50 for p in (p_a, p_b))
    sw = g["switch"]
    p1m, sem = sw["-"]["p1"], sw["-"]["se"]
    inv_win = p1m - 5 * sem > 0.5
    inv_loss = p1m + 5 * sem < 0.5
    no_test = not (band and passive and g["gates"]["retention"] and g["gates"]["therm"])
    verdict = ("NO-TEST" if no_test else
               "WIN" if inv_win else ("LOSS" if inv_loss else "AMBIGUOUS"))
    Pm = 1 - sw["+"]["P"]
    ergotropy = max(0.0, 2 * p1m - 1) * Pm

    out = {"p_a": p_a, "p_b": p_b, "se_cal": se_cal,
           "passive_premise": bool(passive), "band": bool(band),
           "p1_minus": p1m, "se_minus": sem, "inversion": p1m - 0.5,
           "inversion_sigma": (p1m - 0.5) / sem,
           "p1_plus": sw["+"]["p1"], "Delta": sw["Delta"],
           "retention": g["retention"], "therm": bool(g["gates"]["therm"]),
           "P_minus": Pm, "ergotropy_per_run_E": ergotropy,
           "verdict": verdict, "theory": g["theory"],
           "preview": man.get("overrides", {})}
    print(f"=== Exp116 GRADE (job {man['job_id']}) ===")
    print(f"  baths: p_a={p_a:.4f} p_b={p_b:.4f} (+5SE={max(p_a,p_b)+5*se_cal:.4f}) "
          f"passive={'CERTIFIED' if passive else 'FAIL'}")
    print(f"  p1|- = {p1m:.4f}±{sem:.4f} -> INVERSION {p1m-0.5:+.4f} "
          f"({(p1m-0.5)/sem:+.1f} sigma) | cert margin {p1m-5*sem-0.5:+.4f}")
    print(f"  proc-theory p1|-={g['theory']['-']['p1']:.4f} | Delta={sw['Delta']:.4f} "
          f"(th {g['theory']['Delta']:.4f}) | retention {min(g['retention'].values()):.3f}")
    print(f"  ergotropy/run = {ergotropy:.4f} E (P(-)={Pm:.3f})")
    print(f"  VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp116_grade.json"),
                        "w"), indent=1, default=float)
    print("wrote results/exp116_grade.json")


if __name__ == "__main__":
    main()
