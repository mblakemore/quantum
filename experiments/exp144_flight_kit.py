#!/usr/bin/env python3
"""Exp144 FLIGHT KIT (freeze candidate — sha256 recorded at freeze).

Blind-protocol shape (Exp142 lineage): the V = e^{-iHt} gadget depends on the hidden
instance, so EMBER builds/submits from the secret file. The manifest this script
emits is INSTANCE-INDEPENDENT (PUB layout, shots, layouts only). Decoders consume
outcome bitstrings + manifest, never circuit definitions.

Quantum arm per (n, k) instance — ONE co-batched SamplerV2 job:
  [sentinel_start (2q Bell, 400 shots),
   quantum PUB: n Bell pairs + V on system half + transversal Bell measure,
                FIXED circuit (no per-shot rows), shots = N_BELL_BUDGET[n],
   sentinel_end (2q Bell, 400 shots)]
Sign-block wave (AFTER decoders publish accepted support — support is public then):
   per accepted term: iQP-eigenstate prep + V + Q letter-basis measure, N_SIGN shots.
Conventional arm: candidate-sweep PUBs (§4): iQP'-eigenstate prep + V + Q measure,
   SPRT-metered by the decode side; wave-batched like Exp142 §4.

FULL-WEIGHT STRUCTURE = SECRET-INDEPENDENT CIRCUIT SHAPE: every term's rotation
gadget spans all n system qubits (basis-change layer + CNOT ladder + Rz + reverse),
so the transpiled STRUCTURE leaks nothing; the secret enters only via u/rz ANGLES.

Modes:
  --selftest       G2.1 LAW CHECK: StatevectorSampler through the REAL pub path
                   (C4747 A1 lesson) -> exp144_decode_meter.decode -> recover a
                   known instance end-to-end. FREE, no backend.
  --scan --n 8     transpile-free structure + duration estimate (fingerprint arm input)
"""
import argparse
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

from exp144_decode_meter import shots_to_labels, decode, T_FROZEN

NS = (4, 6, 8)
KS = (1, 2, 3, 4, 5)
M = 3
N_BELL_BUDGET = {4: 5000, 6: 5000, 8: 5000}   # 5 x m_bell, FROZEN C6508
N_SIGN = 100                                   # per accepted term, per instance
SENT_SHOTS = 400
COEFF_GRID = (0.15, 0.20, 0.25)

# basis-change angles: rotate letter-basis -> Z basis (u(theta,phi,lam)), and back
TO_Z = {"X": (math.pi / 2, 0.0, math.pi), "Y": (math.pi / 2, 0.0, math.pi / 2),
        "Z": (0.0, 0.0, 0.0)}
FROM_Z = {"X": (math.pi / 2, 0.0, math.pi),                       # H self-inverse
          "Y": (math.pi / 2, math.pi / 2, math.pi),               # S H = u(pi/2,pi/2,pi)
          "Z": (0.0, 0.0, 0.0)}


def rotation_block(qc, qubits, letters, angle):
    """exp(-i angle/2 * P) on `qubits` with letter string `letters` (full weight):
    basis change to Z^n, CNOT ladder, RZ(angle) on last, un-ladder, un-change."""
    for q, c in zip(qubits, letters):
        t, p, l = TO_Z[c]
        qc.u(t, p, l, q)
    for a, b in zip(qubits[:-1], qubits[1:]):
        qc.cx(a, b)
    qc.rz(angle, qubits[-1])
    for a, b in reversed(list(zip(qubits[:-1], qubits[1:]))):
        qc.cx(a, b)
    for q, c in zip(qubits, letters):
        t, p, l = FROM_Z[c]
        qc.u(t, p, l, q)


def quantum_circuit(n, terms, thetas):
    """n Bell pairs (sys i, ref n+i); V = prod_j exp(-i theta_j P_j) on sys half;
    transversal Bell measure. theta_j = c_j * t."""
    qc = QuantumCircuit(2 * n, 2 * n)
    for i in range(n):
        qc.h(i); qc.cx(i, n + i)
    qc.barrier()
    for lab, th in zip(terms, thetas):
        rotation_block(qc, list(range(n)), lab, 2 * th)   # exp(-i th P): RZ(2*th)
    qc.barrier()
    for i in range(n):
        qc.cx(i, n + i); qc.h(i)
    qc.measure(range(2 * n), range(2 * n))
    return qc


