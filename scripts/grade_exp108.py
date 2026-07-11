#!/usr/bin/env python3
"""Exp108 ICO refrigeration resource — MECHANICAL GRADE (Whisper C4561).
Frozen rule: experiments/exp108-ico-refrigeration-preregistration.md (committed 3d8773d
BEFORE submission). Gates:
  1. SENTINEL: min over 3 retention replicates P(c=+,t=0) >= 0.85, else NO-TEST
  2. THERM:    |p1_null - 0.25| + 5*SE < 0.05 for EACH definite order, else NO-TEST
  3. WIN  iff Delta_switch - 5*SE > 0.08  AND  p1|+ + 5*SE < 0.25 (cooling direction)
  4. LOSS iff Delta_switch + 5*SE < 0.08 with gates passing; else AMBIGUOUS
  5. Reported ungraded: P(+) vs 0.71875, p1|- vs 0.41667, deco-null P(c=+) in 0.5+/-0.05,
     null spectator P(c=+) vs 1.
ALSO adjudicates (informal, filed pre-data C4560): depth-decay law Delta=0.2008 vs
FakeMarrakesh Delta=0.2275.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from exp108_ico_refrigeration import pooled_stats, exact_targets, G

MANIFEST = os.path.join(HERE, '..', 'results', 'exp108_jobids.json')


def main():
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    assert str(job.status()) in ("DONE", "JobStatus.DONE"), f"job not done: {job.status()}"
    res = job.result()
    metas = man["metas"]
    assert len(res) == len(metas), (len(res), len(metas))

    counts = {"switch": {}, "null_fwd": {}, "null_rev": {}}
    sentinels, deco = {}, None
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            list(pub.data.values())[0].get_counts()
        kind, label = meta["kind"], meta["label"]
        if kind in counts:
            counts[kind][tuple(meta["prep"])] = c
        elif "retention" in label:
            n = sum(c.values())
            sentinels[label] = c.get("00", 0) / n
        elif "deconull" in label:
            n = sum(c.values())
            deco = {k: v / n for k, v in c.items()}

    sw = pooled_stats(counts["switch"], conditional=True)
    nf = pooled_stats(counts["null_fwd"], conditional=False)
    nr = pooled_stats(counts["null_rev"], conditional=False)
    th = exact_targets(G, np.diag([G, 1 - G]).astype(complex))

    print(f"=== Exp108 GRADE (job {man['job_id']}, chain {man['chain']}, layout {man['layout']}) ===")
    print(f"theory: P(+)={th['+']['P']:.4f} p1|+={th['+']['p1']:.4f} p1|-={th['-']['p1']:.4f} "
          f"Delta={th['Delta']:.4f} (causal 0 exactly)")
    print(f"switch : P(+)={sw['+']['P']:.4f}  p1|+={sw['+']['p1']:.4f}(±{sw['+']['se']:.4f})  "
          f"p1|-={sw['-']['p1']:.4f}(±{sw['-']['se']:.4f})  Delta={sw['Delta']:.4f}(±{sw['Delta_se']:.4f})")
    for name, n in [("null_fwd", nf), ("null_rev", nr)]:
        print(f"{name}: p1={n['p1']:.4f}(±{n['p1_se']:.4f}) [tau {1-G:.4f}]  P(c=+)={n['P+']:.4f}")
    print(f"retention replicates: " +
          " ".join(f"{k.split('_')[1]}={v:.4f}" for k, v in sorted(sentinels.items())))
    dec_pplus = sum(v for k, v in deco.items() if k[-1] == "0")
    print(f"deco-null P(c=+)={dec_pplus:.4f} (ideal 0.5)  P(t=0)={sum(v for k,v in deco.items() if k[-2]=='0'):.4f}")

    # frozen gates
    g1 = min(sentinels.values()) >= 0.85
    g2 = all(abs(n["p1"] - (1 - G)) + 5 * n["p1_se"] < 0.05 for n in (nf, nr))
    win = sw["Delta"] - 5 * sw["Delta_se"] > 0.08 and sw["+"]["p1"] + 5 * sw["+"]["se"] < 0.25
    loss = sw["Delta"] + 5 * sw["Delta_se"] < 0.08
    sigma = sw["Delta"] / sw["Delta_se"]
    print(f"\nGATE 1 sentinel  : {'PASS' if g1 else 'FAIL -> NO-TEST'} (min {min(sentinels.values()):.4f} vs 0.85)")
    print(f"GATE 2 therm-null: {'PASS' if g2 else 'FAIL -> NO-TEST'}")
    if g1 and g2:
        verdict = "WIN" if win else ("LOSS" if loss else "AMBIGUOUS")
        print(f"VERDICT: {verdict}  (Delta={sw['Delta']:.4f}, {sigma:.1f} sigma above the exact-0 causal value; "
              f"floor test Delta-5SE={sw['Delta']-5*sw['Delta_se']:.4f} vs 0.08; "
              f"cooling p1|+ +5SE={sw['+']['p1']+5*sw['+']['se']:.4f} vs 0.25)")
    else:
        verdict = "NO-TEST"
        print("VERDICT: NO-TEST")

    # depth-decay law adjudication (informal, pre-data C4560)
    d_law, d_fake = 0.2008, 0.2275
    print(f"\nLAW ADJUDICATION: measured Delta={sw['Delta']:.4f} | depth-decay law 0.2008 | FakeMarrakesh 0.2275")
    print(f"  |D-law|={abs(sw['Delta']-d_law):.4f}  |D-fake|={abs(sw['Delta']-d_fake):.4f}  "
          f"-> closer to {'LAW' if abs(sw['Delta']-d_law) < abs(sw['Delta']-d_fake) else 'FAKEMARRAKESH'}")

    out = {"verdict": verdict, "switch": sw, "null_fwd": nf, "null_rev": nr,
           "sentinels": sentinels, "deco_pplus": dec_pplus, "sigma_vs_causal": sigma,
           "theory": {"Delta": th["Delta"], "p1p": th["+"]["p1"], "p1m": th["-"]["p1"], "Pp": th["+"]["P"]},
           "law_adjudication": {"measured": sw["Delta"], "law": d_law, "fake": d_fake}}
    outp = os.path.join(HERE, '..', 'results', 'exp108_grade.json')
    with open(outp, 'w') as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\nwrote {os.path.abspath(outp)}")


if __name__ == "__main__":
    main()
