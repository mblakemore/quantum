#!/usr/bin/env python3
"""Epoch-2 revival scout decode (Whisper C5072, board #144 decision rule).
Faithful clone of exp_tricorder_sameepoch_marrakesh_decode.py — same frozen thresholds
(FLAG_SIGMA 3.0, REVIVAL_MIN 0.04 widesweep rule), same estimator math; only the manifest,
job read path (named-account service_for_job), output path, and #144 framing differ."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
MAN = json.load(open(os.path.join(QROOT, "results", "exp_tricorder_epoch2_marrakesh_c5072_manifest.json")))
JOB = MAN["job_id"]
DEPTHS = MAN["depths"]
REG = MAN["register"]
FLAG_SIGMA = 3.0
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

    def absZ(tag, q):
        cc = counts(tag); n = sum(cc.values())
        p1 = sum(v for k, v in cc.items() if k.replace(" ", "")[-1 - q] == "1") / n
        p01, p10 = ro(q); vis = max(1e-6, 1 - p01 - p10)
        return abs((1 - 2 * p1) / vis)

    absz = {q: [absZ(f"twin_d{D}", q) for D in DEPTHS] for q in REG}

    i160, i280 = DEPTHS.index(160), DEPTHS.index(280)
    decay = {q: (absz[q][i280] / absz[q][i160]) for q in REG if absz[q][i160] > 0.05}
    pop = list(decay.values())
    med = float(np.median(pop)); mad = float(np.median([abs(d - med) for d in pop])) or 1e-6
    sigma = 1.4826 * mad

    def mechanism(q):
        z = absz[q]; mn = min(z[1:]); mn_i = z[1:].index(mn) + 1
        post = z[mn_i + 1:]
        revived = len(post) > 0 and (max(post) - mn) > REVIVAL_MIN
        return revived, mn_i, round(max(post) - mn if post else 0.0, 3)

    revivers, drifters = {}, {}
    for q in decay:
        excess = med - decay[q]
        z_ex = excess / sigma
        revived, node_i, amp = mechanism(q)
        if revived:
            revivers[q] = {"node_depth": DEPTHS[node_i], "revival_amplitude": amp,
                           "absZ_curve": [round(v, 4) for v in absz[q]]}
        if z_ex > FLAG_SIGMA:
            drifters[q] = {"decay_excess_sigma": round(z_ex, 2), "revived": revived}

    verdict = ("LIVE-REVIVAL" if revivers else "EPOCH-QUIET")
    rep = {"card": "exp_tricorder_epoch2_decode", "cycle": "C5072", "job": JOB,
           "backend": MAN["backend"], "cal_epoch": MAN["cal_epoch"], "account": acct,
           "thresholds": {"FLAG_SIGMA": FLAG_SIGMA, "REVIVAL_MIN": REVIVAL_MIN,
                          "rule_provenance": "C5004/widesweep frozen rules, unchanged"},
           "population": {"n_scored": len(decay), "decay_ratio_median": round(med, 4),
                          "robust_sigma": round(sigma, 4)},
           "revivers": revivers, "drifters_3sigma": drifters,
           "verdict_144": verdict,
           "decision_rule": MAN["prereg_scope"]["decision_rule"]}
    out = os.path.join(QROOT, "results", "exp_tricorder_epoch2_marrakesh_decoded_c5072.json")
    json.dump(rep, open(out, "w"), indent=1)
    print(f"scored {len(decay)} qubits · median decay ratio {med:.4f} · robust sigma {sigma:.4f}")
    print(f"revivers (> {REVIVAL_MIN} past node): {list(revivers.keys())}")
    for q, r in revivers.items():
        print(f"  q{q}: node at d{r['node_depth']}, revival amp {r['revival_amplitude']}, curve {r['absZ_curve']}")
    print(f"3-sigma drifters: { {q: d['decay_excess_sigma'] for q, d in drifters.items()} }")
    print(f"VERDICT (#144): {verdict}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
