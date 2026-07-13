#!/usr/bin/env python3
"""grade_exp114.py — FROZEN Exp114 grade rule (Whisper C4607).
R5 selftest first (shared estimator, sim module = fixture). Named registers
only (C4597 rule)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
MANIFEST = os.path.join(HERE, "..", "results", "exp114_jobids.json")
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
import exp114_purification_sim as m114  # noqa: E402

COMBO = {"ab": 1, "abp": 1, "apb": 1, "apbp": -1}


def selftest():
    from qiskit_aer import AerSimulator
    m114.SHOTS = 2000
    sim = AerSimulator()
    for arm in ("raw", "purified"):
        S, se, _ = m114.chsh_from_run(sim, arm, 0.0)
        assert abs(S - 2.8284) < 0.15, (arm, S)
    print("R5 SELFTEST PASS (shared estimator: both arms 2sqrt2 noiseless)")


def main():
    selftest()
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)

    acc = {}   # (kind, setting) -> [sum_e, n]
    keep, tot = 0, 0
    sent = {}
    for pub, meta in zip(res, metas):
        kind, lab = meta["kind"], meta["label"]
        if kind == "sent":
            reg = list(pub.data.keys())[0]
            c = getattr(pub.data, reg).get_counts()
            sent[lab] = c.get(lab[-1], 0) / sum(c.values())
            continue
        sk = lab.split("_")[1]
        key = (kind, sk)
        acc.setdefault(key, [0, 0])
        if kind == "pur":
            ch = pub.data.chsh.get_bitstrings()
            co = pub.data.coin.get_bitstrings()
            for c_, k_ in zip(ch, co):
                tot += 1
                if k_[0] != k_[1]:
                    continue
                keep += 1
                acc[key][0] += 1 if c_.count("1") % 2 == 0 else -1
                acc[key][1] += 1
        else:
            reg = list(pub.data.keys())[0]
            c = getattr(pub.data, reg).get_counts()
            for k_, v in c.items():
                acc[key][0] += v * (1 if k_.count("1") % 2 == 0 else -1)
                acc[key][1] += v

    S, SE = {}, {}
    for kind in ("raw0", "rawp", "pur"):
        s, var = 0.0, 0.0
        for sk, sign in COMBO.items():
            tot_e, n = acc[(kind, sk)]
            e = tot_e / n
            s += sign * e
            var += (1 - e * e) / n
        S[kind], SE[kind] = s, float(np.sqrt(var))

    G = man["gates"]
    g1 = all(v >= G["G1_readout_floor"] for v in sent.values())
    g2 = S["raw0"] - 5 * SE["raw0"] > G["G2_anchor"]
    dead = S["rawp"] + 5 * SE["rawp"] < G["DEAD_bound"]
    alive = S["pur"] - 5 * SE["pur"] > G["ALIVE_bound"]
    gain = (S["pur"] - S["rawp"]) - 5 * float(np.hypot(SE["pur"], SE["rawp"])) \
        > G["GAIN_floor"]
    no_test = not (g1 and g2)
    verdict = ("NO-TEST" if no_test else
               {"DEAD": "WIN" if dead else "LOSS",
                "ALIVE": "WIN" if alive else "LOSS",
                "GAIN": "WIN" if gain else "LOSS"})
    out = {"S": S, "SE": SE, "sentinels": sent, "keep_rate": keep / tot,
           "gates": {"G1": bool(g1), "G2": bool(g2)}, "verdict": verdict,
           "gain_value": S["pur"] - S["rawp"], "preview": man["preview"]}
    print(f"=== Exp114 GRADE (job {man['job_id']}, chain {man['chain']}) ===")
    for kind in ("raw0", "rawp", "pur"):
        print(f"  {kind:5s} S={S[kind]:+.4f}±{SE[kind]:.4f} "
              f"(preview {man['preview'][{'raw0':'raw0','rawp':'rawp','pur':'pur'}[kind]]:+.3f})")
    print(f"  keep={keep/tot:.3f} (preview 0.734) | gain={S['pur']-S['rawp']:+.4f}")
    print(f"  G1={g1} G2={g2} | VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp114_grade.json"),
                        "w"), indent=1, default=float)
    print("wrote results/exp114_grade.json")


if __name__ == "__main__":
    main()
