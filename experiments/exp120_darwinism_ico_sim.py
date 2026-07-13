#!/usr/bin/env python3
"""exp120_darwinism_ico_sim.py — Darwinism x ICO, sim tier (Whisper C4643).
Design: exp120-darwinism-ico-design.md. Exact statevector truth + FakeMarrakesh
at budget. Everything derived in-code (C4558 discipline).

Qubits: 0=C, 1=S, 2=F1 (Z-recorder), 3=F2 (X-recorder).
"""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 30000
THETA_S = np.pi / 4          # Ry angle: S = cos(pi/8)|0> + sin(pi/8)|1>


def copy_z(qc, ctrl=None):
    if ctrl is None:
        qc.cz(1, 2)
    else:
        qc.ccz(0, 1, 2)


def copy_x(qc, ctrl=None):
    qc.h(1)
    if ctrl is None:
        qc.cz(1, 3)
    else:
        qc.ccz(0, 1, 3)
    qc.h(1)


def build(arm, s_basis):
    """arm: ordZX | ordXZ | switch | null. s_basis: 'z' | 'x'.
    clbits: c0=C herald, c1=S, c2=F1, c3=F2."""
    qc = QuantumCircuit(4, 4)
    qc.ry(THETA_S, 1)
    qc.h(2)
    qc.h(3)
    if arm == "ordZX":
        copy_z(qc)
        copy_x(qc)
    elif arm == "ordXZ":
        copy_x(qc)
        copy_z(qc)
    else:
        if arm == "switch":
            qc.h(0)
        # slot 1: copy-Z if C=0
        qc.x(0)
        copy_z(qc, ctrl=0)
        qc.x(0)
        # slot 2: copy-X if C=0
        qc.x(0)
        copy_x(qc, ctrl=0)
        qc.x(0)
        # slot 3: copy-X if C=1
        copy_x(qc, ctrl=0)
        # slot 4: copy-Z if C=1
        copy_z(qc, ctrl=0)
        qc.h(0)              # herald in X basis
        qc.measure(0, 0)
    if s_basis == "x":
        qc.h(1)
    qc.measure(1, 1)
    qc.h(2)
    qc.measure(2, 2)
    qc.h(3)
    qc.measure(3, 3)
    return qc


def exact_arm(arm):
    """Exact A_Z, A_X per herald branch via statevector."""
    out = {}
    for s_basis in ("z", "x"):
        qc = build(arm, s_basis)
        qc.remove_final_measurements()
        psi = Statevector.from_instruction(qc)
        probs = psi.probabilities_dict()   # keys: q3 q2 q1 q0
        # branch on q0 (herald): for switch, 0=plus, 1=minus; else pooled
        acc = {}
        for k, p in probs.items():
            q3, q2, q1, q0 = k[0], k[1], k[2], k[3]
            br = q0 if arm == "switch" else "all"
            a = acc.setdefault(br, {"n": 0.0, "agree_z": 0.0, "agree_x": 0.0})
            a["n"] += p
            if s_basis == "z":
                # F1 record: q2 ('0'=X+ -> S_Z=0). Agreement with S outcome q1.
                if q2 == q1:
                    a["agree_z"] += p
            else:
                # F2 record: q3 ('0'=X+ -> S_X=+). S X-outcome q1 after H.
                if q3 == q1:
                    a["agree_x"] += p
        for br, a in acc.items():
            d = out.setdefault(br, {"rate": a["n"]})
            if s_basis == "z":
                d["A_Z"] = a["agree_z"] / a["n"]
            else:
                d["A_X"] = a["agree_x"] / a["n"]
    return out


def counts_arm(counts_z, counts_x, arm):
    """Same estimator from sampled counts (keys c3 c2 c1 c0)."""
    out = {}
    for counts, s_basis in ((counts_z, "z"), (counts_x, "x")):
        acc = {}
        for k, v in counts.items():
            q3, q2, q1, q0 = k[0], k[1], k[2], k[3]
            br = q0 if arm == "switch" else "all"
            a = acc.setdefault(br, {"n": 0, "agree": 0})
            a["n"] += v
            rec = q2 if s_basis == "z" else q3
            if rec == q1:
                a["agree"] += v
        for br, a in acc.items():
            d = out.setdefault(br, {})
            key = "A_Z" if s_basis == "z" else "A_X"
            p = a["agree"] / a["n"]
            d[key] = p
            d[f"SE_{key}"] = float(np.sqrt(p * (1 - p) / a["n"]))
            d[f"n_{s_basis}"] = a["n"]
    return out


def main():
    exact = {arm: exact_arm(arm) for arm in ("ordZX", "ordXZ", "switch", "null")}
    print("EXACT (statevector):")
    print(json.dumps(exact, indent=1, default=float))

    # witness geometry
    wZX = exact["ordZX"]["all"]["A_Z"] + exact["ordZX"]["all"]["A_X"]
    wXZ = exact["ordXZ"]["all"]["A_Z"] + exact["ordXZ"]["all"]["A_X"]
    hull = sorted([wZX, wXZ])
    geometry = {"w_ordZX": wZX, "w_ordXZ": wXZ, "hull": hull}
    for br in ("0", "1"):
        b = exact["switch"].get(br)
        if b and "A_Z" in b and "A_X" in b:
            w = b["A_Z"] + b["A_X"]
            side = ("ABOVE" if w > hull[1] else
                    "BELOW" if w < hull[0] else "inside")
            geometry[f"w_switch_{'plus' if br == '0' else 'minus'}"] = w
            geometry[f"hull_position_{'plus' if br == '0' else 'minus'}"] = side
            geometry[f"violation_{'plus' if br == '0' else 'minus'}"] = (
                max(w - hull[1], hull[0] - w, 0.0))
    print("WITNESS GEOMETRY:", json.dumps(geometry, indent=1, default=float))

    out = {"exact": exact, "geometry": geometry}

    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        res = {}
        twoq_counts = {}
        for arm in ("ordZX", "ordXZ", "switch", "null"):
            cts = {}
            for s_basis in ("z", "x"):
                qc = build(arm, s_basis)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4643,
                                initial_layout=[0, 1, 2, 3]
                                if label != "noiseless" else None)
                n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                         and i.operation.name != "barrier")
                twoq_counts[f"{arm}_{s_basis}"] = n2
                cts[s_basis] = backend.run(tqc, shots=SHOTS).result().get_counts()
            res[arm] = counts_arm(cts["z"], cts["x"], arm)
        out[label] = res
        if label == "fakemarrakesh":
            out["twoq_counts"] = twoq_counts
        print(f"[{label}] " + json.dumps(res, indent=1, default=float)[:1200])

    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp120_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp120_feasibility.json")


if __name__ == "__main__":
    main()
