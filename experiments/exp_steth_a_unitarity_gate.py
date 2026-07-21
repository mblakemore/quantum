#!/usr/bin/env python3
"""Exp-STETH-(a) unitarity gate — measure {r, u} of the 2q Bell cycle (annex §3 flight gate).

Per the flight pre-reg (docs/exp-steth-a-flight-prereg-whisper-c4971.md, quantum@86a3658) and the
advisor's corrections (C4971):
  * The apparatus coherence is CZ-DOMINATED -> benchmark the 2-QUBIT Clifford cycle on the target
    pair (the Bell prep/measure ARE 2q Cliffords), NOT single-qubit RB (which would give a falsely
    clean pass).
  * Unitarity RB alone is NOT an angle: a pure coherent over-rotation has u~=1 regardless of
    magnitude; u is the coherent FRACTION, the magnitude comes from the infidelity. So we measure
    BOTH standard RB (-> r) AND unitarity RB (-> u), then r_coh = coherent part of the infidelity.
  * MEASURE, DO NOT DECLARE: this flight reports {r, u, r_coh}. The pass/fail gate is closed
    SEPARATELY by feeding the measured coherent error through the scout model (predicted ratio-bias
    < eps=0.02) and/or the pinned unitarity-RB paper conversion (G-1). Flying to measure is fine;
    declaring the gate passed on an unpinned/unit-mismatched angle is refused (advisor).

Target: ibm_kingston pair (141,142) — lowest live CZ error 0.00085 (matches scout kingston lambda_eff).
Co-batched (all lengths/bases one job) + drift monitor (repeat a reference length across the batch)
+ manifest committed for recoverability (Ember §3(b) discipline).

Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, json, argparse
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import random_clifford, Clifford

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PAIR = (141, 142)               # ibm_kingston, lowest live CZ error
BACKEND = "ibm_kingston"
STD_LENGTHS = [1, 2, 4, 8, 16]
UNI_LENGTHS = [1, 2, 4, 8]
N_SEEDS = 5
SHOTS = 4000
BASES = [(b0, b1) for b0 in "XYZ" for b1 in "XYZ"]   # 9 Pauli-product bases for purity


def _clifford_seq(m, rng):
    """Return (list of m 2q Clifford circuits, composed Clifford). Sequence applied c1 THEN c2 ...
    THEN cm, so the running product is comp = comp.compose(c) (self first, then c). The inverse to
    append is comp.adjoint() -> ideal returns to |00>."""
    circs, comp = [], Clifford(QuantumCircuit(2))
    for _ in range(m):
        c = random_clifford(2, seed=int(rng.integers(1 << 31)))
        circs.append(c.to_circuit())
        comp = comp.compose(c)   # apply comp first, then c
    return circs, comp


def _corr(cnt):
    """Return (<z0 z1>, <z0>, <z1>) from a 2-clbit count dict. Qiskit key = 'c1 c0' (clbit1 leftmost
    = qubit1; clbit0 rightmost = qubit0)."""
    tot = sum(cnt.values()); z0z1 = z0 = z1 = 0.0
    for key, v in cnt.items():
        k = key.replace(" ", "")
        b1 = int(k[0]); b0 = int(k[1])
        s0 = 1 - 2 * b0; s1 = 1 - 2 * b1
        z0z1 += v * s0 * s1; z0 += v * s0; z1 += v * s1
    return z0z1 / tot, z0 / tot, z1 / tot


def purity_from_bases(basis_counts):
    """2q purity = (1 + sum_{15 non-identity Paulis} <P>^2)/4 from the 9 Pauli-product bases.
    basis_counts: {'XX': counts, 'XY': counts, ...}. Two-body <b0 x b1> from each basis; the two
    one-body marginals <b0 x I>,<I x b1> are each measured in 3 bases -> averaged."""
    two = {}; m0 = {b: [] for b in "XYZ"}; m1 = {b: [] for b in "XYZ"}
    for b, cnt in basis_counts.items():
        z0z1, z0, z1 = _corr(cnt)
        two[b] = z0z1; m0[b[0]].append(z0); m1[b[1]].append(z1)
    num = sum(v * v for v in two.values())
    num += sum((sum(vs) / len(vs)) ** 2 for vs in m0.values())
    num += sum((sum(vs) / len(vs)) ** 2 for vs in m1.values())
    return (1 + num) / 4


def _basis_change(qc, q_local, pauli):
    """Rotate so a computational measurement reads <pauli> on that qubit."""
    if pauli == "X":
        qc.h(q_local)
    elif pauli == "Y":
        qc.sdg(q_local); qc.h(q_local)
    # Z: no rotation


def standard_rb_circuit(m, rng):
    """C1..Cm then the inverse; measure survival to |00> (fit -> alpha -> r)."""
    qc = QuantumCircuit(2, 2)
    circs, comp = _clifford_seq(m, rng)
    for c in circs:
        qc.compose(c, inplace=True); qc.barrier()
    qc.compose(comp.adjoint().to_circuit(), inplace=True)  # inverse -> ideal returns |00>
    qc.measure([0, 1], [0, 1])
    return qc


def unitarity_base(m, rng):
    """C1..Cm (NO inverse), NO measurement — the shared state for all 9 purity bases."""
    qc = QuantumCircuit(2, 2)
    circs, _ = _clifford_seq(m, rng)
    for c in circs:
        qc.compose(c, inplace=True); qc.barrier()
    return qc


def add_basis(base_circ, basis):
    """Append a Pauli-basis change + measure to a COPY of the shared unitarity base (so all 9 bases
    measure the SAME state — required for a valid purity)."""
    qc = base_circ.copy(); qc.barrier()
    _basis_change(qc, 0, basis[0]); _basis_change(qc, 1, basis[1])
    qc.measure([0, 1], [0, 1])
    return qc


def build_all(seed0=20260721):
    """Return (circuits, index) — index records what each circuit is, for decode."""
    rng = np.random.default_rng(seed0)
    circuits, index = [], []
    # standard RB
    for m in STD_LENGTHS:
        for s in range(N_SEEDS):
            circuits.append(standard_rb_circuit(m, rng)); index.append({"kind": "std", "m": m, "seed": s})
    # unitarity RB (9 bases share ONE sequence per (m,seed))
    for m in UNI_LENGTHS:
        for s in range(N_SEEDS):
            base = unitarity_base(m, rng)
            for b in BASES:
                circuits.append(add_basis(base, b))
                index.append({"kind": "uni", "m": m, "seed": s, "basis": "".join(b)})
    # drift monitor: repeat a full m=4 unitarity 9-basis set (fresh seeds) at 2 late batch points
    for rep in range(2):
        for s in range(N_SEEDS):
            base = unitarity_base(4, rng)
            for b in BASES:
                circuits.append(add_basis(base, b))
                index.append({"kind": "drift", "m": 4, "seed": s, "basis": "".join(b), "rep": rep})
    return circuits, index


def local_sanity():
    """Noiseless: standard survival ~1 at all m (alpha~1); unitarity purity ~1 (u~1)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    rng = np.random.default_rng(7)
    print("noiseless sanity (expect survival~1, purity~1):")
    for m in (1, 4, 16):
        qc = standard_rb_circuit(m, rng)
        r = sim.run(transpile(qc, sim), shots=2000, seed_simulator=1).result().get_counts()
        surv = sum(v for k, v in r.items() if k.replace(" ", "") == "00") / 2000
        base = unitarity_base(m, rng); bc = {}
        for b in BASES:
            uc = add_basis(base, b)
            bc["".join(b)] = sim.run(transpile(uc, sim), shots=8000, seed_simulator=2).result().get_counts()
        print(f"  m={m:2d}: survival={surv:.3f}  purity={purity_from_bases(bc):.3f}")


