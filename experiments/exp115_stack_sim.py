#!/usr/bin/env python3
"""exp115_stack_sim.py — network-stack composition, sim tier v1 (Whisper C4608,
horizons P2 capstone). PURIFY -> CARRY: superdense coding through a purified pair.

The resurrection story extended to the APPLICATION layer: at injected noise p*,
a raw noisy pair degrades superdense decoding; the BBPSSW-purified pair restores
it. Arms: sd_clean (p=0 baseline) / sd_raw (noisy pair) / sd_purified (two noisy
pairs -> purify -> superdense on survivor). Validator: p=0 purified == clean == 1.
Qubits (chain order): B2-A2-A1-B1; superdense encode on A1, Bell-measure (A1,B1).
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile  # noqa: E402

PAULIS = ["I", "X", "Y", "Z"]
ENC = {"00": [], "01": ["x"], "10": ["z"], "11": ["z", "x"]}
SHOTS = 3000


def apply_pauli(qc, q, p):
    if p != "I":
        getattr(qc, p.lower())(q)


def circuit(arm, msg, noise=("I", "I")):
    if arm in ("sd_clean", "sd_raw"):
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        apply_pauli(qc, 1, noise[0])
        qc.barrier()
        for g in ENC[msg]:
            getattr(qc, g)(0)
        qc.barrier()
        qc.cx(0, 1)
        qc.h(0)
        qc.measure([0, 1], [0, 1])
        return qc
    qr = QuantumRegister(4)          # 0=B2,1=A2,2=A1,3=B1
    coin = ClassicalRegister(2, "coin")
    out = ClassicalRegister(2, "sd")
    qc = QuantumCircuit(qr, coin, out)
    qc.h(2); qc.cx(2, 3)
    qc.h(1); qc.cx(1, 0)
    apply_pauli(qc, 3, noise[0])
    apply_pauli(qc, 0, noise[1])
    qc.cx(2, 1)
    qc.cx(3, 0)
    qc.measure(1, coin[0])
    qc.measure(0, coin[1])
    qc.barrier()
    for g in ENC[msg]:
        getattr(qc, g)(2)            # encode on A1
    qc.barrier()
    qc.cx(2, 3)
    qc.h(2)
    qc.measure(2, out[0])
    qc.measure(3, out[1])
    return qc


def p_success(backend, arm, p_noise, seed=4608):
    w1 = {"I": 1 - 3 * p_noise / 4, "X": p_noise / 4, "Y": p_noise / 4,
          "Z": p_noise / 4}
    labels = ([("I", "I")] if p_noise == 0 else
              (list(itertools.product(PAULIS, PAULIS)) if arm == "sd_purified"
               else [(a, "I") for a in PAULIS]))
    ok, tot = 0, 0
    for msg in ENC:
        for lab in labels:
            w = w1[lab[0]] * (w1[lab[1]] if arm == "sd_purified" else 1)
            if p_noise == 0:
                w = 1.0
            shots = max(int(round(SHOTS * w)), 1)
            qc = circuit(arm, msg, lab)
            tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=seed)
            counts = backend.run(tqc, shots=shots).result().get_counts()
            for key, v in counts.items():
                toks = key.split()
                if arm == "sd_purified":
                    sd, co = toks[0], toks[1]
                    if co[0] != co[1]:
                        continue
                else:
                    sd = toks[0] if len(toks) == 1 else toks[0]
                dec = f"{int(sd[1])}{int(sd[0])}"
                tot += v
                if dec == msg:
                    ok += v
    return ok / tot, tot


def main():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    res = {}
    for arm, p in (("sd_clean", 0.0), ("sd_purified", 0.0),
                   ("sd_raw", 0.3), ("sd_purified", 0.3)):
        ps, n = p_success(sim, arm, p)
        res[f"{arm}@{p}"] = ps
        print(f"[ideal] {arm}@p={p}: p_success={ps:.4f} (n={n})")
    assert res["sd_clean@0.0"] > 0.995 and res["sd_purified@0.0"] > 0.995
    gain = res["sd_purified@0.3"] - res["sd_raw@0.3"]
    print(f"VALIDATOR PASS (no harm at p=0). STACK GAIN at p*=0.3: {gain:+.4f}")
    json.dump(res, open(os.path.join(HERE, "..", "results",
                                     "exp115_ideal_tier.json"), "w"), indent=1)
    print("wrote results/exp115_ideal_tier.json")


if __name__ == "__main__":
    main()
