#!/usr/bin/env python3
"""exp124_zeno_sim.py — the tractor beam: Zeno pinning, sim tier
(Whisper C4657, horizons-2 Q6 — the LAST open item).

DESIGN CORRECTION OWNED AT DESIGN TIME (C4558 + commutativity-trap lineage):
the horizons-2 sketch said "pin against T1 decay" — PHYSICALLY WRONG. Markovian
exponential decay has linear short-time behavior; projective Z-measurement does
not inhibit relaxation at all (survival e^{-t/T1} at ANY cadence). Zeno freezes
COHERENT evolution. The honest tractor beam: hold |1> against a coherent full
pi-rotation by interleaved projective measurements.

Law (derived in-code): drive Rx(pi) split into N steps with a projective
measurement after each step; P(pinned) = P(every outcome = 1) = [cos^2(pi/2N)]^N
-> 1 as N grows. Unwatched (same N Rx steps, barriers, no measurements):
survival = cos^2(pi/2) = 0 EXACTLY. The no-drive arm (N measurements, no Rx)
measures per-measurement QND survival q — the nuisance, corrected per
friction-02 practice: law_corrected = [cos^2(pi/2N)]^N * q^N.

Qubit: single (q0). Arms: pinned_N (N in ladder), unwatched, nodrive_N.
clbits: N mid + 1 final."""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000
LADDER = [2, 4, 8, 16]


def build(arm, n):
    """arm: pinned | unwatched | nodrive. n = cadence (steps)."""
    qc = QuantumCircuit(1, n + 1)
    qc.x(0)
    for i in range(n):
        if arm != "nodrive":
            qc.rx(np.pi / n, 0)
        qc.barrier()
        if arm != "unwatched":
            qc.measure(0, i)
        qc.barrier()
    qc.measure(0, n)
    return qc


def law(n):
    return float(np.cos(np.pi / (2 * n)) ** (2 * n))


def stats(counts, arm, n):
    """pinned/nodrive: P(all n+1 outcomes = 1). unwatched: P(final = 1)."""
    tot = hit = 0
    for k, v in counts.items():
        tot += v
        if arm == "unwatched":
            ok = k[0] == "1"                 # final clbit only
        else:
            ok = all(c == "1" for c in k)    # every projection stayed |1>
        if ok:
            hit += v
    p = hit / tot
    return p, float(np.sqrt(max(p * (1 - p), 1e-9) / tot))


def main():
    print("LAW (in-code):", {n: round(law(n), 4) for n in LADDER},
          "| unwatched theory: 0.0")
    out = {"law": {str(n): law(n) for n in LADDER}}
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        res = {}
        for arm, ns in (("pinned", LADDER), ("unwatched", [8]),
                        ("nodrive", LADDER)):
            for n in ns:
                qc = build(arm, n)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4657,
                                initial_layout=[0]
                                if label != "noiseless" else None)
                cts = backend.run(tqc, shots=SHOTS).result().get_counts()
                p, se = stats(cts, arm, n)
                res[f"{arm}_{n}"] = [p, se]
        out[label] = res
        print(f"[{label}]", json.dumps(res, default=float))
    # noiseless cross-check of the in-code law
    ok = all(abs(out["noiseless"][f"pinned_{n}"][0] - law(n)) < 0.02
             for n in LADDER)
    out["law_check_pass"] = ok
    print("LAW CHECK vs noiseless sampling:", "PASS" if ok else "FAIL")
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp124_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp124_feasibility.json")


if __name__ == "__main__":
    main()
