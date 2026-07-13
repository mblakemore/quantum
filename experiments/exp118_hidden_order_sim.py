#!/usr/bin/env python3
"""exp118_hidden_order_sim.py — hidden-order diagnostics, sim tier (Whisper C4624).

Purpose per the design doc: FakeMarrakesh has NO crosstalk model, so this tier
(a) validates the builder + TVD/bootstrap estimator machinery and (b) measures
the TVD SHOT-NOISE FLOOR at budget — the feasibility input for the D_order gate.
Any hardware reading above this floor is an unmodeled effect by construction.
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from qiskit import QuantumCircuit, transpile  # noqa: E402

K = 8            # layer amplification
SHOTS = 6000


def probe(schedule, k=K, spectator=True):
    """5 qubits: pairA=(0,1), spectator=2, pairB=(3,4). Probe state: |+> on all
    (maximally sensitive to ZZ-type crosstalk phases). Amplified k layers."""
    qc = QuantumCircuit(5, 5)
    for q in range(5):
        qc.h(q)
    for _ in range(k):
        if schedule == "seqAB":
            qc.cz(0, 1)
            qc.barrier()
            qc.cz(3, 4)
            qc.barrier()
        elif schedule == "seqBA":
            qc.cz(3, 4)
            qc.barrier()
            qc.cz(0, 1)
            qc.barrier()
        else:                      # par
            qc.cz(0, 1)
            qc.cz(3, 4)
            qc.barrier()
    for q in range(5):
        qc.h(q)                    # X-basis read on everything (phase-sensitive)
    qc.measure(range(5), range(5))
    return qc


def tvd(c1, c2):
    n1, n2 = sum(c1.values()), sum(c2.values())
    keys = set(c1) | set(c2)
    return 0.5 * sum(abs(c1.get(k, 0) / n1 - c2.get(k, 0) / n2) for k in keys)


def boot_se(c1, c2, B=200, rng=None):
    rng = rng or np.random.default_rng(4624)
    k1, v1 = list(c1.keys()), np.array(list(c1.values()))
    k2, v2 = list(c2.keys()), np.array(list(c2.values()))
    ts = []
    for _ in range(B):
        r1 = dict(zip(k1, rng.multinomial(v1.sum(), v1 / v1.sum())))
        r2 = dict(zip(k2, rng.multinomial(v2.sum(), v2 / v2.sum())))
        ts.append(tvd(r1, r2))
    return float(np.std(ts))


def main():
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out = {}
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        counts = {}
        for sch in ("seqAB", "seqBA", "par"):
            qc = probe(sch)
            tqc = transpile(qc, backend, optimization_level=1,
                            seed_transpiler=4624,
                            initial_layout=[0, 1, 2, 3, 4]
                            if label != "noiseless" else None)
            counts[sch] = backend.run(tqc, shots=SHOTS).result().get_counts()
        mix = {}
        for k, v in counts["seqAB"].items():
            mix[k] = mix.get(k, 0) + v / 2
        for k, v in counts["seqBA"].items():
            mix[k] = mix.get(k, 0) + v / 2
        r = {"D_order": tvd(counts["seqAB"], counts["seqBA"]),
             "D_A": tvd(counts["par"], counts["seqAB"]),
             "D_B": tvd(counts["par"], counts["seqBA"]),
             "D_mix": tvd(counts["par"], mix),
             "se_order": boot_se(counts["seqAB"], counts["seqBA"])}
        out[label] = r
        print(f"[{label}] D_order={r['D_order']:.4f}±{r['se_order']:.4f}  "
              f"D_A={r['D_A']:.4f} D_B={r['D_B']:.4f} D_mix={r['D_mix']:.4f}")
    # the floor: same-distribution TVD at budget (noise-model-free statement)
    floor = out["fakemarrakesh"]["D_order"]
    print(f"\nTVD shot-noise floor at {SHOTS} shots, 5q, k={K}: ~{floor:.3f} "
          f"(the D_order gate floor must sit >= floor + 5*se; hardware readings "
          f"above it are unmodeled-by-construction)")
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp118_feasibility.json"), "w"), indent=1)
    print("wrote results/exp118_feasibility.json")


if __name__ == "__main__":
    main()
