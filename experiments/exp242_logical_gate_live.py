#!/usr/bin/env python3
"""Exp242 — THE LOGICAL GATE ON LIVE-CORRECTED QUBITS: a transversal CNOT between two qubits kept alive. C4920.

The frontier flight (Creator directive): compose everything. Two logical qubits, each a 3-qubit bit-flip
code; a TWO-QUBIT LOGICAL GATE between them (the transversal/bitwise CNOT — a genuine logical CNOT for
this code, and fault-tolerant since a single fault stays weight-1 per block); and LIVE correction
(non-destructive syndrome + feed-forward, exp240/241) keeping BOTH qubits alive across an idle. The
logical inner loop of a two-qubit quantum computer.

SCOPING (advisor C4920 — the bit-flip code protects ONE basis, a Bell pair needs two):
  logical ops are Z-bar=Z0, X-bar=X0X1X2. The code corrects X errors -> it PROTECTS the Z-bar observable
  and is BLIND to phase (Z) errors (a single Z gives syndrome 00, undetectable, and corrupts X-bar-X-bar
  invisibly; the syndrome machinery even ADDS phase noise). Therefore:
   * CERTIFY live-correction improvement on the Z-bar claim: the logical CNOT TRUTH TABLE (majority
     readout) corrected-vs-sham, with idle between gate and readout so there is error to remove.
   * REPORT the Bell entanglement (both <Z-barZ-bar> and <X-barX-bar> positive from |+_L>|0_L> -> CNOT)
     as "the logical CNOT creates logical entanglement" — DEMONSTRATED, but only the ZZ leg is PROTECTED
     by this code; do NOT fold <XX> into the correction pass/fail.

SHAM control (confound-proof, 241 lesson): sham = the IDENTICAL circuit (same transversal CNOT, same
idle, same syndrome extraction, same mid-circuit measurement, same reset) with ONLY the feed-forward
withheld. Any corrected-vs-sham gap is the correction, not qubits/machinery.

FROZEN GATES:
  G1_GATE_CORRECTED (Z-bar, certified): mean logical-CNOT truth-table fidelity over the 4 inputs,
     corrected - sham >= 0.05, after gate + idle. HELD = the logical CNOT works on two live-corrected
     qubits AND correction improves the observable the code protects.
  G2_ENTANGLES (reported, not gated on correction): the transversal CNOT on |+_L>|0_L> yields a logical
     Bell pair with <Z-barZ-bar> >= 0.5 AND <X-barX-bar> >= 0.5 (logical entanglement demonstrated).
  Registered verdict = G1 and G2. REPORTED: per-input truth table, both Bell legs corr vs sham (with
     the honest note that only ZZ is protected).
SCOPE: two 3-qubit bit-flip logical qubits, transversal logical CNOT, one live round each side, bit-flip/
  T1 channel. First two-logical-qubit gate with live correction in the campaign. Deep circuit (6 data +
  2 reused ancillas); gate on the corrected-vs-sham MARGIN, expect modest absolute fidelity.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
TT_INPUTS = (("0", "0"), ("0", "1"), ("1", "0"), ("1", "1"))
TAU_US = 40


def _prep(qc, d, base, inp):
    if inp == "1": qc.x(d[base])
    elif inp == "+": qc.h(d[base])
    qc.cx(d[base], d[base + 1]); qc.cx(d[base], d[base + 2])   # encode block


def _syndrome_round(qc, d, a, base, syn, correct):
    qc.cx(d[base], a[0]); qc.cx(d[base + 1], a[0])             # z0^z1
    qc.cx(d[base + 1], a[1]); qc.cx(d[base + 2], a[1])         # z1^z2
    qc.measure(a[0], syn[0]); qc.measure(a[1], syn[1])
    if correct:
        with qc.if_test((syn, 1)): qc.x(d[base])
        with qc.if_test((syn, 3)): qc.x(d[base + 1])
        with qc.if_test((syn, 2)): qc.x(d[base + 2])
    qc.reset(a[0]); qc.reset(a[1])


def _idle_or_inject(qc, d, tau_us, inject, phase):
    if inject is not None:
        for (q, p) in inject.get(phase, []): getattr(qc, p)(d[q])   # deterministic error (selftest)
    elif tau_us > 0:
        for i in range(6): qc.delay(tau_us, d[i], unit="us")        # idle: accumulate error to correct


def circuit(inA, inB, correct, basis, tau_us=TAU_US, inject=None):
    """Two logical qubits A(0,1,2) B(3,4,5), transversal CNOT, then idle -> live round -> idle -> read.
    The two idle phases (241's structure) make the correction non-redundant with the majority readout:
    corrected resets the error budget mid-way, so it survives more accumulated error than sham."""
    d = QuantumRegister(6, "d"); a = QuantumRegister(2, "a")
    synA = ClassicalRegister(2, "synA"); synB = ClassicalRegister(2, "synB"); out = ClassicalRegister(6, "out")
    qc = QuantumCircuit(d, a, synA, synB, out)
    _prep(qc, d, 0, inA); _prep(qc, d, 3, inB)
    qc.barrier()
    qc.cx(d[0], d[3]); qc.cx(d[1], d[4]); qc.cx(d[2], d[5])    # TRANSVERSAL logical CNOT (A ctrl, B tgt)
    qc.barrier()
    _idle_or_inject(qc, d, tau_us, inject, "p1")               # idle phase 1
    qc.barrier()
    _syndrome_round(qc, d, a, 0, synA, correct)                # live round on A
    _syndrome_round(qc, d, a, 3, synB, correct)                # live round on B (ancillas reused)
    qc.barrier()
    _idle_or_inject(qc, d, tau_us, inject, "p2")               # idle phase 2
    qc.barrier()
    if basis == "X":
        for i in range(6): qc.h(d[i])
    for i in range(6): qc.measure(d[i], out[i])
    return qc


def _bits(s):
    b = s.replace(" ", ""); return [int(b[-1 - i]) for i in range(6)]   # qubit i = out[i]


def _maj(v3): return 1 if sum(v3) >= 2 else 0


def _truth_fid(counts, inA, inB):
    """P(logical output == CNOT(inA,inB)) via majority readout on each block."""
    wa = int(inA); wb = int(inA) ^ int(inB); ok = tot = 0
    for s, n in counts.items():
        v = _bits(s); la = _maj(v[0:3]); lb = _maj(v[3:6]); tot += n
        if la == wa and lb == wb: ok += n
    return ok / tot


def _zz(counts):
    c = tot = 0
    for s, n in counts.items():
        v = _bits(s); za = 1 - 2 * _maj(v[0:3]); zb = 1 - 2 * _maj(v[3:6]); c += za * zb * n; tot += n
    return c / tot


def _xx(counts):
    c = tot = 0
    for s, n in counts.items():
        v = _bits(s); xa = 1 - 2 * ((v[0] ^ v[1] ^ v[2])); xb = 1 - 2 * ((v[3] ^ v[4] ^ v[5]))
        c += xa * xb * n; tot += n
    return c / tot


def _marg(counts, token):
    out = {}
    for s, n in counts.items():
        k = s.split(" ")[token]; out[k] = out.get(k, 0) + n
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    print("Exp242 selftest | THE LOGICAL GATE ON LIVE-CORRECTED QUBITS")
    # (1) truth table exact noiselessly (out register = token 0)
    for inA, inB in TT_INPUTS:
        f = _truth_fid(_marg(sim.run(circuit(inA, inB, True, "Z", tau_us=0), shots=shots).result().get_counts(), 0), inA, inB)
        assert f > 0.99, f"logical CNOT truth table must be exact ({inA},{inB})"
    print("  (1) transversal CNOT truth table exact for all 4 inputs")
    # (2) entanglement: |+_L>|0_L> -> CNOT -> logical Bell pair, <ZZ>=<XX>=+1
    zz = _zz(_marg(sim.run(circuit("+", "0", True, "Z", tau_us=0), shots=shots).result().get_counts(), 0))
    xx = _xx(_marg(sim.run(circuit("+", "0", True, "X", tau_us=0), shots=shots).result().get_counts(), 0))
    print(f"  (2) logical Bell pair: <Z-barZ-bar>={zz:+.3f}  <X-barX-bar>={xx:+.3f} (both +1 = entangled)")
    assert zz > 0.99 and xx > 0.99, "transversal CNOT must create the logical Bell pair"
    # (3) correction NON-redundant with majority: two flips in the SAME block across the two idle phases.
    #     Corrected fixes the phase-1 flip in the round -> only 1 flip left for majority -> recovers.
    #     Sham carries BOTH into readout -> 2 flips in block A -> majority fails.
    inj = {"p1": [(0, "x")], "p2": [(1, "x")]}   # both block A
    fc = _truth_fid(_marg(sim.run(circuit("1", "0", True, "Z", inject=inj), shots=shots).result().get_counts(), 0), "1", "0")
    fs = _truth_fid(_marg(sim.run(circuit("1", "0", False, "Z", inject=inj), shots=shots).result().get_counts(), 0), "1", "0")
    print(f"  (3) two block-A flips across phases: corrected {fc:.3f}  sham {fs:.3f} (correction beats majority-alone)")
    assert fc > 0.99, "corrected must recover (round fixes phase-1 flip, majority fixes phase-2)"
    assert fs < 0.5, "sham must fail (2 flips in one block defeat majority-alone)"
    # (4) BLIND SPOT (advisor): inject a Z on block A -> syndrome reads 00 (undetectable), <XX> stays corrupted
    injz = {"p1": [(0, "z")]}
    rz = sim.run(circuit("+", "0", True, "X", inject=injz), shots=shots).result().get_counts()
    synA_counts = _marg(rz, 2)   # tokens: out(0) synB(1) synA(2)
    syn00 = synA_counts.get("00", 0) / sum(synA_counts.values())
    xx_z = _xx(_marg(rz, 0))
    print(f"  (4) BLIND SPOT — Z-error on A: synA reads 00 with prob {syn00:.3f} (undetectable); "
          f"<X-barX-bar> = {xx_z:+.3f} (corruption the code CANNOT see)")
    assert syn00 > 0.99, "a phase error MUST be invisible to the bit-flip syndrome (the honest limit)"
    print("SELFTEST PASS: transversal logical CNOT correct + creates a logical Bell pair; correction fixes "
          "the protected Z-bar observable; and the phase-error blind spot is real (syndrome 00). Cleared "
          "to fly — certify Z-bar, report entanglement as half-protected.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = []
    for (inA, inB) in TT_INPUTS:
        order.append(["tt", inA, inB, "corr", "Z"]); order.append(["tt", inA, inB, "sham", "Z"])
    for basis in ("Z", "X"):
        order.append(["bell", "+", "0", "corr", basis]); order.append(["bell", "+", "0", "sham", basis])
    def build(o):
        _, inA, inB, arm, basis = o
        return circuit(inA, inB, arm == "corr", basis)
    circuits = [transpile(build(o), backend=backend, optimization_level=1, seed_transpiler=0) for o in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (transversal CNOT + 2 live rounds)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp242_logical_gate_live_manifest.json")
    man = {"exp": 242, "slug": "logical_gate_live", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order, "tau_us": TAU_US,
           "prereg": {"G1_gate_corrected": "mean CNOT truth-table fidelity corrected - sham >= 0.05 (Z-bar, protected)",
                      "G2_entangles": "logical Bell <ZZ> >= 0.5 and <XX> >= 0.5 (entanglement demonstrated)",
                      "registered_verdict": "G1 and G2; only ZZ leg protected by the code (XX reported, not gated)",
                      "scope": "two 3-qubit bit-flip logical qubits, transversal logical CNOT, one live round each, "
                               "sham control isolates correction; certify Z-bar, report entanglement half-protected"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp242_logical_gate_live_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    idx = {tuple(o): i for i, o in enumerate(man["order"])}
    def oc(o): return getattr(res[idx[tuple(o)]].data, "out").get_counts()
    print(f"Exp242 THE LOGICAL GATE ON LIVE-CORRECTED QUBITS decode | job {man['job_id']}")
    print("  logical CNOT truth table (majority readout):")
    fc_list, fs_list = [], []
    for (inA, inB) in TT_INPUTS:
        fc = _truth_fid(oc(["tt", inA, inB, "corr", "Z"]), inA, inB)
        fs = _truth_fid(oc(["tt", inA, inB, "sham", "Z"]), inA, inB)
        fc_list.append(fc); fs_list.append(fs)
        print(f"    |{inA}_L>|{inB}_L> -> |{inA}>|{int(inA)^int(inB)}> : corrected {fc:.3f}  sham {fs:.3f}  adv {fc-fs:+.3f}")
    mc, ms = float(np.mean(fc_list)), float(np.mean(fs_list))
    zz_c = _zz(oc(["bell", "+", "0", "corr", "Z"])); zz_s = _zz(oc(["bell", "+", "0", "sham", "Z"]))
    xx_c = _xx(oc(["bell", "+", "0", "corr", "X"])); xx_s = _xx(oc(["bell", "+", "0", "sham", "X"]))
    print(f"\n  logical Bell pair (|+_L>|0_L> -> CNOT):")
    print(f"    <Z-barZ-bar> (PROTECTED leg): corrected {zz_c:+.3f}  sham {zz_s:+.3f}")
    print(f"    <X-barX-bar> (BLIND leg):     corrected {xx_c:+.3f}  sham {xx_s:+.3f}   (code cannot protect phase)")
    g1 = (mc - ms) >= 0.05
    g2 = (zz_c >= 0.5) and (xx_c >= 0.5)
    print(f"\n  truth table: corrected {mc:.3f}  sham {ms:.3f}  margin {mc-ms:+.3f}")
    print(f"G1 GATE CORRECTED (Z-bar): truth margin {mc-ms:+.3f} >= 0.05 {'OK' if g1 else 'MISS'}")
    print(f"G2 ENTANGLES: <ZZ> {zz_c:+.3f} and <XX> {xx_c:+.3f} both >= 0.5 {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("THE LOGICAL GATE ON LIVE-CORRECTED QUBITS — a transversal logical CNOT enacts its truth table on "
           "two bit-flip-encoded qubits kept alive by live syndrome+feed-forward, and correction improves the "
           "protected Z-bar observable over an idle (corrected-vs-sham); the CNOT also creates a logical Bell "
           "pair (<ZZ>,<XX> both positive) — entanglement between two error-corrected qubits, ZZ leg protected, "
           "XX leg blind to phase by this code. The two-qubit logical inner loop, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "truth_corrected": fc_list, "truth_sham": fs_list,
               "truth_mean_corr": mc, "truth_mean_sham": ms, "zz_corr": zz_c, "zz_sham": zz_s,
               "xx_corr": xx_c, "xx_sham": xx_s, "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp242_logical_gate_live_decode.json"), "w"), indent=1)
    print("-> results/exp242_logical_gate_live_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
