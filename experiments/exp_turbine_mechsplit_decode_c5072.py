#!/usr/bin/env python3
"""Turbine element-1 decode (Whisper C5072, board #147) — frozen rule from the flight script's
docstring (quantum@18cb0532): per reviver qubit, readout-corrected |<Z>| at fixed d160 vs idle
delay; oscillation = a turning point (rise-after-fall or fall-after-rise) exceeding
REVIVAL_MIN 0.04. Same estimator math as the scout decode, one code path."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
MAN = json.load(open(os.path.join(QROOT, "results", "exp_turbine_mechsplit_c5072_manifest.json")))
JOB = MAN["job_id"]
DELAYS = MAN["delays_us"]
REVIVERS = MAN["reviver_targets"]
REG = MAN["register"]
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
        return abs((1 - 2 * p1) / vis), n, vis

    verdicts = {}
    for q in REVIVERS:
        curve, se = [], []
        for us in DELAYS:
            z, n, vis = absZ(f"d160_delay{us}us", q)
            curve.append(z)
            se.append(2.0 / (vis * (n ** 0.5)))  # se of (1-2p1)/vis, conservative
        # turning-point test per frozen rule
        turning = 0.0
        for i in range(1, len(curve) - 1):
            up_after_down = min(curve[:i+1]) == curve[i] and max(curve[i+1:]) - curve[i] > turning
            if up_after_down: turning = max(curve[i+1:]) - curve[i]
            down_after_up = max(curve[:i+1]) == curve[i] and curve[i] - min(curve[i+1:]) > turning
            if down_after_up: turning = curve[i] - min(curve[i+1:])
        noise = 3 * max(se)
        osc = turning > max(REVIVAL_MIN, noise)
        verdicts[q] = {"curve": [round(v, 4) for v in curve], "turning_amp": round(turning, 4),
                       "noise_3se": round(noise, 4), "clock": "TIME" if osc else "GATE/FLAT"}
        print(f"q{q}: curve {[round(v,3) for v in curve]} turning {turning:.3f} (3se {noise:.3f}) -> {verdicts[q]['clock']}")

    n_time = sum(1 for v in verdicts.values() if v["clock"] == "TIME")
    overall = ("TIME-CLOCK-CONFIRMED" if n_time >= 2 else
               "SINGLE-QUBIT-TIME" if n_time == 1 else "GATE-CLOCK (flat in delay)")
    rep = {"card": "exp_turbine_mechsplit_decode", "cycle": "C5072", "job": JOB,
           "cal_epoch": MAN["cal_epoch"], "account": acct, "delays_us": DELAYS,
           "frozen_rule": "turning point > max(0.04, 3se) per reviver; committed 18cb0532 pre-flight",
           "verdicts": verdicts, "n_time": n_time, "overall": overall}
    out = os.path.join(QROOT, "results", "exp_turbine_mechsplit_decoded_c5072.json")
    json.dump(rep, open(out, "w"), indent=1)
    print(f"OVERALL: {overall}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
