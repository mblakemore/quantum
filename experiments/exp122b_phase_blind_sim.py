#!/usr/bin/env python3
"""exp122b_phase_blind_sim.py — phase-blind twin retest, builders + estimator
(Whisper C4653). Parent: Exp122 (win-as-frozen, mechanism confounded by ZZ
clock-pull rotation — C4651). Fix: |V| = sqrt(<X>^2 + <Y>^2) is rotation-immune;
an echo arm (X on C mid-delay) cancels static ZZ as an independent discriminator.

Frozen estimator: Rice-bias-corrected |V|:
    V^2_hat = max(<X>^2 + <Y>^2 - SE_X^2 - SE_Y^2, 0);  SE by delta method.
Fake preview note (pre-filed): FakeMarrakesh delay noise is pure relaxation (no
coherent ZZ), so fake predicts echo == raw and X == |V|; hardware DIVERGENCE
between raw-X and |V|/echo is itself the ZZ measurement."""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000


def build_b(excited, dt_us, readout, echo=False):
    """Qubits 0=C, 1=K, 2=L. readout: 'x'|'y' on C. echo: X on C mid-delay.
    clbits: c0=C, c1=K, c2=L (K/L in Z: clock-survival diagnostics)."""
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    if excited:
        qc.x(1)
    qc.cswap(0, 1, 2)
    qc.barrier()
    if echo:
        half = int(dt_us * 500)          # ns per half
        if half > 0:
            qc.delay(half, 1, unit="ns")
            qc.delay(half, 2, unit="ns")
        qc.barrier()
        qc.x(0)
        qc.barrier()
        if half > 0:
            qc.delay(half, 1, unit="ns")
            qc.delay(half, 2, unit="ns")
    elif dt_us > 0:
        qc.delay(int(dt_us * 1000), 1, unit="ns")
        qc.delay(int(dt_us * 1000), 2, unit="ns")
    qc.barrier()
    qc.cswap(0, 1, 2)
    if readout == "y":
        qc.sdg(0)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.measure(2, 2)
    return qc


def expec_c(counts):
    n = p = 0
    for k, v in counts.items():
        n += v
        if k[2] == "0":
            p += v
    e = 2 * p / n - 1
    return e, float(np.sqrt(max(1e-12, (1 - e * e) / n)))


def vis_rice(x, sex, y, sey):
    """Rice-corrected |V| and delta-method SE (FROZEN estimator)."""
    v2 = x * x + y * y - sex * sex - sey * sey
    v = float(np.sqrt(max(v2, 0.0)))
    if v > 1e-6:
        se = float(np.sqrt((x * sex) ** 2 + (y * sey) ** 2) / v)
    else:
        se = float(max(sex, sey))
    return v, se


def main():
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = AerSimulator.from_backend(FakeMarrakesh())
    out = {}
    for arm, excited, echo in (("exc", True, False), ("vac", False, False),
                               ("exc_echo", True, True)):
        pts = []
        for dt in (0.0, 50.0, 100.0):
            xy = {}
            for ro in ("x", "y"):
                qc = build_b(excited, dt, ro, echo)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4653, initial_layout=[0, 1, 2],
                                scheduling_method="asap")
                cts = backend.run(tqc, shots=SHOTS).result().get_counts()
                xy[ro] = expec_c(cts)
            v, se = vis_rice(xy["x"][0], xy["x"][1], xy["y"][0], xy["y"][1])
            pts.append({"dt_us": dt, "X": xy["x"][0], "Y": xy["y"][0],
                        "V": v, "SE_V": se})
        out[arm] = pts
        print(arm, json.dumps(pts, default=float))
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp122b_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp122b_feasibility.json")


if __name__ == "__main__":
    main()
