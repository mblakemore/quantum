#!/usr/bin/env python3
"""Exp142 Gate-2: robust decoder vs FakeMarrakesh. Whisper C4746.

KILL-GATE (prereg 7.2): decoder identifies hidden full-weight Pauli P with >=99%
success at <=5x the ideal (noiseless) shot count, under FakeMarrakesh noise,
for n in {4, 8, 10}. F81/C4720 caveat: FakeMarrakesh is KNOWN-OPTIMISTIC at depth;
this circuit is depth ~3 so the model residual is small, but the flight prereg
still quotes the sim number as a PREVIEW, not a hardware floor.

Protocol (quantum arm, per shot):
  - draw random even-parity sign string b for each copy independently
  - prep product eigenstates |P_i, b_i> on qubits 0..n-1 (copy1) and n..2n-1 (copy2)
  - transversal Bell measurement: CX(i, n+i), H(i), measure all 2n
  - outcome -> Pauli Q via mapping CALIBRATED in-script from Statevector (no memory trust)

Decoder (ML enumeration — robust to arbitrary per-shot corruption):
  - candidates P' in {X,Y,Z}^n (3^n; unlimited classical compute is allowed, the
    race currency is SAMPLES)
  - score(P') = #shots with <Q_s, P'>_sp == c(ypar(P')); c() calibrated in-script
  - argmax wins. True P keeps bias 1-p_c/2 vs 1/2 for all others (commutant of P
    is a dim 2n-1 subspace; any P' not in {I,P} splits it exactly in half).
"""
import itertools
import json
import os
import sys
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

rng = np.random.default_rng(142)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- prep helpers
PAULIS = "XYZ"

def prep_gates(qc, q, pauli, sign_bit):
    """Prepare the +/- eigenstate of pauli on qubit q (sign_bit=1 -> minus)."""
    if sign_bit:
        qc.x(q)
    if pauli == "X":
        qc.h(q)
    elif pauli == "Y":
        qc.h(q)
        qc.s(q)
    # Z: computational basis, nothing more

def random_even_parity_bits(n):
    b = rng.integers(0, 2, size=n)
    if b.sum() % 2:
        b[rng.integers(0, n)] ^= 1
    return b

def shot_circuit(P, b1, b2):
    n = len(P)
    qc = QuantumCircuit(2 * n, 2 * n)
    for i in range(n):
        prep_gates(qc, i, P[i], int(b1[i]))
        prep_gates(qc, n + i, P[i], int(b2[i]))
    qc.barrier()
    for i in range(n):
        qc.cx(i, n + i)
        qc.h(i)
    qc.measure(range(2 * n), range(2 * n))
    return qc

# ------------------------------------------------- Bell-outcome->Pauli mapping
def calibrate_bell_mapping():
    """For each 1-qubit Pauli Q, prepare (Q (x) I)|Phi+>, run CX(0,1),H(0),
    read deterministic bits (m0, m1) -> mapping {(m0,m1): Q as (x,z) bits}."""
    mapping = {}
    for name, (x, z) in {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}.items():
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)          # |Phi+>
        if name == "X":
            qc.x(0)
        elif name == "Y":
            qc.y(0)
        elif name == "Z":
            qc.z(0)
        qc.cx(0, 1)
        qc.h(0)
        sv = Statevector.from_instruction(qc)
        probs = sv.probabilities_dict()
        top = max(probs, key=probs.get)
        assert probs[top] > 0.999, f"mapping not deterministic for {name}: {probs}"
        # qiskit bitstring: leftmost = qubit 1, rightmost = qubit 0
        m1, m0 = int(top[0]), int(top[1])
        mapping[(m0, m1)] = (x, z)
    assert len(mapping) == 4, "outcome collision in Bell mapping"
    return mapping

