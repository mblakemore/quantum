#!/usr/bin/env python3
"""QET wheel decode (Whisper C5073, board #146) — frozen rules from 4d45507 docstring.
One code path: analyze_rounds + derive imported from the flight script / exp195c.
P-1: gap_k <= -0.10 at >= 3 sigma, all rounds, band [-0.30, -0.10] each.
P-2: weighted slope of gap_k vs k, with CI.
Falsifiers: dE_k(coinfrozen) - baseline > 0 every round."""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp_qet_wheel_whisper_c5073 import analyze_rounds, N_ROUNDS
from exp195c_energy_teleport import derive, H_, K_
MAN = json.load(open(os.path.join(QROOT, "results", "exp_qet_wheel_c5073_manifest.json")))
JOB = MAN["job_id"]
SHOTS = MAN["shots"]


def main():
    import numpy as np
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(JOB, account_hint="IBMQ_ALT4")
    res = svc.job(JOB).result()
    idx = {m["block"]: i for i, m in enumerate(MAN["pubs_meta"])}
    cb = {}
    for m in MAN["pubs_meta"]:
        d = res[idx[m["block"]]].data
        cb[m["block"]] = d[list(d.keys())[0]].get_counts()

    d = derive()
    base = d["baseline_EB"]
    r = analyze_rounds(cb)
    # per-round SE: E_B = H*<Z_B> + K*<X_A X_B>; se(<.>) <= 1/sqrt(N) each, gap over 2 arms
    se_gap = math.sqrt(2) * math.sqrt(H_**2 + K_**2) / math.sqrt(SHOTS)
    rounds_out, p1_all = [], True
    for k in range(N_ROUNDS):
        gap = r["qet"][k]["E_B"] - r["coinfrozen"][k]["E_B"]
        z = gap / se_gap
        in_band = -0.30 <= gap <= -0.10
        sig = gap <= -0.10 and abs(gap / se_gap) >= 3 and gap + 3*se_gap <= -0.10 or (gap <= -0.10 and -gap/se_gap >= 3)
        # frozen wording: gap <= -0.10 at >= 3 sigma (sigma against 0? against -0.10? Use the
        # stricter reading pre-stated in P-1: significantly <= -0.10 -> (gap + 3*se) <= -0.10
        strict = (gap + 3 * se_gap) <= -0.10
        fals = (r["coinfrozen"][k]["E_B"] - base) > 0
        ok = in_band and strict and fals
        p1_all &= ok
        rounds_out.append({"round": k, "gap": round(gap, 4), "se": round(se_gap, 4),
                           "in_band": in_band, "strict_3se_below_-0.10": strict,
                           "falsifier_coinfrozen_pays": fals,
                           "E_B_qet": round(r["qet"][k]["E_B"], 4),
                           "E_B_coinfrozen": round(r["coinfrozen"][k]["E_B"], 4)})
        print(f"round {k}: gap {gap:+.4f} (se {se_gap:.4f}) band {in_band} strict {strict} "
              f"coinfrozen pays {fals} ({r['coinfrozen'][k]['E_B'] - base:+.4f})")
    ks = np.arange(N_ROUNDS, dtype=float)
    gaps = np.array([ro["gap"] for ro in rounds_out])
    w = np.ones(N_ROUNDS) / se_gap**2
    kbar = ks.mean()
    slope = float(np.sum((ks - kbar) * gaps) / np.sum((ks - kbar)**2))
    se_slope = float(se_gap / math.sqrt(np.sum((ks - kbar)**2)))
    print(f"P-2 wear slope: {slope:+.5f} ± {se_slope:.5f} per round")
    verdict = ("WHEEL-TURNS-ALL-ROUNDS" if p1_all else
               "WHEEL-PARTIAL" if any(ro["in_band"] and ro["strict_3se_below_-0.10"] for ro in rounds_out) else
               "REPRODUCTION-FAILURE")
    rep = {"card": "exp_qet_wheel_decode", "cycle": "C5073", "job": JOB, "account": acct,
           "cal_epoch": MAN["cal_epoch"], "baseline_EB": base,
           "rounds": rounds_out,
           "P_2_wear": {"slope_per_round": slope, "se": se_slope},
           "verdict": verdict}
    out = os.path.join(QROOT, "results", "exp_qet_wheel_decoded_c5073.json")
    json.dump(rep, open(out, "w"), indent=1)
    print(f"VERDICT: {verdict}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