def submit():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service()
    backend = svc.backend(BACKEND)
    circuits, index = build_all()
    tqc = transpile(circuits, backend=backend, optimization_level=1,
                    initial_layout=list(PAIR), seed_transpiler=3211)
    depths = [c.depth() for c in tqc]
    print(f"transpiled {len(tqc)} circuits on {BACKEND} {PAIR}; max depth {max(depths)}")
    sampler = SamplerV2(mode=backend)
    job = sampler.run(tqc, shots=SHOTS)
    manifest = {"exp": "steth_a_unitarity_gate", "backend": BACKEND, "pair": list(PAIR),
                "job_id": job.job_id(), "shots": SHOTS, "index": index,
                "std_lengths": STD_LENGTHS, "uni_lengths": UNI_LENGTHS, "n_seeds": N_SEEDS,
                "note": "MEASURE {r,u} only; gate closed separately via scout-model / pinned paper"}
    out = os.path.join(QROOT, "results", "exp_steth_a_unitarity_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(tqc)} circuits, {SHOTS} shots) -> {os.path.relpath(out)}")
    return job.job_id()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sanity", action="store_true"); ap.add_argument("--submit", action="store_true")
    args = ap.parse_args()
    if args.sanity:
        local_sanity()
    elif args.submit:
        submit()
    else:
        print("use --sanity (local check) or --submit (QPU)")
