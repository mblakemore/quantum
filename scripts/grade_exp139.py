#!/usr/bin/env python3
"""Exp139 coherent entropy concentration — MECHANICAL GRADE (Whisper C4720).
Frozen rule: experiments/exp139-concentration-preregistration.md. ENGINEERING artifact,
classical compression (NOT new ICO physics). Gates:
  INTEGRITY (fail -> NO-TEST): conc_000 < 0.05 AND conc_111 > 0.95
  PRIMARY (WIN): dest_cold + 5*hypot(se) < single_cold  (concentration colder than one input)
  SECONDARY (WIN): dest_cold + 5*hypot(se) < dest_bath
  CONTEXT: dest_cold vs classical 3p^2-2p^3.
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service

DEFAULT_MANIFEST = os.path.join(HERE, '..', 'results', 'exp139_jobids.json')


def w(b, p):
    return float(np.prod([p if bi else 1 - p for bi in b]))


def pooled(dest, p):
    m, v = 0.0, 0.0
    for b, (p1, n) in dest.items():
        wt = w(b, p)
        m += wt * p1
        v += (wt ** 2) * p1 * (1 - p1) / n
    return m, float(np.sqrt(v))


def main():
    man = json.load(open(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MANIFEST))
    P_COLD, P_BATH = man["p_cold"], man["p_bath"]
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    assert str(job.status()) in ("DONE", "JobStatus.DONE"), f"job not done: {job.status()}"
    res, metas = job.result(), man["metas"]
    assert len(res) == len(metas), (len(res), len(metas))

    dest, single = {}, {}
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else list(pub.data.values())[0].get_counts()
        n = sum(c.values())
        p1 = sum(v for k, v in c.items() if k[-1] == "1") / n
        if meta["kind"] == "conc":
            dest[tuple(meta["prep"])] = (p1, n)
        else:
            single[meta["prep"][0]] = (p1, n)

    dc, dc_se = pooled(dest, P_COLD)
    db, db_se = pooled(dest, P_BATH)
    sc = (1 - P_COLD) * single[0][0] + P_COLD * single[1][0]
    sc_se = float(np.sqrt(((1 - P_COLD) ** 2) * single[0][0] * (1 - single[0][0]) / single[0][1]
                          + (P_COLD ** 2) * single[1][0] * (1 - single[1][0]) / single[1][1]))
    th = 3 * P_COLD ** 2 - 2 * P_COLD ** 3
    s000, s111 = dest[(0, 0, 0)][0], dest[(1, 1, 1)][0]

    print(f"=== Exp139 GRADE (job {man['job_id']}, chain {man['chain']}, layout {man['layout']}) ===")
    print(f"theory (classical): dest_cold={th:.4f}  single={P_COLD:.4f}  dest_bath={3*P_BATH**2-2*P_BATH**3:.4f}")
    print(f"dest_cold = {dc:.4f}(±{dc_se:.4f})   dest_bath = {db:.4f}(±{db_se:.4f})")
    print(f"single    = {sc:.4f}(±{sc_se:.4f})   sentinels: conc_000={s000:.4f}(->0) conc_111={s111:.4f}(->1)")

    integ = s000 < man["gates"]["s000_max"] and s111 > man["gates"]["s111_min"]
    primary = dc + 5 * np.hypot(dc_se, sc_se) < sc
    secondary = dc + 5 * np.hypot(dc_se, db_se) < db
    beat_sigma = (sc - dc) / np.hypot(dc_se, sc_se)
    print(f"\nINTEGRITY: conc_000<{man['gates']['s000_max']} & conc_111>{man['gates']['s111_min']} "
          f"-> {'PASS' if integ else 'NO-TEST'}")
    print(f"PRIMARY  concentration-colder-than-single: {sc-dc:.4f} colder ({beat_sigma:.1f}σ) "
          f"-> {'PASS' if primary else 'FAIL'}")
    print(f"SECONDARY colder-inputs-colder: dest_cold {dc:.4f} < dest_bath {db:.4f} "
          f"-> {'PASS' if secondary else 'FAIL'}")
    print(f"CONTEXT  dest_cold {dc:.4f} vs classical {th:.4f} (depth excess {dc-th:+.4f})")

    verdict = "NO-TEST" if not integ else ("WIN" if primary else "LOSS")
    print(f"\nVERDICT: {verdict}"
          + (f"  — coherent concentration produced a destination qubit {sc-dc:.4f} colder than a "
             f"single input ({beat_sigma:.1f}σ). CLASSICAL compression; ICO physics not extended."
             if integ else ""))

    out = {"verdict": verdict, "integrity": bool(integ), "primary": bool(primary),
           "secondary": bool(secondary), "dest_cold": dc, "dest_cold_se": dc_se,
           "dest_bath": db, "dest_bath_se": db_se, "single_cold": sc, "single_cold_se": sc_se,
           "beat_sigma": float(beat_sigma), "classical_theory": th, "s000": s000, "s111": s111}
    tag = man.get("tag", "exp139")
    json.dump(out, open(os.path.join(HERE, '..', 'results', f'{tag}_grade.json'), 'w'), indent=1, default=float)
    print(f"\nwrote results/{tag}_grade.json")


if __name__ == "__main__":
    main()
