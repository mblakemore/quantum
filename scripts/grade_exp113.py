#!/usr/bin/env python3
"""grade_exp113.py — FROZEN Exp113 grade rule (Whisper C4604).

R5 (retro C4602): the noiseless selftest runs FIRST — the shared estimator
(x_exp, imported from the sim module so grading and feasibility literally share
code) must reproduce DISC=2.0 (quantum arms) and 0 (deco) from fresh Aer counts
before any hardware data is read. SamplerV2 parsing uses named registers
(pub.data.xc / .st, per-shot zip) — never join_data (C4597).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
MANIFEST = os.path.join(HERE, "..", "results", "exp113_jobids.json")
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
from exp113_teleported_witness_sim import x_exp, run_arm, PAIRS  # noqa: E402


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    for arm, want in (("tele_frame", 2.0), ("tele_deco", 0.0)):
        d = {p: run_arm(sim, p, arm) for p in PAIRS}
        disc = d["comm"] - d["anti"]
        assert abs(disc - want) < 0.12, (arm, disc)
    print("R5 SELFTEST PASS (shared estimator reproduces 2.0 / 0.0 noiseless)")


def main():
    selftest()
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)

    x, sent = {}, {}
    for pub, meta in zip(res, metas):
        lab, arm = meta["label"], meta["arm"]
        if arm == "sent":
            reg = list(pub.data.keys())[0]
            c = getattr(pub.data, reg).get_counts()
            sent[lab] = c.get(lab[-1], 0) / sum(c.values())
            continue
        if arm == "direct":
            c = getattr(pub.data, list(pub.data.keys())[0]).get_counts()
            x[lab] = x_exp(c, "direct")
        else:
            xc = pub.data.xc.get_bitstrings()
            st = pub.data.st.get_bitstrings()
            x[lab] = x_exp({"xc": xc, "st": st}, arm)

    disc, se = {}, {}
    n = 4000
    for arm in ("direct", "tele_frame", "tele_active", "tele_deco"):
        disc[arm] = x[f"{arm}_comm"] - x[f"{arm}_anti"]
        se[arm] = float(np.sqrt((1 - x[f"{arm}_comm"]**2) / n
                                + (1 - x[f"{arm}_anti"]**2) / n))
    G = man["gates"]
    g1 = all(v >= G["G1_readout_floor"] for v in sent.values())
    g2 = disc["direct"] - 5 * se["direct"] > G["G2_direct_anchor"]
    g3 = abs(disc["tele_deco"]) + 5 * se["tele_deco"] < G["G3_deco_band"]
    w1 = disc["tele_frame"] - 5 * se["tele_frame"] > G["W1_survival_floor"]
    sep = disc["tele_frame"] - disc["tele_deco"]
    se_sep = float(np.hypot(se["tele_frame"], se["tele_deco"]))
    w2 = sep - 5 * se_sep > G["W2_separation_floor"]
    no_test = not (g1 and g2 and g3)
    verdict = ("NO-TEST" if no_test else
               {"W1": "WIN" if w1 else "LOSS", "W2": "WIN" if w2 else "LOSS"})

    out = {"x": x, "DISC": disc, "SE": se, "sentinels": sent,
           "gates": {"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)},
           "W1": bool(w1), "W2": bool(w2), "separation": sep,
           "se_separation": se_sep, "verdict": verdict,
           "survival_ratio": disc["tele_frame"] / disc["direct"],
           "preview": man["preview"]}
    print(f"=== Exp113 GRADE (job {man['job_id']}, chain {man['chain']}) ===")
    for arm in ("direct", "tele_frame", "tele_active", "tele_deco"):
        print(f"  {arm:12s} DISC={disc[arm]:+.4f}±{se[arm]:.4f} "
              f"(preview {man['preview'][arm]:+.3f})")
    print(f"  separation frame-deco = {sep:.4f}±{se_sep:.4f}")
    print(f"  survival ratio = {out['survival_ratio']:.4f} (pre-filed [0.90,1.00])")
    print(f"  gates G1={g1} G2={g2} G3={g3} | W1={'WIN' if w1 else 'LOSS'} "
          f"W2={'WIN' if w2 else 'LOSS'}")
    print(f"  VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp113_grade.json"),
                        "w"), indent=1, default=float)
    print("wrote results/exp113_grade.json")


if __name__ == "__main__":
    main()
