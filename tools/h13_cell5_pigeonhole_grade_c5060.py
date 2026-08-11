#!/usr/bin/env python3
"""
H13 Cell 5 pigeonhole — GRADE a completed job. SEPARATE FROM THE FLIGHT SCRIPT, DELIBERATELY.

WHY THIS IS ITS OWN FILE (C5060, learned the hard way ninety minutes ago). The flight script
submitted AND analysed in one process, so when the job sat in the queue past my 30-minute timeout
the process took SIGTERM and the analysis died with it. NOTHING WAS ACTUALLY LOST — the prereg was
frozen, the job id was published, and results are retrievable by id — but the coupling made a
QUEUE DELAY look like a FAILED EXPERIMENT, and it would have re-run a paid submission to recover
an analysis that needed no QPU at all.

A SUBMISSION IS IRREVERSIBLE AND AN ANALYSIS IS FREE. Binding them in one process gives the
analysis the submission's failure modes and gives the submission the analysis's runtime.

Gates and thresholds are read from the FROZEN prereg (quantum@499cc2b), not re-derived here.

Usage:
  QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell5_pigeonhole_grade_c5060.py <job_id>
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# ── FROZEN (prereg quantum@499cc2b) — mirrored, never recomputed ──────────────────────────────
EPS = 0.25
SHOTS = 20000
PAIRS = [(0, 1), (0, 2), (1, 2)]
ARM_ORDER = ["control", "pair01", "pair02", "pair12"]
G1_CONTROL_MIN = 0.15
G2_PAIR_MAX = 0.06
G3_SUM_MAX = 0.50
G4_KEEP = (0.09, 0.16)
PREREG = "quantum@499cc2b"


def classical_floor():
    best = None
    for a in range(8):
        boxes = [(a >> i) & 1 for i in range(3)]
        shared = sum(1 for (j, k) in PAIRS if boxes[j] == boxes[k])
        best = shared if best is None else min(best, shared)
    return float(best)


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
        sys.exit("usage: QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell5_pigeonhole_grade_c5060.py <job_id>")
    jid = sys.argv[1]
    from ibm_multi_account import assert_explicit_account, service_for_submission
    acct = assert_explicit_account()          # a READ, but the account is still named explicitly
    svc = service_for_submission(acct)
    job = svc.job(jid)
    st = str(job.status())
    print(f"job {jid} on {acct}: {st}")
    if "DONE" not in st.upper():
        print("  not finished — nothing to grade. This script is safe to re-run; it submits nothing.")
        return 2

    res = job.result()
    floor = classical_floor()
    out = {"job_id": jid, "account": acct, "prereg": PREREG, "eps": EPS, "shots": SHOTS,
           "classical_floor": floor, "arms": {}}
    for name, r in zip(ARM_ORDER, res):
        d = r.data
        counts = (d.c.get_counts() if hasattr(d, "c") else list(d.values())[0].get_counts())
        out["arms"][name] = analyse(counts, SHOTS)

    print("\n" + "═" * 78)
    print(f"H13 CELL 5 PIGEONHOLE — GRADE against {PREREG}")
    print(f"  classical floor, enumerated in-code: sum of pair-probabilities >= {floor}")
    print("═" * 78)

    ctrl = out["arms"]["control"]
    g1 = abs(ctrl["shift"]) >= G1_CONTROL_MIN
    print(f"  G1 CONTROL MUST MOVE : |{ctrl['shift']:+.5f}| >= {G1_CONTROL_MIN} -> "
          f"{'PASS' if g1 else '🔴 NO-TEST'}  (keep {ctrl['keep_frac']:.4f})")
    out["G1_control_moves"] = bool(g1)
    if not g1:
        print("\n  🔴 NO-TEST — the apparatus is not demonstrated live, so the three pair readings")
        print("     are UNINTERPRETABLE and are NOT reported as a pigeonhole result. As registered.")
        out["verdict"] = "NO-TEST"
        json.dump(out, open(f"results/h13_cell5_pigeonhole_{jid}.json", "w"), indent=1)
        return 1

    keeps = [out["arms"][a]["keep_frac"] for a in ARM_ORDER]
    g4 = all(G4_KEEP[0] <= k <= G4_KEEP[1] for k in keeps)
    print(f"  G4 KEEP FRACTIONS    : {[f'{k:.4f}' for k in keeps]} in {G4_KEEP} -> "
          f"{'PASS' if g4 else '🔴 FAIL'}")

    shifts = [out["arms"][f"pair{p[0]}{p[1]}"]["shift"] for p in PAIRS]
    g2 = all(abs(s) <= G2_PAIR_MAX for s in shifts)
    print(f"  G2 EACH PAIR NULL    : {[f'{s:+.5f}' for s in shifts]} all |.|<={G2_PAIR_MAX} -> "
          f"{'PASS' if g2 else '🔴 FAIL'}")

    cal = abs(ctrl["shift"]) / 0.5      # control's known weak value is 0.5 -> pointer calibration
    probs = [abs(s) / cal for s in shifts]
    total = sum(probs)
    se_tot = math.sqrt(sum((out["arms"][f"pair{p[0]}{p[1]}"]["se"] / cal) ** 2 for p in PAIRS))
    sigma = (floor - total) / se_tot if se_tot else float("inf")
    g3 = total < G3_SUM_MAX and sigma >= 5
    print(f"  G3 HEADLINE (SUM)    : {total:.5f} +- {se_tot:.5f} vs floor {floor} -> "
          f"{sigma:.1f} sigma, {'PASS' if g3 else '🔴 FAIL'}")
    print(f"     per-pair 'same box' probabilities: {[f'{p:.5f}' for p in probs]}")

    out.update({"G2_pairs_null": bool(g2), "G3_sum": total, "G3_se": se_tot, "G3_sigma": sigma,
                "G3_pass": bool(g3), "G4_keep": bool(g4), "pair_probabilities": probs,
                "calibration_from_control": cal})
    verdict = "PASS" if (g1 and g2 and g3 and g4) else "FAIL"
    out["verdict"] = verdict
    print(f"\n  VERDICT: {verdict}")
    os.makedirs("results", exist_ok=True)
    path = f"results/h13_cell5_pigeonhole_{jid}.json"
    json.dump(out, open(path, "w"), indent=1)
    print(f"  wrote {path}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
