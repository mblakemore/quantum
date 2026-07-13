#!/usr/bin/env python3
"""exp117_extraction_sim.py — the extraction stroke, sim tier (Whisper C4613,
horizons P4 rung 2). Turn certified ergotropy (F94) into a demonstrated engine
stroke: measure the control mid-circuit; IF the − outcome selected the inverted
branch, fire a conditional X (feedforward) that de-excites it. Work extraction
is PHYSICAL — no software frame can do it — so this is the first protocol where
active feedforward is REQUIRED, and its F90-class cost is the demon's cost of
acting.

Arms (per rung at prereg; sim validates the mechanism):
  measure : Exp116b switch arm unchanged (re-certifies inversion in-window)
  extract : same switch, control measured mid-circuit, if_test('1' = minus)
            fires X on the fluid, then fluid measured.
Noiseless validator: p_post|− = 1 − p_pre|− exactly, p_post|+ = p_pre|+
(the + branch is untouched), and ALL post-extraction branches are passive.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit  # noqa: E402
import exp108b_native_thermal as m108  # noqa: E402

m108.P_TARGET = 0.45


def build_extract(t0, delay_a_s, delay_b_s):
    """Switch arm with mid-circuit control readout + conditional extraction X."""
    qc = QuantumCircuit(4, 2)
    qc.x(2)
    qc.x(3)
    qc.delay(delay_a_s, 2, unit="s")
    qc.delay(delay_b_s, 3, unit="s")
    qc.barrier()
    if t0:
        qc.x(1)
    qc.h(0)
    qc.barrier()
    qc.cswap(0, 1, 2)
    qc.cswap(0, 1, 3)
    qc.barrier()
    qc.swap(1, 2)
    qc.swap(1, 3)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)                 # control FIRST (mid-circuit)
    with qc.if_test((0, 1)):         # clbit0 == 1  <=>  minus outcome
        qc.x(1)                      # the extraction stroke
    qc.measure(1, 1)
    return qc


def cond_p1(counts):
    """p1 of fluid conditioned on control outcome, from 'tc' keys."""
    out = {}
    for cbit, name in (("0", "+"), ("1", "-")):
        n = sum(v for k, v in counts.items() if k[1] == cbit)
        n1 = sum(v for k, v in counts.items() if k[1] == cbit and k[0] == "1")
        out[name] = (n1 / n if n else None, n)
    return out


def run(backend, builder, d_a, d_b, shots=20000, seed=4613, pool_p=None):
    """pool_p set => noiseless tier: delays are no-ops without a noise model
    (C4613 validator catch), so baths are realized by ANCILLA BASIS-PREP POOLING
    at weight p per excited ancilla — the exact 108b pooled-equivalent."""
    from qiskit import transpile
    import itertools
    pooled = {}
    preps = list(itertools.product((0, 1), repeat=2)) if pool_p else [(None, None)]
    for t0 in (0, 1):
        for a1, a2 in preps:
            qc = builder(t0, d_a, d_b)
            if pool_p is not None:
                # strip the thermal X's and delays; re-prep ancillas per (a1,a2)
                from qiskit import QuantumCircuit
                q2 = QuantumCircuit(4, 2)
                if a1:
                    q2.x(2)
                if a2:
                    q2.x(3)
                started = False
                for inst in qc.data:
                    nm = inst.operation.name
                    if not started:
                        if nm == "barrier":
                            started = True
                        continue
                    q2.append(inst.operation, inst.qubits, inst.clbits)
                qc = q2
            w = ((0.75 if t0 == 0 else 0.25) *
                 ((pool_p if a1 else 1 - pool_p) if pool_p else 1) *
                 ((pool_p if a2 else 1 - pool_p) if pool_p else 1))
            tqc = transpile(qc, backend, optimization_level=3, seed_transpiler=4562)
            c = backend.run(tqc, shots=max(int(shots * w), 1),
                            seed_simulator=seed).result().get_counts()
            for k, v in c.items():
                pooled[k] = pooled.get(k, 0) + v
    return cond_p1(pooled)


def main():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    t1 = 200e-6
    d = t1 * np.log(1 / 0.45)
    meas = run(sim, lambda t0, a, b: m108.build_circuit_native(t0, "switch", a, b),
               d, d, pool_p=0.45)
    extr = run(sim, build_extract, d, d, pool_p=0.45)
    print(f"[noiseless] measure: p1|+={meas['+'][0]:.4f} p1|-={meas['-'][0]:.4f}")
    print(f"[noiseless] extract: p1|+={extr['+'][0]:.4f} p1|-={extr['-'][0]:.4f}")
    assert abs(extr["-"][0] - (1 - meas["-"][0])) < 0.01, "extraction flip wrong"
    assert abs(extr["+"][0] - meas["+"][0]) < 0.01, "+ branch disturbed"
    assert extr["-"][0] < 0.5 and extr["+"][0] < 0.5, "branch not passive post-stroke"
    work = (2 * meas["-"][0] - 1)
    print(f"VALIDATOR PASS: stroke flips - branch exactly (p_post = 1 - p_pre), "
          f"+ branch untouched, all branches passive. Work/(- run) = {work:.4f} E")
    json.dump({"noiseless": {"measure": {k: v[0] for k, v in meas.items()},
                             "extract": {k: v[0] for k, v in extr.items()}}},
              open(os.path.join(HERE, "..", "results",
                                "exp117_feasibility.json"), "w"), indent=1)
    print("wrote results/exp117_feasibility.json")


if __name__ == "__main__":
    main()
