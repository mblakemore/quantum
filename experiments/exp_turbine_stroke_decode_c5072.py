#!/usr/bin/env python3
"""Turbine element-2 decode (Whisper C5072, board #147) — frozen rule from c1b56ee docstring:
P-STROKE: q45 P1(delay) non-monotone, node ~12us, return peak 18-36us, turning > max(0.04, 3se);
round-trip efficiency P1(peak)/P1(0) vs the flat-population T1 expectation at the same delay.
P-CONTROL: non-reviver median monotone; q34 monotone. NO-TEST if q45 monotone on clean prep."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
MAN = json.load(open(os.path.join(QROOT, "results", "exp_turbine_stroke_q45_c5072_manifest.json")))
JOB = MAN["job_id"]
DELAYS = MAN["delays_us"]
QT = MAN["q_target"]
NPHYS = 156
REVIVAL_MIN = 0.04


def main():
    import numpy as np
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(JOB, account_hint="IBMQ_ALT4")
    res = svc.job(JOB).result()
    idx = {m["block"]: i for i, m in enumerate(MAN["pubs_meta"])}

    def counts(tag):
        d = res[idx[tag]].data
        return d[list(d.keys())[0]].get_counts()

    c0, c1 = counts("cal0"), counts("cal1")
    n0, n1 = sum(c0.values()), sum(c1.values())

    def ro(q):
        p01 = sum(v for k, v in c0.items() if k.replace(" ", "")[-1 - q] == "1") / n0
        p10 = sum(v for k, v in c1.items() if k.replace(" ", "")[-1 - q] == "0") / n1
        return p01, p10

    def p1corr(tag, q):
        cc = counts(tag); n = sum(cc.values())
        p1 = sum(v for k, v in cc.items() if k.replace(" ", "")[-1 - q] == "1") / n
        p01, p10 = ro(q)
        vis = max(1e-6, 1 - p01 - p10)
        return max(0.0, min(1.0, (p1 - p01) / vis)), n

    curves = {}
    for q in range(NPHYS):
        c = []
        for us in DELAYS:
            p, n = p1corr(f"stroke_delay{us}us", q)
            c.append(p)
        curves[q] = c

    def turning(c):
        t = 0.0
        for i in range(1, len(c) - 1):
            if min(c[:i+1]) == c[i]: t = max(t, max(c[i+1:]) - c[i])
            if max(c[:i+1]) == c[i]: t = max(t, c[i] - min(c[i+1:]))
        return t

    se = 3 * (2.0 / (12000 ** 0.5))  # conservative 3se for corrected P1
    qc45 = curves[QT]
    t45 = turning(qc45)
    node_i = qc45.index(min(qc45))
    peak_i = node_i + (qc45[node_i+1:].index(max(qc45[node_i+1:])) + 1) if node_i < len(qc45)-1 else node_i
    stroke = t45 > max(REVIVAL_MIN, se) and DELAYS[node_i] <= 18 and 18 <= DELAYS[peak_i] <= 36

    others = [q for q in range(NPHYS) if q != QT and curves[q][0] > 0.5]
    med_curve = [float(np.median([curves[q][i] for q in others])) for i in range(len(DELAYS))]
    med_monotone = all(med_curve[i+1] <= med_curve[i] + 0.01 for i in range(len(med_curve)-1))
    q34_monotone = turning(curves[34]) <= max(REVIVAL_MIN, se)

    # round-trip vs T1-only expectation at the peak delay
    rt_eff = qc45[peak_i] / max(qc45[0], 1e-6)
    t1_exp = med_curve[peak_i] / max(med_curve[0], 1e-6)

    verdict = ("P-STROKE-CONFIRMED" if stroke and rt_eff > t1_exp else
               "STROKE-PRESENT-BELOW-T1-BAR" if stroke else
               "NO-TEST (q45 monotone on clean prep - mechanism narrows to twin coherence)")
    rep = {"card": "exp_turbine_stroke_decode", "cycle": "C5072", "job": JOB, "account": acct,
           "cal_epoch": MAN["cal_epoch"], "delays_us": DELAYS,
           "q45_curve": [round(v, 4) for v in qc45], "q45_turning": round(t45, 4),
           "node_us": DELAYS[node_i], "peak_us": DELAYS[peak_i],
           "roundtrip_eff": round(rt_eff, 4), "t1_only_expectation": round(t1_exp, 4),
           "noise_3se": round(se, 4),
           "P_CONTROL": {"median_monotone": med_monotone,
                         "median_curve": [round(v, 4) for v in med_curve],
                         "q34_monotone": q34_monotone,
                         "q34_curve": [round(v, 4) for v in curves[34]]},
           "verdict": verdict}
    out = os.path.join(QROOT, "results", "exp_turbine_stroke_decoded_c5072.json")
    json.dump(rep, open(out, "w"), indent=1)
    print(f"q45 P1(delay): {[round(v,3) for v in qc45]}")
    print(f"  turning {t45:.3f} (bar {max(REVIVAL_MIN, se):.3f}) node {DELAYS[node_i]}us peak {DELAYS[peak_i]}us")
    print(f"  round-trip eff {rt_eff:.3f} vs T1-only {t1_exp:.3f}")
    print(f"controls: median monotone {med_monotone} {[round(v,3) for v in med_curve]}")
    print(f"  q34 monotone {q34_monotone} {[round(v,3) for v in curves[34]]}")
    print(f"VERDICT: {verdict}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
