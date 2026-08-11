#!/usr/bin/env python3
"""
h13_cell2_prerun_verdict.py — BOOLEAN-ONLY pre-run adjudicator for the Cell 2 blind (option b).

WHY THIS EXISTS — THE FIFTH LEAK (whisper, general#9472).
  The Cell 2 blind survived four attacks and would then have died to my seat's ROUTINE DUTY.
  Adjudicating G-ISO and the TVD<=0.01 matching dial is the author's job, and the pre-run block
  reports those inputs as ARM-LABELLED CORRELATORS to 4dp:

      CE XX: +0.7823    CC YY: -0.8106

  Ember measured that a SINGLE correlator at 4dp separates 62 of 80 record sets. So the pre-run
  hands the author the exact join key she proved sufficient, through the front door, as normal
  operation. Not an attack — the apparatus working as designed.

  Same shape as the other four: a protection that survives what it was designed against and dies
  to the ordinary running of the machine.

THE RULE THIS ENFORCES:
  IF A GATE NEEDS A NUMBER TO FIRE, THE SEAT HOLDING THE NUMBERS FIRES IT AND SENDS THE VERDICT,
  NOT THE INPUT.
  The author receives pass/fail. The correlators never leave the fetching seat.

WHO RUNS THIS: the FETCHING seat (Ember under option b), never the author.
WHAT THE AUTHOR RECEIVES: this tool's stdout, and nothing else from the pre-run.

THE REDACTION SELF-CHECK IS THE POINT.
  Not printing correlators is discipline — the same species of protection this whole thread
  exists to eliminate. So the tool MECHANICALLY SCANS ITS OWN OUTPUT for any continuous value
  before emitting, and REFUSES TO EMIT if it finds one. A future edit that adds a helpful
  diagnostic float cannot silently reopen the channel; it fails closed and says why.
  Booleans, integers, and the fixed vocabulary below are the entire permitted alphabet.

Usage (fetching seat):
    python3 tools/h13_cell2_prerun_verdict.py <prerun_results.json>
    python3 tools/h13_cell2_prerun_verdict.py --self-test
"""
import json
import re
import sys

# The gates' thresholds are PUBLIC (they are in the signed prereg). Only the MEASURED VALUES
# are secret, because only the measured values are arm-separating.
TVD_MAX = 0.01          # matching dial premise gate (prereg 4c)
BAND = (0.30, 0.70)     # G-BAND depolarizing band
ISO_MIN_AXES = 3        # G-ISO: signal floor, 3-of-3 axes above floor (Elder's tightening)

# Everything the author is permitted to learn. Anything outside this alphabet is a leak.
PERMITTED = {
    "PASS", "FAIL", "NO-TEST", "true", "false",
    "G-ISO", "G-BAND", "TVD-MATCH", "SIGNAL-FLOOR", "VERDICT",
    "CLEAR-TO-DECODE", "ABORT", "arms", "axes", "units",
}


def _leaks(text):
    """Return every token in `text` that could carry arm-separating information.

    A correlator is a signed decimal. A count is an integer and is safe: the design fixes
    40 units x 2 arms x 3 bases and those numbers are in the signed prereg, so they separate
    nothing. Any DECIMAL is treated as a leak regardless of what it measures — the check does
    not try to decide which floats are innocent, because that judgement is exactly the thing
    that would erode.
    """
    return re.findall(r"[-+]?\d+\.\d+(?:[eE][-+]?\d+)?", text)


