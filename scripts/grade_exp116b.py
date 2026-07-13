#!/usr/bin/env python3
"""grade_exp116b.py — FROZEN Exp116b grade rule (Whisper C4612).
Selection by calib arms only (frozen closest-to-0.45 among qualifying rungs),
then Exp116 gates on the selected rung. R5 selftest first."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
MANIFEST = os.path.join(HERE, "..", "results", "exp116b_jobids.json")
import exp108b_native_thermal as m108  # noqa: E402
m108.THERM_BAND = 0.10
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

QUAL = (0.35, 0.4677)


def p1_of(c):
    n = sum(c.values())
    return sum(v for k, v in c.items() if k[-2] == "1") / n, n


def main():
    assert m108.self_validate()
    print("R5 SELFTEST PASS")
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)
    C = {}
    rets, deco = {}, None
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            getattr(pub.data, list(pub.data.keys())[0]).get_counts()
        lab = meta["label"]
        if "retention" in lab:
            rets[lab] = c.get("00", 0) / sum(c.values())
        elif "deconull" in lab:
            deco = c
        else:
            C[lab] = c

    rungs = {}
    for r in ("r1", "r2", "r3"):
        p_a, _ = p1_of(C[f"{r}_calib_a"])
        p_b, _ = p1_of(C[f"{r}_calib_b"])
        sw = m108.pooled_input({t0: C[(f"{r}_switch_t{t0}")] for t0 in (0, 1)})
        nf = m108.pooled_input({t0: C[f"{r}_null_fwd_t{t0}"] for t0 in (0, 1)},
                               conditional=False)
        nr = m108.pooled_input({t0: C[f"{r}_null_rev_t{t0}"] for t0 in (0, 1)},
                               conditional=False)
        th = m108.exact_targets_2tau(p_a, p_b,
                                     np.diag([0.75, 0.25]).astype(complex))
        rungs[r] = {"p_a": p_a, "p_b": p_b, "sw": sw, "nf": nf, "nr": nr,
                    "th": th,
                    "qualifies": QUAL[0] < p_a < QUAL[1] and QUAL[0] < p_b < QUAL[1]}
        print(f"  {r} (r={man['rungs'][r]['r']}): p_a={p_a:.4f} p_b={p_b:.4f} "
              f"{'QUALIFIES' if rungs[r]['qualifies'] else 'out-of-band'} | "
              f"p1|-={sw['-']['p1']:.4f}±{sw['-']['se']:.4f} "
              f"(th {th['-']['p1']:.4f}) Delta={sw['Delta']:.4f}")

    qual = [r for r in rungs if rungs[r]["qualifies"]]
    if not qual:
        print("VERDICT: NO-TEST (zero qualifying rungs)")
        verdict, sel = "NO-TEST", None
    else:
        sel = min(qual, key=lambda r: abs((rungs[r]["p_a"] + rungs[r]["p_b"]) / 2
                                          - 0.45))
        R = rungs[sel]
        se_cal = float(np.sqrt(0.25 / 6000))
        passive = (R["p_a"] + 5 * se_cal < 0.5) and (R["p_b"] + 5 * se_cal < 0.5)
        g_ret = min(rets.values()) >= 0.80
        se_a = np.sqrt(R["p_a"] * (1 - R["p_a"]) / 6000)
        se_b = np.sqrt(R["p_b"] * (1 - R["p_b"]) / 6000)
        g_thm = (abs(R["nf"]["p1"] - R["p_b"]) + 5 * np.hypot(R["nf"]["p1_se"], se_b)
                 < 0.10 and
                 abs(R["nr"]["p1"] - R["p_a"]) + 5 * np.hypot(R["nr"]["p1_se"], se_a)
                 < 0.10)
        p1m, sem = R["sw"]["-"]["p1"], R["sw"]["-"]["se"]
        win = p1m - 5 * sem > 0.5
        loss = p1m + 5 * sem < 0.5
        no_test = not (passive and g_ret and g_thm)
        verdict = ("NO-TEST" if no_test else
                   "WIN" if win else ("LOSS" if loss else "AMBIGUOUS"))
        Pm = 1 - R["sw"]["+"]["P"]
        print(f"SELECTED: {sel} | passive={'CERT' if passive else 'FAIL'} "
              f"ret={min(rets.values()):.3f} therm={'PASS' if g_thm else 'FAIL'}")
        print(f"  p1|- = {p1m:.4f}±{sem:.4f} INVERSION {p1m-0.5:+.4f} "
              f"({(p1m-0.5)/sem:+.1f} sigma) cert margin {p1m-5*sem-0.5:+.4f}")
        print(f"  ergotropy/run = {max(0, 2*p1m-1)*Pm:.4f} E (P(-)={Pm:.3f}) | "
              f"proc-theory residual {abs(p1m - R['th']['-']['p1']):.4f}")
        print(f"VERDICT: {verdict}")
    out = {"rungs": {r: {"p_a": v["p_a"], "p_b": v["p_b"],
                         "qualifies": v["qualifies"],
                         "p1m": v["sw"]["-"]["p1"], "se_m": v["sw"]["-"]["se"],
                         "p1p": v["sw"]["+"]["p1"], "P_plus": v["sw"]["+"]["P"],
                         "Delta": v["sw"]["Delta"],
                         "th_p1m": v["th"]["-"]["p1"]} for r, v in rungs.items()},
           "selected": sel, "retention": rets, "verdict": verdict}
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp116b_grade.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp116b_grade.json")


if __name__ == "__main__":
    main()
