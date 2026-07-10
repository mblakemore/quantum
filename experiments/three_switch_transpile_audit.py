#!/usr/bin/env python3
"""
3-SWITCH TRANSPILE AUDIT (Whisper C4531, roadmap T1.2 gateway — FREE, no QPU).

Question: does an N=3 quantum switch fit our depth budget, and does its payoff
survive the transpiled depth on Heron heavy-hex?

Constructions audited:
  A. CYCLIC 3-switch — control qutrit in 2 qubits, superposition of the 3 cyclic
     orders (ABC/BCA/CAB); slot t applies op_{(t+k)%3} controlled on control==k.
     Per (slot,k): CC-U = locals + CCZ (heavy-hex has NO triangles -> routed cost).
     9 CC-U total + control prep/unprep (state (|00>+|01>+|10>)/sqrt3).
  B. FULL 6-order switch — 3-qubit control encoding k=0..5, 18 CCC-U. Expected
     to blow the budget; audited for the record.

Payoff probe (construction A): capacity activation with THREE completely
depolarizing channels in cyclic-order superposition (cf. arXiv:2004.14339 — exact
target derived here BY SIMULATION, literature cross-check deferred to pre-reg).
64 Pauli triples pooled = exact 3-channel twirl; inputs |0>/|1>; control read in
the prep basis (inverse-prep + computational), target in Z; discriminator
D3 := (<Z_t>_{b0} - <Z_t>_{b1})/2 conditioned on control outcome, and empirical
MI(B; C,T). Causal value: EXACTLY 0 (any causal composition of three full
depolarizers is fully depolarizing).

Depth-stratified noise-model trust (C4530): FakeMarrakesh is reliably predictive
at the 4-CZ class and 400x wrong at 124 CZ (F81). The audited 3-switch lands
in between -> the FakeMarrakesh number here is a PLANNING input, not a promise;
any pre-reg must carry window-sentinel gating (Bridge 2).
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2)
PAULIS = {"1": I2, "X": X, "Y": Y, "Z": Z}
EIG = {"X": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),   # X = H Z H
       "Y": np.array([[1, 1], [1j, -1j]], dtype=complex) / np.sqrt(2),
       "Z": I2}
THETA3 = 2 * np.arcsin(1 / np.sqrt(3))  # for (|00>+|01>+|10>)/sqrt3 prep


def prep_qutrit(qc, c1, c0, inverse=False):
    """(|00>+|01>+|10>)/sqrt3 on (c1,c0): Ry(theta) on c1, then H on c0 iff c1==0.
    Explicit gates (StatePreparation.inverse() core-dumps qiskit-aer in this env)."""
    if not inverse:
        qc.ry(THETA3, c1)
        qc.x(c1)
        qc.ch(c1, c0)
        qc.x(c1)
    else:
        qc.x(c1)
        qc.ch(c1, c0)
        qc.x(c1)
        qc.ry(-THETA3, c1)


def cc_u(qc, name, c1, c0, tgt, kbits):
    """CC-U on control state |kbits> (b1,b0), U = V Z Vdag; identity -> skip."""
    if name == "1":
        return
    b1, b0 = kbits
    if b1 == 0:
        qc.x(c1)
    if b0 == 0:
        qc.x(c0)
    # native locals only (raw unitary gates trigger a transpiler panic in this env):
    # X = H Z H (V=H);  Y = (SH) Z (SH)^dag (V=SH);  Z bare
    if name == "X":
        qc.h(tgt)
    elif name == "Y":
        qc.sdg(tgt)
        qc.h(tgt)
    qc.ccz(c1, c0, tgt)
    if name == "X":
        qc.h(tgt)
    elif name == "Y":
        qc.h(tgt)
        qc.s(tgt)
    if b0 == 0:
        qc.x(c0)
    if b1 == 0:
        qc.x(c1)


def cyclic3_circuit(ops, input_bit, definite=False):
    """q0,q1 = control (c1,c0), q2 = target. clbit0/1 = control pair, clbit2 = target Z."""
    qc = QuantumCircuit(3, 3)
    if input_bit == 1:
        qc.x(2)
    if not definite:
        prep_qutrit(qc, 0, 1)
        kmap = {0: (0, 0), 1: (0, 1), 2: (1, 0)}
        for t in range(3):
            for k in range(3):
                cc_u(qc, ops[(t + k) % 3], 0, 1, 2, kmap[k])
            qc.barrier()
        prep_qutrit(qc, 0, 1, inverse=True)
    else:
        for t in range(3):
            if ops[t] == "X":
                qc.x(2)
            elif ops[t] == "Y":
                qc.y(2)
            elif ops[t] == "Z":
                qc.z(2)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.measure(2, 2)
    return qc


def full6_circuit(ops):
    """Full 6-order switch, 3-qubit binary control (k=0..5), representative cost only."""
    from qiskit.circuit.library import ZGate
    orders = list(itertools.permutations(range(3)))
    qc = QuantumCircuit(4, 1)
    for q in (0, 1, 2):
        qc.h(q)  # stand-in prep of 6-state superposition (audit = cost, not semantics)
    for t in range(3):
        for k, sigma in enumerate(orders):
            name = ops[sigma[t]]
            if name == "1":
                continue
            bits = [(k >> 2) & 1, (k >> 1) & 1, k & 1]
            for q, b in enumerate(bits):
                if b == 0:
                    qc.x(q)
            if name == "X":
                qc.h(3)
            elif name == "Y":
                qc.sdg(3)
                qc.h(3)
            qc.append(ZGate().control(3), [0, 1, 2, 3])
            if name == "X":
                qc.h(3)
            elif name == "Y":
                qc.h(3)
                qc.s(3)
            for q, b in enumerate(bits):
                if b == 0:
                    qc.x(q)
    qc.measure(3, 0)
    return qc


def count2q(tqc):
    return sum(1 for inst in tqc.data
               if inst.operation.num_qubits == 2 and inst.operation.name != "barrier")


def cost_table():
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh, FakeFez
    rows = []
    for backname, back in (("FakeMarrakesh", FakeMarrakesh()), ("FakeFez", FakeFez())):
        for opt in (1, 3):
            qc = cyclic3_circuit(("X", "Y", "Z"), 0)
            t = transpile(qc, back, seed_transpiler=4531, optimization_level=opt)
            rows.append({"construction": "cyclic3", "backend": backname, "opt": opt,
                         "twoq": count2q(t), "depth": t.depth()})
            q6 = full6_circuit(("X", "Y", "Z"))
            t6 = transpile(q6, back, seed_transpiler=4531, optimization_level=opt)
            rows.append({"construction": "full6", "backend": backname, "opt": opt,
                         "twoq": count2q(t6), "depth": t6.depth()})
    return rows


def payoff(backend, shots=1000, noiseless=False):
    """Pool 64 Pauli triples x 2 inputs; return discriminator + MI for switch and null."""
    res = {}
    for kind in ("switch", "null"):
        pools = {0: {}, 1: {}}
        for ops in itertools.product("1XYZ", repeat=3):
            for bit in (0, 1):
                qc = cyclic3_circuit(ops, bit, definite=(kind == "null"))
                t = transpile(qc, backend, seed_transpiler=4531, optimization_level=1)
                c = backend.run(t, shots=shots, seed_simulator=4531).result().get_counts()
                for k, v in c.items():
                    pools[bit][k] = pools[bit].get(k, 0) + v
        # keys 'tqc1c0' -> bit2=target, bits1..0=control. Control outcome classes:
        # '00' = projection back onto prep state (call c=0); anything else c=1.
        stats = {}
        joint = np.zeros((2, 4))
        for bit in (0, 1):
            n = sum(pools[bit].values())
            zsum, zc = {0: 0, 1: 0}, {0: 0, 1: 0}
            for k, v in pools[bit].items():
                t_bit = int(k[0])
                c_cls = 0 if k[1:] == "00" else 1
                zsum[c_cls] += v * (1 - 2 * t_bit)
                zc[c_cls] += v
                joint[bit, 2 * c_cls + t_bit] += v
            joint[bit] /= n
            stats[bit] = {"pc0": zc[0] / n,
                          "z_c0": zsum[0] / max(zc[0], 1), "z_c1": zsum[1] / max(zc[1], 1),
                          "n_c0": zc[0], "n_c1": zc[1]}
        R = {b: stats[b]["z_c0"] - stats[b]["z_c1"] for b in (0, 1)}
        Rbar = (R[0] - R[1]) / 2
        var = sum((1 - stats[b][f"z_c{c}"] ** 2) / max(stats[b][f"n_c{c}"], 1)
                  for b in (0, 1) for c in (0, 1)) / 4
        joint /= 2
        pb, pct = joint.sum(axis=1), joint.sum(axis=0)
        mi = float(sum(joint[i, j] * np.log2(joint[i, j] / (pb[i] * pct[j]))
                       for i in range(2) for j in range(4) if joint[i, j] > 0))
        res[kind] = {"Rbar": Rbar, "SE": float(np.sqrt(var)), "mi_bits": mi,
                     "p_c0_b0": stats[0]["pc0"], "p_c0_b1": stats[1]["pc0"]}
    return res


def main():
    out = {}
    print("=" * 74)
    print("3-SWITCH TRANSPILE AUDIT (free) — Whisper C4531")
    print("=" * 74)
    print("\n[1] Transpiled cost table (representative ops X,Y,Z):")
    rows = cost_table()
    out["cost_table"] = rows
    for r in rows:
        print(f"  {r['construction']:8s} {r['backend']:14s} opt{r['opt']}: "
              f"2q={r['twoq']:4d}  depth={r['depth']:4d}")

    print("\n[2] Payoff, NOISELESS (exact target by simulation):")
    nl = payoff(AerSimulator(), shots=4000)
    out["noiseless"] = nl
    print(f"  switch: Rbar={nl['switch']['Rbar']:+.4f}  MI={nl['switch']['mi_bits']:.4f} bits"
          f"  P(c0)={nl['switch']['p_c0_b0']:.4f}/{nl['switch']['p_c0_b1']:.4f}")
    print(f"  null:   Rbar={nl['null']['Rbar']:+.4f}  MI={nl['null']['mi_bits']:.5f} bits")

    print("\n[3] Payoff, FakeMarrakesh (haircut at audited depth — PLANNING number,")
    print("    noise-model trust is depth-stratified per C4530):")
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    fm = AerSimulator.from_backend(FakeMarrakesh())
    fk = payoff(fm, shots=1000)
    out["fakemarrakesh"] = fk
    print(f"  switch: Rbar={fk['switch']['Rbar']:+.4f} SE={fk['switch']['SE']:.4f}  "
          f"MI={fk['switch']['mi_bits']:.4f} bits")
    print(f"  null:   Rbar={fk['null']['Rbar']:+.4f}  MI={fk['null']['mi_bits']:.5f} bits")

    sig = fk["switch"]["Rbar"] / max(fk["switch"]["SE"], 1e-9)
    print(f"\n  sim signal-to-shot-noise at 1000 shots/circuit: {sig:.1f} sigma")
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "three_switch_audit.json"), "w"), indent=1)
    print("Saved ../results/three_switch_audit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
