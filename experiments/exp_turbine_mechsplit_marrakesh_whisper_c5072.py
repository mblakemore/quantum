#!/usr/bin/env python3
"""TURBINE ELEMENT 1 — mechanism-split control (Whisper C5072, board #147).

Splits the #144 revival's clock: TIME (TLS energy swap — the harvestable stream) vs GATE
(depth-space coherent interference — not an energy stream).

Design: the d160 twin (identical circuit object the scout flew, one code path) with an
APPENDED IDLE DELAY ladder before measurement: {0, 6, 12, 18, 24, 30} microseconds — spanning
the same wall-clock the scout's depth ladder added (d160->400 ~ +24us of gates). Same-window
readout cal (cal0/cal1) as always.

PRE-REGISTERED PREDICTIONS (before decode):
  - TIME-clock: reviver qubits' |<Z>| at fixed depth OSCILLATES vs added delay with the same
    class of period the depth ladder showed (q34 ~120 d2q ~ 12us equivalent) -> TLS confirmed,
    element 2 (extraction stroke) proceeds.
  - GATE-clock: |<Z>| flat-or-monotone vs delay (within noise) on the reviver set -> the
    revival is interference, NOT a borrowable energy stream: post the honest null, stream 3
    (cyclic QET, #146) becomes the turbine lane.
  - Mixed per-qubit verdicts are reported per qubit; no aggregate spin.
DECODE RULE (frozen): per reviver qubit q in {7,24,27,31,34,45,53}: oscillation test = does
|<Z>|(delay) leave the [min,max] band of its own shot-noise + readout envelope with a turning
point (rise after fall or fall after rise) exceeding the scout's REVIVAL_MIN 0.04? Same
estimator math as the scout decode (readout-corrected |<Z>|), same thresholds.
Account: IBMQ_ALT4 (free, open). pending_jobs at submit captured.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp_crossblock_widesweep import build_twins, SEED
from qiskit import QuantumCircuit, transpile
import numpy as np

BACKEND = "ibm_marrakesh"
NPHYS = 156
DELAYS_US = [0, 6, 12, 18, 24, 30]
OUT = os.path.join(QROOT, "results", "exp_turbine_mechsplit_c5072_manifest.json")


def main(submit=False):
    from qiskit_ibm_runtime import SamplerV2
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT4")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")

    twins, active = build_twins(backend)
    base = twins[160]
    pubs, meta = [], []
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})
    for us in DELAYS_US:
        mc = base.copy()
        if us > 0:
            for q in range(mc.num_qubits):
                mc.delay(us, q, unit="us")
        mc.measure_all()
        tqc = transpile(mc, backend, optimization_level=0, initial_layout=list(range(NPHYS)),
                        seed_transpiler=SEED)
        pubs.append((tqc, None, 12000))
        meta.append({"block": f"d160_delay{us}us", "delay_us": us, "shots": 12000})
        print(f"  [$0-validate] d160 + {us}us idle: built")

    man = {"card": "exp_turbine_mechsplit", "cycle": "C5072", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date),
           "delays_us": DELAYS_US, "register": active, "seed": SEED, "account": "IBMQ_ALT4",
           "purpose": "Turbine element 1 (board #147): split TIME-clock (TLS swap, harvestable) from GATE-clock (interference) on the #144 reviver set",
           "reviver_targets": [7, 24, 27, 31, 34, 45, 53],
           "scout_reference": "d9v4s3gb1g9c73a867bg (same window intended)",
           "prereg": "predictions + frozen decode rule in this script's docstring, committed pre-flight",
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
