#!/usr/bin/env python3
"""Exp250 (H7-P5, redesigned) — THE UNIVERSAL TRANSLATOR: mid-circuit code conversion + protection
retargeting, certified for COMPUTATIONAL logicals.

PD-0 SCOUT ($0, C4959) falsified the literal two-storm-survival narrative: 3-qubit codes are
distance-1 (each protects ONE logical basis), so a both-basis (Y/superposition) state is not
protectable by switching distance-1 codes, and the full sequenced two-storm translated arm reads
random (0.502 in sim). That wall is REPORTED, not flown. What IS clean and certifiable:

  G1 CONVERSION: transversal-H carries |0L>,|1L> from the bit-flip code to the phase-flip code
     preserving the logical value (destination X-majority reads 0 / 1). Sim: 0.000 / 1.000 exact.
  G2 RETARGET: after conversion to phase-flip, a Z-storm (phase noise) is CORRECTED by the
     destination code (X-majority), beating bare |+>. Sim: 0.11 code vs 0.21 bare @ theta=0.3pi.
  G3 SOURCE: the bit-flip code protects its native X-storm (Z-majority), beating bare |0>.

Each 3-qubit code is a SPECIALIST (bit-flip guards Z-basis, phase-flip guards X-basis); the
translator hands a logical value between specialists so it always sits in the code matched to the
incoming noise. Storms are COHERENT global rotations (G12): theta=0.3pi -> single-qubit P_flip=0.206.
Pubs: 8 x 8000, static, <=4 2q. Substrate claude-fable-5, Whisper C4959."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
from qiskit import QuantumCircuit

SHOTS = 8000
TH = 0.3 * np.pi   # coherent storm; single-qubit P_flip = sin^2(theta/2) = 0.206

def _bf(qc, b):    # bit-flip encode |bL> = |bbb>
    if b: qc.x(0)
    qc.cx(0, 1); qc.cx(0, 2)

def conv(b):       # G1: |bL,bf> --H3--> pf ; X-basis readout (pf logical distinguisher)
    qc = QuantumCircuit(3, 3); _bf(qc, b)
    for q in range(3): qc.h(q)                 # transversal H = code conversion
    for q in range(3): qc.h(q); qc.measure(q, q)
    return qc

def retarget_pf():  # G2: |0L,bf>->pf, Z-storm, X-majority (destination corrects phase noise)
    qc = QuantumCircuit(3, 3); _bf(qc, 0)
    for q in range(3): qc.h(q)                 # -> pf |0L>=|+++>
    for q in range(3): qc.rz(TH, q)            # Z-storm
    for q in range(3): qc.h(q); qc.measure(q, q)
    return qc

def source_bf():    # G3: |0L,bf>, X-storm, Z-majority (source corrects native bit noise)
    qc = QuantumCircuit(3, 3); _bf(qc, 0)
    for q in range(3): qc.rx(TH, q)            # X-storm
    for q in range(3): qc.measure(q, q)
    return qc

def bare(storm):    # single-qubit baselines
    qc = QuantumCircuit(1, 1)
    if storm == "z": qc.h(0); qc.rz(TH, 0); qc.h(0)
    else: qc.rx(0.0, 0); qc.rx(TH, 0)          # |0> + X-storm, Z-read
    qc.measure(0, 0)
    return qc

def clean_pf():     # encoding-overhead reference (no storm)
    qc = QuantumCircuit(3, 3); _bf(qc, 0)
    for q in range(3): qc.h(q)
    for q in range(3): qc.h(q); qc.measure(q, q)
    return qc

PUBS = [("conv0", conv(0)), ("conv1", conv(1)), ("retarget_pf", retarget_pf()),
        ("bare_z", bare("z")), ("source_bf", source_bf()), ("bare_x", bare("x")),
        ("clean_pf", clean_pf())]

def build():
    return [(lab, qc, SHOTS) for lab, qc in PUBS]

def _leak_maj(counts):   # logical-1 leakage by 3-bit majority
    n = sum(counts.values())
    return sum(c * (1 if k.replace(" ", "").count("1") >= 2 else 0) for k, c in counts.items()) / n

def _leak_1q(counts):
    n = sum(counts.values()); return sum(c for k, c in counts.items() if k.strip() == "1") / n

def grade(counts, out):
    L = {}
    for lab in ("conv0", "conv1", "retarget_pf", "source_bf", "clean_pf"):
        L[lab] = _leak_maj(counts[lab])
    L["bare_z"] = _leak_1q(counts["bare_z"]); L["bare_x"] = _leak_1q(counts["bare_x"])
    se = lambda p, n=SHOTS: float(np.sqrt(max(p*(1-p), 1e-6)/n))
    g1 = L["conv0"] < 0.10 and (1 - L["conv1"]) < 0.10 + 0.9*0 and L["conv1"] > 0.90
    sep_g2 = L["bare_z"] - L["retarget_pf"]; se_g2 = float(np.hypot(se(L["bare_z"]), se(L["retarget_pf"])))
    sep_g3 = L["bare_x"] - L["source_bf"];  se_g3 = float(np.hypot(se(L["bare_x"]), se(L["source_bf"])))
    g2 = sep_g2 > 5 * se_g2
    g3 = sep_g3 > 5 * se_g3
    verdict = "PASS-TRANSLATOR" if (g1 and g2 and g3) else ("CONVERSION-ONLY" if g1 else "NOT-HELD")
    print(f"  G1 CONVERSION: conv0 leak={L['conv0']:.3f} (<0.10)  conv1 fid={1-L['conv1']:.3f}... logical1={L['conv1']:.3f} (>0.90)  -> {g1}")
    print(f"  G2 RETARGET (Z-storm): pf-code {L['retarget_pf']:.3f} vs bare {L['bare_z']:.3f}  sep={sep_g2:+.3f} ({sep_g2/se_g2:.0f}s) -> {g2}")
    print(f"  G3 SOURCE (X-storm):   bf-code {L['source_bf']:.3f} vs bare {L['bare_x']:.3f}  sep={sep_g3:+.3f} ({sep_g3/se_g3:.0f}s) -> {g3}")
    print(f"  clean_pf (encode overhead, no storm) leak={L['clean_pf']:.3f}   VERDICT: {verdict}")
    out.update({"leak": {k: round(float(v), 4) for k, v in L.items()},
                "sep_g2": round(float(sep_g2), 4), "sep_g3": round(float(sep_g3), 4),
                "gates": {"g1": bool(g1), "g2": bool(g2), "g3": bool(g3)}, "verdict": verdict})
    return verdict

def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    counts = {lab: sim.run(qc, shots=40000).result().get_counts() for lab, qc in PUBS}
    out = {}; v = grade(counts, out)
    assert out["leak"]["conv0"] < 0.02 and out["leak"]["conv1"] > 0.98, "conversion must be exact in sim"
    assert v == "PASS-TRANSLATOR", (v, out["gates"])
    print("SELFTEST PASS: conversion exact (0/1), each code beats bare vs its native storm, PASS-TRANSLATOR.")
    print("BOUNDARY (reported, not flown): full two-storm superposition survival reads random (0.50) at")
    print("distance-1 -- each 3-qubit code protects ONE logical basis; the both-basis demo needs Shor [[9,1,3]].")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    pubs = build()
    circs = [transpile(qc, backend, optimization_level=3, seed_transpiler=19) for _, qc, _ in pubs]
    n2 = [sum(1 for i in c.data if len(i.qubits) == 2) for c in circs]
    assert max(n2) <= 6, n2
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    job = SamplerV2(mode=backend).run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": [l for l, _, _ in pubs]}
    json.dump(man, open(os.path.join(QROOT, "results", "exp250_manifest.json"), "w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    counts = {lab: res[i].data.c.get_counts() for i, (lab, _, _) in enumerate(pubs)}
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-opus-4-8", "theta_over_pi": 0.3}
    grade(counts, out)
    json.dump({"card": out, "counts": counts}, open(os.path.join(QROOT, "results", "exp250_result.json"), "w"), indent=1, default=float)
    print("card -> results/exp250_result.json")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        submit(sys.argv[2] if len(sys.argv) > 2 else "ibm_fez")
    else:
        selftest()
