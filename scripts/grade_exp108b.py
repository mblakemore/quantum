#!/usr/bin/env python3
"""grade_exp108b.py — apply the FROZEN Exp108b grade rule (Whisper C4591).

All analysis lives in experiments/exp108b_native_thermal.py::grade_from_counts
(frozen at commit 4ef8276); this runner only fetches counts and maps labels.
Runs self_validate() first (double-anchor rule: Exp108 fixed point + symmetric
2-tau point) — grading aborts if the anchors fail.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
MANIFEST = os.path.join(HERE, "..", "results", "exp108b_jobids.json")

from exp108b_native_thermal import grade_from_counts, self_validate  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402


def main():
    self_validate()
    print("self-validation anchors PASS (Exp108 fixed point + symmetric 2-tau)")
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    res = job.result()
    metas = man["metas"]
    assert len(res) == len(metas), (len(res), len(metas))

    all_counts = {}
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            list(pub.data.values())[0].get_counts()
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
    g = grade_from_counts(all_counts)

    print(f"=== Exp108b GRADE (job {man['job_id']}, chain {man['chain']}, "
          f"layout {man['layout']}) ===")
    print(f"measured reservoirs: p_a={g['p_a']:.4f} p_b={g['p_b']:.4f} "
          f"(delays {man['delays_us']['a1']:.0f}/{man['delays_us']['a2']:.0f} us)")
    t = g["theory"]
    print(f"theory@(p_a,p_b): P(+)={t['+']['P']:.4f} p1|+={t['+']['p1']:.4f} "
          f"p1|-={t['-']['p1']:.4f} Delta={t['Delta']:.4f} (causal 0)")
    s = g["switch"]
    print(f"switch : P(+)={s['+']['P']:.4f} p1|+={s['+']['p1']:.4f}(±{s['+']['se']:.4f}) "
          f"p1|-={s['-']['p1']:.4f}(±{s['-']['se']:.4f}) "
          f"Delta={s['Delta']:.4f}(±{s['Delta_se']:.4f})")
    print(f"nulls  : fwd p1={g['null_fwd']['p1']:.4f} [target p_b] "
          f"rev p1={g['null_rev']['p1']:.4f} [target p_a]")
    print(f"retention: {g['retention']} | deco P(+)={g['deco_pplus']:.4f}")
    print(f"gates: {g['gates']}")
    print(f"sigma vs causal-0: {g['sigma_vs_causal']:.1f}")
    print(f"VERDICT: {g['verdict']}")
    print(f"cooling check: p1|+ + 5SE = {s['+']['p1'] + 5*s['+']['se']:.4f} vs "
          f"min reservoir {min(g['p_a'], g['p_b']):.4f}")

    with open(os.path.join(HERE, "..", "results", "exp108b_grade.json"), "w") as f:
        json.dump(g, f, indent=1, default=float)
    print("wrote results/exp108b_grade.json")


if __name__ == "__main__":
    main()
