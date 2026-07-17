#!/usr/bin/env python3
"""Exp146 — Breaking the Even-Mansour cipher with Simon's algorithm on hardware
(Creator directive: "Both/And" — Rung 2, standing on Exp145's Simon win).

THE CIPHER (Even-Mansour, a real minimal block-cipher construction):
    E_{k1,k2}(x) = P(x XOR k1) XOR k2,   P a PUBLIC permutation, k1/k2 SECRET.

THE ATTACK (Kuwakado-Morii 2012, a published quantum cryptanalysis):
    define f(x) = E(x) XOR P(x) = P(x XOR k1) XOR k2 XOR P(x).
    Then f(x XOR k1) = f(x): f has PERIOD k1 (k2 cancels — irrelevant to the period).
    Simon's algorithm recovers k1 in O(n) queries; classically it costs Theta(2^{n/2}).
    => quantum KEY RECOVERY of a cipher secret.

SELF-VERIFYING (P3 intrinsic, no seals): we plant k1,k2, build E and P, run Simon,
recover k1_hat, and check k1_hat == planted_k1 AND (classically) f(x XOR k1_hat)==f(x)
for all x. The recovered key proves itself.

HONEST FENCES (C4713-16):
 - Quantum-query model: the attack needs superposition query access to the cipher's
   internals (standard caveat for this class of result; Kuwakado-Morii's own model).
 - Small n / toy P: a hardware DEMONSTRATION of a real attack, not a break of a
   deployed cipher. Two P variants: LINEAR (shallow, flies clean) proves the mechanism
   on-chip; NONLINEAR (real S-box, deeper) proves the attack is not exploiting
   linearity (sim-verified; hardware only if depth survives — else boundary quantified,
   Exp144 posture).
 - k2 is unrecoverable by this f (cancels); recovering k1 is the key-recovery claim.

Usage:
  python3 exp146_even_mansour.py --selftest         # sim: Simon recovers k1 for both P
  python3 exp146_even_mansour.py --powercalc        # measured-noise recovery vs P/n
  python3 exp146_even_mansour.py --submit --pkind linear --n 4
  python3 exp146_even_mansour.py --decode --manifest ...
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

E_CX = 0.0106
E_RO = 0.010


# ---- the public permutation P, as BOTH a circuit and a classical function -----
def P_circuit(qc, qubits, kind):
    """Apply public permutation P in place on `qubits`. Self-inverse gate set so
    P_inv = same gates reversed."""
    n = len(qubits)
    if kind == "linear":
        for i in range(n - 1):
            qc.cx(qubits[i], qubits[i + 1])          # linear mixing (invertible)
        qc.cx(qubits[n - 1], qubits[0])
    elif kind == "nonlinear":
        # 2-Toffoli S-box (n=3): the MINIMUM strength giving a clean {0,k1} period
        # for the Kuwakado-Morii attack (weaker P leaves a larger period subgroup;
        # verified by classical search, C482x). Gate order: cx01, ccx012, cx12, ccx120.
        q = qubits
        qc.cx(q[0], q[1]); qc.ccx(q[0], q[1], q[2]); qc.cx(q[1], q[2]); qc.ccx(q[1], q[2], q[0])
    else:
        raise ValueError(kind)


def P_circuit_inv(qc, qubits, kind):
    n = len(qubits)
    if kind == "linear":
        qc.cx(qubits[n - 1], qubits[0])
        for i in reversed(range(n - 1)):
            qc.cx(qubits[i], qubits[i + 1])
    elif kind == "nonlinear":
        q = qubits
        qc.ccx(q[1], q[2], q[0]); qc.cx(q[1], q[2]); qc.ccx(q[0], q[1], q[2]); qc.cx(q[0], q[1])


# clean-period keys for the 2-Toffoli P (classically verified: period-set == {0,k1})
EM_CLEAN_K1 = {(0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1)}


def P_classical(x, n, kind):
    """Classical mirror of P_circuit — for building f and truth-checking."""
    b = list(x)
    if kind == "linear":
        for i in range(n - 1):
            b[i + 1] ^= b[i]
        b[0] ^= b[n - 1]
    elif kind == "nonlinear":
        b[1] ^= b[0]
        if b[0] and b[1]: b[2] ^= 1
        b[2] ^= b[1]
        if b[1] and b[2]: b[0] ^= 1
    return b


def f_classical(x, n, kind, k1, k2):
    """f(x) = E(x) XOR P(x), E(x)=P(x XOR k1) XOR k2."""
    Px = P_classical(x, n, kind)
    xk = [x[i] ^ k1[i] for i in range(n)]
    Exk = P_classical(xk, n, kind)
    Exk = [Exk[i] ^ k2[i] for i in range(n)]
    return [Exk[i] ^ Px[i] for i in range(n)]


# ---- the Simon oracle for f = E XOR P (compute / copy / uncompute) -------------
def em_oracle(n, kind, k1, k2):
    """|x>|0>_Y|0>_W -> |x>|f(x)>_Y|0>_W. X preserved, W uncomputed."""
    X = list(range(n)); Y = list(range(n, 2 * n)); W = list(range(2 * n, 3 * n))
    qc = QuantumCircuit(3 * n)
    # term 1: Y ^= P(x)
    for i in range(n): qc.cx(X[i], W[i])          # W = x
    P_circuit(qc, W, kind)                         # W = P(x)
    for i in range(n): qc.cx(W[i], Y[i])           # Y ^= P(x)
    P_circuit_inv(qc, W, kind)                      # W = x
    for i in range(n): qc.cx(X[i], W[i])           # W = 0
    # term 2: Y ^= E(x) = P(x^k1)^k2
    for i in range(n): qc.cx(X[i], W[i])           # W = x
    for i in range(n):
        if k1[i]: qc.x(W[i])                        # W = x^k1
    P_circuit(qc, W, kind)                          # W = P(x^k1)
    for i in range(n): qc.cx(W[i], Y[i])           # Y ^= P(x^k1)
    for i in range(n):
        if k2[i]: qc.x(Y[i])                        # Y ^= k2
    P_circuit_inv(qc, W, kind)                       # W = x^k1
    for i in range(n):
        if k1[i]: qc.x(W[i])                        # W = x
    for i in range(n): qc.cx(X[i], W[i])           # W = 0
    return qc


def em_simon_circuit(n, kind, k1, k2):
    qc = QuantumCircuit(3 * n, n)
    qc.h(range(n))
    qc.barrier()
    qc.compose(em_oracle(n, kind, k1, k2), inplace=True)
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def _recover(ys, n):
    best, bs = -1, None
    for sc in itertools.product((0, 1), repeat=n):
        if not any(sc):
            continue
        sca = np.array(sc)
        score = sum(1 for y in ys if np.dot(y, sca) % 2 == 0)
        if score > best:
            best, bs = score, list(sc)
    return bs, (best / len(ys) if ys else 0)


def _sample(counts, n):
    ys = []
    for bit, c in counts.items():
        y = [int(x) for x in bit.replace(" ", "")[::-1][:n]]
        if any(y):
            ys.extend([y] * c)
    return ys


def selftest():
    from qiskit.primitives import StatevectorSampler
    sampler = StatevectorSampler(seed=146)
    rng = np.random.default_rng(1460)
    for kind in ("linear", "nonlinear"):
        for n in (3, 4):
            k1 = [0] * n
            while not any(k1):
                k1 = [int(v) for v in rng.integers(0, 2, n)]
            k2 = [int(v) for v in rng.integers(0, 2, n)]
            # classical period check FIRST (independent of the circuit)
            for x in itertools.product((0, 1), repeat=n):
                x = list(x)
                xk = [x[i] ^ k1[i] for i in range(n)]
                assert f_classical(x, n, kind, k1, k2) == f_classical(xk, n, kind, k1, k2), \
                    f"{kind} n={n}: classical f not period-k1"
            # circuit -> Simon recovers k1
            qc = em_simon_circuit(n, kind, k1, k2)
            res = sampler.run([qc], shots=400).result()[0]
            reg = list(res.data.keys())[0]
            counts = getattr(res.data, reg).get_counts()
            ys = _sample(counts, n)
            k1_hat, frac = _recover(ys, n)
            assert k1_hat == k1, f"{kind} n={n}: Simon FAILED, k1_hat={k1_hat} k1={k1} frac={frac}"
            # every noiseless y must be orthogonal to k1 (ground-truth, primitive-independent)
            assert all(np.dot([int(c) for c in b[::-1][:n]], k1) % 2 == 0 for b in counts), \
                f"{kind} n={n}: y not orthogonal to k1"
            print(f"  {kind:>9} n={n}: classical period-k1 OK | Simon recovers k1={k1} "
                  f"(orthogonality {frac:.2f}) ✓")
    print("SELFTEST PASS — both P kinds: f has period k1 AND Simon recovers it")


def _noisy_y_em(n, kind, k1, rng, n_cx):
    comp = [v for v in itertools.product((0, 1), repeat=n) if np.dot(v, k1) % 2 == 0]
    y = list(comp[rng.integers(len(comp))])
    p_flip = 1 - (1 - E_CX) ** n_cx
    for i in range(n):
        if rng.random() < p_flip / n:
            y[i] ^= 1
        if rng.random() < E_RO:
            y[i] ^= 1
    return y


def _cx_estimate(n, kind):
    from qiskit.primitives import StatevectorSampler  # noqa (import cost only)
    qc = em_oracle(n, kind, [1] * n, [0] * n)
    return sum(1 for inst in qc.data if inst.operation.name in ("cx", "ccx")) \
        + 6 * sum(1 for inst in qc.data if inst.operation.name == "ccx")


def powercalc():
    rng = np.random.default_rng(14600)
    print(f"Exp146 Gate-2 | measured E_CX={E_CX} (LOGICAL cx; routing adds overhead)")
    print(f"{'P':>10} {'n':>2} {'~cx':>4} {'reps':>5} {'P(recover k1)':>14}")
    res = {}
    for kind in ("linear", "nonlinear"):
        for n in (3, 4, 5):
            ncx = _cx_estimate(n, kind)
            reps = 12 * n
            succ, TR = 0, 300
            for _ in range(TR):
                k1 = [1] + [0] * (n - 2) + [1]
                ys = [tuple(_noisy_y_em(n, kind, k1, rng, ncx)) for _ in range(reps)]
                ys = [y for y in ys if any(y)]
                kh, _ = _recover(ys, n)
                succ += (kh == k1)
            pr = succ / TR
            res[f"{kind}_n{n}"] = {"cx": ncx, "reps": reps, "p_recover": pr}
            v = "PASS" if pr >= 0.9 else ("marg" if pr >= 0.5 else "KILL")
            print(f"{kind:>10} {n:>2} {ncx:>4} {reps:>5} {pr:>14.3f} {v}")
        print()
    json.dump(res, open(os.path.join(HERE, "..", "results", "exp146_powercalc.json"), "w"), indent=1)


def submit(pkind, n, reps, backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    rng = np.random.default_rng(1461)
    k1 = [0] * n
    while not any(k1):
        k1 = [int(v) for v in rng.integers(0, 2, n)]
    k2 = [int(v) for v in rng.integers(0, 2, n)]
    svc = _get_ibm_service()
    b = svc.backend(backend_name)
    tqc = transpile(em_simon_circuit(n, pkind, k1, k2), backend=b, optimization_level=3)
    job = SamplerV2(mode=b).run([tqc], shots=reps)
    man = {"exp": 146, "pkind": pkind, "n": n, "reps": reps, "backend": backend_name,
           "planted_k1": k1, "planted_k2": k2, "job_id": job.job_id(),
           "cz": sum(v for k, v in tqc.count_ops().items() if k in ("cz", "ecr", "cx")),
           "depth": tqc.depth()}
    out = os.path.join(HERE, "..", "results", f"exp146_manifest_{pkind}_n{n}.json")
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} EM-{pkind} n={n} (cz={man['cz']} depth={man['depth']}) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp))
    n, k1 = man["n"], man["planted_k1"]
    res = svc.job(man["job_id"]).result()[0]
    reg = list(res.data.keys())[0]
    ys = _sample(getattr(res.data, reg).get_counts(), n)
    kh, frac = _recover(ys, n)
    ok = kh == k1
    print(f"EM-{man['pkind']} n={n} (depth {man['depth']}, {man['cz']} CZ): "
          f"recovered k1_hat={kh} | planted k1={k1} | "
          f"{'KEY RECOVERED ✓' if ok else 'MISS ✗'} (orthogonality {frac:.2f})")
    json.dump({"pkind": man["pkind"], "n": n, "planted_k1": k1, "recovered_k1": kh,
               "recovered": ok, "orthogonality": round(frac, 3), "depth": man["depth"]},
              open(mp.replace("manifest", "decode"), "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--powercalc", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--pkind", default="linear", choices=["linear", "nonlinear"])
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--reps", type=int, default=96)
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.powercalc:
        powercalc()
    elif a.submit:
        submit(a.pkind, a.n, a.reps, a.backend)
    elif a.decode:
        decode(a.manifest)
    else:
        ap.print_help()
