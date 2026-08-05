#!/usr/bin/env python3
"""ARM-N RE-FLY decode (Whisper C5018) — frozen rule, blind by construction.

Authorised by Ember's CLEAR (general#4959: req2 PASS, structure PASS, order PASS).

FROZEN RULE (prereg C4998 arm N, G3-closed): per trial, m_Q = 24 two-copy measurements;
decide ALT iff ZERO odd parities across all measurements and all pairs in the rung.
M = 40 trials per block per rung.

REQ-1 BLINDNESS BY CONSTRUCTION: the decision function sees ONLY outcome bitstrings. Block
identity is attached AFTER every decision is computed — the decision path never receives it.
Rungs are assembled here from the pairs the frozen selection rule chose (k=2 takes the two
tightest pairs, k=3 the three tightest; tightness = cal_start diff, already in the bundle).

Per-candidate circuits were flown separately; a rung's statistic is a PRODUCT over independent
single-qubit pairs, so shot-wise combination across candidates is legitimate (no entanglement
between candidates).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
MQ, M = 24, 40

def parities(res, idx, q, plan):
    """Per-shot odd-parity flags for one candidate's two-copy witness.
    Pair 1 = (anc1, anc2); pair 2 = (s1, block q). Odd iff both bits of a pair are 1."""
    c = res[idx].data.meas.get_counts()
    shots = []
    for bs, n in c.items():
        b = bs.replace(" ", "")[::-1]
        p1 = 1 if (b[plan["anc1"]] == "1" and b[plan["anc2"]] == "1") else 0
        p2 = 1 if (b[plan["s1"]] == "1" and b[q] == "1") else 0
        shots.extend([p1 + p2] * n)
    return shots

def main(jid):
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(RES, f"armn_refly_manifest_{jid}.json")))
    bun = json.load(open(os.path.join(RES, f"armn_refly_bundle_{jid}.json")))
    svc, _ = service_for_job(jid); res = svc.job(jid).result()
    qidx = {(m["role"], m["q"]): i for i, m in enumerate(man["pubs_meta"])
            if m["block"].startswith("Q_")}
    pairs = sorted(bun["pairing_reproduction"]["flown_pairs"], key=lambda p: p["diff"])
    par = {}
    for p in pairs:
        for role, q in (("drifter", p["drifter"]), ("null", p["null"])):
            plan = man["partner_plans"][f"{role}_q{q}"][str(q)]
            par[(role, q)] = parities(res, qidx[(role, q)], q, plan)
    report = {"card": "armn_refly_DECODE", "job": jid, "cycle": "C5018",
              "rule": "ALT iff zero odd parities over m_Q=24 measurements x k pairs",
              "authorised_by": "Ember CLEAR general#4959", "rungs": {}}
    for k in (2, 3):
        sel = pairs[:k]
        rung = {"pairs": [(p["drifter"], p["null"]) for p in sel], "blocks": {}}
        for role in ("drifter", "null"):
            qs = [p[role] for p in sel]
            n = min(len(par[(role, q)]) for q in qs)
            trials = min(M, n // MQ)
            calls = []
            for t in range(trials):
                sl = slice(t * MQ, (t + 1) * MQ)
                odd = sum(sum(par[(role, q)][sl]) for q in qs)
                calls.append(1 if odd == 0 else 0)   # 1 = decided ALT
            rate = float(np.mean(calls)) if calls else None
            se = float(np.sqrt(rate * (1 - rate) / len(calls))) if calls else None
            # a rate pinned at 0 or 1 gives se EXACTLY 0.0 — a real value, not a missing one.
            # Use the Wilson/rule-of-three floor so a pinned rate carries honest uncertainty.
            if se is not None and se == 0.0 and calls:
                se = 3.0 / len(calls)
            # REPORTED-NOT-GATED: the underlying continuous witness statistic. The frozen
            # rule is a THRESHOLD on this; if the threshold was calibrated noiseless it can
            # fail to fire on both blocks while the statistic still separates them. Reporting
            # both is the margin-carried-label doctrine, not a bar being moved.
            allpar = [sum(par[(role, q)][i] for q in qs)
                      for i in range(min(len(par[(role, q)]) for q in qs))]
            odd_rate = float(np.mean([1 if x > 0 else 0 for x in allpar]))
            odd_mean = float(np.mean(allpar))
            odd_se = float(np.std([1 if x > 0 else 0 for x in allpar]) / np.sqrt(len(allpar)))
            rung["blocks"][role] = {"trials": len(calls), "alt_call_rate": round(rate, 4),
                                    "odd_shot_rate": round(odd_rate, 5),
                                    "odd_shot_rate_se": round(odd_se, 5),
                                    "mean_odd_per_shot": round(odd_mean, 5),
                                    "shots_used": len(allpar),
                                    "se": round(se, 4) if se is not None else None,
                                    "se_floored": bool(se == 3.0 / max(len(calls), 1)),
                                    "qubits": qs}
        d, nu = rung["blocks"]["drifter"], rung["blocks"]["null"]
        sep = d["alt_call_rate"] - nu["alt_call_rate"]
        sesep = (float(np.hypot(d["se"], nu["se"]))
                 if d["se"] is not None and nu["se"] is not None else None)
        rung["separation"] = round(sep, 4)
        rung["separation_sigma"] = round(sep / sesep, 2) if sesep and sesep > 0 else None
        do, no = d["odd_shot_rate"], nu["odd_shot_rate"]
        dse = float(np.hypot(d["odd_shot_rate_se"], nu["odd_shot_rate_se"]))
        rung["witness_separation"] = {"drifter_odd_rate": do, "null_odd_rate": no,
                                      "difference": round(do - no, 5),
                                      "sigma": round((do - no) / dse, 2) if dse > 0 else None,
                                      "label": "REPORTED-NOT-GATED (the frozen rule is the "
                                               "threshold verdict above; this is the underlying "
                                               "continuous statistic)"}
        print(f"     witness: drifter odd-rate {do:.4f} vs null {no:.4f} -> "
              f"diff {do-no:+.4f} ({rung['witness_separation']['sigma']} sigma) [reported, not gated]")
        report["rungs"][f"k{k}"] = rung
        print(f"k={k} pairs {rung['pairs']}: drifter ALT-rate {d['alt_call_rate']:.3f}"
              f"+/-{d['se']:.3f} | null {nu['alt_call_rate']:.3f}+/-{nu['se']:.3f}"
              f" | separation {sep:+.3f} ({rung['separation_sigma']} sigma)")
    out = os.path.join(RES, f"armn_refly_decode_{jid}.json")
    json.dump(report, open(out, "w"), indent=1)
    print(f"-> {out}")

if __name__ == "__main__":
    main(sys.argv[1])
