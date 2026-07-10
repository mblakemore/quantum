#!/usr/bin/env python3
"""Exp106 grade — frozen rule applied mechanically (first post-drain cycle).
Rule (exp106-capacity-activation-preregistration.md, frozen pre-submission):
  1. sentinel min replicate DISC >= +1.60 else NO-TEST
  2. null |D| + 5*SE_D < 0.05 else NO-TEST
  3. WIN iff Rbar_switch - 5*SE_R > 0.10 ; LOSS iff Rbar + 5*SE < 0.10 ; else AMBIGUOUS
  5. consistency (ungraded): P(+) in 0.625±0.05 both inputs; |D_switch| < 0.05; MI vs 0.0489
Analysis functions imported from the frozen experiment module."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp106_capacity_activation import analyze, mutual_info_bits  # frozen module

MANIFEST = os.path.join(HERE, "..", "results", "exp106_jobids.json")
OUT = os.path.join(HERE, "..", "results", "exp106_hw_results.json")


def get_counts(pub_result):
    db = pub_result.data
    for name in ("c", "meas", "c0"):
        if hasattr(db, name):
            return getattr(db, name).get_counts()
    raise RuntimeError("no classical register found")


def main():
    man = json.load(open(MANIFEST))
    jid = man["job_id"]
    metas = man["metas"]
    g = man["gates"]

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    job = svc.job(jid)
    print(f"job {jid}: {job.status()}")
    res = job.result()
    assert len(res) == len(metas)

    counts_by_label = {}
    for i, m in enumerate(metas):
        counts_by_label[m["label"]] = get_counts(res[i])

    # sentinel gate
    sent = {m["label"]: 2 * (counts_by_label[m["label"]].get("0", 0) / m["shots"]) - 1
            for m in metas if m["kind"] == "sentinel"}
    discs = {rep: sent[f"sent_{rep}_commute"] - sent[f"sent_{rep}_anticommute"]
             for rep in ("start", "mid", "end")}
    min_disc = min(discs.values())
    sent_pass = min_disc >= g["sentinel_min_disc"]
    print(f"sentinel DISC start/mid/end = {discs['start']:+.4f}/{discs['mid']:+.4f}/"
          f"{discs['end']:+.4f}  min={min_disc:+.4f}  gate: "
          f"{'PASS' if sent_pass else 'FAIL -> NO-TEST'}")

    st = analyze(counts_by_label)
    mi_sw = mutual_info_bits(counts_by_label, "switch")
    mi_nu = mutual_info_bits(counts_by_label, "null")

    null_stat = abs(st["null"]["D"]) + 5 * st["null"]["SE_D"]
    null_pass = null_stat < g["null_D_band"]
    print(f"null:   D = {st['null']['D']:+.5f}  SE_D = {st['null']['SE_D']:.5f}  "
          f"|D|+5SE = {null_stat:.5f}  gate(<{g['null_D_band']}): "
          f"{'PASS' if null_pass else 'FAIL -> NO-TEST'}   MI_null = {mi_nu:.5f} bits")

    Rbar, se = st["switch"]["Rbar"], st["switch"]["SE"]
    lo, hi = Rbar - 5 * se, Rbar + 5 * se
    print(f"\nswitch: Rbar = {Rbar:+.5f}  SE = {se:.5f}  Rbar-5SE = {lo:+.5f} "
          f"vs floor {g['win_floor']}  (theory 0.5333, FakeMarrakesh 0.510)")
    print(f"        R(b0) = {st['switch']['R_b0']:+.5f}  R(b1) = {st['switch']['R_b1']:+.5f} "
          f"(theory ±0.5333)")

    if not (sent_pass and null_pass):
        verdict = "NO-TEST"
    elif lo > g["win_floor"]:
        verdict = "WIN"
    elif hi < g["win_floor"]:
        verdict = "LOSS"
    else:
        verdict = "AMBIGUOUS"
    print(f"\n*** VERDICT (frozen rule): {verdict} ***  "
          f"({(Rbar - g['win_floor']) / se:.1f} sigma over the floor; "
          f"{Rbar / se:.1f} sigma over the causal value 0)")

    # consistency checks (ungraded)
    pp = (st["switch"]["p_plus_b0"], st["switch"]["p_plus_b1"])
    c1 = all(abs(p - 0.625) < 0.05 for p in pp)
    c2 = abs(st["switch"]["D"]) < 0.05
    print(f"\nconsistency: P(+) = {pp[0]:.4f}/{pp[1]:.4f} (0.625±0.05: "
          f"{'OK' if c1 else 'VIOLATION'});  D_switch = {st['switch']['D']:+.5f} "
          f"(info-in-correlation-only: {'OK' if c2 else 'VIOLATION'})")
    print(f"MI_switch = {mi_sw:.5f} bits  (ideal 0.0489; FakeMarrakesh 0.0448)  "
          f"MI_null = {mi_nu:.5f}")

    json.dump({"job_id": jid, "graded_by": "whisper-C4530 (frozen rule, mechanical)",
               "sentinel_disc": discs, "sentinel_pass": sent_pass,
               "null": st["null"], "null_pass": null_pass, "switch": st["switch"],
               "mi_switch_bits": mi_sw, "mi_null_bits": mi_nu,
               "verdict": verdict, "consistency_pplus_ok": c1,
               "consistency_Dswitch_ok": c2},
              open(OUT, "w"), indent=1)
    print(f"\nSaved {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
