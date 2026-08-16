#!/usr/bin/env python3
"""H15 Cell N1 — the synapse closes in-circuit ($0, sim only). Elder GO "Build G0"
(coordination#12398). Builds against the PROVISIONAL ceiling 143/256 (building != freezing).

THE CIRCUIT (n=4, 10 qubits):
  q0-3  copy 1 of the stimulus     q4-7  copy 2
  q8    decision ancilla           q9    actuator
  ALT prep : per copy H^4, CZ(i,j) per A_ij=1 (i<j), Z(i) per A_ii=1  (door(a) convention)
  NULL prep: per-shot random |x>|u>  (uniform -> I/4^n exactly in expectation)
  Bell rot : CNOT(q_i -> q_{i+4}), H(q_i), i=0..3
  DECIDE   : Toffoli(q_i, q_{i+4}, q8) x4  == q8 accumulates XOR_i(bit_i AND bit'_i)
             (AND is symmetric, so the a/b label mapping cannot change the value;
              the mapping is still calibrated and asserted below, cal-pins-the-convention)
  MCM      : measure q8 -> c_dec  (ONE mid-circuit measurement; billing 3x noted)
  ACT      : arm 'auto'  : if c_dec==0 -> X(q9)   (respond ALT)
             arm 'never' : no feedforward          (ablation)
             arm 'always': X(q9) unconditionally   (ablation)
  READ     : actuator q9 + the 8 Bell qubits (records only)

THE PIN (G0): shot-by-shot, the in-circuit response must equal the classical
decode XOR_i(a_i AND b_i)==0 computed from the terminally-measured Bell bits —
100.0% agreement required, ALT (all 1024 A) and NULL both. Aggregates must
reproduce the atoms exactly: P(accept|ALT)=1; P(accept|NULL)=17/32 (Wilson-checked);
success 47/64 = 0.734375 vs provisional ceiling 143/256 = 0.558594.

$0. No submission path. No account import anywhere in this file.
"""
import itertools
import json

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator

N = 4
RNG = np.random.default_rng(20260816)
SIM = AerSimulator(seed_simulator=5074)
OUT = {"card": "h15_n1_synapse_incircuit", "cycle": "C5074", "n": N,
       "provisional_ceiling": 143 / 256}


# ---------- convention calibration: which measured bit is a, which is b ----------
def bell_mapping():
    """Prepare (I x X^a Z^b)|Phi+> per (a,b), Bell-rotate, measure.
    Returns the deterministic map (a,b) -> (m_top, m_bot) and asserts the
    unordered pair {m_top, m_bot} == {a, b} (Toffoli-compatibility)."""
    mapping = {}
    for a in (0, 1):
        for b in (0, 1):
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)          # |Phi+>
            if a:
                qc.x(1)
            if b:
                qc.z(1)
            qc.cx(0, 1)
            qc.h(0)
            qc.measure([0, 1], [0, 1])
            counts = SIM.run(qc, shots=256).result().get_counts()
            assert len(counts) == 1, f"non-deterministic Bell cal {a},{b}: {counts}"
            bits = list(counts)[0]        # 'c1c0' little-endian string
            m_top, m_bot = int(bits[-1]), int(bits[-2])   # c0=q0, c1=q1
            mapping[(a, b)] = (m_top, m_bot)
    ok_pair = all({m1, m2} == ({a, b} if a != b else {a})
                  for (a, b), (m1, m2) in mapping.items())
    return mapping, ok_pair


# ---------- circuit builder ----------
def build(A=None, xu=None, arm="auto"):
    """A given -> ALT prep; xu=(x,u) given -> NULL prep."""
    qs = QuantumRegister(10, "q")
    c_bell = ClassicalRegister(8, "bell")
    c_dec = ClassicalRegister(1, "dec")
    c_act = ClassicalRegister(1, "act")
    qc = QuantumCircuit(qs, c_bell, c_dec, c_act)
    if A is not None:
        for base in (0, 4):
            for i in range(N):
                qc.h(base + i)
            for i in range(N):
                for j in range(i, N):
                    if A[i][j]:
                        if i == j:
                            qc.z(base + i)
                        else:
                            qc.cz(base + i, base + j)
    else:
        x, u = xu
        for i in range(N):
            if (x >> i) & 1:
                qc.x(i)
            if (u >> i) & 1:
                qc.x(4 + i)
    qc.barrier()
    for i in range(N):                      # Bell rotation
        qc.cx(i, 4 + i)
        qc.h(i)
    for i in range(N):                      # coherent AND-XOR accumulate
        qc.ccx(i, 4 + i, 8)
    qc.measure(8, c_dec[0])                 # the ONE mid-circuit measurement
    if arm == "auto":
        with qc.if_test((c_dec[0], 0)):     # accept (parity 0) -> respond ALT
            qc.x(9)
    elif arm == "always":
        qc.x(9)
    qc.measure(9, c_act[0])
    for i in range(N):                      # records
        qc.measure(i, c_bell[i])
        qc.measure(4 + i, c_bell[4 + i])
    return qc


def run_batch(circs, shots):
    res = SIM.run(circs, shots=shots, memory=True).result()
    return [res.get_memory(i) for i in range(len(circs))]


def classical_rule(mem_line):
    """mem 'act dec bell' space-separated (registers reversed order in qiskit
    string: 'c_act c_dec c_bell'). Returns (response_bit, accept_from_bells,
    dec_bit)."""
    act_s, dec_s, bell_s = mem_line.split()
    bells = [int(bell_s[-1 - k]) for k in range(8)]   # bell[k], little-endian
    parity = 0
    for i in range(N):
        parity ^= bells[i] & bells[4 + i]
    return int(act_s), 1 - parity, int(dec_s)


