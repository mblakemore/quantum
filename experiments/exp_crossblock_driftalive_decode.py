#!/usr/bin/env python3
"""P2 drift-alive scout decode (C5002). Job d9hhjm0gk0ls73f30gq0 (kingston).
Per-qubit |<Z>| at d2q=160 vs 280 (readout-corrected), envelope-normalized: drifter excess decay
over the matched-null population. VERDICT per Elder #1102/#1108:
  drift-ALIVE  = drifters show excess decay >= ~3sigma over the non-drifter median AND record X;
  drift-GONE   = no excess (drifters decay like the population) -> census needs refresh / scan.
X (strength) = the excess-decay magnitude, the input for sizing the main-block Delta-resolution.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
JOB = "d9hhjm0gk0ls73f30gq0"
MAN = json.load(open(os.path.join(QROOT, "results", "exp_crossblock_driftalive_scout_manifest.json")))
DRIFTERS = MAN["drifters"]; REG = MAN["register"]


def main():
    import numpy as np
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(JOB)
    res = job.result()
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
        p01, p10 = ro(q)
        vis = max(1e-6, 1 - p01 - p10)
        z = (1 - 2 * p1) / vis                       # readout-corrected <Z>
        return abs(z)

    # per-qubit decay ratio |<Z>|_280 / |<Z>|_160 over the whole register
    decay = {}
    for q in REG:
        a160, a280 = absZ("twin_d160", q), absZ("twin_d280", q)
        decay[q] = a280 / a160 if a160 > 0.05 else None
    pop = [d for q, d in decay.items() if q not in DRIFTERS and d is not None]
    med = float(np.median(pop)); mad = float(np.median([abs(d - med) for d in pop])) or 1e-6
    sigma = 1.4826 * mad
    out = {"card": "exp_crossblock_driftalive_decode", "cycle": "C5002", "job": JOB,
           "cal_epoch": MAN["cal_epoch"], "nonfdrifter_median_decay": round(med, 4),
           "robust_sigma": round(sigma, 4), "drifters": {}}
    excesses = []
    for q in DRIFTERS:
        d = decay.get(q)
        if d is None:
            out["drifters"][q] = {"decay_ratio": None, "note": "|<Z>|_160 too small to normalize"}
            continue
        excess = med - d                              # drifter decays MORE => smaller ratio => positive excess
        nsig = excess / sigma
        out["drifters"][q] = {"decay_ratio": round(d, 4), "excess_over_pop": round(excess, 4),
                              "n_sigma": round(nsig, 2)}
        excesses.append(nsig)
    max_sig = max(excesses) if excesses else 0
    n_confirmed = sum(1 for e in excesses if e >= 3)
    X = round(float(np.median([out["drifters"][q].get("excess_over_pop", 0) or 0 for q in DRIFTERS])), 4)
    out["verdict"] = ("DRIFT-ALIVE" if n_confirmed >= 1 and max_sig >= 3
                      else "DRIFT-GONE (census needs refresh/scan)")
    out["drift_strength_X"] = X
    out["n_drifters_confirmed_3sigma"] = n_confirmed
    out["sizing_note"] = f"main-block Delta-resolution must be <= X~{X} (Elder gradeability bar)"
    json.dump(out, open(os.path.join(QROOT, "results", "exp_crossblock_driftalive_decoded.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("verdict", "drift_strength_X", "n_drifters_confirmed_3sigma",
                                          "nonfdrifter_median_decay", "robust_sigma")}, indent=1))
    print("drifter detail:", json.dumps(out["drifters"], indent=1))
    print(f"usage={job.usage()}s")


if __name__ == "__main__":
    main()
