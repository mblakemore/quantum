#!/usr/bin/env python3
"""EPOCH-LAMBDA with HONEST PROVENANCE — Ember, C4262.

WHY THIS EXISTS AS ITS OWN TOOL: I delivered lambda twice (06:39, 08:52) stamped with MY
READ TIME in a field called epoch_utc, and the two reads were BIT-IDENTICAL. The reason is
that backend.target serves IBM's LAST PUBLISHED CALIBRATION — reading it again does not
sample the device. When I finally checked the calibration's own timestamp it was 29.58
HOURS OLD.

So a value comparison across reads inside one calibration window is GUARANTEED to agree and
proves nothing; it can detect a REFRESH, never STALENESS. The timestamp is the only signal.

This tool therefore emits BOTH clocks and refuses to pretend they are one:
    read_utc            when I asked
    calibration_utc     when IBM last published (last_update_date)
    calibration_age_h   the number that actually matters

A provenance block whose whole purpose is provenance must not carry the reader's clock as if
it were the measurement's clock.
"""
import sys, json, datetime, statistics as st, argparse

def measure(backend_name="ibm_marrakesh", n=8, max_age_h=None):
    sys.path.insert(0, "scripts")
    import importlib.util
    from run_exp66_qpu_partb import _get_ibm_service
    s = importlib.util.spec_from_file_location("kit",
        "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass

    bk = _get_ibm_service().backend(backend_name)
    tgt = bk.target
    twoq = "cz" if "cz" in tgt.operation_names else "ecr"
    reg = kit.line_layout(tgt.build_coupling_map(), 2*n)
    if not reg or len(reg) != 2*n:
        sys.exit("REFUSE: no line layout — cannot define the flown register.")

    errs = []
    for i in range(len(reg)-1):
        a, b = reg[i], reg[i+1]
        e = tgt[twoq].get((a, b)) or tgt[twoq].get((b, a))
        if e is not None and getattr(e, "error", None) is not None:
            errs.append(e.error)
    lam = st.mean(errs)

    props = None
    for attr in ("properties", "_properties"):
        try:
            p = getattr(bk, attr); props = p() if callable(p) else p
            if props is not None: break
        except Exception: pass
    cal = getattr(props, "last_update_date", None)
    now = datetime.datetime.now(datetime.timezone.utc)
    age_h = (now - cal).total_seconds()/3600 if cal else None

    out = {
        "lambda": lam,
        "register": reg,
        "backend": bk.name,
        "edges_measured": len(errs),
        "read_utc": now.isoformat(),
        "calibration_utc": cal.isoformat() if cal else None,
        "calibration_age_hours": round(age_h, 2) if age_h is not None else None,
        "NOTE": ("lambda is IBM's LAST PUBLISHED calibration, not a fresh device sample. "
                 "Re-reading returns the same record until IBM republishes, so a value "
                 "comparison across reads cannot detect staleness — only the timestamp can."),
    }
    if max_age_h is not None and age_h is not None and age_h > max_age_h:
        out["GATE"] = f"REFUSE: calibration {age_h:.2f}h old exceeds max {max_age_h}h"
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--max-age-hours", type=float, default=None)
    a = ap.parse_args()
    r = measure(a.backend, a.n, a.max_age_hours)
    print(json.dumps(r, indent=2))
    sys.exit(1 if "GATE" in r else 0)