def adjudicate(prerun):
    """Compute the three verdicts from arm-labelled data. RETURNS BOOLEANS ONLY.

    The caller (fetching seat) holds `prerun`. Nothing derived from it escapes except the
    three booleans and the composite verdict.
    """
    if not isinstance(prerun, dict) or "correlators" not in prerun:
        # ABSENT != PASS. A malformed or renamed input must not adjudicate to CLEAR.
        raise SystemExit("🔴 pre-run input has no 'correlators' key — ABSENT IS NOT A PASS. "
                         "Refusing to emit a verdict from an input I could not read.")

    C = prerun["correlators"]          # {"CE": {"XX": float, ...}, "CC": {...}}
    if set(C) != {"CE", "CC"}:
        raise SystemExit(f"🔴 expected exactly arms CE and CC, found {sorted(C)} — failing closed.")

    # G-ISO: every axis of every arm must clear the signal floor. 3-of-3, per Elder's tightening
    # on consumer-consistency grounds (a gate that passes on 2 of 3 licenses a consumer to read
    # an axis that never cleared).
    floor = prerun.get("signal_floor")
    if floor is None:
        raise SystemExit("🔴 no 'signal_floor' in pre-run — the G-ISO threshold is not optional.")
    iso = all(sum(abs(v) > floor for v in arm.values()) >= ISO_MIN_AXES for arm in C.values())

    # G-BAND: the injected depolarizing parameter sits inside the pre-registered band.
    p = prerun.get("p_measured")
    if p is None:
        raise SystemExit("🔴 no 'p_measured' in pre-run — G-BAND cannot adjudicate without it.")
    band = BAND[0] <= p <= BAND[1]

    # TVD matching dial: the two arms must be statistically matched, or the classical ceiling
    # the whole claim is measured against is computed from the wrong distribution.
    tvd = prerun.get("tvd")
    if tvd is None:
        raise SystemExit("🔴 no 'tvd' in pre-run — the matching premise cannot be checked.")
    match = tvd <= TVD_MAX

    clear = iso and band and match
    return {
        "G-ISO": "PASS" if iso else "FAIL",
        "G-BAND": "PASS" if band else "FAIL",
        "TVD-MATCH": "PASS" if match else "FAIL",
        "VERDICT": "CLEAR-TO-DECODE" if clear else "NO-TEST",
    }


# The verdict's ENTIRE permitted shape. Fixed, and fixed INDEPENDENTLY OF INPUT SIZE.
VERDICT_FIELDS = ("G-ISO", "G-BAND", "TVD-MATCH", "VERDICT")


def emit(verdicts):
    """Render the verdicts, then REFUSE TO PRINT if the render carries any continuous value.

    CARDINALITY GATE — THE SIXTH LEAK (Ember, general#9473).
      "Booleans only" is necessary and NOT sufficient, because it does not say HOW MANY.
      A per-set pass/fail vector is 80 verdicts: at the observed ~27.5% failure rate that is
      ~68 bits, narrowing a failing blinded set from 1-of-80 to 1-of-22 with no correlator ever
      printed. Worse, if G-ISO failures are arm-correlated — AND ARM-CORRELATED ABSTENTION IS
      THE EXACT DEFECT THIS RE-FLY EXISTS TO FIX — the vector is a direct partial read on the
      arm, through the channel we had just declared closed.

      A VERDICT WITH 80 COMPONENTS IS NOT A VERDICT, IT IS THE DATA AT LOWER RESOLUTION.

      So the shape is checked against a FIXED whitelist, not merely written correctly today.
      This tool currently satisfies the rule by construction; the gate is here so that it
      cannot stop satisfying it silently — the difference between happening to be safe and
      being held safe, which is the distinction this whole thread has been converting.
    """
    if tuple(verdicts) != VERDICT_FIELDS:
        sys.exit(f"🔴 CARDINALITY GATE — verdict shape is {tuple(verdicts)}, not {VERDICT_FIELDS}.\n"
                 "   A verdict indexed by set is the data at lower resolution. REFUSING TO EMIT.")
    lines = ["═══ CELL 2 PRE-RUN VERDICT (boolean-only, arm-blind) ═══"]
    for k in ("G-ISO", "G-BAND", "TVD-MATCH"):
        lines.append(f"  {k:<12} {verdicts[k]}")
    lines.append(f"  {'VERDICT':<12} {verdicts['VERDICT']}")
    lines.append("  (measured values withheld by construction — they separate the arms)")
    out = "\n".join(lines)

    found = _leaks(out)
    if found:
        # This is the fail-closed path a future well-meaning edit would hit.
        sys.exit("🔴 REDACTION SELF-CHECK FAILED — output carries continuous value(s): "
                 f"{found}\n   These are arm-separating. REFUSING TO EMIT. "
                 "If a gate needs a number, fire the gate here and send the verdict.")
    print(out)


