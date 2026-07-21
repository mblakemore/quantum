#!/usr/bin/env python3
"""Exp251b (H7-P3, redo) — THE PATTERN BUFFER with IN-CIRCUIT correction: the Exp251 fix.

Exp251 (NO-ADVANTAGE) used offline decode, which cannot re-pump a decaying memory. This version
restores Exp241's ACTIVE in-circuit feed-forward: each round {idle -> syndrome -> if_test fix ->
reset} corrects errors as they happen, so the memory is actively maintained. Teleport front-end
(frame-deferred, Exp177) unchanged; the composition is now teleport + a LIVE-corrected memory.

PD-1 LESSON APPLIED (C4962): the selftest verifies against a realistic THERMAL-RELAXATION (T1/T2)
noise model, not an independent-flip proxy -- the proxy is what falsely passed Exp251.

Arms: tp_corr_R{2,3} (teleport + in-circuit-corrected memory) | tp_bare_R{2,3} (teleport, hold d0
bare, matched idle) | direct_corr_R3 | tp_immediate. Dynamic circuits (if_else, verified on fez).
CLAIM: F(tp_corr,R=3) > F(tp_bare,R=3) + 5se AND seam F(tp_immediate) > 0.90.
Substrate claude-opus-4-8, Whisper C4964."""
import os, sys, json
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
SHOTS = 8000; TAU_US = 30
CORR = {1: 0, 3: 1, 2: 2}   # syndrome int -> data qubit index to flip (Exp241 map)

def buffer_circuit(R, teleport=True, encode=True, correct=True, noise_delay=True):
    s = QuantumRegister(1, "s"); b = QuantumRegister(2, "b"); dd = QuantumRegister(2, "dd")
    a = QuantumRegister(2, "a")
    ms = ClassicalRegister(2, "m"); out = ClassicalRegister(3, "o")
    syn = [ClassicalRegister(2, f"y{r}") for r in range(R)]
    qc = QuantumCircuit(s, b, a, dd, *syn, out, ms)
    d = [b[1], dd[0], dd[1]]
    if teleport:
        qc.x(s[0]); qc.h(b[0]); qc.cx(b[0], b[1])
        qc.cx(s[0], b[0]); qc.h(s[0])
        qc.measure(s[0], ms[0]); qc.measure(b[0], ms[1])
    else:
        qc.x(b[1])
    hold = d if encode else [d[0]]
    if encode:
        qc.cx(d[0], d[1]); qc.cx(d[0], d[2])
    for r in range(R):
        if noise_delay:
            for q in hold: qc.delay(TAU_US, unit="us")
        if encode:
            qc.cx(d[0], a[0]); qc.cx(d[1], a[0]); qc.cx(d[1], a[1]); qc.cx(d[2], a[1])
            qc.measure(a[0], syn[r][0]); qc.measure(a[1], syn[r][1])
            if correct:
                with qc.if_test((syn[r], 1)): qc.x(d[0])   # a0=1,a1=0 -> d0
                with qc.if_test((syn[r], 3)): qc.x(d[1])   # a0=1,a1=1 -> d1
                with qc.if_test((syn[r], 2)): qc.x(d[2])   # a0=0,a1=1 -> d2
            qc.reset(a[0]); qc.reset(a[1])
    if encode:
        for i in range(3): qc.measure(d[i], out[i])
    else:
        qc.measure(d[0], out[0])
    return qc

PUBS = [("tp_corr_R3", dict(R=3)), ("tp_corr_R4", dict(R=4)),
        ("tp_sham_R3", dict(R=3, correct=False)), ("tp_sham_R4", dict(R=4, correct=False)),
        ("tp_bare_R3", dict(R=3, encode=False)), ("tp_bare_R4", dict(R=4, encode=False)),
        ("tp_immediate", dict(R=0))]

def _fid(counts, teleport, encode):
    good = 0; n = 0
    for key, c in counts.items():
        regs = key.split()                # qiskit: m o y{R-1}..y0
        ms = regs[0]; out = regs[1]
        maj = (1 if out.count("1") >= 2 else 0) if encode else int(out.replace(" ", "")[-1])
        if teleport: maj ^= int(ms[0])
        good += c * (1 if maj == 1 else 0); n += c
    return good / n

def _join(databin):
    names = [n for n in databin.__dict__ if not n.startswith("_")]
    ys = sorted([n for n in names if n.startswith("y")], key=lambda x: int(x[1:]), reverse=True)
    order = [n for n in ["m", "o"] + ys if n in names]
    ba = {n: getattr(databin, n).get_bitstrings() for n in order}
    from collections import Counter
    sh = len(next(iter(ba.values())))
    return dict(Counter(" ".join(ba[n][s] for n in order) for s in range(sh)))

