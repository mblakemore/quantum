#!/usr/bin/env python3
"""Exp-HSS RACE 4 — frozen decode (card docs/exp-hss-race5-prereg-FROZEN-whisper-c4980.md).
Whisper C4979, substrate claude-fable-5. BLIND: counts only; never reads seals.

GRADED statistic: CALIBRATED PER-BIT MAJORITY — s_hat_i = 1 iff frac_i > t_i where
t_i = (p01_i + 1 - p10_i)/2 from the co-batched whole-chip cal block (per flown physical qubit).
Chase-12/soft = reported DIAGNOSTICS only (amendment, 3-of-3). Flagged bits (|t_i-0.5| > 0.02)
listed in the stage output BEFORE reveals. s_hat in s_str display order, 0-indexed positions.
"""
import json, os, sys
from collections import Counter
from itertools import combinations
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
MAN = json.load(open(os.path.join(RES, "exp_hss_race5_flight_manifest.json")))
NPHYS = 156
K_CHASE, RHO, SOFT_ITERS = 12, 0.5, 8


def get_counts(res_item):
    return res_item.data[list(res_item.data.keys())[0]].get_counts()


def readout_cal(res, meta):
    """Per-physical-qubit p01 (read1|prep0) and p10 (read0|prep1) from the cal block."""
    p01 = np.zeros(NPHYS); p10 = np.zeros(NPHYS)
    for i, m in enumerate(meta):
        if m["block"] not in ("cal_all0", "cal_all1"):
            continue
        ones = np.zeros(NPHYS); tot = 0
        for s, c in get_counts(res[i]).items():
            s = s.replace(" ", "")
            ones += c * (np.frombuffer(s.encode(), np.uint8).astype(np.int64) - 48)
            tot += c
        frac1 = ones / tot                    # string index j corresponds to qubit NPHYS-1-j
        perq = frac1[::-1]                    # now index q = qubit q
        if m["block"] == "cal_all0":
            p01 = perq.copy()
        else:
            p10 = 1.0 - perq
    return p01, p10


def marginalize(counts, layout):
    idx = [NPHYS - 1 - p for p in layout]
    out = Counter()
    for s, c in counts.items():
        out["".join(s[i] for i in idx)] += c
    return out


def block_thresholds(layout, p01, p10):
    """t_i in MARGINAL order (marginal index j = virtual qubit j = physical layout[j])."""
    return np.array([(p01[q] + 1 - p10[q]) / 2 for q in layout])


def decode(counts, n, t_marg):
    """Graded: calibrated majority. Diagnostics: chase12+soft (raw 0.5-threshold lineage)."""
    S = len(counts)
    A = np.empty((S, n), dtype=np.int8)
    c = np.empty(S, dtype=np.float64)
    for i, (s, cnt) in enumerate(counts.items()):
        A[i] = np.frombuffer(s.encode(), np.uint8).astype(np.int8) - 48
        c[i] = cnt
    tot = c.sum()
    frac = (c @ A) / tot
    graded = (frac > t_marg).astype(np.int8)                    # GRADED
    # diagnostics: raw chase (race-3 lineage, unchanged)
    mhat = (frac > 0.5).astype(np.int8)
    order = np.argsort(np.abs(frac - 0.5))
    weak, strong = order[:K_CHASE], order[K_CHASE:]
    hd_strong = (A[:, strong] != mhat[strong]).sum(1)
    pow2 = (1 << np.arange(K_CHASE)).astype(np.int64)
    w_int = (A[:, weak].astype(np.int64)) @ pow2
    u = np.zeros(1 << K_CHASE)
    np.add.at(u, w_int, c * (RHO ** hd_strong))
    pc = np.array([bin(x).count("1") for x in range(1 << K_CHASE)])
    rho_pc = RHO ** pc
    scores = np.array([u @ rho_pc[np.arange(1 << K_CHASE) ^ p] for p in range(1 << K_CHASE)])
    best = mhat.copy()
    best[weak] = ((int(np.argmax(scores)) >> np.arange(K_CHASE)) & 1).astype(np.int8)
    est = best
    for _ in range(SOFT_ITERS):
        w_s = c * (RHO ** (A != est).sum(1))
        new = ((w_s @ A) / w_s.sum() > 0.5).astype(np.int8)
        if (new == est).all():
            break
        est = new
    to_disp = lambda arr: "".join(str(int(b)) for b in arr)[::-1]
    return {
        "s_hat_GRADED_calibrated_majority": to_disp(graded),
        "diag_raw_majority": to_disp(mhat),
        "diag_chase_soft": to_disp(est),
        "shots": int(tot),
        "n_bits_where_calibration_flipped_decision": int((graded != mhat).sum()),
        "min_margin_vs_t": float(np.abs(frac - t_marg).min()),
        "bit_frac_marginal_order": [round(float(x), 5) for x in frac],
    }


