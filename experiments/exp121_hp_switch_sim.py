#!/usr/bin/env python3
"""exp121_hp_switch_sim.py — Hayden-Preskill x switch, sim tier (Whisper C4646).
Horizons-2 Q3. Apparatus = the Exp120 skeleton VERBATIM (same slots, same CCZ
blocks, hardware-certified at 22/52sigma at C4645); only the probe encoding and
readout change: diary in X on P, retrieval measured on P ALONE.

Qubits: 0=C, 1=P (probe/diary), 2=E1 (Z-query env), 3=E2 (X-query env).
Definite orders: the Z-query dephases the diary -> P alone is DEAD (S_X=0).
Question: do the heralded switch branches retrieve the diary from P alone?
Everything computed in-code (C4558)."""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 30000


def query_z(qc, ctrl=None):
    """Horizon query 1: records Z of P into E1 (dephases X)."""
    if ctrl is None:
        qc.cz(1, 2)
    else:
        qc.ccz(0, 1, 2)


def query_x(qc, ctrl=None):
    """Horizon query 2: records X of P into E2."""
    qc.h(1)
    if ctrl is None:
        qc.cz(1, 3)
    else:
        qc.ccz(0, 1, 3)
    qc.h(1)


def build(arm, diary):
    """arm: ordZX | ordXZ | switch | null; diary: '+' | '-'.
    clbits: c0=C herald, c1=P (X basis), c2=E1 (X), c3=E2 (X)."""
    qc = QuantumCircuit(4, 4)
    qc.h(1)
    if diary == "-":
        qc.z(1)
    qc.h(2)
    qc.h(3)
    if arm == "ordZX":
        query_z(qc)
        query_x(qc)
    elif arm == "ordXZ":
        query_x(qc)
        query_z(qc)
    else:
        if arm == "switch":
            qc.h(0)
        qc.x(0)
        query_z(qc, ctrl=0)
        qc.x(0)
        qc.x(0)
        query_x(qc, ctrl=0)
        qc.x(0)
        query_x(qc, ctrl=0)
        query_z(qc, ctrl=0)
        qc.h(0)
        qc.measure(0, 0)
    qc.h(1)
    qc.measure(1, 1)
    qc.h(2)
    qc.measure(2, 2)
    qc.h(3)
    qc.measure(3, 3)
    return qc


def exact_arm(arm):
    """Exact per-branch: S_P (diary retrieval from P alone), and joint-decoder
    diagnostics S_PE2 (P+E2 majority-free best: use E2 record alone) etc."""
    out = {}
    for diary in ("+", "-"):
        qc = build(arm, diary)
        qc.remove_final_measurements()
        psi = Statevector.from_instruction(qc)
        probs = psi.probabilities_dict()   # keys q3 q2 q1 q0
        for k, p in probs.items():
            q3, q2, q1, q0 = k[0], k[1], k[2], k[3]
            br = q0 if arm == "switch" else "all"
            d = out.setdefault(br, {"n": 0.0, "hit_P": 0.0, "hit_E2": 0.0,
                                    "hit_E1": 0.0})
            d["n"] += p
            want = "0" if diary == "+" else "1"      # X-basis: 0 <-> +
            if q1 == want:
                d["hit_P"] += p
            if q3 == want:
                d["hit_E2"] += p
            if q2 == want:
                d["hit_E1"] += p
    res = {}
    for br, d in out.items():
        res[br] = {"rate": d["n"] / 2,
                   "S_P": d["hit_P"] / d["n"] - 0.5,
                   "S_E2": d["hit_E2"] / d["n"] - 0.5,
                   "S_E1": d["hit_E1"] / d["n"] - 0.5}
    return res


def counts_arm(cts, arm):
    """cts: {(diary): counts}. Same estimator from samples."""
    acc = {}
    for diary in ("+", "-"):
        want = "0" if diary == "+" else "1"
        for k, v in cts[diary].items():
            q3, q2, q1, q0 = k[0], k[1], k[2], k[3]
            br = q0 if arm == "switch" else "all"
            d = acc.setdefault(br, {"n": 0, "hit_P": 0, "hit_E2": 0})
            d["n"] += v
            if q1 == want:
                d["hit_P"] += v
            if q3 == want:
                d["hit_E2"] += v
    res = {}
    for br, d in acc.items():
        p = d["hit_P"] / d["n"]
        res[br] = {"S_P": p - 0.5,
                   "SE_S_P": float(np.sqrt(p * (1 - p) / d["n"])),
                   "S_E2": d["hit_E2"] / d["n"] - 0.5,
                   "n": d["n"]}
    return res


def main():
    exact = {arm: exact_arm(arm) for arm in ("ordZX", "ordXZ", "switch", "null")}
    print("EXACT (statevector):")
    print(json.dumps(exact, indent=1, default=float))

    geometry = {
        "S_P_ordZX": exact["ordZX"]["all"]["S_P"],
        "S_P_ordXZ": exact["ordXZ"]["all"]["S_P"],
        "S_P_switch_plus": exact["switch"].get("0", {}).get("S_P"),
        "S_P_switch_minus": exact["switch"].get("1", {}).get("S_P"),
        "rate_minus": exact["switch"].get("1", {}).get("rate"),
    }
    print("RETRIEVAL GEOMETRY:", json.dumps(geometry, indent=1, default=float))
    out = {"exact": exact, "geometry": geometry}

    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        res = {}
        for arm in ("ordZX", "ordXZ", "switch", "null"):
            cts = {}
            for diary in ("+", "-"):
                qc = build(arm, diary)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4646,
                                initial_layout=[0, 1, 2, 3]
                                if label != "noiseless" else None)
                cts[diary] = backend.run(tqc, shots=SHOTS // 2).result() \
                                    .get_counts()
            res[arm] = counts_arm(cts, arm)
        out[label] = res
        print(f"[{label}] " + json.dumps(res, indent=1, default=float)[:900])

    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp121_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp121_feasibility.json")


if __name__ == "__main__":
    main()