def signblock_circuit(n, terms, thetas, target_idx, probe, prep_letters, prep_signs):
    """Single-copy: prep product eigenstate of iQP (letters+signs precomputed by
    the decode side), apply V, measure probe Q in its letter basis."""
    qc = QuantumCircuit(n, n)
    PREP = {("Z", 0): (0.0, 0.0), ("Z", 1): (math.pi, 0.0),
            ("X", 0): (math.pi / 2, 0.0), ("X", 1): (math.pi / 2, math.pi),
            ("Y", 0): (math.pi / 2, math.pi / 2), ("Y", 1): (math.pi / 2, -math.pi / 2)}
    for i, (c, s) in enumerate(zip(prep_letters, prep_signs)):
        if c == "I":
            continue
        t, p = PREP[(c, s)]
        qc.u(t, p, 0.0, i)
    qc.barrier()
    for lab, th in zip(terms, thetas):
        rotation_block(qc, list(range(n)), lab, 2 * th)
    qc.barrier()
    for i, c in enumerate(probe):
        if c != "I":
            t, p, l = TO_Z[c]
            qc.u(t, p, l, i)
    qc.measure(range(n), range(n))
    return qc


def sentinel_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def build_quantum_job(n, terms, coeffs, t=T_FROZEN):
    """(pubs, manifest) for one instance's quantum-arm job. Manifest is
    instance-independent: layout + shots only."""
    thetas = [c * t for c in coeffs]
    pubs = [(sentinel_circuit(), None, SENT_SHOTS),
            (quantum_circuit(n, terms, thetas), None, N_BELL_BUDGET[n]),
            (sentinel_circuit(), None, SENT_SHOTS)]
    manifest = {"n": n, "arm": "quantum",
                "pubs": [{"kind": "sentinel_start", "shots": SENT_SHOTS},
                         {"kind": "bell", "shots": N_BELL_BUDGET[n]},
                         {"kind": "sentinel_end", "shots": SENT_SHOTS}]}
    return pubs, manifest


def duration_estimate(n, backend_1q_ns=32, backend_2q_ns=68, ro_ns=1500):
    """Gate-count duration estimate for the fingerprint-arm selection (§8):
    per term: 2n u + 2(n-1) cx + 1 rz(virtual); 3 terms; + Bell prep/measure."""
    oneq = 2 * n * M + 2 * n + 2 * n        # basis changes + bell prep/meas H's
    twoq = 2 * (n - 1) * M + 2 * n          # ladders + bell prep/meas CXs
    ns = oneq * backend_1q_ns + twoq * backend_2q_ns + ro_ns
    return {"n": n, "1q": oneq, "2q": twoq, "est_us": round(ns / 1000, 2)}


