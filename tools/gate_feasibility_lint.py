#!/usr/bin/env python3
"""gate_feasibility_lint.py — pre-registration gate feasibility linter (Whisper C4587).

A frozen grading gate must be able to PASS and able to FAIL at the budgeted
statistics, or it is vacuous and the prereg proves nothing (Exp108b pre-freeze
lesson, prereg line ~57: drafted therm band 0.05 was IMPOSSIBLE at draft shots —
5*SE alone = 0.069 with zero real deviation).

Usage:
    python3 tools/gate_feasibility_lint.py spec.json
    python3 tools/gate_feasibility_lint.py --selftest   # reproduces the Exp108b catch

Spec JSON:
{
  "k": 5,                       # SE multiplier for PASS feasibility (default 5, matches freeze practice)
  "k_fail": 2,                  # SE multiplier for FAIL detectability (default 2 ~ 95%;
                                #   a fail needs to be probable, not 5-sigma guaranteed)
  "gates": [{
    "name": "therm_null_band",
    "pass_value": 0.0,          # statistic value in the scenario that SHOULD pass
                                #   (deviation gates: 0 = zero real deviation)
    "fail_value": 0.10,         # optional: statistic in a broken scenario that SHOULD fail
    "threshold": 0.06,
    "direction": "below",       # passing side of the threshold: "below" | "above"
    "se": 0.00866,              # SE of the statistic at budget; OR give binomial inputs:
    "binomial": {"p": 0.25, "shots": 2500}   # se = sqrt(p*(1-p)/shots) if "se" absent
  }]
}

Verdicts per gate:
  VACUOUS-FAIL  cannot pass at budget even in the should-pass scenario (k*SE crosses
                the threshold from the passing side) — the Exp108b defect class
  VACUOUS-PASS  cannot fail at budget even in the provided broken scenario
  OK            both feasible; margins reported
  OK*           pass side feasible; no fail scenario provided (CAN-FAIL not evaluated)
"""
import json
import math
import sys


def gate_se(g):
    if "se" in g:
        return float(g["se"])
    b = g["binomial"]
    return math.sqrt(b["p"] * (1 - b["p"]) / b["shots"])


def lint_gate(g, k, k_fail):
    se = gate_se(g)
    thr = float(g["threshold"])
    below = g["direction"] == "below"
    pv = float(g["pass_value"])
    out = {"name": g["name"], "se": se, "k_se": k * se, "threshold": thr,
           "direction": g["direction"]}

    # CAN-PASS: in the should-pass scenario, the k*SE band must sit on the passing side.
    pass_edge = pv + k * se if below else pv - k * se
    can_pass = (pass_edge < thr) if below else (pass_edge > thr)
    out["can_pass"] = can_pass
    out["pass_margin"] = (thr - pass_edge) if below else (pass_edge - thr)

    # CAN-FAIL: in the broken scenario (if given), the k*SE band must sit on the failing side.
    if "fail_value" in g:
        fv = float(g["fail_value"])
        fail_edge = fv - k_fail * se if below else fv + k_fail * se
        can_fail = (fail_edge > thr) if below else (fail_edge < thr)
        out["can_fail"] = can_fail
        out["fail_margin"] = (fail_edge - thr) if below else (thr - fail_edge)
    else:
        out["can_fail"] = None

    if not can_pass:
        out["verdict"] = "VACUOUS-FAIL"
        out["note"] = ("cannot pass at budget even with the should-pass value "
                       f"{pv}: {k}*SE = {k*se:.4f} crosses threshold {thr}")
    elif out["can_fail"] is False:
        out["verdict"] = "VACUOUS-PASS"
        out["note"] = ("cannot fail at budget even in the broken scenario "
                       f"{g['fail_value']}: gate proves nothing")
    elif out["can_fail"] is None:
        out["verdict"] = "OK*"
        out["note"] = "pass side feasible; no fail scenario provided"
    else:
        out["verdict"] = "OK"
        out["note"] = "gate can pass and can fail at budget"
    return out


def lint(spec):
    k = spec.get("k", 5)
    k_fail = spec.get("k_fail", 2)
    return [lint_gate(g, k, k_fail) for g in spec["gates"]]


def selftest():
    """Reproduce the Exp108b pre-freeze catch from its recorded constants.

    Recorded (experiments/exp108b-native-thermal-preregistration.md:57-58 and
    exp108b_native_thermal.py:58): therm gate statistic = |p_hat_null - 0.25|,
    drafted band 0.05 at draft null shots (binomial p=0.25, n=1000:
    5*SE = 0.0685 ~ the recorded 0.069) -> impossible; frozen fix = band 0.06
    + null shots 2500 (5*SE = 0.0433, margin ~1.7pp ~ the recorded ~1.8pp).
    """
    drafted = {"name": "therm_band_DRAFT_0.05@1000sh", "pass_value": 0.0,
               "fail_value": 0.10, "threshold": 0.05, "direction": "below",
               "binomial": {"p": 0.25, "shots": 1000}}
    frozen = {"name": "therm_band_FROZEN_0.06@2500sh", "pass_value": 0.0,
              "fail_value": 0.10, "threshold": 0.06, "direction": "below",
              "binomial": {"p": 0.25, "shots": 2500}}
    res = lint({"k": 5, "gates": [drafted, frozen]})
    r0, r1 = res
    assert r0["verdict"] == "VACUOUS-FAIL", r0
    assert abs(r0["k_se"] - 0.0685) < 0.001, r0["k_se"]   # the recorded "0.069"
    assert r1["verdict"] == "OK", r1
    assert abs(r1["pass_margin"] - 0.017) < 0.002, r1["pass_margin"]  # "~1.8pp"
    for r in res:
        print(f"{r['name']:34s} {r['verdict']:12s} {r['note']}")
    print("SELFTEST PASS: Exp108b defect reproduced (drafted gate vacuously "
          "impossible; frozen gate feasible with the recorded ~1.7pp margin)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        selftest()
    elif len(sys.argv) > 1:
        for r in lint(json.load(open(sys.argv[1]))):
            print(json.dumps(r))
        if any(x["verdict"].startswith("VACUOUS") for x in
               lint(json.load(open(sys.argv[1])))):
            sys.exit(1)
    else:
        print(__doc__)
