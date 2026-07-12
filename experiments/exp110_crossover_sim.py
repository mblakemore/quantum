#!/usr/bin/env python3
"""exp110_crossover_sim.py — SWAP-vs-teleport crossover, sim tiers (Whisper C4595).

Design doc: experiments/exp110-swap-vs-teleport-crossover-design.md (E2).
Arms per N hops in {1,2,4,6}, probe preps {0,1,+,+i}:
  swap     : probe on q0, N SWAPs down a line, unprep, measure (3 CZ/hop after compile)
  teleport : fresh Bell pair per hop, Bell measurement + feedforward (if_test)
             corrections — depth per hop ~constant, classical wire does the work
Estimator (frozen at prereg): mean survival probability over the 4 probe preps,
measured in the prep basis (declared estimator, not full process fidelity).
Noiseless tier doubles as the CORRECTIONS-WIRING VALIDATOR: survival must be 1.0000
for every (arm, N, prep) or the feedforward is miswired.
CAVEAT carried from the design doc: FakeMarrakesh does not model feedforward
latency noise — the teleport-arm preview is optimistic in an UNKNOWN amount; the
prereg must gate on the relative comparison, not absolute teleport fidelity.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile  # noqa: E402

HOPS = [1, 2, 4, 6]
PREPS = ["0", "1", "+", "+i"]
SHOTS = 3000


def prep(qc, q, p):
    if p == "1":
        qc.x(q)
    elif p == "+":
        qc.h(q)
    elif p == "+i":
        qc.h(q)
        qc.s(q)


def unprep(qc, q, p):
    if p == "1":
        qc.x(q)
    elif p == "+":
        qc.h(q)
    elif p == "+i":
        qc.sdg(q)
        qc.h(q)


def swap_chain(n_hops, p):
    qr = QuantumRegister(n_hops + 1)
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qr, cr)
    prep(qc, 0, p)
    for i in range(n_hops):
        qc.swap(i, i + 1)
    unprep(qc, n_hops, p)
    qc.measure(n_hops, 0)
    return qc, n_hops


def teleport_chain(n_hops, p):
    # qubits: 0 = source; per hop i: (1+2i, 2+2i) = Bell pair (a_i lands next state)
    qr = QuantumRegister(1 + 2 * n_hops)
    crs = [ClassicalRegister(2, f"m{i}") for i in range(n_hops)]
    out = ClassicalRegister(1, "out")
    qc = QuantumCircuit(qr, *crs, out)
    prep(qc, 0, p)
    src = 0
    for i in range(n_hops):
        a, b = 1 + 2 * i, 2 + 2 * i
        qc.h(a)
        qc.cx(a, b)
        qc.cx(src, a)
        qc.h(src)
        qc.measure(src, crs[i][0])   # phase bit
        qc.measure(a, crs[i][1])     # flip bit
        with qc.if_test((crs[i][1], 1)):
            qc.x(b)
        with qc.if_test((crs[i][0], 1)):
            qc.z(b)
        src = b
    unprep(qc, src, p)
    qc.measure(src, out)
    return qc, src


def survival(counts):
    # success = out register bit 0; count keys look like 'o mN ... m0' space-separated
    n_ok = sum(v for k, v in counts.items() if k.split()[0] == "0")
    return n_ok / sum(counts.values())


def run_tier(backend, label):
    from collections import defaultdict
    res = defaultdict(dict)
    for arm, builder in (("swap", swap_chain), ("teleport", teleport_chain)):
        for n in HOPS:
            surv = []
            for p in PREPS:
                qc, _ = builder(n, p)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4595)
                c = backend.run(tqc, shots=SHOTS).result().get_counts()
                surv.append(survival(c))
            m = float(np.mean(surv))
            res[arm][n] = {"mean_survival": m,
                           "per_prep": dict(zip(PREPS, map(float, surv))),
                           "se": float(np.sqrt(m * (1 - m) / (SHOTS * 4)))}
    print(f"[{label}]")
    for arm in ("swap", "teleport"):
        line = "  ".join(f"N={n}: {res[arm][n]['mean_survival']:.4f}" for n in HOPS)
        print(f"  {arm:9s} {line}")
    return dict(res)


def main():
    from qiskit_aer import AerSimulator
    ideal = AerSimulator()
    r1 = run_tier(ideal, "noiseless")
    for arm in ("swap", "teleport"):
        for n in HOPS:
            assert r1[arm][n]["mean_survival"] > 0.999, (arm, n, r1[arm][n])
    print("WIRING VALIDATOR PASS: survival 1.0 for every (arm, N, prep)")
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    noisy = AerSimulator.from_backend(FakeMarrakesh())
    r2 = run_tier(noisy, "FakeMarrakesh (no feedforward-latency noise — stated caveat)")
    json.dump({"tier1_noiseless": r1, "tier2_fakemarrakesh": r2},
              open(os.path.join(HERE, "..", "results", "exp110_feasibility.json"),
                   "w"), indent=1)
    print("wrote results/exp110_feasibility.json")


if __name__ == "__main__":
    main()
