#!/usr/bin/env python3
"""exp128_qrac_sim.py — THE POCKET DICTIONARY: 2->1 quantum random access
code, sim tier (Whisper C4667, follow-on to F106; Creator directive: run the
next measurable advantage).

THE PROTOCOL (Ambainis-Nayak-Ta-Shma-Vazirani QRAC, textbook): Alice holds two
bits (x0,x1) and may send Bob ONE qubit (or classically: one bit). The referee
then asks Bob for bit b, chosen uniformly. CLASSICAL CEILING: 0.75 exactly —
VERIFIED IN-CODE below by exhaustive enumeration over all 256 deterministic
strategy pairs (16 encodings x 4x4 decodings; shared randomness is convex).
QUANTUM: encode on the X-Z great circle, Bloch vector
r = ((-1)^x1, 0, (-1)^x0)/sqrt(2); decode x0 by measuring Z, x1 by measuring
X. Every one of the 8 (message, query) cases succeeds at cos^2(pi/8) = 0.8536
— which is ALSO the quantum optimum for this protocol, so the measured value
must land in the band (0.75, 0.8536]: above the classical law, below the
quantum law. Zero two-qubit gates.

Prep from |0>: Ry(theta), theta = pi/4 (00), -pi/4 (01), 3pi/4 (10),
-3pi/4 (11)  [Ry(theta)|0> has Bloch (sin theta, 0, cos theta)].
Decode: b=0 -> measure Z, guess = outcome; b=1 -> H then measure, guess =
outcome. Classical reference arm: optimal classical strategy executed (send
x0 as a basis state; query-0 leg measured on hardware, query-1 leg = 0.5
EXACTLY by construction under uniform messages — documented, not measured).
"""
import itertools
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000
Q_OPT = float(np.cos(np.pi / 8) ** 2)
THETA = {(0, 0): np.pi / 4, (0, 1): -np.pi / 4,
         (1, 0): 3 * np.pi / 4, (1, 1): -3 * np.pi / 4}


def classical_bound():
    """Exhaustive: encodings e:{0,1}^2->{0,1} (16), decodings d_b:{0,1}->{0,1}
    (4 per query). Uniform over 8 (message, query) cases."""
    msgs = list(itertools.product([0, 1], repeat=2))
    encs = list(itertools.product([0, 1], repeat=4))          # e[msg_index]
    decs = list(itertools.product([0, 1], repeat=2))          # d[received bit]
    best, n = 0.0, 0
    for e in encs:
        for d0 in decs:
            for d1 in decs:
                wins = 0
                for i, (x0, x1) in enumerate(msgs):
                    bit = e[i]
                    wins += (d0[bit] == x0) + (d1[bit] == x1)
                best = max(best, wins / 8.0)
                n += 1
    return best, n


def build(x0, x1, query):
    qc = QuantumCircuit(1, 1)
    qc.ry(THETA[(x0, x1)], 0)
    qc.barrier()
    if query == 1:
        qc.h(0)
    qc.measure(0, 0)
    return qc


def build_classical(x0):
    qc = QuantumCircuit(1, 1)
    if x0:
        qc.x(0)
    qc.measure(0, 0)
    return qc


def grade(counts, target):
    tot = sum(counts.values())
    hit = sum(v for k, v in counts.items() if int(k) == target)
    p = hit / tot
    return p, float(np.sqrt(max(p * (1 - p), 1e-9) / tot))


def main():
    bound, n = classical_bound()
    ok = abs(bound - 0.75) < 1e-12
    print(f"CLASSICAL BOUND (enumerated, {n} strategy pairs): {bound} "
          f"-> {'PASS' if ok else 'FAIL'} | quantum optimum {Q_OPT:.6f}")
    if not ok:
        return 1
    out = {"classical_bound": bound, "quantum_optimum": Q_OPT}
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()))):
        res, ps = {}, []
        for (x0, x1) in THETA:
            for q in (0, 1):
                qc = build(x0, x1, q)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4667)
                cts = backend.run(tqc, shots=SHOTS).result().get_counts()
                p, se = grade(cts, (x0, x1)[q])
                res[f"main_{x0}{x1}_q{q}"] = [p, se]
                ps.append(p)
        res["main_pooled"] = float(np.mean(ps))
        res["main_min"] = float(np.min(ps))
        # classical reference: q0 leg measured, q1 leg = 0.5 exact
        cps = []
        for x0 in (0, 1):
            qc = build_classical(x0)
            tqc = transpile(qc, backend, optimization_level=1,
                            seed_transpiler=4667)
            cts = backend.run(tqc, shots=SHOTS).result().get_counts()
            p, se = grade(cts, x0)
            res[f"class_{x0}_q0"] = [p, se]
            cps.append(p)
        res["class_pooled"] = float((np.mean(cps) + 0.5) / 2)
        out[label] = res
        print(f"[{label}] pooled={res['main_pooled']:.4f} "
              f"min={res['main_min']:.4f} class={res['class_pooled']:.4f}")
    nl = out["noiseless"]
    ok2 = abs(nl["main_pooled"] - Q_OPT) < 0.01
    print("NOISELESS = QUANTUM OPTIMUM CHECK:", "PASS" if ok2 else "FAIL")
    out["design_valid"] = bool(ok and ok2)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp128_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp128_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
