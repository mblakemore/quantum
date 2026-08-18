#!/usr/bin/env python3
"""H15 N4 — THE REAL-TIME NEURON (Whisper C5075). $0 design study, sim only.

TWO CHANGES to the N1 loop, both pointing the same way:

(1) DECISION MOVES FROM 4 TOFFOLIS TO REAL-TIME CLASSICAL LOGIC.
    N1 accumulated XOR_i(a_i AND b_i) coherently into an ancilla (4 Toffolis ≈ 24 CZ), measured
    the ancilla once, and fed forward. N4 measures the 8 Bell bits mid-circuit and evaluates the
    rule in the control processor, then feeds forward. Evidence this is the better half: in the
    SAME kingston job, the no-Toffoli sensor arm read 0.9375 while the Toffoli loop read 0.875.
    This is still a closed in-circuit reflex arc — real-time classical logic driving a quantum
    actuator inside one execution is exactly how QEC decoders and every feedforward experiment
    work. What must stay quantum is the TWO-COPY BELL MEASUREMENT, and it does.

(2) THE OPTIMAL DECISION RULE REPLACES THE SIMPLE ONE — free accuracy we were giving away.
    N1 accepted on parity alone: 136 of 256 Bell outcomes. The true ALT support is 121; the extra
    15 cells carry EXACTLY ZERO ALT probability, so accepting them only manufactured false
    positives. Closed form (verified against the support at n=2,3,4):

        accept  iff  XOR_i(a_i AND b_i) == 0   AND   NOT (a == 0 AND b != 0)

    Trivial classically (two OR-reductions), awkward coherently — which is why change (1) enables
    change (2). Noiseless accuracy rises 0.7344 -> 0.7637 (= the exact Helstrom value), and the
    NULL accept rate falls 17/32 -> 121/256.

BIT ORIENTATION, determined from noiseless simulation rather than assumed (512 shots, the
excluded cells fired 0 times under this orientation and 73 times under the swap):
    b = low nibble  (bell[0..3], the q0-q3 halves)
    a = high nibble (bell[4..7], the q4-q7 halves)

$0. No submission path in this file.
"""
import itertools
import json
import sys

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.circuit.classical import expr

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import all_A_mats, SIM, wilson

N = 4


def build_n4(A=None, xu=None, arm="auto", rule="optimal"):
    """Real-time neuron. arm: auto|never|always. rule: optimal|simple."""
    qs = QuantumRegister(10, "q")
    c_b = ClassicalRegister(4, "bb")     # b = low nibble  (copy-1 halves)
    c_a = ClassicalRegister(4, "aa")     # a = high nibble (copy-2 halves)
    c_act = ClassicalRegister(1, "act")
    qc = QuantumCircuit(qs, c_b, c_a, c_act)
    if A is not None:
        for base in (0, 4):
            for i in range(N):
                qc.h(base + i)
            for i in range(N):
                for j in range(i, N):
                    if A[i][j]:
                        qc.z(base + i) if i == j else qc.cz(base + i, base + j)
    else:
        x, u = xu
        for i in range(N):
            if (x >> i) & 1:
                qc.x(i)
            if (u >> i) & 1:
                qc.x(4 + i)
    qc.barrier()
    for i in range(N):                    # transversal Bell rotation — the quantum resource
        qc.cx(i, 4 + i)
        qc.h(i)
    for i in range(N):                    # mid-circuit readout of both nibbles
        qc.measure(i, c_b[i])
        qc.measure(4 + i, c_a[i])
    if arm == "always":
        qc.x(9)
    elif arm == "auto":
        # parity of the AND, in real-time classical logic
        andw = expr.bit_and(expr.lift(c_b), expr.lift(c_a))          # 4-bit AND
        par0 = expr.equal(andw, 0)
        p1 = expr.not_equal(expr.bit_and(andw, 0x3), 0x3)            # helper terms below
        # XOR-reduce the 4 AND bits: parity == 0 iff popcount even.
        # Expressed as equality against the 8 even-popcount patterns of a 4-bit word.
        EVEN = [0b0000, 0b0011, 0b0101, 0b0110, 0b1001, 0b1010, 0b1100, 0b1111]
        cond_par = expr.equal(andw, EVEN[0])
        for v in EVEN[1:]:
            cond_par = expr.logic_or(cond_par, expr.equal(andw, v))
        if rule == "optimal":
            a_zero = expr.equal(expr.lift(c_a), 0)
            b_nonzero = expr.not_equal(expr.lift(c_b), 0)
            excluded = expr.logic_and(a_zero, b_nonzero)
            cond = expr.logic_and(cond_par, expr.logic_not(excluded))
        else:
            cond = cond_par
        with qc.if_test(cond):
            qc.x(9)
    qc.measure(9, c_act[0])
    return qc