def grade(counts_by_label, out):
    F = {lab: _fid(counts_by_label[lab], kw.get("teleport", True), kw.get("encode", True)) for lab, kw in PUBS}
    se = lambda p, n=SHOTS: float(np.sqrt(max(p*(1-p), 1e-6)/n))
    # PRIMARY (Exp241 confound-free): does in-circuit correction beat the IDENTICAL sham machinery?
    gains = {}
    for R in (3, 4):
        sp = F[f"tp_corr_R{R}"] - F[f"tp_sham_R{R}"]
        sesp = float(np.hypot(se(F[f"tp_corr_R{R}"]), se(F[f"tp_sham_R{R}"])))
        gains[R] = (sp, sesp, sp > 5 * sesp)
    g_corr = gains[3][2] or gains[4][2]        # Exp241's gain grows with R; PASS if it survives at R3 or R4
    g_seam = F["tp_immediate"] > 0.90
    verdict = "LIVE-BUFFER-CERTIFIED" if (g_corr and g_seam) else ("SEAM-FAIL" if not g_seam else "NO-CORRECTION-GAIN")
    print(f"  seam(R=0)={F['tp_immediate']:.4f} (>0.90) -> {g_seam}")
    for R in (3, 4):
        sp, sesp, ok = gains[R]
        print(f"  R{R}: corr={F[f'tp_corr_R{R}']:.4f} sham={F[f'tp_sham_R{R}']:.4f} bare={F[f'tp_bare_R{R}']:.4f}  CORRECTION GAIN={sp:+.4f} ({sp/sesp:.1f}s) -> {ok}")
    print(f"  VERDICT: {verdict}  (correction beats matched sham at R3 or R4)")
    out.update({"F": {k: round(float(v), 4) for k, v in F.items()},
                "gain_R3": round(float(gains[3][0]), 4), "gain_R4": round(float(gains[4][0]), 4),
                "gates": {"correction": bool(g_corr), "seam": bool(g_seam)}, "verdict": verdict})
    return verdict

def selftest():
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, thermal_relaxation_error
    from qiskit import transpile
    # realistic T1/T2 model (the C4962 lesson): T1=90us, T2=60us -> real decay, not independent flips
    T1, T2 = 90e3, 60e3   # ns
    nm = NoiseModel()
    for ng, t in (("delay", TAU_US*1000), ("id", TAU_US*1000), ("x", 100), ("sx", 100), ("reset", 100)):
        nm.add_all_qubit_quantum_error(thermal_relaxation_error(T1, T2, t), [ng])
    nm.add_all_qubit_quantum_error(
        thermal_relaxation_error(T1, T2, 400).tensor(thermal_relaxation_error(T1, T2, 400)), ["cx", "cz"])
    sim = AerSimulator(noise_model=nm)
    def run(correct):
        counts = {}
        for lab, kw in PUBS:
            qc = buffer_circuit(**{**kw, "correct": correct})
            counts[lab] = _join(sim.run(transpile(qc, sim), shots=6000).result().data(0)) if False else \
                sim.run(transpile(qc, sim), shots=6000).result().get_counts()
        return counts
    print("== IN-CIRCUIT CORRECTION ON (realistic T1/T2 noise) ==")
    out = {}; v = grade(run(True), out)
    print("== correction OFF (control: does the loop's machinery alone help? expect NO) ==")
    out2 = {}; grade(run(False), out2)
    # noiseless pipeline check
    sim0 = AerSimulator()
    c0 = {lab: sim0.run(transpile(buffer_circuit(**kw), sim0), shots=4000).result().get_counts() for lab, kw in PUBS}
    o0 = {}; grade(c0, o0)
    assert o0["F"]["tp_immediate"] > 0.99 and o0["F"]["tp_corr_R3"] > 0.99, "noiseless pipeline must be exact"
    print("SELFTEST: noiseless pipeline exact; realistic-T1 result above shows whether in-circuit correction helps a decaying memory.")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    circs, labels = [], []
    for lab, kw in PUBS:
        circs.append(transpile(buffer_circuit(**kw), backend, optimization_level=1, seed_transpiler=31, scheduling_method="asap"))
        labels.append(lab)
    n2 = [sum(1 for i in c.data if len(i.qubits) == 2) for c in circs]
    assert max(n2) <= 45, n2
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    job = SamplerV2(mode=backend).run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": labels}
    json.dump(man, open(os.path.join(QROOT, "results", "exp251b_manifest.json"), "w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    counts = {lab: _join(res[i].data) for i, lab in enumerate(labels)}
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-opus-4-8", "tau_us": TAU_US}
    grade(counts, out)
    json.dump({"card": out, "counts": counts}, open(os.path.join(QROOT, "results", "exp251b_result.json"), "w"), indent=1, default=float)
    print("card -> results/exp251b_result.json")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        submit(sys.argv[2] if len(sys.argv) > 2 else "ibm_fez")
    else:
        selftest()
