#!/usr/bin/env python3
"""
Exp139 — Coherent entropy concentration seeded at F118's cold value (Whisper C4720,
Creator-directed "run it"). ENGINEERING ARTIFACT, honestly scoped.

WHAT THIS IS (and is NOT). Majority-vote of 3 biased qubits is CLASSICAL entropy
compression: p1(dest) = 3p^2 - 2p^3, works on ANY biased qubit, uses no coherence
(the inputs are diagonal thermal populations, the majority commutes with the
computational basis). The identical statistics come from taking the classical
majority of 3 measured qubits in post-processing. So this run does NOT extend the
ICO physics (that is F118, unchanged; the cascade floor 0.177 is ICO's real limit —
see docs/ico-cooling-floor-and-concentration-boundary-whisper-c4720.md). The ONLY
thing a hardware run adds over post-processing: a physically-produced (not
post-selected) destination qubit colder than any single input, built by a coherent
majority gate — i.e. the coherent-concentration circuit runs on silicon without the
depth eating the classically-predicted number. That is the artifact; the inputs are
prepared AT F118's measured cold population (0.21) to isolate the concentration step
rather than fly 3 live fridges (which would add 13-qubit NO-TEST risk for no new
physics). Fuel-mislocation guard (F94/C4717): the cooling here is the classical
majority, NOT the ICO resource.

CIRCUIT (4 qubits: q0,q1,q2 inputs; q3 destination). The concentration circuit is
INPUT-TEMPERATURE-INDEPENDENT: prep inputs to a basis state (b0,b1,b2) with X gates,
then dest = majority via 3 Toffolis (ccx(0,1,3) ccx(1,2,3) ccx(0,2,3) with dest|0>),
measure dest. Pooling the 8 basis circuits with weights prod(w(b_i)), w(1)=p,
realizes 3 i.i.d. inputs at population p — EXACTLY, and the SAME 8 circuits pool to
BOTH p=0.21 (cold, F118) and p=0.25 (bath) readouts. Single-input reference: 2
circuits (input |0>/|1>) pooled to p, capturing readout error with no gate depth.
Integrity sentinels are the corners of the 8: conc_000 -> dest must be 0,
conc_111 -> dest must be 1 (the majority logic + noise floor).

Theory: dest(0.21)=3(0.21^2)-2(0.21^3)=0.1138 ; dest(0.25)=0.1562 ; single=p.

Modes: --sim | --fake (both FREE).
"""
import argparse
import itertools
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

HERE = os.path.dirname(os.path.abspath(__file__))
P_COLD = 0.21          # F118 hardware cold-branch population (the seed)
P_BATH = 0.25          # bare bath, for the colder-inputs-concentrate-colder reference
SHOTS = 3000


def conc_circuit(b):
    """b = (b0,b1,b2) basis prep of the 3 inputs; dest = majority(inputs)."""
    qc = QuantumCircuit(4, 1)
    for i, bi in enumerate(b):
        if bi:
            qc.x(i)
    qc.barrier()
    qc.ccx(0, 1, 3)
    qc.ccx(1, 2, 3)
    qc.ccx(0, 2, 3)     # dest (q3, |0>) = majority(q0,q1,q2)  [3p^2-2p^3]
    qc.measure(3, 0)
    return qc


def single_circuit(b0):
    qc = QuantumCircuit(1, 1)
    if b0:
        qc.x(0)
    qc.measure(0, 0)
    return qc


def w(b, p):
    return np.prod([p if bi else 1 - p for bi in b])


def pooled(dest_pop, p):
    """dest_pop: {b: (p1, n)}. Returns (mean, se) of the p-weighted pool."""
    m, v = 0.0, 0.0
    for b, (p1, n) in dest_pop.items():
        wt = w(b, p)
        m += wt * p1
        v += (wt ** 2) * p1 * (1 - p1) / n
    return m, float(np.sqrt(v))


