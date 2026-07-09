#!/usr/bin/env python3
"""Exp105 grade — FROZEN pre-reg rule applied mechanically (Whisper C4526, first
post-drain cycle per the pre-reg; Ember owns pred_c4117_001 resolution + finding doc).

Frozen rule (experiments/exp105-causal-game-preregistration.md, commit 3dd64f3):
  1. sentinel gate: min replicate DISC >= +1.60 ; null gate: weighted null < 0.70
     (either fails -> NO-TEST, not a loss)
  2. WIN  iff p_hat - 5*SE_w > 0.8695
  3. LOSS iff p_hat + 5*SE_w < 0.8695 (gates passing)
  4. else UNDERPOWERED/AMBIGUOUS

Conventions from Ember's frozen code (exp105_causal_game_feasibility.py):
  P(+) = counts['0']/shots (control readout H, bit 0);  succ_k = P(+) if commuting
  else 1-P(+);  <X_c> = 2*P(+)-1;  replicate DISC = <X_c>_commute - <X_c>_anticommute.
All weights/constants read from the job manifest (results/exp105_jobids.json).
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_ap = argparse.ArgumentParser()
_ap.add_argument("--tag", default="exp105", help="manifest tag (exp105b = fez replication)")
_ARGS = _ap.parse_args()
MANIFEST = os.path.join(HERE, "..", "results", f"{_ARGS.tag}_jobids.json")
OUT = os.path.join(HERE, "..", "results", f"{_ARGS.tag}_hw_results.json")


def get_counts(pub_result):
    db = pub_result.data
    for name in ("c", "meas", "c0"):
        if hasattr(db, name):
            return getattr(db, name).get_counts()
    vals = list(getattr(db, "values", lambda: [])())
    if vals:
        return vals[0].get_counts()
    raise RuntimeError("no classical register found on pub result")


def main():
    man = json.load(open(MANIFEST))
    jid = man["job_id"]
    metas = man["metas"]
    grade_const = man["grade_constant"]
    sent_min = man["sentinel_min_disc"]
    null_max = man["null_gate_max"]

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    job = svc.job(jid)
    status = str(job.status())
    print(f"job {jid}: {status}")
    if "DONE" not in status.upper() and "Completed" not in status:
        print("not done — no grade")
        return 1
    res = job.result()
    assert len(res) == len(metas), f"PUB count mismatch {len(res)} vs {len(metas)}"

    rows = []
    for i, m in enumerate(metas):
        counts = get_counts(res[i])
        shots = m["shots"]
        p_plus = counts.get("0", 0) / shots
        rows.append({**m, "p_plus": p_plus})

    # --- sentinel gate: 3 replicates, DISC = <Xc>_commute - <Xc>_anti, gate on MIN
    sent = {r["label"]: 2 * r["p_plus"] - 1 for r in rows if r["kind"] == "sentinel"}
    discs = {}
    for rep in ("start", "mid", "end"):
        discs[rep] = sent[f"sent_{rep}_commute"] - sent[f"sent_{rep}_anticommute"]
    min_disc = min(discs.values())
    sent_pass = min_disc >= sent_min
    print(f"sentinel DISC start/mid/end = {discs['start']:+.4f} / {discs['mid']:+.4f} "
          f"/ {discs['end']:+.4f}  min={min_disc:+.4f}  gate(>= {sent_min:+.2f}): "
          f"{'PASS' if sent_pass else 'FAIL -> NO-TEST'}")

    # --- null gate: weighted success of definite-order arm
    null_rows = [r for r in rows if r["kind"] == "null"]
    wsum_n = sum(r["q"] for r in null_rows)
    p_null = sum(r["q"] * (r["p_plus"] if r["commuting"] else 1 - r["p_plus"])
                 for r in null_rows) / wsum_n
    null_pass = p_null < null_max
    print(f"null arm weighted success = {p_null:.4f}  gate(< {null_max}): "
          f"{'PASS' if null_pass else 'FAIL -> NO-TEST'}  "
          f"(sim 0.6139; commuting prior 0.6165)")

    # --- game estimator
    game_rows = [r for r in rows if r["kind"] == "game"]
    wsum = sum(r["q"] for r in game_rows)
    print(f"game pairs: {len(game_rows)}, q-sum = {wsum:.6f} (expect ~1)")
    p_hat = sum(r["q"] * (r["p_plus"] if r["commuting"] else 1 - r["p_plus"])
                for r in game_rows) / wsum
    var = sum((r["q"] / wsum) ** 2
              * (lambda s: s * (1 - s))(r["p_plus"] if r["commuting"] else 1 - r["p_plus"])
              / r["shots"] for r in game_rows)
    se_w = math.sqrt(var)
    lo5, hi5 = p_hat - 5 * se_w, p_hat + 5 * se_w
    print(f"\np_hat = {p_hat:.6f}   SE_w = {se_w:.6f}")
    print(f"p_hat - 5*SE_w = {lo5:.6f}   vs grade constant {grade_const}")

    if not (sent_pass and null_pass):
        verdict = "NO-TEST"
    elif lo5 > grade_const:
        verdict = "WIN"
    elif hi5 < grade_const:
        verdict = "LOSS"
    else:
        verdict = "UNDERPOWERED/AMBIGUOUS"
    margin_sigma = (p_hat - grade_const) / se_w if se_w > 0 else float("inf")
    print(f"\n*** VERDICT (frozen rule): {verdict} ***")
    print(f"    margin over bound: {p_hat - grade_const:+.6f} = {margin_sigma:.1f} sigma")

    # per-class and worst pairs for the finding doc
    per_class = {}
    for cls, flag in (("commuting", True), ("anticommuting", False)):
        rr = [r for r in game_rows if r["commuting"] == flag]
        w = sum(r["q"] for r in rr)
        per_class[cls] = sum(r["q"] * (r["p_plus"] if flag else 1 - r["p_plus"])
                             for r in rr) / w
    print(f"per-class success: commuting {per_class['commuting']:.4f}, "
          f"anticommuting {per_class['anticommuting']:.4f}")
    worst = sorted(game_rows, key=lambda r: (r["p_plus"] if r["commuting"]
                                             else 1 - r["p_plus"]))[:5]
    for r in worst:
        s = r["p_plus"] if r["commuting"] else 1 - r["p_plus"]
        print(f"  worst: {r['pair']:24s} succ={s:.4f} (q={r['q']})")

    out = {
        "job_id": jid, "graded_by": f"whisper (frozen rule, mechanical, tag={_ARGS.tag})",
        "sentinel_disc": discs, "sentinel_min": min_disc, "sentinel_pass": sent_pass,
        "null_weighted_success": p_null, "null_pass": null_pass,
        "p_hat": p_hat, "se_w": se_w, "p_hat_minus_5se": lo5,
        "grade_constant": grade_const, "verdict": verdict,
        "margin_sigma": margin_sigma, "per_class": per_class,
        "rows": rows,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nSaved {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
