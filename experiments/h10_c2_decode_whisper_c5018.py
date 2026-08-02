#!/usr/bin/env python3
"""H10-C2 DECODE (Whisper C5018) — frozen SS3 arithmetic against the landed job.
Plumbing only: fetch, map pubs by manifest tag, build outcome distributions; every statistic
comes from the flight script's frozen functions (tomo_decode / negativity) and the sealed
prereg's gates. Bootstrap: multinomial resampling, seed 20260802, 4000 resamples (frozen)."""
import json, math, os, sys
import importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
spec = importlib.util.spec_from_file_location("fl", os.path.join(HERE, "h10_c2_flight_whisper_c5018.py"))
fl = importlib.util.module_from_spec(spec); spec.loader.exec_module(fl)

MAN = json.load(open(os.path.join(RESULTS, "h10_c2_flight_manifest.json")))
KAREG = json.load(open(os.path.join(RESULTS, "h10_c2_ka_asflown_c5018.json")))
JOB = MAN["job_id"]

def counts_of(pr):
    return pr.data.c.get_counts()

def probs2_from_counts(cnt):
    n = sum(cnt.values())
    p = np.zeros((2, 2))
    for s, c in cnt.items():
        p[int(s[-1]), int(s[-2])] += c / n
    return p, n

def main():
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(JOB)
    print(f"job resolved on {acct}")
    res = svc.job(JOB).result()
    by_tag = {}
    for pub, pr in zip(MAN["pubs"], res):
        by_tag[pub["tag"]] = (pub, pr)
    rng = np.random.default_rng(20260802)

    def arm_negativity(arm):
        settings = {}
        ns = {}
        for a in "XYZ":
            for b in "XYZ":
                pub, pr = by_tag[f"{arm}_{a}{b}"]
                p, n = probs2_from_counts(counts_of(pr))
                settings[a + b] = p; ns[a + b] = n
        Nhat = fl.tomo_decode(settings)
        boots = []
        for _ in range(4000):
            rs = {}
            for k, p in settings.items():
                draw = rng.multinomial(ns[k], p.reshape(-1) / p.sum()).reshape(2, 2) / ns[k]
                rs[k] = draw
            boots.append(fl.tomo_decode(rs))
        boots = np.array(boots)
        return Nhat, float(boots.std()), [float(np.percentile(boots, 2.5)),
                                          float(np.percentile(boots, 97.5))]

    out = {"job_id": JOB, "decode": "frozen SS3; bootstrap seed 20260802 x4000"}
    for arm in ("A1cut", "A2full", "A4prod"):
        N, sd, ci = arm_negativity(arm)
        out[arm] = {"N": N, "sd": sd, "ci95": ci}
        print(f"{arm}: N = {N:.5f} +- {sd:.5f}  ci95 {np.round(ci,5)}")
    # gates
    N1, s1 = out["A1cut"]["N"], out["A1cut"]["sd"]
    band = max(3 * s1, 0.015)
    sig = (N1 / s1) if s1 > 0 else 0.0   # sd=0 arises when every bootstrap PT is positive: N identically 0
    G1 = (sig >= 5) and (abs(N1 - 0.04876) <= band)
    N4, s4 = out["A4prod"]["N"], out["A4prod"]["sd"]
    G2 = N4 <= 2 * s4
    out["G1"] = {"pass": bool(G1), "sig_gt0": sig, "band": band,
                 "dev_from_reg": N1 - 0.04876}
    out["G2"] = {"pass": bool(G2), "N_over_sd": (N4 / s4 if s4 > 0 else None)}
    out["R1_exchange"] = {"N_full_minus_N_cut": out["A2full"]["N"] - N1,
                          "sd_sum": math.hypot(s1, out["A2full"]["sd"])}
    # R2 floor
    pub, pr = by_tag["A3floor_ZZ"]
    pfl, nfl = probs2_from_counts(counts_of(pr))
    out["R2_floor_P00"] = float(pfl[0, 0])
    # R3 cone
    cone = {}
    for k in range(8):
        pub, pr = by_tag[f"A5cone_t{k}"]
        cnt = counts_of(pr); n = sum(cnt.values())
        expX = (cnt.get("0", 0) - cnt.get("1", 0)) / n
        cone[str(pub["t"])] = {"measured": float(expX),
                               "asflown": KAREG["A5_asflown_expX"][str(pub["t"])]}
    out["R3_cone"] = cone
    # R4 books: Pe from A1cut ZZ marginals; dE_field from A6
    pZZ = None
    pub, pr = by_tag["A1cut_ZZ"]
    pZZ, _ = probs2_from_counts(counts_of(pr))
    out["R4_Pe"] = {"Pe1": float(pZZ[1, 0] + pZZ[1, 1]), "Pe2": float(pZZ[0, 1] + pZZ[1, 1]),
                    "pred": [0.0626, 0.0622]}
    def bonds_of(tag):
        pub, pr = by_tag[tag]
        cnt = counts_of(pr); n = sum(cnt.values())
        e = np.zeros(fl.L - 1)
        for s, c in cnt.items():
            bits = [int(s[-(j + 1)]) for j in range(fl.L)]
            for j in range(fl.L - 1):
                e[j] += (1 - 2 * bits[j]) * (1 - 2 * bits[j + 1]) * c / n
        return e
    E1 = sum(fl.J / 2 * (x + y) for x, y in zip(bonds_of("A6X1"), bonds_of("A6Y1")))
    E0 = sum(fl.J / 2 * (x + y) for x, y in zip(bonds_of("A6X0"), bonds_of("A6Y0")))
    out["R4_dE_field"] = {"measured": float(E1 - E0), "pred": 0.8835}
    verdict = "HOLDS" if (G1 and G2) else "DOES NOT HOLD"
    out["VERDICT"] = f"G1 {'PASS' if G1 else 'FAIL'} AND G2 {'PASS' if G2 else 'FAIL'} -> {verdict}"
    path = os.path.join(RESULTS, "h10_c2_decode_whisper_c5018.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k in ("G1", "G2", "R1_exchange",
                                                             "R2_floor_P00", "R4_Pe",
                                                             "R4_dE_field", "VERDICT")},
                     indent=1, default=float))
    print("->", path)

if __name__ == "__main__":
    main()
