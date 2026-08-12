#!/usr/bin/env python3
"""
Grade the Cell 5 pinned-placement + sensitivity flight. Boards #113 and #115.

Gates read from the FROZEN prereg quantum@d9983cb, not re-derived. Submits nothing; safe to re-run.

  G1  CONTROL MUST MOVE   |shift| >= 0.15 on control@BEST. Failure = NO-TEST, checked FIRST.
      NO keep bound on the control — it keeps ~0.98 BY CONSTRUCTION, and last flight I registered
      a bound it could not satisfy.
  G2  KEEP FRACTIONS      the six pigeonhole arms within [0.09, 0.16]
  G3  #113 PINNED TEST    all three pairs on BEST |bias| <= 0.06 AND sum < 0.50 vs in-code floor 1
  G4  #115 SENSITIVITY    per-placement bias for pair01, the spread, and whether the ordering
                          matches the picker's ranking. A MEASUREMENT, NOT A TEST — cannot fail.

Usage: QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell5_placement_grade_c5060.py <job_id>
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

G1_CONTROL_MIN = 0.15
G2_KEEP = (0.09, 0.16)
G3_PAIR_MAX = 0.06
G3_SUM_MAX = 0.50
PREREG = "quantum@d9983cb"
FLOWN_PRIOR = {"flownA": +0.09467, "flownB": -0.19872}   # what the unpinned flight read


def analyse(counts, shots):
    k0 = k1 = 0
    for b, v in counts.items():
        bits = b.replace(" ", "")
        if bits[-3:] == "000":
            if bits[-4] == "0":
                k0 += v
            else:
                k1 += v
    kept = k0 + k1
    if kept == 0:
        return {"kept": 0, "keep_frac": 0.0, "shift": float("nan"), "se": float("nan")}
    x = (k0 - k1) / kept
    return {"kept": kept, "keep_frac": kept / shots, "shift": x,
            "se": math.sqrt(max(1e-12, 1 - x * x) / kept)}


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 %s <job_id>" % sys.argv[0])
    jid = sys.argv[1]
    man_path = f"results/h13_cell5_placement_manifest_{jid}.json"
    man = json.load(open(man_path))
    shots, arms = man["shots"], man["arms"]

    from ibm_multi_account import assert_explicit_account, service_for_submission
    acct = assert_explicit_account()
    svc = service_for_submission(acct)
    job = svc.job(jid)
    st = str(job.status())
    print(f"job {jid}: {st}")
    if "DONE" not in st.upper():
        print("  not finished — nothing to grade. Safe to re-run; submits nothing.")
        return 2

    res = job.result()
    out = {"job_id": jid, "prereg": PREREG, "placements": man["placements"],
           "picker_best_score": man["picker_best_score"],
           "picker_worst_score": man["picker_worst_score"], "arms": {}}
    for name, r in zip(arms, res):
        d = r.data
        counts = (d.c.get_counts() if hasattr(d, "c") else list(d.values())[0].get_counts())
        out["arms"][name] = analyse(counts, shots)

    print("\n" + "═" * 78)
    print(f"H13 CELL 5 — PINNED PLACEMENT + SENSITIVITY, graded against {PREREG}")
    print("═" * 78)

    ctrl = out["arms"]["control@BEST"]
    g1 = abs(ctrl["shift"]) >= G1_CONTROL_MIN
    print(f"  G1 CONTROL MUST MOVE : |{ctrl['shift']:+.5f}| >= {G1_CONTROL_MIN} -> "
          f"{'PASS' if g1 else '🔴 NO-TEST'}   (keep {ctrl['keep_frac']:.4f}, no bound by design)")
    out["G1"] = bool(g1)
    if not g1:
        print("\n  🔴 NO-TEST — apparatus not demonstrated live; no pair or placement conclusions.")
        out["verdict"] = "NO-TEST"
        json.dump(out, open(f"results/h13_cell5_placement_grade_{jid}.json", "w"), indent=1)
        return 1

    pig = [a for a in arms if a != "control@BEST"]
    keeps = [out["arms"][a]["keep_frac"] for a in pig]
    g2 = all(G2_KEEP[0] <= k <= G2_KEEP[1] for k in keeps)
    print(f"  G2 KEEP FRACTIONS    : {[f'{k:.4f}' for k in keeps]} -> {'PASS' if g2 else '🔴 FAIL'}")

    print("\n  ── G3 · #113 THE PINNED TEST (all three pairs, ONE placement, equal gate count) ──")
    trio = [f"pair{p}@BEST" for p in ("01", "02", "12")]
    shifts = [out["arms"][a]["shift"] for a in trio]
    for a, s in zip(trio, shifts):
        print(f"     {a:16} {s:+.5f}  (bar |·| <= {G3_PAIR_MAX})")
    cal = abs(ctrl["shift"]) / 0.5
    probs = [abs(s) / cal for s in shifts]
    total = sum(probs)
    se_tot = math.sqrt(sum((out["arms"][a]["se"] / cal) ** 2 for a in trio))
    sigma = (1.0 - total) / se_tot if se_tot else float("inf")
    g3 = all(abs(s) <= G3_PAIR_MAX for s in shifts) and total < G3_SUM_MAX
    print(f"     sum {total:.5f} ± {se_tot:.5f} vs floor 1.0 -> {sigma:.1f}σ below classical")
    print(f"     G3: {'✅ PASS — CELL 5 REOPENS' if g3 else '🔴 FAIL — closes on an unconfounded measurement'}")

    print("\n  ── G4 · #115 PLACEMENT SENSITIVITY (pair01, equal gate count, one job) ──")
    print("     placement    bias        prior(unpinned)   qubits")
    sweep = {}
    for k in ("BEST", "WORST", "flownA", "flownB"):
        a = f"pair01@{k}"
        s = out["arms"][a]["shift"]
        sweep[k] = s
        prior = FLOWN_PRIOR.get(k)
        pr = f"{prior:+.5f}" if prior is not None else "     —   "
        print(f"     {k:9}   {s:+.5f}    {pr}        {man['placements'][k]}")
    spread = max(sweep.values()) - min(sweep.values())
    print(f"     SPREAD across placements: {spread:.5f}")
    print(f"     picker score  best {man['picker_best_score']:.4f}  worst {man['picker_worst_score']:.4f}")
    picker_predicts = abs(sweep["WORST"]) > abs(sweep["BEST"])
    print(f"     does the picker's ranking predict bias? "
          f"{'YES (|worst| > |best|)' if picker_predicts else 'NO — registered in advance as likely false'}")

    out.update({"G2": bool(g2), "G3_pass": bool(g3), "G3_sum": total, "G3_se": se_tot,
                "G3_sigma": sigma, "pair_shifts_BEST": shifts, "sweep": sweep,
                "spread": spread, "picker_predicts_bias": bool(picker_predicts)})
    out["verdict"] = "PASS" if (g1 and g2 and g3) else "FAIL"
    print(f"\n  VERDICT (#113): {out['verdict']}    ·    #115 is a measurement, reported above")
    os.makedirs("results", exist_ok=True)
    p = f"results/h13_cell5_placement_grade_{jid}.json"
    json.dump(out, open(p, "w"), indent=1)
    print(f"  wrote {p}")
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
