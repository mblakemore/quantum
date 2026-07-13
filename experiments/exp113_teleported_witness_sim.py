#!/usr/bin/env python3
"""exp113_teleported_witness_sim.py — 'beam the arrow of time', sim tier
(Whisper C4602, horizons P1). Does causal indefiniteness survive teleportation?

Protocol: run the switch witness (F75/F82 apparatus — commuting (X,X) vs
anticommuting (X,Z) pairs, DISC = <X_c>_comm − <X_c>_anti), but TELEPORT the
control qubit one hop (F91 machinery) before its X-basis readout.
Arms:
  direct      : witness as in F75 (baseline, same window)
  tele_frame  : control teleported, frame-tracked (X-readout correction derived
                numerically: Z-frame bit flips the X outcome; the noiseless
                validator PROVES the correction rule rather than trusting it)
  tele_active : control teleported, if_test corrections (F91 losing-but-honest arm)
  tele_deco   : teleported control with dephased Bell resource (null: indefiniteness
                should NOT survive a classical channel — DISC collapses)
Noiseless validator (R5 discipline, adopted C4602): every arm's DISC must equal
the direct arm's ideal to statistical tolerance, EXCEPT tele_deco -> 0.
This file's simulated counts are ALSO the grader's selftest fixture (R5).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile  # noqa: E402
from exp105_causal_game_feasibility import apply_ctrl_unitary  # noqa: E402

SHOTS = 4000
PAIRS = {"comm": ("X", "X"), "anti": ("X", "Z")}


def witness_core(qc, a, b):
    """Exp106-style 4-slot switch of (a,b) on qubits (0=C, 1=T)."""
    qc.h(0)
    apply_ctrl_unitary(qc, a, 0, 1, 0, pad_identity=True)
    apply_ctrl_unitary(qc, b, 0, 1, 1, pad_identity=True)
    qc.barrier()
    apply_ctrl_unitary(qc, b, 0, 1, 0, pad_identity=False)
    apply_ctrl_unitary(qc, a, 0, 1, 1, pad_identity=False)
    qc.barrier()


def build(pair, arm):
    a, b = PAIRS[pair]
    if arm == "direct":
        qc = QuantumCircuit(2, 1)
        witness_core(qc, a, b)
        qc.h(0)
        qc.measure(0, 0)
        return qc
    # teleported arms: qubits 0=C, 1=T, 2=bell_a, 3=bell_b(C')
    qr = QuantumRegister(4)
    st = ClassicalRegister(2, "st")
    out = ClassicalRegister(1, "xc")
    qc = QuantumCircuit(qr, st, out)
    witness_core(qc, a, b)
    # Bell resource
    qc.h(2)
    qc.cx(2, 3)
    if arm == "tele_deco":
        # classical channel null: dephase the Bell resource pre-use
        qc.barrier()
        qc.reset(2) if False else None
        # dephasing via measure-and-forget is post-selection-free: measure Z on 2
        # into the st register's spare slot is NOT spare; use explicit Z-basis
        # collapse: measure then continue (mid-circuit measurement dephases)
        qc.measure(2, st[0])
    # Bell measurement of (C, bell_a)
    qc.cx(0, 2)
    qc.h(0)
    qc.measure(0, st[0]) if arm != "tele_deco" else qc.measure(0, st[1])
    if arm != "tele_deco":
        qc.measure(2, st[1])
    if arm == "tele_active":
        with qc.if_test((st[1], 1)):
            qc.x(3)
        with qc.if_test((st[0], 1)):
            qc.z(3)
    # X-basis readout of the teleported control C' = qubit 3
    qc.h(3)
    qc.measure(3, out[0])
    return qc


def x_exp(pub_or_counts, arm):
    """<X_c'> with frame correction for tele_frame (rule PROVEN by validator):
    X-basis outcome flips with the Z-frame bit (st[0])."""
    if arm in ("direct",):
        c = pub_or_counts
        n = sum(c.values())
        return (c.get("0", 0) - c.get("1", 0)) / n
    xc = pub_or_counts["xc"]
    stb = pub_or_counts["st"]
    tot, n = 0, 0
    for x, s in zip(xc, stb):
        v = 1 if x == "0" else -1
        if arm == "tele_frame":
            if s[1] == "1":     # st[0] = phase bit -> flips X outcome
                v = -v
        n += 1
        tot += v
    return tot / n


def run_arm(backend, pair, arm):
    qc = build(pair, arm)
    tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=4602)
    job = backend.run(tqc, shots=SHOTS)
    res = job.result()
    if arm == "direct":
        return x_exp(res.get_counts(), arm)
    # need per-shot register alignment: memory=True path via counts is lossy;
    # use joint counts split by register (Aer counts keys 'xc st')
    counts = res.get_counts()
    xc, stb = [], []
    for key, v in counts.items():
        toks = key.split()
        for _ in range(int(v)):
            xc.append(toks[0])
            stb.append(toks[1])
    return x_exp({"xc": xc, "st": stb}, arm)


def main():
    from qiskit_aer import AerSimulator
    out = {}
    for label, backend in (("noiseless", AerSimulator()),):
        out[label] = {}
        for arm in ("direct", "tele_frame", "tele_active", "tele_deco"):
            d = {p: run_arm(backend, p, arm) for p in PAIRS}
            disc = d["comm"] - d["anti"]
            out[label][arm] = {"x_comm": d["comm"], "x_anti": d["anti"],
                               "DISC": disc}
            print(f"[{label}] {arm:12s} <X>c={d['comm']:+.4f} <X>a={d['anti']:+.4f} "
                  f"DISC={disc:+.4f}")
    ideal = out["noiseless"]["direct"]["DISC"]
    tol = 5 * 2 * np.sqrt(1 / SHOTS)
    assert abs(out["noiseless"]["tele_frame"]["DISC"] - ideal) < tol, "frame rule wrong"
    assert abs(out["noiseless"]["tele_active"]["DISC"] - ideal) < tol, "active wiring wrong"
    assert abs(out["noiseless"]["tele_deco"]["DISC"]) < tol, "deco null not null"
    print(f"VALIDATOR PASS: indefiniteness survives ideal teleportation "
          f"(DISC {ideal:+.4f} preserved), dies over the classical channel (0)")
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out["fakemarrakesh"] = {}
    noisy = AerSimulator.from_backend(FakeMarrakesh())
    for arm in ("direct", "tele_frame", "tele_active", "tele_deco"):
        d = {p: run_arm(noisy, p, arm) for p in PAIRS}
        out["fakemarrakesh"][arm] = {"x_comm": d["comm"], "x_anti": d["anti"],
                                     "DISC": d["comm"] - d["anti"]}
        print(f"[fake] {arm:12s} DISC={d['comm']-d['anti']:+.4f}")
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp113_feasibility.json"), "w"), indent=1)
    print("wrote results/exp113_feasibility.json")


if __name__ == "__main__":
    main()