def calibrate_constraint_sign(mapping):
    """Noiseless n=2 runs for a ypar-even and a ypar-odd P: which constraint value
    do outcomes satisfy? Returns dict {0: c_even, 1: c_odd}."""
    sim = AerSimulator()
    out = {}
    for P, ypar in (("XZ", 0), ("YZ", 1), ("YY", 0), ("XY", 1)):
        n = len(P)
        vals = set()
        for _ in range(40):
            qc = shot_circuit(P, random_even_parity_bits(n), random_even_parity_bits(n))
            res = sim.run(qc, shots=1).result().get_counts()
            bits = outcome_to_bits(list(res)[0], n, mapping)
            vals.add(int(sp_inner(bits, pauli_to_bits(P), n)))
        assert len(vals) == 1, f"constraint value not constant for {P}: {vals}"
        c = vals.pop()
        if ypar in out:
            assert out[ypar] == c, f"inconsistent sign for ypar={ypar}"
        out[ypar] = c
    return out

def outcome_to_bits(bitstring, n, mapping):
    """Measured 2n-bit string -> Q as 2n-vector (x|z)."""
    s = bitstring.replace(" ", "")[::-1]  # index by qubit
    q = np.zeros(2 * n, dtype=np.int8)
    for i in range(n):
        x, z = mapping[(int(s[i]), int(s[n + i]))]
        q[i], q[n + i] = x, z
    return q

def pauli_to_bits(P):
    n = len(P)
    v = np.zeros(2 * n, dtype=np.int8)
    for i, p in enumerate(P):
        x, z = {"X": (1, 0), "Y": (1, 1), "Z": (0, 1)}[p]
        v[i], v[n + i] = x, z
    return v

def sp_inner(u, v, n):
    return int(u[:n] @ v[n:] + u[n:] @ v[:n]) % 2

# ------------------------------------------------------------------ ML decoder
def candidate_matrix(n):
    """(3^n, 2n) int8 matrix of all full-weight candidates + their ypar."""
    cands = list(itertools.product(PAULIS, repeat=n))
    M = np.zeros((len(cands), 2 * n), dtype=np.int8)
    ypar = np.zeros(len(cands), dtype=np.int8)
    for k, c in enumerate(cands):
        M[k] = pauli_to_bits("".join(c))
        ypar[k] = c.count("Y") % 2
    return cands, M, ypar

def decode_success_curve(shots_bits, true_idx, cand_M, ypar, csign, n, grid):
    """shots_bits: (m, 2n). Returns {m: success(0/1)} evaluated on prefix lengths."""
    # constraint value of each shot against each candidate:
    # <Q, P'> = Q_x . P'_z + Q_z . P'_x  (mod 2)
    swapped = np.concatenate([cand_M[:, n:], cand_M[:, :n]], axis=1)  # (C, 2n)
    vals = (shots_bits @ swapped.T) % 2                               # (m, C)
    target = np.array([csign[int(y)] for y in ypar], dtype=np.int8)   # (C,)
    agree = (vals == target[None, :]).astype(np.int32)                # (m, C)
    cum = np.cumsum(agree, axis=0)                                    # (m, C)
    out = {}
    for m in grid:
        if m > shots_bits.shape[0]:
            continue
        scores = cum[m - 1]
        best = np.flatnonzero(scores == scores.max())
        out[m] = int(len(best) == 1 and best[0] == true_idx)
    return out

# ------------------------------------------------------------------- run arms
def run_arm(n, trials, m_max, noisy, mapping, csign, backend=None):
    """Returns success-rate-vs-m dict. One hidden P per trial."""
    cands, cand_M, ypar = candidate_matrix(n)
    if noisy:
        sim = AerSimulator.from_backend(backend)
    else:
        sim = AerSimulator()
    grid = sorted(set(list(range(4, min(m_max, 40) + 1, 2)) +
                      list(range(40, m_max + 1, 10))))
    tally = {m: 0 for m in grid}
    counts_at = {m: 0 for m in grid}
    for t in range(trials):
        idx = rng.integers(0, len(cands))
        P = "".join(cands[idx])
        circs = [shot_circuit(P, random_even_parity_bits(n), random_even_parity_bits(n))
                 for _ in range(m_max)]
        tcircs = transpile(circs, sim, optimization_level=1, seed_transpiler=7)
        result = sim.run(tcircs, shots=1, memory=True).result()
        shots_bits = np.array([
            outcome_to_bits(result.get_memory(i)[0], n, mapping)
            for i in range(m_max)])
        curve = decode_success_curve(shots_bits, idx, cand_M, ypar, csign, n, grid)
        for m, s in curve.items():
            tally[m] += s
            counts_at[m] += 1
        print(f"    n={n} noisy={noisy} trial {t+1}/{trials} done", flush=True)
    return {m: tally[m] / counts_at[m] for m in grid if counts_at[m]}

