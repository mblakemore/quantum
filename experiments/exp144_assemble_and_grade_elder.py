#!/usr/bin/env python3
"""Exp144 FINAL GRADE assembly + run (Elder) — per chair C4821 rulings.

Assembles the 15 answers_n{N}_k{K}.json from COMMITTED artifacts ONLY (no fitting),
stages a commits dir the frozen grader reads (commit_/reveal_ prefixes), and runs
exp144_grader.py (sha db2843ee, selftest PASS). Verdict = grader JSON stdout, verbatim.

Chair C4821 encodings:
  QUANTUM n4,n6 (k1..5): terms = c4789 top3_fw; coeffs = implied_c × SIGNS
    (committed 4315f410, 2-of-2 vs Whisper); shots_budget = 5*M_BELL = 5000.
  QUANTUM n8 (k1..5): terms = c4789 top3_fw; coeffs = UNSIGNED implied_c (magnitudes),
    support_only=true. §5 PASS needs SIGNED coeffs within τ → every n8 has a negative
    true coeff (verified) → NOT-PASS by construction. No signed-vector claim at n8.
  CONV (all): identified=false, terms=null, coeffs=null, meter=null (no ratio ever) +
    status string + overage_submitted (DISCLOSURE ONLY — grader ignores it, not in output).
    n4 DETECTOR_FALSIFIED (C4810/C4811) · n6 HALTED_EARLY_STOP (C4810.2, 43740) ·
    n8 UNMETERED_DEVIATED (C4785.2).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
COM = os.path.join(HERE, "exp144_commitments")
REV = os.path.join(HERE, "exp144_reveals")
SUP = json.load(open(os.path.join(HERE, "../results/exp144_w1_fwfilter_secondary_whisper_c4789.json")))
SIGNS = json.load(open(os.path.join(HERE, "../results/exp144_signwave_real_signs_elder.json")))
M_BELL = 1000
BUDGET = 5 * M_BELL

CONV = {
    4: {"status": "DETECTOR_FALSIFIED (C4810/C4811)", "overage_submitted": None},   # disclosure TBD-Ember
    6: {"status": "HALTED_EARLY_STOP (C4810.2)",       "overage_submitted": 43740},
    8: {"status": "UNMETERED_DEVIATED (C4785.2)",      "overage_submitted": None},   # disclosure TBD-Ember
}


def signs_for(key):
    return {t["term"]: t["sign"] for t in SIGNS["instances"][key]["terms"]}


def build_answer(n, k):
    key = f"n{n}_k{k}"
    e = SUP[key]
    terms = list(e["top3_fw"])
    mags = list(e["implied_c"])
    if n in (4, 6):
        sg = signs_for(key)
        coeffs = [(m if sg[t] == "+" else -m) for t, m in zip(terms, mags)]
        quantum = {"terms": terms, "coeffs": coeffs, "shots_budget": BUDGET}
    else:  # n8 — support-only, UNSIGNED magnitudes, no signed-vector claim
        quantum = {"terms": terms, "coeffs": list(mags), "shots_budget": BUDGET,
                   "support_only": True}
    conv = {"identified": False, "terms": None, "coeffs": None, "meter": None,
            "status": CONV[n]["status"], "overage_submitted": CONV[n]["overage_submitted"]}
    return {"n": n, "instance": k, "quantum": quantum, "conventional": conv}


def main():
    with tempfile.TemporaryDirectory() as td:
        cdir = os.path.join(td, "commits"); adir = os.path.join(td, "answers")
        os.makedirs(cdir); os.makedirs(adir)
        # stage commit_/reveal_ the grader expects (commitments use 'commitment_' prefix)
        for n in (4, 6, 8):
            for k in (1, 2, 3, 4, 5):
                base = f"dynamics_fullweight_m3_n{n}_k{k}.json"
                os.symlink(os.path.join(COM, "commitment_" + base),
                           os.path.join(cdir, "commit_" + base))
                os.symlink(os.path.join(REV, "reveal_" + base),
                           os.path.join(cdir, "reveal_" + base))
                json.dump(build_answer(n, k),
                          open(os.path.join(adir, f"answers_n{n}_k{k}.json"), "w"), indent=1)
            os.symlink(os.path.join(COM, f"commit_convseed_n{n}.json"),
                       os.path.join(cdir, f"commit_convseed_n{n}.json"))
            os.symlink(os.path.join(REV, f"reveal_convseed_n{n}.json"),
                       os.path.join(cdir, f"reveal_convseed_n{n}.json"))
        # run the FROZEN grader as a subprocess → capture JSON stdout verbatim
        r = subprocess.run([sys.executable, os.path.join(HERE, "exp144_grader.py"), cdir, adir],
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0 or r.stderr:
            sys.stderr.write("\n[grader stderr / rc=%d]\n%s" % (r.returncode, r.stderr))


if __name__ == "__main__":
    main()
