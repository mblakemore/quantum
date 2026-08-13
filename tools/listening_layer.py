#!/usr/bin/env python3
"""
listening_layer.py — the ship's side of the conversation, standardized (H14 B7, Whisper C5069).

THE RIDER SPEC (charter B7):
  Every deep job MAY carry a standard telemetry block — the rider — at near-zero marginal cost:
    * THREE same-depth sentinel circuits (identical known-ideal circuit, placed at START / MID /
      END of the job's circuit list) — the window lottery (±7pp class) is detectable in-run,
      never forecastable from calibration age;
    * optionally ONE drift-phase probe row (the coherent-clock reader's minimal unit) — each
      carried probe is one epoch toward re-opening A4 (the PUF test needs >=5; see
      h14-a4-drift-puf-UNDERPOWERED-AT-FREEZE).
  The rider's qubit/shot budget is PRINTED IN THE PREREG at freeze time. Rider placement is
  disjoint from science qubits (stated per flight). RIDER DATA IS TELEMETRY, NEVER CLAIM-BEARING
  (genre fence). Every decode appends one ship-state record to the ledger (append-only, actor
  mandatory — board #88: unattributed writes are permanently unattributed).

THE WINDOW-QUALITY ESTIMATOR — exp101's, verbatim (Ember C4099), not an approximation:
    M_shift : p = P_ideal(k) + c
    M_dep   : p = 0.5 + R^k * (P_ideal - 0.5)
    M_both  : p = 0.5 + d + R^k * (P_ideal - 0.5)
  compared by AIC, with the binomial shot floor printed. Validated in --selftest by reproducing
  the BANKED exp101 fits for both the BAD and GOOD windows from the banked per-pub values —
  the charter's "validate against banked jobs" control, achieved with the original estimator
  rather than a lookalike (a build-time custody check found the estimator source on disk;
  charter controls get re-derived from artifacts, the B5 lesson).

    python3 tools/listening_layer.py --selftest
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "results", "ship_state_ledger.jsonl")
R_DEGRADED = 0.90   # exp101's bad window read R=0.853; flag threshold, tunable per prereg


def _aic(rss, n, kparams):
    return n * np.log(max(rss, 1e-300) / n) + 2 * kparams


def window_quality(p_ideal, obs, ks=None, shots=2000):
    """exp101's three-model window fit. p_ideal/obs: per-k probabilities; ks: iteration indices."""
    p_ideal = np.asarray(p_ideal, dtype=float)
    obs = np.asarray(obs, dtype=float)
    ks = np.arange(len(obs)) if ks is None else np.asarray(ks)
    n = len(obs)

    def rss_of(pred):
        return float(np.sum((pred - obs) ** 2))

    out = {}
    c = float(np.mean(obs - p_ideal))
    out["M_shift"] = {"params": {"c": round(c, 5)}, "rss": rss_of(p_ideal + c)}
    res = minimize(lambda x: rss_of(0.5 + (x[0] ** ks) * (p_ideal - 0.5)), x0=[0.9],
                   bounds=[(0.0, 1.5)])
    out["M_dep"] = {"params": {"R": round(float(res.x[0]), 4)}, "rss": float(res.fun)}
    res2 = minimize(lambda x: rss_of(0.5 + x[1] + (x[0] ** ks) * (p_ideal - 0.5)), x0=[0.9, 0.0],
                    bounds=[(0.0, 1.5), (-0.2, 0.2)])
    out["M_both"] = {"params": {"R": round(float(res2.x[0]), 4), "d": round(float(res2.x[1]), 5)},
                     "rss": float(res2.fun)}
    for m, kp in (("M_shift", 1), ("M_dep", 1), ("M_both", 2)):
        out[m]["aic"] = _aic(out[m]["rss"], n, kp)
    out["shot_floor_rss"] = float(np.sum(obs * (1 - obs) / shots))
    best = min(("M_shift", "M_dep", "M_both"), key=lambda m: out[m]["aic"])
    R = out["M_both"]["params"]["R"]
    out["best_by_aic"] = best
    out["R"] = R
    out["window_class"] = "DEGRADED" if R < R_DEGRADED else "GOOD"
    return out


def append_ship_state(actor, job_id, backend, window=None, drift_phase=None, meta=None,
                      ledger_path=LEDGER):
    """Append one ship-state record. actor is MANDATORY — a telemetry ledger with unattributed
    rows inherits the board-#88 defect at birth."""
    if not actor:
        raise ValueError("actor is mandatory: an unattributed telemetry row is permanently "
                         "unattributed (board #88) — refuse at the API, not in review")
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "actor": actor,
           "job_id": job_id, "backend": backend}
    if window is not None:
        rec["window"] = {"R": window["R"], "class": window["window_class"],
                         "model": window["best_by_aic"], "d": window["M_both"]["params"]["d"]}
    if drift_phase is not None:
        rec["drift_phase"] = drift_phase
    if meta:
        rec["meta"] = meta
    with open(ledger_path, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def selftest():
    bank = json.load(open(os.path.join(HERE, "..", "results",
                                       "exp101_window_retention_decomposition_c4099.json")))
    ideal = bank["ideal"]
    # P1 — reproduce the BANKED fits for both windows with the verbatim estimator
    for w, want_class in (("bad", "DEGRADED"), ("good", "GOOD")):
        got = window_quality(ideal, bank[w]["p_hw"])
        for m in ("M_dep", "M_both"):
            for pname, val in bank[w]["fits"][m]["params"].items():
                mine = got[m]["params"][pname]
                assert abs(mine - val) < 2e-3, (w, m, pname, mine, val)
        assert got["window_class"] == want_class, (w, got["R"], got["window_class"])
        print(f"P1 {w} window: R={got['M_both']['params']['R']} d={got['M_both']['params']['d']} "
              f"(banked {bank[w]['fits']['M_both']['params']}) -> class {got['window_class']} — banked fits REPRODUCED")
    # P2 — synthetic perfect window: obs == ideal -> R ~ 1, d ~ 0, GOOD
    got = window_quality(ideal, ideal)
    assert abs(got["R"] - 1.0) < 1e-3 and got["window_class"] == "GOOD", got
    print(f"P2 synthetic perfect: R={got['R']} -> GOOD")
    # P3 — synthetic dead window: obs flat at 0.5 -> R ~ 0, DEGRADED flagged
    got = window_quality(ideal, [0.5] * len(ideal))
    assert got["R"] < 0.05 and got["window_class"] == "DEGRADED", got
    print(f"P3 synthetic dead: R={got['R']} -> DEGRADED (the flag fires)")
    # P4 — ledger: actor mandatory (refusal) + append/re-read round trip on a temp ledger
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name
    try:
        append_ship_state("", "job_x", "ibm_test", ledger_path=tmp)
        raise AssertionError("actorless append must refuse")
    except ValueError:
        print("P4a actorless append: REFUSED at the API")
    rec = append_ship_state("whisper", "job_x", "ibm_test",
                            window=window_quality(ideal, ideal), ledger_path=tmp)
    back = json.loads(open(tmp).read().strip())
    assert back["actor"] == "whisper" and back["window"]["class"] == "GOOD", back
    os.unlink(tmp)
    print("P4b ledger round-trip: appended and re-read with attribution")
    print("\nSELFTEST PASS: banked exp101 fits reproduced with the verbatim estimator (both windows), "
          "synthetic perfect/dead classified, ledger refuses unattributed rows. Rider spec in the "
          "docstring; each carried drift probe is one epoch toward re-opening A4.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        print(__doc__)
