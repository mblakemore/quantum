#!/usr/bin/env python3
"""grade_exp125.py — grade Exp125 (Landauer final invoice, H4) under the FROZEN prereg
(with the data-blind pre-grade correction to the conservative bracket estimator).
Reads results/exp125_jobids.json, retrieves counts, computes the Landauer floor bracket
per site, grades G1 (floor vs banked F95 credit). Writes results/exp125_grade.json."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

W_CREDIT = 0.0920
SE_CREDIT = 0.0098


def floor_of(p):
    if p <= 0:
        return 0.0
    if p >= 0.5:
        return float("inf")
    return math.log(2) / math.log((1 - p) / p)


def se_floor(p, se_p):
    if p <= 0 or p >= 1:
        return float("inf")
    L = math.log((1 - p) / p)
    return math.log(2) / (L * L * p * (1 - p)) * se_p


def counts_p1(counts):
    """P(measure=1) from a {bitstring: count} dict on 1 classical bit."""
    n1 = sum(c for b, c in counts.items() if b.strip()[-1] == "1")
    tot = sum(counts.values())
    return n1 / tot, tot


def main():
    man = json.load(open(os.path.join(HERE, "..", "results", "exp125_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    # map pubs back by shuffled meta order
    metas = man["metas"]
    a_max = {s["qubit"]: s["readout_err"] for s in man["sites"]}
    name_of = {s["qubit"]: s["name"] for s in man["sites"]}

    raw = {}  # (site,arm) -> (p1, N)
    for i, m in enumerate(metas):
        c = res[i].data
        creg = getattr(c, list(vars(c).keys())[0]) if hasattr(c, "__dict__") else None
        counts = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else \
            list(res[i].data.__dict__.values())[0].get_counts()
        p1, N = counts_p1(counts)
        raw[(m["site"], m["arm"])] = (p1, N)

    sites_out = []
    verdicts = []
    for q, nm in name_of.items():
        m0, N0 = raw[(nm, "prep0")]
        p0_1, N1 = raw[(nm, "prep1")]      # P(1|prep1)
        b_hat = 1 - p0_1                     # P(0|prep1) readout 1->0 handle
        am = a_max[q]
        se_m0 = math.sqrt(m0 * (1 - m0) / N0)

        p_lower = max(0.0, m0 - am)
        p_upper = m0
        fl = floor_of(p_lower)
        fu = floor_of(p_upper)
        se_fl = se_floor(p_lower, se_m0)
        se_fu = se_floor(p_upper, se_m0)
        sec_l = math.sqrt(se_fl ** 2 + SE_CREDIT ** 2)
        sec_u = math.sqrt(se_fu ** 2 + SE_CREDIT ** 2)

        pass_ = (fl - W_CREDIT - 5 * sec_l) > 0
        fail_ = (W_CREDIT - fu - 5 * sec_u) > 0
        v = "PASS" if pass_ else ("FAIL" if fail_ else "STRADDLE-REFUTED")
        verdicts.append(v)
        sites_out.append({
            "site": nm, "qubit": q, "a_max": am, "N": N0,
            "m0_raw_excited": round(m0, 6), "se_m0": round(se_m0, 6),
            "b_hat_readout_1to0": round(b_hat, 6),
            "p_eq_lower": round(p_lower, 6), "p_eq_upper": round(p_upper, 6),
            "floor_lower_E": round(fl, 5), "floor_upper_E": round(fu, 5),
            "se_floor_lower": round(se_fl, 5), "se_floor_upper": round(se_fu, 5),
            "W_credit": W_CREDIT,
            "PASS_margin(fl-cred-5SE)": round(fl - W_CREDIT - 5 * sec_l, 5),
            "FAIL_margin(cred-fu-5SE)": round(W_CREDIT - fu - 5 * sec_u, 5),
            "verdict": v,
        })

    graded_site = next((s for s in sites_out if s["site"] == "engine"), sites_out[0])
    out = {
        "experiment": "exp125-landauer-final-invoice", "cycle": "C4663-whisper",
        "job_id": man["job_id"], "bound_graded": man["bound_graded"],
        "W_credit": W_CREDIT, "SE_credit": SE_CREDIT,
        "sites": sites_out,
        "G1_headline_verdict": graded_site["verdict"],
        "graded_on": graded_site["site"],
        "sites_agree": len(set(verdicts)) == 1,
        "coherent_extension": man["coherent_extension"],
    }
    outp = os.path.join(HERE, "..", "results", "exp125_grade.json")
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
