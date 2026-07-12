#!/usr/bin/env python3
"""grade_exp110.py — apply the FROZEN Exp110 grade rule (Whisper C4597).

Prereg: experiments/exp110-swap-vs-teleport-preregistration.md. Estimator: mean
4-prep survival per (arm, N); Outcome A on aggregate mean D over N in {2,4,6};
Outcome B per-N at 5SE; G1 readout sentinels; G2 teleport-N1 wiring floor.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MANIFEST = os.path.join(HERE, "..", "results", "exp110_jobids.json")
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

HOPS = [1, 2, 4, 6]
PREPS = ["0", "1", "+", "+i"]


def survival(counts):
    ok = sum(v for k, v in counts.items() if k.split()[0] == "0")
    return ok / sum(counts.values())


def main():
    man = json.load(open(MANIFEST))
    svc = _get_ibm_service()
    res = svc.job(man["job_id"]).result()
    metas = man["metas"]
    assert len(res) == len(metas)
    counts = {}
    for pub, meta in zip(res, metas):
        # read the OUT register directly (join_data concatenates registers
        # without separators — C4597 grader-bug catch: a 2-bit m register where
        # the 1-bit out was expected read as exactly-0 survival)
        names = list(pub.data.keys())
        reg = "out" if "out" in names else names[0]
        counts[meta["label"]] = getattr(pub.data, reg).get_counts()

    surv = {}
    for arm in ("swap", "teleport"):
        surv[arm] = {}
        for n in HOPS:
            vals = []
            tot = 0
            for p in PREPS:
                c = counts[f"{arm}_N{n}_{p}"]
                ok = c.get("0", 0)   # out register is 1 bit
                ntot = sum(c.values())
                vals.append(ok / ntot)
                tot += ntot
            m = float(np.mean(vals))
            surv[arm][n] = {"mean": m, "per_prep": dict(zip(PREPS, map(float, vals))),
                            "se": float(np.sqrt(m * (1 - m) / tot))}

    sent = {}
    for lab in ("sent_ro_start_0", "sent_ro_start_1", "sent_ro_end_0", "sent_ro_end_1"):
        c = counts[lab]
        want = lab[-1]
        sent[lab] = sum(v for k, v in c.items() if k.split()[0] == want) / sum(c.values())
    drift = survival(counts["sent_mid_swapN6p0"])

    G = man["gates"]
    g1 = all(v >= G["G1_readout_floor"] for v in sent.values())
    g2 = surv["teleport"][1]["mean"] >= G["G2_teleport_N1_floor"]

    D, seD = {}, {}
    for n in (2, 4, 6):
        D[n] = surv["swap"][n]["mean"] - surv["teleport"][n]["mean"]
        seD[n] = float(np.hypot(surv["swap"][n]["se"], surv["teleport"][n]["se"]))
    meanD = float(np.mean(list(D.values())))
    se_mean = float(np.sqrt(sum(s ** 2 for s in seD.values())) / 3)
    outcome_a = meanD - 5 * se_mean > G["A_no_crossover_meanD_floor"]
    outcome_b = any(D[n] + 5 * seD[n] < 0 for n in (2, 4, 6))
    no_test = not (g1 and g2)
    verdict = ("NO-TEST" if no_test else
               "A_NO_CROSSOVER" if outcome_a else
               "B_CROSSOVER" if outcome_b else "AMBIGUOUS")

    law = {int(k): v for k, v in man["prefiled_law"].items()}
    fake = {int(k): v for k, v in man["prefiled_fake_swap"].items()}
    model_cmp = {n: {"measured": surv["swap"][n]["mean"], "law": law[n],
                     "fake": fake[n],
                     "closer_to": "law" if abs(surv["swap"][n]["mean"] - law[n])
                     < abs(surv["swap"][n]["mean"] - fake[n]) else "fake"}
                 for n in HOPS}

    out = {"survival": surv, "sentinels": sent, "drift_meter_swapN6p0": drift,
           "D_per_N": D, "meanD": meanD, "se_meanD": se_mean,
           "gates": {"G1": bool(g1), "G2": bool(g2)},
           "outcome_A": bool(outcome_a), "outcome_B": bool(outcome_b),
           "verdict": verdict, "swap_model_comparison": model_cmp}
    print(f"=== Exp110 GRADE (job {man['job_id']}, chain {man['chain'][:7]}...) ===")
    for arm in ("swap", "teleport"):
        print(f"  {arm:9s} " + "  ".join(
            f"N={n}: {surv[arm][n]['mean']:.4f}" for n in HOPS))
    print(f"  D(2,4,6) = " + ", ".join(f"{D[n]:+.4f}±{seD[n]:.4f}" for n in (2, 4, 6)))
    print(f"  meanD = {meanD:+.4f}±{se_mean:.4f} | sentinels {min(sent.values()):.3f}+ "
          f"| drift meter {drift:.4f}")
    print(f"  swap vs models: " + ", ".join(
        f"N{n}->{model_cmp[n]['closer_to']}" for n in HOPS))
    print(f"  gates G1={g1} G2={g2} | VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp110_grade.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp110_grade.json")


if __name__ == "__main__":
    main()
