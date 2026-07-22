#!/usr/bin/env python3
"""Exp-HSS race flight DECODE — frozen order per exp-hss-race-flight-prereg-whisper-c4973.md:
(1) rung-0 lambda fit + gate (self-verifying: modal-based R, no reveal needed);
(2) ball-argmax s_hat on race rungs (mechanical, frozen statistic);
(3) STOP — print s_hat for public posting; reveal is opened by a SEPARATE step after posting.
Whisper C4973, substrate claude-fable-5."""
import json, math, os, sys
from collections import Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = json.load(open(os.path.join(HERE, "..", "results", "exp_hss_race_flight_manifest.json")))

from qiskit_ibm_runtime import QiskitRuntimeService

def get_counts(res_item):
    return res_item.data[list(res_item.data.keys())[0]].get_counts()

def ball_argmax(counts, n):
    """Radius-1 ball score for every observed string + its HD1 neighbors (frozen statistic)."""
    score = Counter()
    for s, c in counts.items():
        v = int(s, 2)
        score[v] += c
        for i in range(n):
            score[v ^ (1 << i)] += c
    best_v, best_score = score.most_common(1)[0]
    ranked = score.most_common(5)
    return format(best_v, f"0{n}b"), best_score, ranked

def main():
    svc = QiskitRuntimeService()
    job = svc.job(MAN["job_id"])
    res = job.result()
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        usage = {}

    meta = MAN["pubs_meta"]
    # ---- (1) RUNG-0: pooled counts per fold, modal-based R (self-verifying) ----
    fold_data = {}
    for i, m in enumerate(meta):
        if m["block"] != "rung0":
            continue
        c = get_counts(res[i])
        fd = fold_data.setdefault(m["fold_m"], {"d2q": m["d2q"], "counts": Counter(), "shots": 0})
        fd["counts"].update(c)
        fd["shots"] += m["shots"]
    rung0 = []
    modal_strings = set()
    for fm in sorted(fold_data):
        fd = fold_data[fm]
        modal, mc = fd["counts"].most_common(1)[0]
        R = mc / fd["shots"]
        rung0.append({"fold_m": fm, "d2q": fd["d2q"], "modal": modal, "modal_counts": mc,
                      "shots": fd["shots"], "R_modal": R})
        modal_strings.add(modal)
        print(f"rung0 m={fm} d2q={fd['d2q']} modal_counts={mc}/{fd['shots']} R={R:.4g} modal={modal[:12]}..")
    consistent = len(modal_strings) == 1
    print("rung0 modal CONSISTENT across folds:", consistent)
    # Poisson-weighted linear fit of ln R vs d2q (weights ~ counts)
    xs = np.array([r["d2q"] for r in rung0 if r["modal_counts"] >= 5])
    ys = np.array([math.log(r["R_modal"]) for r in rung0 if r["modal_counts"] >= 5])
    ws = np.array([r["modal_counts"] for r in rung0 if r["modal_counts"] >= 5])
    A = np.vstack([xs, np.ones_like(xs)]).T
    coef = np.linalg.lstsq(A * np.sqrt(ws)[:, None], ys * np.sqrt(ws), rcond=None)[0]
    lam = -coef[0]
    R194 = math.exp(coef[1] - lam * MAN["d2q_race40"])
    R218 = math.exp(coef[1] - lam * MAN["d2q_race32"])
    GATE = 5.1e-4
    gate40, gate32 = R194 >= GATE, R218 >= GATE
    print(f"lambda_fit={lam:.5f}/slot  R_pred(d2q=194)={R194:.4g}  R_pred(218)={R218:.4g}  "
          f"GATE(>=5.1e-4): n40={'PASS' if gate40 else 'FOLD'} n32={'PASS' if gate32 else 'FOLD'}")

    out = {"card": "exp_hss_race_decode_stage1", "cycle": "C4973",
           "substrate": "claude-fable-5", "job_id": MAN["job_id"], "usage": usage,
           "rung0": rung0, "rung0_modal_consistent": consistent,
           "lambda_fit_per_slot": lam, "R_pred_race40": R194, "R_pred_race32": R218,
           "gate_threshold": GATE, "gate_race40": gate40, "gate_race32": gate32}

    # ---- (2) race rungs: ball argmax (only for rungs whose gate PASSED) ----
    for block, n, gate_ok in (("race_n40", 40, gate40), ("race_n32", 32, gate32)):
        pooled, shots = Counter(), 0
        for i, m in enumerate(meta):
            if m["block"] != block:
                continue
            pooled.update(get_counts(res[i]))
            shots += m["shots"]
        if not gate_ok:
            out[block] = {"gated": "FOLD — race rung DISCARDED UNGRADED per card"}
            print(block, "GATED OUT — not decoded")
            continue
        modal, modal_c = pooled.most_common(1)[0]
        s_hat, ball, ranked = ball_argmax(pooled, n)
        # diffuse-null sanity for the ball at 2^n (informational; structured null per card note)
        out[block] = {"shots": shots, "modal": modal, "modal_counts": modal_c,
                      "s_hat_ball": s_hat, "ball_score": ball,
                      "ball_top5": [(format(v, f'0{n}b'), int(c)) for v, c in ranked],
                      "peak_counts_at_s_hat": pooled.get(s_hat, 0)}
        print(f"{block}: s_hat={s_hat} ball={ball} modal_counts={modal_c} shots={shots}")

    path = os.path.join(HERE, "..", "results", "exp_hss_race_decode_stage1.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path))
    print("STAGE 1 COMPLETE — post s_hat publicly BEFORE opening the sealed reveal.")

if __name__ == "__main__":
    main()
