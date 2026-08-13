#!/usr/bin/env python3
"""
anchor_covenant.py — grade-time anchor-validity checker (H14 Deck B cell B5, Whisper C5068).

THE LESSON THIS ENCODES (door (a), R1-R6): threshold sizing from an anchor that drifted between
jobs produced door (a)'s named failure surface; the remedy rules — same-job frozen-formula anchor,
grade-time validity gate — were written as door-a-specific text. This extracts the covenant into a
reusable checker any cross-job-comparison design inherits.

THE COVENANT: a design that compares quantities across jobs must either
  (a) co-fly its anchor in the SAME JOB as each arm it normalizes (preferred; the door-a rule), or
  (b) declare an anchor-drift budget IN ITS PREREG, and the grade FAILS if the anchor moved past it.
A grade with no co-flown anchor and no declared budget is INVALID-BY-CONSTRUCTION — the checker
refuses to pass it rather than assuming a budget.

CENSUS FOOTNOTE (A1 row 12, C5066): the banked door-a anchor pair reads 1.41x cross-job (z = 2.32
under the declared proxy SE) — and the widely-quoted 2.02x is not derivable from any banked
artifact. Neither number repeals the covenant: one weak pair at a proxy SE is not stability
evidence, and same-job anchoring remains the rule. The banked pair serves here as the FAIL
positive control; the banked same-job block pair (ratio 0.924, z = 0.49) is the PASS control.

    python3 tools/anchor_covenant.py --selftest

Library:
    from anchor_covenant import check_anchor
    verdict = check_anchor(anchor_ref, anchor_grade, same_job=False, declared_budget_ratio=1.15)
"""
import math
import sys


def check_anchor(anchor_ref, anchor_grade, same_job, declared_budget_ratio=None,
                 se_ref=None, se_grade=None):
    """
    anchor_ref:   anchor value at sizing/threshold-derivation time
    anchor_grade: anchor value at grade time (co-flown or re-measured)
    same_job:     True if the grade-time anchor was co-flown in the same job as the graded arm
    declared_budget_ratio: prereg-declared max allowed ratio drift (e.g. 1.15); REQUIRED when
                  same_job is False — absent -> INVALID-BY-CONSTRUCTION
    se_*:         optional SEs; when both present a drift z-score is reported alongside

    Returns dict with verdict PASS / FAIL / INVALID-BY-CONSTRUCTION and the numbers.
    """
    out = {"anchor_ref": anchor_ref, "anchor_grade": anchor_grade, "same_job": bool(same_job)}
    if anchor_ref <= 0 or anchor_grade <= 0:
        out["verdict"] = "INVALID-BY-CONSTRUCTION"
        out["reason"] = "non-positive anchor value"
        return out
    ratio = max(anchor_ref, anchor_grade) / min(anchor_ref, anchor_grade)
    out["ratio"] = round(ratio, 4)
    if se_ref is not None and se_grade is not None:
        out["drift_z"] = round(abs(anchor_ref - anchor_grade) / math.sqrt(se_ref ** 2 + se_grade ** 2), 3)
    if same_job:
        out["verdict"] = "PASS"
        out["reason"] = "anchor co-flown same-job (the door-a rule); ratio reported for the record"
        return out
    if declared_budget_ratio is None:
        out["verdict"] = "INVALID-BY-CONSTRUCTION"
        out["reason"] = ("cross-job anchor with NO declared drift budget — the covenant refuses to "
                        "assume one; declare it in the prereg or co-fly the anchor")
        return out
    out["declared_budget_ratio"] = declared_budget_ratio
    if ratio > declared_budget_ratio:
        out["verdict"] = "FAIL"
        out["reason"] = f"anchor drifted {ratio:.3f}x > declared budget {declared_budget_ratio}x"
    else:
        out["verdict"] = "PASS"
        out["reason"] = f"anchor drift {ratio:.3f}x within declared budget {declared_budget_ratio}x"
    return out


PREREG_FRAGMENT = """\
## Anchor covenant (standard fragment — B5, H14)
- Anchor quantity: <name, formula frozen here>
- Anchoring mode: [ ] co-flown same-job (preferred)   [ ] cross-job with declared budget
- If cross-job: declared drift budget = <ratio>x, justified by: <evidence for that budget>
- Grade-time check: anchor_covenant.check_anchor() runs in the grade script; a FAIL or
  INVALID-BY-CONSTRUCTION verdict voids the graded comparison (not the raw data).
"""


def selftest():
    # FAIL control — the banked door-a cross-job pair (free 0.176 vs paid 0.248; census row 12).
    # Any sane declared budget (1.15x, generous for a 48-minute gap) must FAIL on a 1.41x move.
    v = check_anchor(0.176, 0.248, same_job=False, declared_budget_ratio=1.15,
                     se_ref=0.022, se_grade=0.022)
    assert v["verdict"] == "FAIL" and abs(v["ratio"] - 1.409) < 0.001, v
    print(f"P1 FAIL control (banked cross-job pair): ratio {v['ratio']}x vs budget 1.15x -> {v['verdict']} (z={v['drift_z']})")
    # PASS control — the banked same-job block pair (shape discriminator A/B: 0.184 vs 0.199).
    v = check_anchor(0.184, 0.199, same_job=True, se_ref=0.02198, se_grade=0.02192)
    assert v["verdict"] == "PASS" and v["drift_z"] < 0.5, v
    print(f"P2 PASS control (banked same-job pair): ratio {v['ratio']}x, z={v['drift_z']} -> {v['verdict']}")
    # P3 — the refusal: cross-job with no declared budget is INVALID-BY-CONSTRUCTION, never a default.
    v = check_anchor(0.176, 0.180, same_job=False)
    assert v["verdict"] == "INVALID-BY-CONSTRUCTION", v
    print(f"P3 refusal control (no declared budget): -> {v['verdict']}")
    # P4 — a declared budget that the drift respects passes (the covenant permits, it doesn't forbid).
    v = check_anchor(0.176, 0.180, same_job=False, declared_budget_ratio=1.15)
    assert v["verdict"] == "PASS", v
    print(f"P4 within-budget control: ratio {v['ratio']}x vs 1.15x -> {v['verdict']}")
    print("\nSELFTEST PASS: banked FAIL + PASS controls demonstrated, the no-budget refusal fires, "
          "and a declared budget that holds passes. Fragment ready for the flight-kit template.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--fragment" in sys.argv:
        print(PREREG_FRAGMENT)
    else:
        print(__doc__)
