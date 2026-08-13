#!/usr/bin/env python3
"""TURBINE ELEMENT 2 — THE STROKE on q45 (Whisper C5072, board #147).

The loan-and-retrieve demonstration on the measured TLS time-clock (element 1, quantum@166e25d:
q45 node ~12us, return above start by 30us, still rising).

DESIGN (whole-chip; every non-q45 qubit is a free incoherent control):
  X on ALL qubits -> delay ladder {0, 6, 12, 18, 24, 27, 30, 36, 42}us -> measure.
  Per qubit: P1(delay). Clean population prep — deliberately NOT the twin circuit: this
  independently tests whether the q45 swap moves ENERGY (population), not just deep-circuit
  coherence. Plus cal0/cal1 readout blocks, same job.

PRE-REGISTERED PREDICTIONS (frozen before flight):
  P-STROKE: q45's P1(delay) is NON-MONOTONE with a node near ~12us and a return peak in the
    18-36us band, turning amplitude > max(0.04, 3se) — the energy leaves (loan out) and comes
    back (retrieved) on a clean population prep. Round-trip efficiency = P1(peak)/P1(0),
    reported with its interval, vs the T1-only expectation from the flat-population median
    at the same delay (the borrow must beat plain relaxation to count).
  P-CONTROL: population median (non-reviver qubits) is MONOTONE decreasing (plain T1);
    q34 specifically stays monotone (its gate-clock verdict predicts no population return).
  NO-TEST branch (honest): q45 monotone on clean prep -> the element-1 return rides the twin's
    coherence, not bare population; mechanism narrows, no stroke claim, #146 becomes the lane.
CLAIM CLASS if P-STROKE holds: energy parked in and retrieved from a coherent environmental
mode at measured round-trip efficiency — a device running on a natural stream. hbar-omega
scale, joules one-sided, demonstration class (standing fences).
Account IBMQ_ALT4; pending_jobs at submit; epoch-volatile target — same window or NO-TEST.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from qiskit import QuantumCircuit, transpile

BACKEND = "ibm_marrakesh"
NPHYS = 156
DELAYS_US = [0, 6, 12, 18, 24, 27, 30, 36, 42]
Q_TARGET = 45
OUT = os.path.join(QROOT, "results", "exp_turbine_stroke_q45_c5072_manifest.json")


def main(submit=False):
    from qiskit_ibm_runtime import SamplerV2
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT4")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")

    pubs, meta = [], []
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})
    for us in DELAYS_US:
        qc = QuantumCircuit(NPHYS)
        qc.x(range(NPHYS))
        if us > 0:
            for q in range(NPHYS):
                qc.delay(us, q, unit="us")
        qc.measure_all()
        tqc = transpile(qc, backend, optimization_level=0, initial_layout=list(range(NPHYS)))
        pubs.append((tqc, None, 12000))
        meta.append({"block": f"stroke_delay{us}us", "delay_us": us, "shots": 12000})
        print(f"  [$0-validate] X + {us}us + measure: built")

    man = {"card": "exp_turbine_stroke_q45", "cycle": "C5072", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date),
           "delays_us": DELAYS_US, "q_target": Q_TARGET, "account": "IBMQ_ALT4",
           "purpose": "Turbine element 2 (board #147): loan-and-retrieve stroke on the q45 TLS time-clock; clean population prep",
           "element1_reference": "d9v4v5l0vrcc73boput0 (same window intended)",
           "prereg": "predictions + NO-TEST branch in docstring, committed pre-flight",
           "pubs_meta": meta}
    if submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted (pass --submit to fly)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