def run(backend, tk, shots=SHOTS, seed=None):
    labels = list(itertools.product([0, 1], repeat=3))
    dest_pop = {}
    twoq = 0
    for b in labels:
        tqc = transpile(conc_circuit(b), backend, seed_transpiler=4720, **tk)
        c = tqc  # keep for depth
        counts = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
        n = sum(counts.values())
        dest_pop[b] = (sum(v for k, v in counts.items() if k[-1] == "1") / n, n)
        twoq = max(twoq, sum(1 for i in c.data if i.operation.num_qubits == 2
                             and i.operation.name != "barrier"))
    single = {}
    for b0 in (0, 1):
        tqc = transpile(single_circuit(b0), backend, seed_transpiler=4720, **tk)
        counts = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
        n = sum(counts.values())
        single[b0] = (sum(v for k, v in counts.items() if k[-1] == "1") / n, n)
    return dest_pop, single, twoq


def single_pop(single, p):
    m = (1 - p) * single[0][0] + p * single[1][0]
    v = ((1 - p) ** 2) * single[0][0] * (1 - single[0][0]) / single[0][1] \
        + (p ** 2) * single[1][0] * (1 - single[1][0]) / single[1][1]
    return m, float(np.sqrt(v))


def report(dest_pop, single, twoq, tag):
    dc, dc_se = pooled(dest_pop, P_COLD)
    db, db_se = pooled(dest_pop, P_BATH)
    sc, sc_se = single_pop(single, P_COLD)
    th_cold = 3 * P_COLD ** 2 - 2 * P_COLD ** 3
    th_bath = 3 * P_BATH ** 2 - 2 * P_BATH ** 3
    s000 = dest_pop[(0, 0, 0)][0]
    s111 = dest_pop[(1, 1, 1)][0]
    print(f"\n=== {tag} ===")
    print(f"theory: dest(cold 0.21)={th_cold:.4f}  dest(bath 0.25)={th_bath:.4f}  single={P_COLD:.4f}")
    print(f"dest  : cold={dc:.4f}(±{dc_se:.4f})  bath={db:.4f}(±{db_se:.4f})   [routed 2q/circ {twoq}]")
    print(f"single: {sc:.4f}(±{sc_se:.4f})   sentinels: conc_000={s000:.4f}(->0)  conc_111={s111:.4f}(->1)")
    beats_single = dc + 5 * np.hypot(dc_se, sc_se) < sc
    colder_bath = dc + 5 * np.hypot(dc_se, db_se) < db
    integ = s000 < 0.05 and s111 > 0.95
    print(f"gates: [PRIMARY] concentration-colder-than-single {'PASS' if beats_single else 'FAIL'} "
          f"({sc-dc:.4f} colder) | [SECONDARY] colder-inputs-colder {'PASS' if colder_bath else 'FAIL'} "
          f"| [INTEGRITY] {'PASS' if integ else 'NO-TEST'}")
    return {"dest_cold": dc, "dest_cold_se": dc_se, "dest_bath": db, "dest_bath_se": db_se,
            "single_cold": sc, "single_cold_se": sc_se, "th_cold": th_cold, "th_bath": th_bath,
            "s000": s000, "s111": s111, "beats_single": bool(beats_single),
            "colder_bath": bool(colder_bath), "integrity": bool(integ), "twoq": twoq}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args()
    out = {}
    if args.sim:
        out["sim"] = report(*run(AerSimulator(), {"optimization_level": 1}, shots=20000, seed=4720),
                            tag="NOISELESS")
    if args.fake:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
        out["fake"] = report(*run(AerSimulator.from_backend(FakeMarrakesh()),
                                  {"optimization_level": 3}, seed=4720), tag="FakeMarrakesh")
    if out:
        path = os.path.join(HERE, "..", "results", "exp139_feasibility.json")
        json.dump(out, open(path, "w"), indent=2, default=float)
        print(f"\nwrote {os.path.abspath(path)}")
