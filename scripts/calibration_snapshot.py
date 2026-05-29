"""Backend calibration snapshot helper (Whisper C3723).

WHY THIS EXISTS
---------------
Creator (Discord, 5/29/26) asked: "with the day-to-day variance is there some
sort of calibration sequence prior needed to baseline?" — exactly right.

The day's QPU calibration is a CONFOUNDER on any absolute error metric. We already
deconfound RELATIVE criteria (T1/T3) by co-submitting raw+ZNE+REM in one job (a
matched-pairs design — the daily drift cancels). But ABSOLUTE thresholds (e.g.
Exp27 T2: error < 1.00pp) re-introduce the confound, because the raw floor itself
wanders ±7pp/day. Exp27 T2 "failed" by 0.02pp — that was measuring the weather,
not the technique.

Fix #1 (this module): snapshot backend.properties() at submit time — T1/T2, 2q
gate error, readout error, and the calibration timestamp — so every result is
TAGGED with the hardware state it was collected under. Zero QPU time (metadata
only). Lets us regress results against the day's calibration and separate
technique-effect from drift-effect.

USAGE
-----
    from calibration_snapshot import capture_calibration
    snap = capture_calibration(backend, physical_qubits=[q0, q1])
    results["calibration"] = snap   # store in results JSON

Always defensive: never raises into a live run. Returns a dict; on any failure
returns {"available": False, "error": "..."} so a missing snapshot can never
break an experiment.
"""

from statistics import median


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def capture_calibration(backend, physical_qubits=None, two_qubit_gates=("cz", "ecr", "cx")):
    """Return a calibration snapshot dict for `backend`.

    physical_qubits: list of physical qubit indices actually used by the
        transpiled circuit (if known). If None, only device-wide medians are
        recorded. Pass these so the snapshot reflects the qubits the result
        actually lived on, not the device average.
    two_qubit_gates: candidate 2q gate names to probe (first one present wins).
    """
    snap = {"available": False}
    try:
        snap["backend_name"] = _safe(lambda: backend.name, _safe(lambda: backend.name(), "unknown"))
        props = None
        get_props = getattr(backend, "properties", None)
        if callable(get_props):
            props = get_props()
        if props is None:
            snap["error"] = "backend.properties() unavailable"
            return snap

        snap["available"] = True
        lud = getattr(props, "last_update_date", None)
        snap["last_update_date"] = lud.isoformat() if lud is not None else None

        # Device-wide medians (units: T1/T2 seconds, readout error fraction)
        n = _safe(lambda: backend.num_qubits, None)
        if n is None:
            n = _safe(lambda: len(props.qubits), 0)
        all_t1, all_t2, all_ro = [], [], []
        for q in range(n or 0):
            t1 = _safe(lambda q=q: props.t1(q))
            t2 = _safe(lambda q=q: props.t2(q))
            ro = _safe(lambda q=q: props.readout_error(q))
            if t1 is not None:
                all_t1.append(t1)
            if t2 is not None:
                all_t2.append(t2)
            if ro is not None:
                all_ro.append(ro)
        snap["device_median"] = {
            "T1_s": median(all_t1) if all_t1 else None,
            "T2_s": median(all_t2) if all_t2 else None,
            "readout_error": median(all_ro) if all_ro else None,
            "n_qubits": n,
        }

        # Per-qubit detail for the qubits actually used
        if physical_qubits:
            per_q = {}
            for q in physical_qubits:
                per_q[int(q)] = {
                    "T1_s": _safe(lambda q=q: props.t1(q)),
                    "T2_s": _safe(lambda q=q: props.t2(q)),
                    "readout_error": _safe(lambda q=q: props.readout_error(q)),
                }
            snap["per_qubit"] = per_q

            # 2-qubit gate error on the coupling actually used (consecutive pairs)
            gate_errs = {}
            for a, b in zip(physical_qubits, physical_qubits[1:]):
                for gname in two_qubit_gates:
                    ge = _safe(lambda gname=gname, a=a, b=b: props.gate_error(gname, [a, b]))
                    if ge is not None:
                        gate_errs[f"{gname}_{a}_{b}"] = ge
                        break
            if gate_errs:
                snap["two_qubit_gate_error"] = gate_errs

        return snap
    except Exception as e:  # absolute backstop — never break a run
        return {"available": False, "error": f"{type(e).__name__}: {e}"}


if __name__ == "__main__":
    # Self-test against FakeMarrakesh (no QPU, no service needed)
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    import json
    b = FakeMarrakesh()
    s = capture_calibration(b, physical_qubits=[0, 1])
    print(json.dumps(s, indent=2, default=str))
