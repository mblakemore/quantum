#!/usr/bin/env python3
"""
placement_floor_kit.py — measured in-job placement floors for absolute claims (H14 B4, Whisper C5068).

THE DOCTRINE THIS PACKAGES (board #117 + Cell 5's closure): relational claims certify; ABSOLUTE
claims need the measured in-job placement floor — the placement spread is 51x the noise model's sd,
and Cell 5 measured 0.324 sensitivity within ONE job for a quantity whose true value is exactly
zero. The prescription (K>=4 pinned placements co-flown, floor measured in-job, absolute quantity
graded against it) existed as doctrine prose; this is the executable module.

CENSUS FOOTNOTE (A1 row 8, C5066): the "placement is weather" cross-JOB claim rests on
cross-stratum evidence only — but the IN-JOB floor (this kit's business) is well measured and is
exactly what the doctrine requires absolute claims to clear.

    python3 tools/placement_floor_kit.py --selftest    # banked Cell 5 reproduction + block/clear controls
    python3 tools/placement_floor_kit.py --fragment    # prereg fragment

Library:
    from placement_floor_kit import floor_from_arms, grade_absolute
    rep = floor_from_arms({"BEST": (-0.1019, 0.0199), "WORST": (0.2218, 0.0355), ...})
    verdict = grade_absolute(measured=0.30, se=0.01, floor_report=rep)
"""
import json
import math
import os
import sys

K_CLEARANCE = 3.0  # frozen default: an absolute claim must clear floor + 3*se_floor


def floor_from_arms(arms):
    """arms: {placement_name: (shift, se)} for the SAME observable co-flown at K placements.
    Returns the measured in-job placement report. K >= 4 required (the #117 prescription)."""
    if len(arms) < 4:
        return {"valid": False,
                "reason": f"K={len(arms)} < 4 placements — the #117 prescription requires K>=4; "
                          "a 2-placement 'floor' cannot see the spread it exists to measure"}
    names = sorted(arms)
    vals = {n: float(arms[n][0]) for n in names}
    ses = {n: float(arms[n][1]) for n in names}
    hi, lo = max(vals, key=vals.get), min(vals, key=vals.get)
    spread = vals[hi] - vals[lo]
    spread_se = math.sqrt(ses[hi] ** 2 + ses[lo] ** 2)
    floor = max(abs(v) for v in vals.values())
    floor_se = ses[max(vals, key=lambda n: abs(vals[n]))]
    detector_z = spread / spread_se
    return {"valid": True, "K": len(arms), "per_placement": {n: (vals[n], ses[n]) for n in names},
            "spread": spread, "spread_se": spread_se, "detector_z": detector_z,
            "placement_matters": detector_z >= 3.0,
            "floor": floor, "floor_se": floor_se,
            "note": "floor = max |shift| over placements: the measured in-job systematic an absolute "
                    "claim must clear; spread/detector quantify placement dependence itself"}


def grade_absolute(measured, se, floor_report, k=K_CLEARANCE):
    """Grade an ABSOLUTE quantity against the measured in-job floor (never a simulated one)."""
    if not floor_report.get("valid"):
        return {"verdict": "INVALID-BY-CONSTRUCTION", "reason": floor_report.get("reason")}
    bar = floor_report["floor"] + k * floor_report["floor_se"]
    out = {"measured": measured, "se": se, "floor": round(floor_report["floor"], 5),
           "bar_floor_plus_kse": round(bar, 5), "k": k}
    if abs(measured) <= bar:
        out["verdict"] = "UNGRADEABLE-AGAINST-MEASURED-FLOOR"
        out["reason"] = (f"|measured| {abs(measured):.4f} <= floor+{k}*se_floor {bar:.4f} — the placement "
                         "systematic can produce this reading; state the claim relationally or don't fly (#117)")
    else:
        out["clearance_z"] = round((abs(measured) - bar) / se, 2)
        out["verdict"] = "GRADEABLE"
        out["reason"] = f"clears the measured floor bar by {out['clearance_z']} sigma of the claim's own se"
    return out


PREREG_FRAGMENT = """\
## Placement floor (standard fragment — B4, H14; board #117 doctrine)
- Claim type: [ ] relational (exempt — state and skip)   [ ] ABSOLUTE (this fragment mandatory)
- K >= 4 pinned placements co-flown IN the science job: <list the K physical tuples>
- Null observable at each placement: <the same observable, true value known (usually 0)>
- Floor computation: placement_floor_kit.floor_from_arms() on the K co-flown arms — grade-time,
  never design-time, never simulated (the noise model under-predicts absolute-null bias 15-35x)
- Overhead priced here: K x <shots per null arm> = <total> added shots (seen at freeze, not at submit)
- Grade rule: grade_absolute(measured, se, floor_report); UNGRADEABLE => the absolute claim is not
  made (the relational restatement, if any, is pre-registered here: <...>)
"""


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    g = json.load(open(os.path.join(here, "..", "results",
                                    "h13_cell5_placement_grade_d9trnegu5hac73agchf0.json")))
    arms = {p: (g["arms"][f"pair01@{p}"]["shift"], g["arms"][f"pair01@{p}"]["se"])
            for p in ("BEST", "WORST", "flownA", "flownB")}
    rep = floor_from_arms(arms)
    # P1 — exact reproduction of the banked Cell 5 spread (the 0.324 the doctrine cites)
    assert abs(rep["spread"] - g["spread"]) < 1e-12, (rep["spread"], g["spread"])
    assert rep["placement_matters"] and rep["detector_z"] > 7, rep["detector_z"]
    print(f"P1 banked reproduction: spread {rep['spread']:.6f} == grade file's {g['spread']:.6f} (exact); "
          f"detector z = {rep['detector_z']:.2f} -> placement_matters fires")
    # P2 — the fence BLOCKS: an absolute claim inside the measured floor is refused
    v = grade_absolute(0.10, 0.01, rep)
    assert v["verdict"] == "UNGRADEABLE-AGAINST-MEASURED-FLOOR", v
    print(f"P2 block control: |0.10| vs bar {v['bar_floor_plus_kse']} -> {v['verdict']}")
    # P3 — the fence CLEARS: a claim well above the floor grades, with its clearance printed
    v = grade_absolute(0.60, 0.01, rep)
    assert v["verdict"] == "GRADEABLE" and v["clearance_z"] > 20, v
    print(f"P3 clear control: |0.60| clears bar by {v['clearance_z']} sigma -> {v['verdict']}")
    # P4 — quiet placements: synthesized uniform arms -> detector quiet, small floor
    quiet = {f"p{i}": (0.001 * (-1) ** i, 0.02) for i in range(4)}
    rq = floor_from_arms(quiet)
    assert not rq["placement_matters"], rq
    print(f"P4 quiet control: synthesized uniform arms -> detector z = {rq['detector_z']:.2f}, quiet")
    # P5 — K<4 refused
    rk = floor_from_arms({"a": (0, 0.01), "b": (0.1, 0.01)})
    assert not rk["valid"]
    print("P5 K<4 refusal: INVALID (a 2-placement floor cannot see the spread)")
    print("\nSELFTEST PASS: banked Cell 5 floor reproduced exactly, block/clear/quiet/refusal all "
          "demonstrated. Fragment ready for the flight-kit template.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--fragment" in sys.argv:
        print(PREREG_FRAGMENT)
    else:
        print(__doc__)
