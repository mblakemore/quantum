#!/usr/bin/env python3
"""grade_exp117.py — FROZEN Exp117 grade rule (Whisper C4615). R5 first."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
MANIFEST = os.path.join(HERE, "..", "results", "exp117_jobids.json")
import exp108b_native_thermal as m108  # noqa: E402
m108.THERM_BAND = 0.10
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

QUAL = (0.35, 0.4677)


def p1_of(c):
    n = sum(c.values())
    return sum(v for k, v in c.items() if k[-2] == "1") / n, n


def cond(counts_by_t0):
    """input-pooled conditional p1 per control outcome (g=0.75 weights)."""
    out = {}
    for cbit, name in (("0", "+"), ("1", "-")):
        num = den = 0.0
        for t0, c in counts_by_t0.items():
            w = 0.75 if t0 == 0 else 0.25
            n_t = sum(c.values())
            for k, v in c.items():
                if k[1] == cbit:
                    den += w * v / n_t
                    if k[0] == "1":
                        num += w * v / n_t
        p = num / den
        # SE via effective counts
        n_eff = sum((0.75 if t0 == 0 else 0.25) * sum(v for k, v in c.items()
                    if k[1] == cbit) for t0, c in counts_by_t0.items())
        out[name] = (p, float(np.sqrt(p * (1 - p) / max(n_eff, 1))), n_eff)
    return out


def main():
    assert m108.self_validate()
    print("R5 SELFTEST PASS")
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)
    C, rets = {}, {}
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            getattr(pub.data, list(pub.data.keys())[0]).get_counts()
        lab = meta["label"]
        if "retention" in lab:
            rets[lab] = c.get("00", 0) / sum(c.values())
        elif "deconull" not in lab:
            C[lab] = c

    rungs = {}
    for r in ("r1", "r2", "r3"):
        p_a, _ = p1_of(C[f"{r}_calib_a"])
        p_b, _ = p1_of(C[f"{r}_calib_b"])
        rungs[r] = {"p_a": p_a, "p_b": p_b,
                    "qualifies": QUAL[0] < p_a < QUAL[1] and QUAL[0] < p_b < QUAL[1]}
        print(f"  {r}: p_a={p_a:.4f} p_b={p_b:.4f} "
              f"{'QUALIFIES' if rungs[r]['qualifies'] else 'out-of-band'}")
    qual = [r for r in rungs if rungs[r]["qualifies"]]
    if not qual:
        print("VERDICT: NO-TEST (zero qualifying rungs)")
        json.dump({"rungs": rungs, "verdict": "NO-TEST"},
                  open(os.path.join(HERE, "..", "results", "exp117_grade.json"),
                       "w"), indent=1, default=float)
        return
    sel = min(qual, key=lambda r: abs((rungs[r]["p_a"] + rungs[r]["p_b"]) / 2 - 0.45))
    R = rungs[sel]
    se_cal = float(np.sqrt(0.25 / 6000))
    passive = R["p_a"] + 5 * se_cal < 0.5 and R["p_b"] + 5 * se_cal < 0.5
    g_ret = min(rets.values()) >= 0.80
    nf = m108.pooled_input({t0: C[f"{sel}_null_fwd_t{t0}"] for t0 in (0, 1)},
                           conditional=False)
    nr = m108.pooled_input({t0: C[f"{sel}_null_rev_t{t0}"] for t0 in (0, 1)},
                           conditional=False)
    se_a = np.sqrt(R["p_a"] * (1 - R["p_a"]) / 6000)
    se_b = np.sqrt(R["p_b"] * (1 - R["p_b"]) / 6000)
    g_thm = (abs(nf["p1"] - R["p_b"]) + 5 * np.hypot(nf["p1_se"], se_b) < 0.10 and
             abs(nr["p1"] - R["p_a"]) + 5 * np.hypot(nr["p1_se"], se_a) < 0.10)

    meas = cond({t0: C[f"{sel}_switch_t{t0}"] for t0 in (0, 1)})
    extr = cond({t0: C[f"{sel}_extract_t{t0}"] for t0 in (0, 1)})
    pm, sem = meas["-"][0], meas["-"][1]
    pe, see = extr["-"][0], extr["-"][1]
    recert = pm - 5 * sem > 0.5
    dplus = abs(extr["+"][0] - meas["+"][0])
    se_dplus = float(np.hypot(extr["+"][1], meas["+"][1]))
    integ = dplus + 5 * se_dplus < 0.05
    drop = pm - pe
    se_drop = float(np.hypot(sem, see))
    w1 = drop - 5 * se_drop > 0.05
    w2 = pe + 5 * see < 0.5
    deficit = pe - (1 - pm)
    no_test = not (passive and g_ret and g_thm and recert and integ)
    verdict = ("NO-TEST" if no_test else
               {"W1": "WIN" if w1 else "LOSS", "W2": "WIN" if w2 else "LOSS"})
    Pm = meas["-"][2] / (meas["-"][2] + meas["+"][2])
    work = drop * Pm

    print(f"SELECTED: {sel} | passive={'CERT' if passive else 'FAIL'} ret="
          f"{min(rets.values()):.3f} therm={'PASS' if g_thm else 'FAIL'}")
    print(f"  measure: p1|-={pm:.4f}±{sem:.4f} (recert "
          f"{'PASS' if recert else 'FAIL'}) p1|+={meas['+'][0]:.4f}")
    print(f"  extract: p1|-={pe:.4f}±{see:.4f} p1|+={extr['+'][0]:.4f} "
          f"(integrity d+={dplus:.4f}, {'PASS' if integ else 'FAIL'})")
    print(f"  W1 drop={drop:.4f}±{se_drop:.4f} -> "
          f"{'WIN' if w1 else 'LOSS'} | W2 post-passivity "
          f"{pe+5*see:.4f} vs 0.5 -> {'WIN' if w2 else 'LOSS'}")
    print(f"  DEMON COST deficit = {deficit:+.4f} E | net work = {work:.4f} E/run")
    print(f"VERDICT: {verdict}")
    json.dump({"rungs": rungs, "selected": sel,
               "measure": {k: v[:2] for k, v in meas.items()},
               "extract": {k: v[:2] for k, v in extr.items()},
               "drop": drop, "se_drop": se_drop, "deficit": deficit,
               "work_per_run_E": work, "retention": rets,
               "gates": {"passive": bool(passive), "recert": bool(recert),
                         "integrity": bool(integ), "therm": bool(g_thm)},
               "verdict": verdict},
              open(os.path.join(HERE, "..", "results", "exp117_grade.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp117_grade.json")


if __name__ == "__main__":
    main()
