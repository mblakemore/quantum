#!/usr/bin/env python3
"""grade_exp109.py — apply the FROZEN Exp109 grade rule (Whisper C4591).

Prereg: experiments/exp109-superdense-coding-preregistration.md (+ dated
compilation amendment). Constants from the manifest: G1 win floor 0.55,
G2 null band 0.03, G3 sentinel floor 0.95. Pre-filed hw expectation [0.93,0.97].
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MANIFEST = os.path.join(HERE, "..", "results", "exp109_jobids.json")

from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402


def decode(bits):
    return f"{int(bits[1])}{int(bits[0])}"


def mi_bits(counts_by_m):
    tot = sum(sum(c.values()) for c in counts_by_m.values())
    pm = {m: sum(c.values()) / tot for m, c in counts_by_m.items()}
    pout = {}
    for c in counts_by_m.values():
        for o, n in c.items():
            pout[o] = pout.get(o, 0) + n / tot
    return sum((n / tot) * np.log2((n / tot) / (pm[m] * pout[o]))
               for m, c in counts_by_m.items() for o, n in c.items())


def arm_stats(counts_by_m):
    succ = sum(c.get(o, 0) for m, c in counts_by_m.items()
               for o in c if decode(o) == m)
    tot = sum(sum(c.values()) for c in counts_by_m.values())
    p = succ / tot
    return {"p_success": p, "se": float(np.sqrt(p * (1 - p) / tot)),
            "mi_bits": float(mi_bits(counts_by_m)), "shots": tot,
            "per_message": {m: sum(n for o, n in c.items() if decode(o) == m)
                            / sum(c.values()) for m, c in counts_by_m.items()}}


def main():
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    res = job.result()
    metas = man["metas"]
    assert len(res) == len(metas), (len(res), len(metas))

    arms = {"main": {}, "null": {}}
    sent = {}
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            list(pub.data.values())[0].get_counts()
        if meta["kind"] in arms:
            arms[meta["kind"]][meta["message"]] = c
        else:
            n = sum(c.values())
            sent[meta["prep"]] = c.get(meta["prep"][::-1], c.get(meta["prep"], 0)) / n

    main_s, null_s = arm_stats(arms["main"]), arm_stats(arms["null"])
    G = man["gates"]
    g3 = all(v >= G["G3_sentinel_floor"] for v in sent.values())
    g2 = abs(null_s["p_success"] - 0.5) < G["G2_null_band"]
    g1 = main_s["p_success"] >= G["G1_win_floor"]
    verdict = "NO-TEST" if not (g2 and g3) else ("WIN" if g1 else "LOSS")
    lo, hi = man["prefiled_expectation"]
    in_band = lo <= main_s["p_success"] <= hi

    sigma = (main_s["p_success"] - 0.5) / main_s["se"]
    out = {"main": main_s, "null": null_s, "sentinels": sent,
           "gates": {"G1_win": bool(g1), "G2_null": bool(g2), "G3_sent": bool(g3)},
           "verdict": verdict, "sigma_above_unassisted_ceiling": float(sigma),
           "prefiled_band": [lo, hi], "in_prefiled_band": bool(in_band)}
    print(f"=== Exp109 GRADE (job {man['job_id']}, pair {man['pair']}) ===")
    print(f"main: p={main_s['p_success']:.4f}±{main_s['se']:.4f} "
          f"MI={main_s['mi_bits']:.4f}b | per-msg {main_s['per_message']}")
    print(f"null: p={null_s['p_success']:.4f} MI={null_s['mi_bits']:.4f}b")
    print(f"sentinels: {sent} | gates: G1={g1} G2={g2} G3={g3}")
    print(f"sigma above 0.5 ceiling: {sigma:.1f} | pre-filed band {lo}-{hi}: "
          f"{'IN' if in_band else 'OUT'}")
    print(f"VERDICT: {verdict}")
    with open(os.path.join(HERE, "..", "results", "exp109_grade.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote results/exp109_grade.json")


if __name__ == "__main__":
    main()
