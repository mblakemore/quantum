#!/usr/bin/env python3
"""Exp107 grade — frozen rule (exp107-cyclic3-capacity-preregistration.md), mechanical.
1. shallow sentinel min DISC >= +1.60 else NO-TEST (apparatus)
2. DEEP sentinel min P(000) >= 0.55 else NO-TEST-WINDOW (window meter; values feed F84 regardless)
3. null |D|+5SE < 0.05 else NO-TEST
4. WIN iff Rbar - 5SE > 0.10 ; LOSS iff Rbar + 5SE < 0.10 ; else AMBIGUOUS
Conventions: count key 'tqc' with k[0]=target Z bit, k[1:]=(c0,c1) prep-basis pair,
'00' = prep-state class (c=0). Rbar = (R(b0)-R(b1))/2, R = <Z|c0> - <Z|c1>.
Null observable = UNCONDITIONED D (Exp106 lesson)."""
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "..", "results", "exp107_jobids.json")
OUT = os.path.join(HERE, "..", "results", "exp107_hw_results.json")
PAULIS = "1XYZ"


def get_counts(pr):
    db = pr.data
    for name in ("c", "meas", "c0"):
        if hasattr(db, name):
            return getattr(db, name).get_counts()
    raise RuntimeError("no creg")


def main():
    man = json.load(open(MANIFEST))
    g = man["gates"]
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    job = svc.job(man["job_id"])
    print(f"job {man['job_id']}: {job.status()}")
    res = job.result()
    assert len(res) == len(man["metas"])
    C = {m["label"]: get_counts(res[i]) for i, m in enumerate(man["metas"])}
    shots = {m["label"]: m["shots"] for m in man["metas"]}

    # 1. shallow sentinels (1-clbit counts)
    xc = {lab: 2 * (C[lab].get("0", 0) / shots[lab]) - 1
          for lab in C if lab.startswith("sent_")}
    discs = {r: xc[f"sent_{r}_commute"] - xc[f"sent_{r}_anticommute"]
             for r in ("start", "mid", "end")}
    smin = min(discs.values())
    s_pass = smin >= g["sentinel_min_disc"]
    print(f"shallow sentinel DISC s/m/e = {discs['start']:+.4f}/{discs['mid']:+.4f}/"
          f"{discs['end']:+.4f} min={smin:+.4f} gate(>= +1.60): "
          f"{'PASS' if s_pass else 'FAIL -> NO-TEST'}")

    # 2. deep sentinels (3-clbit counts, ideal '000')
    p000 = {r: C[f"deep_{r}"].get("000", 0) / shots[f"deep_{r}"]
            for r in ("start", "mid", "end")}
    dmin = min(p000.values())
    d_pass = dmin >= g["deep_min_p000"]
    print(f"DEEP sentinel P(000) s/m/e = {p000['start']:.4f}/{p000['mid']:.4f}/"
          f"{p000['end']:.4f} min={dmin:.4f} gate(>= {g['deep_min_p000']}): "
          f"{'PASS' if d_pass else 'FAIL -> NO-TEST-WINDOW'} "
          f"[FakeMarrakesh-grade 0.744; F84 data regardless]")

    # 3+4. pool game/null
    def pool_stats(prefix):
        stats, joint = {}, np.zeros((2, 4))
        dz, dvar = [], []
        for bit in (0, 1):
            pool = {}
            for ops in itertools.product(PAULIS, repeat=3):
                lab = f"{prefix}({''.join(ops)})b{bit}"
                for k, v in C[lab].items():
                    pool[k] = pool.get(k, 0) + v
            n = sum(pool.values())
            zs, zc = {0: 0, 1: 0}, {0: 0, 1: 0}
            for k, v in pool.items():
                t = int(k[0])
                cls = 0 if k[1:] == "00" else 1
                zs[cls] += v * (1 - 2 * t)
                zc[cls] += v
                joint[bit, 2 * cls + t] += v
            joint[bit] /= n
            stats[bit] = {"pc0": zc[0] / n,
                          "z0": zs[0] / max(zc[0], 1), "z1": zs[1] / max(zc[1], 1),
                          "n0": zc[0], "n1": zc[1]}
            zu = sum(v * (1 - 2 * int(k[0])) for k, v in pool.items()) / n
            dz.append(zu)
            dvar.append((1 - zu * zu) / n)
        R = {b: stats[b]["z0"] - stats[b]["z1"] for b in (0, 1)}
        Rbar = (R[0] - R[1]) / 2
        var = sum((1 - stats[b][f"z{c}"] ** 2) / max(stats[b][f"n{c}"], 1)
                  for b in (0, 1) for c in (0, 1)) / 4
        D = (dz[0] - dz[1]) / 2
        seD = math.sqrt((dvar[0] + dvar[1]) / 4)
        joint /= 2
        pb, pct = joint.sum(axis=1), joint.sum(axis=0)
        mi = float(sum(joint[i, j] * np.log2(joint[i, j] / (pb[i] * pct[j]))
                       for i in range(2) for j in range(4) if joint[i, j] > 0))
        return {"Rbar": Rbar, "SE": math.sqrt(var), "D": D, "SE_D": seD,
                "mi_bits": mi, "pc0_b0": stats[0]["pc0"], "pc0_b1": stats[1]["pc0"],
                "R_b0": R[0], "R_b1": R[1]}

    sw = pool_stats("sw")
    nu = pool_stats("nu")
    null_stat = abs(nu["D"]) + 5 * nu["SE_D"]
    n_pass = null_stat < g["null_D_band"]
    print(f"null: D={nu['D']:+.5f} SE={nu['SE_D']:.5f} |D|+5SE={null_stat:.5f} "
          f"gate(<0.05): {'PASS' if n_pass else 'FAIL -> NO-TEST'}  MI_null={nu['mi_bits']:.5f}")
    lo, hi = sw["Rbar"] - 5 * sw["SE"], sw["Rbar"] + 5 * sw["SE"]
    print(f"\nswitch: Rbar = {sw['Rbar']:+.5f}  SE = {sw['SE']:.5f}  "
          f"Rbar-5SE = {lo:+.5f} vs floor {g['win_floor']}")
    print(f"        R(b0)={sw['R_b0']:+.5f} R(b1)={sw['R_b1']:+.5f} "
          f"(noiseless ±0.673; FM +0.518)")
    print(f"        MI_switch = {sw['mi_bits']:.5f} bits (ideal 0.0833, FM 0.0485; "
          f"N=2 measured 0.0436)")
    print(f"        P(c=0) = {sw['pc0_b0']:.4f}/{sw['pc0_b1']:.4f} (noiseless 0.4953)  "
          f"D_switch = {sw['D']:+.5f}")

    if not s_pass or not n_pass:
        verdict = "NO-TEST"
    elif not d_pass:
        verdict = "NO-TEST-WINDOW"
    elif lo > g["win_floor"]:
        verdict = "WIN"
    elif hi < g["win_floor"]:
        verdict = "LOSS"
    else:
        verdict = "AMBIGUOUS"
    sig0 = sw["Rbar"] / sw["SE"] if sw["SE"] > 0 else 0
    print(f"\n*** VERDICT (frozen rule): {verdict} ***  "
          f"({sig0:.1f} sigma over the causal value 0)")

    json.dump({"job_id": man["job_id"], "graded_by": "whisper-C4539 (frozen rule)",
               "shallow_disc": discs, "shallow_pass": s_pass,
               "deep_p000": p000, "deep_pass": d_pass,
               "null": nu, "null_pass": n_pass, "switch": sw,
               "verdict": verdict, "sigma_over_zero": sig0},
              open(OUT, "w"), indent=1)
    print(f"Saved {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
