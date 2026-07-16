#!/usr/bin/env python3
"""Exp142 FROZEN GRADER — Whisper C4746. SHA256 of this file is recorded in the
pre-registration at freeze. No edits post-freeze; post-flight bugs are reported
alongside results, never patched silently.

Grades per-n WIN/LOSS/NULL per prereg section 5:
  WIN  = both arms' P_hat match Ember's sealed P (hash-verified)
         AND quantum_shots_budget == frozen budget 5 * M99_IDEAL[n] (conformity)
         AND (conventional_meter_median / (5 * M99_IDEAL[n])) >= R_THRESHOLD[n]
  LOSS = quantum arm wrong, OR ratio < R_THRESHOLD[n] with both arms correct
  Ratio denominator = FULL frozen quantum budget (Elder C6490 pre-freeze NACK):
  apples-to-apples with the R(n) formula and strictly conservative. The quantum
  stable-prefix meter is reported alongside as a secondary observable, never in
  the graded ratio.
  NULL = conventional arm failed to identify (transcript exhausted, no acceptance)
Overall WIN = n=8 wins AND >=3 of 4 rungs win.

Usage: python3 exp142_grader.py <commitments_dir> <answers_dir>
  commitments_dir: commitment_{ens}_n{N}.json + reveal_{ens}_n{N}.json (post-reveal)
  answers_dir:     answers_n{N}.json with
    {"n": N,
     "quantum": {"P_hat": "XZY...", "shots_budget": int, "meter": int},
     "conventional": {"P_hat": "XZY..." | null, "meter_median": float | null,
                       "identified": bool, "overage_submitted": int}}
"""
import glob
import hashlib
import json
import os
import sys

ENSEMBLE = "fullweight_eps1"
NS = (4, 6, 8, 10)

# ---- FROZEN CONSTANTS (filled from Gate-2 sim outputs at freeze) ----
M99_IDEAL = {4: None, 6: None, 8: None, 10: None}   # FREEZE-FILL
R_THRESHOLD = {4: None, 6: None, 8: None, 10: None} # FREEZE-FILL
# ---------------------------------------------------------------------


def verify_commitment(commit_path, reveal_path):
    with open(commit_path) as f:
        c = json.load(f)
    with open(reveal_path) as f:
        r = json.load(f)
    preimage = bytes.fromhex(r["salt_hex"]) + \
        f"exp142|{r['ensemble']}|{r['n']}|{r['P']}".encode()
    digest = hashlib.sha256(preimage).hexdigest()
    ok = (digest == c["sha256"]) and (c.get("ensemble") == r["ensemble"]) \
        and (int(c["n"]) == int(r["n"]))
    return ok, r["P"]


def grade_n(n, true_P, ans):
    q, c = ans["quantum"], ans["conventional"]
    q_correct = (q["P_hat"] == true_P)
    if not q_correct:
        return "LOSS", "quantum arm wrong P_hat"
    if q["shots_budget"] != 5 * M99_IDEAL[n]:
        return "LOSS", (f"quantum budget {q['shots_budget']} != frozen "
                        f"5 x m99_ideal = {5 * M99_IDEAL[n]} (conformity, prereg s5 cond 2)")
    if not c.get("identified", False) or c.get("P_hat") is None:
        return "NULL", "conventional arm failed to identify (ratio reported as lower bound)"
    c_correct = (c["P_hat"] == true_P)
    if not c_correct:
        return "NULL", "conventional arm misidentified (graded as conventional failure)"
    ratio = c["meter_median"] / (5 * M99_IDEAL[n])
    secondary = f"(secondary: q stable-prefix meter {q['meter']}, " \
                f"prefix-ratio {c['meter_median'] / q['meter']:.1f})"
    if ratio >= R_THRESHOLD[n]:
        return "WIN", f"ratio {ratio:.1f} >= {R_THRESHOLD[n]} {secondary}"
    return "LOSS", f"ratio {ratio:.1f} < {R_THRESHOLD[n]} with both arms correct {secondary}"


def main():
    if any(v is None for v in list(M99_IDEAL.values()) + list(R_THRESHOLD.values())):
        print("GRADER NOT FROZEN: constants unfilled")
        return 2
    commits_dir, answers_dir = sys.argv[1], sys.argv[2]
    verdicts = {}
    for n in NS:
        cpath = os.path.join(commits_dir, f"commitment_{ENSEMBLE}_n{n}.json")
        rpath = os.path.join(commits_dir, f"reveal_{ENSEMBLE}_n{n}.json")
        apath = os.path.join(answers_dir, f"answers_n{n}.json")
        ok, true_P = verify_commitment(cpath, rpath)
        if not ok:
            verdicts[n] = ("INVALID", "commitment hash mismatch — protocol breach")
            continue
        with open(apath) as f:
            ans = json.load(f)
        verdicts[n] = grade_n(n, true_P, ans)
    wins = [n for n, (v, _) in verdicts.items() if v == "WIN"]
    overall = "WIN" if (8 in wins and len(wins) >= 3) else "NOT-WIN"
    out = {"per_n": {str(n): {"verdict": v, "reason": r}
                     for n, (v, r) in verdicts.items()},
           "overall": overall,
           "constants": {"M99_IDEAL": M99_IDEAL, "R_THRESHOLD": R_THRESHOLD}}
    print(json.dumps(out, indent=2))
    return 0 if overall == "WIN" else 1


if __name__ == "__main__":
    sys.exit(main())