# ------------------------------------------------------------------- selftest
def selftest():
    """G2.1: the REAL pub path (StatevectorSampler coerces pubs exactly like
    runtime SamplerV2) -> real decode_meter -> known instance recovered."""
    from qiskit.primitives import StatevectorSampler
    rng = np.random.default_rng(20260717)
    ok_all = True
    # known commuting mult-independent full-weight instance at n=4
    cases = [(4, ["XXXX", "XXYY", "XXZZ"], [0.15, -0.20, 0.25]),
             (4, ["YYYY", "YYXX", "YYZZ"], [-0.25, 0.15, 0.20])]
    sampler = StatevectorSampler(seed=7)
    for n, terms, coeffs in cases:
        thetas = [c * T_FROZEN for c in coeffs]
        pubs, _ = build_quantum_job(n, terms, coeffs)
        job = sampler.run(pubs, shots=None)
        res = job.result()
        bell = res[1].data.c.get_bitstrings() if hasattr(res[1].data, "c") else \
            res[1].data.meas.get_bitstrings()
        labels = shots_to_labels(bell, n)
        dec = decode(labels, n, len(bell))
        want = sorted(terms)
        got = sorted(dec["support"])
        sup_ok = got == want
        mag_ok = sup_ok and all(
            abs(dec["abs_coeffs"][lab] - abs(c)) <= 0.03
            for lab, c in zip(terms, coeffs))
        grp_ok = dec["off_group_mass"] < 0.005
        cons_ok = all(c["ok"] for c in dec["consistency"])
        ok = sup_ok and mag_ok and grp_ok and cons_ok
        ok_all &= ok
        print(f"  n={n} {terms} c={coeffs}: support {'OK' if sup_ok else got} "
              f"| |c| max err {max(abs(dec['abs_coeffs'][l] - abs(c)) for l, c in zip(terms, coeffs)) if sup_ok else float('nan'):.4f} "
              f"| off-group {dec['off_group_mass']:.4f} | consistency "
              f"{'OK' if cons_ok else 'FAIL'} -> {'PASS' if ok else 'FAIL'}")
    # sign block law: planted term readout = -sin(2 theta) via the REAL circuit
    n, terms, coeffs = cases[0]
    thetas = [c * T_FROZEN for c in coeffs]
    # probe for term 0 (XXXX): anticommute with it, commute with XXYY, XXZZ.
    # ZZII: vs XXXX 2 anti (even->commute) — need odd. YXII: vs XXXX qubit0 anti
    # -> 1 anti (odd, anticommutes); vs XXYY qubit0 anti only -> anticommutes. Bad.
    # Use ZYZY: vs XXXX 4 anti (comm). Systematic search instead:
    def commutes(a, b):
        return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0
    probe = next("".join(p) for p in itertools.product("IXYZ", repeat=n)
                 if set(p) != {"I"}
                 and not commutes("".join(p), terms[0])
                 and all(commutes("".join(p), tt) for tt in terms[1:]))
    # prep letters/signs for +1 eigenstate of iQP computed via matrix (selftest only)
    import functools
    I2 = np.eye(2, dtype=complex)
    PM = {"I": I2, "X": np.array([[0, 1], [1, 0]], complex),
          "Y": np.array([[0, -1j], [1j, 0]], complex),
          "Z": np.array([[1, 0], [0, -1]], complex)}
    kron = lambda s: functools.reduce(np.kron, [PM[c] for c in s])
    R = 1j * kron(probe) @ kron(terms[0])
    Slab, coef = None, None
    for p in itertools.product("IXYZ", repeat=n):
        s = "".join(p)
        tr = np.trace(kron(s).conj().T @ R) / 2 ** n
        if abs(abs(tr) - 1) < 1e-9:
            Slab, coef = s, float(np.real(tr)); break
    signs = [0] * n
    if coef < 0:
        signs[next(i for i, c in enumerate(Slab) if c != "I")] = 1
    qc = signblock_circuit(n, terms, thetas, 0, probe, Slab, signs)
    res = sampler.run([(qc, None, 20000)]).result()
    bits = res[0].data.c.get_bitstrings() if hasattr(res[0].data, "c") else \
        res[0].data.meas.get_bitstrings()
    vals = []
    for s in bits:
        b = s[::-1]
        v = 1
        for i, c in enumerate(probe):
            if c != "I":
                v *= (1 - 2 * int(b[i]))
        vals.append(v)
    got = float(np.mean(vals))
    want = -math.sin(2 * thetas[0])
    sign_ok = abs(got - want) < 0.02
    ok_all &= sign_ok
    print(f"  sign block (term XXXX, probe {probe}, prep {Slab}): <Q(t)> = {got:+.4f} "
          f"vs -sin(2th) = {want:+.4f} -> {'PASS' if sign_ok else 'FAIL'}")
    print("SELFTEST (G2.1 law check, REAL pub path):", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--n", type=int, default=8)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.scan:
        for n in NS:
            d = duration_estimate(n)
            print(f"n={n}: ~{d['1q']} 1q + {d['2q']} 2q gates, "
                  f"est duration ~{d['est_us']} us (fingerprint-arm input, §8)")
        return 0
    print("submit modes are EMBER's (sealed-committer); this kit ships build+selftest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