def read(mem):
    """mem = 'act aa bb' (qiskit prints registers in reverse creation order)."""
    act_s, a_s, b_s = mem.split()
    return int(act_s), int(a_s, 2), int(b_s, 2)


def expected(a, b, rule):
    par = bin(a & b).count("1") % 2
    if par != 0:
        return 0
    if rule == "optimal" and a == 0 and b != 0:
        return 0
    return 1


def run(circs, shots=1):
    res = SIM.run(circs, shots=shots, memory=True).result()
    return [res.get_memory(i) for i in range(len(circs))]


if __name__ == "__main__":
    out = {"card": "h15_n4_realtime_neuron", "cycle": "C5075"}
    # --- PIN: in-circuit response must equal the rule applied to the measured bits ---
    for rule in ("simple", "optimal"):
        circs = [build_n4(A=A, arm="auto", rule=rule) for A in itertools.islice(all_A_mats(), 0, 1024, 2)]
        mism = acc = tot = 0
        for mem in run(circs, 4):
            for line in mem:
                act, a, b = read(line)
                mism += int(act != expected(a, b, rule))
                acc += act; tot += 1
        out[f"pin_{rule}"] = {"mismatches": mism, "n": tot, "alt_accept": acc / tot}
        print(f"PIN {rule:8s}: mismatches {mism}/{tot} | noiseless ALT accept {acc/tot:.4f}")
    # --- ablations ---
    for arm, want in (("never", 0), ("always", 1)):
        mem = run([build_n4(A=next(all_A_mats()), arm=arm)], 32)[0]
        vals = {read(x)[0] for x in mem}
        out[f"ablation_{arm}"] = sorted(vals)
        print(f"ablation {arm}: {sorted(vals)} (want [{want}])")
    # --- NULL arm, both rules ---
    rng = np.random.default_rng(5075)
    xus = [(int(rng.integers(16)), int(rng.integers(16))) for _ in range(512)]
    for rule in ("simple", "optimal"):
        circs = [build_n4(xu=xu, arm="auto", rule=rule) for xu in xus]
        acc = tot = 0
        for mem in run(circs, 2):
            for line in mem:
                acc += read(line)[0]; tot += 1
        lo, hi = wilson(acc, tot)
        out[f"null_{rule}"] = {"accept": acc / tot, "wilson": [lo, hi],
                               "theory": 17/32 if rule == "simple" else 121/256}
        print(f"NULL {rule:8s}: accept {acc/tot:.4f} [{lo:.4f},{hi:.4f}]  theory "
              f"{(17/32 if rule=='simple' else 121/256):.4f}")
    # --- resource comparison vs N1 ---
    from qiskit.providers.fake_provider import GenericBackendV2
    bk = GenericBackendV2(num_qubits=10, basis_gates=["cz", "rz", "sx", "x", "id"], control_flow=True)
    t = transpile(build_n4(A=next(all_A_mats()), arm="auto", rule="optimal"), bk,
                  optimization_level=1, seed_transpiler=5075)
    ops = {k: int(v) for k, v in t.count_ops().items()}
    out["transpiled"] = {"ops": ops, "cz": ops.get("cz", 0), "depth": int(t.depth()),
                         "n1_reference": {"cz": 28, "depth": 87, "mcm": 1}}
    print(f"\nN4 transpiled: cz={ops.get('cz',0)} depth={t.depth()}  (N1 reference: cz=28 depth=87)")
    json.dump(out, open("/droid/repos/quantum/results/h15_n4_design_sim_c5075.json", "w"), indent=1)
    print("WROTE results/h15_n4_design_sim_c5075.json")