def main(stage):
    from qiskit_ibm_runtime import QiskitRuntimeService
    job = QiskitRuntimeService().job(MAN["job_id"])
    res = job.result()
    try:
        usage = job.metrics().get("usage", {})
    except Exception:
        usage = {}
    meta = MAN["pubs_meta"]
    p01, p10 = readout_cal(res, meta)
    lay = MAN["layouts"]
    out = {"card": "exp_hss_race5_decode", "cycle": "C4980", "substrate": "claude-fable-5",
           "job_id": MAN["job_id"], "usage": usage, "stage": stage,
           "decoder": MAN["decoder_frozen"], "depth_cap": MAN["depth_cap"],
           "advantage_eligible": MAN["advantage_eligible"], "rows": [],
           "flagged_bits": {}}
    # pre-reveal flag list per register (card: |t_i - 0.5| > 0.02), display-order 0-indexed
    for tag, key in (("rung0_base", "rung0_base"), ("twin40_src", "twin40_src"),
                     ("race_n40", "race_n40")):
        t_marg = block_thresholds(lay[key]["final"], p01, p10)
        n = len(t_marg)
        flags = [{"pos_display": n - 1 - j, "physical": lay[key]["final"][j],
                  "t": round(float(t_marg[j]), 4)}
                 for j in range(n) if abs(t_marg[j] - 0.5) > 0.02]
        out["flagged_bits"][tag] = flags

    def run_block(block, laykey, n, fm=None, subs=None):
        t_marg = block_thresholds(lay[laykey]["final"], p01, p10)
        idxs = [i for i, m in enumerate(meta) if m["block"] == block and
                (fm is None or m.get("fold_m") == fm)]
        seq = [(None, idxs)] if subs is None else [(np_, idxs[:np_]) for np_ in subs]
        for np_, ix in seq:
            pooled = Counter()
            for i in ix:
                pooled.update(marginalize(get_counts(res[i]), lay[laykey]["final"]))
            d = decode(pooled, n, t_marg)
            row = {"block": block + (f"_m{fm}" if fm is not None else ""),
                   "npubs": np_, "d2q": meta[ix[0]]["d2q"], **d}
            out["rows"].append(row)
            print(f"{row['block']}@{np_} d2q={row['d2q']} shots={d['shots']} "
                  f"flips={d['n_bits_where_calibration_flipped_decision']} "
                  f"s_hat={d['s_hat_GRADED_calibrated_majority']}")

    if stage == "gate":
        run_block("ladder", "rung0_base", 40, fm=0)
        run_block("ladder", "rung0_base", 40, fm=1)
        run_block("twin40", "twin40_src", 40, subs=MAN["subsample_pubs"]["twin40"])
        path = os.path.join(RES, "exp_hss_race5_gate_shat.json")
    else:
        run_block("race_n40", "race_n40", 40, subs=MAN["subsample_pubs"]["race_n40"])
        path = os.path.join(RES, "exp_hss_race5_race_shat.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path), "— POST s_hat + flagged bits before reveals.")


if __name__ == "__main__":
    main("race" if "--race" in sys.argv else "gate")
