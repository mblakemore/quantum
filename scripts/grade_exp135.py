#!/usr/bin/env python3
"""grade_exp135.py — Exp135 CHSH randomness-scope grading (Whisper C4676).
Prereg: experiments/exp135-chsh-randomness-preregistration.md"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TS = 2 * math.sqrt(2)


def di_hmin(S):
    if S <= 2:
        return 0.0
    val = max(2 - S * S / 4, 0.0)
    return 1 - math.log2(1 + math.sqrt(val))


def corr_se(counts):
    return float(np.sqrt(1.0 / sum(counts.values())))


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp135_jobids.json")))
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(man["job_id"])
    print("status:", job.status())
    res = job.result()
    E = {"main": {}, "null": {}}
    Ese = {"main": {}, "null": {}}
    signs = {}
    sents = []
    for pub, meta in zip(res, man["metas"]):
        c = pub.data.c.get_counts()
        if meta["kind"] == "sentinel":
            sents.append(c.get(meta["prep"], 0) / sum(c.values()))
            continue
        tot = sum(c.values())
        e = sum((1 if k.count("1") % 2 == 0 else -1) * v
                for k, v in c.items()) / tot
        key = f"{meta['a']}{meta['b']}"
        E[meta["kind"]][key] = e
        Ese[meta["kind"]][key] = corr_se(c)
        signs[key] = meta["sign"]

    def S_of(arm):
        S = sum(signs[k] * E[arm][k] for k in E[arm])
        se = float(np.sqrt(sum(Ese[arm][k] ** 2 for k in E[arm])))
        return S, se
    S, seS = S_of("main")
    Sn, seSn = S_of("null")

    gates = {
        "W1_WITNESS": S > 2 + 5 * seS,
        "W2_TSIRELSON": S <= TS + 5 * seS,
        "W3_NULL": Sn <= 2,
        "G_SENT": all(s >= 0.95 for s in sents)}
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "substrate": man.get("substrate"), "tsirelson": TS,
           "S": [S, seS], "S_null": [Sn, seSn],
           "corrs_main": E["main"], "corrs_null": E["null"],
           "sigma_over_2": (S - 2) / seS,
           "reported_not_gated": {
               "di_hmin_counterfactual_per_use": di_hmin(S),
               "di_note": "NOT usable on-chip (no-signaling unmet); tier-3 what-if",
               "trusted_born_hmin_per_qubit": 1.0,
               "trusted_note": "usable ONLY under explicit device-trust; CHSH health-checks it"},
           "sentinels": sents, "gates": gates}
    print(f"S = {S:.4f} ± {seS:.4f}  (Tsirelson {TS:.4f}) = {(S-2)/seS:.0f}σ over 2")
    print(f"S_null = {Sn:.4f} ± {seSn:.4f}")
    print(f"DI-counterfactual H_min = {di_hmin(S):.4f}/use (NOT usable on-chip)")
    print(f"trusted-device Born H_min = 1.0/qubit (under device-trust)")
    print("GATES:", gates)
    print("sentinels:", [round(s, 4) for s in sents])
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp135_hw_results.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp135_hw_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
