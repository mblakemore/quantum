#!/usr/bin/env python3
"""exp123_pctc_sim.py — P-CTC grandfather-paradox audit, sim tier
(Whisper C4655, horizons-2 Q5). Lloyd postselected-CTC simulation:
the time loop = Bell pair (A,T) closed by Bell-projection onto Phi+;
U(theta)=Ry on T is the attempted grandfather flip; S is a chronology-
respecting BYSTANDER correlated with the traveler before the loop closes.

Everything derived in-code (C4558). Expected structure (sim verifies):
  - herald rate p(theta) ~ cos^2(theta/2): the paradox point theta=pi has
    ZERO self-consistent amplitude — the timeline's enforcement-rate law.
  - the broken-loop arm shares the RATE shape (the projection IS the
    mechanism — stated honestly) but its bystander is theta-independent;
    the LOOP's fingerprint is the heralded bystander rotation.
Qubits: 0=A (past anchor), 1=T (traveler), 2=S (bystander).
clbits: c0=A, c1=T (herald Phi+ <=> c0=c1=0), c2=S."""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 15000
THETAS = [0.0, np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi]


def build(arm, theta, s_basis):
    """arm: loop | broken. s_basis: z | x."""
    qc = QuantumCircuit(3, 3)
    if arm == "loop":
        qc.h(0)
    qc.cx(0, 1)              # Bell(A,T) (identity when broken: A=|0>)
    qc.cx(1, 2)              # bystander correlates with the traveler
    qc.ry(theta, 1)          # the grandfather gun
    qc.cx(1, 0)              # Bell measurement of (T,A)
    qc.h(1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    if s_basis == "x":
        qc.h(2)
    qc.measure(2, 2)
    return qc


def exact(arm, theta):
    qc = build(arm, theta, "z")
    qc.remove_final_measurements()
    psi = Statevector.from_instruction(qc)
    probs = psi.probabilities_dict()      # keys q2 q1 q0
    p_h = zs = xs = 0.0
    # Z of S from heralded (q0=q1=0) probabilities
    for k, p in probs.items():
        if k[1] == "0" and k[2] == "0":
            p_h += p
            zs += p * (1 - 2 * int(k[0]))
    # X of S: rebuild with H on S before the (removed) measurement
    qc2 = build(arm, theta, "x")
    qc2.remove_final_measurements()
    psi2 = Statevector.from_instruction(qc2)
    xacc = 0.0
    for k, p in psi2.probabilities_dict().items():
        if k[1] == "0" and k[2] == "0":
            xacc += p * (1 - 2 * int(k[0]))
    return {"p_herald": p_h,
            "Z_S": zs / p_h if p_h > 1e-12 else None,
            "X_S": xacc / p_h if p_h > 1e-12 else None}


def stats(counts_z, counts_x):
    def herald(counts, want_s=None):
        n = h = acc = 0
        for k, v in counts.items():
            n += v
            if k[1] == "0" and k[2] == "0":
                h += v
                acc += v * (1 - 2 * int(k[0]))
        return n, h, acc
    nz, hz, az = herald(counts_z)
    nx, hx, ax = herald(counts_x)
    p = (hz + hx) / (nz + nx)
    se_p = float(np.sqrt(p * (1 - p) / (nz + nx)))
    zs = az / hz if hz else None
    xs = ax / hx if hx else None
    se_z = float(np.sqrt(max(1e-12, (1 - zs * zs) / hz))) if hz else None
    se_x = float(np.sqrt(max(1e-12, (1 - xs * xs) / hx))) if hx else None
    return {"p_herald": p, "SE_p": se_p, "Z_S": zs, "SE_Z": se_z,
            "X_S": xs, "SE_X": se_x, "n_herald": hz + hx}


def main():
    ex = {}
    for arm in ("loop", "broken"):
        ex[arm] = {f"{t:.4f}": exact(arm, t) for t in THETAS}
    print("EXACT:", json.dumps(ex, indent=1, default=float))
    out = {"exact": ex, "thetas": THETAS}

    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        res = {}
        for arm in ("loop", "broken"):
            for t in THETAS:
                cts = {}
                for sb in ("z", "x"):
                    qc = build(arm, t, sb)
                    tqc = transpile(qc, backend, optimization_level=1,
                                    seed_transpiler=4655,
                                    initial_layout=[0, 1, 2]
                                    if label != "noiseless" else None)
                    cts[sb] = backend.run(tqc, shots=SHOTS).result() \
                                     .get_counts()
                res[f"{arm}_{t:.4f}"] = stats(cts["z"], cts["x"])
        out[label] = res
        if label == "fakemarrakesh":
            k0, kpi = f"loop_{0.0:.4f}", f"loop_{np.pi:.4f}"
            print(f"[fake] p(0)={res[k0]['p_herald']:.4f} "
                  f"p(pi)={res[kpi]['p_herald']:.4f} "
                  f"ratio={res[kpi]['p_herald']/res[k0]['p_herald']:.4f} | "
                  f"X_S(loop,0)={res[k0]['X_S']:.3f} "
                  f"X_S(broken,0)={res[f'broken_{0.0:.4f}']['X_S']:.3f}")
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp123_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp123_feasibility.json")


if __name__ == "__main__":
    main()