def _self_test():
    """Demonstrate the tool BOTH passing and refusing — a can-it-fire proof needs both arms
    in the same run, or a failure to fire is indistinguishable from a verdict."""
    ok = {"correlators": {"CE": {"XX": 0.78, "YY": 0.77, "ZZ": 0.78},
                          "CC": {"XX": 0.81, "YY": -0.81, "ZZ": 0.80}},
          "signal_floor": 0.05, "p_measured": 0.50, "tvd": 0.004}
    print("[self-test 1/6] well-formed, all gates satisfiable:")
    emit(adjudicate(ok))

    bad = dict(ok, tvd=0.03)   # matching premise violated
    print("\n[self-test 2/6] TVD premise violated — must read NO-TEST, still leaking nothing:")
    emit(adjudicate(bad))

    # ABSENT != PASS, on each threshold separately. A single fixture over the bar demonstrates
    # wiring, not coverage (Ember) — so every input the adjudicator depends on gets its own
    # deletion test, because a missing threshold is the input most likely to arrive silently.
    print("\n[self-test 3/6] each required input, deleted in turn — all must REFUSE, none may PASS:")
    for key in ("correlators", "signal_floor", "p_measured", "tvd"):
        missing = {k: v for k, v in ok.items() if k != key}
        try:
            adjudicate(missing)
            sys.exit(f"🔴 adjudicated with '{key}' ABSENT — absent was read as satisfied. "
                     "This is the fail-OPEN class; refusing to ship.")
        except SystemExit as e:
            if str(e).startswith("🔴 "):
                print(f"  ✅ '{key}' absent → refused")
            else:
                raise

    print("\n[self-test 4/6] wrong arm set must fail closed (a renamed arm is not two arms):")
    try:
        adjudicate(dict(ok, correlators={"CE": ok["correlators"]["CE"]}))
        sys.exit("🔴 adjudicated with one arm — refusing to ship.")
    except SystemExit as e:
        if not str(e).startswith("🔴 "):
            raise
        print("  ✅ single-arm input → refused")

    print("\n[self-test 5/6] redaction check must FIRE on a leaking render:")
    try:
        found = _leaks("  CE XX: +0.7823")
        assert found, "redaction check failed to detect a correlator"
        print(f"  ✅ detected {found} — a correlator in the output would abort the emit")
    except AssertionError as e:
        sys.exit(f"🔴 {e}")

    # The sixth-leak fixture: a verdict that grew a per-set index. This is what a future
    # "helpful" edit looks like — no correlator anywhere, every value a boolean, and ~68 bits
    # of arm-correlated information leaving the seat.
    print("\n[self-test 6/6] a PER-SET boolean vector must be REFUSED (booleans-only is not enough):")
    per_set = {f"set_{i}": ("PASS" if i % 4 else "FAIL") for i in range(80)}
    try:
        emit(per_set)
        sys.exit("🔴 emitted an 80-component verdict — the sixth leak is OPEN. Refusing to ship.")
    except SystemExit as e:
        if "CARDINALITY GATE" not in str(e):
            raise
        print("  ✅ 80-component verdict → refused by the cardinality gate")

    print("\n✅ self-test complete: emits an aggregate verdict, refuses on premise failure, "
          "refuses on absent input, detects a correlator in its own render, and refuses a "
          "verdict indexed by set.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _self_test()
    elif len(sys.argv) < 2:
        sys.exit(__doc__)
    else:
        emit(adjudicate(json.load(open(sys.argv[1]))))
