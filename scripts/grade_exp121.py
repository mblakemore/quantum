#!/usr/bin/env python3
"""grade_exp121.py — Exp121 heralded-mirror grader (Whisper C4647).
FROZEN AT PREREG. Estimators imported from the sim module (zero drift).
Prereg: experiments/exp121-hp-switch-preregistration.md."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp121_hp_switch_sim import counts_arm  # noqa: E402
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

NSIG = 5
PREM_BAND = 0.05


def main():
    man = json.load(open(os.path.join(HERE, "..", "results",
                                      "exp121_jobids.json")))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    counts = {}
    for pub, meta in zip(res, man["metas"]):
        arr = getattr(pub.data, list(pub.data.keys())[0])
        counts.setdefault(meta["arm"], {})[meta["diary"]] = arr.get_counts()

    arms = {arm: counts_arm(counts[arm], arm) for arm in counts}
    dz = arms["ordZX"]["all"]
    dx = arms["ordXZ"]["all"]
    nu = arms["null"]["all"]
    plus = arms["switch"].get("0")
    minus = arms["switch"].get("1")
    n_minus = minus["n"] if minus else 0
    n_tot = sum(b["n"] for b in arms["switch"].values())
    minus_rate = n_minus / n_tot if n_tot else 0.0

    premise_ok = abs(dz["S_P"]) < PREM_BAND and abs(dx["S_P"]) < PREM_BAND
    n1_ok = abs(nu["S_P"]) < PREM_BAND and nu["S_E2"] < 0.25
    h1_ok = 0.10 <= minus_rate <= 0.40
    W_MIRROR = (minus is not None
                and minus["S_P"] + NSIG * minus["SE_S_P"] < -PREM_BAND)
    W_PLUS = (plus is not None
              and plus["S_P"] - NSIG * plus["SE_S_P"] > PREM_BAND)

    if not premise_ok:
        verdict = "NO-TEST(premise-not-dead)"
    elif not n1_ok:
        verdict = "NO-TEST(null-classification)"
    elif not h1_ok:
        verdict = "NO-TEST(herald-rate)"
    elif W_MIRROR and W_PLUS:
        verdict = "HERALDED-MIRROR-CERTIFIED(+plus-branch)"
    elif W_MIRROR:
        verdict = "HERALDED-MIRROR-CERTIFIED"
    elif W_PLUS:
        verdict = "PLUS-ONLY(no-mirror)"
    else:
        verdict = "FAIL-RETRIEVAL"

    out = {"arms": arms,
           "guards": {"premise_ok": bool(premise_ok),
                      "S_P_ordZX": dz["S_P"], "S_P_ordXZ": dx["S_P"],
                      "N1_ok": bool(n1_ok), "H1_ok": bool(h1_ok),
                      "minus_rate": minus_rate},
           "gates": {"W_MIRROR": bool(W_MIRROR), "W_PLUS": bool(W_PLUS)},
           "key_numbers": {
               "S_P_minus": [minus["S_P"], minus["SE_S_P"]] if minus else None,
               "S_P_plus": [plus["S_P"], plus["SE_S_P"]] if plus else None},
           "subclaims_reported": {
               "mirror_depth_vs_-0.5": (minus["S_P"] + 0.5) if minus else None,
               "plus_depth_vs_1/6": (plus["S_P"] - 1 / 6) if plus else None,
               "horizon_keeps_it": {"S_E2_ordZX": dz["S_E2"],
                                    "S_E2_ordXZ": dx["S_E2"],
                                    "theory": [0.0, 0.5]},
               "minus_rate_vs_0.25": minus_rate - 0.25},
           "verdict": verdict}
    print(json.dumps(out, indent=1, default=float))
    p = os.path.join(HERE, "..", "results", "exp121_grade.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