def m99(curve):
    """Smallest m with success >= 0.99 sustained (this m and all larger grid m)."""
    ms = sorted(curve)
    for i, m in enumerate(ms):
        if all(curve[mm] >= 0.99 for mm in ms[i:]):
            return m
    return None

# -------------------------------------------------- conventional-arm noise probe
def conventional_noise_probe(n, backend, mapping, shots=400):
    """Measured parity retention in the TRUE basis under FakeMarrakesh (readout+1q
    noise inflates the executed 3^n baseline; quote measured, not assumed)."""
    sim = AerSimulator.from_backend(backend)
    cands = ["".join(rng.choice(list(PAULIS), size=n)) for _ in range(3)]
    rets = []
    for P in cands:
        qc = QuantumCircuit(n, n)
        b = random_even_parity_bits(n)
        for i in range(n):
            prep_gates(qc, i, P[i], int(b[i]))
        # measure in P basis: undo the basis rotation
        for i in range(n):
            if P[i] == "X":
                qc.h(i)
            elif P[i] == "Y":
                qc.sdg(i)
                qc.h(i)
        qc.measure(range(n), range(n))
        tqc = transpile(qc, sim, optimization_level=1, seed_transpiler=7)
        counts = sim.run(tqc, shots=shots).result().get_counts()
        even = sum(v for k, v in counts.items()
                   if (np.array([int(c) for c in k.replace(' ', '')]).sum() - b.sum()) % 2 == 0)
        rets.append(even / shots)
    return float(np.mean(rets))

# ------------------------------------------------------------------------ main
def main():
    print("calibrating Bell mapping from Statevector...", flush=True)
    mapping = calibrate_bell_mapping()
    print(f"  mapping: {mapping}")
    csign = calibrate_constraint_sign(mapping)
    print(f"  constraint sign by ypar: {csign}")

    # self-test: noiseless n=3 must recover P
    st = run_arm(3, trials=6, m_max=30, noisy=False, mapping=mapping, csign=csign)
    assert m99(st) is not None and m99(st) <= 20, f"SELF-TEST FAIL: {st}"
    print(f"  self-test n=3 noiseless m99={m99(st)} OK")

    backend = FakeMarrakesh()
    results = {"mapping_ok": True, "csign": {str(k): v for k, v in csign.items()},
               "per_n": {}, "kill_gate": "m99_noisy <= 5 * m99_ideal AND success>=0.99"}
    for n, trials, m_max in ((4, 30, 80), (8, 25, 140), (10, 20, 200)):
        print(f"n={n}: ideal arm...", flush=True)
        ideal = run_arm(n, trials, m_max, noisy=False, mapping=mapping, csign=csign)
        mi = m99(ideal)
        print(f"n={n}: FakeMarrakesh arm...", flush=True)
        noisy = run_arm(n, trials, m_max, noisy=True, mapping=mapping, csign=csign,
                        backend=backend)
        mn = m99(noisy)
        conv_ret = conventional_noise_probe(n, backend, mapping)
        verdict = (mn is not None and mi is not None and mn <= 5 * mi)
        results["per_n"][n] = {
            "m99_ideal": mi, "m99_noisy": mn,
            "inflation": (mn / mi) if (mn and mi) else None,
            "ideal_curve": ideal, "noisy_curve": noisy,
            "conventional_true_basis_parity_retention": conv_ret,
            "kill_gate_pass": bool(verdict),
        }
        print(f"n={n}: m99 ideal={mi} noisy={mn} "
              f"inflation={(mn/mi):.2f}x conv_retention={conv_ret:.3f} "
              f"KILL-GATE {'PASS' if verdict else 'FAIL'}"
              if (mi and mn) else f"n={n}: m99 ideal={mi} noisy={mn} — FAIL/insufficient",
              flush=True)

    out = os.path.join(HERE, "exp142_robust_decoder_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out}")
    overall = all(v["kill_gate_pass"] for v in results["per_n"].values())
    print(f"OVERALL KILL-GATE: {'PASS' if overall else 'FAIL'}")
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
