#!/usr/bin/env python3
"""
helm.py — one GO/HOLD annunciator over the ship's weather dials (H14 B2, Whisper C5069).

THE PROBLEM THIS SOLVES (charter B2): the bridge has gauges on four consoles — `qpu_weather.py`
(quiet line, live readout, mirror ladder, nowcast), the drift clock, same-depth sentinels, and
now the A1 census saying which dials are constants and which are weather. Nobody can fly watching
all of them. The helm reads them in one place and emits GO / HOLD pre-flight and CONTINUE / ABORT
in-run, every threshold carrying its provenance.

EVERY THRESHOLD SOURCED, NOT TASTED (the charter's wall): see THRESHOLDS — each entry names the
census row or instrument it comes from. The census's own findings shape the rules:
  * window quality is in-run-detect-only (census row 9 UNDERPOWERED for forecasting) — so DEEP
    flights REQUIRE the B7 sentinel rider; the helm refuses to bless a deep flight without one.
  * readout asymmetry stability is UNDERPOWERED (row 2) — so it is read LIVE from the weather
    report, never cited from a previous epoch.
  * DD is OFF by default (measured net harmful; the census adds that its between-epoch stability
    is one-epoch evidence) — a flight requesting DD gets a HOLD with the provenance printed.

    python3 tools/helm.py --selftest      # the three fault-injected controls + two mandate checks
Library:
    from helm import preflight, inrun
    v = preflight(weather_report, flight_class="deep", sentinel_planned=True, dd_requested=False)
    v = inrun(sentinel_ideal, sentinel_obs)
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from listening_layer import window_quality

THRESHOLDS = {
    "deep_p0_go": {
        "value": 0.55,
        "provenance": "qpu_weather.py GO_THRESHOLD lineage (mirror-deep P0; the instrument's own gate)"},
    "readout_live_max": {
        "value": 0.05,
        "provenance": "census row 2: asymmetry stability UNDERPOWERED -> live read mandatory; "
                      "0.05 = the campaign's standing blindness/dial band"},
    "inrun_R_abort": {
        "value": 0.90,
        "provenance": "B7/exp101: measured bad window R=0.853 (DEGRADED), good window R=1.002; "
                      "0.90 separates the measured exemplars"},
    "sentinel_mandate": {
        "value": "deep flights require the B7 rider",
        "provenance": "census row 9: window lottery UNDERPOWERED for forecasting — "
                      "in-run detection is the only measured instrument"},
    "dd_default": {
        "value": "OFF",
        "provenance": "measured net harmful at every sparse density flown (H11 arm N); "
                      "census row 4: stability evidence is one-epoch"},
}


def preflight(weather_report, flight_class="shallow", sentinel_planned=False, dd_requested=False):
    """GO/HOLD with reasons. weather_report: the qpu_weather.py report dict (or a compatible
    snapshot). flight_class: 'shallow' | 'deep'. Refuses to guess on missing dials."""
    reasons, holds = [], []
    v = str(weather_report.get("verdict", ""))
    if "NO-GO" in v:
        holds.append(f"weather verdict '{v}' "
                     f"[{THRESHOLDS['deep_p0_go']['provenance']}]")
    elif "GO" in v:
        reasons.append(f"weather {v}")
    else:
        holds.append("weather verdict MISSING from report — the helm does not guess "
                     "(a dial that cannot be read is a HOLD, not a default)")
    lr = weather_report.get("live_readout", {})
    ro = max(1 - lr.get("ro0_p0", 1.0), lr.get("ro1_p0_complement", 0.0)) if lr else None
    if ro is None:
        holds.append("live readout MISSING — census row 2 rules the live read mandatory "
                     f"[{THRESHOLDS['readout_live_max']['provenance']}]")
    elif ro > THRESHOLDS["readout_live_max"]["value"]:
        holds.append(f"live readout error {ro:.4f} > {THRESHOLDS['readout_live_max']['value']} "
                     f"[{THRESHOLDS['readout_live_max']['provenance']}]")
    else:
        reasons.append(f"live readout {ro:.4f} within band")
    if flight_class == "deep" and not sentinel_planned:
        holds.append("DEEP flight with NO sentinel rider planned "
                     f"[{THRESHOLDS['sentinel_mandate']['provenance']}]")
    if dd_requested:
        holds.append(f"DD requested but campaign default is OFF "
                     f"[{THRESHOLDS['dd_default']['provenance']}] — override requires its own prereg line")
    return {"verdict": "HOLD" if holds else "GO",
            "holds": holds, "clears": reasons, "flight_class": flight_class}


def inrun(sentinel_ideal, sentinel_obs, shots=2000):
    """CONTINUE/ABORT from the in-run sentinel block, adjudicated by B7's verbatim exp101 fit.
    The isotropy-gate lineage: in-flight adjudication that has actually fired and aborted a
    science block is the precedent; this generalizes it to the window dial."""
    wq = window_quality(sentinel_ideal, sentinel_obs, shots=shots)
    abort = wq["R"] < THRESHOLDS["inrun_R_abort"]["value"]
    return {"verdict": "ABORT" if abort else "CONTINUE",
            "R": wq["R"], "window_class": wq["window_class"],
            "threshold": THRESHOLDS["inrun_R_abort"]["value"],
            "provenance": THRESHOLDS["inrun_R_abort"]["provenance"]}


def selftest():
    ideal = [0.47896, 0.56298, 0.39552, 0.64523, 0.31505, 0.72337]
    clean_weather = {"verdict": "GO for deep work",
                     "live_readout": {"ro0_p0": 0.985, "ro1_p0_complement": 0.02}}
    # P1 — synthetic BAD WEATHER must HOLD
    bad = {"verdict": "NO-GO for deep work",
           "live_readout": {"ro0_p0": 0.985, "ro1_p0_complement": 0.02}}
    v = preflight(bad, "deep", sentinel_planned=True)
    assert v["verdict"] == "HOLD" and "weather" in v["holds"][0], v
    print(f"P1 bad weather -> HOLD ({v['holds'][0][:60]}...)")
    # P2 — synthetic SENTINEL COLLAPSE must ABORT in-run
    v = inrun(ideal, [0.5] * 6)
    assert v["verdict"] == "ABORT" and v["R"] < 0.05, v
    print(f"P2 sentinel collapse -> ABORT (R={v['R']})")
    # P3 — CLEAN synthetic must GO and CONTINUE (the fences can clear)
    v = preflight(clean_weather, "deep", sentinel_planned=True)
    assert v["verdict"] == "GO", v
    v2 = inrun(ideal, ideal)
    assert v2["verdict"] == "CONTINUE" and abs(v2["R"] - 1) < 1e-3, v2
    print(f"P3 clean -> GO + CONTINUE (R={v2['R']})")
    # P4 — deep flight with no sentinel rider must HOLD (the census-row-9 mandate has teeth)
    v = preflight(clean_weather, "deep", sentinel_planned=False)
    assert v["verdict"] == "HOLD" and "sentinel" in v["holds"][0].lower(), v
    print("P4 deep-without-rider -> HOLD (the mandate enforces itself)")
    # P5 — DD requested must HOLD with provenance
    v = preflight(clean_weather, "shallow", dd_requested=True)
    assert v["verdict"] == "HOLD" and "DD" in v["holds"][0], v
    print("P5 DD-requested -> HOLD (net-harmful provenance printed)")
    # P6 — missing dial is a HOLD, never a default
    v = preflight({}, "shallow")
    assert v["verdict"] == "HOLD" and len(v["holds"]) >= 2, v
    print("P6 missing dials -> HOLD (the helm does not guess)")
    # P7 — the measured BAD window from the banked record must ABORT (real-exemplar check)
    bank = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                       "results", "exp101_window_retention_decomposition_c4099.json")))
    v = inrun(bank["ideal"], bank["bad"]["p_hw"])
    assert v["verdict"] == "ABORT" and abs(v["R"] - 0.8531) < 2e-3, v
    v2 = inrun(bank["ideal"], bank["good"]["p_hw"])
    assert v2["verdict"] == "CONTINUE", v2
    print(f"P7 banked exemplars: BAD window (R={v['R']}) ABORTS, GOOD window (R={v2['R']}) CONTINUES")
    print("\nSELFTEST PASS: all three charter fault-injections + both mandate checks + the missing-dial "
          "refusal + the banked-exemplar pair. Every threshold carries its provenance. "
          "Live shakedown rides the next flight at zero marginal cost.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        print(__doc__)