def all_A_mats():
    idx = [(i, j) for i in range(N) for j in range(i, N)]
    for bits in itertools.product([0, 1], repeat=len(idx)):
        A = [[0] * N for _ in range(N)]
        for (i, j), b in zip(idx, bits):
            A[i][j] = b
        yield A


def wilson(k, n_, z=1.96):
    p = k / n_
    den = 1 + z * z / n_
    ctr = p + z * z / (2 * n_)
    rad = z * np.sqrt(p * (1 - p) / n_ + z * z / (4 * n_ * n_))
    return ((ctr - rad) / den, (ctr + rad) / den)


if __name__ == "__main__":
    mapping, pair_ok = bell_mapping()
    OUT["bell_convention_map"] = {f"{a}{b}": list(v) for (a, b), v in mapping.items()}
    OUT["bell_map_pair_ok_for_toffoli"] = pair_ok
    assert pair_ok, "Bell mapping not a/b-pair-preserving: Toffoli rule invalid"
    print(f"convention pin: {OUT['bell_convention_map']} pair_ok={pair_ok}", flush=True)

    # --- ALT: all 1024 A, 8 shots each ---
    circs = [build(A=A, arm="auto") for A in all_A_mats()]
    mismatch = 0
    dec_mismatch = 0
    acc = tot = 0
    for mem in run_batch(circs, 8):
        for line in mem:
            r, accept, dec = classical_rule(line)
            if r != accept:
                mismatch += 1
            if dec != 1 - accept:
                dec_mismatch += 1
            acc += accept
            tot += 1
    OUT["alt_shots"] = tot
    OUT["alt_pin_mismatches"] = mismatch
    OUT["alt_dec_bit_mismatches"] = dec_mismatch
    OUT["alt_accept_rate"] = acc / tot
    print(f"ALT: {tot} shots, pin mismatches {mismatch}, accept rate {acc/tot}",
          flush=True)

    # --- NULL: 2048 sampled (x,u) preps x 4 shots ---
    xus = [(int(RNG.integers(16)), int(RNG.integers(16))) for _ in range(2048)]
    circs = [build(xu=xu, arm="auto") for xu in xus]
    mismatch = acc = tot = 0
    for mem in run_batch(circs, 4):
        for line in mem:
            r, accept, dec = classical_rule(line)
            if r != accept:
                mismatch += 1
            acc += accept
            tot += 1
    lo, hi = wilson(acc, tot)
    OUT["null_shots"] = tot
    OUT["null_pin_mismatches"] = mismatch
    OUT["null_accept_rate"] = acc / tot
    OUT["null_accept_wilson95"] = [lo, hi]
    OUT["null_accept_exact_target"] = 17 / 32
    OUT["null_target_in_interval"] = bool(lo <= 17 / 32 <= hi)
    print(f"NULL: {tot} shots, pin mismatches {mismatch}, accept "
          f"{acc/tot:.5f} [{lo:.5f},{hi:.5f}] target {17/32}", flush=True)

    # --- ablation arms sanity (64 shots each on one A and one xu) ---
    arms = {}
    for arm in ("never", "always"):
        r_alt = run_batch([build(A=next(all_A_mats()), arm=arm)], 64)[0]
        resp = {classical_rule(x)[0] for x in r_alt}
        arms[arm] = sorted(resp)
    OUT["ablation_response_sets"] = arms   # never->{0}, always->{1}
    print(f"ablation arms: {arms}", flush=True)

    # --- success bookkeeping vs atoms + provisional ceiling ---
    succ = 0.5 * OUT["alt_accept_rate"] + 0.5 * (1 - OUT["null_accept_rate"])
    OUT["success_estimate"] = succ
    OUT["success_exact_target_47_64"] = 47 / 64
    OUT["margin_over_provisional_ceiling"] = succ - 143 / 256
    print(f"success {succ:.5f} (target {47/64}) margin over ceiling "
          f"{succ - 143/256:.5f}", flush=True)

    # --- resource accounting: transpile to CZ-native generic 10q backend ---
    from qiskit.providers.fake_provider import GenericBackendV2
    try:
        bk = GenericBackendV2(num_qubits=10,
                              basis_gates=["cz", "rz", "sx", "x", "id"],
                              control_flow=True)
        tqc = transpile(build(A=next(all_A_mats()), arm="auto"), bk,
                        optimization_level=2, seed_transpiler=5074)
        ops = dict(tqc.count_ops())
        OUT["transpiled_ops"] = {k: int(v) for k, v in ops.items()}
        OUT["transpiled_2q"] = int(ops.get("cz", 0))
        OUT["transpiled_depth"] = int(tqc.depth())
    except Exception as e:                      # report, never mask
        OUT["transpile_error"] = f"{type(e).__name__}: {e}"
    OUT["mcm_count"] = 1
    OUT["mcm_billing_note"] = "MCM ~3x billing multiplier applies at G4 pricing"
    OUT["interferometric_wall_2q"] = 475

    verdict = ("G0-PIN-PASS" if OUT["alt_pin_mismatches"] == 0
               and OUT["null_pin_mismatches"] == 0
               and OUT["alt_accept_rate"] == 1.0
               and OUT["null_target_in_interval"]
               else "G0-PIN-FAIL")
    OUT["verdict"] = verdict
    with open("/droid/repos/quantum/results/h15_n1_pin_c5074.json", "w") as f:
        json.dump(OUT, f, indent=1)
    print(f"VERDICT {verdict} — wrote results/h15_n1_pin_c5074.json", flush=True)
