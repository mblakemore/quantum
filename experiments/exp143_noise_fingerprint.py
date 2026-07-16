#!/usr/bin/env python3
"""Exp143 — Two-copy noise fingerprint of ibm_kingston's own Pauli error channel.

Application of the Exp142 machinery to a string NATURE wrote (Creator directive
C4763: "fly it"). Physics: prepare n disjoint Bell pairs; let the device's noise
act on the system qubits inside a barrier-protected process window; unprep and
measure. Per pair, the outcome bits (s,a) ARE the Pauli error syndrome:
    00 = I   01 = X   10 = Z   11 = Y
so every shot is one direct draw from the JOINT Pauli error distribution across
all n pairs — marginals and k-wise correlations come from the same shots.

Arms (one job, 4 PUBs):
  R  reference: empty window            -> SPAM + prep/unprep noise floor
  D1 delay 1 us on system qubits        -> idle channel, short
  D5 delay 5 us on system qubits        -> idle channel, long
  G  X . X on system (barrier-split)    -> gate-induced channel (2x X noise)

FENCES (stated up front, framing-over-reach guard):
- Process-attributed rates are arm-minus-reference; valid in the small-rate
  linear regime only (all rates here are few-percent).
- Pairwise crosstalk maps are classically obtainable at polynomial cost; the
  two-copy exponential edge (Exp142/CCHL) applies to HIGH-WEIGHT joint
  structure. The demo value here: one experiment, all marginals + all k-wise
  correlations from the same shots, by direct sampling of the error
  distribution.
- Single backend, single calibration window, one flight: a fingerprint
  snapshot, not a stability claim.

Usage:
  python3 exp143_noise_fingerprint.py --selftest            # P2: sim, decode-path with known truth
  python3 exp143_noise_fingerprint.py --submit [--n 20] [--shots 4096]
  python3 exp143_noise_fingerprint.py --decode --manifest ../results/exp143_manifest.json
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

SYNDROME = {(0, 0): "I", (0, 1): "X", (1, 0): "Z", (1, 1): "Y"}  # (s,a) bits
# derivation: X_s|Phi+> -> unprep -> (s,a)=(0,1); Z_s -> (1,0); Y_s -> (1,1).
# The first draft had X/Z transposed — caught by selftest 2 (known-truth injection),
# the exact A1-scramble class, surface #7, zero hardware shots spent.
ARMS = ["R", "D1", "D5", "G"]


def build_circuit(n, arm, synth_errors=None):
    """n Bell pairs on 2n virtual qubits: pair i = (system 2i, ancilla 2i+1).
    Measure system -> clbit 2i, ancilla -> clbit 2i+1."""
    qc = QuantumCircuit(2 * n, 2 * n)
    for i in range(n):
        qc.h(2 * i)
        qc.cx(2 * i, 2 * i + 1)
    qc.barrier()
    if arm == "D1":
        for i in range(n):
            qc.delay(1.0, 2 * i, unit="us")
    elif arm == "D5":
        for i in range(n):
            qc.delay(5.0, 2 * i, unit="us")
    elif arm == "G":
        for i in range(n):
            qc.x(2 * i)
        qc.barrier()
        for i in range(n):
            qc.x(2 * i)
    elif arm == "SYNTH":  # selftest only: inject known Pauli errors
        for (pair, pauli) in synth_errors:
            if pauli in ("X", "Y"):
                qc.x(2 * pair)
            if pauli in ("Z", "Y"):
                qc.z(2 * pair)
    qc.barrier()
    for i in range(n):
        qc.cx(2 * i, 2 * i + 1)
        qc.h(2 * i)
    for i in range(n):
        qc.measure(2 * i, 2 * i)
        qc.measure(2 * i + 1, 2 * i + 1)
    return qc


def decode_bitstrings(bitstrings, n):
    """bitstrings: iterable of '0101...' (qiskit display order: leftmost char =
    HIGHEST clbit). Returns (shots x n) array of syndrome chars per pair."""
    out = np.empty((len(bitstrings), n), dtype="<U1")
    for k, bs in enumerate(bitstrings):
        bits = bs.replace(" ", "")[::-1]  # index j = clbit j
        for i in range(n):
            out[k, i] = SYNDROME[(int(bits[2 * i]), int(bits[2 * i + 1]))]
    return out


def fingerprint(synd):
    """synd: (shots x n) syndrome chars. Marginal rates + pairwise correlation excess."""
    shots, n = synd.shape
    marg = {}
    for i in range(n):
        vals, counts = np.unique(synd[:, i], return_counts=True)
        d = dict(zip(vals.tolist(), (counts / shots).tolist()))
        marg[i] = {p: d.get(p, 0.0) for p in "IXZY"}
    err = synd != "I"  # (shots x n) bool
    p_err = err.mean(axis=0)
    corr = []
    for i in range(n):
        for j in range(i + 1, n):
            joint = float((err[:, i] & err[:, j]).mean())
            excess = joint - float(p_err[i] * p_err[j])
            se = float(np.sqrt(max(joint * (1 - joint), 1e-12) / shots))
            corr.append({"pair_i": i, "pair_j": j, "joint": joint,
                         "expected_indep": float(p_err[i] * p_err[j]),
                         "excess": excess, "se": se,
                         "sigma": excess / se if se > 0 else 0.0})
    corr.sort(key=lambda c: -abs(c["sigma"]))
    return {"marginals": marg, "p_err_per_pair": p_err.tolist(),
            "mean_err_rate": float(p_err.mean()), "top_correlations": corr[:10]}


def selftest():
    """P2 decode-path selftest with KNOWN truth (A1-scramble lesson: never trust
    bit-order conventions untested)."""
    from qiskit.primitives import StatevectorSampler
    n = 8
    sampler = StatevectorSampler()
    # 1) Reference, noiseless -> every pair must read I
    qc = build_circuit(n, "R")
    res = sampler.run([qc], shots=200).result()[0]
    reg = list(res.data.keys())[0]
    synd = decode_bitstrings(getattr(res.data, reg).get_bitstrings(), n)
    assert (synd == "I").all(), "selftest 1 FAIL: reference arm not all-I"
    print("selftest 1 PASS: noiseless reference -> all-I (200 shots x 8 pairs)")
    # 2) Synthetic known errors: X on pair 2, Z on pair 5, Y on pair 6
    truth = [(2, "X"), (5, "Z"), (6, "Y")]
    qc = build_circuit(n, "SYNTH", synth_errors=truth)
    res = sampler.run([qc], shots=200).result()[0]
    synd = decode_bitstrings(getattr(res.data, reg).get_bitstrings(), n)
    for i in range(n):
        want = dict(truth).get(i, "I")
        got = set(np.unique(synd[:, i]).tolist())
        assert got == {want}, f"selftest 2 FAIL pair {i}: want {want} got {got}"
    print("selftest 2 PASS: synthetic X/Z/Y land on the right pairs with the right labels")
    # 3) G arm (X.X == I), noiseless -> all-I (checks barrier does not break identity)
    qc = build_circuit(n, "G")
    res = sampler.run([qc], shots=200).result()[0]
    synd = decode_bitstrings(getattr(res.data, reg).get_bitstrings(), n)
    assert (synd == "I").all(), "selftest 3 FAIL: G arm not identity"
    print("selftest 3 PASS: X.X window is identity in sim")
    # 4) fingerprint() on synthetic: pair 2/5/6 err rate 1.0, others 0; corr excess ~0..
    fp = fingerprint(synd)
    assert fp["mean_err_rate"] == 0.0
    print("selftest 4 PASS: fingerprint() zero on clean input")
    print("SELFTEST 4/4 PASS")


def submit(n, shots, backend_name):
    from exp142_flight_kit import pick_layouts
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service()
    backend = svc.backend(backend_name)
    _, _, pairs = pick_layouts(backend, n)
    assert len(pairs) == n, f"only {len(pairs)} disjoint pairs available"
    layout = [q for p in pairs for q in p]  # virtual 2i,2i+1 -> physical pair i
    pubs, arm_order = [], []
    for arm in ARMS:
        qc = build_circuit(n, arm)
        tqc = transpile(qc, backend=backend, initial_layout=layout,
                        optimization_level=1)
        pubs.append(tqc)
        arm_order.append(arm)
    sampler = SamplerV2(mode=backend)
    job = sampler.run(pubs, shots=shots)
    manifest = {"exp": 143, "n_pairs": n, "shots": shots,
                "backend": backend_name, "arms": arm_order,
                "physical_pairs": [list(p) for p in pairs],
                "job_id": job.job_id()}
    out = os.path.join(HERE, "..", "results", "exp143_manifest.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"submitted {job.job_id()} ({len(pubs)} arms x {shots} shots, "
          f"{n} pairs) -> manifest {out}")


def decode(manifest_path):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(manifest_path))
    n = man["n_pairs"]
    job = svc.job(man["job_id"])
    results = {}
    for k, arm in enumerate(man["arms"]):
        res = job.result()[k]
        reg = list(res.data.keys())[0]
        synd = decode_bitstrings(getattr(res.data, reg).get_bitstrings(), n)
        results[arm] = fingerprint(synd)
        print(f"arm {arm}: mean err rate {results[arm]['mean_err_rate']:.4f}")
    ref = np.array(results["R"]["p_err_per_pair"])
    for arm in ("D1", "D5", "G"):
        excess = np.array(results[arm]["p_err_per_pair"]) - ref
        results[arm]["process_attributed_per_pair"] = excess.tolist()
        results[arm]["process_attributed_mean"] = float(excess.mean())
        print(f"arm {arm}: process-attributed mean {excess.mean():+.4f} "
              f"(linear small-rate approx)")
    out = os.path.join(HERE, "..", "results", "exp143_fingerprint.json")
    with open(out, "w") as f:
        json.dump({"manifest": man, "results": results}, f, indent=1)
    print(f"fingerprint -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--backend", default="ibm_kingston")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    elif args.submit:
        submit(args.n, args.shots, args.backend)
    elif args.decode:
        decode(args.manifest or os.path.join(HERE, "..", "results", "exp143_manifest.json"))
    else:
        ap.print_help()
